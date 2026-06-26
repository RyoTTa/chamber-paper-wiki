---
tags: [paper, 2025, 2025HPCA, topic/dram, topic/rowhammer, topic/security, topic/storage]
venue: "HPCA 2025"
year: 2025
summary_path: "../paper-summaries/2025HPCA-summarize/qprac-towards-secure-and-practical-prac-based-rowhammer-mitigation-using-priority-queues.md"
---

# QPRAC: Towards Secure and Practical PRAC-based Rowhammer Mitigation using Priority Queues

**Venue:** HPCA 2025
**저자:** Jeonghyun Woo, Shaopeng (Chris) Lin, Prashant J. Nair, Aamer Jaleel, Gururaj Saileshwar (UBC, NVIDIA, Univ. of Toronto)

## 개요

JEDEC DDR5 spec(2024년 4월)은 PRAC(Per Row Activation Counting) framework를 도입: DRAM row당 activation counter + ABO(Alert Back-Off) protocol로 필요 시 RFM 요청. 그러나 구체 구현은 DRAM vendor에 위임되어 있어, **기존 PRAC 구현들은 insecure하거나 impractical함**.

### 1.1 Panopticon의 취약성 (Insecure)

Panopticon[Bennett+ DRAMSec'21]은 FIFO-based service queue를 사용. 두 가지 공격에 취약:

**Toggle+Forget Attack (t-bit toggling exploit):** Panopticon은 counter의 threshold bit(t)가 toggle될 때만 row를 queue에 삽입. ABOACT=3 activation(window of normal traffic 180ns/tRC) 동안 queue가 가득 차면 target row가 queue를 bypass → t-bit가 toggle된 상태이므로 다음 2^t activation까지 다시 삽입되지 않음 → **100K회 이상 unmitigated activation 가능** (sub-100 TRH 기준 100× TRH).

**Fill+Escape Attack (FIFO queue exploit):** Full counter comparison으로 t-bit 문제를 해결해도 FIFO queue의 한계는 남음. Attacker가 Q개 row를 M-1회 activate → Q개 row를 1회씩 더 activate하여 queue를 가득 채움 → Alert 발생 → ABOACT 3회로 target row hammer (queue full이라 bypass) → RFM 후 최대 5개 entry 제거 → 다시 5개 row로 queue 채우기 → 반복. **최소 1283회 unmitigated activation (M=512 기준).** Threshold가 낮을수록 더 심각.

### 1.2 UPRAC의 비현실성 (Impractical)

UPRAC[Canpolat+ DRAMSec'24]는 service queue 없이 Alert 시 **모든 DRAM row의 counter를 scan하여 top-N row 식별** 제안. 128K rows/bank에서 row당 52ns activation → millisecond 단위의 search time → impractical. FIFO queue를 추가하면 Fill+Escape Attack에 취약.

**핵심 질문:** FIFO queue 없는 설계는 impractical, FIFO queue 있는 설계는 insecure → **PRAC specification 내에서 secure & practical한 queue 설계가 가능한가?**

## 방법론

### 3.1 Methodology

| Component | Configuration |
|-----------|--------------|
| Simulator | Ramulator2 (cycle-accurate) |
| CPU | 4-core OoO, 4GHz, 4-wide, 352-entry ROB |
| LLC | 8MB, 8-way, 64B lines |
| Memory | DDR5 6400MT/s, 1ch, 2 ranks, 8 bank groups × 4 banks, 128K rows/bank (8KB), 64GB |
| PRAC timings | tRC=52ns, tRP=36ns, tRCD/tCL=16ns, ABOACT=180ns, tRFMab=350ns |
| N_BO sweep | 16, 32, 64, 128 (default 32) |
| PRAC level | 1, 2, 4 RFMs/Alert (default 1) |
| Benchmarks | SPEC2006, SPEC2017, TPC, Hadoop, MediaBench, YCSB → 57 apps, 4-core homogeneous |

### 3.2 Performance (N_BO=32, PRAC-1)

| Configuration | Avg Slowdown |
|--------------|-------------|
| QPRAC-NoOp (opportunistic 없음) | 12.4% |
| QPRAC (opportunistic) | 0.8% |
| QPRAC+Proactive | **0%** |
| QPRAC+Proactive-EA (default) | **0%** |
| QPRAC-Ideal | **0%** |

### 3.3 N_BO Sensitivity

| N_BO | QPRAC | QPRAC+Proactive | Secure TRH (PRAC-1) |
|------|-------|-----------------|---------------------|
| 16 | 2.3% | 0.3% | 57 |
| 32 | 0.8% | **0%** | 71 |
| 64 | <0.5% | 0% | 103 |
| 128 | <0.5% | 0% | 181 |

Default N_BO=32 권장: proactive mitigation 없이도 <1% slowdown, TRH=71.

### 3.4 PRAC Level Sensitivity (1/2/4 RFMs per Alert)

QPRAC: 0.8%/0.8%/0.9% for PRAC-1/2/4. Proactive variants: 모두 0%. PRAC-2,4는 Alert frequency가 1.9×, 3.3× 감소하여 RFM duration 증가를 상쇄.

### 3.5 PSQ Size Sensitivity (1~5 entries)

모든 size에서 <1% overhead. Larger=better (mitigation 기회 증가). Default 5는 PRAC-4 + proactive 지원.

### 3.6 Performance Attack Resilience

Multi-bank hammering으로 Alert frequency 극대화. RFMab(all-bank RFM) 기준 worst-case bandwidth loss:

| N_BO | QPRAC-RFMab | QPRAC+Proactive | RFMsb | RFMpb |
|------|-------------|-----------------|-------|-------|
| 16 | 93% | 91% | 68% | 27% |
| 32 | 77% | 77% | 42% | 15% |
| 64 | 62% | 10% | — | — |
| 128 | 32% | 0% | — | — |

> RFMpb(per-bank RFM) 명령 도입 시 N_BO=32에서 bandwidth loss 15%로 감소. DRAM interface 수정 필요.

### 3.7 Storage & Energy

- **PSQ Storage:** 5 entries × (17-bit RowID + 7-bit Ctr) = 15 bytes per bank. Area: 0.038mm² (10nm DRAM process). In-DRAM per-row counter는 7-bit → 0.05% of DDR5 chip.
- **PSQ Latency:** Counter increment, comparison, insertion: 2.5ns (45nm CMOS), Precharge(36ns) shadow → zero overhead.
- **PSQ Energy:** 0.23µJ per ACT (0.05% of activation energy), static power 0.38mW/chip.

| PRAC Level | QPRAC | QPRAC+Proactive | QPRAC+Proactive-EA |
|------------|-------|-----------------|-------------------|
| PRAC-1 | 1.2% | 14.6% | **1.9%** |
| PRAC-4 | 1.5% | 14.6% | **1.9%** |

### 3.8 타 기법 비교

**Mithril[HPCA'22]:** TRH≤512에서 급격한 성능 저하 (TRH=64→69%, 128→54%, 256→32%, 512→10%). 5,300-entry CAM/bank 필요 → impractical. QPRAC: 5-entry CAM/bank, 모든 TRH에서 0% overhead.

**PrIDE[ISCA'24]:** TRH=64→54%, 128→32%, 256→19%, 512→7%. Probabilistic → 보장 없음.

**MOAT[HPCA'25] (concurrent):** Dual-threshold, single-entry queue. N_BO=32에서는 유사 (<1%), N_BO=16에서 QPRAC 2.3% vs MOAT 3.6%. QPRAC+Proactive 0.1% vs MOAT+Proactive 0.7%.

**Storage 비교 (per-bank SRAM, TRH=100):** Misra-Gries 1700KB, TWiCe 12MB, CAT 7.84MB, **QPRAC 15 bytes**.

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

- C++ code integrated with Ramulator2
- Python scripts for security analysis (Equation 2, 3 evaluation)
- Security evaluation: ~2 hours
- Performance evaluation: ~16 hours (1000-core cluster)
- Open source: https://github.com/sith-lab/qprac, https://doi.org/10.5281/zenodo.14336354

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]
- [[paper-wiki/concepts/security.md|Security]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2025HPCA-summarize/qprac-towards-secure-and-practical-prac-based-rowhammer-mitigation-using-priority-queues.md|전체 요약 보기]]
