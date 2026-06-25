---
tags: [paper, 2018, 2018ASPLOS, topic/gpu, topic/register-file]
venue: "ASPLOS 2018"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/ltrf-enabling-high-capacity-register-files-for-gpus.md"
---

# LTRF: Enabling High-Capacity Register Files for GPUs via Hardware/Software Cooperative Register Prefetching

**Venue:** ASPLOS 2018
**저자:** Mohammad Sadrosadati¹², Amirhossein Mirhosseini³, Seyed Borna Ehsani¹, Hamid Sarbazi-Azad¹⁴, Mario Drumond⁵, Babak Falsafi⁵, Rachata Ausavarungnirun⁶, Onur Mutlu²⁶ (¹Sharif University of Technology, ²ETH Zürich, ³University of Michigan, ⁴IPM, ⁵EPFL, ⁶Carnegie Mellon University)

## 개요

GPU는 대규모 레지스터 파일을 사용하여 모든 활성 스레드를 수용하지만, 높은 접근 지연 시간, 전력 소비, 큰 실리콘 면적 할당으로 인해 확장성 병목이 됨. 기존 계층적 레지스터 파일은 낮은 히트율로 인해 지연 시간 개선에 실패.

LTRF는 컴파일 시간 구간 분석을 활용하여 레지스터 작업 집합을 추정하고, 하드웨어/소프트웨어 협력으로 프리페칭. 31% IPC 향상, 46% 전력 소비 감소, 8배 용량 확장 달성.

## 방법론

### 두 수준 계층적 레지스터 파일
- 메인 레지스터 파일(Main RF): 큰 용량, 높은 지연 시간의 메모리 기술 사용 가능
- 레지스터 캐시(Register Cache): 작은 용량, 낮은 지연 시간의 SRAM
- 프리페칭 로직: 소프트웨어 제어로 메인 RF에서 캐시로 레지스터 프리페칭

### 컴파일 시간 구간 분석
- 구간(Interval) 개념: GPU 프로그램 실행을 연속적인 구간으로 분할
- 작업 집합 추정: 각 구간에서 warp가 사용할 레지스터 집합을 컴파일러가 정확히 추정
- 프리페칭 윈도우: 구간 시작 시점에 레지스터를 프리페칭할 수 있는 타이밍 결정

### 하드웨어/소프트웨어 협력 메커니즘
- 소프트웨어 컴포넌트: 컴파일러가 구간 분석 및 프리페칭 명령어 삽입
- 하드웨어 컴포넌트: 프리페칭 요청 처리 및 레지스터 전송
- 동기화 메커니즘: 프리페칭 완료와 warp 실행 시작 간 동기화

## 핵심 기여

1. 컴파일 시간 구간 분석을 활용한 하드웨어/소프트웨어 협력 레지스터 프리페칭 메커니즘 제시
2. 31% IPC 향상, 46% 전력 소비 감소, 8배 용량 확장
3. 고밀도 메모리 기술 활용 가능성 제시

## 주요 결과

- 성능 향상: 기존 레지스터 파일 대비 31% IPC 향상
- 전력 소비 감소: 레지스터 파일 전력 소비 46% 감소
- 용량 확장: 메인 레지스터 파일 용량 8배 확장 가능
- 히트율 향상: 레지스터 캐시 히트율 기존 대비 3.2배 향상

## 한계점

- 컴파일러 수정이 필요하여 기존 GPU 프로그래밍 도구 변경 필요
- 특정 워크로드에서의 프리페칭 정확도 제한
- 하드웨어 복잡성 증가로 인한 설계 비용 증가

## 관련 개념

- [[paper-wiki/concepts/gpu|GPU]]
- [[paper-wiki/concepts/register-file|Register File]]
- [[paper-wiki/concepts/prefetching|Prefetching]]

## 관련 논문

- [LTRF 논문 요약](../paper-summaries/2018ASPLOS-summarize/ltrf-enabling-high-capacity-register-files-for-gpus.md)