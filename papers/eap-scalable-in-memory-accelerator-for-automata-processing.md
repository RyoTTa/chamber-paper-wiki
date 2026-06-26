---
tags: [paper, 2019, 2019MICRO, topic/cache, topic/dram, topic/gpu]
venue: "52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '19)"
year: 2019
summary_path: "../paper-summaries/2019MICRO-summarize/eap-scalable-in-memory-accelerator-for-automata-processing.md"
---

# eAP: A Scalable and Efficient In-Memory Accelerator for Automata Processing

**Venue:** 52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '19)
**저자:** Elaheh Sadredini, Reza Rahimi, Vaibhav Verma, Mircea Stan, Kevin Skadron (University of Virginia)

## 개요

- 패턴 매칭은 네트워크 보안, 데이터 마이닝, 유전학 등 빅데이터 애플리케이션의 핵심 연산으로, 복잡한 비정확 매칭(inexact matching)을 지원해야 함
- 정규 표현식과 유한 오토마타(finite automata)는 복잡한 패턴을 식별하는 주요 방법론이나, CPU/GPU에서는 불규칙한 메모리 접근 패턴으로 인해 예측 및 데이터 포워딩 기술이 비활성화됨
- 기존 인메모리 오토마타 프로세서(AP, Cache Automaton)의 인터커넥트 구조 비효율성:
  - **Micron AP:** 계층적 인터커넥트 설계로 라우팅 병목 현상 발생 → Levenstein 오토마타에서 상태 매칭 리소스의 13%만 활용 가능, 87%는 라우팅 리소스 부족으로 사용 불가
  - **Cache Automaton (CA):** 풀 크로스바(Full-Crossbar, FCB) 사용 → 256개 상태 시 256²=65,536개 스위치 필요, 하드웨어 리소스의 50% 이상이 인터커넥트에 소비
  - 21개 오토마타 벤치마크 분석 결과: FCB 스위치의 평균 활용률은 0.53%에 불과
- AP 칩은 동일 면적의 일반 DRAM 대비 16배 적은 1.5MB만 저장 가능 (상태 매칭 규칙 기준)
- 실제 워크로드는 상태 수가 매우 커서 단일 하드웨어 유닛에 맞지 않아, 여러 번의 재구성과 재처리가 필요 → Significant performance penalties

## 방법론

### 3.1. Reduced-Crossbar (RCB) 인터커넥트

- **설계 동기:** 실제 오토마타 연결 패턴의 고유 특성에서 영감
  - 21개 벤치마크 분석: 17개는 RCB만으로 완전 매핑 가능 (FCB 불필요)
- **RCB 구조:**
  - 각 RCB 블록은 인접 상태 간의 연결만 처리
  - 상태 전이 시 시그널이 RCB를 통해 전파됨
  - FCB 대비 7배 이상 적은 스위치로 동일 연결성 달성
- **전역 스위치 (Global Switches):**
  - RCB 블록 간 및 RCB-FCB 간 연결 지원
  - 대규모 상태 수를 가진 오토마타 지원

### 3.2. 메모리 기술 선택

- **8T SRAM 셀:**
  - 비파괴적 리드 지원
  - 논파파시티브 리드 시 여러 비트셀이 공통 비트라인을 드라이브
  - 기존 Cache Automaton에서 사용
- **2T1D GC-eDRAM (Gain-Cell eDRAM):**
  - 8T 셀 대비 적은 트랜지스터 수 → 낮은 면적 오버헤드
  - 더 높은 상태 밀도 → 더 높은 throughput (재구성 및 재스트리밍 횟수 감소)
  - FinFET 기술에서의 스케일링 가능성 연구됨
- **핵심 요구사항:** wired-OR 기능으로 서브어레이 내 메모리 행에서 논리적 OR 연산 지원

### 3.3. 상태 매칭 및 전이 파이프라인

- **상태 매칭 (State Matching):**
  - 입력 심볼이 디코딩됨
  - 해당 심볼과 일치하는 규칙을 가진 상태들이 메모리 행 읽기를 통해 탐지됨 (match vector 생성)
  - 매칭되는 상태 집합과 현재 활성 상태 벡터(Active State Vector)가 AND 연산됨
- **상태 전이 (State Transition):**
  - 현재 활성 상태 벡터의 잠재적 다음 활성 상태가 결정됨
  - 인터커넥트를 통해 시그널 전파 → 활성 상태 벡터 업데이트
  - eAP는 2-Tier RCB + FCB 하이브리드로 최적화된 파이프라인 구현

### 3.4. Place-and-Route 알고리즘

- AP 컴파일러 대비 1-2 orders of magnitude 빠른 속도
- 오토마타를 RCB/FCB 블록에 효율적으로 배치 및 라우팅
- 오픈소스 사이클 정확한 오토마타 시뮬레이터 제공

## 핵심 기여

- **핵심 기여:** Compact한 Reduced-Crossbar (RCB) 인터커넥트와 고성능 인메모리 오토마타 가속기 eAP 제시
- **성능 향상:** eAP_2T1D는 CA 대비 5.1배, AP 대비 210배 향상된 throughput per unit area (28nm 기준)
- **메모리 기술 선택:** 2T1D GC-eDRAM은 8T SRAM 대비 더 높은 상태 밀도와 낮은 면적 오버헤드로 최적의 성능 제공
- **실용성:** 21개 실제 벤치마크에서 RCB만으로 17개 완전 매핑 가능 → 높은 실용성
- **오픈소스:** 사이클 정확한 오토마타 시뮬레이터 및 자동화된 place-and-route 컴파일러 제공
- **확장성:** 네트워크 보안, 바이오인포매틱스, 머신 런닝 등 다양한 패턴 매칭 애플리케이션에 적용 가능

## 주요 결과

- **하드웨어 구현:**
  - 28nm 기술 노드 기준 평가
  - eAP_2T1D: 2T1D GC-eDRAM 기반
  - eAP_8T: 8T SRAM 기반
- **소프트웨어:**
  - 오픈소스 사이클 정확한 오토마타 시뮬레이터
  - 자동화된 place-and-route 컴파일러
- **시스템 구성:**
  - 메모리 어레이에서 상태 매칭 및 전이를 직접 수행
  - 서브어레이 수준 병렬성으로 다중 오토마타 동시 처리

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]


## 전체 요약

[[../paper-summaries/2019MICRO-summarize/eap-scalable-in-memory-accelerator-for-automata-processing.md|전체 요약 보기]]
