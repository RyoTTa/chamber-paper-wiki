---
tags: [paper, 2018, 2018ISCA, topic/cache]
venue: "ISCA 2018"
year: 2018
summary_path: "../paper-summaries/2018ISCA-summarize/criticality-aware-tiered-cache-hierarchy-a-fundamental-relook-at-multi-level-cache-hierarchies.md"
---

# Criticality Aware Tiered Cache Hierarchy: A Fundamental Relook at Multi-level Cache Hierarchies

**Venue:** ISCA 2018
**저자:** Anant Vithal Nori, Jayesh Gaur, Siddharth Rai, Sreenivas Subramoney, Hong Wang (Intel MRL, IIT Kanpur)

## 개요

현대 프로세서의 3레벨 캐시 계층에서 L2 캐시를 크게 만드는 트렌드는 실제로 비효율적이다. 프로그램 성능에 영향을 미치는 것은 critical load뿐이며, 모든 로드의 평균 히트 지연 시간을 최적화하는 것은 하위 최적이다.

CATCH는 하드웨어 기반 criticality 감지와 TACT 프리패처를 통해 critical load를 L1 지연 시간으로 서비스한다. L2를 제거하더라도 4.5% 성능 향상 + 30% 면적 절감을 달성하며, 8.4~10.3% IPC 향상을 보인다.

## 방법론

### Criticality 감지
- 데이터 의존성 그래프의 최적화된 하드웨어 표현으로 3KB 면적에 critical path 학습
- 점진적 학습으로 런타임에 동적 critical load 식별

### TACT 프리패처
- LLC/L2에서 L1로 critical load 데이터 프리패칭
- 주소/데이터 기반 프리패칭 + 코드 런어헤드 프리패처
- Critical load가 실제로 발행되기 직전에 L1에 데이터 준비

### CATCH 기반 구성
- L2 완전 제거 가능 → 절감 면적을 LLC 용량 증가 또는 코어 수 증가에 활용
- 칩 전체 면적, 성능, 전력 간 유연한 트레이드오프 탐색

## 핵심 기여

1. 프로그램 criticality를 활용한 캐시 계층 설계의 근본적 재검토
2. 3KB 하드웨어로 critical path 학습 가능
3. L2 제거로 30% 면적 절감 + 성능 향상 동시 달성

## 주요 결과

- **CATCH vs 3레벨 계층** (1MB L2): ST 8.4%, MP 8.9% IPC 향상
- **CATCH vs 3레벨 계층** (256KB L2): ST 10.3% IPC 향상
- **L2 완전 제거**: 4.5% IPC 향상 + 30% 면적 절감
- **면적 활용**: LLC 용량 증가 시 7.25% IPC 향상 + 11% 에너지 절감

## 한계점

- Criticality 감지 정확도에 대한 민감도 분석 부족
- 멀티스레드 환경에서의 criticality 변화 고려 미흡

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
