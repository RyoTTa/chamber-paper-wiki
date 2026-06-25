---
tags: [paper, 2025, 2025MICRO, topic/dram, topic/storage]
venue: "MICRO 2025"
year: 2025
summary_path: "../paper-summaries/2025MICRO-summarize/dram-fault-classification-through-large-scale-field-monitoring-for-robust-memory-ras-management.md"
---

# DRAM Fault Classification through Large-Scale Field Monitoring for Robust Memory RAS Management

**Venue:** MICRO 2025
**저자:** Hoiju Chung, Euisang Oh, Seungmin Baek, Hyeongshin Yoon, Jaesung Yoo, Sanghwan Lee (SK hynix America), Yongjun Lee, Arhatha Bramhanand, Brett Dodds (Microsoft), Yang Zhou, Nam Sung Kim (University of Illinois Urbana-Champaign)

## 개요

DRAM 기술이 scaling 됨에 따라 in-field 신뢰성 유지가 점점 더 어려워지고 있다. 기존 field study들은 DRAM error behavior를 분석했으나, DIMM 및 DRAM architecture의 계층적 구조를 충분히 반영하지 못해 fault 원인 추론과 RAS action 선택의 정확도가 제한된다.

**정량적 동기:**
- DRAM scaling이 slowing → heightened susceptibility to faults [22]
- 기존 error classification은 memory controller ECC에 의해 capture된 error만으로 패턴 분류 → DRAM architecture 주소 체계를 고려하지 않음
- DDR5 도입으로 in-DRAM ECC(IDECC)가 field error log를 distort → classification 더욱 복잡

**연구 목표:**
1. DRAM type/technology node에 무관한 **hierarchical fault classification methodology** 수립
2. DDR5 IDECC 환경에서의 error behavior characterization (server용 최초)
3. Fault type별 최적 memory RAS action mapping 규칙 정의
4. DRAM vendor domain knowledge를 안전하게 공유하는 시스템 구현 (DRAM Fault Analyzer)

---

## 배경 지식

### DRAM Module Architecture (Figure 1)

**DDR4 2Rx4 ECC RDIMM:**
- 2 rank × 18 DDR4 x4 DRAM chips (16 data + 2 ECC)
- DIMM DQ ↔ DRAM DQ mapping이 DIMM type별로 다름 (swizzling)
- RCD(Register Clock Driver)가 address signal inversion 수행 (side L/R, rank 0/1)

**DDR5 2Rx4 ECC RDIMM:**
- Channel이 2개의 독립 sub-channel로 분할 → higher MLP
- Sub-channel 당 8 data chips + 2 ECC parity chips (DDR5 10x4)
- PMIC on-DIMM

### DDR4 x4 DRAM Device Architecture (Figure 2, 3)

- 4 Bank Groups(BG) → BG당 4 banks → bank 내 2D MAT array
- MAT: N_BL(=1024) Bit Lines × N_SWL(=X) Sub-Word Lines 크기의 cell array
- RowMAT: WL 방향으로 N_RowMAT(=Y)개 MAT, ColMAT: BL 방향으로 N_ColMAT(=8)개 MAT
- RowDec → MWL(Main Word Line) + FX//FX(pre-decoded signals) → SWD(Sub-Word Line Driver)가 SWL 구동
- Even-address row: 4 SWDs per RowMAT (각각 2 SWLs 구동), Odd-address row: 5 SWDs (3 Type-1 각 2 SWL + 2 Type-2 edge 각 1 SWL)
- 1024×8 BLSA가 RowMAT 간 배치

**Two Device Architectures:**
- **Device A:** RA[m] 비트에 따라 MAT[3:0] 또는 MAT[7:4]의 32비트가 bank → external I/O로 전송 (burst-aligned)
- **Device B:** RA[m]에 따라 각 MAT의 upper/lower 4비트를 모든 8개 MAT에서 선택 → 4 DQ × 8 beats
- burst length = 8 → 4 DQ × 8 edges = 32-bit per read

### DDR5 x4 DRAM Architecture (Figure 4, 5)

DDR4 대비 5가지 차이:
1. 8 Bank Groups (2배)
2. RowMAT 당 parity MAT (N_BL/2 크기) → IDECC용
3. burst length = 16 (2배)
4. MAT당 16-bit 선택 + parity MAT 8-bit → 128-bit당 single-bit error 정정
5. **DQ-aligned architecture:** RA[m]에 따라 even/odd 4개 MAT가 4개 DQ에 16 beats 할당 → SWD fault가 하나의 DQ에만 error 발생 (burst-aligned와 달리 SWL/SWD boundary 동일) → system-level ECC가 두 개 DQ error까지 정정 가능

---

## DRAM Fault Classification Methodology (§4)

### 1. Spatial Fault Classification

**DRAM fault 정의:** "일정 observation period 동안 발생한 모든 errors를 포함하며, DRAM hierarchical architecture에 정렬되고, 고유한 temporal behavior pattern을 갖는 분류"

