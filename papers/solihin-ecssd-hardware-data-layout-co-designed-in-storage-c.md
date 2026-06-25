---
tags: [paper, 2023, 2023ISCA, topic/gpu, topic/storage]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023ISCA-summarize/ecssd-hardware-data-layout-co-designed-in-storage-computing-architecture-for-extreme-classification.md"
---

# ECSSD: Hardware/Data Layout Co-Designed In-Storage-Computing Architecture for Extreme Classification

**Venue:** 
**저자:** Siqi Li, Fengbin Tu, Liu Liu, Jilan Lin, Zheng Wang, Yangwook Kang, Yufei Ding, Yuan Xie (UCSB, HKUST, RPI, Samsung, Alibaba DAMO Academy)

## 개요

딥러닝 classification workload의 분류 카테고리 수가 급격히 증가하면서, 최종 classification layer가 **extreme classification** 문제로 대두됨. 카테고리 수가 최대 1억 개에 달하는 경우, classifier parameter만 수백 GB를 소비하여 CPU/GPU의 main memory 용량을 초과함 [21, 28, 37, 42, 54]. Classification layer가 전체 응용 실행 시간의 **30-60%** 를 차지함 [22].

**핵심 병목:** SSD는 충분한 저장 용량을 제공하지만, PCIe 3.0 기준 lane당 1GB/s에 불과한 external I/O bandwidth로 인해 host↔SSD 간 데이터 이동이 극도로 느림.

**In-storage-computing 기회:** SSD 내부 bandwidth는 external보다 훨씬 높음 (채널당 1GB/s, 8채널 SSD 기준 8GB/s). In-storage computing은 host로의 데이터 이동을 제거하고 SSD 내부에서 직접 연산하여 이 병목을 해결 가능.

**Approximate screening 알고리즘 [22]:** Full-precision(FP32) weight matrix를 4-bit integer로 projection하여 low-precision screening → threshold filtering → candidate weight만 FP32로 연산. 이로써 floating-point 연산량을 **10%** 로 감소 (10× speedup). 그러나 남은 10% FP32 연산량조차 SSD에 삽입 가능한 제한된 area budget으로는 감당 불가.

## 방법론

### 3.1 Overall Architecture (Fig. 4)

ECSSD는 기존 SSD 구조에 **custom accelerator**를 data buffer 근처에 추가. 두 가지 모드:

- **SSD Mode:** 기존 SSD와 동일하게 동작 (accelerator disabled).
- **Accelerator Mode:** Extreme classification 전용. INT4 MAC circuit(approximate screening) + Alignment-free FP32 MAC circuit(candidate-only classification) + Comparator(threshold filtering) + Scheduler(전체 조정).

### 3.2 Alignment-free Floating-point MAC Circuit (핵심 기법 1)

**Naive FP32 MAC의 문제:** Area breakdown 분석 결과, exponent comparator + mantissa shifter 등 alignment-related component가 전체 면적의 **37.7%** 차지.

**ECSSD의 해법 — Pre-alignment + CFP32 format:**

**Step 1 — Vector-wise pre-alignment (host에서 실행):**
입력 feature vector에서 maximum exponent `E_max`를 찾고, 모든 mantissa를 `E_max - E` 만큼 right-shift → 전체 vector가 `E_max`를 공통 exponent로 사용.

**Step 2 — CFP32 (Compensation FP32) data format (Fig. 5(b)):**
- FP32의 8-bit exponent 공간을 **7-bit mantissa compensation** + **1-bit hidden one**으로 재활용
- 공통 8-bit exponent `E_max`는 vector별로 1회만 저장
- 95% 이상의 floating-point data에서 bit 손실 없음 → accuracy drop 없음

**Step 3 — In-storage alignment-free FP MAC 회로:**
Pre-alignment 완료된 mantissa만으로 MAC 연산 수행 → exponent comparator, mantissa shifter 등 alignment component 완전 제거. FP multiplier도 INT mantissa multiplier로 단순화.

**성능:** 동일 0.21mm² area budget에서 naive FP32 MAC: 29.2 GFLOPS → alignment-free: **50 GFLOPS** (1.73×). SK Hynix의 pre-alignment 기법 [18] 대비 1.38× area 효율.

### 3.3 Heterogeneous Data Layout Design (핵심 기법 2)

4-bit weight → **DRAM** 저장, 32-bit weight → **NAND flash channels** 저장. 이로써:
- 모든 channel bandwidth를 FP32 데이터 전송에 전용
- DRAM bandwidth(12.8GB/s)를 INT4 데이터 전송에 활용
- 두 데이터 타입 간 transfer interference 완전 제거 → 1.43× speedup (Transformer-W268K, candidate ratio 5%~20% 평균)

### 3.4 Learning-based Adaptive Interleaving Framework (핵심 기법 3)

**Strawman 1 — Sequential storing:** 인접 tile의 candidate vector들이 동일 channel에 집중 → 한 번에 1개 channel만 사용 → bandwidth 활용률 <10%.

**Strawman 2 — Uniform interleaving (Fig. 6):** Weight vector를 8개 channel에 순차 분배 (No.1→Ch1, No.2→Ch2, ...). 모든 channel 병렬 가동되나, candidate filtering 결과 channel별 workload 불균형 → 활용률 44.31%.

**ECSSD 해법 — Learning-based adaptive interleaving (Fig. 7):**

