---
tags: [paper, 2023, 2023ISCA, topic/compression, topic/dram, topic/gpu, topic/llm-inference]
venue: "Proceedings of the 50th Annual International Symposium on Computer Architecture (ISCA 2023)"
year: 2023
summary_path: "../paper-summaries/2023ISCA-summarize/olive-accelerating-llms-via-hardware-friendly-outlier-victim-pair-quantization.md"
---

# OliVe: Accelerating Large Language Models via Hardware-friendly Outlier-Victim Pair Quantization

**Venue:** Proceedings of the 50th Annual International Symposium on Computer Architecture (ISCA 2023)
**저자:** Cong Guo, Jiaming Tang, Weiming Hu, Jingwen Leng, Chen Zhang, Fan Yang, Yunxin Liu, Minyi Guo, Yuhao Zhu (Shanghai Jiao Tong University, Shanghai Qi Zhi Institute, Microsoft Research, Tsinghua University AIR, University of Rochester)

## 개요

- Transformer 기반 LLM의 모델 크기가 **2년마다 240배**씩 성장하며, 하드웨어 발전 속도(**3.1배/2년**)를 크게 상회
  - 예: OPT-175B는 최신 H100 GPU(80GB)에 단일 GPU로 적재 불가
- **Quantization**은 LLM 추론 비용을 줄이는 가장 하드웨어 효율적인 방법이나, Transformer 모델의 **outlier** 문제로 기존 방법의 효과가 제한됨
  - Outlier: 일반 값 대비 훨씬 큰 값을 가지는 극소수의 요소 (<0.1%)
  - 6B 이상 모델에서 outlier에 대한 민감도가 급격히 증가 → 일반 quantization으로는 정확도 크게 저하
- **기존 outlier-aware 양자화의 한계**:
  - **GOBO**: 희소 좌표 리스트(coordinate list)로 outlier 위치를 전역적으로 관리 → 인코딩/디코딩 하드웨어 복잡성 + 오케스트레이션 컨트롤러 필요
  - **OLAccel**: 유사한 희소 인코딩 사용 → 비정렬 메모리 접근
  - **BiScaled-DNNs**: 블록 희소 인덱스 포맷 사용 → 메모리 서브시스템과 비호환
  - **DRQ**: 비트맵 직접 사용 → 하드웨어 오버헤드 큼
  - 모든 기존 방법이 **전역적(global)으로 outlier를 분리**하여 처리 → 복잡한 하드웨어 설계와 낮은 성능 이점

## 방법론

### 3.1 Outlier 분석 (Section 2)

- **CNN vs Transformer 차이 (Figure 2)**:
  - ResNet-18 (ImageNet): 대부분의 텐서에서 outlier <0.1%, 최대 3σ 이상 비율 매우 낮음
  - BERT-base (MNLI): 특정 텐서에서 outlier 비율이 **최대 40%**까지 증가, 6σ 이상의 값도 빈번
- **모델 크기와 outlier 관계**: 모델이 커질수록 outlier의 영향력과 빈도가 증가
- **Quantization 정확도 영향**: outlier를 무시하면 정확도 급락, outlier를 일반 값과 동일하게 클리핑하면 정확도 급락

### 3.2 OVP 인코딩 방식 (Section 3)

- **인코딩 흐름 (Figure 1b)**:
  1. **Prune Victims**: outlier와 인접한 정상 값을 zero로 프루닝
  2. **Quantize & Embed Outliers**: outlier를 8비트 정밀도로 인코딩, victim 위치에 삽입
  3. **OVP Encoding**: 4비트 outlier + 4비트 victim = **8비트 특수 포맷** 구성
- **인코딩 예시**:
  ```
  입력 행렬:
  [1.5, 2.6, 0, -98]    → [-98은 outlier, 0은 victim]
  [17.6, 4.2, 7.1, -6.8] → [17.6은 outlier, 4.2는 victim]
  
  OVP 인코딩:
  (0, -98) → 8비트: 0010 1000
  (16, 0)  → 8비트: 인접 victim 활용
  ```
- **GOBO 대비 차이 (Figure 1a)**: GOBO는 coordinate list로 모든 outlier 위치를 전역 관리 (비정렬), OLIve는 로컬 쌍으로 메모리 정렬 달성

### 3.3 하드웨어 통합 (Section 4)

- **Systolic Array 호환**: 8비트 OVP 포맷이 기존 TPU/NVIDIA GPU의 systolic array/tensor core와 자연스럽게 통합 가능
- **Mixed-precision 지원**: outlier는 8비트, 정상 값은 4비트로 혼합 정밀도 아키텍처 지원
- **Locality 기반 처리**: 인코딩/디코딩이 완전히 로컬에서 수행 → 전역 동기화 불필요
- **기존 가속기(GOBO) 대비 장점**:
  - GOBO: DRAM에서만 weight 압축/해제, on-chip은 FP16/32 유지
  - OliVe: on-chip에서도 저정밀 연산 가능 → 성능 대폭 향상

### 3.4 Pruning 효과 분석

- Outlier를 clip하면 **재앙적 정확도 하락** (0.1% 미만의 outlier가 모델 성능의 핵심)
- 동일한 비율의 정상 값을 pruning하면 **정확도 하락 <0.1%**
- OVP의 victim pruning은 모델 프루닝과 유사한 효과 → 통계적으로 정당화 가능

## 핵심 기여

- **핵심 기여**: 최초로 로컬 기반 outlier 처리를 위한 **Outlier-Victim Pair 양자화** 제안
- **성능 향상**: GOBO 대비 **4.5배 속도**, **4.0배 에너지 절감**, 우수한 정확도
- **하드웨어 호환성**: 기존 systolic array/tensor core와 완전 호환, 전역 동기화 불필요
- **의의**: LLM의 outlier 문제를 하드웨어 효율적으로 해결하여 대규모 모델 추론의 비용과 에너지를 크게 절감
- **향후 활용**:更大规模 Transformer 모델, mixed-precision 아키텍처, 다양한 가속기에 폭넓게 적용 가능

## 주요 결과

- **데이터 타입**: int4, FP4 (정상 값), 8비트 OVP 포맷 (outlier 포함)
- **인코딩 포맷**: 4비트 outlier + 4비트 victim = 8비트 특수 포맷 (기존 int8/FP8과 다름)
- **하드웨어 통합**: 기존 quantization 프레임워크 및 가속기 아키텍처에 쉽게 통합 가능
  - Google TPU systolic array
  - NVIDIA GPU tensor core
- **Mixed-type 지원**: 각 값의 동적 범위와 표현 형식에 따라 다른 데이터 타입 적용 가능

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]


## 전체 요약

[[../paper-summaries/2023ISCA-summarize/olive-accelerating-llms-via-hardware-friendly-outlier-victim-pair-quantization.md|전체 요약 보기]]
