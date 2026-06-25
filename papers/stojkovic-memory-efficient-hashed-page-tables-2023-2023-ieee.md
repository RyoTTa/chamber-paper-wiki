---
tags: [paper, 2023, 2023HPCA, topic/cache, topic/nvm, topic/virtual-memory]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023HPCA-summarize/memory-efficient-hashed-page-tables.md"
---

# Memory-Efficient Hashed Page Tables

**Venue:** 
**저자:** 

## 개요

**Radix-tree page table의 확장성 한계:**
- x86-64에서 TLB miss 발생 시 PGD→PUD→PMD→PTE의 4-level sequential page walk 필요. 각 level이 이전 level의 결과값에 의존적 → memory-level parallelism 활용 불가.
- Intel Sunny Cove는 5-level page table 도입. NVM 등장으로 memory 용량 증가 추세 → scalability 문제 심화.

**Hashed Page Table (HPT)의 가능성:**
- VPN hashing → single memory access로 translation 가능 (collision 없을 시). IBM PowerPC, HP PA-RISC, Intel Itanium에서 구현 사례.
- 전통적 문제: (1) hash가 spatial locality 파괴, (2) hash tag 저장 공간 overhead, (3) collision handling 비용, (4) global HPT 설계 어려움 (page sharing, multiple page sizes 지원).

