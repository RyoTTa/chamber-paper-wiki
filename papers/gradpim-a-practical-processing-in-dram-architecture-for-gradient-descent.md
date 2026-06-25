---
tags: [paper, 2021, 2021HPCA, topic/dram, topic/pim]
venue: "2021 IEEE International Symposium on High-Performance Computer Architecture (HPCA '21)"
year: 2021
summary_path: "../paper-summaries/2021HPCA-summarize/gradpim-a-practical-processing-in-dram-architecture-for-gradient-descent.md"
---

# GradPIM: A Practical Processing-in-DRAM Architecture for Gradient Descent

**Venue:** 2021 IEEE International Symposium on High-Performance Computer Architecture (HPCA '21)
**저자:** Heesu Kim (Seoul National University), Hanmin Park (Samsung Electronics), Taehyun Kim (Seoul National University), Kwanheum Cho (Yonsei University), Eojin Lee (Samsung Electronics), Soojung Ryu (Seoul National University), Hyuk-Jae Lee (Seoul National University), Kiyoung Choi (Seoul National University), Jinho Lee (Yonsei University)

## 개요

- DNN 학습에서 NPU(Neural Processing Unit)의 성능은 주로 **메모리(DRAM) 대역폭 요구사항 최소화**에 달려 있으며, 기존 데이터 재사용 기법(Loop reordering, 주소 매핑 등)으로도 해결이 어려운 병목 존재
- **Mixed-precision 학습**과 최신 데이터 재사용 기법(MiniBatch Serialization, BN Fission and Fusion) 적용 시, **파라미터 업데이트 단계의 메모리 트래픽 비율이 급격히 증가**: ResNet-18 기준 업데이트 단계가 전체 메모리 트래픽의 **45.9%** 차지 (혼합 정밀도), 최대 층에서는 **80.5%**
- Processing-in-Memory(PIM)는 오프칩 대역폭 병목을 완화하는 기술이나, 상용 DRAM 제품에 적용되기 어려운 이유:
  - 3D 스택킹 오버헤드, 제한된 전력/열 예산, 기존 프로토콜과의 충돌
  - ISA 확장, 메모리 컨트롤러 지원 등 CPU 측면의 변경이 기존 생태계에 너무 파괴적
- DNN 학습을 위한 실용적 PIM 솔루션이 충족해야 할 세 가지 목표:
  1. **기존 프로토콜 비침해형 고정 기능 PIM**: 결정론적 지연 시간으로 메모리 컨트롤러 설계와 충돌 방지
  2. **단순하고 메모리 집약적인 함수**: 면적/전력/열 오버헤드 최소화하면서 큰 성능 향상
  3. **PIM 구성 요소와 DRAM 셀 어레이 격리**: 셀 어레이 수정 없이 주변장치에만 모듈 배치

## 방법론

### 3.1. DRAM 내부 구조利用

- **DDR4 SDRAM 아키텍처**: 다수의 bank로 구성된 2D 셀 어레이, 각 bank는 wordline(행 선택)과 bitline(데이터 전달) 사용
- **Bank group 개념**: DDR4에서 도입, I/O gating이 bank group I/O gating과 global I/O gating으로 분리
  - 연속된 column 접근이 서로 다른 bank group에 대해 이루어지면 tCCD_S(4사이클)로 스케줄링 가능
  - 같은 bank group에 대해 이루어지면 tCCD_L(25~100% 더 김) 필요
- **은행 수준 병렬성**: 각 bank가 독립적으로 접근 가능
- **Bank group 수준 병렬성**: bank group I/O gating이 bank 그룹별로 분리되어 동시 접근 가능

### 3.2. GradPIM 유닛 설계

- **위치**: Bank group I/O gating 옆에 레지스터와 함께 배치
- **구성 요소**:
  - **레지스터**: bank group I/O gating과 DRAM 셀 어레이 사이에 위치
  - **연산 유닛**: 곱셈기(multiplier)와 덧셈기(adder)로 구성된 파라미터 업데이트 로직
  - **제어 로직**: 메모리 컨트롤러의 RFU 명령어로 제어
- **동작 원리**:
  1. 메모리 컨트롤러가 RFU 명령어를 통해 GradPIM에 데이터 전달 요청
  2. GradPIM이 bank group에서 데이터를 읽음 (내부 대역폭 활용)
  3. 읽은 데이터에 대해 파라미터 업데이트 연산 수행
  4. 결과를 다시 bank group에 기록

### 3.3. 파라미터 업데이트 연산

- **SGD(Stochastic Gradient Descent) 변형 지원**:
  - 기본 SGD: θ_{t+1} = θ_t - η·g_t
  - Momentum SGD: v_t = α·v_{t-1} - η·g_t, θ_{t+1} = θ_t + v_t
  - Weight decay 포함: v_t = α·v_{t-1} - η·(β·θ_t + g_t)
- **요소별(element-wise) 연산**: 곱셈과 덧셈 위주로 구성되어 메모리 집약적
- **혼합 정밀도 지원**: 8비트 그래디언트와 32비트 마스터 가중치 혼합 처리

### 3.4. 데이터 배치 및 매핑

- **Bank group 간 데이터 분산**: 파라미터를 여러 bank group에 분산 배치하여 병렬 처리 최적화
- **Stride 패턴 활용**: bank group 간 연속 접근 패턴으로 내부 대역폭 최대 활용
- **Gradient와 가중치 분리 배치**: 읽기(gradients)와 쓰기(updated weights) 작업의 병렬 처리 지원

## 핵심 기여

- GradPIM은 **DDR4 SDRAM의 bank group 병렬성을 활용**하여 DNN 학습의 파라미터 업데이트를 DRAM 내부에서 수행하는 실용적 PIM 아키텍처
- **혼합 정밀도 학습 환경**에서 파라미터 업데이트가 전체 메모리 트래픽의 45.9%를 차지함을 명확히 입증
- 기존 DDR4 프로토콜을 완전히 존중하면서도 **최소 면적/전력 오버헤드**로 성능 향상 달성
- NPU 생태계의 유연성을 활용하여 PIM 기술의 상용화 가능성 제시
- 향후 non-CNN 워크로드(AlphaGo, MLP 등)에서 가중치 파라미터 비율 증가에 따른 추가 성능 향상 기대

## 주요 결과

- **구현 기술**: DDR4 SDRAM 프로토콜 기반, RFU 명령어 활용
- **드레인 기술 노드**: 20nm급 DRAM 공정 기술로 레이아웃 모델링
- **면적 오버헤드 분석**: bank group당 GradPIM 유닛의 면적 추정
- **전력 소비 분석**: 연산 유닛과 레지스터의 정적/동적 전력 추정
- **기존 프로토콜 완전 호환**: 기존 DDR4 명령어셋 변경 없이 확장

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2021HPCA-summarize/gradpim-a-practical-processing-in-dram-architecture-for-gradient-descent.md|전체 요약 보기]]
