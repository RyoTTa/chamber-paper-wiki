---
tags: [paper, 2024, 2024MICRO, topic/dram, topic/rowhammer]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024MICRO-summarize/self-managing-dram-a-low-cost-framework-for-enabling-autonomous-and-efficient-dram-maintenance-operations.md"
---

# Self-Managing DRAM: A Low-Cost Framework for Enabling Autonomous and Efficient DRAM Maintenance Operations

**Venue:** 
**저자:** 

## 개요

### 1.1 DRAM Maintenance Operations의 현황과 문제점

현대 DRAM 칩은 안정적인 동작을 위해 3가지 주요 유지보수 작업(maintenance operations)을 필요로 한다:

1. **DRAM Refresh:** 주기적으로 셀의 전하를 복원하여 데이터 유지 (DDR4: 64ms 주기, rank당 410ns 소모)
2. **RowHammer Protection:** 특정 row의 반복적 활성화가 인접 row의 bit flip을 유발 → DRAM 내 TRR(Target Row Refresh)로 방어
3. **Memory Scrubbing:** on-die ECC로 교정 가능한 오류가 누적되어 uncorrectable이 되기 전 주기적 스캔·교정

**근본적 문제 1: 긴 표준화 주기.** 새로운 maintenance operation을 구현하거나 기존 것을 수정하려면 DRAM 인터페이스 변경이 필요하며, 이는 JEDEC 표준화 과정을 거쳐야 한다:
- DDR3→DDR4: 5년, DDR4→DDR5: **8년**
- DDR5에서 추가된 SBR (Same Bank Refresh), RFM (Refresh Management), PRAC, in-DRAM scrubbing 모두 새로운 DRAM 커맨드와 인터페이스 변경 요구

**근본적 문제 2: Maintenance로 인한 성능 저하.** Maintenance operation 실행 중에는 DRAM이 메모리 요청을 서비스할 수 없음:
- DDR4: rank 전체가 410ns 동안 접근 불가 (per-rank refresh)
- DDR5: 모든 bank group의 해당 bank가 190ns 동안 접근 불가
- DRAM 기술 스케일링에 따라 refresh 주기는 더 짧아지고(64→32→16ms), 새로운 maintenance도 추가되어 성능 영향 증가 추세

**Strawman: DARP/DSARP의 한계.** DSARP [19]는 subarray 단위로 refresh와 접근을 병렬화할 수 있지만, 여전히 메모리 컨트롤러가 각 maintenance operation마다 DRAM 커맨드를 발행해야 해서 커맨드 버스 점유 및 지연 발생. 또한 새로운 maintenance 유형마다 인터페이스 변경 필요.

### 1.2 핵심 통찰

현재 DDRx 인터페이스는 **완전한 Master-Slave** 관계 — 메모리 컨트롤러가 DRAM의 모든 동작을 통제하며, DRAM 칩은 자율적으로 아무것도 할 수 없다. 이 아키텍처적 제약이 DRAM 혁신의 속도를 제한한다.

**핵심 아이디어:** DRAM 칩에 자율적으로 maintenance operation을 수행할 수 있는 "breathing room"을 제공하면, (1) 새로운 maintenance mechanism 구현이 DRAM 인터페이스 변경 없이 가능해지고, (2) maintenance와 memory access의 병렬화를 통해 성능 오버헤드를 최소화할 수 있다.

## 방법론

### 3.1 실험 방법론

| 항목 | 구성 |
|------|------|
| Simulator | Ramulator (cycle-accurate), CPU-trace driven |
| Energy | DRAMPower |
| Processor | 4GHz, 4-wide issue, 128-entry instruction window, 1-4 cores |
| LLC | 4 MiB/core, 8-way |
| MC | 64-entry read/write queue, FR-FCFS-Cap (Cap=7) |
| DRAM | DDR4-3200, 4 channels, 2 ranks, 4/4 bank groups/banks, 128K-row bank, 512-row subarray, 8 KiB row |
| Refresh period | 32 ms (default), 16/8/4 ms (sensitivity) |
| Workloads | 62 single-core (SPEC CPU2006/2017, TPC, STREAM, MediaBench) + 60 four-core (multi-programmed, 3 intensity levels) |
| SMD config | 16 lock regions/bank, ARI=62.5ns, RG=8, N=8, ACT_max=512, scrubbing period=5min |
| Baselines | DDR4 baseline (per-rank refresh), DARP-Combined, DSARP-Combined, No-Refresh |

### 3.2 성능 결과

**단일 코어 (22개 memory-intensive workloads, Fig. 6):**

| Configuration | 평균 Speedup |
|--------------|-------------|
| SMD-FR | 4.8% |
| SMD-FR + SMD-DRP | 4.8% |
| SMD-FR + SMD-MS | 5.0% |
| SMD-Combined | **5.0%** |
| No-Refresh (oracle) | — (84.7% 달성) |

SMD-DRP(ACT_max=512)와 SMD-MS(5분 scrubbing 주기)의 오버헤드가 거의 완전히 가려짐 → SMD-FR 대비 추가 성능 저하 0.1% 미만.

**멀티코어 (60개 four-core workloads, Fig. 7):**

| Intensity | SMD-Combined 평균 Speedup | No-Refresh 대비 |
|-----------|--------------------------|-----------------|
| 4c-low | 1.3% | 88.8% |
| 4c-medium | 5.1% | — |
| 4c-high | **8.9%** (최대 10.5%) | **88.3%** |