1. **Hot degree prediction:** 각 4-bit weight vector의 element absolute value 합을 기준으로 3등급 분류 — very hot, medium hot, not hot.
2. **Fine-tuning:** Training dataset에서 candidate로 선택된 빈도 기반 hot degree 재조정.
3. **Balanced interleaving:** Hot degree에 따라 8개 channel에 균등 배분. FTL의 logical-to-physical address mapping을 통해 구현 — firmware 수정만으로 가능.

**결과:** Channel bandwidth 활용률 **94.7%** → sequential storing 대비 **10.5×** speedup, uniform interleaving 대비 **1.43×** speedup.

### 3.5 Workflow (전체 실행 흐름)

1. **Data preparation:** 4-bit weight → DRAM, pre-aligned 32-bit weight → NAND flash (learning-based interleaving).
2. **Inference (tile-by-tile):** INT4 MAC이 tile N 처리 중일 때 FP32 MAC이 tile N-1 처리 → pipelining으로 latency hiding. Ping-pong buffer로 read/write overlap.

## 핵심 기여

ECSSD는 circuit-algorithm-data layout의 **cross-layer co-design**을 통해 extreme classification을 in-storage-computing으로 구현한 최초의 아키텍처. 핵심 기여: (1) CFP32 기반 alignment-free FP MAC으로 제한된 area budget 내에서 SSD internal bandwidth에 필적하는 50 GFLOPS 달성, (2) heterogeneous data layout으로 4-bit/32-bit transfer interference 제거, (3) learning-based adaptive interleaving으로 channel-level bandwidth 활용률 94.7% 달성. 결과적으로 기존 baseline 대비 **3.24-49.87×** 성능 향상, ENMC 대비 **8.87×** cost efficiency 달성. 향후 in-storage-computing 시스템의 computational ability와 internal bandwidth 활용 최적화에 중요한 방향 제시.

## 주요 결과

### 4.1 Methodology

| 항목 | 내용 |
|------|------|
| **Testbed** | MQSim 기반 시뮬레이터, host 포함 |
| **ECSSD config** | 4TB, 8 flash channels, 16GB DRAM, PCIe 3.0 x4 |
| **Accelerator** | INT4 MAC: 200 GOPS, FP32 MAC: 50 GFLOPS, 28nm, 400MHz |
| **Area/Power** | 0.1836mm² / 52.93mW (budget 0.21mm² 이내) |
| **Benchmarks** | GNMT-E32K, LSTM-W33K, Transformer-W268K, XMLCNN-A670K, XMLCNN-S10M/50M/100M |
| **Baselines** | CPU-N/AP, GenStore-N/AP, SmartSSD-N/H-N/AP/H-AP |
| **Metrics** | End-to-end latency, channel bandwidth utilization |

### 4.2 Area & Power (Table 4)

- Alignment-free FP32 MAC: 0.139mm² (75.7%), 33.87mW (63.9%)
- INT4 MAC: 0.044mm² (24%), 19.04mW (36%)
- Comparator: 0.0004mm², Scheduler: 0.0002mm²
- **Total: 0.1836mm², 52.93mW** → area budget 만족

### 4.3 End-to-end 성능 (Fig. 8, 13)

**Breakdown (Fig. 8):** Sequential storing baseline → uniform interleaving: 4.06× → +alignment-free MAC: 추가 개선 → +heterogeneous layout: 채널 활용률 67.6% → +learning-based interleaving: 94.7%, 최종 **10.5×** speedup.

**Architecture 비교 (Fig. 13, large-scale benchmarks 평균):**

| Baseline | Speedup |
|----------|---------|
| CPU-N | **49.87×** |
| SmartSSD-N | **37.83×** |
| GenStore-N | **24.51×** |
| SmartSSD-H-N | **19.11×** |
| CPU-AP | **8.22×** |
| SmartSSD-AP | **6.28×** |
| GenStore-AP | **4.05×** |
| SmartSSD-H-AP | **3.24×** |

### 4.4 Ablation Studies

- **Alignment-free FP MAC (Fig. 9):** Naive 대비 area 1.73×↓, power 1.53×↓. SK Hynix 기법 대비 area 1.38×↓, power 1.19×↓.
- **Heterogeneous layout (Fig. 10):** Candidate ratio 5%일 때 1.73× speedup, 평균 **1.43×**.
- **Learning-based interleaving (Fig. 12):** Uniform interleaving 대비 **1.43×**, sequential 대비 **7.57×**.

### 4.5 Scalability (Section 7.1)

- **Scale-up:** 16GB DRAM → 100M-category 지원. 8GB는 50M-category로 제한, 32GB는 40% power 증가.
- **Scale-out:** Category 500M 도달 시 5개 ECSSD로 partitioned parallel execution → 기존 server infrastructure 재사용.

### 4.6 GPU / ENMC 비교 (Section 7.2-7.3)

- **vs GPU (RTX 3090):** 100M-category 분류에 GPU 18대 필요 → ECSSD 대비 573× power. ECSSD는 cost/power-limited 시나리오에 적합.
- **vs ENMC (near-DRAM-computing):** ENMC는 512GB, 800 GFLOPS로 peak 성능은 높으나, cost efficiency: ECSSD 0.018 GFLOPS/$ vs ENMC 0.002 GFLOPS/$ (**8.87×**), energy efficiency: 4.55 vs 3.805 GFLOPS/W (**1.19×**).

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2023ISCA-summarize/ecssd-hardware-data-layout-co-designed-in-storage-computing-architecture-for-extreme-classification.md|전체 요약 보기]]
