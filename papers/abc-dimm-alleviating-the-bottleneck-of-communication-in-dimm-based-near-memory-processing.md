---
tags: [paper, 2021, 2021ISCA, topic/dram, topic/near-data-processing, topic/virtual-memory]
venue: "ISCA 2021 (48th Annual IEEE/ACM International Symposium on Computer Architecture)"
year: 2021
summary_path: "../paper-summaries/2021ISCA-summarize/abc-dimm-alleviating-the-bottleneck-of-communication-in-dimm-based-near-memory-processing.md"
---

# ABC-DIMM: Alleviating the Bottleneck of Communication in DIMM-based Near-Memory Processing with Inter-DIMM Broadcast

**Venue:** ISCA 2021 (48th Annual IEEE/ACM International Symposium on Computer Architecture)
**저자:** Weiyi Sun (Tsinghua University), Zhaoshi Li (Tsinghua University), Shouyi Yin (Tsinghua University), Shaojun Wei (Tsinghua University), Leibo Liu (Tsinghua University)

## 개요

- 그래프 애플리케이션, 희소 행렬-벡터 곱셈(SpMV) 등 데이터 집약적 워크로드는 높은 메모리 용량과 데이터 전송 속도를 요구하지만, 메인 메모리 시스템의 핀 수 및 전력 제약으로 인해 대역폭 수요를 충족하기 어려움
- DIMM 기반 NMP(Near-Memory Processing)는 버퍼 칩에 가속기를 통합하여 높은 성능과 상대적으로 낮은 설계/제조 비용을 제공하지만, **메인 메모리 버스를 통한 DIMM 간 통신이 주요 병목**으로 부상
  - 포인트투포인트 통신 방식: DIMM 수(n)가 증가하면 DIMM당 대역폭이 **1/n**로 감소
  - DIMM 간 통신은 데이터를 CPU 캐시를 통해 2회 전송 → effective bandwidth가 **반으로 절감**
  - Chameleon-MapReduce 방식의 NMP에서 CPU Processing 단계의 통신 오버헤드가 전체 실행 시간의 **80% 이상** 차지
- 기존 DIMM 기반 NMP(Chameleon, MCN)는 통신 병목 문제를 해결하지 못하여 DIMM 수가 4개 이상일 때 성능 확장성이 급격히 저하

## 방법론

### 3.1. Broadcast-Process 프레임워크

- **실행 흐름** (Figure 10):
  1. **Broadcast 단계**: CPU가 각 DIMM의 부분 결과를 모든 DIMM에 브로드캐스트
  2. **NMP 단계**: 각 DIMM이 완전한 입력 데이터와 로컬 행렬을 사용하여 독립적으로 계산
  3. **동기화**: CPU가 모든 DIMM의 완료를 폴링 또는 인터럽트로 감지
- **반복형 워크로드** (PageRank 등): 새로운 반복 시작 시 이전 반복 결과를 브로드캐스트
- **비반복형 워크로드** (SpMV 등): 데이터 레이아웃 초기화 단계에서 브로드캐스트 사용
- **범용성**: 분할-정복 패러다임으로 변환 가능한 많은 워크로드에 적용 가능
- **브로드캐스트 비율**: 반복형 알고리즘에서 **100%** 도달 가능, 비반복형에서는 N채널 기준 N/(N+1) × 100%

### 3.2. Intra-Channel Broadcast 메커니즘

- **Broadcast-Write (WRB)**:
  - CPU MC에서 채널 내 모든 rank에 데이터를 동일한 주소에 기록
  - 일반적인 DDR Write와 달리 하나의 명령으로 모든 rank에 동시 기록 → C/A 대역폭 최소화
  - 각 rank의 동일한 주소에 저장하여 브로드캐스트 대역폭 완전 활용
- **Read-Broadcast (RDB)**:
  - 소스 DIMM이 데이터를 버스에 전송的同时, 나머지 DIMM은 동일 데이터를 로컬 rank에 기록
  - 일반적인 DDR Read로 동작하지만, 나머지 DIMM은 Write 명령으로 처리
  - tCL - tCWL 간격만큼 지연 후 Write 명령을 발행하여 타이밍 일치
  - Broadcast-write의 이중 전송 오버헤드를 방지 (버스를 1회만 사용)
- **ACTB/PREB 명령**: 16-rank 채널에서 row miss 발생 시 32개 명령 발행 오버헤드를 해결하기 위한 브로드캐스트 버전의 ACT/PRE 명령

### 3.3. 하드웨어 구현

