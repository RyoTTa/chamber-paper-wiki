---
tags: [paper, 2018, 2018MICRO, topic/pim, topic/gpu]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/tapas-generating-parallel-accelerators-from-parallel-programs.md"
---

# TAPAS: Generating Parallel Accelerators from Parallel Programs

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Steven Margerm, Amirali Sharifian, Apala Guha, Arrvindh Shriraman (Simon Fraser University), Gilles Pokam (Intel Corporation)

## 개요

- 기존 High-Level Synthesis (HLS) 도구들은 병렬 프로그램에서 하드웨어 가속기를 생성할 때 정적 병렬리즘(static parallelism)만 지원.
- 현재 HLS 도구들은 고정된 패턴(파이프라인, 데이터 병렬 커널)만 타겟으로 하며, 동적 병렬리즘(dynamic parallelism)을 지원하지 못함.
- 소프트웨어 프로그래머가 병렬성을 표현하는 능력이 제한되어 있으며, 생성된 가속기는 동적 비동기성(asyncrony)과 캐시 미스 숨김(latency hiding)이라는 병렬 하드웨어의 핵심 이점을 잃음.
- 기존 HLS 도구들은 Sequential compiler 기반이며, 병렬 프로그램 의존성 그래프(PDG)를 제대로 분석하지 못함.

## 방법론

### 1. Tapir 병렬 컴파일러 통합

- Tapir는 LLVM의 확장으로, fork-join 병렬리즘을 IR에 명시적으로 표현.
- TAPAS는 Tapir의 병렬리즘 마커를 활용하여 태스크 의존성을 자동으로 추론.
- 기존 HLS 도구와 달리 별도의 어노테이션이나 라이브러리 호출 없이 병렬 프로그램을 하드웨어로 합성.

### 2. 하드웨어 생성 파이프라인

1. **정적 분석 단계:** 병렬 IR을 분석하여 태스크 그래프 구성
   - 태스크 간 의존성 관계 추론
   - 동기화 필요성 결정
   - 메모리 공유 패턴 분석
2. **태스크별 RTL 생성:** 각 태스크에 대해 개별적인 데이터플로우 실행 로직 합성
   - 임의의 제어 흐름(루프 포함) 지원
   - 메모리 연산 지원
   - 공유 리소스 관리

### 3. 마이크로아키텍처 구조

- **Tiles:** 각 태스크에 할당된 독립적인 실행 단위
- **Task Queue:** 태스크 생성 및 동기화를 위한 큐
- **Shared RAM/Cache:** 태스크 간 데이터 공유를 위한 메모리
- **AXI Bus:** 외부 DRAM과의 인터페이스
- **Spawn/Sync 하드웨어:** 태스크 생성 및 동기화를 위한 전용 하드웨어 유닛

## 핵심 기여

- Tapir 병렬 컴파일러 IR을 활용하여 태스크 기반 가속기를 자동 생성하는 최초의 HLS 도구.
- 동적, 중첩, 재귀적 병렬 패턴을 모두 지원하는 범용 병렬 가속기 합성.
- Intel Xeon 대비 **20배 전력 효율** while 성능은 유지하는 가속기 생성 가능.

## 주요 결과

- **전력 효율:** TAPAS가 생성한 가속기가 Intel Xeon 대비 **20배 높은 전력 효율** 달성.
- **성능:** Xeon과 비교하여 유사한 수준의 성능 유지 while 20배 적은 전력 소비.
- **태스크 생성 지연:** 경량 태스크 생성에 약 **10 사이클** 소요.
- **세밀한 병렬리즘 활용:** 기존 HLS 도구가 지원하지 못하는 세밀한 병렬성(fine-grain parallelism)을 효과적으로 활용.

## 한계점

- 주로 Cilk-P 기반 병렬 프로그래밍 모델에 최적화되어 있어 다른 병렬 프로그래밍 모델과의 호환성 필요.
- FPGA 기반 평가로, 실제 상용 하드웨어와의 성능 차이 존재 가능.

## 관련 개념

- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/gpu.md|GPU]]

## 전체 요약

[[../paper-summaries/2018MICRO-summarize/tapas-generating-parallel-accelerators-from-parallel-programs.md|전체 요약 보기]]