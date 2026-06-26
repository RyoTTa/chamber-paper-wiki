---
tags: [paper, 2025, 2025MICRO, topic/gpu, topic/llm-inference]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO 2025)"
year: 2025
summary_path: "../paper-summaries/2025MICRO-summarize/axcore-quantization-aware-approximate-gemm-for-llm-inference.md"
---

# AxCore: A Quantization-Aware Approximate GEMM Unit for LLM Inference

**Venue:** IEEE/ACM International Symposium on Microarchitecture (MICRO 2025)
**저자:** Jiaxiang Zou, Yonghao Chen, Xingyu Chen, Chenxi Xu, Xinyu Chen (The Hong Kong University of Science and Technology (Guangzhou))

## 개요

- Transformer 기반 LLM은 FP GEMM(General Matrix-Matrix Multiplication)에 의존하며, GPT-3(175B 파라미터)은 FP16 기준 약 350GB 메모리 필요 — 일반 GPU의 메모리 용량을 크게 초과
- LLM 추론에서 선형 레이어의 GEMM 연산은 전체 연산의 69%~99%를 차지(Figure 2, OPT-175B/LLaMA-3.1-405B 기준, 시퀀스 길이 10k~20k 토큰)
- Weight-only quantization(INT4/FP4)은 모델 가중치를 저비트로 압축하여 메모리 및 대역폭 요구사항을 줄이지만, 기존 mpGEMM(mixed-precision GEMM) 유닛은 여전히 FP 곱셈기를 포함하여 하드웨어 비용이 높음
- Floating-Point Multiplication Approximation(FPMA)는 곱셈을 정수 덧셈으로 대체하여 효율적이나, 기존 방법은 균일 정밀도(FP16×FP16)에만 한정되어 혼합 정밀도 mpGEMM에 직접 적용 불가
- 낮은 비트 폭의 FP4 포맷에서 subnormal 값이 빈번하게 발생하며, FPMA의 수학적 근사(log₂(1+M) ≈ M)가 subnormal에선 성립하지 않아 심각한 정확도 손실 발생(Figure 4)

## 방법론

### 3.1. mpFPMA Processing Element (PE)

- 각 PE는 Approximate Multiplication 블록과 Accumulation 블록으로 구성
- 입력: 낮은 비트 양자화된 가중치 Wq(FP4)와 PreAdd 유닛에서 사전 계산된 중간 값 T
- T = A - B1 + C1 (A: FP16 활성화, B1: 지수 바이어스 보정, C1: 포맷별 보상 상수)
- PE 내부: SNC(Subnormal Number Conversion) → mantissa 정렬 → T + Align(Wq) = R (정수 덧셈으로 곱셈 근사)
- Guard 유닛이 영(0) 입력을 검출하여 출력을 강제로 0으로 설정
- Partial FP Adder로 수직 방향 부분 합을 누적, 정규화는 후처리 단계로 연기

### 3.2. Subnormal Number Conversion (SNC)

- FP4 포맷(E1M2, E2M1, E3M0)에서 subnormal 인코딩을 가장 가까운 정규 표현으로 변환
- 변환 테이블(Table 1): mantissa 비트 폭별로 subnormal → normal 매핑 정의
- 예: E1M2에서 subnormal "011" → normal "10" (동일 값 0.75)
- 정확한 매핑이 불가능한 경우 확률적 라운딩(stochastic rounding) 적용 — 활성화의 가장 중요한 mantissa 비트에서 샘플링하여 라운딩 방향 교대, 시스템적 편향 방지
- 모든 변환 출력은 통일된 내부 포맷 S1E3M2로 변환 → 하드웨어가 포맷에 무관하게 동작 가능

### 3.3. Correction Advancing (보정 사전 계산)

- mpFPMA에서 보정 값 B1과 C1은 피연산자의 FP 포맷에 의해 결정되며, 가중치 값과 무관
- PreAdd 모듈에서 한 번만 계산: T = A - B1 + C1
- 이 값을 행(row) 전체 PE에 스트리밍 → 각 PE는 7비트 덧셈기만으로 R = T + Align(Wq) 수행
- 기존 방식 대비 15비트 덧셈기를 PE마다 복제할 필요 없음 → PE 면적 대폭 절감(Figure 12)

### 3.4. Normalization Postponing

- 전통적 GEMM 아키텍처: 각 PE에서 실시간 정규화(LZD, 시프트, 라운딩) → 면적/지연 시간 증가
- AxCore: PE에서 NMa + 2비트 폭 mantissa로 부분 결과 누적, 정규화는 공유 Norm 모듈에 위임
- n×n 배열에서 로직 중복을 n배 절감 → 확장성 및 에너지 효율 향상(Figure 11c)

### 3.5. Adaptive Format-Aware Quantization

- 블록별로 최적의 FP4 포맷(E3M0, E2M1, E1M2)을 선택하는 오프라인 양자화
- E3M0: 2의 거듭제곱 분포에 적합 (희소 데이터), E2M1: 표준, E1M2: 균일 분포에 적합
- 블록 크기: OPT는 128×64, LLaMA2는 64×64
- 포맷 선택 목표: 실제 활성화 분포 하에서 평균 제곱 오차 최소화
  - D_type = argmin_{d∈D} ||A·Wd - A·W||²₂ (Equation 12)
- FPMA 기반 양자화/역양자화 통합: wq = clamp(round(w - S + B - C)), wr = wq + S - B + C2 → C와 C2가 상쇄되어 원래 값 보존

## 핵심 기여

- **핵심 기여:** FP 곱셈기를 완전히 제거하고 정수 덧셈만으로 혼합 정밀도 mpGEMM을 수행하는 최초의 approximate 가속기
- **성능 향상:** W4-FP16에서 compute density 6.7× 향상(FPC 대비), 면적 31%~37% 절감(Baseline 대비)
- **정확도 유지:** 모든 OPT/LLaMA2 모델에서 기존 4비트 양자화 대비 동등 이상의 perplexity 달성
- **실용성:** 오프라인 calibration과 호환되며, 다양한 FP4 포맷(E3M0, E2M1, E1M2)을 블록별로 선택적으로 적용 가능
- **의의:** Approximate computing과 quantization-aware design의 결합을 통해 LLM 추론 가속기의 효율성 한계를 재정의, 낮은 비트 정밀도에서도 높은 정확도를 유지하면서 하드웨어 자원을 대폭 절감

## 주요 결과

- **구현 언어:** SpinalHDL, Synopsys Design Compiler로 Verilog RTL 합성
- **기술 노드:** 28nm TSMC
- **타겟 주파수:** 1 GHz
- **기본 구성:** 64×64 systolic array, 4×4 tiling
- **가속기 구성:** GEMM Unit(AxCore) + Weight Buffer + Unified Buffer + Vector Unit + Control Unit + DRAM 인터페이스(Figure 13)
- **SNC 유닛 오버헤드:** PE 면적의 평균 3.5%
- **FPMA 기반 디양자화(AxScale):** 역양자화를 정수 덧셈 2회로 구현 → 멀티플라이어 불필요

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]


## 전체 요약

[[../paper-summaries/2025MICRO-summarize/axcore-quantization-aware-approximate-gemm-for-llm-inference.md|전체 요약 보기]]
