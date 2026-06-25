---
tags: [paper, 2018, 2018HPCA, topic/pim, topic/cache]
venue: "HPCA 2018"
year: 2018
summary_path: "../paper-summaries/2018HPCA-summarize/outerspace-an-outer-product-based-sparse-matrix-multiplication-accelerator.md"
---

# OuterSPACE: An Outer Product based Sparse Matrix Multiplication Accelerator

**Venue:** HPCA 2018
**저자:** Subhankar Pal, Jonathan Beaumont, Dong-Hyeon Park, Aporva Amarnath, Siying Feng, Chaitali Chakrabarti, Hun-Seok Kim, David Blaauw, Trevor Mudge, Ronald Dreslinski (University of Michigan, Arizona State University)

## 개요

희소 행렬 곱셈을 위한 고도로 스케일 가능한, 에너지 효율적인 재구성 가능한 가속기입니다. 외적(outer product) 기반 행렬 곱셈 기법으로 곱셈과 축적을 분리하여 중복 메모리 접근을 제거합니다. Intel MKL 대비 7.9배, cuSPARSE 대비 13.0배, CUSP 대비 14.0배 속도 향상을 달성합니다.

## 방법론

### 외적 기반 행렬 곱셈
- 곱셈과 축적 연산 분리를 통한 중복 메모리 접근 제거
- 기존 알고리즘 대비 메모리 접근 횟수 대폭 감소
- 희소 행렬의 특성 활용한 효율적인 연산

### 하드웨어 구조
- SPMD 스타일 처리 유닛의 대규모 병렬 구조
- 분산 메모리 시스템으로 메모리 대역폭 병목 해결
- 고속 크로스바를 통한 효율적인 데이터 통신
- HBM을 통한 고대역폭 메모리 접근

### 재구성 가능성
- 다양한 희소 행렬 형상에 대응할 수 있는 재구성 가능한 설계
- 애플리케이션별 최적화 가능한 하드웨어 구조
- 유연한 메모리 접근 패턴 지원

## 핵심 기여

1. 희소 행렬 곱셈을 위한 고효율 가속기 제안
2. 외적 기반 기법으로 중복 메모리 접근을 효과적으로 제거
3. 기존 CPU/GPU 솔루션 대비 높은 성능 및 에너지 효율 달성

## 주요 결과

- **처리량**: 24W 전력 예산에서 평균 2.9 GFLOPS
- **속도 향상**: Intel MKL 대비 7.9배, cuSPARSE 대비 13.0배, CUSP 대비 14.0배
- **효율성**: 87mm² 영역에서 구현

## 한계점

- gem5 시뮬레이터를 통한 검증에 한정
- 실제 하드웨어 구현에서의 검증 필요
- 다양한 희소 행렬 형상에서의 일반화 가능성 검증 필요

## 관련 개념

- [[paper-wiki/concepts/pim.md|PIM]]
- [[paper-wiki/concepts/cache.md|Cache]]