PA(Physical Address) → DA(DRAM Address) 변환 후 hierarchical boundary 식별.

**Spatial fault taxonomy (20 sub-classes):**

**Intra-bank faults (5 major types):**

| Type | Sub-classes | 조건 |
|------|------------|------|
| SA (Single Address) | SB, SAm | 1 RA + 1 CA |
| COL (Column) | BL, BLSA, CSL, Cpost | Multiple RA + 1 CA |
| ROW (Single Row) | SWL, SWD, Rpost | 1 RA + multiple CA |
| MROW (Multiple Row) | MWLb, MWLub, EAWLb, EEWLb, EEWLub | Multiple RA with specific patterns + multiple CA |
| MAT (Array MAT) | MR1C, MR1R, MR2b, MRMC1b, MR2post, MRMpost | Multiple RA + multiple CA |

**Bounded faults (핵심 개념, Figure 6-7):** 2×2 adjacent MATs 내에 confined된 fault (blue box). SWD, MWLb, EAWLb, EEWLb 포함.
- **SWD fault:** 2 adjacent MATs에 걸친 fault, 특정 beat에서 4 DQ에 16-bit error (Figure 7a). RA[0] 차이로 even/odd row 교차.
- **MWLb fault:** 2 adjacent RowMATs에 걸쳐 최대 4개 faulty row, RA interval = 2 (Figure 7b)
- **EAWLb fault:** 2 adjacent RowMATs, 2 faulty rows, RA interval = 8 (Figure 7c) — FX(i) 신호 결함
- **EEWLb fault:** 2×2 MATs, RA interval = 8 (Figure 7d) — 상위 row decoding 신호 결함

**Inter-bank faults:** Single-die(Data-line, Multiple-bank), Multiple-die(DIMM-IO, Rank, DIMM)

## 방법론

- 6h/12h/1d/2d/4d/8d/16d → 7-day에서 95% match rate, 이후 saturation
- 7-day 선택 근거: 충분한 patrol scrub reads 확보 + over-accumulation 방지

## 핵심 기여

1. **DRAM vendor 독점 domain knowledge를 활용한 refined fault classification methodology**를 수립하고 대규모 field data(~545B device-hours, ~9.1M DIMMs)로 검증.

2. **Bounded fault(2×2 MATs) 개념**을 정의하고, **in-field DRAM faults의 대부분(~99.5%)이 DRAM hierarchical architecture에 정렬**되며, 그 중 **100%가 bounded**임을 밝힘. 이는 향후 DRAM RAS 설계의 핵심 지표.

3. **DDR5 10x4 RDIMM**에서 IDECC의 영향을 최초로 체계적으로 분석: ~80% fault masking(SB 제거), ~20%는 system-level ECC coverage 내 유지. Unbounded faults의 DUE risk는 왜곡되지 않음 → **IDECC는 "good filter" 역할**.

4. **DUE risk 감지 후 30분 내 RAS action으로 최대 75% DUE 예방 가능** → 실시간 memory reliability management의 정량적 필요성 입증.

5. **DFA를 통한 안전한 domain knowledge sharing framework**를 실제 hyperscaler(Microsoft Azure)에 배포. 향후 LPDDRx, HBMx 등 rank operation이 없는 차세대 메모리의 RAS 설계에 direct implication 제공.

## 주요 결과

- IDECC가 single-bit error를 마스킹 → SB fault는 host에 보고되지 않음
- Mis-correction으로 인한 추가 bit-flip → CSLp, SWLp, SWDp, EAWLpb, EEWLpb 분류 추가

---

## Large-Scale Field Study Results (§5)

### Data Collection (Table 1)

| 항목 | 규모 |
|------|------|
| DDR4 RDIMMs (Device A, B) | ~8.3 million |
| DDR5 RDIMMs (Device C, D) | ~0.8 million |
| Total device-hours | ~545 billion |
| RDIMM types | 20+ (다양한 technology node, architecture) |
| Observation period | 7-day |

### DDR4 x4 RDIMM 결과 (Table 2)

**Intra-bank faults:**
- **99.5% 이상이 DRAM bank hierarchical architecture와 연관** (Key Insight 1)
- 기존 field study [42, 46] 대비 SA fault 비율 감소 → scaling limitation이 random fault보다 **clustered fault(ROW, MROW)로 발현**
- Clustered faults 중 **100%가 bounded faults (2×2 MATs 내)** → bounded fault의 error coverage가 memory subsystem 신뢰성의 pivotal factor
- SA fault sub-classes: Transient가 대부분, SBs>75%, SAm 약 5%

**Temporal stability (Figure 10):**
- 64-day operational period 동안 bounded → bounded 유지: **98.6%**
- Unbounded → unbounded 유지: **93.8%**
- Cross-transition(Bounded↔Unbounded): 0.0%, 2.4% → **분류 신뢰도 매우 높음**

