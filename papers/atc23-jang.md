---
tags: [paper, 2023, 2023ATC, topic/cache, topic/compression, topic/disaggregation, topic/dram, topic/memory-tiering, topic/nvm, topic/storage]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023ATC-summarize/atc23-jang.md"
---

# CXL-ANNS: Software-Hardware Collaborative Memory Disaggregation and Computation for Billion-Scale Approximate Nearest Neighbor Search

**Venue:** 
**저자:** 

## 개요

- **Billion-scale ANNS의 메모리 압박:** Production 추천 시스템은 수십 TB의 working memory 필요. Microsoft Bing/Outlook: 100B+ 벡터 × 100차원 → 40TB 이상. Alibaba: 2B+ 벡터 × 128차원 → TB-scale.
- **기존 접근법의 한계:**
  - Compression (Product Quantization 등): embedding table을 cluster centroid로 양자화 → 정확도 저하. 압축률 45.8% 이상에서 target recall@k=0.9 도달 불가. 또한 graph 자체는 압축되지 않음.
  - Hierarchical (DiskANN, HM-ANN): SSD/PMEM에 original graph + vector 저장, DRAM에 압축/simplified 버전 유지. High-accuracy search가 storage access를 요구 → DiskANN/HM-ANN latency가 in-memory Oracle 대비 각 29.4×, 64.6× 느림 (평균). Storage access가 전체 latency의 87.6%.
- **CXL-augmented baseline:** CXL switch + 4× 1TB Type 3 EP로 모든 graph/vector를 CXL memory pool에 배치. Compression/hierarchical 방식의 정확도·성능 저하를 피할 수 있으나, 모든 memory access가 host RC의 flit 변환 + EP-side 재변환을 거쳐 **Oracle 대비 3.9× 느린 search latency** (Figure 8). 이는 production 환경에서 수용 불가능한 수준.
- **목표:** CXL memory pool의 scalability + accuracy를 유지하면서 Oracle(in-memory DRAM-only, unlimited capacity)보다 더 빠른 latency/throughput 달성.

## 방법론

### 1. Observation 기반 설계 방향

**(O1) Node-level relationship:** ANNS는 fixed entry-node에서 BFS 시작 → inner edge hops (2~3 hops) 노드들이 1M queries 동안 압도적으로 많이 방문됨 (Figure 9b). → inner node graph+vector를 local DRAM에 캐싱, outer node는 CXL pool에 배치.

**(O2) Distance calculation이 bottleneck:** End-to-end kNN search 분해 결과, distance calculation이 전체 latency의 81.8% (Figure 10). Graph traverse보다 dominant. Distance 계산은 lightweight arithmetic → EP-side 가속에 적합.

**(O3) Vector transfer reduction:** EP가 distance를 계산하면 scalar distance만 host로 전송 → vector dimension (96~256)만큼 data transfer 감소. 평균 73.3× reduction (Figure 11b).

### 2. 아키텍처 개요 (Figure 12)

**RC-side software stack:**
- **Query Scheduler:** 각 kNN query를 graph traverse, distance calculation, candidate update의 3개 subtask로 분할. Graph traverse + candidate update → CXL CPU, distance calc → EP로 할당.
- **Pool Manager:** edge hop count 기반 데이터 배치. User-level virtual address에 CXL arena 매핑.
- **Kernel Driver:** CXL device enumeration, HDM mapping to HPA, EP interface registers를 CXL.io (non-cacheable PCIe space)로 매핑.

**EP-side hardware stack:**
- PHY controller + CXL engine (flit↔memory request 변환) + 4 memory controllers (각 256GB DIMM)
- **DSA (Domain-Specific Accelerator):** CXL engine과 memory controller 사이 위치. 10 PEs, 각 PE는 multiplier + subtractor + adder의 arithmetic logic tree. 4개 DIMM channel 병렬 읽기.

### 3. Relationship-Aware Graph Caching (§4.1)

**Algorithm:** SSSP(Single Source Shortest Path)로 entry-node에서 각 노드까지의 edge hop count 계산.
1. 모든 노드 hop count = -1로 초기화
2. Entry-node부터 BFS로 방문, 각 hop마다 count 증가
3. Hop count 오름차순 정렬 → local DRAM이 수용 가능한 만큼 low-hop node 할당

**CXL arena management (§4.2):**
- Kernel driver: PCIe config space → CXL devices 식별 → device tree/ACPI로 HPA base 확인 → contiguous HPA 할당
- Pool manager: Stack-like allocator (embedding table, round-robin across EPs) + Buddy-like allocator (variable-length neighbor lists, 16B~1KB, round-robin per hop). 두 allocator가 각 CXL arena에서 opposite direction으로 grow.

## 핵심 기여

1. **CXL memory pool은 ANNS의 accuracy·scalability 문제를 해결할 근본적 접근.** Compression/hierarchical 방식의 정확도 저하나 storage latency 폭증 없이 billion-scale dataset 수용 가능.

2. **Distance calculation의 EP-side 가속이 핵심.** 전체 latency의 81.8%를 차지하는 distance calc을 CXL EP의 lightweight DSA로 분산 처리 → data transfer 21.1× 감소, Oracle 대비 1.9× 낮은 latency. GPU 대비 cost-effective (경량 PE로 충분, data movement overhead 없음).

3. **ANNS 알고리즘 특성(CXL-aware) 활용이 성능 차별화.** Node-level relationship 기반 graph caching + candidate array 기반 prefetching으로 CXL의 far-memory latency를 숨기고, fine-granular scheduling으로 RC-EP 간 CPU idle을 최소화. 모두 ANNS 알고리즘의 고유한 동작 패턴(entry-node, BFS, candidate array)을 깊이 이해한 설계.

4. **Oracle system을 능가하는 최초의 CXL-augmented ANNS.** CXL memory pool의 구조적 latency penalty에도 불구하고, S/W-H/W 협업 설계로 순수 local DRAM system보다 3.8× 높은 throughput 달성. CXL 기반 memory disaggregation이 단순히 "느린 메모리 확장"이 아니라 성능 향상 플랫폼이 될 수 있음을 입증.

## 주요 결과

**Motivation:** Local caching만으로는 large graph(Meta-S, MS-S)에서 24.5%만 local hit → 나머지는 CXL round-trip latency에 노출.

**Observation:** 다음 iteration에 방문할 노드의 82.3%가 현재 candidate array에 이미 존재 (미업데이트 상태라도) (Figure 18).

**Prefetch mechanism:** Candidate array를 보고 next visiting node speculation → graph 정보를 미리 CXL pool에서 prefetch. Speculation overhead는 전체 query latency의 1.3%로 미미.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2023ATC-summarize/atc23-jang.md|전체 요약 보기]]
