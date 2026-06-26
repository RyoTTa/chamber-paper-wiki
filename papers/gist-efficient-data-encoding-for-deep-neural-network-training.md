---
tags: [paper, 2018, 2018ISCA, topic/compression, topic/dram, topic/gpu, topic/storage]
venue: "45th Annual International Symposium on Computer Architecture (ISCA '18)"
year: 2018
summary_path: "../paper-summaries/2018ISCA-summarize/gist-efficient-data-encoding-for-deep-neural-network-training.md"
---

# Gist: Efficient Data Encoding for Deep Neural Network Training

**Venue:** 45th Annual International Symposium on Computer Architecture (ISCA '18)
**저자:** Animesh Jain (University of Michigan, Microsoft Research), Amar Phanishayee (Microsoft Research), Jason Mars (University of Michigan), Lingjia Tang (University of Michigan), Gennady Pekhimenko (University of Toronto)

## 개요

- DNN 학습에서 GPU 메모리는 주요 병목으로, 모델이 깊어질수록 중간 레이어 출력(feature maps)의 메모리 사용량이 급격히 증가
- VGG16에서 stashed feature maps가 전체 메모리의 83%를 차지하며, Inception에서는 97%에 달함 (minibatch size 64 기준)
- 기존 방법들의 한계:
  - **가중치 압축 기반**: 학습 시 가중치는 전체 메모리의 일부에 불과하여 효과 제한
  - **CPU-GPU 데이터 전송 기반 (vDNN 등)**: CPU/GPU 간 데이터 이동으로 인한 성능 오버헤드 발생
  - **저정밀 연산 기반**: feature maps를 직접 대상으로 하지 않거나, 공격적 양자화 시 학습 정확도 저하
- 핵심 문제: **feature maps의 시간적 간격(temporal gap)을 활용한 효율적 인코딩 메커니즘 부재** — forward pass에서 생성된 feature maps는 backward pass에서 오래 후에 사용되는데, 그 사이 32비트 단밀도로 불필요하게 저장됨

## 방법론

### 3.1. 메모리 사용량 분석
- 5개 CNN (AlexNet, NiN, Overfeat, VGG16, Inception)의 메모리 사용량 분석
- Stashed feature maps가 학습 시 메모리 사용의 주요 구성 요소
- Larger minibatch = 더 나은 GPU 활용도이나, 메모리 제한으로 증가 어려움

### 3.2. Binarize 인코딩 (ReLU→Pool)
- ReLU backward pass: 출력이 양수이면 gradient를 그대로 전달, 음수이면 0
- 따라서 ReLU 출력은 **부호 비트(0/1)만 저장하면 됨** → 32비트 대신 1비트
- 32× 압축률, decode 비용 거의 없음 (단순 lookup)

### 3.3. Sparse Storage and Dense Compute (SSDC) (ReLU→Conv)
- ReLU 출력의 높은 희소성 활용 (일반적으로 40~70%가 0)
- 메모리에서는 희소 형식(CSR 등)으로 저장하여 공간 절약
- 연산 시에는 밀집 형식으로 변환하여 cuDNN의 최적화된 밀집 연산 활용
- 희소성에 비례한 메모리 절약 + 밀집 연산의 성능 유지

### 3.4. Delayed Precision Reduction (DPR) (Lossy)
- Forward pass: 전체 32비트 정밀도 유지 → 정확도 보장
- Forward pass 종료 후: 해당 feature map의 정밀도를 8비트 또는 그 이하로 축소
- Backward pass에서 decode 시 정밀도 복원
- 정확도 손실 거의 없음: 두 사용 시점 사이에서만 압축되고, 실제 연산은 항상 32비트로 수행

### 3.5. 시스템 구현
- **정적 분석**: DNN 실행 그래프를 분석하여 각 레이어에 적용 가능한 인코딩 자동 탐지
- **인코딩/디코딩 삽입**: 실행 그래프에 encode/decode 함수를 동적으로 삽입
- **메모리 할당 최적화**: 라이프타임 분석을 통해 인코딩된 표현의 효과적 메모리 할당 지원

## 핵심 기여

- **핵심 기여**: DNN 학습의 feature maps에 대한 레이어별 손실/손실 없는 인코딩 프레임워크 제시
- **성능**: 2× 메모리 절감 (최대 4.1×), 4% 오버헤드 미만
- **실용성**: CNTK에 통합되어 실제 DNN 학습에 즉시 적용 가능
- **의의**: GPU 메모리 병목을 완화하여 더 크고 깊은 DNN 학습을 가능하게 하며, feature maps의 시간적 간격을 활용한 새로운 메모리 최적화 패러다임 제시

## 주요 결과

- **구현 언어**: Python (CNTK 프레임워크 기반)
- **프레임워크**: Microsoft CNTK ( Cognitive Toolkit)
- **적용 대상**: CNN, RNN, LSTM 등 다양한 DNN 아키텍처
- **변경 범위**: 프레임워크 레이어 수준의 코드 수정, 기존 cuDNN 연산과 호환

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2018ISCA-summarize/gist-efficient-data-encoding-for-deep-neural-network-training.md|전체 요약 보기]]
