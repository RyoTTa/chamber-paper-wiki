---
tags: [paper, 2021, 2021MICRO, topic/storage]
venue: "MICRO 2021 (54th Annual IEEE/ACM International Symposium on Microarchitecture)"
year: 2021
summary_path: "../paper-summaries/2021MICRO-summarize/racer-bit-pipelined-processing-using-resistive-memory.md"
---

# RACER: Bit-Pipelined Processing Using Resistive Memory

**Venue:** MICRO 2021 (54th Annual IEEE/ACM International Symposium on Microarchitecture)
**저자:** Minh S. Q. Truong, Eric Chen, Deanyone Su, Alexander Glass, Liting Shen, L. Richard Carley, James A. Bain (Carnegie Mellon University), Saugata Ghose (University of Illinois Urbana-Champaign)

## 개요

- 현대 데이터 집약적 애플리케이션(graph processing, genome sequencing, video processing, machine learning)은 CPU와 메모리 간 대규모 데이터 이동이 필요
- 데이터 이동은 데이터 처리 대비 **최대 100배 더 많은 에너지**를 소비하며, 여러 애플리케이션의 에너지 소비 대부분을 차지
- 기존 캐시 기반 접근법은 Locality가 부족한 워크로드에서 효과가 제한적
- Processing-Using-Memory(PUM)은 메모리 셀에서 in-situ 연산을 수행하여 데이터 이동을 줄이지만, 다음과 같은 실용적 제약이 존재:
  - Resistive crossbar array의 **wire current carrying capacity** 제한으로 배열 크기 제한 (n ≤ 128)
  - 작은 배열에서 **peripheral circuitry**가 셀 배열 면적보다 커져 area efficiency 저하
  - 기존 bit-serial PUM 아키텍처는 long latency로 인해 높은 성능 달성 어려움

## 방법론

### 3.1. 버퍼를 이용한 타일 간 통신

- Figure 2a: 각 타일 사이에 1x64 ReRAM 셀 버퍼 배치
- 버퍼는 양쪽 이웃 타일에 pass gate로 연결되지만, **동시에 하나의 이웃만 연결** 가능
  - 최대 융합 crossbar 크기: 65x64 (wire current 제한 준수)
- Figure 2b: 타일 간 데이터 전송 시 전체 버퍼로 병렬 복사 가능

### 3.2. Bit-Pipelining 실행 모델

- **비트 스트라이핑**: w-bit 워드의 비트를 w개 타일에 분산 저장
  - Figure 2a: 동일 워드의 비트들이 모든 타일의 동일 좌표에 위치
- **마이크로-op 재사용**: 
  - 각 타일의 bit-serial 연산은 동일한 마이크로-op 시퀀스를 반복
  - 제어 회로는 단일 타일용 마이크로-op 시퀀스를 생성하고, 이를 타일 간에 전파
- **파이프라이닝 동작**:
  - Tile t가 현재 마이크로-op 시퀀스를 완료하면 인접 타일로 전달
  - Tile t는 새로운 시퀀스를 처리하는 동안 Tile t-1이 전달된 시퀀스를 실행
  - 각 비트 위치에서 파이프라이닝 실행 가능

### 3.3. 제어 회로 (Figure 3)

- **Byte group**: 8개 타일로 구성된 기본 제어 단위
  - 마이크로-op 큐 (Circular FIFO): 각 타일당 1개
  - Broadcast bus: 타일 간 마이크로-op 전파
  - Direction reversal switch: MSB→LSB 또는 LSB→MSB 방향 전환 가능
- **마이크로-op 큐**: 32-entry 길이로 충분한 시퀀스 저장
- **Byte group 간 연결**: 동적으로 연결하여 16/32/64비트 연산 지원

### 3.4. 읽기/쓰기 회로 (Figure 4)

