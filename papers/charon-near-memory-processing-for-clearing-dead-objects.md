---
tags: [paper, 2019, 2019MICRO, topic/dram, topic/near-data-processing, topic/virtual-memory]
venue: "52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO-52), 2019"
year: 2019
summary_path: "../paper-summaries/2019MICRO-summarize/charon-specialized-near-memory-processing-architecture-for-clearing-dead-objects-in-memory.md"
---

# Charon: Specialized Near-Memory Processing Architecture for Clearing Dead Objects in Memory

**Venue:** 52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO-52), 2019
**저자:** Jaeyoung Jang (Sungkyunkwan University), Jun Heo (Seoul National University), Yejin Lee (Seoul National University), Jaeyeon Won (Seoul National University), Seonghak Kim (Seoul National University), Sung Jun Jung (Seoul National University), Hakbeom Jang (Sungkyunkwan University), Tae Jun Ham (Seoul National University), Jae W. Lee (Seoul National University)

## 개요

- Garbage Collection(GC)는 Java, C#, JavaScript, Python 등 주요 프로그래밍 언어에서 사용되는 자동 메모리 관리 기법으로, 프로그래머의 생산성을 크게 향상시킨다. 그러나 GC는 **응용 처리량(throughput), 최악 레이턴시, 에너지 소비 측면에서 상당한 성능/전력 비용을 수반**한다.
- 빅 데이터 분석 워크로드에서 GC는 전체 실행 시간의 **최대 50%**를 차지하며, 대규모 객체를 다루는 메모리 집약적 애플리케이션에서 특히 심각한 문제로 부상한다. GC로 인한 **테일 레이턴시(tail-latency)** 증가는 클라우드 환경에서 QoS(Quality of Service) 저하와 관리 비용 상승으로 직결된다.
- 기존 하드웨어 GC 가속 기법들은 △특정 언어(Lisp, Smalltalk) △특정 하드웨어(FPGA, specialized memory) △특정 알고리즘(reference counting) 등에 국한되어 **광범위한 적용 범위가 부족**했으며, 전체 GC를 하드웨어에 구현한 접근법들은 유연성(flexibility)이 떨어지고 프로세서 변경에 대한 높은 비용이 요구되었다.
- 현대 범용 프로세서(Intel Xeon)에서 GC 워크로드의 **평균 IPC가 0.5 이하**로, 범용 프로세서가 GC에 매우 비효율적임이 확인되었다. 메모리 병렬도(MLP, Memory-Level Parallelism)와 오프칩 메모리 대역폭이 제한되어 GC의 그래프 순회 및 객체 복사 작업을 효율적으로 수행하기 어렵다.
- 메모리 기술 스케일링 둔화와 데이터셋 크기/컴퓨팅 병렬도의 급격한 증가로 GC 오버헤드는 향후 **지속적으로 증가**할 것으로 예상된다.

## 방법론

### 3.1. GC 동작 분석 및 핵심 프리미티브 식별

- **HotSpot JVM의 ParallelScavenge GC**를 분석 대상으로 선정 (현존 가장 널리 사용되는 프로덕션 JVM)
- ParallelScavenge GC의 4단계 동작:
  - ❶ **Traverse(순회):** root set에서 시작하여 live object 그래프를 순회
  - ❷ **Copying(복사):** live object를 Eden → Survivor space로 복사
  - ❸ **Promotion(승격):** 일정 기간 생존한 객체를 Old generation으로 승격
  - ❹ **Compaction(압축):** Old generation 내 객체를 연속 메모리 영역으로 재배치
- 분석 결과, **소수의 간단한 프리미티브가 GC 전체 시간의 대부분을 차지**:
  - **Pointer traversal (포인터 순회):** live object 그래프 탐색
  - **Object copying (객체 복사):** semispace 간 데이터 이동
  - **Bitmap operations (비트맵 연산):** live/dead object 표시용 비트맵 조작
  - **Address translation (주소 변환):** 논리적 → 물리적 주소 매핑

### 3.2. 특화된 프로세싱 유닛 설계

- **Charon Processing Unit:** 3D 적층 DRAM의 로직 레이어에 탑재되는 전용 가속기
- ** 메모리 병렬도 극대화:**
  - 넓은 명령 윈도우(load/store queue)를 통해 대규모 병렬 메모리 접근 가능
  - 범용 프로세서의 제한된 MLP를 극복하여 GC 연산의 메모리 대역폭 활용도 극대화
- **프리미티브 구현:**
  - **Bitmap-based live/dead marking:** 비트 단위 병렬 연산으로 live object 식별
  - **Bulk copy engine:** 대규모 객체 복사를 위한 DMA 기반 복사 엔진
  - **Pointer chasing unit:** 객체 그래프 순회를 위한 포인터 추적 전용 유닛
- **메모리 대역폭 활용:** 3D 적층 메모리의 로직 레이어에서 직접 접근 가능한 풍부한 대역폭 활용으로 GC의 메모리 병목 문제 해결

### 3.3. 프로세서-가속기 통합

- **최소 프로세서 변경:** Charon 가속기는 기존 프로세서에 최소한의 인터페이스 변경으로 통합
- **GC 오프로딩 메커니즘:**
  - JVM이 GC의 핵심 프리미티브를 식별하면 Charon 가속기로 오프로딩
  - 가속기가 프로세서의 메모리 주소 공간에 직접 접근하여 GC 연산 수행
- **동작 흐름:**
  1. MinorGC/MajorGC 트리거 시 JVM이 Charon에 GC 프리미티브 오프로딩 요청
  2. Charon이 3D 적층 메모리의 풍부한 대역폭을 활용하여 병렬 GC 수행
  3. 완료 후 프로세서에 통지

## 핵심 기여

- Charon은 **최초의 3D 적층 메모리 기반 GC 가속기**로, GC의 핵심 프리미티브를 근근접 메모리 처리로 오프로딩하는 새로운 접근법을 제시
- **핵심 기여:**
  1. HotSpot JVM 기반 빅 데이터 워크로드의 GC 동작에 대한 상세한 분석
  2. GC의 핵심 알고리즘 프리미티브 식별 및 해당 연산의 MLP/처리량을 극대화하는 특화 하드웨어 설계
  3. 프로덕션 JVM에서의 프로토타입 구현 및 검증
  4. 770B+ 명령어 규모의 cycle-level 시뮬레이션을 통한 정밀 평가
- **성능:** 베이스라인 대비 **3.29× GC 속도 향상, 60.7% 에너지 절감**
- **의의:** 수십 년간 지속되어 온 GC 가속 문제를 3D 적층 메모리 기술과 특화 아키텍처의 결합으로 해결. 향후 GC 알고리즘의 진화에도 적용 가능한 미래 지향적 설계

## 주요 결과

- **구현 환경:** Full-production HotSpot JVM 기반 프로토타입
- **시뮬레이터:** 상세한 cycle-level 시뮬레이터 사용
  - **770 billion 이상의 명령어**를 regions of interest에서 실행하여 정확한 성능 평가
- **평가 워크로드:** Apache Spark, GraphChi 두 가지 대규모 데이터 분석 프레임워크
- **하드웨어 구성:** 8코어 out-of-order 프로세서(기존 베이스라인) + Charon 3D 적층 메모리 가속기

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2019MICRO-summarize/charon-specialized-near-memory-processing-architecture-for-clearing-dead-objects-in-memory.md|전체 요약 보기]]
