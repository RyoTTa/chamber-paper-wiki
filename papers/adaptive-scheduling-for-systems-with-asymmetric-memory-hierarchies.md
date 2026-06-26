---
tags: [paper, 2018, 2018MICRO, topic/cache, topic/near-data-processing, topic/pim]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/adaptive-scheduling-for-systems-with-asymmetric-memory-hierarchies.md"
---

# Adaptive Scheduling for Systems with Asymmetric Memory Hierarchies

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Po-An Tsai, Changping Chen, Daniel Sanchez (Massachusetts Institute of Technology)

## 개요

- 데이터 이동이 컴퓨터 시스템의 주요 병목 현상으로, 오프칩 메모리 접근은 더블 프리시전 곱셈-덧셈 대비 **1000배 많은 에너지**를 소비하고 **100배 더 느린 레이턴시**를 가짐
- 기존 시스템은 깊은 캐시 계층(deep cache hierarchy)에 의존하지만, 워킹 세트가 LLC에 맞지 않으면 캐시는 지연 시간과 에너지만 추가하고 이점을 제공하지 못함
- Die-stacking 기술의 발전으로 메모리 스택 근처에 코어를 배치하는 NDP(Near-Data Processing) 시스템이 등장했으나, NDP 코어는 면적/전력 제약으로 인해 얕은 캐시 계층(shallow hierarchy)을 사용
- **비대칭 메모리 계층(asymmetric memory hierarchy)** 시스템이 제안됨 (깊은 계층 + 얕은 계층을 하나의 시스템에서 결합): 구글도 소비자 워크로드를 위해 이러한 시스템을 제안
- 문제: 스레드를 올바른 계층에 스케줄링해야 하며, 동일 애플리케이션이 입력에 따라 다른 계층을 선호하고, 공존하는 애플리케이션이 리소스 경쟁을 일으켜 선호도가 동적으로 변함
- 올바른 계층 매핑은 성능당 전력(performance per Joule)을 최대 **2.8배**, 평균 **40%** 향상시킬 수 있음

## 방법론

### 3.1. 지연 시간 곡선(Latency Curve) 모델링

- 프로세서 다이 코어에서의 지연 시간: `Lproc(s) = A · LatLLC + M(s) · Latmem,proc`
  - `A`: 프라이빗 캐시 레벨 이후의 LLC 접근 수
  - `M(s)`: 용량 `s`에서의 LLC 미스 수 (미스 곡선)
  - `LatLLC`: LLC 접근 평균 레이턴시
  - `Latmem,proc`: 오프칩 메모리 접근 평균 레이턴시
- NDP 코어에서의 지연 시간: `LNDP = A × Latmem,NDP`
  - NDP 코어는 LLC를 사용하지 않으므로 지연 시간 곡선이 상수
  - `Latmem,NDP`: 메모리 스택의 비균일 메모리 접근(NUMA)에 따라 달라짐

### 3.2. AMS-Greedy 알고리즘

- **1단계:** 항상 NDP를 선호하는 스레드를 식별하여 NDP 코어 그룹으로 이동
  - 조건: 모든 LLC 용량에서 `Cproc_i(s) > Cbest_NDP_i`인 스레드
- **2단계:** Peekahead 알고리즘(선형 시간 UCP Lookahead의 구현)을 사용하여 LLC를 파티셔닝
  - 각 스레드에 대해 최적의 파티션 크기를 찾아 총 비용(`ΣCproc_i(si)`) 최소화
- **3단계:** 기회 비용(opportunity cost)이 낮은 스레드를 NDP 코어로 이동
  - 기회 비용이 가장 낮은 스레드부터 순서대로 배치
- **공유 데이터 처리:** 같은 프로세스의 스레드들을 하나의 단위로 묶어 공유 인텐시브한 데이터를 처리

### 3.3. AMS-DP: 동적 프로그래밍 기반 최적화

- **동적 프로그래밍(DP)**을 활용하여 글로벌 최적 해를 탐색
  - 캐시 파티셔닝 문제와의 유사성을 활용: 이산적 결정이 캐시 세그먼트 크기 단위로 수행
  - 모든 가능한 선택지를 효율적으로 탐색 (메모이제이션 활용)
- AMS-Greedy는 로컬 최적 결정을 수행하지만 글로벌 최적에서 벗어날 수 있음
- AMS-DP는 모든 선택지를 고려하여 글로벌 최적 해를 보장하지만, 더 높은 오버헤드를 가짐

### 3.4. 데이터 배치(Data Placement)

- NDP 코어는 로컬 메모리 스택에 접근할 때 가장 효율적
- NUMA 시스템과의 차이: NDP 시스템은 인트라스택 대역폭이 풍부하지만 인터스택 대역폭이 제한적
- **비대칭 계층 인식 데이터 배치:** 페이지를 가능한 적은 스택에 유지하여 NDP 코어의 로컬 접근 최대화
- 페이지 마이그레이션 없이 간단한 휴리스틱으로 데이터 로컬리티 유지

## 핵심 기여

- **핵심 기여:** 비대칭 메모리 계층 시스템을 위한 최초의 적응형 스케줄러 AMS 제시
- **성능:** 비대칭 무시 스케줄러 대비 최대 **37%**, 평균 **18%** 향상
- **핵심 기법:** 캐시 파티셔닝 알고리즘을 스케줄링 문제에 창의적으로 적용하여 미스 곡선 기반 성능 모델링 구현
- **실용성:** 온라인 사용이 가능한 저렴한 오버헤드로 프로그램 단계에 적응
- **의의:** NDP 시스템의 실용화를 위한 스케줄링 문제를 해결하여, 비대칭 메모리 계층의 잠재적 이점을 실현
- **확장성:** 다양한 워크로드 (단일/멀티스레드, 캐시 친화적/스트리밍)에서 일관된 성능 향상 달성

## 주요 결과

- **시뮬레이션 환경:** gem5 기반 cycle-accurate 시뮬레이션
- **데이터 배치:** CRUISE의 휴리스틱 활용 (UMONs를 통해 필요한 정보 수집)
- **마이그레이션 오버헤드:** 50ms마다 재매핑 시 무시할 수 있는 오버헤드 (PIE 연구와 유사)
- **프라이빗 캐시:** 스케줄러와 동일 ( NDP와 프로세서 다이 코어 모두 동일한 프라이빗 캐시 사용)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/adaptive-scheduling-for-systems-with-asymmetric-memory-hierarchies.md|전체 요약 보기]]