**Time to Failure — DUE Prevention (Figure 11):**
- DUE risk 감지 후 30분 내 RAS action → Device A: **75%** DUE 예방, Device B: **~45%**
- 1일 내 action → Device A: 58%, Device B: 45%
- Exponential relationship → **신속한 RAS action의 중요성** (Key Insight 4)

### DDR5 10x4 RDIMM 결과

**Pseudo-DDR5 emulation (Figure 12-13, Table 3):**
- DDR4 Device B error log에 DDR5 IDECC bounded error 특성 적용 (JEDEC 표준)
- DDR4 → Pseudo-DDR5 transition:
  - **81.8% faults가 host에 미보고** (주로 SB fault → IDECC가 제거)
  - **4.3% misinterpreted** (주로 bounded fault → SAm으로 전환)
  - Unbounded faults(DUE risk 보유)는 largely unchanged → IDECC가 trivial errors filtering 역할 (Key Insight 3)
  - **SAm fault는 실제 ROW fault일 가능성** (Figure 13b: DIMM faults의 절반이 SAm으로 변환) → DDR5에서 SAm 감지 시 최소 ROW fault로 간주하고 RAS action 필요

**Real DDR5 field data (Table 4):**
- Device C, D: 93.9%, 82.9%가 architectural hierarchy 정렬
- DDR4 대비 SA fault 감소로 unbound fault 비율 상대적 증가 (절대적 증가 아님)
- DDR5 10x4 RDIMM은 system-level ECC가 125-bit mode에서 DUE probability ~10⁻¹² → 실제 DUE rate가 너무 낮아 통계적 Time-to-Failure 분석 불가
- 약 97%의 unbounded fault가 system-level ECC로 detect 가능 → IDECC가 전체 신뢰성을 저하시키지 않음

### Key Insight: Typical Faulty RA Patterns
- Bounded fault(2×2 MATs)는 특정 RA pattern 동반
- FX(i) 결함: RA interval = 8로 2 adjacent MATs에 걸친 fault
- MWLb: RA interval = 2, 최대 4개 row
- 이 패턴들은 DRAM architecture에서 inevitable한 structural addressing patterns → 미래에도 유사 fault는 동일 boundary 내에서 지속

---

## DRAM Fault Analyzer (DFA) (§6)

### Architecture (Figure 14)

3개 컴포넌트:
1. **Address Translator:** PA → DA 변환 + SWD boundary 초과 error pattern 감지 시 즉시 분석 trigger
2. **Fault Classifier:** §4 methodology로 spatial + temporal fault 분류
3. **RAS Action Advisor:** Fault type, platform ECC capability, DUE risk를 고려한 최적 RAS action 추천

DFA는 compiled object file 형태로 배포 → vendor domain knowledge 보호. **Microsoft Azure Data Centers에 배포 완료.**

### Memory RAS Actions (Table 5)

**Runtime actions (current power cycle):**
- sPPR(Soft Post Package Repair): 데이터 보존하며 row remapping, 빈번한 ROW fault에 적합
- Page off-lining(Poff): OS-level page retirement
- Bank sparing(BnkSpr): 전체 bank 비활성화

**Next power-cycle actions:**
- hPPR(Hard Post Package Repair): sPPR 기록 기반 영구 remapping
- DIMM initialization(INIT): full re-initialization
- DIMM removal(RMV)

**Fault별 권장 RAS action:**
| Fault Type | RAS Action | 근거 |
|-----------|------------|------|
| Transient/Sporadic SA | ECC에 의존 (scrubbing) | 자연 소멸 |
| SAm (DDR5) | sPPR or hPPR | 실제 ROW fault 가능성 (Table 5-1) |
| Sporadic MR1C | No action | Redundancy register upset, scrubbing 복구 (Table 5-2) |
| MRMpost | BnkSpr (inter-bank 확인 후) | Multiple row+column → bank-level 영향 (Table 5-3) |

### Log Sampling Frequency (Table 6)
- 10μs(event-driven) → 1s(polling/BMC) resolution 감소 시:
  - DDR4: incorrect RAS action **0%** (unbounded faults with DUE risk)
  - Pseudo-DDR5: underestimated boundary 0.2% (negligible)
  - Bounded fault의 boundary underestimation: DDR4 2.9%, DDR5 3.3% → acceptable range
- **Polling-based collection이 viable함** (Key Insight 2) → BMC 기반 시스템 구현 가능

---

## 구현 및 Deploy

- **DFA:** Microsoft Azure Data Centers에서 memory reliability management system의 integral component로 운영
- **DFACA (DFA Controlling Agent):** 주기적 log 분석 + Address Translator의 SWD boundary 초과 감지 시 immediate trigger
- **Methodology:** DDR4/DDR5 양쪽 모두에 적용 가능하며, LPDDRx/HBMx 등 rank operation이 없는 미래 메모리 기술로 확장 가능 (conclusion에 명시)

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2025MICRO-summarize/dram-fault-classification-through-large-scale-field-monitoring-for-robust-memory-ras-management.md|전체 요약 보기]]
