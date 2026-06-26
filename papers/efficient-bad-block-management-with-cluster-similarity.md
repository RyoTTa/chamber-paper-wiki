---
tags: [paper, 2022, 2022HPCA, topic/storage]
venue: "IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2022"
year: 2022
summary_path: "../paper-summaries/2022HPCA-summarize/efficient-bad-block-management-with-cluster-similarity.md"
---

# Efficient Bad Block Management with Cluster Similarity

**Venue:** IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2022
**저자:** Jui-Nan Yen, Yao-Ching Hsieh, Cheng-Yu Chen (National Taiwan University), Tseng-Yi Chen (National Central University), Chia-Lin Yang (National Taiwan University), Hsiang-Yun Cheng (Academia Sinica), Yixin Luo (Carnegie Mellon University)

## 개요

- **3D NAND Flash의 공정 변이 문제**: 3D flash 아키텍처에서 process variation으로 인해 동일 칩 내 여러 블록이 서로 다른 읽기/쓰기 지연 시간과 RBER(Raw Bit Error Rate) 특성을 보임
- **Bad Block Management의 본질적 도전**: SSD 수명(lifetime)과 신뢰성(reliability) 간 트레이드오프
  - P/E cycle 임계값을 낮추면 신뢰성 ↑ but 수명 ↓
  - P/E cycle 임계값을 높이면 수명 ↑ but 신뢰성 ↓
- **기존 P/E cycle 기반 관리 정책의 한계**:
  - 고정된 cycle 임계값 설정이 어려움 → 모든 블록의 신뢰성 특성이 동일하다는 가정
  - 데이터 손실 가능성 증가 및 SSD 수명 단축
  - 블록 하나가 실패하면 해당 블록만 폐기 → 인접 블록의 임박한 실패 무시
- **핵심 통찰**: 물리적으로 인접한 flash 블록들이 유사한 오류 특성을 보이는 **cluster similarity** 현상 발견

## 방법론

### 3.1. Cluster Similarity 특성

- **실험 플랫폼**: Hynix 3D TLC NAND flash 메모리 칩 사용
- **관찰**: 물리적으로 인접한 블록들이 유사한 RBER 특성 공유
  - 동일 layer의 인접 wordline 간 유사성 (wordline similarity)
  - 인접 레이어 간 유사성
- **Divergence Indicator Dpage(X,k)**: 클USTER 유사성을 정량화하는 메트릭
  - Dpage(X,k) < 1.4일 때 강한 유사성 존재
  - 클러스터 크기 k가 증가함에 따라 유사성 약화 경향
- **핵심 발견**: 물리적 근접성이 클USTER 유사성의 핵심 — 동일 칩 내 블록들이 높은 유사성 공유

### 3.2. 클러스터 크기 선택

- **공식 도출**:
  - 실패율 ≤ overprovisioning rate / cluster size
  - Reference cluster size = overprovisioning rate / 허용 실패율
- **예시**: 10% overprovisioning, 허용 실패율 0.01 → reference cluster size = 10
- **실용적 가이드라인**: 클러스터 크기 10이면 Dpage < 1.4 조건을 충족하면서 수명-신뢰성 트레이드오프 최적화
- **과도한 클러스터 폐기 방지**: 클러스터가 너무 크면 불필요한 블록 폐기로 수명 단축

### 3.3. Critical-Block First Scheduling

- **문제점**: 클러스터 전체 폐기 시 유효 데이터 실시간 이동 → burst read/write로 인한 I/O 지연
- **기존 접근 (ClusterReAlloc)**: 클러스터 폐기를 사용자 I/O보다 높은 우선순위로 처리 → TPCC 워크로드에서 **30초 이상** I/O 지연
- **Critical-Block First**: 실패한 블록만 높은 우선순위로 처리, 나머지 블록은 SSD 유휴 시간에 처리
- **효과**: 95th percentile 지연시간 **2배** 개선 (ClusterReAlloc 대비)
- **I/O 성능 비교**:
  - BlockReAlloc: 블록당 1개 실시간 재할당 → 사용자 I/O 영향 적음
  - CriticalReAlloc: 블록당 1개 높은 우선순위 + 나머지 유휴 시간 → BlockReAlloc와 유사하거나 더 우수

## 핵심 기여

- **핵심 기여**: 3D flash 메모리에서 cluster similarity 현상을 최초 실증하고, 이를 활용한 bad block management 정책 제시
- **성능 혁신**: 동일 신뢰성에서 SSD 수명 **2배** 향상, 동일 수명에서 실패율 **9배** 감소
- **실용성**: 기존 SSD 아키텍처 변경 없이 bad block management 소프트웨어 수정만으로 구현 가능
- **Critical-Block First**: 클러스터 기반 관리의 I/O 성능 문제를 해결하는 실용적 스케줄링 알고리즘
- **설계 원칙**: 물리적 근접성이 flash 블록의 신뢰성 특성을 결정 → 이를 기반으로 한 관리 정책이 효과적
- **미래 적용**: 3D flash 메모리의 층 수 증가(100+ layer)에 따라 process variation 심화 → cluster similarity 기반 관리의 중요성 증가 예상

## 주요 결과

- **구현 언어**: 실험은 Hynix 3D TLC flash 칩 기반 실제 하드웨어 플랫폼에서 수행
- **시뮬레이션 프레임워크**: MQSim (현대적 multi-queue SSD 시뮬레이션 프레임워크)
- **데이터셋**: 
  - RocKDB: 읽기 130 MB/s, 쓰기 240 MB/s
  - TPCC: 읽기 270 MB/s, 쓰기 160 MB/s
  - MSNFS: 읽기 10 MB/s, 쓰기 5 MB/s
  - MSNFS-scale: 읽기 200 MB/s, 쓰기 100 MB/s (MSNFS의 I/O 강도 20배 증가)
- **클러스터 크기 기본값**: 10 (Dpage < 1.4 조건 충족)
- **Overprovisioning rate**: 10%

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2022HPCA-summarize/efficient-bad-block-management-with-cluster-similarity.md|전체 요약 보기]]
