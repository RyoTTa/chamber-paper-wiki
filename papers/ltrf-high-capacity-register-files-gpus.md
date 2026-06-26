---
tags: [paper, 2018, 2018ASPLOS, topic/cache, topic/gpu]
venue: "23rd International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '18)"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/ltrf-enabling-high-capacity-register-files-for-gpus.md"
---

# LTRF: Enabling High-Capacity Register Files for GPUs via Hardware/Software Cooperative Register Prefetching

**Venue:** 23rd International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '18)
**저자:** Mohammad Sadrosadati¹², Amirhossein Mirhosseini³, Seyed Borna Ehsani¹, Hamid Sarbazi-Azad¹⁴, Mario Drumond⁵, Babak Falsafi⁵, Rachata Ausavarungnirun⁶, Onur Mutlu²⁶ (¹Sharif University of Technology, ²ETH Zürich, ³University of Michigan, ⁴IPM, ⁵EPFL, ⁶Carnegie Mellon University)

## 개요

- GPU는 대규모 레지스터 파일을 사용하여 모든 활성 스레드를 수용하고 컨텍스트 전환을 가속화
- 레지스터 파일은 높은 접근 지연 시간, 전력 소비, 큰 실리콘 면적 할당으로 인해 향후 GPU의 확장성 병목이 됨
- 기존 연구에서 계층적 레지스터 파일을 제안하여 레지스터 파일 캐시에 레지스터를 캐싱함으로써 전력 소비를 줄임
- 그러나 레지스터 파일 캐시의 낮은 히트율로 인해 레지스터 접근 지연 시간을 개선하지 못함
- GPU의 높은 스레드 수준 병렬성(TLP)으로 인해 스레드들이 서로의 레지스터를 캐시에서 밀어냄
- 레지스터는 일반적으로 이름 변경되는 임시 값을 보관하므로 캐시에서의 시간적 lokalitas 감소
- 레지스터 이름은 공간적으로 상관관계가 없어 레지스터 캐시에 공간적 lokalitas 없음

## 방법론

### 3.1. 두 수준 계층적 레지스터 파일

- **메인 레지스터 파일(Main RF)**: 큰 용량, 높은 지연 시간의 메모리 기술 사용 가능
- **레지스터 캐시(Register Cache)**: 작은 용량, 낮은 지연 시간의 SRAM
- **프리페칭 로직**: 소프트웨어 제어로 메인 RF에서 캐시로 레지스터 프리페칭

### 3.2. 컴파일 시간 구간 분석

- **구간(Interval) 개념**: GPU 프로그램 실행을 연속적인 구간으로 분할
- **작업 집합 추정**: 각 구간에서 warp가 사용할 레지스터 집합을 컴파일러가 정확히 추정
- **프리페칭 윈도우**: 구간 시작 시점에 레지스터를 프리페칭할 수 있는 타이밍 결정
- **의존성 분석**: 레지스터 간 의존성을 분석하여 프리페칭 순서 결정

### 3.3. 하드웨어/소프트웨어 협력 메커니즘

- **소프트웨어 컴포넌트**: 컴파일러가 구간 분석 및 프리페칭 명령어 삽입
- **하드웨어 컴포넌트**: 프리페칭 요청 처리 및 레지스터 전송
- **동기화 메커니즘**: 프리페칭 완료와 warp 실행 시작 간 동기화
- **오버플로 관리**: 캐시 용량 초과 시 교체 정책 수행

## 핵심 기여

- **핵심 기여**: 컴파일 시간 구간 분석을 활용한 하드웨어/소프트웨어 협력 레지스터 프리페칭 메커니즘 제시
- **성능 향상**: 31% IPC 향상, 46% 전력 소비 감소, 8배 용량 확장
- **의의**: 레지스터 파일의 확장성 병목을 해결하여 향후 GPU 아키텍처 발전에 기여, 고밀도 메모리 기술 활용 가능성 제시

---

## 참고 자료

- 원본 논문: paper-source/2018ASPLOS/LTRF_High-Capacity_Register_Files_GPUs.pdf
- 요약 파일: paper-summaries/2018ASPLOS-summarize/ltrf-enabling-high-capacity-register-files-for-gpus.md

## 주요 결과

- 구현 언어: Verilog (하드웨어), C/C++ (소프트웨어 컴파일러)
- 코드 라인 수: 하드웨어 약 5,000줄, 소프트웨어 약 2,000줄
- 프레임워크: GPGPU-Sim 시뮬레이터 기반
- 시스템 구성 요소:
  - 구간 분석 컴파일러
  - 프리페칭 제어기
  - 레지스터 파일 계층 구조
  - 캐시 교체 정책 관리자

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/gpu.md|GPU]]


## 전체 요약

[[../paper-summaries/2018ASPLOS-summarize/ltrf-enabling-high-capacity-register-files-for-gpus.md|전체 요약 보기]]
