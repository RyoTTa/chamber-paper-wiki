---
tags: [paper, 2018, 2018MICRO, topic/cache, topic/dram]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/tapas-generating-parallel-accelerators-from-parallel-programs.md"
---

# TAPAS: Generating Parallel Accelerators from Parallel Programs

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Steven Margerm, Amirali Sharifian, Apala Guha, Arrvindh Shriraman (Simon Fraser University), Gilles Pokam (Intel Corporation)

## 개요

- 기존 High-Level Synthesis (HLS) 도구들은 병렬 프로그램에서 하드웨어 가속기를 생성할 때 정적 병렬리즘(static parallelism)만 지원함.
- 현재 HLS 도구들은 고정된 패턴(파이프라인, 데이터 병렬 커널)만 타겟으로 하며, 동적 병렬리즘(dynamic parallelism)을 지원하지 못함.
- 소프트웨어 프로그래머가 병렬성을 표현하는 능력이 제한되어 있으며, 생성된 가속기는 동적 비동기성(asyncrony)과 캐시 미스 숨김(latency hiding)이라는 병렬 하드웨어의 핵심 이점을 잃음.
- 기존 HLS 도구들은 Sequential compiler 기반이며, 병렬 프로그램 의존성 그래프(PDG)를 제대로 분석하지 못함.
- 정적 병렬리즘만 지원하는 템플릿 기반 HLS는 런타임에서 병렬성이 변하는 프로그램에 적합하지 않음.

## 방법론

### 3.1. Tapir 병렬 컴파일러 통합

- Tapir는 LLVM의 확장으로, fork-join 병렬리즘을 IR에 명시적으로 표현.
- TAPAS는 Tapir의 병렬리즘 마커를 활용하여 태스크 의존성을 자동으로 추론.
- 기존 HLS 도구와 달리 별도의 어노테이션이나 라이브러리 호출 없이 병렬 프로그램을 하드웨어로 합성.

### 3.2. 하드웨어 생성 파이프라인

1. **정적 분석 단계:** 병렬 IR을 분석하여 태스크 그래프 구성
   - 태스크 간 의존성 관계 추론
   - 동기화 필요성 결정
   - 메모리 공유 패턴 분석
2. **태스크별 RTL 생성:** 각 태스크에 대해 개별적인 데이터플로우 실행 로직 합성
   - 임의의 제어 흐름(루프 포함) 지원
   - 메모리 연산 지원
   - 공유 리소스 관리

### 3.3. 마이크로아키텍처 구조

- **Tiles:** 각 태스크에 할당된 독립적인 실행 단위
- **Task Queue:** 태스크 생성 및 동기화를 위한 큐
- **Shared RAM/Cache:** 태스크 간 데이터 공유를 위한 메모리
- **AXI Bus:** 외부 DRAM과의 인터페이스
- **Spawn/Sync 하드웨어:** 태스크 생성 및 동기화를 위한 전용 하드웨어 유닛

## 핵심 기여

- TAPAS는 병렬 프로그램에서 동적 병렬리즘을 지원하는 최초의 HLS 도구 중 하나.
- Tapir 병렬 컴파일러 IR을 활용하여 태스크 기반 가속기를 자동 생성.
- Intel Xeon 대비 **20배 전력 효율** while 성능은 유지하는 가속기 생성 가능.
- 동적, 중첩, 재귀적 병렬 패턴을 모두 지원하는 범용 병렬 가속기 합성.
- **의의:** 기존 HLS 도구의 정적 병렬리즘 제한을 극복하고, 소프트웨어 프로그래머가 쉽게 병렬 하드웨어 가속기를 생성할 수 있는 방법을 제시.

## 주요 결과

- **구현 언어:** Chisel (Scala 기반 하드웨어 설명 언어)
- **ompiler 기반:** LLVM/Tapir 컴파일러 프레임워크
- **하드웨어 플랫폼:** Intel-Altera DE1-SoC 및 Arria-10 FPGA 보드
- **오픈소스:** GitHub (https://github.com/sfu-arch/tapas)에서 공개
- **지원 프로그래밍 모델:** Cilk-P 기반 병렬 프로그래밍

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/tapas-generating-parallel-accelerators-from-parallel-programs.md|전체 요약 보기]]
