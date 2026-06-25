---
tags: [paper, 2024, 2024MICRO, topic/cache, topic/dram, topic/virtual-memory]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024MICRO-summarize/genie-cache-non-blocking-miss-handling-and-replacement-in-page-table-based-dram-cache.md"
---

# Genie Cache: Non-blocking Miss Handling and Replacement in Page-Table-Based DRAM Cache

**Venue:** 
**저자:** 

## 개요

### 1.1 이종 메모리 시스템의 대두

- 최근 메모리 집약적 애플리케이션(SPEC2006, GAPBS 등)의 증가로 고대역폭 on-package DRAM(HBM2)과 대용량 off-package 메모리(DDR4)를 결합한 이종 메모리 시스템이 제안됨 [10], [12], [41], [43].
- On-package DRAM을 캐시(DRAM Cache, DC)로 활용하는 설계는 크게 두 가지 접근 방식으로 분류됨: **HW-based**와 **PT-based (Page-Table-based)**.

### 1.2 HW-based DRAM Cache

- DC metadata(tag)를 on-package DRAM에 저장하며 확장성(scalability)을 제공 [24], [31], [38].
- 대표적인 예: Unison Cache [24] — large cache line(1KB), 4-way set-associative, non-blocking miss handling 지원.
- **근본적 한계:** 모든 LLC miss마다 DC controller가 physical-to-cache address translation을 위해 on-package DRAM의 DC metadata를 읽어야 하므로 추가 메모리 대역폭과 에너지 소모 발생 (Fig.1a).
- ACCORD [47]는 ECC unused bit에 metadata를 저장해 DC hit시 추가 대역폭 소모를 없앴으나, 여전히 small cache line size(64B)로 인해 spatial locality 활용이 제한적.

### 1.3 PT-based DRAM Cache

- DC metadata(tag)를 Page Table Entry(PTE)에 저장하고 TLB를 통해 접근 [22], [29], [37].
- Fully associative cache 구조 — PTE의 page frame number가 곧 cache frame number(CFN) 역할.
- DC hit 시 TLB에서 virtual-to-cache address translation이 추가 대역폭 없이 수행됨 → **ideal DC access time** 달성 (Fig.1b).
- **핵심 약점:** DC miss 시 OS exception handler를 호출해야 하며, 여기에는 page data copy, PTE 수정 등 고비용 연산이 포함됨.
  - NOMAD [26]는 MHA(Miss-Handling Architecture)를 도입해 page data copy를 non-blocking으로 전환했으나, 여전히 exception handler 호출 자체의 지연시간이 큼.
  - Multi-core 환경에서는 kernel synchronization 비용이 core 수에 비례하여 증가: single-threaded microbenchmark는 fault latency ∼0.4µs로 안정적이나, multi-threaded는 thread 수 증가에 따라 latency가 급증하고 throughput(FPMS)이 포화됨 (Fig.2b).

### 1.4 Motivation Data

- gem5 시뮬레이션(8 core, 0.4µs DC miss latency) 결과:
  - **High-class workloads** (DC MPMS 높음): NOMAD가 execution time의 51.5–69.0%를 kernel thread에서 소비. Exception handler가 application thread보다 더 많은 core time을 점유.
  - **Medium-class workloads**: 최대 43.7% execution time을 kernel thread에서 소비.
  - **Dirty page ratio**가 높은 workload(gems: 99.9% dirty ratio)는 blocking writeback으로 상당한 시스템 전체 오버헤드 발생 (Fig.3).
- 따라서 PT-based DC의 miss handling과 eviction을 모두 non-blocking으로 전환할 필요성 대두.

## 방법론

### 3.1 방법론

| 항목 | 구성 |
|------|------|
| **Simulator** | gem5 v21.1 (cycle-level), x86 out-of-order |
| **Processor** | 8 cores, 4GHz, 192 ROB entries, 8 issue width |
| **Cache** | L1: 32KB/2-way(priv), L2: 128KB/4-way(priv), L3: 8MB/8-way(shared) |
| **On-package DRAM** | HBM2, 1GB, 2GHz, 8 channels, 16 banks/rank |
| **Off-package memory** | DDR4-2400, 2 channels, 16 banks/rank, 2 ranks/channel |
| **Workloads** | SPEC CPU2006 11종 + GAPBS 4종, classified by DC MPMS |
| **Baselines** | Baseline(off-package only), Unison Cache, ACCORD, TiS, NOMAD, Ideal |

