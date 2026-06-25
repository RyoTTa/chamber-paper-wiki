---
tags: [paper, 2024, 2024ISCA, topic/compression, topic/dram, topic/gpu, topic/llm-inference]
venue: "ACM/IEEE 51st Annual International Symposium on Computer Architecture (ISCA 2024)"
year: 2024
summary_path: "../paper-summaries/2024ISCA-summarize/alisa-accelerating-llm-inference-via-sparsity-aware-kv-caching.md"
---

# ALISA: Accelerating Large Language Model Inference via Sparsity-Aware KV Caching

**Venue:** ACM/IEEE 51st Annual International Symposium on Computer Architecture (ISCA 2024)
**저자:** Youpeng Zhao, Di Wu, Jun Wang (University of Central Florida)

## 개요

- LLM 추론은 autoregressive 방식으로 생성되며, Transformer의 self-attention은 시퀀스 길이에 대해 **quadratic complexity**를 가짐 → 긴 시퀀스에서 성능/확장성 병목
- **KV caching**은 이전에 계산된 Key/Value 텐서를 저장하여 중복 계산을 제거하고 quadratic complexity를 선형으로 줄이지만, KV 텐서의 크기가 시퀀스 길이에 비례하여 선형 증가
- 단일 GPU 환경에서 배치 크기와 시퀀스 길이가 증가하면 KV caching이 **GPU 메모리 용량을 초과** → Out-of-Memory (OOM) 에러 발생 (Figure 1: OPT-6.7B에서 workload 2의 "GPU only" 경우)
- KV 텐서를 CPU 메모리로 오프로딩하면 GPU-CPU 간 데이터 전송 오버헤드가 새로운 병목 → FlexGen 사용 시 KV caching 시간이 전체 실행 시간의 상당 부분 차지
- 기존 희소 attention 기법 (Longformer, SparseTransformer 등)은 고정된 sparse 패턴을 사용하여 autoregressive LLM 추론에서 중요한 토큰을 정확히 포착하지 못함 → 정확도 붕괴
- 기존 시스템 (vLLM, FlexGen)은 KV 텐서를 블록/헤드 단위로 정적 관리 → 동적 메모리 용량 변화를 활용하지 못함

## 방법론

### 3.1. Sparse Window Attention (SWA)

**핵심 관찰:**
- Autoregressive 추론 과정에서 attention weight 행렬은 **높은 희소성**을 보이며, 더 큰 LLM일수록 희소성이 높음
- 소수의 중요한 토큰만 새 토큰 생성에 기여 → 중요 토큰을 식별하면 KV 텐서 접근 대폭 줄일 수 있음

**글로벌 동적 sparse 패턴:**
- 각 디코딩 스텝에서 attention weight를 분석하여 상위 k개의 중요한 토큰을 동적으로 선택
- 스텝마다 다른 토큰이 중요해질 수 있으므로 **동적** 패턴

**로컬 정적 sparse 패턴:**
- 최근 시퀀스의 로컬 윈도우 내 토큰은 항상 포함 (최근성이 높은 토큰의 중요성 보장)
- 윈도우 크기는 고정적이지만, 글로벌 패턴과 혼합하여 시너지 효과

**정확도 영향:**
- ALISA (SWA + Compression): 80% KV sparsity에서도 dense attention 대비 **5% 미만** 정확도 하락
- Local attention, Strided attention: 20% sparsity에서 즉시 정확도 붕괴 (Figure 8)
- 더 큰 LLM (13B, 30B)에서 ALISA의 정확도 유지 능력이 더욱 강화됨
- KV compression (INT8 quantization)은 정확도에 거의 영향 없음

### 3.2. 3단계 동적 스케줄링

**Phase I — GPU Caching:**
- KV 텐서 전체가 GPU 메모리에 맞는 초기 단계
- CPU 메모리 접근 불필요, 최고 성능

**Phase II — GPU-CPU Caching:**
- KV 텐서 총합이 GPU 용량을 초과하면 토큰 수준에서 GPU/CPU에 분할 저장
- 글로벌 동적으로 선택된 중요 토큰은 GPU에, 로컬 정적 토큰은 GPU에 우선 배치
- 나머지 선행 토큰은 CPU로 오프로딩

**Phase III — Recomputation-Caching:**
- 특정 시퀀스 길이 이후, CPU에서 가장 오래된 KV 텐서를 삭제하고 필요 시 GPU에서 재계산
- CPU 접근보다 재계산이 더 빠른 구간에서 활용
- 재계산은 계산 오버헤드를 유발하지만, CPU-GPU 전송 시간 감소로 순수익 발생 (1.2~1.3× 시간 단축)

**최적화 수식 (Equation 3-6):**
- Tm_j(α) = 4·b·l·h·(θc_j + θg_j) / B (전송 시간)
- 최적화 목적함수: min {α,β,p1,p2} Σ Tc_j + Σ Tm_j(α) + Σ Tr_j(β)
- 오프라인 greedy search로 최적 파라미터 사전 계산 → 추론 시 오버헤드 0

### 3.3. KV Compression (INT8 양자화)

- Fine-grained channel-wise 양자화로 KV 텐서를 FP16 → INT8로 압축
- 수식: x_quant = round(λx + z), x = λ(x_quant - z)
- 모든 모델/데이터셋에서 KV sparsity와 모델 크기에 관계없이 정확도 거의 영향 없음
- 메모리 footprint 추가 절감 → 더 긴 시퀀스 처리 가능

## 핵심 기여

- **핵심 기여:** 알고리즘-시스템 co-design으로 KV caching의 메모리 병목을 해결하는 ALISA 제안
- **알고리즘:** SWA로 80% sparsity에서도 정확도 유지하며 KV 텐서 footprint 대폭 감소
- **시스템:** 3단계 동적 스케줄링으로 GPU/CPU 메모리 활용 최적화, 토큰 수준 세밀한 관리
- **성능:** FlexGen 대비 **최대 3×**, vLLM 대비 **최대 1.9×** throughput 향상 (단일 GPU-CPU 시스템)
- **실용성:** FlexGen/HuggingFace 기반 구현, 오프라인 최적화 오버헤드 0, 다양한 LLM 모델에서 검증
- **의의:** LLM 추론이 computation 문제가 아닌 **메모리 문제**임을 명확히 정의하고, 희소 KV caching + 동적 스케줄링으로 자원 제약 환경에서의 LLM 확장성 문제를 체계적으로 해결하는 연구

## 주요 결과

- **기반 플랫폼:** FlexGen + HuggingFace Transformers
- **하드웨어:** NVIDIA Tesla V100 (16/32GB HBM), NVIDIA H100 (80GB HBM)
- **CPU:** Intel Xeon 2.60GHz, 128GB DRAM, GPU-CPU 대역폭 20GB/s
- **모델:** OPT (6.7B, 13B, 30B), LLaMA (7B, 13B, 33B), Pythia (6.7B, 12B)
- **정확도 평가:** Wiki-Text-2, Penn Treebank, Alpaca (perplexity), PIQA, COPA, OpenBookQA, Winogrande (accuracy)
- **시스템 평가:** Alpaca 데이터셋, 입력 128 + 출력 512 토큰, 배치 4~64
- **토큰 수준 메모리 관리:** layerwise KV 텐서 스케줄링

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]


## 전체 요약

[[../paper-summaries/2024ISCA-summarize/alisa-accelerating-llm-inference-via-sparsity-aware-kv-caching.md|전체 요약 보기]]
