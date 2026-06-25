---
tags: [paper, 2023, 2023ASPLOS, topic/dram, topic/gpu, topic/llm-inference]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023ASPLOS-summarize/grace-a-scalable-graph-based-approach-to-accelerating-recommendation-model-inference.md"
---

# GRACE: A Scalable Graph-Based Approach to Accelerating Recommendation Model Inference

**Venue:** 
**저자:** 

## 개요

DLRM(Deep Learning Recommendation Models)은 데이터센터 AI 추론 사이클의 60% 이상을 소비한다 (Meta 기준). DLRM의 sparse embedding layer는 전체 추론 시간의 25-80%를 차지하며, 주요 병목은 **memory bandwidth**다. DLRM 임베딩 테이블 크기는 4년간 16배 증가하여 TB급에 도달했고, bandwidth 요구량은 2TB/s로 30배 증가해 accelerator memory/상호연결의 bandwidth 성장을 크게 앞질렀다.

실제 사용자-아이템 상호작용은 power-law 분포를 따르므로, 자주 접근되는 아이템을 캐싱하는 접근이 연구되어 왔다. 그러나:

- **FAE, RecNMP:** 인기 아이템을 HBM/캐시로 이동시키지만 memory traffic 자체를 줄이지 못함 (reduction ratio = 1).
- **SPACE:** 인기 아이템 2개 조합의 partial sum(psum2)을 exhaustive하게 캐싱. 그러나 캐시된 psum의 25%만이 95%의 접근을 차지해 비효율적. Memory traffic 감소는 평균 1.09×에 불과.
- **MERCI:** 임의 길이의 partial sum을 클러스터링하여 캐싱. 그러나 (a) 복잡도가 `O(C × n² × m)`로 대규모 데이터셋에 확장 불가, sub-group으로 분할 시 global view 상실, (b) heterogeneous memory unaware — 큰 클러스터가 GPU 메모리를 과도하게 점유해 DIMM 병목을 야기.

이상적인 목표: memory traffic을 크게 줄이면서 heterogeneous memory bandwidth를 균형 있게 활용하고, 대규모 아이템/사용자에 확장 가능해야 함.

## 방법론

### 3.1 방법론

| 항목 | 상세 |
|------|------|
| **CPU** | Intel Xeon Platinum 8380, 80 cores, 512GB DDR4-3200 (32채널) |
| **GPU** | NVIDIA A40, 48GB GDDR6 |
| **Datasets** | Steam(10K items), Anime(11K), MovieLens20M(27K), DBLP(540K), AmazonOffices(599K), Twitch(740K), AmazonSports(1.5M), AmazonClothes(2.3M) + 4개 mixed |
| **Embedding dim** | 1024, batch size 1024 |
| **Baselines** | CPU only, Infinite GPU Memory, Metis clustering, FAE, SPACE, MERCI, Oracle-of-2 |
| **DLRM Models** | RM1(8 tables), RM2(32 tables), RM3(10 tables), RM4(3 tables) |
| **Metrics** | Embedding layer throughput, end-to-end throughput, memory traffic reduction, 95%-ile latency, energy |

### 3.2 주요 결과

**Embedding layer throughput (CPU-GPU heterogeneous, 1× extra capacity):**
- SPACE 대비: 평균 **1.50×** (Geomean)
- MERCI 대비: 평균 **1.40×**
- Oracle-of-2와의 gap을 **52.1%** 감소
- 성능은 ICG average node degree와 양의 상관관계 (stm=1405, ani=1148, mov=2107, M1=900에서 최대 성능)

**Memory traffic reduction (1=no reduction, lower better):**
- Oracle-of-2: 0.50, GRACE: 0.60, MERCI: 0.63, SPACE: 0.92, Metis: 0.99
- GRACE는 memory traffic을 40% 감소, MERCI는 37%

**95-percentile latency:** SPACE 대비 1.54×, MERCI 대비 1.41× 개선

**End-to-end DLRM throughput:**
- RM1: Infinite GPU 대비 1.46×, MERCI 대비 1.17×
- RM2 (embedding-heavy): Infinite GPU 대비 **1.60×**, MERCI 대비 **1.35×**
- RM3 (MLP-heavy): Infinite GPU 대비 1.20×, MERCI 대비 1.04×

### 3.3 Heterogeneous memory time split 분석

- SPACE: GPU time 15% 감소, CPU time 대폭 증가 (DIMM → GPU traffic migration 때문)
- MERCI: CPU time이 bottleneck (대형 클러스터로 GPU 공간 과점유 → DIMM spill)
- GRACE: CPU-GPU 실행시간 **거의 완벽한 균형**

### 3.4 Alternative hardware platforms

- **Homogeneous GPU memory:** GRACE > MERCI (5% margin), traffic reduction 차이와 일치
- **DIMM-HBM + PIM:** GRACE > MERCI (1.5×), heterogeneous awareness의 중요성 부각

### 3.5 Sensitivity: GPU memory capacity 제약

| Capacity | GRACE vs SPACE |
|----------|---------------|
| 1.0× | 1.50× |
| 0.5× | **1.63×** |
| 0.25× | **1.54×** |

제약된 환경에서 GRACE의 heterogeneous awareness가 더 큰 이점 제공.

### 3.6 Clustering speed

128-thread 구현 기준, GRACE가 MERCI 대비 평균 **8.3×** 빠름 (mixed dataset: 26.6×).

### 3.7 Energy

GRACE는 Infinite GPU Memory 대비 4% 더 나은 에너지 소비. Energy-optimized 설정 시 18% 절감.

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

- ICG/clustering: GAPBS [6] 프레임워크, C++/OpenMP
- Decision engine: scikit-learn CART
- GPU embedding reduction: CUDA/C++ (PyTorch보다 낙관적 baseline)
- CPU reduction: AVX-512, OpenMP 병렬화 (80코어 완전 활용)
- 1GB super pages로 paging overhead 제거
- GitHub: https://github.com/Linestro/GRACE, Zenodo artifact

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]


## 전체 요약

[[../paper-summaries/2023ASPLOS-summarize/grace-a-scalable-graph-based-approach-to-accelerating-recommendation-model-inference.md|전체 요약 보기]]
