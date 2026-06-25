---
tags: [memristive-accelerator, scientific-computing, linear-algebra, sparse-matrix]
venue: ISCA
year: 2018
summary_path: paper-summaries/2018ISCA-summarize/enabling-scientific-computing-on-memristive-accelerators.md
---

# Enabling Scientific Computing on Memristive Accelerators

## 개요

메모리스트 크로스바에서 고정밀 부동소수점 연산을 가능하게 하는 최초의 연구입니다. 세 가지 최적화 기법을 통해 과학 기산 분야에서의 메모리스트 컴퓨팅을 활성화합니다.

## 방법론

- **지수 범위 국소성 활용**: 패딩 비트 수 대폭 감소 (2046비트 → 수백 비트)
- **조기 종료(Early Termination)**: IEEE-754 정밀도 충족 시 연산 중단
- **정적 연산 스케줄링**: 하이브리드 그룹링으로 에너지-지연 트레이드오프 최적화

## 핵심 기여

1. 메모리스트 가속기를 과학 기산 분야에 처음으로 적용
2. 고정점 하드웨어에서 고정밀 부동소수점 연산 지원
3. 이종 크로스바 구조로 희소 행렬 처리 효율성 향상

## 주요 결과

- GPU 대비 실행 시간 10.3배 향상
- GPU 대비 에너지 소비 10.9배 절감
- SuiteSparse 컬렉션의 20개 입력 행렬로 평가

## 한계점

- 메모리스트 기술의 성숙도 및 제조 비용
- ADC 오버헤드 및 칩 면적 제약

## 관련 concept

- [[paper-wiki/concepts/memristive-computing.md|Memristive Computing]]
- [[paper-wiki/concepts/processing-in-memory.md|Processing-in-Memory]]
- [[paper-wiki/concepts/linear-algebra-acceleration.md|Linear Algebra Acceleration]]