### 3.2 DC MPMS 기준 Workload 분류

| Class | DC MPMS 범위 | 대표 workload | 특성 |
|-------|-------------|---------------|------|
| Low | ≤2.3 | pr, sop, tc, mcf, ast, lbm | Miss overhead minimal |
| Medium | 3.3–9.2 | bc, libq, cc, gems, les | Moderate miss pressure |
| High | ≥10.6 | bfs, cact, bwav, sssp | Extreme miss pressure |

### 3.3 성능 결과

#### IPC Speedup (vs. Baseline, Fig.14)

| Class | Unison | ACCORD | TiS | NOMAD | Genie | Ideal |
|-------|--------|--------|-----|-------|-------|-------|
| Low | +8.7% | +15.3% | +22.0% | +17.5% | +25.3% | +28.0% |
| Medium | -5.2% | +5.1% | +12.1% | -3.8% | +38.7% | +30.5% |
| High | -12.3% | +3.5% | +8.5% | -20.1% | +31.2% | +27.0% |
| **Geomean** | **+8.7%** | **+10.3%** | **+15.3%** | **-2.2%** | **+31.5%** | **+28.5%** |

#### Key Findings

- **Genie vs. NOMAD: 51.3% speedup.** Non-blocking miss handling으로 40.2%, non-blocking writeback으로 추가 11.1% 향상.
- **High-class workloads:** NOMAD은 baseline보다 20% 느림. Genie는 31.2% 빠름.
- **Genie > Ideal:** libq, cc, gems에서 MHA의 page copy buffer가 즉시 data miss를 serving(각각 33.1%, 10.4%, 30.9% of DC read access) → DC access latency와 bandwidth 모두 절감.
- **On-package DRAM bandwidth:** Genie는 NOMAD보다 43.8% 더 많은 bandwidth 사용 — 더 높은 throughput으로 인한 자연스러운 결과.

#### Blocking vs. Non-blocking Writeback (Fig.16)

| Workload | Blocking WB app. stall | NB-WB app. stall | NB-WB speedup over B-WB |
|----------|----------------------|-------------------|------------------------|
| libq | >25% | negligible | +51.5% |
| gems | >25% | negligible | +34.2% |
| cact | >25% | moderate | +14.1% |

### 3.4 Power & Energy (Fig.17)

- **On-package DRAM Energy:** Genie < NOMAD — 더 짧은 execution time으로 static energy 절감.
- **Off-package memory:** 모든 DC scheme이 baseline 대비 에너지 절감 — 대부분의 access를 high-bandwidth on-package DRAM이 흡수.
- ACCORD는 small cache line → off-package access가 less sequential(row buffer hit 64.5% vs. 98.2%) → 더 많은 row activation → 더 높은 power.

### 3.5 Sensitivity Analysis

- **MMU-to-DCMU latency (20→320 cycles):** 성능 영향 <1% (Fig.18a). OOO execution window가 효과적으로 latency hiding.
- **TLB shootdown overhead (4→128µs) + eviction granularity (2K→32K pages):** granularity ≥16K pages이면 TLB shootdown overhead에 insensitive (Fig.18b).
- **Multi-socket:** DCMU 간 broadcast protocol로 coordination 가능. 320-cycle inter-DCMU latency도 1% 미만 성능 저하.

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

- **Simulation 기반:** gem5에 DCMU, MHA(MSHR/PSHR) 구현.
- **OS modification:** kernel data structure(PPD, CPD) 추가, eviction routine 구현 (batch page migration routine의 minor variant).
- **MMU modification:** DC miss detection logic, DCMU interface 추가.
- HW-based DC 대비 검증 노력이 현저히 적음 — memory controller 수정 불필요.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2024MICRO-summarize/genie-cache-non-blocking-miss-handling-and-replacement-in-page-table-based-dram-cache.md|전체 요약 보기]]