- **DDR4 C/A 신호 활용**: 3비트 Chip ID의 최상위 비트를 브로드캐스트 명령 표시에 활용
  - 8-layer DRAM 디바이스가 거의 제조되지 않으므로 최상위 비트를 안전하게 재사용
  - 새로운 모드 레지스터로 브로드캐스트 명령 활성화/비활성화 제어 가능
- **DIMM 버퍼 칩 수정** (Figure 13(b)):
  - C/A Translator: 브로드캐스트 명령을 일반 DDR 명령으로 변환
  - WRB → WR로 변환 (CS 신호로 모든 rank 동시 선택)
  - RDB → 소스 rank는 RD, 나머지 rank는 WR로 변환 (tCL - tCWL 지연 적용)
  - 명령 마스킹: 특정 rank의 브로드캐스트를 비활성화하여 다중 NMP 워크로드 환경 지원
- **호스트 메모리 컨트롤러 수정** (Figure 13(d)(e)):
  - 물리 주소 최상위 2비트를 브로드캐스트 플래그로 사용 (11: 브로드캐스트)
  - 주소 매핑 유닛: 브로드캐스트 트랜잭션을 NMP 친화적으로 매핑
  - 브로드캐스트 큐 및 스케줄러 추가
  - FSM/Fixed State Machine 수정: 브로드캐스트 관련 타이밍 제약 처리
  - tRTRS(rank-to-rank switching time) 고려한 아비트레이터 설계
- **ECC 및 C/A 패리티 체크 지원**:
  - NMP 단계: DIMM 내 compute unit의 ECC 활성화 MC가 처리
  - Broadcast-write: 호스트 MC가 ECC 체크 비트를 생성하여 모든 rank에 브로드캐스트
  - Read-broadcast: 'Delayed' ECC 방식 사용 (compute unit이 읽을 때 ECC 수행)
  - C/A 패리티: 모든 관련 rank에서 브로드캐스트 C/A를 병렬로 체크

### 3.4. 소프트웨어 구현

- **A指令 활용**:
  - Broadcast-write: `_mm256_stream_pd()` 사용 (캐시 우회, non-temporal store)
  - Read-broadcast: `_mm256_load_pd()` 사용 후 `_mm_clflush()`로 캐시라인 무효화
- **API 설계**:
  - 사용자 수준 API로 리소스 관리 및 정합성 보장 세부사항 캡슐화
  - OS 수준 가상-물리 주소 매핑으로 브로드캐스트 플래그 비트 설정
  - 캐시 잠금 기능을 활용한 인-캐시 버퍼 관리

## 핵심 기여

- **핵심 Contribution**: DIMM 기반 NMP의 통신 병목을 identified하고, inter-DIMM broadcast와 Broadcast-Process 프레임워크로 해결하는 하드웨어/소프트웨어 통합 솔루션 제시
- **성능**: 16코어 CPU 대비 **8.33배**, 기존 NMP 대비 **2.59~2.93배** speedup 달성
- **실용성**: DDR4 표준과의 호환성을 최우선으로 고려한 풀스택 구현으로 최소한의 시스템 수정으로 실현 가능
- **물리적 브로드캐스트**: 기존 DDR 메인 메모리 버스에 이미 존재하는 물리적 브로드캐스트 현상을 "저주에서 축복으로" 전환하는 독창적 접근
- **범용성**: Broadcast-Process 프레임워크가 다양한 그래프/희소 워크로드에 적용 가능하며, 희소성이 높은 데이터셋일수록 broadcast의 효과가 극대화

## 주요 결과

| 항목 | 내용 |
|------|------|
| **시뮬레이터** | Ramulator + zsim 통합 (호스트 CPU), 자체 SIMD 시뮬레이터 (DIMM 내 compute unit) |
| **기술 노드** | 14nm (28nm RTL 합성 결과에서 스케일링) |
| **DRAM** | DDR4-2133, 4Gb, x8 |
| **시스템 구성** | 4채널 × 8 DIMM × 2 ranks, 최대 32 DIMM |
| **Compute Unit** | SIMD 유닛 (1024비트, 1.2GHz), 768KB scratchpad, 256KB stream buffer |
| **면적** | SIMD: 0.386 mm², 메모리: 0.154 mm² (14nm 기준) |
| **전력** | SIMD: 295.6 mW, 메모리: 225.0 mW |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2021ISCA-summarize/abc-dimm-alleviating-the-bottleneck-of-communication-in-dimm-based-near-memory-processing.md|전체 요약 보기]]
