---
tags: [paper, 2024, 2024ISCA, topic/dram, topic/gpu, topic/llm-inference]
venue: "51st Annual International Symposium on Computer Architecture (ISCA 2024)"
year: 2024
summary_path: "../paper-summaries/2024ISCA-summarize/mecla-memory-compute-efficient-llm-accelerator.md"
---

# MECLA: Memory-Compute-Efficient LLM Accelerator with Scaling Sub-matrix Partition

**Venue:** 51st Annual International Symposium on Computer Architecture (ISCA 2024)
**저자:** Yubin Qin, Yang Wang, Zhiren Zhao, Xiaolong Yang, Yang Zhou, Shaojun Wei, Yang Hu, Shouyi Yin (Tsinghua University, BNRist)

## 개요

- LLM (GPT-4, PaLM, LLaMA 등)의 추론은 기존 Transformer(BERT, GPT-2) 대비 압도적인 메모리 및 연산량을 요구: Bloom-7B의 경우 출력 토큰 하나 생성에 약 8.53x 더 많은 메모리 접근과 연산 필요
- LLaMA-7B에서 32개 출력 토큰 생성 시 14GB 가중치 데이터 접근 및 4000억 이상의 연산 필요 (98%가 linear layer에서 발생), 이는 일반 GPU와 기존 가속기의 역량을 크게 초과
- 기존 Transformer 가속기(SpAtten, FACT, A3 등)는 attention 연산에 초점: linear layer의 메모리/연산 병목을 효과적으로 해결하지 못함
- Table I에서 SpAtten은 QKV와 FFN linear layer 모두에서 최적화 미적용, FACT는 메모리 접근 최적화 미적용
- Autoregressive 생성 방식으로 인해 각 새 토큰마다 전체 모델 가중치를 반복 접근해야 하며, 이는 linear layer의 메모리 footprint 문제를 더욱 악화시킴
- LLM의 거대한 차원(scale)으로 인해 attention 연산 비중이 2% 미만으로 작아져, attention 중심 최적화가 효과적이지 않음

## 방법론

### 3.1. SSMP 원리

- 거대한 가중치 행렬 W를 small-scale source sub-matrix(SS, 크기 [x,y])와 derived sub-matrix(DS)로 분해
- 각 SS는 스케일링 스칼라를 통해 인접 DS들을 생성: DS = scalar × SS
- **메모리 절감:** 전체 가중치 행렬 대신 SS 파라미터와 DS 스케일링 스칼라만 접근하면 됨
- **연산 절감:** SS와 DS가 스케일링 스칼라 차이만 가지므로, partial sum(PSum)을 재사용하여 중복 행렬 곱셈 계산 회피 가능
- 동일 입력 채널을 공유하는 SS와 DS의 partial sum도 동일 스케일링 스칼라 비율로 차이남 → 특수 설계 회로로 연산 효율성 확보

### 3.2. 파인튜닝 방법

- SSMP 최적화를 위한 파인튜닝 하이퍼파라미터 검색 공간: {2, 4, 8, 16}
- Grid search와 successive halving으로 파인튜닝 구성 탐색
- **Standard 설정:** 계산 및 메모리 접근을 최소화하면서 GLUE 태스크 정확도 2% 이내, wikitext perplexity 5% 이내 degradation
- **Aggressive 설정:** GLUE 5%, wikitext/dolly 10% 이내 degradation에서 최소 모델 설정
- Table II: RoBERTa Large 기준 standard SSMP은 평균 0.6%, aggressive는 1.1% 정확도 저하

## 핵심 기여

- **MECLA:** SSMP 행렬 분할 방법을 활용한 memory-compute-efficient LLM 추론 가속기
- **핵심 기여:**
  - SSMP: large weight matrix를 small SS와 스케일링 스칼라로 분해하여 메모리 접근 **83.6%** 절감
  - 온칩 행렬 리그루핑 및 dual-mode 매핑으로 PSum 재사용을 통한 연산 **72.2%** 절감
  - 28nm 공정에서 **7088 GOPS/W** 에너지 효율 달성
- **기존 대비 성능:** V100 대비 **113.14x**, SpAtten 대비 **12.99x**, FACT 대비 **1.62x** 에너지 효율 향상
- **의의:** LLM의 linear layer 병목을 해결하기 위해 파라미터 효율적 전략을 적용한 최초의 가속기. attention 중심 기존 가속기와 달리, LLM에서 95% 이상을 차지하는 linear layer의 메모리/연산 병목을 동시에 해결하여 edge 배포에도 적합한 저전력 고효율 LLM 추론 가능

## 주요 결과

### 4.1. 전체 구조 (Overall Architecture)

- RISC-V 코어, DDR 컨트롤러, 1.25MB 온칩 버퍼, 8개 PE 클러스터, 보조 처리 유닛으로 구성
- AXI 버스를 통한 컴포넌트 간 통신
- **온칩 버퍼:** 256KB data buffer + 512KB source sub-matrix buffer + 512KB scaling scalar buffer
- 입력 텐서는 data buffer에서 8개 PE 클러스터로 broadcast, SS와 스케일링 스칼라는 각 클러스터에 분배
- 보조 처리 유닛: softmax, normalization, activation, sinusoidal embedding 계산 담당

### 4.2. PE 배열 설계 및 On-the-fly 행렬 리그루핑

- reordered data mapping으로 PSum 재사용 활용
- SSMP의 inner product(입력 채널)와 outer product(출력 채널) 데이터 재사용 모두 지원
- **Dual-mode 매핑 전략:**
  - nx > ny일 때: SS를 PE weight buffer에, DS 스케일링 스칼라를 scale buffer에 매핑 (outer-product PSum 재사용)
  - nx ≤ ny일 때: 행렬 곱셈 순서 변경, DS 스케일링 스칼라를 weight buffer에, SS를 scale buffer에 매핑 (inner-product 재사용)
- PE 클러스터: 16개 PE 배열, 각 배열은 4×4 PE로 구성된 행렬-벡터 곱셈기
- 각 PE 배열에서 4개의 32비트 partial sum 생성 → 4×4 스케일링 곱셈기 배열에서 추가 곱셈/누적

### 4.3. Outer-product 재사용 및 Inner-product 재결합

- **Outer-product 최적화 (Figure 8a):**
  - 관련 행을 리그루핑한 후, 4×4 가중치 행렬을 4×1 스케일링 벡터 × 1×4 가중치 벡터로 분해
  - 1×4 가중치 벡터와 입력 벡터를 먼저 곱하여 1×1 공유 PSum 생성 → 4개 스케일링 스칼라와 곱셈/누적
  - 불필요한 스케일링 곱셈기는 energy saving을 위해 게이팅

- **Inner-product 재결합 (Figure 8b):**
  - SSMP의 inner-product 수준 재사용을 활용하기 위한 연산 재결합 메커니즘
  - 가중치 데이터를 입력 채널 순서로 리그루핑하여 내적곱 수준의 중복 활용

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]


## 전체 요약

[[../paper-summaries/2024ISCA-summarize/mecla-memory-compute-efficient-llm-accelerator.md|전체 요약 보기]]
