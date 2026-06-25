---
tags: [paper, 2023, 2023ASPLOS, topic/cache, topic/disaggregation, topic/dram, topic/virtual-memory]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023ASPLOS-summarize/tpp-transparent-page-placement-for-cxl-enabled-tiered-memory.md"
---

# TPP: Transparent Page Placement for CXL-Enabled Tiered-Memory

**Venue:** 
**저자:** 

## 개요

Hyperscale datacenter의 memory demand 급증으로 memory가 rack TCO와 power의 주요 비중을 차지 (Meta 하드웨어 세대별: Gen0→Gen5에서 memory 비중 14.6%→31.8%, Figure 3). CXL은 cache-line granularity, DRAM-like bandwidth (~180 ns latency), coherent access semantics를 갖춘 새로운 memory bus interface로, CPU-attached memory와 독립적인 CPU-less NUMA node를 제공 (Figure 1). 이를 통해 flexible tiered-memory system 설계가 가능해졌으나, Linux의 memory management는 homogeneous DRAM-only system에 최적화되어 있어 tiered-memory에서 비효율적.

**Characterization 결과 (Chameleon 도구):** Meta production server fleet의 4개 서비스 도메인 (Web, Cache, Data Warehouse, Ads) 분석:

1. **상당량의 cold memory 존재:** 2분 interval 내에 allocated memory의 22~80%만 hot — 나머지 55~80%는 idle (Figure 7). Data Warehouse도 평균 20%만 hot.
2. **Anon pages가 file pages보다 더 hot:** Web에서 2분 내 hot anon 35~60%, file은 3~14% (Figure 8). Cache도 유사 경향.
3. **Access pattern이 minutes-to-hours 단위로 안정적:** Kernel-space page placement 결정에 충분한 observation window 제공.
4. **Physical page 주소가 바뀌면 hot/cold 특성도 빠르게 변화:** Static page allocation은 성능 저하 초래.
5. **Cold page re-access time은 workload별 상이:** Web은 10분 내 80% 재접근, Data Warehouse는 20%만 재접근 (Figure 11). Blind offloading 위험.
6. **Page type별 sensitivity 다름:** Web throughput은 anon 활용도에 비례, Cache는 file pages 의존도 높음 (Figure 10).

## 방법론

TPP는 OS-level application-transparent page placement. CXL-Memory를 swap-space가 아닌 load/store access semantics로 직접 사용 — swap abstraction 사용 시 매 access마다 major page fault 발생 → 200ns 이상 latency 손실.

## 핵심 기여

1. **Production workload characterization으로 tiered-memory feasibility 입증:** 55~80%의 allocated memory가 2분 내 idle. Chameleon 도구 공개.
2. **CXL-Memory를 swap이 아닌 load/store access semantics로 직접 사용:** Swap abstraction의 major page fault overhead 제거. CXL의 핵심 장점인 cache-line granularity 활용.
3. **3대 핵심 메커니즘:** (a) Migration 기반 fast demotion (swapping 대비 orders of magnitude faster), (b) Allocation/reclamation decoupling으로 free page headroom 유지, (c) Active LRU 기반 hysteresis promotion으로 ping-pong 제거.
4. **Up to 18% 개선 (vs default Linux), 5~17% 개선 (vs NUMA Balancing/AutoTiering).** Local memory가 전체 20%에 불과한 1:4 configuration에서도 baseline 대비 <1% throughput gap.
5. **Linux kernel upstream:** v5.18에 major portion merged. 실질적 production deployment 가능.

## 주요 결과

**구현 계층:** User-space (Chameleon-like + `move_pages()`) → context-switch overhead, user-space history 관리 부담, large working set에 scaling 불가. **Kernel-space가 더 적합** — less complex + more performant.

**Page temperature detection 방식 선택:**
- PEBS: Counter가 CPU vendor별 비표준, always-running component로 부적합 (high-pressure workload에서 overhead).
- Page poisoning + accessed bit: IPT 기반 방식은 TLB flush 필요 → unacceptable slowdown. Thermostat은 2MB granularity에 한정.
- **LRU + NUMA Balancing 조합 채택:** Local node cold detection = kernel LRU-based age 관리 (lightweight, 효율적). CXL-node hot detection = NUMA Balancing의 minor page fault (CXL-node는 warm/cold page 보관 → overhead 낮음). Virtually zero overhead 달성 (Figure 14, Table 1).

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2023ASPLOS-summarize/tpp-transparent-page-placement-for-cxl-enabled-tiered-memory.md|전체 요약 보기]]
