---
tags: [paper, pim, neural-network-training, heterogeneous-pim, energy-efficiency]
venue: MICRO 2018
year: 2018
summary_path: paper-summaries/2018MICRO-summarize/processing-in-memory-for-energy-efficient-neural-network-training-a-heterogeneous-approach.md
---

# Processing-in-Memory for Energy-Efficient Neural Network Training: A Heterogeneous Approach

## 개요

- 3D 다이 스택 메모리의 로직 레이어에 고정 기능 연산 유닛과 ARM 기반 프로그래머블 코어를 결합한 이질적 PIM 아키텍처
- OpenCL 기반 통합 프로그래밍 모델로 다양한 PIM 하드웨어 구성 지원
- 하드웨어 이질성 인식 런타임 시스템으로 동적 연산 오프로딩 및 스케줄링

## 방법론

- **하드웨어**: 고정 기능 PIM(FIFO 레지스터 파일 + ALU) + 프로그래머블 PIM(ARM Cortex-A9, 4코어 2GHz)
- **소프트웨어**: OpenCL 커널 분할 → 고정 기능 PIM용 바이너리 + 프로그래머블 PIM용 바이너리 + CPU용 바이너리
- **런타임**: TensorFlow 런타임 확장 (약 2000줄 코드), 하드웨어 활용 정보 기반 동적 할당

## 핵심 기여

- 이질적 PIM 아키텍처 제안: 고정 기능의 높은 병렬성 + 프로그래머블의 유연성 결합
- OpenCL 기반 통합 프로그래밍 모델로 프로그래머 생산성 향상
- 하드웨어 이질성 인식 런타임 시스템으로 자동 연산 배치

## 주요 결과

- 단일 유형 PIM 대비 유의미한 에너지 효율 향상
- 다양한 신경망 학습 연산의 효과적인 PIM 오프로딩 가능
- 프로그래머블 PIM의 유연성으로 다양한 워크로드 지원

## 한계점

- 프로그래머블 PIM을 하나만 사용 (동시 실행 않는 연산에 대한 제한)
- TensorFlow 런타임에 대한 의존성
- 3D 다이 스택 메모리 기반 제한

## 관련 개념

- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
