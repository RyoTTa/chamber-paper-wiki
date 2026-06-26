---
tags: [paper, 2024, 2024HPCA, topic/dram, topic/rowhammer, topic/storage]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024HPCA-summarize/comet-count-min-sketch-based-row-tracking-to-mitigate-rowhammer-at-low-cost.md"
---

# CoMeT: Count-Min-Sketch-based Row Tracking to Mitigate RowHammer at Low Cost

**Venue:** 
**저자:** İsmail Emir Yüksel, F. Nisa Bostancı, Yahya Can Tuğrul, A. Giray Yağlıkçı, Ataberk Olgun, Konstantinos Kanellopoulos, Mohammad Sadrosadati, Onur Mutlu (ETH Zürich)

## 개요

### 1.1 RowHammer 위협의 심화

DRAM technology node 축소에 따라 RowHammer threshold (NRH: bitflip을 유발하는 최소 row activation 횟수)가 급격히 감소:

| DRAM 세대 | NRH |
|-----------|-----|
| 2010-2013 (old) | ~69.2K |
| 2019-2020 (new) | **~4.8K** (14.4× 감소) |

더욱이 **RowPress**[13]는 row를 장시간 open 상태로 유지하는 것만으로도 RowHammer보다 1~2 order of magnitude 적은 activation으로 bitflip 유발.

### 1.2 기존 Mitigation의 Trade-off 딜레마

기존 counter-based mitigation은 두 가지 극단 사이에서 trade-off:

#### Performance-optimized (e.g., Graphene[86])

Misra-Gries 알고리즘 기반 tagged counter table. CAM 구현으로 높은 면적 비용:
| NRH | Graphene storage |
|-----|-----------------|
| 1K | 207.2 KB |
| 500 | 498.4 KB |
| 250 | 765.0 KB |
| **125** | **~1.5 MB** (prohibitive) |

#### Area-optimized (e.g., Hydra[90])

Per-DRAM-row counter를 DRAM에 저장 + SRAM group counter로 필터링. 그러나:
- NRH=125에서 **평균 5.66%, 최대 51.24% 성능 저하** (single-core)
- Off-chip counter fetch로 인한 **평균 memory read latency 16.91% 증가**

#### Radar Plot 분석 (Figure 4, NRH=125)

| Mechanism | Performance | Energy | Processor Area | DRAM Area |
|-----------|:-----------:|:------:|:-------------:|:---------:|
| Graphene | ✓ | ✓ | ✗ (high) | — |
| Hydra | ✗ | ✗ | ✓ | ✓ |
| PARA | ✗✗ | ✗✗ | ✓✓ | ✓✓ |
| REGA | ✗ | ✗ | ✓ | ✗ |

**어떤 mitigation도 네 축 모두에서 우수하지 않음.**

### 1.3 핵심 인사이트

RowHammer는 **frequent item counting 문제**로 해석 가능하다. CMS(Count-Min Sketch)[128]는 hash-based counter array로 frequent item을 low-area로 추적하는 데이터 구조다. 그러나 CMS를 그대로 적용하면:
- Counter collision → overestimation → unnecessary preventive refresh
- Counter saturation (reset 불가 → 다른 row의 underestimation 위험)

CoMeT의 해결책: CMS에 **RAT(Recent Aggressor Table)** 을 결합하여 saturation 문제를 해결한다.

## 방법론

### 3.1 실험 방법론

| 항목 | 구성 |
|------|------|
| **Simulator** | Ramulator[130] (cycle-level DRAM) + DRAMPower[136] |
| **Processor** | 1~8 core, 3.6 GHz, 4-wide OoO |
| **DRAM** | DDR4, 1 ch/2 ranks, 4 bank groups × 4 banks, 128K rows/bank |
| **Scheduler** | FR-FCFS, column cap=16 |
| **LLC** | 8 MB (single), 16 MB (8-core) |
| **Workloads** | 61 single-core + 56 multi-core (8-core) from SPEC 2006/2017, TPC, MediaBench, YCSB |
| **RowHammer Thresholds** | NRH = 1000, 500, 250, 125 |
| **Baselines** | No mitigation, Graphene[86], Hydra[90], REGA[127], PARA[1] |
| **CoMeT Config** | k=3 hash functions, 2048 CT counters/bank, 128-entry RAT, EPRT=25%, RAT miss history=256 |

