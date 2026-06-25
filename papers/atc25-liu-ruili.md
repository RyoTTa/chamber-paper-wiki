---
tags: [paper, 2025, 2025ATC, topic/disaggregation, topic/dram, topic/memory-tiering, topic/nvm, topic/virtual-memory]
venue: ""
year: 2025
summary_path: "../paper-summaries/2025ATC-summarize/dsa-2lm-a-cpu-free-tiered-memory-architecture-with-intel-dsa.md"
---

# DSA-2LM: A CPU-Free Tiered Memory Architecture with Intel DSA

**Venue:** 
**저자:** Ruili Liu (Tsinghua Univ. / UESTC), Teng Ma (Alibaba), Mingxing Zhang, Jialiang Huang, Yingdi Shan (Tsinghua), Zheng Liu (Alibaba), Lingfeng Xiang, Zhen Lin, Hui Lu, Jia Rao (UT Arlington), Kang Chen, Yongwei Wu (Tsinghua)

## 개요

데이터 집약적 애플리케이션(그래프 처리, ML, 인메모리 DB)의 메모리 수요가 지속 증가하며 DRAM 비용이 서버 총비용의 ~50%를 차지한다. CXL/NVM 기반 tiered memory는 저비용 대용량을 제공하나, hot/cold page의 최적 배치를 위해 page migration이 필수적이다.

**Page copy가 tiered memory의 핵심 병목이다.** MEMTIS의 kmigrated 프로세스를 perf로 프로파일링한 결과 (Figure 2):

| 단계 | CPU 비중 |
|------|----------|
| page migration 전체 (shrink_page_list) | 72.87% |
| └ reverse mapping + 통계 갱신 (get_pginfo_idx) | 29.82% |
| └ **메모리 복사 (migrate_page_list)** | **34.43%** |
| └ migrate_page_copy (순수 copy) | 25.31% |

즉 migration 과정의 73.51% processor cycle이 page copy에 소모된다. MEMTIS의 histogram 기반 최적화에도 migration 시간의 ~49%가 copy에 사용된다. 또한 NOMAD의 TPM(Transactional Page Migration)은 migration window가 길어질수록 transactional 실패 확률이 증가한다.

**Hotness detection도 CPU를 소모한다.** 샘플링 interval을 줄이면(더 정밀한 detection) CPU utilization과 page migration 횟수가 증가하여 오히려 애플리케이션 성능이 저하된다 (Figure 1). PEBS 기반 하드웨어 offload를 해도 20% 성능 저하가 보고된다 [44].

## 방법론

### 3.1 아키텍처 개요 (Figure 8)

DSA-2LM은 MEMTIS의 3단계 파이프라인을 계승한다:
1. **Access tracking:** PEBS로 page-granularity 메모리 접근 샘플링 → histogram에 access count 누적
2. **Hot/cold 판별:** Thot/Tcold 임계값 기반. fast tier가 모든 hot page를 수용하도록 동적 조정
3. **Background migration:** per-node kmigrated 커널 스레드, 주기적 wake-up (200ms → DSA로 더 짧게)

MEMTIS 대비 개선점:
- 오래된 샘플 제거 (가장 최근 샘플만 사용)
- Nimble에서 영감을 받은 concurrent migration 전략
- DSA CPU-free 특성으로 더 aggressive한 migration interval 사용

### 3.2 Migration Workflow (§3.3)

각 memory tier마다 migration 커널 스레드가 promotion/demotion을 처리한다.

**Promotion:** 페이지 접근 샘플 처리 시 hotness factor Hi > Thot → promotion list에 추가.

**Cooling:** N개 샘플마다 모든 페이지의 access count를 절반으로 감소 (aging). 이로 인해 cold 상태로 전환된 페이지는 demotion list로 이동.

**Demotion 트리거:** fast tier의 가용 메모리가 3% 미만일 때 시작. Hi ≤ Tcold인 cold page를 slow tier로 demotion하여 충분한 여유 공간 확보까지 수행. cold page 중에서도 가능한 많은 페이지를 fast tier에 유지하는 전략.

### 3.3 Adaptable Concurrent Migration (§3.4) — 핵심 설계

기존 MEMTIS는 `migrate_page_copy`가 4KB/2MB page를 구분 없이 CPU로 복사. DSA-2LM은 mixed page list를 효율적으로 처리하는 adaptable 2-pass 알고리즘을 도입했다.

#### Algorithm 1 (의사코드)

