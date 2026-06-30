---
tags: [paper, 2025, 2025OSDI, topic/llm, topic/accelerator, topic/gpu]
venue: "OSDI 2025"
year: 2025
summary_path: "../paper-summaries/2025OSDI-summarize/20260630-064008-waferllm-large-language-model-inference-at-wafer-scale.md"
---

# WaferLLM: Large Language Model Inference at Wafer Scale

**Venue:** OSDI 2025
**저자:** Congjie He, Yeqi Huang, Pei Mu (University of Edinburgh); Ziming Miao, Jilong Xue, Lingxiao Ma, Fan Yang (Microsoft Research); Luo Mai (University of Edinburgh)

## 개요

LLM 추론은 메모리 대역폭에 의해 제한되며, 기존 GPU/TPU 기반 시스템은 공유 메모리 아키텍처에 최적화되어 있다. 웨이퍼 스케일 가속기(Cerebras WSE-2: 850,000 코어, 40GB 온칩 메모리, 22PB/s 대역폭)는 수백만개의 코어와 대규모 분산 메시 기반 온칩 메모리 아키텍처를 채택하지만, 기존 LLM 시스템은 이를 효과적으로 활용하지 못한다.

WaferLLM은 최초의 웨이퍼 스케일 LLM 추론 시스템으로, PLMR 디바이스 모델을 기반으로 수백만개 코어에서의 밀리온 스케일 병렬성과 MeshGEMM/MeshGEMV 알고리즘을 제안한다.

## 방법론

### PLMR 디바이스 모델
- **P (Massive Parallelism):** 수백만개 병렬 코어 → 밀리온 스케일 병렬성 요구
- **L (Non-uniform Latency):** 메시 NoC에서 최대 1,000배 지연시간 차이
- **M (Constrained Memory):** 코어당 수KB~수MB 로컬 메모리
- **R (Limited Routing):** Cerebras WSE-2에서 코어당 최대 25개 라우팅 경로

### 웨이퍼 스케일 LLM 병렬성
- **Prefill:** 입력/가중치 행렬의 2차원 분할로 밀리온 코어 병렬성; 전치 분산 GEMM으로 행렬 전치 회피
- **Decode:** 시퀀스 차원 미세 복제로 균일 부하; 가중치 배치 사전 최적화로 decode 중 전치 회피
- **KV 캐시 관리:** Shift 기반 관리로 균등 분산 — concat 대비 400배 확장성 향상

### MeshGEMM & MeshGEMV
- **MeshGEMM:** Cyclic shifting + Interleaving으로 임계 경로를 2 hops(O(α))로 제한 — SUMMA/Cannon 대비 2~3배 가속
- **MeshGEMV:** K-tree allreduce로 수백만 코어 결과 집약 — A100 대비 606배 가속

## 핵심 기여

- 최초의 웨이퍼 스케일 LLM 추론 시스템
- PLMR 모델로 웨이퍼 스케일 가속기의 고유 특성 체계화
- 수백만개 코어에서의 밀리온 스케일 병렬성 + Two-hop transmission으로 비균일 지연시간 해결

## 주요 결과

- GEMV: Cerebras 최적화 대비 **4~8배**, A100 대비 **606배** 가속
- GEMM: SUMMA/Cannon 대비 **2~3배** 가속
- LLM 추론: T10 대비 **100~200배**, Ladder 대비 **200~400배**, SGLang(A100) 대비 **30~40배**, 멀티-GPU 대비 **10~20배** 가속
- 에너지 효율: A100 대비 **2.5배** 향상

## 한계점

- 현재 소프트웨어/하드웨어/모델 설계의 제한으로 GEMV에서 전체 LLM 추론까지의 성능 격차 존재
- 동일 메모리 채널 내 코어만 직접 연결; 멀티 채널 간 통신 미지원

## 관련 개념

- [[paper-wiki/concepts/llm.md|LLM Inference]]
- [[paper-wiki/concepts/gpu.md|GPU/Accelerator]]

## 전체 요약

[[../paper-summaries/2025OSDI-summarize/20260630-064008-waferllm-large-language-model-inference-at-wafer-scale.md|전체 요약 보기]]
