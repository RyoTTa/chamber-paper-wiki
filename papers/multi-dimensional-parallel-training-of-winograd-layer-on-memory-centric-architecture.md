---
tags: [paper, 2018, 2018MICRO, topic/dram, topic/gpu, topic/near-data-processing, topic/pim, topic/virtual-memory]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/multi-dimensional-parallel-training-of-winograd-layer-on-memory-centric-architecture.md"
---

# Multi-dimensional Parallel Training of Winograd Layer on Memory-Centric Architecture

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Byungchul Hong (FuriosaAI), Yeonju Ro (KAIST), John Kim (KAIST)

## 개요

- CNN 학습 가속을 위한 데이터 병렬(Data Parallelism)은 가중치 그래디언트 통신 오버헤드로 인해 스케일러빌리티가 제한됨
- 고정된 총 배치 크기에서 워커 수가 증가하면 워커당 계산량이 감소하고 통신 비중이 커짐
- 기존 배치 크기 확장 방식은 모델 품질 저하와 수렴 속도 감소를 유발 (large batch size → degraded quality)
- Winograd 변환은 연산량을 줄이지만, 데이터 접근량을 평균 4.4배 증가시킴 (Figure 1 참조)
- 기존 NDP(Near-Data Processing) 아키텍처는 데이터 접근을 효율적으로 처리하지만, 새로운 유형의 통신(tile transfer)을 고려하지 않음

## 방법론

### 3.1. 2차원 워커 조직

- **Group (데이터 병렬성 차원):** 같은 열의 워커들이 동일한 데이터 배치를 공유
- **Cluster (intra-tile 병렬성 차원):** 같은 행의 워커들이 Winograd 도메인 타일의 서로 다른 요소를 처리
- 입력 배치는 클러스터 간 분배, 타일 요소는 그룹 간 분배
- 가중치 그래디언트는 그룹 내에서만 통신 필요 → 워커 수 증가 시 스케일러빌리티 향상

### 3.2. 타일 전송(Tile Transfer)

- MPT에서 새로 발생하는 통신: 클러스터 내에서 Winograd 도메인 피처 맵의 gather/scatter
- 하이브리드 토폴로지 구성:
  - **Ring 토폴로지:** 그룹 간 가중치 통신 (collective communication)
  - **고연결 토폴로지:** 타일 전송용 (flattened butterfly 등)
- 타일 전송 비용 최소화를 위한 예측 기반 비활성화 기법: 공간 도메인 뉴런의 활성화를 예측하여 비활성화된 타일의 통신 제거

### 3.3. 동적 클러스터링(Dynamic Clustering)

- 합성곱 레이어마다 최적의 워커 구성(그룹/클러스터 비율)을 재구성
- 가중치 그래디언트 통신과 타일 전송 간 균형을 위해 사전 추정된 통신량 기반으로 토폴로지 동적 변경
- 합성곱 레이어의 통신 특성에 따라 유연한 리소스 배분

### 3.4. NDP 아키텍처

- 3D 적층 메모리(HMC/HBM)의 고대역폭을 활용하여 Winograd 변환의 추가 데이터 접근 처리
- 메모리 중심 네트워크로 워커 간 고연결성 제공
- Near-Data Processing을 통해 데이터 접근 비용 최소화

## 핵심 기여

- Winograd 변환의 intra-tile 병렬성을 데이터 병렬성과 결합한 MPT는 CNN 학습의 스케일러빌리티 문제를 효과적으로 해결
- 메모리 중심 NDP 아키텍처와 하이브리드 네트워크 토폴로지는 새로운 유형의 통신(tile transfer)을 효율적으로 지원
- 최대 2.7배 학습 가속 달성 (기존 데이터 병렬 NDP 대비)
- 변환 기반 학습의 통신 과제를 해결하는 일반적인 프레임워크를 제시

## 주요 결과

- **시뮬레이션 환경:** CACTI 3DD 기반 메모리 모델링, BookSim 네트워크 시뮬레이터
- **시스템 구성:** 8-64개 워커, 3D 적층 메모리(4GB HMC + DDR4)
- **네트워크 토폴로지:** Ring + Flattened Butterfly 하이브리드
- **워크로드:** VGGNet, ResNet, DenseNet 등 CNN 모델의 합성곱 레이어

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/multi-dimensional-parallel-training-of-winograd-layer-on-memory-centric-architecture.md|전체 요약 보기]]
