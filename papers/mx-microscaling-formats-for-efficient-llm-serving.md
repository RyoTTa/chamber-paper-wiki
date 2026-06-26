---
tags: [paper, 2025, 2025MICRO, topic/gpu, topic/llm-inference]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO 2025)"
year: 2025
summary_path: "../paper-summaries/2025MICRO-summarize/mx-microscaling-formats-for-efficient-llm-serving.md"
---

# MX+: Pushing the Limits of Microscaling Formats for Efficient Large Language Model Serving

**Venue:** IEEE/ACM International Symposium on Microarchitecture (MICRO 2025)
**저자:** Jungi Lee, Junyong Park, Soohyun Cha, Jaehoon Cho, Jaewoong Sim (Seoul National University)

## 개요

- LLM 추론의 비용 효율적 서빙을 위해 감소 정밀도(reduced-precision) 데이터 포맷이 필수적이며, 최근 AMD, Arm, Intel, Meta, Microsoft, NVIDIA, Qualcomm 등이 협력하여 Microscaling (MX) 데이터 포맷을 표준화
- 기존 블록 부동소수점(BFP) 변형들은 소프트웨어 프레임워크에 침입적 수정을 요구하거나, 하드웨어 벤더 간 광범위한 채택에 적합하지 않은 비관용적(conventional) 표현
- MXFP4(MX 4비트) 포맷을 가중치와 활성화 모두에 사용하면 모델 성능이 크게 저하됨 — LLM 활성화의 소수 값(outlier values)이 블록 내에서 큰 양자화 오차 발생
- 기존 Ultra low-bit BFP 변형들은 outlier 문제를 효과적으로 해결하지 못하며, language model 성능이 부적절한 수준으로 떨어짐
- MXFP6 대비 MXFP4는 메모리 대역폭 및 저장 공간 측면에서 상당한 이점을 제공하지만, outlier로 인한 정확도 손실이 핵심 병목

## 방법론

### 3.1. 기존 BFP 포맷 분석

- MX 포맷: 블록 내 요소들이 공유 마이크로 지수를 사용하며, 각 요소는 고유 지수 없이 mantissa와 sign으로 구성
- MSFP (Microsoft Floating Point): 블록 전체가 하나의 공유 지수를 사용
- Shared Microexponents: MX와 유사하나 지수 할당 방식에 차이
- Figure 1에서 기존 산업계 BFP 포맷들의 구조 비교: MX N, MSFP N, MXFP N
- MX 포맷이 동일 비트 폭을 사용하는 다른 BFP 변형들보다 language model 성능에서 우위

### 3.2. Outlier 문제 분석

- LLM 활성화에서 소수의 값들이 다른 값들보다 훨씬 큰 크기를 가짐 (outlier)
- MXFP4 포맷: 블록 크기 N에 따라 12~16비트 마이크로 지수 + 각 요소당 4비트 (sign + mantissa)
- Figure 2에서 outlier가 블록 내에서 크게 벗어날 때 quantization error가 급격히 증가하는 것을 시각화
- MXFP4는 outlier에 대해 충분한 mantissa 비트를 확보하지 못해 큰 정밀도 손실 발생

### 3.3. MX+ 메커니즘

- MX 블록에서 최대 크기 값을 가진 요소의 지수는 항상 element data type의 최대 지수값으로 설정
- 따라서 해당 요소의 고유 지수를 별도로 저장할 필요 없음 → 지수 필드를 mantissa로 재사용
- MX+에서는 outlier 요소에 대해 지수 필드를 확장 mantissa로 활용하여 정밀도 향상
- 잔여 요소들은 기존 MX 방식대로 공유 마이크로 지수 사용
- 저장 오버헤드: 블록당 최대 하나의 outlier 요소에만 추가 mantissa 비트 할당 → 미미한 수준

### 3.4. 소프트웨어 통합

- MX emulation library, NVIDIA CUTLASS, Triton 컴파일러를 활용한 MX+ 구현
- LLM 추론 파이프라인에서 기존 MX와 동일한 인터페이스로 투명하게 통합
- Token generation 단계에서의 지연 시간(slowdown)이 미미 — inference 시간 대부분이 token generation에 소요되므로 전체 오버헤드 최소화

### 3.5. 하드웨어 설계 (Architectural Support)

- NVIDIA GPU의 Tensor Core 내에서 직접 MX+ 연산을 수행할 수 있는 하드웨어 설계 제안
- 기존 dot product 파이프라인에 침입적 수정 없이 MX+ 지원 가능
- MX 성능에 근접하면서 더 높은 모델 정확도 달성
- 하드웨어적 변환: outlier 요소의 mantissa 확장 필드를 dot product 내적 연산에 포함

## 핵심 기여

- **핵심 기여:** MX 포맷에 대한 비침입적 확장 MX+를 제안하여, outlier 문제를 해결하면서 LLM 서빙 효율성 극대화
- **성능 향상:** MXFP4 대비 최대 +42.15% model performance 향상
- **실용성:** 소프트웨어 및 하드웨어 양쪽에서 모두 통합 가능하며, 기존 MX 인프라와 완전 호환
- **의의:** 산업계에서 표준화된 MX 포맷의 실용성을 높여, 4비트 양자화 기반 효율적 LLM 서빙을 현실화
- **한계 및 향후 연구:** 하드웨어 Tensor Core 수정이 필요한 수준의 완전한 최적화는 아직 연구 과제로 남음

## 주요 결과

- **소프트웨어 구현:** MX emulation library 기반, NVIDIA CUTLASS 및 Triton 컴파일러 활용
- **하드웨어 구현:** Tensor Core 내 MX+ 연산 유닛 설계 (NVIDIA GPU 아키텍처 기반)
- **양자화 설정:** 가중치와 활성화 모두 4비트 (W4A4) 또는 가중치 4비트 + 활성화 6비트 (W4A6)
- **평가 대상 LLM:** 다양한 크기의 모델 (LLaMA, OPT 등)
- **비교 대상:** MXFP4, MXFP6, MSFP, 기타 BFP 변형

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]


## 전체 요약

[[../paper-summaries/2025MICRO-summarize/mx-microscaling-formats-for-efficient-llm-serving.md|전체 요약 보기]]
