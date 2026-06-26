---
tags: [paper, 2024, 2024HPCA, topic/dram, topic/rowhammer]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024HPCA-summarize/spatial-variation-aware-read-disturbance-defenses-experimental-analysis-of-real-dram-chips-and-implications-on-future-solutions.md"
---

# Spatial Variation-Aware Read Disturbance Defenses: Experimental Analysis of Real DRAM Chips and Implications on Future Solutions

**Venue:** 
**저자:** 

## 개요

DRAM read disturbance (RowHammer, RowPress)는 technology scaling에 따라 점점 악화되고 있음. 2012-2013년 DDR3: HC_first = 139K [1], 2018-2020년 LPDDR4: HC_first = 4.8K [61] — 한 order of magnitude 감소. RowPress [70] 발견으로 tAggOn (aggressor row on time)이 길어질수록 read disturbance vulnerability가 더욱 악화됨이 밝혀짐.

**문제:** 기존 read disturbance solution들은 모든 DRAM row가 동일한 vulnerability를 가진다고 가정하고 worst-case row에 맞춰 동작 → strong row도 weak row처럼 overprotect → 불필요한 preventive action으로 성능 저하.

**Key gap:** Prior characterization works [1, 61, 62, 63, 70, 97]는 DRAM row의 일부만 테스트하거나 bank-level aggregate만 분석. **어떤 prior work도 DRAM bank 내 모든 row에 대한 spatial variation을 rigorous하게 분석하지 않음.**

## Characterization (144개 real DDR4 DRAM chip)

### Methodology

| 항목 | 내용 |
|------|------|
| Testbed | FPGA (Xilinx Alveo U200 / Bittware XUSP3S) + DRAM Bender |
| Chips | 144 DDR4 chips, 11 die revisions, 3 manufacturers (Samsung, SK Hynix, Micron) |
| Temperature | 80°C ±0.5°C (PID controller) |
| Metrics | HC_first (minimum hammer count for first bitflip), BER (bit error rate) |
| Tests | Double-sided hammering, 14 hammer counts (1K~128K), 6 data patterns, 3 tAggOn (36ns, 0.5μs, 2μs), 4 banks/module |
| Interference Control | Refresh disabled, test time < tREFW, 10 iterations for worst-case, ECC 확인 |

Algorithm 1 (core test):
```
For each tAggOn ∈ {36ns, 0.5μs, 2μs}:
  For each bank ∈ {1, 4, 10, 15}:
    For each victim row in bank:
      Find worst-case data pattern (WCDP) at HC=128K
      Sweep HC ∈ {1K,2K,4K,8K,12K,16K,24K,32K,40K,48K,56K,64K,96K}
      Measure BER at each HC
```

### Key Findings

#### BER Variation (Figure 3, 4)

**Observation 1:** BER varies significantly across DRAM rows within a bank. M1: CV=8.08%, S1: CV=5.77%.

**Observation 2:** Different banks within same module exhibit similar BER. M0 예: 4개 bank 평균 BER = 1.71%, 1.71%, 1.70%, 1.72%.

**Observation 3:** Same manufacturer의 다른 module 간 BER가 크게 다를 수 있음. M0 vs M1 vs M3는 mean BER가 서로 strictly distinct.

**Observation 4:** BER는 row address 증가에 따라 반복적 증가/감소 패턴을 보임 (design-induced variation). S4: 0.25, 0.50, 0.75, 1.00 상대 위치에서 local minimum.

**Observation 5:** 일부 module에서 large chunk of rows가 다른 chunk보다 높은 BER. M1: 상대 위치 0.03~0.12에서 avg normalized BER=1.51, 0.20~1.00에서 1.25.

> **Takeaway 1:** BER significantly varies across DRAM rows within a bank and across modules, while banks within a module exhibit similar BER.

> **Takeaway 2:** BER in a bank exhibits repeating patterns as row address increases. Certain chunks of rows can exhibit higher BER than others.

#### HC_first Variation (Figure 5, 6)

**Observation 6:** HC_first varies significantly across rows. S0/S1: 32K/24K에서 bitflip 발생하는 row도 있고 128K까지 bitflip 없는 row도 있음.

**Observation 7:** Same manufacturer의 다른 module 간 HC_first 분포가 크게 다름. M0: 8K~40K, M4: 12K~96K.

**Observation 8:** HC_first는 row마다 크게 다름. H0: minimum HC_first의 8×~20×까지 variation.

**Observation 9:** HC_first variation은 BER과 달리 regular transition pattern을 보이지 않음 → weakest cell의 HC_first는 design-induced variation보다 random variation이 지배적.

> **Takeaway 3:** HC_first varies significantly and irregularly across rows and banks in a module.

> **Takeaway 4:** HC_first does not exhibit regular trend as row address increases (unlike BER).

#### RowPress Effect (Figure 7)

**Observation 10:** tAggOn 증가 시 HC_first 감소 (mean + IQR 모두). 거의 모든 row에 해당.

**Observation 11:** tAggOn=2μs에서도 HC_first variation은 여전히 큼. H2: CV=25.0%(36ns), 23.0%(0.5μs), 30.4%(2μs).

> **Takeaway 5:** HC_first reduces as tAggOn increases and varies significantly across rows for large tAggOn.

#### Spatial Feature Correlation Analysis (Figure 9, Table 3)

Row's spatial features (bank addr, row addr, subarray addr, distance to sense amplifiers)로 HC_first 예측 시도:

- 15개 module 중 **단 4개만** F1 score > 0.7 (S0: 0.77, S1: 0.71, S3: 0.75, S4: 0.76)
- No module achieves F1 > 0.77
- Spatial features that work: 특정 row address bits, subarray address bits → design-specific
- Bank address bit 중 F1 > 0.7인 경우 없음

