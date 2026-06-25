---
tags: [paper, 2021, 2021HPCA, topic/dram, topic/gpu, topic/pim]
venue: "2021 IEEE International Symposium on High-Performance Computer Architecture (HPCA '21)"
year: 2021
summary_path: "../paper-summaries/2021HPCA-summarize/spacea-sparse-matrix-vector-multiplication-on-processing-in-memory-accelerator.md"
---

# SpaceA: Sparse Matrix-Vector Multiplication on Processing-in-Memory Accelerator

**Venue:** 2021 IEEE International Symposium on High-Performance Computer Architecture (HPCA '21)
**저자:** Xinfeng Xie (UCSB), Zheng Liang (UCSB), Peng Gu (UCSB), Abanti Basak (UCSB), Lei Deng (UCSB), Ling Liang (UCSB), Xing Hu (UCSB), Yuan Xie (UCSB)

## 개요

- 희소 행렬-벡터 곱셈(Sparse Matrix-Vector Multiplication, SpMV)은 과학적 컴퓨팅, 그래프 분석 등 다양한 응용 영역에서 중요한 기본 연산(primitive)으로 활용됨
- SpMV는 본질적으로 **메모리 바운드(memory-bound)** 특성을 가지며, GPU 등 throughput-oriented 아키텍처에서 프로세서-메모리 간 제한된 대역폭에 의해 성능이 제약됨
- 기존 SpMV 최적화 연구의 한계:
  - CPU/GPU 플랫폼에서 메모리 대역폭을 최대한 활용하는 연구가 주를 이루었으나 **대역폭 자체의 한계를 극복할 수 없음**
  - NVIDIA GPU에서 vendor-provided library의 최신 SpMV 구현을 프로파일링한 결과 **DRAM 활용률이 높게 나타남** → 메모리 대역폭이 병목임을 확인
- PIM(Processing-in-Memory) 아키텍처는 3D 적층 기술의 발전으로 메모리에 연산 로직을 통합하여 **초고대역폭 활용**이 가능하지만, SpMV 가속기를 위한 최적화된 설계가 부족

## 방법론

### 3.1. 하드웨어 설계

- **뱅크 수준 연산 로직 통합**: 메모리 뱅크 근처에 PE(Processing Element)를 배치하여 로컬 데이터 접근 시 더 낮은 지연 시간, 더 높은 대역폭, 더 높은 에너지 효율 달성
- **Outstanding Memory Requests 활용**: 비로컬 뱅크에 위치한 데이터에 대한 메모리 접근 지연 시간을 숨기기 위해 메모리 요청 병렬 처리
- **뱅크 수준 CAM 통합**: 입력 벡터의 데이터 재사용을 활용하여 동일한 입력 벡터 요소에 대한 반복적인 메모리 접근 방지
- **3D 적층 메모리 구조**: HMC(Hybrid Memory Cube) 또는 HBM(High Bandwidth Memory) 기반, TSV(Through-Silicon Via)를 통한 레이어 간 통신
- 각 PE는 여러 행(row)의 희소 행렬을 담당하며, non-zero 요소의 수에 따라 워크로드 분배

### 3.2. 매핑 알고리즘(Mapping Algorithm)

- **Phase I: 행 할당(Row Assignment)** - 논리적 PE에 희소 행렬 행 배정
  - NP-hard 문제이지만 heuristic 알고리즘으로 실용적 시간 복잡도 달성
  - 워크로드 균형과 intra-PE 지역성 최적화를 위한 점수(score) 기반 할당
  - 점수 계산 원리:
    - 현재 PE의 non-zero 요소 수가 예산(nnz/P)을 초과하면 페널티 부여
    - 현재 행의 non-zero 요소와 이미 할당된 행들의 non-zero 요소 간 **컬럼 인덱스 중복 비율(ratio)** 계산
    - 중복이 없으면 현재 PE에 할당된 non-zero 요소 수의 역수를 점수로 사용
  - 시간 복잡도: O(P × nnz × log(nnz)) — P: PE 수, nnz: 전체 non-zero 요소 수

- **Phase II: PE 배치(PE Placement)** - 논리적 PE를 물리적 PE에 배치
  - **Bank Group 배치**: 논리적 PE를 뱅크 그룹으로 클러스터링
  - **Vault 배치**: 뱅크 그룹을 볼트로 클러스터링
  - 최적화 목표: 뱅크 그룹 및 볼트 간 **최대 고유 컬럼 인덱스 수 최소화** → 워크로드 균형 및 지역성 동시 달성
  - 수학적 공식화: min_C F(C) = max_{1≤g≤q} |∪_{w=1}^{k} S_{C_{gw}}| (NP-hard, heuristic 해결)

### 3.3. 데이터 흐름 및 연산

- 각 PE는 할당된 행의 non-zero 요소를 순회하면서:
  - 입력 벡터 요소를 CAM에서 검색하여 데이터 재사용 활용
  - 로컬 메모리 뱅크에서 데이터를 빠르게 접근
  - 출력 벡터에 대한 부분 곱셈 연산 수행
  - 부분 합(partial sum)을 볼트 간 통신을 통해 최종 결과에 병합

## 핵심 기여

- SpaceA는 PIM 아키텍처 기반 SpMV 가속기로, 뱅크 수준 연산 로직 통합과 outstanding requests 활용으로 **13.54x speedup** 및 **87.49% 에너지 절약** 달성
- CAM 통합과 최적화된 매핑 알고리즘으로 희소 행렬의 불규칙한 메모리 접근 패턴 문제 효과적으로 해결
- 그래프 분석(PageRank, SSSP)에서도 Tesseract, GraphP 대비 우수한 성능으로 SpMV 기반 응용 가속 가능성 입증
- PIM 아키텍처가 SpMV와 같은 메모리 바운드 워크로드에 효과적인 솔루션임을 입증

## 주요 결과

- **시뮬레이터**: gem5 기반 PIM 시뮬레이션 환경 활용
- **기본 구성**: 16개 큐브(cube), 각 큐브당 16개 볼트, 각 볼트당 16개 뱅크
- **PE 수**: 뱅크당 1개 PE, 총 4096 PE (16×16×16)
- **테스트 매트릭스**: University of Florida Sparse Matrix Collection에서 다양한 희소 행렬 사용
- **비교 Baselines**: NVIDIA GPU (CUDA 기반 SpMV), Tesseract, GraphP

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2021HPCA-summarize/spacea-sparse-matrix-vector-multiplication-on-processing-in-memory-accelerator.md|전체 요약 보기]]
