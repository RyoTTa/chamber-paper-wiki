---
tags: [spiking-neural-network, digital-neuron, flexibility, neuroscience]
venue: ISCA
year: 2018
summary_path: paper-summaries/2018ISCA-summarize/flexon-a-flexible-digital-neuron-for-efficient-spiking-neural-network-simulations.md
---

# Flexon: A Flexible Digital Neuron for Efficient Spiking Neural Network Simulations

## 개요

다양한 뉴런 모델이 공유하는 생물학적 공통 특징을 활용한 유연한 디지털 뉴런입니다. 모델 기반 설계의 한계를 극복하고 효율적인 SNN 시뮬레이션을 가능하게 합니다.

## 방법론

- **생물학적 공통 특징 식별**: 5개 카테고리 12개 특징 분류
- **특징 기반 데이터 패스**: 각 특징에 대한 전용 연산 유닛 구현
- **공간 폴딩**: 중복 연산 유닛 제거로 칩 면적 최소화

## 핵심 기여

1. 다양한 뉴런 모델이 공유하는 12개 생물학적 공통 특징 식별
2. 모델 기반 설계의 한계를 극복한 유연한 디지털 뉴런
3. 공간 폴딩을 통한 칩 면적 최소화

## 주요 결과

- 12뉴런 Flexon: CPU 대비 6,186배 에너지 효율 향상
- 72뉴런 공간 폴딩 Flexon: CPU 대비 122.45배 속도 향상
- 칩 면적: 7.62mm² (TSMC 45nm)

## 한계점

- SNN 시뮬레이션에 특화된 설계
- 범용 프로세서 대비 범용성 제한

## 관련 concept

- [[paper-wiki/concepts/spiking-neural-network.md|Spiking Neural Network]]
- [[paper-wiki/concepts/neuromorphic-computing.md|Neuromorphic Computing]]
- [[paper-wiki/concepts/digital-neuron.md|Digital Neuron]]