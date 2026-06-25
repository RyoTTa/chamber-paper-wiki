---
tags: [paper, 2023, 2023MICRO, topic/cache, topic/dram, topic/virtual-memory]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023MICRO-summarize/victima-drastically-increasing-address-translation-reach-by-leveraging-underutilized-cache-resources.md"
---

# Victima: Drastically Increasing Address Translation Reach by Leveraging Underutilized Cache Resources

**Venue:** 
**저자:** Konstantinos Kanellopoulos, Hong Chul Nam, F. Nisa Bostanci, Rahul Bera, Mohammad Sadrosadati (ETH Zürich), Rakesh Kumar (NTNU), Davide Basilio Bartolini (Huawei Zurich), Onur Mutlu (ETH Zürich)

## 개요

- **Address translation bottleneck:** 현대 data-intensive workloads에서 large data footprints + irregular access patterns → 높은 L2 TLB MPKI (baseline 1.5K-entry L2 TLB 기준 **평균 39 MPKI**).
- **PTW latency:** 평균 **137 cycles** (최대 608 cycles). → 전체 execution cycles의 평균 **30%**가 address translation에 소비.
- **Virtualized environments:** Nested paging은 two-level translation → 최대 **24회 sequential memory access** (native 4회 대비 6×).
- **기존 해결책의 한계:**
  - **Large hardware TLBs:** 64K-entry L2 TLB → MPKI 44% 감소하나 CACTI 7.0 기준 access latency 39 cycles → 실제 성능 향상 **0.8%**에 불과 (Fig. 7). L3 TLB 64K-entry도 optimistic 15-cycle latency에서 2.9% 향상 (Fig. 8).
  - **Software-managed TLBs (STLB):** Memory fetch 필요 → native 환경 평균 L2 miss latency 122 cycles (baseline 128 cycles와 유사). Virtualized에서는 220 cycles (baseline 275 cycles)로 더 효과적. 그러나 contiguous physical memory 필요 (수십 MB), OS 수정 필요, resize 어려움.
- **Opportunity:** 2MB L2 cache는 2048-entry L2 TLB의 **128×** TLB entries 저장 가능. L2 cache hit 시 ≈16 cycles로 translation 가능 (PTW 137 cycles 대비).

## 방법론

**핵심 아이디어:** L2 cache의 underutilized block을 재활용하여 TLB entry cluster 저장 → low-latency, high-capacity backup for L2 TLB.

### 1. L2 Cache Modifications

**TLB Block (Fig. 13):**
- 새로운 cache block type. 각 64-byte cache block은 8개의 8-byte PTE 저장 (= 8개 contiguous virtual page).
- Tag 구성: VPN(23-bit) + ASID/VMID(11-bit) + page size + TLB entry bit(1-bit) + nested TLB bit.
- 조건: `PA_length > VA_length − 9` (48-bit VA, 52-bit PA → 52 > 39 충족). 조건 불충족 시 7개 PTE 저장하고 남은 bit를 tag로 사용 가능.
- ASID 11-bit → Linux의 12 ASIDs/core 충분히 커버.

**TLB-Aware SRRIP Replacement Policy (Listing 5.1):**
- **Insertion:** TLB block + L2 TLB MPKI > 5 → RRIP counter = 0 (최우선). 아니면 RRIP_MAX.
- **Eviction candidate:** TLB block이 victim으로 선택되면 + MPKI > 5 → 한 번 더 skip 시도, non-TLB block 찾기. 없으면 TLB block evict (drop, no writeback).
- **Cache hit:** TLB block hit → RRIP counter −3 (일반 data block은 −1) → TLB entry 우선 유지.

### 2. TLB Block Insertion (Fig. 14)

**PTW Cost Predictor (PTW-CP) (Fig. 15, Table 1-2):**
- 목적: costly-to-translate page 예측 → cache 공간을 효과적으로 사용.
- PTE의 unused bit에 2개 counter 저장: **PTW frequency (3-bit)** — PTW 발생 시 증가, **PTW cost (4-bit)** — PTW 중 ≥1 DRAM access 시 증가.
- **Feature selection:** 10개 feature → NN-10(F1 90.42%) → NN-5(F1 89.89%) → **NN-2(PTW frequency + PTW cost, F1 80.66%)**.
- **Final implementation:** Comparator-based model (Fig. 16). NN-2의 prediction pattern 분석 → bounding box: PTW frequency [1,12] × PTW cost [1,7] → inside = costly. Comparators 4개만 필요, 24 bytes, single-cycle prediction, F1-score 80.66% 유지.
- L2 cache MPKI > 5 → PTW-CP bypass (data locality 낮아 cache data 효용성 낮으므로 모든 TLB entry cache).

**L2 TLB Miss 시 Insertion:**
1. PTW-CP에 costly-to-translate 여부 확인
2. 이미 L2 cache에 TLB block 존재 → no action
3. 없으면 PTW 완료 대기 → 마지막 level PTE가 fetch된 cache block을 TLB block으로 변환: tag 교체, TLB bit set, ASID/page size 업데이트

**L2 TLB Eviction 시 Insertion:**
1. PTW-CP 확인
2. Cache에 존재 → no action
3. 없으면 **background PTW** 발행 → PTE fetch 완료 시 해당 cache block을 TLB block으로 변환

### 3. Address Translation Flow (Fig. 17)

- L2 TLB miss 발생 시 (1) PTW 시작 + (2) parallel L2 cache lookup (TLB block 검색).
- TLB block lookup은 VPN + ASID로 수행. 4KB/2MB VPN 모두 probe (parallel).
- TLB block hit → **PTW abort**, translation을 L2 TLB에 insert.
- TLB block miss → PTW 완료까지 진행.

## 핵심 기여

1. **Cache hierarchy underutilization을 활용한 TLB 확장** — 92%의 L2 cache block이 zero reuse → TLB entries로 repurpose.
2. **Native 7.4%, Virtualized 28.7% 성능 향상** — 간단한 comparator-based predictor(80.66% F1) + TLB-aware SRRIP로 달성.
3. **Opt. L2 TLB-128K와 동등한 성능을 0.04% area/0.08% power로 달성** — hardware TLB 확장의 cost 문제 해결.
4. **STLB의 단점 극복:** contiguous memory 불필요, OS 수정 불필요, L2 cache hit latency(≈16 cycles)로 memory fetch overhead 회피.
5. **Virtualization에 특히 효과적** — PTW latency가 큰 환경에서 L2 cache hit의 이점 극대화.

## 주요 결과

- TLB block + **Nested TLB block** 모두 L2 cache에 저장.
- Nested TLB block: 8개 guest-physical-to-host-physical mappings 저장 (host-virtual page 기준).
- 별도 nested TLB bit로 conventional TLB block과 구분.
- Nested TLB miss → nested TLB block lookup in L2 cache → hit 시 host-PTW skip.
- Insertion logic은 §5.2와 동일 (miss/eviction 기반).

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2023MICRO-summarize/victima-drastically-increasing-address-translation-reach-by-leveraging-underutilized-cache-resources.md|전체 요약 보기]]
