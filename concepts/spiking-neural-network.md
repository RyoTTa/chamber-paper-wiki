---
tags: [concept, spiking-neural-network, neuromorphic, digital-neuron]
source_count: 1
last_updated: 2026-06-25
---

# Spiking Neural Network

## Summary

Spiking Neural Network(SNN)은 세 번째 세대 신경망 모델로, 뉴런과 뉴런 간 상호작용인 스파이크에 시간 개념을 통합합니다. 생물학적 신경계와 유사한 작동 모델로 정확한 신경계 모델링이 가능합니다.

## Key Ideas

### SNN의 특징
- 시간 의존적 동작: 막 전위가 시간에 따라 변하고, 특정 임계값에 도달하면 스파이크 발사
- 흥분성/억제성 시냅스: 막 전위를 증가 또는 감소시키는 시냅스
- 시냅스 가중치(synaptic weight): 시냅스의 강도
- 불응기(refractory): 스파이크 후 일정 시간 동안 새로운 스파이크 발사 불가

### 뉴런 모델
- **Hodgkin-Huxley(HH) 모델**: 높은 모델링 정확도, 높은 계산 오버헤드
- **Leaky Integrate-and-Fire(LIF) 모델**: 지수 감쇠를 사용한 단순화된 모델
- **Linear LIF(LLIF) 모델**: 선형 감쇠로 계산 오버헤드 추가 절감
- **Adaptive Exponential(AdEx) 모델**: 적응 및 지수 발생 특성

### 생물학적 공통 특징 (Flexon 분류)
- **막 감쇠**: 지수(EXD), 선형(LID)
- **입력 스파이크 축적**: 전류 기반(CUB), 전도 기반(COBE/COBA), 반전 전압(REV)
- **스파이크 발생**: 이차(QDI), 지수(EXI)
- **스파이크 트리거 전류**: 적응(ADT), 하위 진동(SBT)
- **불응기**: 절대(AR), 상대(RR)

### 시뮬레이션 도전과제
- 뉴런 계산 단계의 높은 지연 시간 (시뮬레이션 지연의 최대 32.2%)
- 다양한 뉴런 모델 지원 필요성
- 기존 가속기의 모델 기반 설계로 인한 유연성 부족

## Related Papers

- **Flexon**: 생물학적 공통 특징 기반 유연한 디지털 뉴런 — 12뉴런 배열로 CPU 대비 6,186배 에너지 효율 향상, 공간 폴딩으로 7.62mm² 칩 면적 ([paper-summaries/2018ISCA-summarize/flexon-a-flexible-digital-neuron-for-efficient-spiking-neural-network-simulations.md])

## Cross-references

- [[paper-wiki/concepts/neuromorphic-computing|Neuromorphic Computing]] - SNN 기반 컴퓨팅 패러다임
- [[paper-wiki/concepts/dnn-accelerator|DNN Accelerator]] - 기존 딥러닝 가속기와의 비교