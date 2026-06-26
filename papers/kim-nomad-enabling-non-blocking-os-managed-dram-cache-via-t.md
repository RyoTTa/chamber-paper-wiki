---
tags: [paper, 2023, 2023HPCA, topic/cache, topic/dram, topic/virtual-memory]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023HPCA-summarize/nomad-enabling-non-blocking-os-managed-dram-cache-via-tag-data-decoupling.md"
---

# NOMAD: Enabling Non-blocking OS-managed DRAM Cache via Tag-Data Decoupling

**Venue:** 
**저자:** 

## 개요

Heterogeneous memory system에서 on-package DRAM(HBM)을 cache로 활용하는 DRAM cache(DC) 설계는 크게 HW-based와 OS-managed 방식으로 나뉜다.

**HW-based DRAM cache (TiD: Tags-in-DRAM):**
- Non-blocking miss handling 지원 — MSHR(Miss Status/Information Holding Register)을 통해 여러 outstanding miss를 동시 처리 가능.
- 그러나 DC tag/metadata를 on-package DRAM에 저장하므로, 매 DC access마다 metadata read/write를 위해 on-package DRAM bandwidth를 소비 → effective DC cycle time 증가 → 성능 저하.
- 예: 4-way set-associative, 1KB cache line, LRU policy.

**OS-managed DRAM cache (TDC: Tagless DRAM Cache):**
- PTE/TLB에 DC tag를 저장 → TLB hit 시 바로 cache address(CA) 획득 → **ideal DC access time** 제공 (metadata transfer overhead 없음).
- 그러나 **blocking cache** — DC miss 발생 시 OS가 cache fill을 완료할 때까지 application thread가 수천 cycle 동안 stall → 심각한 miss penalty.
- FIFO replacement + fully-associative 구조 (HW-based 대비 23% 적은 DC miss).

**핵심 통찰:** 두 방식의 장점을 결합하지 못하는 근본 원인은 **coupled tag-data management** — 기존 OS-managed DC는 tag hit = data hit을 보장해야 하므로, tag update 후 cache fill 완료까지 thread를 block해야 함.

**워크로드 분류 (RMHB 기준):**
| Class | RMHB (GB/s) | 워크로드 예시 |
|-------|-------------|-------------|
| Excess | >31.7 (off-package bandwidth 초과) | cact, sssp, bwav, les |
| Tight | 12.2~26.5 | libq, gems, bfs |
| Loose | 3.4~12.2 | cc, lbm, mcf, bc |
| Few | <1.7 | ast, pr, sop, tc |

TDC는 Excess-class에서 성능 저하 (43% stall rate), TiD는 모든 class에서 metadata bandwidth overhead로 DC access time 증가.

## 방법론

- **Simulator:** gem5 (SE-mode) + DRAMsim3, OS emulation 기능 수정 (multi-level TLB, address translation, memory management)
- **Processor:** 8 OoO cores, 4GHz, 192 ROB entries, 8-issue width
- **On-package DRAM:** HBM2, 2GHz, 128-bit, 64B burst, 16 banks/rank, 1 rank/channel, 8 channels, 1GB total
- **Off-package memory:** DDR4-3200, 64-bit, 2 channels, 2 ranks/channel
- **NOMAD config:** Front-end 400-cycle tag management, 16 PCSHRs, 4 sub-entries/PCSHR, no write buffer
- **TiD config:** 1KB cache line, 4-way, LRU, 32 MSHRs, 4 sub-entries/MSHR, 32 write buffers, 64B dirty tracking
- **Shared resource:** CPD array 등 약 2MB (on-package DRAM 상주)
- **Workloads:** SPEC2006 9종 + GAPBS 6종, fast-forward 후 500M instructions/core (총 4B instructions)

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1 Methodology Overview

| 항목 | 내용 |
|------|------|
| Testbed | gem5 + DRAMsim3 cycle-level simulation |
| CPU | 8-core OoO, 4GHz |
| DRAM Cache | 1GB HBM2 (on-package) |
| Main Memory | DDR4-3200 (off-package) |
| Baselines | Baseline (DC 없음), TiD (HW-based), TDC (blocking OS-managed), Ideal (zero-latency OS) |
| Workloads | SPEC2006 + GAPBS, 4 classes (Excess/Tight/Loose/Few) |
| Metrics | IPC, DC access time, bandwidth usage, stall rate |

### 4.2 IPC 및 DC Access Time (Fig. 9)

- **Excess-class:** NOMAD는 Baseline 대비 유의미한 speedup, TDC는 거의 개선 없음. TiD는 metadata bandwidth로 DC access time 증가.
- **Tight-class:** NOMAD > TDC > TiD 순. bfs(낮은 spatial locality)에서도 NOMAD 우수.
- **Loose-class:** NOMAD ≈ Ideal (5% 미만 stall rate). TDC도 양호(15% stall).
- **Few-class:** NOMAD ≈ TDC ≈ Ideal. TiD는 metadata overhead로 Baseline보다 열등(tc).
- **Overall:** NOMAD는 TDC 대비 **IPC 16.7% 향상**, TiD 대비 **25.5% 향상**. Application stall cycle **76.1% 감소** (TDC 대비).

### 4.3 Bandwidth Usage 및 Row Buffer Hit Rate (Fig. 10)

- TiD: metadata access가 on-package DRAM bandwidth의 상당 부분 소비. Data access + cache-fill + writeback + metadata access가 혼재.
- TDC/NOMAD: metadata access 없음 → bandwidth를 data access와 cache-fill에 집중.
- NOMAD는 TDC보다 page granularity(4KB)로 인한 row buffer hit rate 우위 유지.

### 4.4 Stall Rate 및 Tag Management Latency (Fig. 11)

- **Excess-class:** TDC stall rate ~43%, NOMAD는 tag management contention(shared critical section)으로 latency 증가하나 여전히 TDC보다 현저히 낮은 stall.
- **Tight-class:** TDC ~29% stall. NOMAD는 tag miss tolerance + near-ideal DC access time으로 최고 성능.
- **Loose-class:** NOMAD <5% stall (적은 DC tag miss + 적은 contention).
- NOMAD의 tag management latency는 contention으로 인해 baseline 400 cycles보다 높을 수 있으나(최대 3200 cycles), back-end data management offload가 이를 상쇄.

### 4.5 Sensitivity: Number of PCSHRs (Fig. 12-14)

- Excess-class: 8 PCSHRs에서 near-max 성능, 그 이상은 off-package bandwidth가 bottleneck → core 수 증가에도 PCSHR 추가 불필요.
- Tight-class: 4 PCSHRs로 충분. Bursty-RMHB workload(libq, gems)는 16→32 PCSHRs에서 tag management latency 48% 감소, 성능 11.3% 향상.
- Loose/Few-class: 1~2 PCSHRs로도 충분.

### 4.6 Area-optimized Design (Fig. 15)

Page copy buffer(4KB × PCSHR 수)가 주요 area overhead. Buffer 수를 줄이고 PCSHR 수를 늘리는 비대칭 구성 가능. Bursty workload에 대해 (32 PCSHRs, 8 buffers) 구성이 (16, 8) 대비 우수.

### 4.7 Centralized vs Distributed (Fig. 16)

FIFO allocation의 균등 분배 효과로 centralized와 distributed back-end가 유사한 성능. 동일 hardware cost로 구현 가능.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2023HPCA-summarize/nomad-enabling-non-blocking-os-managed-dram-cache-via-tag-data-decoupling.md|전체 요약 보기]]