> **Takeaway 6:** Spatial features correlate well with HC_first in only 4 out of 15 modules. 따라서 spatial features만으로 HC_first 예측은 insufficient → per-row profiling 필요.

#### Aging Effect (Figure 10)

68일 aging (double-sided RowHammer test, 80°C):

**Observation 12:** 0.4% of rows: HC_first가 12K→8K로 감소. Static HC_first 기반 configuration은 unsafe → periodic online testing 필요.

**Observation 13:** Weakest rows (lowest HC_first)만 aging 영향 받음. Strong rows (HC_first=128K)는 변화 없음.

> **Takeaway 7:** Static HC_first determination is not completely safe. Worst-case HC_first changes with aging.

## Svärd: Spatial Variation-Aware Read Disturbance Defense

## 방법론

**핵심 아이디어:** 기존 read disturbance solution의 aggressiveness를 각 potential victim row의 vulnerability level(HC_first)에 맞춰 동적 조정.

#### 동작 방식 (Figure 11)

1. DRAM row activation 시 기존 solution과 Svärd에 row address 제공
2. Svärd가 activated row의 HC_first 값을 solution에 제공
3. Solution은 이 precise threshold로 preventive action 여부 결정
   - Weak row (low HC_first) → aggressive prevention
   - Strong row (high HC_first) → relaxed/없음

#### Implementation Options

**Memory Controller-based:**
- MC에 HC_first table 저장 (row당 4-bit bin ID, 16 bins 이하)
- Table size: bank당 0.056mm² (CACTI estimate). Dual-rank 16-bank: high-end Intel Xeon의 0.86% area
- Access latency 0.47ns → row activation latency (~14ns)에 완전히 overlap 가능
- 또는 DRAM data integrity bits에 metadata 저장: row당 4 bits → DRAM array size 0.006% 증가

**DRAM Chip-based:**
- In-DRAM TRR 등에 적용. Activation 시 Svärd가 precise threshold 제공
- Metadata는 DRAM array 또는 activation counter 내 저장

#### Security

Svärd는 weakest row에 대해 동일한 security guarantee 유지. 기존 solution들은 모든 row를 weakest로 가정 → strong row overprotect. Svärd는 strong row의 overprotection만 제거. Security degradation 없음.

## 핵심 기여

1. **핵심 발견:** 144개 real DDR4 chip 분석 결과, read disturbance vulnerability는 row마다 BER 2×, HC_first는 order of magnitude까지 irregularly하게 variation. Spatial features만으로 예측 불가 (15개 중 4개 module만 F1 > 0.7).

2. **Svärd:** 기존 solution에 row-level vulnerability profile을 제공하는 lightweight mechanism. Overhead: memory controller area 0.86% 또는 DRAM bits 0.006%. 기존 solution의 security guarantee 유지하며 성능 overhead 대폭 감소.

3. **Broader significance:**
   - DRAM vendor가 per-row profiling 정보를 공개하거나 system-level online testing infrastructure를 제공해야 함을 시사
   - Aging으로 인한 HC_first 변화에 대응하기 위한 periodic re-profiling 필요성 제기
   - Svärd는 controller-based와 DRAM-based solution 모두와 호환 → universal adaptation layer

## 주요 결과

### Methodology

| 항목 | 내용 |
|------|------|
| Simulator | Ramulator (cycle-level) |
| Processor | 1 or 8 cores, 3.2GHz, 4-wide, 128-entry instruction window |
| DRAM | DDR4, 1ch, 2 ranks/ch, 4 bank groups × 4 banks, 128K rows/bank |
| Memory Ctrl | FR-FCFS-Cap (column cap=16), MOP address mapping |
| LLC | 2MB/core |
| Workloads | 120 8-core multiprogrammed mixes (SPEC2006/2017, TPC, MediaBench, YCSB) |
| Metrics | Weighted speedup, harmonic speedup, max slowdown |
| Proﬁles | Manufacturer별 3개 대표 모듈 (S0, M0, H1)의 실제 측정 분포 scaling |

### Performance (Figure 12)

**HC_first = 128 기준, 5개 solution에 대한 Svärd 성능 향상:**
- AQUA: 1.23×
- BlockHammer: 2.65×
- Hydra: 1.03×
- PARA: 1.57×
- RRS: 2.76×

**HC_first = 64:**
- AQUA: 1.63×
- BlockHammer: 4.88×
- Hydra: 1.07×
- PARA: 1.95×
- RRS: 4.80×

**Observation 14:** HC_first < 1K에서 Svärd는 모든 solution의 3개 metric을 consistently 향상.

**Observation 15:** S0 profile이 3개 중 가장 큰 성능 향상. HC_first=64:
- AQUA overhead: 43.51% → S0: 0.32%, M0: 16.36%, H1: 6.81%
- BlockHammer: 92.29% → 31.15% / 82.68% / 73.32%
- RRS: 87.40% → 5.83% / 65.44% / 47.17%

Hydra의 Svärd benefit이 상대적으로 작은 이유: Hydra overhead는 preventive refresh보다 off-chip counter transfer가 dominant → Svärd는 refresh만 줄임.

### Adversarial Access Patterns (Figure 13)

HC_first=64:
- **Hydra:** slowdown 73.1% → Svärd-S0: 71.6%, M0: 72.3%, H1: 72.4%
- **RRS:** slowdown 95.6% → Svärd-S0: 48.2%, M0: 79.3%, H1: 69.9%

Svär-S0가 가장 효과적 (Takeaway 8, 9).

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]


## 전체 요약

[[../paper-summaries/2024HPCA-summarize/spatial-variation-aware-read-disturbance-defenses-experimental-analysis-of-real-dram-chips-and-implications-on-future-solutions.md|전체 요약 보기]]
