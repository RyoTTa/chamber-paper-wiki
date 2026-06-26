---
tags: [paper, 2025, 2025MICRO, topic/cache, topic/disaggregation, topic/dram, topic/memory-tiering, topic/pim, topic/virtual-memory]
venue: ""
year: 2025
summary_path: "../paper-summaries/2025MICRO-summarize/beyond-page-migration-enhancing-tiered-memory-performance-via-integrated-last-level-cache-management-and-page-migration.md"
---

# Beyond Page Migration: Enhancing Tiered Memory Performance via Integrated Last-Level Cache Management and Page Migration

**Venue:** 
**저자:** Hwanjun Lee, Minho Kim, Yeji Jung, Seonmu Oh (DGIST), Ki-Dong Kang (ETRI), Seunghak Lee (Samsung), Daehoon Kim (Yonsei Univ.)

## 개요

### 1.1 Tiered Memory System의 대역폭 불균형 문제

CXL 기반 tiered memory는 local DRAM(near memory)과 CXL-attached DRAM(far memory)을 함께 사용하여 메모리 대역폭과 용량을 확장한다. 예를 들어 Samsung의 CXL 1.1 Type 3 device는 35 GB/s 대역폭을 제공하며, CXL-DRAM은 DDR5 대비 약 3배 적은 pin을 소모한다.

그러나 기존 **hotness-based page migration** (TPP[45], Memtis[37], HeMem[50])은 자주 접근되는 hot page를 near memory로 몰아넣는 전략을 취한다. 이로 인해:

- **Near memory bandwidth saturation**: bc workload에서 전체 대역폭의 96%가 near memory에서 발생, LULESH와 miniFE는 near memory의 67.6 GB/s 대역폭을 포화시킴
- **Aggregate bandwidth underutilization**: miniFE의 경우 memory interleaving 대비 33% 낮은 aggregate bandwidth 사용
- **성능 저하**: LULESH +39%, miniFE +33% execution time 증가 (interleaving 대비)

**Insight #1**: Hotness-based migration은 near memory로 트래픽을 집중시켜 aggregate bandwidth 활용을 저해하고 성능을 저하시킨다.

### 1.2 Migration-Only 접근의 느린 응답성 (Colloid의 한계)

Colloid[62]는 이러한 문제를 해결하기 위해 LLC miss latency 기반의 page migration을 제안했다. 그러나:

**느린 수렴 속도** (Table 1). GUPS workload에서 latency balancing을 위해 약 10 GB 데이터 마이그레이션이 필요하며:
- TPP+Colloid: **250초** (page table scanning의 느린 hotness tracking)
- HeMem+Colloid: **25초**
- Memtis+Colloid: **25초**

**동적 workload에서 실패**. DLRM workload에서 HeMem+Colloid는 5% 이내 latency difference 달성에 **20%만 성공**, 50% threshold에서도 16%가 실패한다 (Figure 2). Working set이 빈번히 변화하는 동적 workload에서 page migration의 느린 반응 속도가 치명적이다.

**Insight #2**: Migration-only memory traffic management는 늦은 적응 속도와 큰 오버헤드로 인해 동적 access pattern에 효과적으로 대응하지 못한다.

### 1.3 LLC Miss Latency 메트릭의 부적절성

Colloid는 LLC miss latency를 migration decision의 기준으로 사용한다. 그러나 Figure 3에서 보이듯, mcf workload에서 LLC miss latency가 급증하는 구간에서 오히려 **IPC가 향상**되는 역설이 발생한다. 원인은 L1D prefetch가 memory latency를 효과적으로 가리는 동안 LLC miss count를 증가시키기 때문이다. 이로 인해 **불필요하거나 해로운 migration**이 발생할 수 있다.

**Insight #3**: LLC miss latency는 caching/prefetching의 긍정적 효과를 포착하지 못해 부정확한 migration decision을 유도한다.

---

## 방법론

### 3.1 방법론 개요

| 항목 | 내용 |
|------|------|
| **Simulator** | ZSim[52] (host) + Ramulator[34] (memory), 4-level page table, 4KB pages |
| **System** | 16 OoO cores, 20-way LLC (2.5MB/core), DDR5-3200 (scaled-down from 128-core full system) |
| **Near memory** | 8 channels DDR5, 64 GB |
| **Far memory** | 8 channels DDR5 + latency penalty (CXL-100: +100ns default; CXL-200: +200ns; CXL-400: +400ns) |
| **Baselines** | TPP[45], Memtis[37], Memtis+Colloid[62], Interleave, W-Interleave |
| **Configs** | TierTune (cache-only), TierTune+ (cache + migration) |
| **Workloads** (20개) | SPECCPU2017 (6): bwaves, cactusBSSN, mcf, lbm, omnetpp, roms; GAPBS (6): BC, BFS, CC, CC_SV, PR, PR_SpMV; HPC (3): LULESH, miniFE, XSBench; AI (5): ResNet-50, VGG-16, DLRM, Llama inf./train |
| **Simulation** | 20B instructions/thread (warmup 40B), ≈25초 real-time equivalent |