```
Input: page_list (4KB/2MB 혼합 page pair 리스트)
1: per-cpu descriptor/completion 구조체 포인터 획득
2: repeat
3:   nr_base_pages ← 0
4:   // Pass 1 — 2MB Huge Page 처리
5:   for each unsolved page_pair:
6:     if HugePage:
7:       transfer_size ← 2MB / limit_chans  // 예: 256KB
8:       for each WQ i:
9:         memmove descriptor 생성 (page_pair, transfer_size, WQ_i)
10:        descriptor submit
11:    else:
12:      nr_base_pages++
13:  // Pass 2 — 4KB Page 배치 처리
14:  batch_size ← nr_base_pages / limit_chans
15:  batch_list ← ∅
16:  for each unsolved 4KB page_pair:
17:    memmove descriptor desc 생성
18:    batch_list ← batch_list ∪ {desc}
19:    if |batch_list| == batch_size:
20:      WQ_t ← round-robin 선택
21:      batch descriptor 생성 (batch_list, batch_size, WQ_t)
22:      submit
23:      batch_list ← ∅
24:  // 모든 WQ 완료 대기 (async)
25:  for each WQ i:
26:    yield and wait for completion
27: until all page_pairs migrated
```

**Pass 1 — 2MB Huge Page 분할:** 하나의 2MB page를 `limit_chans`(기본값 8)개로 분할하여 각 WQ에 하나씩 할당 (transfer_size = 256KB). DSA의 multi-WQ 병렬성을 활용.

**Pass 2 — 4KB Page 집계:** 개별 4KB page는 DSA 이점을 얻지 못하므로 (32KB 미만), 여러 4KB page를 `batch_size` 단위로 묶어 하나의 batch descriptor로 제출. Round-robin으로 WQ 간 균등 분배.

**"Shortboard effect" (균형 원칙):** 각 WQ에 할당되는 총 transfer size 차이가 4KB 이하가 되도록 batch_size를 계산. `batch_size = nr_base_pages / limit_chans`. 코너 케이스 (batch_size < 2): 남은 4KB page를 각 WQ에 직접 submit.

**비동기 처리 메커니즘:**
- Submit 후 busy-polling 대신 Linux kernel의 `completion` 메커니즘 사용
- DSA 하드웨어 완료 시 MSI-X 인터럽트 발생 → `idxd_wq_thread`가 pending descriptor 스캔 → callback 호출 → `completion` signal
- `wait_for_completion_timeout`으로 migration 스레드 block 해제

**Descriptor 최적화:**
- per-cpu 전역 변수로 descriptor(`idxd_desc`, `dsa_hw_desc`, `dsa_completion_record`)를 미리 할당 → 동적 할당 오버헤드 제거
- DMA interface 우회: 물리 주소를 직접 descriptor에 기록 (page fault 불가 확인)

### 3.4 DSA 파라미터 적응형 튜닝

`limit_chans` (사용할 DSA/WQ 개수): 기본 8 (power-of-two), `sysfs` API로 동적 변경 가능. 각 DSA device = 4 PE + 1 WQ → WQ와 device가 1:1 대응.

`batch_size`: 페이지 리스트의 4KB page 개수에 따라 자동 계산. WQ 개수로 균등 분할.

### 3.5 Strawman 솔루션과 실패 이유

| 접근법 | 문제점 |
|--------|--------|
| DMA 인터페이스로 DSA 사용 | buffer (un)map, descriptor 준비에 88ns 추가 → fine-grained 4KB migration에 부적합 |
| 4KB = CPU, 2MB = DSA 분리 경로 | 4KB page는 DSA 이점 없음, dual path 관리 오버헤드 |
| User-space UMONITOR/UMWAIT | kernel-space에서 사용 불가, 진정한 async 아님 (CPU 저전력 상태 유지) |
| sched_yield polling 회피 (DTO) | 응답성 희생 |

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

- **기반 커널:** Linux 5.13/5.15 (MEMTIS, TPP 호환)
- **DSA 가속 모듈:** `misc/exp` 하위에 별도 모듈. `dsa_multi_copy_pages`, `dsa_copy_page_lists` API 노출
- **코드 규모:**

| 구성요소 | LoC |
|----------|-----|
| Memory management + DSA acceleration | ~2K |
| IDXD / IOMMU driver (kernel 6.4 → 5.x backport) | ~8K |
| **합계** | **~10K** |

- **인터페이스:**
  - `sysfs` API로 기능 toggle 및 `limit_chans` 조정
  - `procfs`로 통계 모니터링 (migration 횟수, DSA 상태 등)
- **기타 tiering system 연동:** TPP+, NOMAD+, AutoNUMA+ — 유사한 DSA 통합 방식으로 다른 시스템에도 적용 가능

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2025ATC-summarize/dsa-2lm-a-cpu-free-tiered-memory-architecture-with-intel-dsa.md|전체 요약 보기]]
