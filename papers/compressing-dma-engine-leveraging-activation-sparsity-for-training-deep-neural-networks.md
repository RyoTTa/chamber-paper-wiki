---
tags: [paper, 2018, 2018HPCA, topic/compression, topic/gpu]
venue: "IEEE International Symposium on High Performance Computer Architecture (HPCA) 2018"
year: 2018
summary_path: "../paper-summaries/2018HPCA-summarize/compressing-dma-engine-leveraging-activation-sparsity-for-training-deep-neural-networks.md"
---

# Compressing DMA Engine: Leveraging Activation Sparsity for Training Deep Neural Networks

**Venue:** IEEE International Symposium on High Performance Computer Architecture (HPCA) 2018
**저자:** Minsoo Rhu (POSTECH), Mike O'Connor (NVIDIA), Niladrish Chatterjee (NVIDIA), Jeff Pool (NVIDIA), Youngeun Kwon (POSTECH), Stephen W. Keckler (NVIDIA)

## 개요

- 딥러닝 프레임워크는 GPU 물리적 메모리 내에 학습 데이터를 적재해야 하며, 이는 더 크고 깊은 DNN 학습을 제한
- 기존 가상화 기법(vDNN)은 CPU/GPU 메모리를 동시에 활용하지만, PCIe를 통한 데이터 복사 오버헤드 발생
- vDNN은 메모리 병목이 없는 경우 성능 영향이 적지만, PCIe 대역폭이 병목인 경우 평균 51% 성능 저하 (최대 63%)
- ReLU 계층에서 발생하는 activation sparsity를 활용하여 데이터 전송 대역폭 병목을 해결할 수 있는 방안 필요

## 방법론

### 3.1. 시스템 아키텍처

- cDMA는 범용 GPU DMA 아키텍처로, 기존 (de)compression 유닛을 확장하여 구현
- 메모리 컨트롤러에서 충분한 속도로 데이터를 읽어 압축 처리 (유효 PCIe 대역폭 × 압축률)
- 압축된 데이터를 PCIe를 통해 CPU 메모리로 스트리밍 전송

### 3.2. Activation Sparsity 분석

- ReLU 계층에서 발생하는 zero-valued activation이 주요 희소성 원인
- 평균 2.6배(최대 13.8배) 압축률 달성 가능
- 학습 과정에서의 sparsity 패턴을 데이터 기반으로 특성 분석

### 3.3. 메모리 가상화 전략

- vDNN과 결합하여 메모리 가상화 성능 최적화
- activation map 압축을 통한 효과적인 PCIe 대역폭 활용
- CPU/GPU 메모리 동시 활용 능력 유지하면서 성능 오버헤드 최소화

## 핵심 기여

- cDMA를 통해 DNN 학습 시 GPU-CPU 메모리 간 데이터 전송 병목 해결
- activation sparsity 활용으로 평균 53% 성능 향상
- 메모리 가상화의 성능 확장성 확보로 더 크고 깊은 DNN 학습 가능
- 향후 딥러닝 프레임워크에서의 메모리 관리 최전선 연구 기반 마련

## 주요 결과

- NVIDIA Titan Xp GPU에서 평가
- 기존 GPU 메모리 컨트롤러의 압축 유닛 확장
- 범용 DMA 아키텍처로 설계되어 다양한 DNN에 적용 가능

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/gpu.md|GPU]]


## 전체 요약

[[../paper-summaries/2018HPCA-summarize/compressing-dma-engine-leveraging-activation-sparsity-for-training-deep-neural-networks.md|전체 요약 보기]]