### 3.2 Throughput 결과 (§5.2)

**Overall (CXL-100)** (Figure 6):
- TierTune (cache-only) vs TPP: **191.8%**, vs Memtis: **9.9%**, vs Memtis+Colloid: **8.5%** 평균 향상
- TierTune+ (cache+migration) vs TPP: **223.6%**, vs Memtis: **21.4%**, vs Memtis+Colloid: **19.6%** 평균 향상

**고대역폭 workload**: lbm_r (37.3%), cc_sv (37.4%), Llama Inf. (23.4%) — page migration overhead 회피 효과 극대화

**저대역폭 workload** (pr, pr_spmv): TierTune(cache-only)은 migration 대비 낮은 성능 — cache만으로는 큰 latency 차이 극복 불가 → TierTune+에서 migration 통합으로 보완 (+10.4% over TierTune)

**Bandwidth Utilization** (Figure 7):
| Policy | Total BW Utilization |
|--------|---------------------|
| TPP | 26.1% |
| Memtis | 69.7% |
| Memtis+Colloid | 70.4% |
| TierTune | 79.6% |
| TierTune+ | 84.4% |

**Migration Count** (Figure 8):
TierTune+는 TPP 대비 5.45×, Memtis 대비 8.97×, Memtis+Colloid 대비 9.76× 적은 migration 수행. 즉, **더 적은 migration으로 더 높은 성능** 달성.

**Latency Difference** (Figure 6):
- TPP: 284 ns, Memtis: 72 ns, Memtis+Colloid: 37 ns
- TierTune: 16 ns, TierTune+: **12 ns** (가장 균형 잡힌 latency)

### 3.3 Metric Ablation (§5.2, §5.3)

LLC miss latency를 L1 miss latency 대신 사용 시 (Figure 9):
- TierTune: 평균 9.8% 성능 저하 (cc_sv: 19.8%, lbm_r: 14.2%)
- TierTune+: 평균 더 큰 저하 (cc_sv: 23.2%, lbm_r: 18.6%) — 부정확한 latency 측정이 불필요한 migration trigger
- Memtis+Colloid도 7.2% 저하

→ **L1 miss latency의 우수성 입증**

### 3.4 Multi-Tenant (§5.3)

- Multiple applications (Figure 10): TierTune+ vs Memtis 14.18~37.24% 향상, vs Colloid 7.18~17.46%
- Per-application TierTune+: 추가 3-4% 향상 (minimal cache contention)
- Partitioned LLC (Figure 11): 4-way 이하 제외하고 안정적 성능, 2~3 application/VM 환경에서 Colloid 대비 2.9~26.0% 향상

### 3.5 Robustness (§5.4)

**Higher CXL Latencies** (Figure 12a):
- CXL-200/400: TierTune+는 Memtis 대비 5-10% 평균 향상
- Multi-node (CXL-400, 2/4 nodes): 15.4%/37.2% 추가 향상 — far memory 대역폭 증가 시 cache management + migration의 시너지

**Memory Bandwidth Scaling** (Figure 12b):
- BW ×2: TierTune+ vs Memtis +19.8%
- BW ×4: +7.4%, BW ×8: +3.2% — bandwidth 충분 시 latency gap 감소로 이득 축소
- 단, 미래 many-core (Intel Sierra Forest: 144 cores/8 channels = 18 cores/channel, Clearwater Forest: 288 cores/12 channels) 환경에서 bandwidth saturation이 심화되어 TierTune+의 중요성 증가

**Cache Size** (Figure 13):
- 0.5 MB/core: +2.5% (cache 너무 작음)
- 2.0~2.5 MB/core: +12.3%, +11.0% (optimal)
- 8.0 MB/core: +1.0% (cache hit rate 높아 latency gap 자체 축소)
- 작은 cache → migration 비중 증가, 큰 cache → cache management 비중 증가

**Interleaving vs TierTune** (Figure 14):
- Weighted interleave: 8% 향상 (static 6:4 ratio)
- TierTune: **15% 향상** (동적 적응)
- Latency difference: Interleave 64ns, W-Interleave 47ns, TierTune **14ns**

---

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

| Component | 내용 |
|-----------|------|
| **Hardware changes** | MSHR destination bits (12 bits/core), address comparator (1/core), LLC bit mask (32 bits) |
| **Simulator** | ZSim + Ramulator 통합, 4-level page table, 4 KB pages |
| **Latency monitor** | MSHR 기반, L1 miss latency per-node 측정, 50ms interval |
| **Cache allocator** | Way-based partitioning (Intel CAT/AMD CAE 확장) |
| **Migration** | Linux kswapd 비동기, 1 GB/s bandwidth, 최소 2-way per partition 보장 |
| **Multi-node** | Diffusion-based load balancing algorithm |

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2025MICRO-summarize/beyond-page-migration-enhancing-tiered-memory-performance-via-integrated-last-level-cache-management-and-page-migration.md|전체 요약 보기]]