- **읽기 회로**: 전압 분배기 + 비대칭 인버터로 셀 상태 감지
  - 버퍼에서만 읽기 수행 (타일 직접 읽기 시 다른 셀 간섭 문제)
  - 각 셀에 독립적 읽기 회로 연결
- **쓰기 회로**: Write driver로 저항 상태 변경
  - 버퍼에만 쓰기 수행
  - 2 사이클: (1) 전체 0으로 프리셋, (2) 활성화된 셀에 논리 1 기록

### 3.5. 클러스터 스케일링 (Figure 5)

- **64 파이프라인 공유**: 단일 제어 회로와 디코더를 64 파이프라인이 공유
  - 파이프라인 선택기로 활성 파이프라인 선택
  - 열 밀도: 0.02 W/mm2 (일반적인 냉각 한도 내)
- **I/O 멀티플렉싱**: 64비트 버스로 64 버퍼를 멀티플렉싱
  - 매 사이클당 64버퍼에서 각 1비트씩 읽기 → 64비트 워드 전체 읽기
  - 클러스터당 단일 버스 사용

## 핵심 기여

- **핵심 기여**: 
  - 소형 ReRAM 타일에서도 높은 성능을 달성하는 bit-pipelining 실행 모델 제안
  - 실용적 wire current 제한을 준수하면서 107x 성능 향상 달성
  - 라이트웨이트 ISA와 데이터 공유 네트워크로 프로그래밍 가능성 확보
- **성능**: 16코어 CPU 대비 107x, GPU 대비 12x, in-SRAM PUM 대비 7x
- **에너지**: CPU 대비 189x, GPU 대비 17x 에너지 절약
- **의의**: 
  - Resistive memory 기반 PUM의 실용성을 입증
  - 데이터 집약적 애플리케이션의 에너지/성능 병목 해결
  - 향후 ReRAM 기술 발전에 따른 스케일링 가능성 제시

## 주요 결과

### 4.1. ISA (Table 2)

| 연산 유형 | 명령어 | 설명 |
|-----------|--------|------|
| **산술** | ADD, SUB, MUL†, MAC†, DIV† | 2의 보수 덧셈/뺄셈, 곱셈†, 곱셈-누적†, 나눗셈† |
| **비트 연산** | NOR, NAND, NOT, OR, AND, XOR | 비트단위 논리 연산 |
| **시프트** | LSHIFT, RSHIFT | 좌/우 1비트 시프트 |
| **특수 함수** | POPC, CMPEQ, RELU, FUZZY, MAX, MIN | 집합 개수, 비교, ReLU, 퍼지 검색 |
| **CORDIC** | SQRT, SIN, COS, EXP | CORDIC 기반 수학 함수 |
| **데이터 전송** | MOV, SHIFT | 코어 간 데이터 이동 |

†: 비트-파이프라이닝 모드가 아닌 연산

### 4.2. 데이터 공유 네트워크

- 각 코어는 32KB 로컬 데이터에 저지연 접근 가능
- I/O 컨트롤러로 인접 4개 클러스터 연결 (총 9클러스터 로컬 접근, 18MB)
- 메쉬 네트워크로 비지역 클러스터 간 통신
- 512비트 칩 전체 공유 버스로 CPU 통신 (피크 대역폭: 32 GB/s)
- **NUMA 인터페이스**: 로컬 메모리/글로벌 메모리 두 티어로 프로그래밍

### 4.3. 비-파이프라이닝 연산 지원

- **Wallace-Tree 곱셈**: 3단계 (부분 곱 생성 → Wallace tree 감소 → 최종 RCA)
- **CORDIC 함수**: 반복적 비트 연산으로 sin/cos/sqrt 등 구현 (12 반복)
- **정수 나눗셈**: MUX, RSHIFT, SUB 시퀀스로 구현
- 모든 비-파이프라이닝 연산이 RACER의 시프트 능력 활용

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2021MICRO-summarize/racer-bit-pipelined-processing-using-resistive-memory.md|전체 요약 보기]]
