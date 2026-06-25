---
tags: [neural-network-accelerator, quantization, energy-efficiency, outlier-aware]
venue: ISCA
year: 2018
summary_path: paper-summaries/2018ISCA-summarize/energy-efficient-neural-network-accelerator-based-on-outlier-aware-low-precision-computation.md
---

# Energy-efficient Neural Network Accelerator Based on Outlier-aware Low-precision Computation

## 개요

아웃라이어 인식 양자화를 하드웨어로 구현한 OLAccel 가속기입니다. 4비트 정밀도로 깊은 딥러닝 네트워크를 지원하면서 에너지 효율을 크게 향상시킵니다.

## 방법론

- **아웃라이어 인식 양자화**: 데이터를 저정밀(4비트, 97%)과 고정밀(16비트, 3%) 영역으로 분할
- **혼합 정밀도 MAC**: 일반 4비트 MAC + 고정밀 16비트 MAC 동시 지원
- **제로 건너뛰기**: 영 입력 활성화에 대한 연산 건너뛰기

## 핵심 기여

1. 4비트 정밀도로 깊은 딥러닝 네트워크 지원 (ResNet-101 등)
2. 아웃라이어 가중치/활성화의 차별화 처리
3. 일반 및 고정밀 연산의 파이프라인 동작

## 주요 결과

- 16비트 Eyeriss 대비 최대 62.2% 에너지 절감 (ResNet-18)
- 8비트 Eyeriss 대비 최대 49.5% 에너지 절감
- 3% 아웃라이어 비율로 정확도 유지 (<1% 손실)

## 한계점

- 아웃라이어 비율에 따른 정확도-효율 트레이드오프
- 첫 번째 합성층에서 더 높은 정밀도 필요

## 관련 concept

- [[paper-wiki/concepts/neural-network-acceleration.md|Neural Network Acceleration]]
- [[paper-wiki/concepts/quantization.md|Quantization]]
- [[paper-wiki/concepts/energy-efficient-computing.md|Energy-Efficient Computing]]