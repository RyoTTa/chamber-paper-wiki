---
tags: [paper, 2021, 2021MICRO, topic/dram, topic/pim]
venue: "MICRO 2021 (54th Annual IEEE/ACM International Symposium on Microarchitecture)"
year: 2021
summary_path: "../paper-summaries/2021MICRO-summarize/sisa-set-centric-isa-for-graph-mining-on-pim-systems.md"
---

# SISA: Set-Centric Instruction Set Architecture for Graph Mining on Processing-in-Memory Systems

**Venue:** MICRO 2021 (54th Annual IEEE/ACM International Symposium on Microarchitecture)
**저자:** Maciej Besta (ETH Zurich), Raghavendra Kanakagiri (IIT Tirupati), Grzegorz Kwasniewski (ETH Zurich), Rachata Ausavarungnirun (King Mongkut's University of Technology North Bangkok), Jakub Beránek (Technical University of Ostrava), Konstantinos Kanellopoulos (ETH Zurich), Kacper Janda (AGH-UST), Zur Vonarburg-Shmaria (ETH Zurich), Lukas Gianinazzi (ETH Zurich), Ioana Stefan (ETH Zurich), Juan Gómez-Luna (ETH Zurich), Marcin Copik (ETH Zurich), Lukas Kapp-Schwoerer (ETH Zurich), Salvatore Di Girolamo (ETH Zurich), Nils Blach (ETH Zurich), Marek Konieczny (AGH-UST), Onur Mutlu (ETH Zurich), Torsten Hoefler (ETH Zurich)

## 개요

- 기존 그래프 분석은 vertex-centric, edge-centric, linear algebra 패러다임에 집중하여 BFS, PageRank 등 단순 알고리즘을 다루었으나, **graph mining**(clustering, maximal clique listing, subgraph isomorphism 등)은 거의 연구되지 않음
- Graph mining 알고리즘은 **NP-hard 문제**가 많으며, 최소 이차 이상의 시간 복잡도를 가지므로 기존 방법으로는 대규모 그래프 처리에 한계
- Vertex-centric 모델(Pregel)은 **지역 그래프 구조만** 노출하므로, graph mining에 필요한 **비지역 그래프 지식(non-local knowledge)** 획득이 어려움
- Graph mining 알고리즘은 **메모리 바운드** 특성이 뚜렷함: Figure 1에서 병렬 스레드 수 증가 시 실행 시간 감소가 평탄화(stall CPU cycle 증가)로 확인
- 기존 그래프 가속기(GaaS-X, GraphiDe, Spara 등)는 특정 문제(SpMV, vertex-centric 등)에만 특화되어 **범용 graph mining을 지원하지 않음**

## 방법론

### 3.1. Set-Centric 프로그래밍 패러다임

- 그래프 마이닝 알고리즘을 **집합 중심으로 재구성** (Table 2):
  - Maximal clique listing: Bron-Kerbosch 알고리즘에서 $A \cup B$, $A \cap B$, $A \setminus B$ 사용
  - k-clique listing: $A \cap B$
  - Triangle counting: $|A \cap B|$
  - Subgraph isomorphism: $A \cap B$, $|A \cap B|$, $A \cup B$, $A \setminus B$
  - Vertex similarity/Clustering: $|A \cap B|$, $|A \cup B|$ (Jaccard 계수 등)
- Algorithm 1-5에 각 문제별 set-centric 알고리즘 수록
- **10개 이상의 SISA set-centric 알고리즘** 제안으로 광범위한 적용성 입증

### 3.2. SISA ISA 확장

- **집합 연산 명령어** (intersection, union, difference)를 하드웨어 수준에서 지원
- 각 명령어에 대해 ** Variant 자동 선택**: merge vs. galloping
  - **Merge variant**: 두 집합을 병렬 스트리밍하여 처리
  - **Galloping variant**: 작은 집합의 각 원소에 대해 큰 집합에서 이진 탐색
- **SCU(Set Control Unit)**: 명령어 Variant 선택 및 실행 제어
  - LRU 캐시(32 KB) 포함으로 집합 메타데이터 캐싱
  - 성능 모델 기반 자동 Variant 결정

### 3.3. PIM 통합

- **SISA-PUM**: 고도 정점의 비트벡터에 대한 in-DRAM 비트 연산
  - 실행 시간: $l_M + l_I \cdot \lceil n/(qS) \rceil$ ($l_M$: DRAM 접근 지연, $l_I$: in-situ 명령 실행 시간, $n$: 비트벡터 크기, $q$: 병렬 처리 가능한 행 수, $S$: 행 크기)
  - 최대 8개의 DRAM 행을 병렬 처리 가능
- **SISA-PNM**: Tesseract 기반 near-memory logic layer 활용
  - 각 vault당 1개 in-order 코어 (32 KB L1 캐시)
  - 16 GB HMC × 16개 = 128 GB, 32 vaults/cube
  - Vault당 16 GB/s 메모리 대역폭

### 3.4. Set Metadata 관리

- **Set Metadata (SM) 구조**: 각 집합에 대한 상수 크기 메타데이터 저장
  - 집합 표현 방식 (DB: Dense Bitvector vs. SA: Sparse Array)
  - 집합 크기
- 총 SM 크기: $O(n)$ — 그래프의 정점 수에 비례
- SM은 캐시 또는 small scratchpad에 완전히 적재 가능 (대부분의 graph mining 데이터셋에서 $n$이 수백~수천 수준)

## 핵심 기여

- **핵심 기여**: Graph mining을 위한 최초의 **set-centric ISA + PIM 통합 시스템** 제안
- **성능 향상**: non-set 기반 기존 방법 대비 **2x ~ >10x** 가속, set-based 알고리즘 대비 **최대 9.8x** 추가 가속
- **범용성**: 10개 이상의 그래프 마이닝 문제(maximal clique, k-clique, subgraph isomorphism, clustering, triangle counting 등)에 적용 가능
- **의의**:
  - Graph mining의 메모리 바운드 문제를 PIM으로 효과적으로 해결
  - 기존 가속기들이 다루지 못한 범용 graph mining 지원
  - Set-centric 프로그래밍 패러다임으로 복잡한 그래프 알고리즘을 단순화
  - 고도 정점(실세계 그래프에서 흔함)에 특화된 PUM 활용으로 높은 효율 달성

## 주요 결과

| 항목 | 내용 |
|------|------|
| **시뮬레이터** | custom 시뮬레이션 프레임워크 |
| **호스트 플랫폼** | Out-of-Order manycore CPU (128-entry instruction window, 32 KB L1, 256 KB L2, 8 MB L3) |
| **PIM 플랫폼** | Tesseract (PNM) + Ambit (PUM) |
| **HMC** | 16 × 8 GB = 128 GB (32 vaults/cube, 16 banks/vault) |
| **대역폭** | Vault당 16 GB/s (scalable bandwidth) |
| **DRAM row rank** | 8 KB (Ambit 기준) |
| **설정 파라미터** | $t = 0.4$ (40% neighborhoods를 DB로 저장), neighborhood 저장 오버헤드 < CSR 대비 10% |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2021MICRO-summarize/sisa-set-centric-isa-for-graph-mining-on-pim-systems.md|전체 요약 보기]]
