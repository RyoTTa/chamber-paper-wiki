---
tags: [paper, 2024, 2024OSDI, topic/cache, topic/disaggregation, topic/dram, topic/memory-tiering, topic/nvm, topic/virtual-memory]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024OSDI-summarize/osdi24-zhong-yuhong.md"
---

# Managing Memory Tiers with CXL in Virtualized Environments

**Venue:** 
**저자:** Yuhong Zhong (Columbia Univ. / Microsoft Azure), Daniel S. Berger (Microsoft Azure / Univ. of Washington), Carl Waldspurger (Carl Waldspurger Consulting), Ryan Wee (Columbia), Ishwar Agarwal, Rajat Agarwal, Frank Hady, Karthik Kumar (Intel), Mark D. Hill (Univ. of Wisconsin–Madison), Mosharaf Chowdhury (Univ. of Michigan), Asaf Cidon (Columbia Univ.)

## 개요

### 1.1 클라우드 환경의 Tiered Memory Needs

퍼블릭 클라우드에서 VM 메모리 크기는 지속 증가 (4-32GB/vCPU)하나, DDR 채널로 접근 가능한 DRAM 용량은 물리적 한계로 인해 core 수 증가를 따라가지 못한다. DIMM은 서버 비용의 가장 큰 단일 요소이며 embodied carbon의 41%를 차지한다.

**CXL 메모리는 해결책을 제공한다:**
- PCIe 버스를 통한 DRAM/NVM 접근 → 대용량 확장
- DDR4 → CXL 재활용으로 TCO, carbon emission 절감 (40% CXL 시 embodied carbon 20%+ 절감 [83])
- CXL.mem은 cacheable load/store로 직접 접근 (RDMA보다 order-of-magnitude 빠름)

**CXL latency penalty:** 5세대 Xeon 기준 CXL이 local DDR5의 2.02× load-to-use latency를 가짐. 하지만 대부분의 워크로드는 이 차이에 둔감 → 효율적 tiering이 핵심.

### 1.2 Software-managed Tiering의 한계 (Azure 실무 경험)

기존 software tiering (TPP, MEMTIS, Nimble 등)은 virtualized environment에서 세 가지 치명적 문제가 있다.

**Problem 1 — High host CPU cost:**
- Instruction sampling (PEBS)은 VM에서 미지원 + privacy 문제
- Page table 기반 tracking은 host CPU cycle을 과도하게 소모
- **TPP 실측:** 7.5GB DRAM + 2.5GB CXL에서 FASTER+YCSB-A 실행 시 **거의 1코어 전체를 소모** (kswapd의 access-bit scanning)
- Figure 1: spatial locality가 VM 환경에서 사라짐 — fresh VM에서는 locality 있으나, free page randomization / warm VM에서는 소멸

**Problem 2 — Coarse-grained data placement (page granularity):**
- 많은 애플리케이션이 spatially-sparse access pattern → page 내 일부 cacheline만 hot
- Cloud에서는 2MB/1GB huge page 사용 → 문제 악화
- Figure 2 실증: FASTER+YCSB-A, 25% DRAM 시 2MB page size가 4KB 대비 **throughput 25% 저하** (coarse placement)
- Google production cluster에서도 huge page로 인한 cold page identification 문제 보고 [61]

### 1.3 Hardware-managed Tiering과 2LM의 한계

2LM (Intel Optane Memory Mode): DRAM을 NVM의 inclusive direct-mapped cache로 사용 → SW overhead 없고 cacheline granularity이나, **inclusive design이 capacity 낭비**.

예: 600GB DDR5 + 1000GB CXL → 2LM에서는 1000GB만 usable (600GB 낭비). Cloud provider들은 fast tier를 크게 provisioning하므로 특히 비효율적.

## 방법론

### 3.1 Page Coloring for Local DRAM Isolation (§4.1)

Page coloring의 CXL adaptation: physical memory lines가 동일 local memory line에 매핑되는 page들은 **항상 동일 VM에 할당**. 각 VM은 자신과만 conflict → inter-VM interference 완전 제거.

**구현:** Host Linux kernel의 free-page management + page allocator 수정. 동일 local DRAM page에 매핑되는 physical page들을 grouping.

### 3.2 Online Slowdown Estimator — Outlier Detection (§4.2)

