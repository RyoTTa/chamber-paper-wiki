---
tags: [paper, 2025, 2025ASPLOS, topic/cache, topic/dram, topic/virtual-memory]
venue: "ASPLOS 2025 (Volume 1)"
year: 2025
summary_path: "../paper-summaries/2025ASPLOS-summarize/instruction-aware-cooperative-tlb-and-cache-replacement-policies.md"
---

# Instruction-Aware Cooperative TLB and Cache Replacement Policies

**Venue:** ASPLOS 2025 (Volume 1)
**저자:** Dimitrios Chasapis, Georgios Vavouliotis (BSC), Daniel A. Jiménez (Texas A&M), Marc Casas (BSC/UPC)

## 개요

Modern server/data center application은 대규모 dataset뿐 아니라 **대규모 instruction footprint** (수백만 instruction)를 가짐 [14, 39, 61, 88]. 이러한 large code footprint는 frequent STLB miss를 유발하며, instruction TLB miss는 특히 pipeline stall을 일으켜 성능에 큰 영향을 미침. Server application의 instruction footprint는 연간 최대 30%씩 증가하는 추세 [39, 52, 74].

**定量 분석 (Figure 1, 2):** Qualcomm Server workload는 전체 execution cycle의 평균 **12.52%**를 instruction address translation에 소비 (SPEC은 0.03%). 64-entry ITLB, 1536-entry STLB 환경에서 Qualcomm Server workload의 instruction STLB MPKI는 최대 **0.9**에 달함 — 빈번한 instruction page walk 발생. ITLB를 1024 entry까지 늘려야 overhead 최소화 가능.

**현행 STLB replacement policy의 한계:** Vendor들은 STLB에 LRU variant를 사용하며, instruction/data PTE를 구분하지 않음 [10, 66, 70]. CPU의 out-of-order execution이 data TLB miss latency를 부분적으로 숨길 수 있지만, instruction TLB miss는 pipeline의 critical path에 있어 더 치명적 [61, 80].

## Motivation — 3가지 Findings

### Finding 1: Large code footprint → high instruction translation overhead
Server workload의 instruction translation cost가 HPC/desktop 대비 현저히 높음 (Figure 1).

### Finding 2: STLB에서 instruction 우선 시 성능 향상
STLB replacement policy에서 확률 P로 instruction translation을 data translation보다 우선하여 keep하는 modified LRU 실험 결과 (Figure 3):
- **P=0.8** (80% 확률로 data evict): Qualcomm Server workload에서 geomean 성능 향상.
- **P=0.2** (20% 확률): 오히려 성능 저하.
- SPEC workload: instruction footprint가 ITLB에 fit → STLB는 대부분 data translation만 보유 → 영향 미미.

### Finding 3: STLB instruction 우선 → data page walk 증가 → cache pressure 증가
STLB에서 instruction을 우선하면 data STLB miss 증가 → data page walk로 인한 cache hierarchy의 dtMPKI 증가 (Figure 4). L2C에서 data PTE cache block에 대한 miss가 늘어나 data STLB miss의 실질적 latency cost가 증가.

## 방법론

### 1. iTP: Instruction Translation Prioritization (§4.1)

STLB replacement policy로, instruction translation entry를 data 대비 우선하여 keep함으로써 성능에 critical한 instruction page walk를 줄이는 것이 목표. 전체 STLB MPKI 감소가 아니라 **data translation을 instruction translation과 trade**하는 전략.

**Metadata:** STLB entry당 4비트 추가 — Type (1bit, instruction=0/data=1) + Freq (3bit frequency counter). 1536-entry STLB 기준 768 bytes 추가, LRU 대비 access latency 증가 없음.

**Insertion Policy (Figure 5):**
- **Data translation (Type=1):** LRUpos (eviction 우선순위 최상위)에 insert → 곧바로 eviction 후보.
- **Instruction translation (Type=0):** MRUpos - N 위치에 insert (N=4). Freq=0으로 초기화.
- 합리적 근거: MRUpos는 frequency-saturated instruction entry를 위해 reserved.

**Promotion Policy (Figure 5):**
- **Instruction translation hit:**
  - Freq가 saturated 상태 → MRUpos로 promote.
  - Freq 미포화 → insertion과 동일한 MRUpos - N으로 promote, Freq increment.
- **Data translation hit:** LRUpos + M 위치로 promote (M=8, N < M < associativity).

**Eviction Policy:** 기존 LRU와 동일 — LRUpos의 entry를 evict.

### 2. xPTP: extended Page Table Prioritization (§4.2)

L2C replacement policy로, iTP로 인해 증가한 data page walk의 cache pressure를 완화. **Cache block 중 data PTE를 포함한 block의 eviction을 지연**시켜 data page walk의 latency cost 감소.

**Metadata:** L2C block당 1bit Type (data PTE 여부). L2C MSHR entry당 1bit 추가.

**Eviction Policy (Figure 6):**
- **Step a:** LRUpos victim 식별.
- **Step b:** LRUpos부터 위로 탐색하여 data PTE가 아닌 block 중 가장 LRU에 가까운 block(ALT_LRUpos) 식별.
- **Step c:** ALT_LRUpos ≥ LRUpos + K (K=8) 확인.
  - **True:** LRUpos victim 선택 (data PTE block이 너무 오래되어 evict).
  - **False:** ALT_LRUpos victim 선택 (data PTE block 보호).

### 3. iTP+xPTP Adaptive Scheme (§4.3)

**Phase Adaptability:** xPTP가 항상 유리한 것은 아님 — STLB pressure가 낮은 phase에서는 data PTE 우선 보호로 인해 일반 cache block이 불필요하게 evict될 수 있음.

