---
tags: [paper, 2023, 2023ASPLOS, topic/cache, topic/compression, topic/dram, topic/virtual-memory]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023ASPLOS-summarize/mosaic-pages-big-tlb-reach-with-small-pages.md"
---

# Mosaic Pages: Big TLB Reach with Small Pages

**Venue:** 
**저자:** 

## 개요

TLB는 big data application의 major bottleneck. 현대 TLB는 latency 제약으로 entry 수가 극히 제한적이며, working set 성장 속도를 따라가지 못한다:

- Intel Golden Cove 서버 칩: L2 TLB에 **2,488개 discrete translation**만 보유 (모든 page size 합산)
- Graph500 BFS: working set ~215 MiB, 4KB page TLB는 단 **8.6 MiB**만 커버
- 현대 application의 20-30% overhead가 TLB miss에서 발생, 일부는 **83%** 까지

**기존 해결책의 한계 — Huge Pages:**
Huge pages(2 MiB, 1 GiB)는 physical contiguity에 의존하며, defragmentation 비용이 성능 이득을 상쇄할 수 있다:
- Zhu et al. 보고: Redis cold cache, 2 MiB pages → 0% fragmentation 시 **29% throughput gain**, 50% fragmentation 시 4KB pages throughput의 **89%**로 저하
- Memory bloat: huge page가 실제 필요한 것보다 많은 물리 메모리를 점유 → swapping 유발

Perforated pages 등 discontiguous huge page 기법도 residual physical contiguity에 의존하며, 복잡한 hardware(shadow page table, bitmap filter)를 필요로 한다.

---

## 방법론

### 3.1 gem5 Full-System Simulation

- gem5 simulator에 Mosaic TLB + modified radix-tree page table 구현
- L1 DTLB/ITLB: 1024 entries, unified 4KB/2MB pages
- L1d: 64KB 2-way, L1i: 32KB 2-way, L2: 2MB 8-way, L3: 16MB 16-way
- CPFN encoding: 7 bits — leading bit(front/back yard), remaining 6 bits(bucket offset) 또는 3+3 bits(backyard bucket+offset)

### 3.2 Linux Prototype (x86 bare metal)

- Linux kernel v5.11.6에 Mosaic page allocator 구현 (anonymous, unshared pages only)
- 4 GiB reserved for Mosaic allocator, 나머지는 standard Linux allocator
- xxHash 사용, demand paging
- Horizon LRU swapping 구현 (access bit emulation: 1s 주기 daemon scan + per-page 8-histories sampling)
- Shared memory, file cache, kernel은 standard allocator 사용

### 3.3 Hardware Synthesis

**FPGA (Artix-7, Verilog):**
- Tabulation hash latency: 2.155ns (464 MHz)
- 8 hash functions: 6,208 LUTs, 32 registers
- Hash function 수 증가해도 latency 불변 (probing 설계 덕분)

**28nm CMOS (System Verilog, Cadence):**
- Maximum frequency: **4 GHz**
- Latency: 220 ps, 20 ps positive slack
- Area: 13.806 KGE (8 hash functions, 2-input NAND gate 기준)
- Hash function 수 증가 → area minimal 증가, latency 불변

---

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1 실험 환경 개요

| 항목 | 내용 |
|------|------|
| Simulation (gem5) | Single-core TimingSimpleCPU, 36-bit VPN/PFN, 16GB DDR4, Linux 4.16/Debian |
| Bare metal (Linux) | Intel Xeon E3-1220 v6 4-core 3.0GHz, 32 GiB (4 GiB Mosaic reserved), Linux 5.11.6/Ubuntu 20.04, 4 GiB ramdisk swap |
| Workloads | Graph500(1010 MiB), BTree(2618 MiB), GUPS(8207 MiB), XSBench(1012 MiB) |

### 4.2 TLB Miss Reduction [Fig.6]

Arity(CPFN 수)와 TLB associativity를 변화시키며 평가:

**Arity = 4 (unmodified x86 TLB entry width):**
| Workload | TLB miss reduction |
|----------|-------------------|
| Graph500 | **6-81%** |
| BTree | **6-81%** (일부 case) |
| XSBench | **6-81%** |
| GUPS | 제한적 (random access 특성상) |

**Arity = 64:** 11-98% reduction. Graph500, XSBench에서 거의 완전히 TLB miss 제거.

**TLB associativity 영향:**
- **Direct-mapped Mosaic-8 > fully associative vanilla** (Graph500, BTree, XSBench)
- Mosaic은 TLB associativity에 덜 민감 → 저 associativity TLB로도 높은 성능

### 4.3 Memory Utilization — Associativity Conflicts [Table 3]

| Metric | Mosaic | Standard Linux |
|--------|--------|----------------|
| First associativity conflict | **98.0-98.1%** utilization | 99.2% (swapping 시작점) |
| Steady-state utilization | **99.2-99.99%** | — |

𝛿 ≈ **2%** — Iceberg hashing의 이론적 보장과 일치. Memory overhead 1% 미만.

### 4.4 Swapping Behavior [Table 4]

Memory footprint를 available memory의 100%→157%로 증가시키며 swapping 비교:

| Condition | Mosaic vs Linux |
|-----------|-----------------|
| Slightly oversubscribed | Mosaic이 더 많은 swapping (Linux가 ~1% 더 많은 memory 활용) |
| Moderately oversubscribed | Mosaic이 **최대 29% 적은** swapping |
| Heavily oversubscribed | Mosaic이 Linux와 동등 또는 우수 |

Green cells: Mosaic이 더 적은 swapping — 전체적으로 Mosaic ≈ Linux 또는 Mosaic 우수. Associativity restriction이 오히려 LRU의 worst-case(cyclic reference 등)를 회피하는 효과.

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2023ASPLOS-summarize/mosaic-pages-big-tlb-reach-with-small-pages.md|전체 요약 보기]]
