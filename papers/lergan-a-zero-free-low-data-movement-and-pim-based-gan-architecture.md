---
tags: [paper, 2018, 2018MICRO, topic/pim, topic/gan, topic/accelerator]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO), 2018"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/lergan-a-zero-free-low-data-movement-and-pim-based-gan-architecture.md"
---

# LerGAN: A Zero-free, Low Data Movement and PIM-based GAN Architecture

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Haiyu Mao, Mingcong Song, Tao Li, Yuting Dai, Jiwu Shu (Tsinghua University, University of Florida, Guizhou University)

## 개요

- GAN(Generative Adversarial Network)은 비지도 학습 방법으로 영상 예측, 자율 주행 등 다양한 분야에서 중요한 역할을 수행
- MIT Technology Review가 2018년 10대 돌파구 기술로 선정할 정도로 주목받는 기술
- GAN 훈련 시 세 가지 주요 도전 과제: 집약적 통신, 비효율적 연산, 빈번한 오프칩 메모리 접근
- LerGAN은 PIM(Process-in-Memory) 기반 GAN 가속기로这些挑战을 해결

## 방법론

### 3.1. Zero-free 데이터 리슈어핑

- ReRAM 기반 PIM에서 zero 값은 불필요한 연산을 유발
- Zero-free 데이터 리슈어핑 스킴은 zero 값을 제거하고 non-zero 요소만 PIM에서 처리
- 불필요한 PIM 연산을 제거하여 에너지 소비 및 처리 시간 감소

### 3.2. 3D-연결 PIM

- GAN 훈련의 두 가지 주요 데이터플로우: 전파(propagation)와 갱신(updating)
- 3D-연결 PIM은 데이터플로우에 따라 내부 연결을 동적으로 재구성
- 메모리 내에서 직접 연산 수행으로 데이터 이동 대폭 감소

### 3.3. LerGAN 아키텍처

- PIM 메모리 배열과 로직 레이어의 3D 적층 구조
- 프로그래머에게 다양한 가속 수준 제공

## 핵심 기여

- **핵심 기여:** PIM 기반 GAN 가속기를 위한 두 가지 새로운 기술 제시 (zero-free 데이터 리슈어핑, 3D-연결 PIM)
- **성능 향상:** 기존 플랫폼 대비 최대 **47.2x** 속도 향상 및 **9.75x** 에너지 절약

## 주요 결과

- FPGA 기반 가속기 대비 **47.2x** 속도 향상
- GPU 플랫폼 대비 **21.42x** 속도 향상
- ReRAM 기반 신경망 가속기 대비 **7.46x** 속도 향상
- GPU 플랫폼 대비 평균 **9.75x** 에너지 절약
- ReRAM 기반 신경망 가속기 대비 평균 **7.68x** 에너지 절약

## 한계점

- ReRAM 기반 구현의 실제 하드웨어 검증 필요
- 다양한 GAN 아키텍처 및 더 큰 데이터셋에 대한 확장성 검증 필요
- ReRAM 셀 크기와 연결 밀도 간 트레이드오프 존재

## 관련 개념

- [[paper-wiki/concepts/processing-in-memory|Processing-in-Memory]]
- [[paper-wiki/concepts/gan-acceleration|GAN Acceleration]]
- [[paper-wiki/concepts/reram|ReRAM]]

## 관련 논문

- [lergan-a-zero-free-low-data-movement-and-pim-based-gan-architecture.md](../paper-summaries/2018MICRO-summarize/lergan-a-zero-free-low-data-movement-and-pim-based-gan-architecture.md)