**Adaptive mechanism:** 1000 dynamic instruction마다 STLB MPKI 측정 → threshold T1 초과 시에만 xPTP 활성화. 구현: 2개 counter + 1-bit status register.

**전체 동작 흐름 (Figure 7):**
1. ITLB/DTLB miss → STLB lookup.
2. STLB hit → iTP promotion policy (Type 기반 Freq 갱신).
3. STLB miss → STLB MSHR에 Type 저장 → page walker 활성화.
4. Page walk reference가 L2C miss → L2C MSHR에 Type 저장 → xPTP eviction policy.
5. Page walk complete → STLB에 새 PTE insert (iTP insertion policy).

## 핵심 기여

1. **Server workload에서 instruction address translation이 주요 bottleneck** — Qualcomm Server workload는 전체 cycle의 12.52%를 instruction TLB miss 처리에 소비. Desktop/HPC workload에서는 무시할 수준이지만, 대규모 code footprint를 가진 현대 server에서는 critical.

2. **iTP+xPTP cooperative approach:** STLB에서 instruction translation 우선 → data page walk 증가 → L2C(xPTP)에서 data PTE 보호로 latency 보상. 단순히 STLB만 최적화하는 것이 아니라 **STLB+L2C의 협력적 최적화**가 핵심.

3. **18.9% 단일코어 / 11.4% SMT 성능 향상** — 기존 state-of-the-art 대비 월등. 단, LLC replacement policy(Mockingjay 등)에 따라 효과가 달라질 수 있음.

4. **Practical overhead:** STLB entry당 4비트, L2C block당 1비트 추가 — negligible hardware cost. STLB access latency 증가 없음.

## 주요 결과

### 실험 설정

| Component | Config |
|---|---|
| CPU Core | 4GHz, 352-entry ROB, 6-wide fetch |
| L1 ITLB | 64-entry, 4-way, 1-cycle |
| L1 DTLB | 64-entry, 4-way, 1-cycle |
| STLB | 1536-entry, 12-way, 8-cycle, 16-entry MSHR |
| L1I/L1D | 32KB/32KB, 8/12-way |
| L2C | 512KB, 8-way, 32-entry MSHR, xPTP: K=8 |
| LLC (per core) | 2MB, 16-way |
| DRAM | tRP=tRCD=tCAS=12, 12.8 GB/s |

**Workloads:** 120 single-core Qualcomm Server workloads (STLB MPKI ≥ 1.0), 75 SMT pairs (Intense/Medium/Relaxed Load). ChampSim 시뮬레이터 사용. 50M warmup + 100M measurement instructions.

**비교 대상:** LRU baseline, TDRRIP [79], PTP [63], CHiRP [55], CHiRP+TDRRIP, CHiRP+PTP, iTP, iTP+xPTP, iTP+TDRRIP, iTP+PTP.

### 성능 — Single Thread (Figure 8a)

| Policy | Geomean IPC Improvement vs. LRU |
|---|---|
| iTP | +2.2% |
| iTP+xPTP | **+18.9%** |
| PTP | +7.1% |
| TDRRIP | +9.3% |
| CHiRP | ~0% (LRU와 유사, i/d 구분 없음) |
| iTP+TDRRIP | +11.6% (TDRRIP 단독 대비 향상) |
| iTP+PTP | +9.4% (PTP 단독 대비 향상) |

iTP+xPTP가 모든 정책 중 최고 성능.

### 성능 — SMT (2 threads, Figure 8b)

| Policy | Geomean IPC Improvement vs. LRU |
|---|---|
| iTP | +0.3% |
| iTP+xPTP | **+11.4%** |
| TDRRIP | +8.5% |
| PTP | ~0% |

### MPKI 및 Miss Latency 분석 (Figure 9, 10)

**iTP+xPTP (single-thread):**
- STLB MPKI: 1.8 → 1.6 (11.1% 감소)
- STLB avg miss latency: 170.9 → 92.3 cycles (**45.9% 감소**)
- L2C MPKI: 30.6 → 46.5 (증가) — 그러나 data PTE miss는 1.0 → 0.4로 감소
- LLC MPKI: 13.8 → 8.4 (39.1% 감소)
- L2C avg miss latency: **47.5% 감소**

**Mechanism:** iTP가 instruction page walk를 data page walk로 trade → xPTP가 data PTE를 L2C에 keep → data page walk는 cache에서 빠르게 서비스, instruction page walk 감소로 pipeline stall 축소.

**STLB MPKI breakdown (Figure 10):** iTP 사용 시 instruction MPKI(iMPKI)는 현저히 감소, data MPKI(dMPKI)는 증가 — 의도된 trade-off.

### LLC Replacement Sensitivity (Figure 11)

| LLC Policy | iTP+xPTP Improvement (single) | iTP+xPTP Improvement (SMT) |
|---|---|---|
| LRU | +18.9% | +11.4% |
| SHiP | +15.8% | +10.6% |
| Mockingjay | +1.6% | +2.1% |

Mockingjay는 large data footprint workload에 최적화 — server code+data workload에서 효과 제한적.

### Sensitivity: ITLB Size, Huge Pages

- **ITLB 1024 entries:** instruction translation이 대부분 ITLB에서 서비스 → iTP+xPTP 개선 효과 4.6%로 감소 (예상된 결과).
- **2MB huge pages 사용:** iTP+xPTP의 상대적 이점 유지.

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2025ASPLOS-summarize/instruction-aware-cooperative-tlb-and-cache-replacement-policies.md|전체 요약 보기]]
