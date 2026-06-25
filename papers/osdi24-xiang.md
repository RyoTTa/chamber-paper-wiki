---
tags: [paper, 2024, 2024OSDI, topic/disaggregation, topic/dram, topic/memory-tiering, topic/virtual-memory]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024OSDI-summarize/osdi24-xiang.md"
---

# NOMAD: Non-Exclusive Memory Tiering via Transactional Page Migration

**Venue:** 
**저자:** Lingfeng Xiang, Zhen Lin, Weishu Deng, Hui Lu, Jia Rao (UT Arlington), Yifan Yuan, Ren Wang (Intel Labs)

## 개요

CXL 메모리, Optane PM 등 byte-addressable slow memory device의 등장으로 tiered memory가 현실화되었으나, 기존 OS page management는 **exclusive tiering**(한 페이지가 fast/slow tier 중 한 곳에만 존재)을 전제한다. 이는 DRAM-disk 간 2-3 order 차이의 전통적 memory hierarchy 가정에 기반한다.

**CXL/PM 환경에서는 이 가정이 깨진다.** CXL memory는 DRAM 대비 latency 2-3×, bandwidth ~50% 수준으로 gap이 좁다. 또한 CPU가 load/store로 직접 접근 가능하므로, warm page를 굳이 migration하지 않고 slow tier에서 직접 접근하는 것이 유리할 수 있다.

**Figure 1 — TPP의 motivation 실험:**
- 16GB DRAM + 16GB CXL, Zipfian distribution micro-benchmark
- WSS 10GB (fits fast tier): TPP가 active migration 중일 때 bandwidth가 TPP stable 대비 10배 이상 낮음. **"No migration" baseline이 TPP in progress보다 일관되게 우수** — migration overhead가 benefit을 압도.
- WSS 24GB (exceeds fast tier): **TPP가 stable state에 도달하지 못하고 memory thrashing에 빠짐.**
- 초기 배치가 sub-optimal(random)일 때만 page migration이 궁극적 이점을 제공.

**Figure 2 — TPP runtime breakdown:**
migrating 과정에서 synchronous page promotion + page fault handling이 application core 시간의 대부분을 소모. demotion core는 대부분 idle. 최악의 경우 한 페이지 promotion에 최대 15회의 minor page fault 발생 가능.

## 방법론

- **Kernel:** Linux v5.13-rc6
- **Page shadowing:** XArray, shadow flag, shadow page fault handler
- **TPM:** kpromote kernel thread, PCQ/migration pending queue, per-cpu migration state
- **No hardware modification required** — PEBS, additional counters 불필요

## 핵심 기여

**핵심 기여:**
1. **Non-exclusive memory tiering 개념 제안:** 기존 exclusive tiering의 한계를 지적하고, promotion된 page의 shadow copy를 slow tier에 유지하는 새로운 패러다임
2. **Transactional Page Migration:** page unmap 없이 copy → dirty bit 기반 commit/abort. Migration을 완전히 asynchronous로 만들고 critical path에서 제거
3. **Page Shadowing:** PTE software bit를 활용한 shadow page fault로 consistency tracking. Demotion을 page remapping만으로 처리

**Broader significance:**
- CXL/PM 환경에서 fast-slow tier 성능 격차가 좁아질수록 NOMAD의 이점이 증가 (Platform D 결과)
- Page fault 기반 tracking (recency) vs PEBS sampling (frequency) 간 근본적 tradeoff 규명
- "No migration"이 많은 시나리오에서 page migration보다 우수 — **migration on/off 결정의 중요성** 입증
- Shadowing으로 read 작업은 thrashing에서도 보호되나, write에서는 shadow page fault overhead 존재

## 주요 결과

### 4.1 실험 환경 — 4개 플랫폼 (Table 1)

| Platform | CPU | Fast tier | Slow tier | Fast:Slow latency ratio |
|----------|-----|-----------|-----------|------------------------|
| A | 4th Gen Xeon Gold, DDR5 | 16GB DRAM | 16GB FPGA CXL (Agilex 7) | 316:854 cycles (2.7×) |
| B | 4th Gen Xeon Platinum (ES) | 16GB DRAM | 16GB FPGA CXL | 226:737 cycles (3.3×) |
| C | 2nd Gen Xeon Gold | 16GB DDR4 | 256GB Optane PM×6 | 249:1077 cycles (4.3×) |
| D | AMD Genoa | 16GB DDR5 | 256GB Micron CXL×4 | 391:712 cycles (1.8×) |

