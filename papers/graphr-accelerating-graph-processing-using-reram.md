---
tags: [pim, near-data-processing, reram, graph-processing, analog-computing]
venue: HPCA
year: 2018
summary_path: paper-summaries/2018HPCA-summarize/graphr-accelerating-graph-processing-using-reram.md
---

# GraphR: Accelerating Graph Processing Using ReRAM

## 개요

GraphR는 ReRAM의 아날로그 연산을 활용한 최초의 그래프 처리 가속기입니다. 그래프 알고리즘의 정점 프로그램이 SpMV로 표현 가능하다는 점에 착안하여, ReRAM 크로스바에서 대규모 병렬 아날로그 SpMV를 수행합니다.

## 방법론

- **ReRAM 크로스바 SpMV**: 인접 행렬을 ReRAM에 저장하고, 정점 값을 벡터로 입력하여 아날로그 전류 합산으로 곱셈-누적 연산 수행
- **Graph Engine (GE)**: ReRAM 크로스바 + ADC + 디지털 로직으로 구성된 그래프 전용 가속기
- **서브그래프 처리**: 큰 그래프를 작은 서브블록으로 분할하여 GE에서 병렬 처리
- **HMC 연동**: 고대역폭 Hybrid Memory Cube와 연결하여 데이터 이동 최소화

## 핵심 기여

1. ReRAM의 아날로그 연산을 그래프 처리에 활용하는 최초의 시도
2. SpMV를 ReRAM 크로스바에서 효율적으로 수행하는 아키텍처
3. 아날로그 연산의 오차가 그래프 알고리즘에 미치는 영향이 최소함을 입증

## 주요 결과

- CPU 대비: 평균 16.01× speedup (최대 132.67×), 33.82× energy saving
- GPU 대비: 1.69~2.19× speedup, 4.77~8.91× energy 절약
- PIM 가속기 대비: 1.16~4.12× speedup, 3.67~10.96× energy 효율
- GE 수 증가에 비례한 성능 스케일링

## 한계점

- ReRAM 기술의 성숙도에 따라 실용성 달라짐
- 아날로그 연산의 오차가 정밀한 그래프 알고리즘에 영향 가능
- GE의 하드웨어 면적 및 전력 소비

## 관련 concept

- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
