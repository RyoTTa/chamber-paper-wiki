---
tags: [paper, 2022, 2022MICRO, topic/cache, topic/dram, topic/gpu, topic/nvm, topic/pim]
venue: "55th IEEE/ACM International Symposium on Microarchitecture (MICRO 2022)"
year: 2022
summary_path: "../paper-summaries/2022MICRO-summarize/multi-layer-in-memory-processing.md"
---

# Multi-Layer In-Memory Processing

**Venue:** 55th IEEE/ACM International Symposium on Microarchitecture (MICRO 2022)
**저자:** Daichi Fujiki (Keio University), Alireza Khadem (University of Michigan), Scott Mahlke (University of Michigan / Nvidia Research), Reetuparna Das (University of Michigan)

## 개요

- 메모리 히어라키의 다양한 메모리 기술(SRAM, DRAM, NVM)이 각각의 속도/밀도 트레이드오프를 가지고 있으나, 기존 인메모리 컴퓨팅 연구는 **단일 메모리 계층에만 초점**을 맞추어 왔다.
- 애플리케이션에 따라 최적의 인메모리 컴퓨팅 위치가 다르다: 재사용 패턴, 데이터 크기, 명령어 혼합에 따라 SRAM, DRAM, NVM 중 선호도가 달라진다(Figure 1).
- **워크로드 다이나미즘:** GNN(Graph Neural Networks)의 서브그래프 학습은 서브그래프 크기 분포가 매우 불균일하여(ogbl-citation2 데이터셋 기준 Figure 5), 단일 하드웨어로는 비효율적.
  - 빠른 SRAM은 면적 제한으로 대규모 서브그래프 처리에 부적합.
  - 느린 NVM은 소규모 서브그래프 처리 시 과도한 지연 유발.
- 기존 PIM(Processing-in-Memory) 솔루션은 단일 메모리 계층에서만 동작하므로, **여러 계층의 이질적인 연산 자원을 통합 활용**하는 프레임워크가 부재.
- 서버급 GPU(Xeon + GPU) 베이스라인 대비 GNN 추론에서 상당한 성능 격차 존재.

## 방법론

### 3.1. 프로그래밍 프론트엔드

- **SIMD DFG 추출:** 애플리케이션의 인메모리 처리 함수를 SIMD Data Flow Graph로 기술(Python/C++에서 추출 가능).
- **크로스 컴파일:** SIMD DFG를 각 메모리 백엔드의 인메모리 ISA로 크로스 컴파일(Figure 6).
  - SRAM 백엔드: 비트-시리얼 연산 ISA.
  - DRAM 백엔드: charge-sharing 기반 비트와이즈 연산 ISA.
  - ReRAM 백엔드: 아날로그 MAC 연산 ISA.
- **런타임 흐름:** 함수 호출 → MLIMP 스케줄러 → 작업 생성 → 성능 예측기 입력 → 메모리 할당 → 작업 큐 enqueue → 인메모리 디바이스에서 실행.
- **기존 프레임워크와의 호환성:** TensorFlow의 protobuf 형식 DFG 추출, CUDA/OpenACC 프로그래밍 모델 지원.

### 3.2. 메모리 할당 및 공존

- **In-memory computing + 일반 메모리 시스템 공존:** 애플리케이션의 일부 커널만 인메모리에서 실행하고 나머지는 호스트 프로세서에서 실행 가능.
- **메모리 할당:** 인메모리 컴퓨팅에 사용할 메모리 영역을 시스템 소프트웨어가 분리하여 할당.
- **스케줄러:** 작업별 메모리 할당 크기를 조절하여 병렬성과 작업별 지연시간의 균형을 맞춤.

### 3.3. 작업 스케줄링 및 성능 예측

- **NP-hard 문제:** 메모리 히어라키의 이질적인 리소스에 작업을 배분하는 것은 자원 제약 프로젝트 스케줄링 문제로 NP-hard.
- **해석적 스케일링 모델:** 각 메모리에서의 커널 실행 시간을 해석적으로 모델링하여 스케줄링 결정에 활용.
- **신경망 기반 성능 예측기:** 가벼운 신경망 회귀 모델로 특정 메모리-할당 크기 조합의 성능을 예측.
- **스케줄링 전략 비교 (Figure 19):**
  - Global scheduler (지역 + 글로벌 조정)이 거의 모든 시나리오에서 최적 성능 달성.
  - 단일 메모리 계층 IMP 대비 **7.1×** 성능 향상.

### 3.4. GEMM/SpMM 커널 매핑

- **In-SRAM (LLC):** 비트-시리얼 연산. n비트 곱셈에 n²+3n-2사이클, 비트-슬라이스 256개 벡터 요소를 수직 정렬(Figure 2).
- **In-DRAM:** Charge-sharing 기반 TRA(Triple-Row Activation)로 AND/OR 연산 지원(Ambit 방식). 3-input majority 게이트로 모든 논리 연산 가능.
- **In-ReRAM:** 아날로그 MAC 연산. 셀 전도율과 입력 전압의 곱셈 → 비트라인에서 전류 합산(Kirchhoff 법칙)(Figure 3).
- **GNN 매핑:**
  - SpMM(이웃 집계): 희소 인접 행렬 A와 밀집 특징 행렬 X의 곱셈 → In-ReRAM에서 아날로그 MAC 활용.
  - GEMM(특징 결합): 밀집 가중치 행렬과의 곱셈 → In-SRAM/ReRAM에서 효율적 처리.
  - 서브그래프 크기별 최적 메모리 자동 선택.

## 핵심 기여

- **핵심 기여:** 메모리 히어라키의 여러 계층을 온디맨드 인메모리 컴퓨팅 리소스로 통합 활용하는 최초의 MLIMP 시스템 제안.
- **성능:** GNN 추론에서 서버급 GPU 대비 **4.8×**, 일반 애플리케이션에서 단일 레이어 IMP 대비 **7.1×** 성능 향상.
- **에너지:** 기존 대비 **5.02×** 에너지 효율 개선.
- **스케줄링:** 해석적 스케줄링 + 신경망 기반 예측기로 NP-hard 스케줄링 문제를 실용적으로 해결.
- **범용성:** GNN(SpMM + GEMM)뿐 아니라 일반 데이터 병렬 애플리케이션에도 적용 가능.
- **의의:** 워크로드 다이나미즘이 있는 애플리케이션에서 이질적인 메모리 기술의 상호보완적 특성을 체계적으로 활용하는 프레임워크를 제시하여, 인메모리 컴퓨팅의 실용화를 한 단계 진전시킴.

## 주요 결과

- **시뮬레이터:** 자체 개발 MLIMP 시뮬레이터 (메모리별 인메모리 컴퓨팅 모델 포함).
- **하드웨어 베이스라인:** 서버급 GPU (Intel Xeon + NVIDIA GPU).
- **인메모리 디바이스:** In-SRAM (CPU LLC 기반), In-DRAM (DDR4 기반), In-ReRAM (crossbar array 기반).
- **소프트웨어 프레임워크:** SIMD DFG 기반 프론트엔드, 크로스 컴파일러 백엔드.
- **대상 애플리케이션:** 
  - GNN 추론: GCN (Graph Convolutional Network) on ogbl-citation2.
  - 일반 데이터 병렬 애플리케이션: Parsec/Rodinia 벤치마크.
- **스케줄러:** Global scheduler, Local scheduler, Baseline(LJF) 비교.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2022MICRO-summarize/multi-layer-in-memory-processing.md|전체 요약 보기]]
