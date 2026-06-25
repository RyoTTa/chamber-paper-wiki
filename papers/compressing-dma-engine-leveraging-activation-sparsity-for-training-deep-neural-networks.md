---
tags: [paper, 2018, 2018HPCA, topic/dnn-accelerator, topic/compression]
venue: "HPCA 2018"
year: 2018
summary_path: "../paper-summaries/2018HPCA-summarize/compressing-dma-engine-leveraging-activation-sparsity-for-training-deep-neural-networks.md"
---

# Compressing DMA Engine: Leveraging Activation Sparsity for Training Deep Neural Networks

**Venue:** HPCA 2018
**저자:** Minsoo Rhu (POSTECH), Mike O'Connor (NVIDIA), Niladrish Chatterjee (NVIDIA), Jeff Pool (NVIDIA), Youngeun Kwon (POSTECH), Stephen W. Keckler (NVIDIA)

## 개요

딥러닝 프레임워크는 GPU 물리적 메모리 내에 학습 데이터를 적재해야 하며, 이는 더 크고 깊은 DNN 학습을 제한합니다. 기존 가상화 기법(vDNN)은 CPU/GPU 메모리를 동시에 활용하지만, PCIe를 통한 데이터 복사 오버헤드로 인해 평균 51% 성능 저하(최대 63%)가 발생합니다.

cDMA(Compressing DMA Engine)는 activation map의 희소성(sparsity)을 활용한 압축을 통해 GPU-CPU 간 데이터 전송 병목을 해결합니다. 평균 2.6배(최대 13.8배) 압축률과 평균 53%(최대 79%) 성능 향상을 달성합니다.

## 방법론

### cDMA 아키텍처
- 기존 GPU 메모리 컨트롤러의 (de)compression 유닛을 확장하여 구현
- 메모리 컨트롤러에서 충분한 속도로 데이터를 읽어 압축 처리 (유효 PCIe 대역폭 × 압축률)
- 압축된 데이터를 PCIe를 통해 CPU 메모리로 스트리밍 전송

### Activation Sparsity 활용
- ReLU 계층에서 발생하는 zero-valued activation이 주요 희소성 원인
- 학습 과정에서의 sparsity 패턴을 데이터 기반으로 특성 분석
- 다양한 DNN 아키텍처에서의 sparsity 분석을 통한 최적 압축 전략 수립

### 메모리 가상화 최적화
- vDNN과 결합하여 메모리 가상화 성능 최적화
- activation map 압축을 통한 효과적인 PCIe 대역폭 활용
- CPU/GPU 메모리 동시 활용 능력 유지하면서 성능 오버헤드 최소화

## 핵심 기여

1. DNN 학습 과정에서의 activation sparsity를 체계적으로 분석하고 활용하는 최초의 연구
2. 범용 GPU DMA 아키텍처인 cDMA 제안으로 기존 압축 유닛 활용 설계 오버헤드 최소화
3. 메모리 가상화의 성능 확장성 확보로 더 크고 깊은 DNN 학습 가능

## 주요 결과

- **성능 향상**: 평균 53% (최대 79%) vDNN 대비 성능 개선
- **압축률**: 평균 2.6배 (최대 13.8배) 달성
- **평가 환경**: NVIDIA Titan Xp GPU에서 다양한 DNN 아키텍처 평가

## 한계점

- NVIDIA Titan Xp와 같은 특정 GPU 아키텍처에서의 평가로 다른 GPU에서의 일반화 필요
- activation sparsity가 낮은 DNN의 경우 효과 제한
- PCIe 대역폭이 병목이 아닌 경우 성능 향상 제한

## 관련 개념

- [[paper-wiki/concepts/dnn-accelerator.md|DNN Accelerator]]
- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/gpu.md|GPU]]

## 관련 논문

- [paper-summaries/2018HPCA-summarize/compressing-dma-engine-leveraging-activation-sparsity-for-training-deep-neural-networks.md]