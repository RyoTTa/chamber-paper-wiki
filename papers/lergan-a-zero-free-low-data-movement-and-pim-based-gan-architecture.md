---
tags: [paper, 2018, 2018MICRO, topic/gpu, topic/pim, topic/virtual-memory]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/lergan-a-zero-free-low-data-movement-and-pim-based-gan-architecture.md"
---

# LerGAN: A Zero-free, Low Data Movement and PIM-based GAN Architecture

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Haiyu Mao, Mingcong Song, Tao Li, Yuting Dai, Jiwu Shu (Tsinghua University, University of Florida, Guizhou University)

## 개요

- GAN(Generative Adversarial Network)은 비지도 학습 방법으로 영상 예측, 자율 주행 등 다양한 분야에서 중요한 역할을 수행
- MIT Technology Review가 2018년 10대 돌파구 기술로 선정할 정도로 주목받는 기술
- GAN 훈련 시 세 가지 주요 도전 과제:
  1. **집약적 통신:** GAN의 복잡한 훈련 단계로 인한 intensive communication
  2. **비효율적 연산:** 특수 합성곱(convolution)으로 인한 ineffectual computations
  3. **빈번한 오프칩 메모리 접근:** 생성기(generator)와 판별기(discriminator) 간 중간 데이터 교환을 위한 frequent off-chip memory accesses
- 기존 가속기(FPGA, GPU, ReRAM 기반 신경망 가속기)는 GAN 훈련의 특수한 요구사항을 효과적으로 처리하지 못함
- 데이터 이동(data movement)이 GAN 훈련의 주요 병목 현상으로, I/O가 병목이 되는 것을 방지해야 함

## 방법론

### 3.1. Zero-free 데이터 리슈어핑

- ReRAM 기반 PIM에서 zero 값은 불필요한 연산을 유발
- GAN의 특수 합성곱(strided/dilated convolution)에서 zero 패딩으로 인해 많은 zero 값이 생성
- Zero-free 데이터 리슈어핑 스킴은 zero 값을 제거하고 non-zero 요소만 PIM에서 처리
- 불필요한 PIM 연산을 제거하여 에너지 소비 및 처리 시간 감소

### 3.2. 3D-연결 PIM

- GAN 훈련의 두 가지 주요 데이터플로우:
  1. **전파(Propagation):** 입력 데이터가 생성기/판별기를 순방향으로 통과
  2. **갱신(Updating):** 가중치가 역방향 전파에 따라 갱신됨
- 3D-연결 PIM은 데이터플로우에 따라 내부 연결을 동적으로 재구성
- 전파 시: 인접 PIM 셀 간 연결 사용
- 갱신 시: 재구성된 연결을 통한 가중치 업데이트
- 메모리 내에서 직접 연산 수행으로 데이터 이동 대폭 감소

### 3.3. LerGAN 아키텍처

- PIM 메모리 배열과 로직 레이어의 3D 적층 구조
- 각 PIM 셀에서 곱셈-축적(MAC) 연산 수행
- 동적 연결 재구성을 위한 스위칭 메커니즘
- 프로그래머에게 다양한 가속 수준 제공:
  - 레벨 1: Zero-free 데이터 리슈어핑만 적용
  - 레벨 2: 3D-연결 PIM 적용
  - 레벨 3: 두 기술 모두 적용 (전체 LerGAN)

## 핵심 기여

- **핵심 기여:** PIM 기반 GAN 가속기를 위한 두 가지 새로운 기술 제시 (zero-free 데이터 리슈어핑, 3D-연결 PIM)
- **성능 향상:** 기존 플랫폼 대비 최대 **47.2x** 속도 향상 및 **9.75x** 에너지 절약
- **의의:** GAN 훈련의 데이터 이동 병목을 해결하는 새로운 접근법 제시
- **향후 과제:** 다양한 GAN 아키텍처 및 더 큰 데이터셋에 대한 확장성 검증 필요

## 주요 결과

- 구현 언어: 시뮬레이션 기반
- ReRAM 기반 PIM 프레임워크 사용
- GAN 아키텍처: DCGAN (Deep Convolutional GAN) 기반
- 시스템 구성 요소:
  - ReRAM 기반 PIM 배열
  - 3D 연결 스위칭 메커니즘
  - Zero-free 데이터 리슈어핑 로직
  - 메모리 컨트롤러 및 인터페이스

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/lergan-a-zero-free-low-data-movement-and-pim-based-gan-architecture.md|전체 요약 보기]]
