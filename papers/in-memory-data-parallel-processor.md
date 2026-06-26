---
tags: [paper, 2018, 2018ASPLOS, topic/gpu, topic/nvm]
venue: "ASPLOS 2018 (Architectural Support for Programming Languages and Operating Systems)"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/in-memory-data-parallel-processor.md"
---

# In-Memory Data Parallel Processor

**Venue:** ASPLOS 2018 (Architectural Support for Programming Languages and Operating Systems)
**저자:** Daichi Fujiki (University of Michigan), Scott Mahlke (University of Michigan), Reetuparna Das (University of Michigan)

## 개요

- NVM(Non-Volatile Memory)의 발전이 인메모리 컴퓨팅의 새로운 지평을 열음
- 계산용 NVM이 제공하는 significant한 성능 향상에도 불구하고, 기존 연구들은 메모리 배열에 특화된 커널을 수동으로 매핑하는 데 의존
- 이러한 접근 방식은 더 일반적인 워크로드를 실행하기에 비실용적
- ReRAM(Resistive Memory) 기반 가속기는 머신러닝 알고리즘에 특화되어 일반적인 계산에 대한 활용도가 낮음
- 기존 CPU/GPU 아키텍처 및 커스텀 ASIC 대비 orders of magnitude 성능 향상 가능성에도 불구하고, 범용 계산에 대한 연구 부족

## 방법론

### 3.1. 프로세서 아키텍처
- 메모리 배열과 여러 디지털 컴포넌트가 타일로 그룹화된 구조
- 커스텀 인터커넥트를 통한 배열 간 통신 및 명령 공급 촉진
- 각 배열은 저장 단위이자 벡터 프로세싱 유닛으로 기능
- ReRAM 배열 확장: 점곱 외에 덧셈, 요소별 곱셈, 뺄셈 연산 지원

### 3.2. 프로그래밍 프레임워크
- 데이터 흐름과 벡터 프로세싱 개념의 융합
- SIMD 실행 모델 채택: 매 사이클 명령이 타일 내 여러 배열로 멀티캐스팅
- 인메모리 프로그래밍을 위한 컴파일러 프레임워크 개발
- TensorFlow 입력을 인메모리 프로세서 코드로 변환

### 3.3. 명령 세트 아키텍처 (ISA)
- 메모리 배열에 대한 일반화된 계산 기능 제공
- 컴팩트한 명령 세트로 메모리 배열의 다양한 연산 지원
- 점곱, 덧셈, 곱셈, 뺄셈 등의 기본 연산 지원
- 프로그래밍 용이성을 위한 높은 수준의 추상화 제공

## 핵심 기여

- 프로그래밍 가능한 인메모리 프로세서 아키텍처의 실현 가능성 입증
- 데이터 병렬 애플리케이션에서 significant한 성능 및 에너지 효율성 향상
- TensorFlow 기반 컴파일러 프레임워크로 프로그래밍 용이성 제공
- 향후 인메모리 컴퓨팅 연구를 위한 기초 아키텍처 및 프로그래밍 모델 제시

## 주요 결과

- ReRAM 기반 인메모리 프로세서 시뮬레이터 구현
- TensorFlow 기반 컴파일러 프레임워크 개발
- 프로세서 아키텍처의 RTL(Register Transfer Level) 설계
- 기존 NVM 하드웨어와의 호환성 확인

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]


## 전체 요약

[[../paper-summaries/2018ASPLOS-summarize/in-memory-data-parallel-processor.md|전체 요약 보기]]
