---
tags: [dnn-accelerator, cnn, relu, early-activation, computation-reduction]
venue: ISCA
year: 2018
summary_path: paper-summaries/2018ISCA-summarize/snapea-predictive-early-activation-for-reducing-computation-in-deep-convolutional-neural-networks.md
---

# SnaPEA: Predictive Early Activation for Reducing Computation in Deep Convolutional Neural Networks

## 개요

SnaPEA는 CNN의 ReLU 활성화 함수가 음수 입력에 0을 출력하는 특성을 활용하여 convolution 연산을 조기에 중단하는 기법입니다. Exact mode(정확도 손실 0%)와 Predictive mode(정확도-연산 트레이드오프)를 모두 지원합니다.

## 방법론

- **Exact Mode**: 가중치를 부호 순서로 재배치하고 부분 합의 부호 비트를 모니터링 → 합이 음수가 되면 중단
- **Predictive Mode**: 다변수 최적화 알고리즘으로 층별 임계값 결정 → 더 일찍 중단
- **Early Termination Unit (ETU)**: 하드웨어에서 부호 비트 모니터링 및 중단 제어
- **Weight Pre-processing**: 가중치를 부호 순서로 정렬하는 정적 분석

## 핵심 기여

1. CNN의 algorithmic 구조 (ReLU zero 출력)을 활용한 최초의 조기 활성화 기법
2. Exact/Predictive 두 모드로 정확도-연산 트레이드오프 제어
3. 기존 정적 pruning과 complementary한 동적 기법

## 주요 결과

- Exact mode: 평균 28% speedup, 16% energy reduction (정확도 손실 0%)
- Predictive mode (3% 정확도 손실): 67.8% convolution 층에서 적용, 평균 2.02× speedup, 1.89× energy saving
- 최대: 3.59× speedup, 3.14× energy reduction
- 정적 pruning + SnaPEA: 최대 63% speedup, 49% energy reduction

## 한계점

- Predictive mode에서 정확도 손실 발생 (3% 수준)
- CNN 아키텍처에 따라 적용 가능한 층 비율이 달라짐
- 하드웨어 ETU 오버헤드가虽小但非零

## 관련 concept

- [[paper-wiki/concepts/dnn-accelerator.md|DNN Accelerator]]