### 4.2 Baselines

- **TPP** (transparent page placement) — synchronous promotion + async demotion
- **Memtis-Default** — PEBS sampling, 2,000k sample cooling period
- **Memtis-QuickCool** — PEBS sampling, 2k sample cooling period (aggressive)
- **No migration** baseline

### 4.3 Micro-benchmark 결과 (Figure 7-9)

**Small WSS (10GB, fits fast tier):**

| Phase | Read | Write |
|-------|------|-------|
| Transient | NOMAD ≈ Memtis > TPP | Memtis > NOMAD (aborted migration + shadow overhead) |
| Stable | NOMAD ≈ TPP >> Memtis (40% of NOMAD) | 동일 |

Memtis의 stable phase 취약점: PEBS가 hot page를 충분히 포착하지 못해 대부분의 access가 여전히 slow tier에서 발생. QuickCool이 더 나은 성능 → sampling rate와 accuracy의 tradeoff.

**Medium WSS (13.5GB, barely fits):**

| Phase | Read | Write |
|-------|------|-------|
| Transient | Memtis > NOMAD ≈ TPP (NOMAD/TPP: 2-6× more migrations, many futile) | 동일 |
| Stable | **NOMAD >> TPP** (shadowing benefit), NOMAD > Memtis (read) | Memtis > NOMAD (shadow page fault overhead) |

Platform D에서 NOMAD의 우위가 가장 두드러짐: fast-slow gap이 작을수록 sync migration overhead가 상대적으로 더 크기 때문.

**Large WSS (27GB, severe thrashing):** Memtis > NOMAD > TPP. Page-fault 기반 접근은 심한 thrashing에서 불리. 그러나 NOMAD는 TPP 대비 일관되게 우수 (shadowing + async TPM).

### 4.4 Real-world Applications (§4.2)

**Redis + YCSB-A (50/50 read/write):**

| Case | RSS | NOMAD vs TPP | NOMAD vs Memtis |
|------|-----|-------------|-----------------|
| Case 1 | 13GB (small) | 우수 | 우수 |
| Case 2 | 24GB (medium) | 우수 | 열세 (migration 증가 + overhead) |
| Case 3 | 24GB (no initial demote) | 우수 | 열세 |
| Large RSS | 36.5GB | 우수 | 열세 |

모든 migration approach가 **"no migration"보다 열세** — YCSB workload가 random access pattern이어서 migration 이점이 제한적.

**PageRank (22GB RSS):** Migration 여부에 따른 성능 차이 미미. Compute-intensive workload는 CXL memory latency에 덜 민감. Memtis가 가장 낮은 성능.

**Liblinear (10GB RSS, L1 logistic regression):** NOMAD/TPP가 no migration/Memtis 대비 **20~150% 성능 향상**. WSS < fast tier일 때 timely migration이 중요함을 입증.

**Large RSS PageRank (100GB → 45-50GB):** NOMAD가 TPP 대비 **2× 성능** (양 platform), Memtis보다 약간 우수.

**Large RSS Liblinear:** NOMAD consistent high performance, TPP는 kernel CPU time spike로 인해 성능 급락.

### 4.5 Migration Success Rate (Table 4)

| Workload | Success:Aborted ratio |
|----------|----------------------|
| Liblinear (large RSS, C) | 1:1.9 (낮음) |
| Liblinear (large RSS, D) | 2.6:1 |
| Redis (large RSS, C) | 153:1 (매우 높음) |
| Redis (large RSS, D) | 278.2:1 |

**역설:** Success rate가 낮은 Liblinear에서 NOMAD 성능이 우수, 높은 Redis에서 저조. 낮은 success rate = page가 활발히 write 중 = truly hot page → migration 가치가 높음.

### 4.6 PEBS 한계 분석 (Figure 10)

**Pointer-chasing benchmark** (모든 access가 LLC miss 유발 → PEBS에 완벽히 포착):

Memtis는 WSS > fast tier일 때 대부분의 hot page가 slow tier에 남아있음 (평균 latency ≈ slow memory latency). 원인: cache hit이 많은 truly hot page는 PEBS가 포착하지 못함 (cache miss 기반 샘플링의 근본적 한계).

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2024OSDI-summarize/osdi24-xiang.md|전체 요약 보기]]
