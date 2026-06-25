---
tags: [ndp, asymmetric-hierarchy, scheduling, cache-partitioning, near-data-processing]
venue: MICRO
year: 2018
summary_path: paper-summaries/2018MICRO-summarize/adaptive-scheduling-for-systems-with-asymmetric-memory-hierarchies.md
---

# Adaptive Scheduling for Systems with Asymmetric Memory Hierarchies (AMS)

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Po-An Tsai, Changping Chen, Daniel Sanchez (Massachusetts Institute of Technology)

---

## 개요

비대칭 메모리 계층(asymmetric memory hierarchy) 시스템에서 스레드를 올바른 계층에 스케줄링하는 문제를 해결하는 적응형 스케줄러 AMS를 제안. 깊은 캐시 계층(프로세서 다이)과 얕은 캐시 계층(NDP 코어)을 하나의 시스템에서 결합한 환경에서, 캐시 파티셔닝 알고리즘을 스케줄링 문제에 처음 적용하여 미스 곡선 기반 성능 모델링을 구현.

## 방법론

- **미스 곡선(Miss Curve) 기반 모델링:** 스레드의 다양한 캐시 크기에서의 LLC 미스 수를 샘플링하여 각 계층에서의 성능을 예측
- **AMS-Greedy:** 항상 NDP를 선호하는 스레드 식별 → LLC를 Peekahead 알고리즘으로 파티셔닝 → 기회 비용이 낮은 스레드를 NDP로 이동
- **AMS-DP:** 동적 프로그래밍으로 글로벌 최적 해 탐색 (캐시 파티셔닝 문제와의 유사성 활용)
- **비대칭 계층 인식 데이터 배치:** NDP 코어의 로컬 접근을 위한 휴리스틱 기반 페이지 배치

## 핵심 기여

- 비대칭 메모리 계층 시스템을 위한 최초의 적응형 스케줄러
- 캐시 파티셔닝 기법을 스케줄링 문제에 창의적으로 적용
- 온라인 사용이 가능한 저렴한 오버헤드로 프로그램 단계에 적응

## 주요 결과

- 비대칭 무시 스케줄러 대비 최대 **37%**, 평균 **18%** 성능 향상
- 전면 탐색 스케줄러 대비 **1% 이내** 성능 달성
- 멀티스레드 애플리케이션에서 기하평균 **22%** 향상
- 인터스택 트래픽을 All NDP 대비 **3.1배** 감소

## 한계점

- NDP 코어의 수와 메모리 스택 구조에 대한 가정이 필요
- 공유 읽기-쓰기 데이터가 지배적인 워크로드에서 NDP 코어의 이점이 제한
- 프로세서 다이와 NDP 코어 간 캐시 일관성 처리 오버헤드 미고려

## 관련 개념

- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/cache.md|Cache]]

## 전체 요약

[adaptive-scheduling-for-systems-with-asymmetric-memory-hierarchies.md](../../paper-summaries/2018MICRO-summarize/adaptive-scheduling-for-systems-with-asymmetric-memory-hierarchies.md)
