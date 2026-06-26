---
tags: [paper, 2018, 2018MICRO, topic/gpu, topic/pim]
venue: "MICRO 2018 (51st Annual IEEE/ACM International Symposium on Microarchitecture)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/processing-in-memory-for-energy-efficient-neural-network-training-a-heterogeneous-approach.md"
---

# Processing-in-Memory for Energy-Efficient Neural Network Training: A Heterogeneous Approach

**Venue:** MICRO 2018 (51st Annual IEEE/ACM International Symposium on Microarchitecture)
**저자:** Jiawen Liu (UC Merced / UC Santa Cruz), Hengyu Zhao (UC San Diego), Matheus Almeida Ogleari/sharp (UC Santa Cruz), Dong Li (UC Merced), Jishen Zhao (UC San Diego)

## 개요

- 딥러닝 신경망(DNN) 학습은 프로세서와 메모리 간 빈번한 데이터 이동으로 인해 막대한 에너지와 시간이 소요됨
- VGG(138M 파라미터), AlexNet(61M 파라미터) 등 대규모 모델의 학습 시 데이터 이동이 주요 에너지/성능 병목
- 기존 저정밀 데이터, 모델 프루닝 기법은 모델 정확도에 미치는 영향 정량화가 어려우며, 데이터 이동 문제를 근본적으로 해결하지 못함
- PIM(Processing-in-Memory) 기술은 데이터 이동 문제를 해결하기 위한 유망한 접근법으로 주목받고 있으나, 기존 PIM 설계는 고정 기능(fixed-function) 또는 프로그래머블 중 하나만 사용하는 단일 유형 구조
- 신경망 학습 워크로드는 다양한 메모리 접근 패턴, 계산 집약도, 병렬성을 가지므로, 단일 유형 PIM으로는 최적의 에너지 효율과 병렬성/프로그래머빌리티 간 균형 달성 어려움

## 방법론

### 3.1. 하드웨어 아키텍처 (Fig. 3, 7)

- **고정 기능 PIM**: FIFO 레지스터 파일, ALU로 구성된 간단한 연산 유닛
  - 높은 병렬성 제공, 특정 연산(예: Conv2D BackpropFilter)에 최적화
  - ISA 수준 명령어로 접근, 어셈블리 수준 인트린식 또는 라이브러리 호출로 프로그래밍
- **프로그래머블 PIM**: ARM Cortex-A9 프로세서 (4개 2GHz 코어, in-order 파이프라인)
  - 유연한 프로그래밍 가능, 복잡한 연산 처리
  - 표준 프로그래밍 패러다임(스레딩 패키지 또는 GPGPU 프로그래밍 인터페이스) 사용
- **구현**: 하나의 프로그래머블 PIM만 사용 (일반적으로 동시에 실행되지 않는 연산들을 위해)

### 3.2. 프로그래밍 모델 (Fig. 4)

- **4개 바이너리 파일 생성**:
  1. CPU용 바이너리
  2. 프로그래머블 PIM용 바이너리
  3. 고정 기능 PIM용 바이너리 (OpenCL 커널에서 코드 섹션 추출 후 변환)
  4. 고정 기능 PIM 호출이 포함된 프로그래머블 PIM용 바이너리
- **OpenCL 커널 분할**: 큰 연산(예: Conv2DBackpropFilter)을 OpenCL 커널에서 코드 섹션을 추출하고, 고정 기능 PIM에서 실행할 수 있는 작은 커널로 변환

### 3.3. 런타임 시스템

- **CPU 런타임**: TensorFlow 런타임에 약 2000줄 코드 추가
  - 장치 초기화 및 특성화 (OpenCL 인트린식 사용)
  - PIM 장치 컨텍스트 및 인스턴스 생성
  - 프로그래머블 PIM과의 통신 메커니즘
  - 하드웨어 활용 정보 기반 동적 연산 오프로딩
- **프로그래머블 PIM 런타임**: 재귀적 PIM 커널 지원 및 연산 파이프라인 처리
  - 고정 기능 PIM에 대한 자동 오프로딩
  - 각 PIM의 동적 활용 추적 (완료된/남은 연산 수 기록)

### 3.4. 저수준 API (Table III)

| API 함수 | 설명 |
|----------|------|
| `pim_fix()` | 고정 기능 PIM에 특정 연산 오프로딩 |
| `pim_prog()` | 프로그래머블 PIM에 커널 실행 요청 |
| `pim_status()` | 특정 PIM의 바쁨/한가함 상태 확인 |
| `work_query()` | 특정 연산 완료 여부 확인 |
| `work_info()` | 연산 위치 및 데이터 위치 조회 |

## 핵심 기여

- 이질적 PIM 아키텍처가 신경망 학습에서 데이터 이동 병목을 효과적으로 해결
- OpenCL 기반 통합 프로그래밍 모델로 프로그래머 생산성 및 하드웨어 다양성 동시 지원
- 하드웨어 이질성 인식 런타임 시스템이 동적 연산 할당을 통해 에너지 효율 및 활용도 최적화
- PIM 기반 신경망 학습 가속을 위한 실용적인 소프트웨어/하드웨어 공동 설계 방법론 제시

## 주요 결과

| 항목 | 세부사항 |
|------|---------|
| **프로그래머블 PIM** | ARM Cortex-A9, 4개 2GHz 코어 |
| **구현 언어** | OpenCL (확장) |
| **런타임 수정** | TensorFlow 런타임에 약 2000줄 코드 추가 |
| **하드웨어 구성** | 3D 다이 스택 메모리 + 로직 레이어 |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/processing-in-memory-for-energy-efficient-neural-network-training-a-heterogeneous-approach.md|전체 요약 보기]]
