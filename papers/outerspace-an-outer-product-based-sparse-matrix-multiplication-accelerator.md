---
tags: [paper, 2018, 2018HPCA, topic/dram, topic/gpu]
venue: "HPCA 2018 (IEEE International Symposium on High-Performance Computer Architecture)"
year: 2018
summary_path: "../paper-summaries/2018HPCA-summarize/outerspace-an-outer-product-based-sparse-matrix-multiplication-accelerator.md"
---

# OuterSPACE: An Outer Product based Sparse Matrix Multiplication Accelerator

**Venue:** HPCA 2018 (IEEE International Symposium on High-Performance Computer Architecture)
**저자:** Subhankar Pal, Jonathan Beaumont, Dong-Hyeon Park, Aporva Amarnath, Siying Feng, Chaitali Chakrabarti, Hun-Seok Kim, David Blaauw, Trevor Mudge, Ronald Dreslinski (University of Michigan, Arizona State University)

## 개요

- 희소 행렬은 그래프/데이터 분석, 머신 러닝, 공학/과학 애플리케이션에서 광범위하게 사용
- SpGEMM(일반화된 희소 행렬-행렬 곱셈)과 SpMV(희소 행렬-벡터 곱셈)은 복잡한 연산의 핵심 커널
- 기존 희소 행렬 곱셈 알고리즘에서 비영(non-zero) 요소에 대한 중복 메모리 접근이 주요 병목
- 기존 아키텍처는 메모리 계층 구조와 병렬성 활용 능력의 한계로 중복 접근 제거에 어려움
- Facebook 그래프 예시: 10.8억 정점, 밀도 0.0003%의 인접 행렬

## 방법론

### 3.1. 외적 기반 행렬 곱셈

- 곱셈과 축적 연산 분리를 통한 중복 메모리 접근 제거
- 기존 알고리즘 대비 메모리 접근 횟수 대폭 감소
- 희소 행렬의 특성 활용한 효율적인 연산

### 3.2. 하드웨어 구조

- SPMD 스타일 처리 유닛의 대규모 병렬 구조
- 분산 메모리 시스템으로 메모리 대역폭 병목 해결
- 고속 크로스바를 통한 효율적인 데이터 통신
- HBM을 통한 고대역폭 메모리 접근

### 3.3. 재구성 가능성

- 다양한 희소 행렬 형상에 대응할 수 있는 재구성 가능한 설계
- 애플리케이션별 최적화 가능한 하드웨어 구조
- 유연한 메모리 접근 패턴 지원

## 핵심 기여

- OuterSPACE는 희소 행렬 곱셈을 위한 고효율 가속기를 제안
- 외적 기반 기법으로 중복 메모리 접근을 효과적으로 제거
- 기존 CPU/GPU 솔루션 대비 높은 성능 및 에너지 효율 달성
- 희소 행렬 기반 애플리케이션의 가속을 위한 유망한 접근법

---

## 참고 자료

- 논문 원문: `/home/ryotta205/Chamber_paper/paper-source/2018HPCA/OuterSPACE_An_Outer_Product_Based_Sparse_Matrix_Multiplication_Accelerator.pdf`
- 관련 개념: Sparse Matrix, Accelerator, Parallel Processing, HBM, Outer Product

## 주요 결과

- gem5 시뮬레이터를 통한 핵심 구성 요소 구현
- University of Florida SuiteSparse 컬렉션 및 Stanford Network Analysis Project의 다양한 행렬 테스트
- 24W 전력 예산, 87mm² 영역에서 구현

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]


## 전체 요약

[[../paper-summaries/2018HPCA-summarize/outerspace-an-outer-product-based-sparse-matrix-multiplication-accelerator.md|전체 요약 보기]]