**최근 진전 (ECPT: Elastic Cuckoo Page Tables [Skarlatos et al., ASPLOS'20]):**
- Cuckoo hashing으로 conflict handling 간소화 — W-way set-associative HPT, 각 way는 다른 hash function.
- Per-process HPT, 작게 시작하여 동적 resize (Elastic Cuckoo Hashing). Upsize: old/new HPT 공존하며 gradual rehash.
- PTE Clustering + Compaction으로 locality 및 hash tag overhead 해결.

**ECPT의 남은 문제 — 대규모 연속 물리 메모리 요구:**
- 각 HPT way는 연속된 물리 메모리 영역에 할당되어야 함. 응용에 따라 way당 최대 **64MB**까지 필요.
- Fragmentation이 심한 서버(>0.7 FMFI)에서는 64MB 연속 할당 불가 → 프로그램 crash.
- 할당 latency: 4KB chunk ~4K cycles, 64MB chunk ~120M cycles (2GHz, FMFI 0.7).
- HPT 총 메모리도 radix-tree 대비 138%(THP 미사용) / 128%(THP 사용) 더 소비.

## 방법론

- **Simulator:** Simics full-system + SST framework + DRAMSim2. Intel SAE로 OS instrumentation.
- **Architecture:**
  - 8 OoO cores, 256-entry ROB, 2GHz
  - L1 I/D: 32KB, 8-way, 2 cycles / L2: 512KB, 8-way, 16 cycles / L3: 2MB/core, 16-way, 56 cycles
  - L1 DTLB: 64(4KB)+32(2MB)+4(1GB) entries / L2 DTLB: 1024(4KB)+1024(2MB)+16(1GB) entries
  - 4 page walkers / PWC: 3-level, 32 entries/level, 0.75KB
- **Memory:** 64GB DDR, 4 channels, 8 banks/channel, 200-cycle average access
- **ME-HPT config:**
  - Initial HPT: 128 entries × 3 ways per page size
  - Hash functions: CRC (2-cycle latency, 1.9×10⁻³ mm² area)
  - L2P table: 32 entries × 3 ways × 3 page sizes = 288 entries (1.16KB), 4-cycle latency
  - Chunk sizes: 8KB, 1MB (8MB, 64MB 미사용)
  - Occupancy thresholds: 0.6 upsize, 0.2 downsize
  - Memory fragmentation: 0.7 FMFI
- **Applications:** GraphBIG 8종 (BC, BFS, CC, DC, DFS, PR, SSSP, TC), GUPS (HPC Challenge), MUMmer (BioBench), SysBench Memory. 550M instructions/thread 측정.

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1 Methodology Overview

| 항목 | 내용 |
|------|------|
| Testbed | Simics + SST + DRAMSim2 full-system simulation |
| CPU | 8-core OoO, 2GHz, 256 ROB |
| Memory | 64GB DDR, 200-cycle avg latency |
| Baselines | ECPT (SOTA HPT), Radix-tree, with/without THP |
| Workloads | GraphBIG(8), GUPS, MUMmer, SysBench (11종) |
| Metrics | Max contiguous allocation size, speedup, page table memory, resize stats |

### 4.2 Memory Contiguity Savings (Fig. 8)

| Application | ECPT max contig | ME-HPT max contig |
|-------------|-----------------|-------------------|
| Graph apps (8종) | 16MB | 1MB or 8KB |
| GUPS, SysBench | **64MB** | **1MB** |
| **Geomean (no THP)** | 12.7MB | **92% 감소** |
| **Geomean (THP)** | - | **84% 감소** |

- ME-HPT가 요구하는 최대 연속 메모리는 L2P chunk size(=1MB)로 제한. 가장 demanding한 GUPS/SysBench도 64MB→1MB 감소.

### 4.3 Application Performance (Fig. 9)

| Config | vs Radix (no THP) |
|--------|-------------------|
| ME-HPT | **1.23×** (no THP), **1.28×** (THP) |
| ECPT | 1.14× (no THP), 1.22× (THP) |
| Radix+THP | 0.96× |

- ME-HPT는 ECPT 대비 **1.09×** (no THP), **1.06×** (THP) speedup.
- Speedup 원인: ME-HPT의 chunk 할당(8KB~1MB)은 ECPT의 way 전체 할당(최대 64MB)보다 훨씬 저렴.
- FMFI > 0.7에서 ECPT는 GUPS, SysBench 실행 불가 (64MB 할당 실패). ME-HPT는 정상 실행.

### 4.4 Page Table Memory Savings (Fig. 10)

| Metric | No THP | THP |
|--------|--------|-----|
| Average memory reduction | **43%** | **41%** |
| Absolute savings | 37MB avg | 20MB avg |
| In-place resize 기여 | ~75-80% | ~75-80% |
| Per-way resize 기여 | ~20-25% | ~20-25% |

### 4.5 Why Reducing Page Table Size Matters

GUPS, SysBench (no THP): ME-HPT는 192 L2P entries 사용. 메모리 절약 96MB가 없다면 288 entries 필요 → L2P capacity(192) 초과 → 8MB chunk 사용 강제 → 최대 contiguity 1MB→8MB 증가. 즉, **메모리 절약이 간접적으로 contiguity 요구를 낮춤**.

### 4.6 ME-HPT Characterization

**Resizing Operations (Fig. 11):**
- Way당 평균 10.6/10.5/9.9회 upsize (no THP). Per-way resizing으로 way 간 load balance.
- Steady state에서 평균 1.8회 upsize만 발생.
- 전체 실행 중 chunk size switch는 최대 1회 (8KB→1MB).

**Final Way Sizes (Fig. 12):**
- Way별 크기가 상이 → per-way resizing 효과 검증. GUPS/SysBench: way당 64MB.
- THP heavy user(GUPS/SysBench): 4KB page HPT는 initial size(8KB) 유지.

**Data Movement Reduction (Fig. 13):**
- In-place resize로 upsize 시 entry 이동 비율: 평균 **0.5** (이론적 예측과 일치, 50% entry in-place 유지).

**L2P Table Entries Used (Fig. 14):**
- Range: 11(TC) ~ 195(MUMmer). 평균 **52.5 entries**만 사용 → 288개 중 18%만 활용.

**Benefits for Small Apps (Fig. 15):**
- 1K/10K-node graph에서는 8KB+1MB chunk 지원이 1MB-only 대비 HPT way 메모리를 각각 8×, 16× 절약.

**Cuckoo Re-insertions (Fig. 16):**
- Probability of 0 re-insertions = **0.64**. Average = **0.7 re-insertions** per insertion/rehash.
- Negligible aggregate overhead.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2023HPCA-summarize/memory-efficient-hashed-page-tables.md|전체 요약 보기]]