**State-of-the-art 비교 (4c-high, Fig. 9):**
- SMD-Combined vs DARP-Combined: **8.6% speedup**
- SMD-Combined vs DSARP-Combined: **4.1% speedup**

SMD가 DSARP보다 우수한 이유: (1) maintenance-access parallelization, (2) MC가 maintenance 커맨드를 발행할 필요 없음 → command bus contention 제거. DSARP는 여전히 per-bank refresh command 등으로 bus를 점유.

### 3.3 에너지 소비 (Fig. 8)

| Workload | SMD-Combined DRAM Energy 감소 | No-Refresh 대비 |
|----------|------------------------------|-----------------|
| Single-core | 2.2% | — |
| 4c-medium | 4.8% | — |
| 4c-high | **4.3%** | 59.6% |

에너지 감소 요인: (1) 실행 시간 단축으로 background energy 감소, (2) power-hungry DDRx bus에서 REF 등 maintenance command 제거.

### 3.4 Ablation Studies

**Lock Region 개수 영향 (Fig. 11, 4c-high):**
- 2→256개로 증가: speedup 1.8%→10.0%
- 16개가 256개의 **88.8%** speedup 제공 → diminishing returns
- 1개(bank-level lock): **3.9% slowdown** — maintenance-access parallelization 불가, ACT_NACK rate: 1/11.7 ACTs (16개일 때 1/134.6)

**Refresh 주기 영향:**
- 4ms refresh 주기 (rank 70.9% 시간이 refresh에 소비): SMD가 baseline 대비 **3.6× speedup**
- Per-bank refresh baseline 대비도 **1.7× speedup** → 미래 DRAM의 더 짧은 refresh 주기에 SMD의 이점이 더욱 증가

**코어 수 영향:** 1/2/4/8-core 모두 8.0~8.7% speedup → 코어 수에 관계없이 일관된 이득.

**SMD vs MC-based Scrubbing (Fig. 12):**

| Scrubbing Period | MC-based Slowdown | SMD-MS Slowdown |
|-----------------|-------------------|-----------------|
| 1 hour | 0.7% | 0.1% |
| 5 min | 1.0% | 0.1% |
| 1 min | **1.5%** (최대 2.4%) | **0.2%** (최대 0.3%) |
| 10 sec | **8.8%** (최대 14.3%) | **1.1%** (최대 1.8%) |

MC-based scrubbing은 데이터를 칩 밖으로 이동시켜야 하므로 높은 scrubbing rate에서 prohibitively expensive. SMD-MS는 칩 내부에서 완결하여 훨씬 효율적.

**SMD-PMP (Pause Maintenance Policy):** 진행 중인 maintenance를 중단하고 ACT를 우선 서비스. SMDPMP-FR이 SMD-FR보다 4c-high에서 0.4% 높은 speedup — ACT_NACK rate 2% 감소.

### 3.5 Variable Rate Refresh 및 Probabilistic RowHammer (Extended version [139])

- **SMD-VR:** RAIDR [20] 기반 가변 refresh rate → 4c-high에서 9.2% speedup, No-Refresh의 **91.2%** 달성
- **SMD-PARA:** PARA [12] 기반 확률적 RowHammer 방어(1% 확률로 2개 victim refresh) → SMD-FR과 결합 시 4c-high에서 4.7% speedup, RH threshold ≈3500까지 방어

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1 DRAM 인터페이스 변경

| 방식 | 설명 |
|------|------|
| **alert_n 재활용** | 기존 DDR4/5 alert_n pin으로 ACT_NACK 전송. 추가 pin 불필요하나, 다중 의미 부여로 MC 설계 복잡도 증가, open drain 신호의 느린 set/reset |
| **신규 pin 추가** | 단일 uni-directional pin. 채널당 1개 pin (rank-based 설계). high-end 12채널 시스템: 96 pins → 이미 6K+ pin 시스템에서 1.6% 증가 |

### 4.2 DRAM 칩 면적 오버헤드 (22nm, 45.5 mm² DRAM 칩 기준)

| Component | 면적 | 비율 |
|-----------|------|------|
| LRB (bank당 16비트) | 32 µm²/bank | 0.001% |
| RA-latches (per lock region) | — | **1.1%** |
| SMD-FR 로직 | 77.1 µm² | <0.1% |
| SMD-DRP (Counter Table, ACT_max=512) | 3.2 mm² | 7.0% |
| SMD-MS 로직 | 77.1 µm² | <0.1% |

SMD-DRP의 높은 면적은 Graphene의 CAM 구조 때문 — 더 저렴한 RowHammer 방어 기법(예: PARA)으로 대체 가능.

### 4.3 메모리 컨트롤러 변경

- ACT_NACK 처리: ARI timing parameter 적용, bank 상태를 precharged로 표시
- Locked region tracking: rank(1bit) + bank(4bits) + lock region(4bits) = 9 bits/bank → dual-rank x8 module에서 총 **288 bytes**
- 기존 request scheduler(FR-FCFS) 재활용, Cap=7로 column access 제한
- Address mapping 변경 불필요 (SMD-FR이 alternative mapping에서도 8.7% speedup)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]


## 전체 요약

[[../paper-summaries/2024MICRO-summarize/self-managing-dram-a-low-cost-framework-for-enabling-autonomous-and-efficient-dram-maintenance-operations.md|전체 요약 보기]]
