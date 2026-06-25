---
tags: [paper, 2023, 2023ISCA, topic/dram, topic/near-data-processing]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023ISCA-summarize/accelerating-personalized-recommendation-with-cross-level-near-memory-processing.md"
---

# Accelerating Personalized Recommendation with Cross-level Near-Memory Processing

**Venue:** 
**저자:** Haifeng Liu, Long Zheng, Yu Huang, Chaoqiang Liu, Xiangyu Ye, Jingrui Yuan, Xiaofei Liao, Hai Jin (HUST / Zhejiang Lab), Jingling Xue (UNSW)

## 개요

개인화 추천 시스템의 DLRM(Deep Learning Recommendation Model)은 Facebook AI 데이터센터 추론 사이클의 **80% 이상**을 소비할 정도로 중요하지만, embedding layer가 performance bottleneck이다.

**Embedding layer의 특성:**
- 수백 GB~수 TB 규모의 embedding table을 main memory에 저장.
- Sparse categorical feature → embedding vector lookup(gathering) → reduction(pooling).
- Memory-bound: 낮은 compute intensity, irregular/sparse memory access.
- 한 번의 embedding operation당 20~80개 vector gather, batch 처리로 throughput 향상.

**기존 NMP 접근의 한계:**
- TensorDIMM[38], RecNMP[42]: rank-level NMP → coarse-grained parallelism.
- TRiM[52]: bank-group(TRiM-G) 및 bank-level(TRiM-B) NMP → fine-grained parallelism.
- **문제 1 - Skewed access vs. Symmetrical architecture (Figure 3):** Embedding table 접근은 long-tail 분포. **상위 20% 미만의 row가 대부분의 access를 차지**, 나머지는 거의 접근되지 않음. 모든 데이터를 동일한 NMP level에서 동일하게 처리하면 load imbalance 발생 → 가장 많이 lookup되는 memory node가 bottleneck.
- **문제 2 - Successive access vs. Serial operation (Figure 4-5):** Bank-level로 갈수록 load imbalance ratio가 악화. NMP node 수 증가 → 평균 lookup/node 감소하지만 불균형 심화. Bank-level NMP(TRiM-B)는 TRiM-G 대비 **internal bandwidth 4×** 증가하나 speedup은 **1.31×** 에 그침. 면적 overhead는 **4×** 증가.

**핵심 인사이트:** 기존 symmetrical NMP는 데이터 특성을 무시하고 architecture 관점에서만 memory parallelism을 추구함. 실제로는 embedding data마다 필요한 bandwidth가 다르며, 이것을 architecture에 반영해야 함.

---

## 방법론

### 3.1 Methodology

| 항목 | 내용 |
|------|------|
| **Simulator** | Ramulator (cycle-accurate, modified) |
| **CPU** | 16-core x86-64, 2.2GHz Broadwell, 32MB LLC |
| **Memory** | DDR5-4800, 1 DIMM/ch, 2 Ranks/DIMM, 8 BG/Rank, 4 Banks/BG, **256 subarrays/Bank** |
| **Timing** | tRCD=40, tCL=40, tRP=40, tRAS=76, tRC=116, tBL=8, tCCDS=8, tCCDL=12, tFAW=32 |
| **PE synthesis** | 40nm CMOS, 300MHz, Synopsys Design Compiler |
| **Dataset** | Criteo Ad Kaggle/Terabyte (26 sparse features, production-scale 특성 유사) |
| **Model** | Facebook DLRM[50] |
| **Defaults** | Vector length=64, batch=32, pooling=80, rank=2 |
| **Baselines** | CPU-only, TensorDIMM[38], RecNMP[42], TRiM-G[52], TRiM-B[52] |

### 3.2 Overall Performance

**Vector length별 speedup (Figure 9, batch=32):**
- vs CPU baseline: **15.5×**
- vs TensorDIMM: **9.3×**
- vs RecNMP: **7.9×**
- vs TRiM-G: **2.5×**
- vs TRiM-B: **1.8×** (with **4× less area overhead**)

Short vector(16~32)에서는 C/A bandwidth 한계로 speedup 감소하지만 여전히 모든 baseline 능가.

**Batch size별 speedup (Figure 10, vector=64):**
- Batch 1~128 전 구간에서 TRiM-G 대비 **2~2.5×**, TRiM-B 대비 **1.5~1.8×**.
- Batch 증가 → memory parallelism 활용률 증가 → 소폭 성능 향상.

**Rank 수 scaling (Figure 11):**
- 2/4/8/16/32 rank 모두에서 ReCross가 우수. Subarray parallelism은 rank 내부에서 bandwidth를 제공하므로 rank 수 scaling에 강건.

### 3.3 Effectiveness Breakdown (Figure 12)

ReCross-Base(no SAP, no BWP, no LAS) → CPU 대비 **5.4×** (TRiM-G 수준):

| Optimization 추가 | 누적 speedup |
|---|---|
| + Subarray-level parallelism (SAP) | **9.3×** |
| + Bandwidth-aware partitioning (BWP) | **13.7×** |
| + Locality-aware scheduling (LAS) | **14.4×** |

**Load imbalance ratio (Figure 13):** BWP가 load imbalance를 TRiM-G보다 낮은 수준으로 감소.

### 3.4 Configuration Exploration (Figure 14)

5가지 대안 구성 실험 (PE 수 및 capacity ratio 변경):
- Bank-level PE를 8→16→32로 증가시켜도 성능 향상 미미 (tail data는 접근 빈도가 낮기 때문).
- **ReCross-d (1/4/4 PE, R:G:B=16:12:4)가 area efficiency sweet spot.**

### 3.5 Energy and Area

**Energy (Figure 15):**
- CPU 대비 **58.5%** 감소, TRiM-G 대비 **28.5%** 감소, TRiM-B 대비 **23.7%** 감소.
- PE overhead: 3.5%, subarray parallelism overhead: 0.28%.

**Area (Table 3):**
- Rank PE (per buffer chip): 0.34 mm²
- BG/Bank PE (per DRAM chip): 2.35 mm² (TRiM-G: 2.03 mm², TRiM-B: **11.5 mm²**)
- Buffer chip >100 mm², DRAM chip >75 mm² 대비 미미한 비중.

### 3.6 Partitioning Overhead

- Criteo 26 features: LP solve **<5초**.
- Production 수백 tables: 수십 초.
- Model training(hours~days) 대비 negligible. 1회만 수행.

---

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

- **Simulator:** Ramulator 기반, NMP instruction encoder/decoder, PE arithmetic logic, subarray parallelism timing model(SALP) 추가.
- **PE:** 40nm CMOS, 300MHz (DDR5-4800 internal freq). FP32 multiplier+adder.
- **Software:** C++ programming framework. EMB_Preparation(partition+allocate), EMB_Operation(offload) API.
- **Memory controller modification:** NMP extension queue → encoder → FR-FCFS scheduler → dispatcher.

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]


## 전체 요약

[[../paper-summaries/2023ISCA-summarize/accelerating-personalized-recommendation-with-cross-level-near-memory-processing.md|전체 요약 보기]]
