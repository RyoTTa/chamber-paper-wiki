---
tags: [paper, 2019, 2019ISCA, topic/compression, topic/nvm, topic/storage]
venue: "The 46th Annual International Symposium on Computer Architecture (ISCA '19)"
year: 2019
summary_path: "../paper-summaries/2019ISCA-summarize/graphssd-graph-semantics-aware-ssd.md"
---

# GraphSSD: Graph Semantics Aware SSD

**Venue:** The 46th Annual International Symposium on Computer Architecture (ISCA '19)
**저자:** Kiran Kumar Matam (University of Southern California), Gunjae Koo (Hongik University), Haipeng Zha (University of Southern California), Hung-Wei Tseng (North Carolina State University), Murali Annavaram (University of Southern California)

## 개요

- 그래프 분석(Social Network, Drug Discovery, Recommendation System 등)은 현대 컴퓨팅의 핵심 워크로드이나, 그래프 크기가 메인 메모리를 초과할 때 **스토리지 접근 병목**이 발생
- 기존 Out-of-core 그래프 처리 프레임워크는 graph sharding, sub-graph partitioning 등을 사용하지만, **서브그래프 간 데이터 접근**으로 인해 스토리지 시스템이 여전히 주요 성능 병목
- NAND Flash SSD 가격이 2019년 기준 약 **$100/1TB** 수준으로 하락하고, NVMe 인터페이스로 **대역폭 및 통합 컴퓨팅** 가능성 확대
- 기존 SSD는 그래프 구조를 인식하지 못하고 **블록集合으로만** 취급 → 그래프 의미 구조(graph semantics)를 활용한 최적화 불가능
- 그래프의 인접 리스트 크기가 정점마다 크게 다름 → 고정된 NAND 페이지 크기 제약과의 불일치 문제

## 방법론

### 3.1. 그래프 레이아웃 및 API

- CSR 형식의 세 벡터(rowPtr, colIdx, val)를 NAND 페이지에 배치
- **colIdx와 val 벡터**만 NAND 페이지에 저장, rowPtr는 인덱스 테이블로 사용
- 지원 API: `getNeighbors(vertex_id)`, `getEdgeWeight(vertex_id, neighbor_id)` 등
- 모든 API는 vertex ID를 입력으로 받아 그래프 접근 시작

### 3.2. Graph Translation Layer (GTL)

- 기존 LBA-to-PPN 매핑을 대체하는 **vertex ID → PPN 직접 매핑**
- GTT(Graph Translation Table) 구조:
  - 각 엔트리: vertex ID, PPN, status flags (dirty, extension, valid)
  - **정렬된 vertex ID** 저장으로 이진 검색 지원
- 페이지 레이아웃 메타데이터:
  - 페이지 끝에 `{vertex, offset}` 튜플 N+1개 저장
  - 마지막 필드: 해당 페이지에 저장된 정점 수
  - **인접 리스트는 페이지 시작부터**, 메타데이터는 **페이지 끝부터** 저장
- Dense vertex 처리: 인접 리스트가 페이지를 초과하면 **여러 GTT 엔트리** 할당

### 3.3. 그래프 업데이트 메커니즘

- **AddEdge(Vid1, Vid2)**:
  - Vid1의 인접 리스트가 단일 페이지인 경우: 페이지 끝에 추가 후 후속 정점들의 offset 갱신
  - 인접 리스트가 여러 페이지에 걸친 경우: 새 페이지 할당 및 GTT 업데이트
  - **Extension 비트**를 사용한 확장 GTT 관리
- **AddVertex**: 새 정점과 인접 리스트를 새로운 페이지에 저장
- **Delta Graph**: 업데이트된 서브그래프만 별도 저장하여 전체 그래프 재배치 방지
- **Delta Merging**: 주기적으로 원래 그래프와 Delta Graph를 병합

## 핵심 기여

- **핵심 Contribution**: 그래프 의미를 인식하는 최초의 SSD 프레임워크 GraphSSD 제안
- **성능 향상**: 기존 SSD 기반 그래프 처리 대비 평균 1.29×~1.85× 성능 개선
- **실용성**: NVMe 인터페이스와 호환되는 프로그래밍 API로 기존 그래프 프레임워크와의 통합 용이
- **의의**: 스토리지 계층에서 그래프 의미를 활용하는 새로운 패러다임 제시, 대규모 그래프 처리의 성능 병목 해소

## 주요 결과

- **구현 플랫폼**: 산업용 SSD 개발 플랫폼 기반
- **인터페이스**: NVMe 인터페이스에 최소 변경으로 그래프 접근 API 매핑
- **프로그래밍 모델**: GraphCHI, Pregel 유사 API 제공
- **지원 연산**: BFS, Connected Components, Random Walk, Maximal Independent Set, PageRank

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2019ISCA-summarize/graphssd-graph-semantics-aware-ssd.md|전체 요약 보기]]