**Challenge:** Local memory miss rate은 MC 수준에서만 측정 가능 (system-wide). Per-core/per-VM miss rate 직접 측정 불가.

**Key insight — MPKI proxy:**
- Local memory MPKI (misses per thousand instructions)는 application slowdown과 r²=0.73 상관관계 (Figure 9a)
- Demand load L3 miss latency가 **local memory miss ratio와 r²=0.87 선형 상관관계** (Figure 9b)
- Intel® Flat Memory Mode는 hit/miss latency가 안정적 → L3 miss latency로 miss ratio 추정 가능
- Estimated miss ratio × main memory request count ÷ instruction count = estimated MPKI

**Random Forest classifier:**
- Binary classifier (>5% slowdown 여부 판별)
- 5개 feature: (a) estimated MPKI, (b) L3 miss latency of demand loads, (c) L2 miss latency of demand loads, (d) data TLB load miss latency, (e) L2 MPKI of demand loads
- 100 decision-tree estimators
- **Train accuracy: 100%, Validation accuracy: 88%** (MPKI 단독: 63%)

### 3.3 Dynamic Page Allocator (§4.3, Listing 1)

10초 interval로 동작:
1. `perf`로 각 VM의 성능 이벤트 측정 → EWMA smoothing (α=0.2)
2. Random Forest로 outlier VM 식별
3. VM 정렬: outlier > non-outlier, 동일 그룹 내에서는 avg miss count 높은 순
4. **Page migration:** 최하위 VM → 최상위 VM으로 dedicated page migration. `stepRatio` (10%)까지. Conflicting page pair는 항상 함께 이동.

**VM launch/termination:**
- Terminating VM: active list에서 제거 후 셧다운
- New VM: 전체 시스템과 동일 비율로 dedicated/hardware-tiered page 할당. 기존 VM들이 균등하게 dedicated page 제공/수용

**Hotness-based allocation (평가 결과 부정적):** DAMON으로 guest physical page hotness 추적 → hot region에 dedicated page 할당. 그러나 overhead가 benefit을 초과 (software tiering과 유사한 이유). **Default는 random assignment.**

## 핵심 기여

**핵심 기여:**
1. **Intel® Flat Memory Mode:** 최초의 CXL용 hardware-managed memory tiering. MC 내 cacheline granularity, exclusive placement, mixed mode 지원
2. **Virtualized 환경에서 SW tiering의 한계 체계적 분석:** host CPU overhead, page granularity 문제 (특히 huge page), inter-VM interference
3. **Memstrata:** HW-managed tiering 위에 구축된 lightweight SW stack. Page coloring으로 inter-VM isolation, random forest 기반 online outlier detection, dynamic dedicated page allocation

**Broader significance:**
- HW + SW co-design 패러다임: HW는 low-overhead fine-grained tiering, SW는 application-level performance awareness 제공
- CXL latency가 2×임에도 **82% workload가 ≤5% slowdown** — CXL 도입의 practical feasibility 입증
- TPP와의 비교에서 HW tiering의 우수성 입증 (TPP는 VM 내부 visibility라는 unfair advantage에도 불구하고 thrashing으로 인한 catastrophic failure)
- Page coloring의 CXL adaptation으로 inter-VM side channel 방지까지 가능
- Memstrata의 online approach는 VM 간 page migration을 통해 4% single-core overhead로 outlier → <6% slowdown 달성

## 주요 결과

| Component | Language | LoC |
|-----------|----------|-----|
| Host Linux kernel (v5.19) — page coloring + exchange_pages syscall | C | 2,729 |
| QEMU (v6.2) — guest memory preallocation | C | 60 |
| Memstrata userspace process | C++ | 2,190 |
| **Total** | | **~5K** |

**exchange_pages(pid_1, pid_2, page_arr_1, page_arr_2, num_pages) syscall:**
- migrate_pages() 기반. temporary page로 첫 페이지 이동 → 두 번째 페이지를 첫 위치로 → 임시 페이지를 두 번째 위치로
- Linux MMU notifier로 guest page table과 host page table 동기화
- 같은 프로세스 내 page 교환도 지원 (pid_1 == pid_2)

**Userspace process:** perf로 이벤트 수집, ONNX로 ML 모델 실행, POSIX message queue로 VM scheduler 연동.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2024OSDI-summarize/osdi24-zhong-yuhong.md|전체 요약 보기]]
