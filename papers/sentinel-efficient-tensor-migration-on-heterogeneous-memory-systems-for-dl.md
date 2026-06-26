---
tags: [paper, 2021, 2021HPCA, topic/dram, topic/gpu, topic/nvm]
venue: "2021 IEEE International Symposium on High-Performance Computer Architecture (HPCA '21)"
year: 2021
summary_path: "../paper-summaries/2021HPCA-summarize/sentinel-efficient-tensor-migration-on-heterogeneous-memory-systems-for-deep-learning.md"
---

# Sentinel: Efficient Tensor Migration and Allocation on Heterogeneous Memory Systems for Deep Learning

**Venue:** 2021 IEEE International Symposium on High-Performance Computer Architecture (HPCA '21)
**저자:** Jie Ren (University of California, Merced), Jiaolin Luo (University of California, Merced), Kai Wu (University of California, Merced), Minjia Zhang (Microsoft), Hyeran Jeon (University of California, Merced), Dong Li (University of California, Merced)

## 개요

- DNN(Deep Neural Network) 학습은 극도로 많은 메모리 용량을 필요로 하며, 최신 언어 모델과 번역 모델은 **수백억 개의 파라미터**를 보유하여 학습에 **수백 GB의 메모리**가 요구됨
- 메모리 부족은 DNN 학습에서 OOM(Out-of-Memory) 크래시를 유발하며, 모델 크기와 배치 크기를 제한하여 학습 효율성과 효과성을 저하시킴
- 이종 메모리(Heterogeneous Memory, HM)는 고속 메모리(예: DRAM)와 저속 메모리(예: NVM)를 결합하여 메모리 용량 확장 가능성을 제공하지만, **텐서 마이그레이션 및 할당 최적화**에 새로운 과제를 야기
- 기존 연구의 한계:
  - DNN 도메인 지식에 과도하게 의존하여 특정 모델(예: feedforward CNN)에만 적용 가능
  - **페이지 수준의 false sharing**으로 인해 불필요한 텐서 마이그레이션 발생
  - 텐서를 개별적으로 배치하여 메모리 단편화 및 예상치 못한 마이그레이션 초래
  - 짧은 수명(lifetime)의 텐서가 고속 메모리에서 불필요하게 오래 머물러 고속 메모리 공간 낭비

## 방법론

### 3.1. 동적 텐서 프로파일링

- OS와 런타임 프로파일링을 결합하여 **텐서 수준 프로파일링** 수행
- 각 텐서의 **메모리 접근 빈도**와 **수명(lifetime)** 정보를 수집
- 페이지 수준이 아닌 텐서 수준에서 메모리 접근 패턴을 추적하여 false sharing 문제 해결
- 프로파일링 오버헤드는 **수 초 이내**이며 전체 학습 시간의 1% 미만

### 3.2. 데이터 재조직(Data Reorganization)

- 프로파일링 결과를 바탕으로 메모리 접근 빈도와 수명이 유사한 텐서를 **동일 페이지에 그룹핑**
- 페이지당 25%가 자주 접근되는 텐서로 채워지고 나머지가 드물게 접근되는 텐서로 채워지는 경우, 기존에는 4개 페이지 모두가 고속 메모리에 배치되었으나 Sentinel은 불필요한 할당 방지
- 짧은 수명 텐서와 긴 수명 텐서를 분리하여 고속 메모리 공간 최적화

### 3.3. 적응형 레이어 기반 마이그레이션(Adaptive Layer-Based Migration)

- 학습 스텝(순전파 + 역전파)을 동일 크기의 **마이그레이션 간격(migration interval)**으로 분할
- 각 간격의 시작 시 **느린 메모리 → 빠른 메모리** 텐서 마이그레이션 실행 (다음 간격에 필요한 텐서 프리페치)
- 각 간격의 중간 시점에 **빠른 메모리 → 느린 메모리** 마이그레이션 실행 (고속 메모리 공간 확보)
- 마이그레이션 주문: 메모리 접근 수 기준 **감소 순서**로 수행하여 가장 많이 접근되는 텐서부터 우선 마이그레이션
- 레이어 기반 간격의 장점:
  - 레이어 간 작업 완료를 보장 (명시적 동기화 불필요)
  - 프로파일링 단계에서 수집된 메모리 접근 패턴을 마이그레이션에 쉽게 활용
  - 작업 수준 병렬성(operation-level parallelism)으로 인한 간격 결정 어려움 해소

### 3.4. 마이그레이션 간격 길이 최적화

- 간격이 너무 길면 마이그레이션할 텐서가 고속 메모리 공간보다 커질 수 있음 (**공간 제약**)
- 간격이 너무 짧으면 텐서 마이그레이션 시간이 critical path에 노출됨 (**시간 제약**)
- ResNet-32 실험에서 간격 길이에 따라 **21% 성능 차이** 발생 (최적 간격: 8)
- 공간 제약과 시간 제약 간의 트레이드오프를 수식으로 공식화하여 최적 간격 결정

## 핵심 기여

- Sentinel은 동적 프로파일링과 OS/런타임 공동 조율을 통해 HM 상에서 DNN 학습의 텐서 관리를 자동 최적화
- **80% 고속 메모리 절약**하면서 동등한 성능 유지, 기존 최신 솔루션 대비 CPU에서 **37%**, GPU에서 **2x~21%** 성능 향상
- 레이어 기반 적응형 마이그레이션으로 메모리 접근 패턴을 효과적으로 활용
- DNN 도메인 지식에 의존하지 않는 범용 솔루션으로 다양한 DNN 모델(CNN, RNN, Transformer)에 적용 가능

## 주요 결과

- **구현 언어/프레임워크**: TensorFlow 기반 구현
- **CPU 플랫폼**: Intel Xeon E5-2698 v4 (20 cores, 2.2 GHz), 128 GB DDR4 DRAM + 128 GB Intel Optane DC Persistent Memory
- **GPU 플랫폼**: NVIDIA Tesla V100 (16 GB HBM2), CUDA v10.1
- **프로파일링 방법**: 동적 프로파일링 (런타임에 텐서 접근 패턴 수집)
- **비교 대상**: Unified Memory, vDNN, AutoTM, SwapAdvisor, Capuchin

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]


## 전체 요약

[[../paper-summaries/2021HPCA-summarize/sentinel-efficient-tensor-migration-on-heterogeneous-memory-systems-for-deep-learning.md|전체 요약 보기]]
