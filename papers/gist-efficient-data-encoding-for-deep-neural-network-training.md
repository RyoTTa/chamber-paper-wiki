---
tags: [paper, 2018, 2018ISCA, topic/compression, topic/dnn-accelerator]
venue: "ISCA 2018"
year: 2018
summary_path: "../paper-summaries/2018ISCA-summarize/gist-efficient-data-encoding-for-deep-neural-network-training.md"
---

# Gist: Efficient Data Encoding for Deep Neural Network Training

**Venue:** ISCA 2018
**저자:** Animesh Jain, Amar Phanishayee, Jason Mars, Lingjia Tang, Gennady Pekhimenko (Univ. of Michigan, Microsoft Research, Univ. of Toronto)

## 개요

DNN 학습에서 feature maps가 메모리의 83~97%를 차지하여 GPU 메모리 병목의 주원인이다. Gist는 레이어별 손실/손실 없는 인코딩을 통해 이 메모리 사용량을 최대 4.1× 절감한다.

## 방법론

### Binarize (ReLU→Pool)
- ReLU 출력을 1비트로 인코딩 → 32× 압축
- backward pass에서 ReLU 출력은 부호 비트만 필요

### SSDC (ReLU→Conv)
- ReLU 출력의 높은 희소성 활용, 희소 형식 저장 + 밀집 연산
- cuDNN의 최적화된 밀집 연산 성능 유지

### DPR (Delayedy Precision Reduction)
- Forward pass: 32비트 정밀도 유지, backward pass용으로만 정밀도 축소
- 정확도 손실 거의 없이 공격적 비트 절약

## 핵심 기여

1. DNN 학습의 feature maps에 대한 레이어별 인코딩 프레임워크 제시
2. 시간적 간격을 활용한 새로운 메모리 최적화 패러다임
3. CNTK 통합으로 실제 학습에 즉시 적용 가능

## 주요 결과

- **메모리 절감**: 최대 4.1×, 평균 1.8× (5개 DNN)
- **성능 오버헤드**: 4% 미만
- **정확도**: 기존 대비 변화 없음
- **학습 속도**: ResNet-1202에서 22% 향상 (더 큰 minibatch 사용 가능)

## 한계점

- 특정 레이어 조합에서만 최적 인코딩 적용 가능
- 32비트 초과 정밀도의 경우 효과 제한

## 관련 개념

- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/dnn-accelerator.md|DNN Accelerator]]