### 3.2 주요 결과

#### Single-Core Performance Overhead (Figure 10)

| NRH | Avg Performance Overhead | Max | Avg Mem Read Latency Increase |
|-----|:------------------------:|:---:|:----------------------------:|
| 1K | **0.19%** | 2.64% | 0.18% |
| 500 | 0.57% | — | — |
| 250 | 0.96% | — | — |
| **125** | **4.01%** | 19.82% | 5.30% |

#### Single-Core DRAM Energy Overhead (Figure 11)

| NRH | Avg | Max |
|-----|:---:|:---:|
| 1K | **0.08%** | 1.13% |
| 125 | **2.07%** | 14.11% |

#### State-of-the-Art 비교 (Figure 12, NRH=125)

| Mechanism | Avg Perf Overhead | Comparison to CoMeT |
|-----------|:-----------------:|---------------------|
| **CoMeT** | **4.01%** | — |
| Graphene | 2.26% | CoMeT within **1.75%** |
| Hydra | 5.66% | CoMeT **39.1% better** (up to) |
| REGA | 14.15% | CoMeT **3.5× better** |
| PARA | 30.0% | CoMeT **7.5× better** |

#### Multi-Core (8-core) Weighted Speedup

| NRH | CoMeT |
|-----|:-----:|
| 1K | **0.73% avg overhead** |
| 125 | **~4%** (vs Graphene ~2.5%, Hydra ~25%) |

### 3.3 면적 분석 (Table 4, Dual-rank)

| | NRH=1K | NRH=125 |
|---|:------:|:-------:|
| CoMeT CT (SRAM) | 64.0 KB | 40.0 KB |
| CoMeT RAT (CAM) | 12.5 KB | 11.0 KB |
| CoMeT Logic | <0.005 mm² | <0.005 mm² |
| **CoMeT Total** | **76.5 KB / 0.09 mm²** | **51.0 KB / 0.07 mm²** |
| Graphene | 207.2 KB / 0.49 mm² | 1466.2 KB / 4.89 mm² |
| Hydra | 61.6 KB / 0.08 mm² | 46.8 KB / 0.07 mm² |
| **CoMeT vs Graphene** | **5.4× less** | **74.2× less** |

CoMeT 면적은 Hydra와 유사하나, Hydra는 추가로 4 MiB DRAM storage overhead 발생.

### 3.4 Ablation: Design Space Exploration

#### CT Configuration (Figure 6)
- NHash=4, NCounters=512 조합이 NRH=125에서 최적 (더 증가시켜도 성능 향상 미미)
- Storage: 2048 counters/bank (vs 128K rows — 62.5× reduction)

#### RAT Size (Figure 7)
- 128 entries에서 수렴 (256으로 증가시 추가 이득 없음)

#### Early Preventive Refresh (Figure 8)
- EPRT=25%, miss history=256이 최적 성능/에너지 trade-off
- EPRT=0% (매 capacity miss마다 refresh) → frequent rank-level refresh로 성능 저하

#### Counter Reset Period (Figure 9)
- k=3 (reset period = tREFW/3)에서 worst-case 성능 최적
- k>3 → NPR이 너무 작아져 오히려 preventive refresh 빈도 증가

### 3.5 Latency 분석

Verilog 구현 합성 결과: CoMeT의 activation count 추정 latency = **1.98ns**. DDR4 tRRD(2.5ns) 미만 → critical path off-load 가능.

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

- **Memory controller 내 구현** (DRAM chip/interface 변경 없음)
- CT: 4개 scratchpad SRAM array (병렬 접근)
- RAT: CAM tag array + SRAM counter array (128 entries × [17-bit tag + counter])
- Hash functions: bit-shift + bit-mask 연산으로 구현 (조합 회로만 필요)
- Preventive refresh: ACT+PRE 명령으로 victim rows 1회 접근 (표준 DRAM command 사용)
- Early preventive refresh: rank-level REF 명령 (모든 bank의 모든 row refresh)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2024HPCA-summarize/comet-count-min-sketch-based-row-tracking-to-mitigate-rowhammer-at-low-cost.md|전체 요약 보기]]
