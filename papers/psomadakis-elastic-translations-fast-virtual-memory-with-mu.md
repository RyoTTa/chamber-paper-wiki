---
tags: [paper, 2024, 2024MICRO, topic/dram, topic/virtual-memory]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024MICRO-summarize/elastic-translations-fast-virtual-memory-with-multiple-translation-sizes.md"
---

# Elastic Translations: Fast Virtual Memory with Multiple Translation Sizes

**Venue:** 
**저자:** 

## 개요

### 1.1 Address Translation Wall

- Modern workload의 memory footprint 증가로 virtual memory subsystem의 address translation overhead가 계속 증가 [1].
- Large page는 TLB reach 증가, page walk depth 축소를 위한 대표적 해결책이나, x86은 2MiB와 1GiB 두 가지 크기만 지원.
- Large page의 단점: internal fragmentation, high fault latency, external fragmentation으로 인한 allocation difficulty [3–8].
- Workload footprint가 계속 커지면서 2MiB의 효과도 감소 [8].

### 1.2 ARMv8-A/RISC-V의 OS-assisted TLB Coalescing

- ARMv8-A와 RISC-V는 page table entry의 **contiguous bit**(bit 52)를 통해 OS가 N=16개 연속 page의 TLB entry를 하나로 병합(coalesce) 가능 [21], [22].
- 이를 통해 두 가지 **intermediate translation size** 지원:
  - **64KiB:** 16개의 연속된 4KiB PTE를 하나의 TLB entry로 병합
  - **32MiB:** 16개의 연속된 2MiB PMD를 하나의 TLB entry로 병합 (Fig.1)
- RISC-V Svnapot extension [22]은 coalescing factor를 page table entry에 인코딩하여 더 다양한 translation size 지원.
- **문제:** 이 intermediate translation size의 성능 잠재력이 system software 지원 부족으로 거의 활용되지 못함.

### 1.3 Motivation Data

ARMv8-A 서버(Ampere Altra)에서 HugeTLB를 통해 측정한 intermediate-sized translation의 성능 (Fig.2):

| Workload | 64KiB vs. 4KiB (native) | 64KiB vs. 4KiB (virt) | 32MiB vs. 2MiB (native) | 32MiB vs. 2MiB (virt) | 32MiB vs. 1GiB |
|----------|------------------------|----------------------|------------------------|----------------------|-----------------|
| Small-memory (astar, omnetpp, streamcluster) | +4–15% | +9–15% | N/A | N/A | N/A |
| Big-memory (canneal, svm, hashjoin) | N/A | N/A | +2–30% | +8–30% | close |

**핵심 발견:**
- 64KiB는 small footprint workload에서 2MiB에 근접한 성능을 내면서도 memory bloat이 적음.
- 32MiB는 2MiB가 cover하지 못하는 translation cost를 효과적으로 줄이며, 1GiB보다 훨씬 달성하기 쉬운 contiguity 요구사항을 가짐.
- Virtualized execution에서는 nested page walk로 인해 translation overhead가 증폭 → intermediate translation의 benefit이 더 커짐.

### 1.4 Translation Size Selection의 문제

- ARMv8-A SPE(Statistical Profiling Extension)로 TLB miss sampling을 수행한 결과, address space 내에 **narrow TLB miss hotspot**이 존재 (Fig.3a).
- 예: astar에서 단일 2MiB region이 전체 TLB miss의 ~5%를 차지.
- 기존의 page-based access frequency sampling [3], [4], [8]으로는 이런 fine-grained hotspot을 탐지하기 어려움 (Fig.3b).

## 방법론

### 3.1 방법론

| 항목 | 구성 |
|------|------|
| **Platform** | Ampere Altra Mt.Jade, 2×80 Neoverse N1 cores, 256GiB/node |
| **OS** | Linux v5.18 (+ v6.8 for mTHP), Ubuntu 22.04 |
| **Virtualization** | KVM + Qemu v7 |
| **Allocator** | gperftools tcmalloc (glibc malloc 대체) |
| **TLB Spec** | L1: 48-entry fully-assoc D-TLB/I-TLB, L2: 1280-entry 5-way unified |
| **Metrics** | Execution cycles, L2 TLB misses (HW PMU) |
| **Baselines** | 4KiB (baseline), Linux THP, mTHP (v6.8), HawkEye [4] (ARMv8-A port) |
| **Workloads** | 10종: astar, omnetpp, streamcluster, BFS, canneal, XSBench, SVM, BTree, hashjoin, GUPS |

### 3.2 Native Execution (No Fragmentation, Fig.8, Fig.9)

#### 성능 Speedup vs. 4KiB

| Category | Workload | THP | mTHP | HawkEye | ET | ET-offline |
|----------|----------|-----|------|---------|-----|------------|
| **64KiB-friendly** | astar | 1.47× | 1.56× | 1.56× | 1.47× | 1.56× |
| | omnetpp | 1.31× | 1.33× | 1.34× | 1.31× | 1.33× |
| | streamcluster | 1.10× | 1.10× | 1.10× | 1.10× | 1.22× |
| **2MiB-sufficient** | canneal | 2.12× | 2.48× | 2.48× | 2.17× | 2.10× |
| | XSBench | 1.45× | 1.58× | 1.58× | 1.51× | 1.49× |
| | BFS | 1.22× | 1.24× | 1.26× | 1.22× | 1.21× |
| **32MiB-beneficiary** | BTree | 1.64× | 1.85× | 1.85× | 2.04× | 1.99× |
| | SVM | 1.09× | 1.07× | 1.12× | 1.14× | 1.14× |
| | hashjoin | 1.12× | 1.08× | 1.12× | 1.24× | 1.24× |
| | GUPS | 1.09× | 1.07× | 1.09× | 1.22× | 1.21× |

**TLB Miss Reduction (vs. 4KiB):**
- ET: streamcluster 13.71%, astar ~81%, omnetpp ~81% → 64KiB translations으로 2MiB 없이도 상당한 TLB miss 감소.
- 32MiB-beneficiary: SVM 99.97%, hashjoin 99.29%, BTree 99.88% TLB miss reduction.
- ET-offline: Leshy hint로 정확히 hotspot에만 큰 translation 적용 → XSBench 93% 4KiB + 32MiB 조합으로 THP보다 적은 large page 사용.

### 3.3 Virtualized Execution (No Fragmentation, Fig.10)

Nested page walk의 추가 비용으로 translation overhead가 증폭 → ET benefit이 더욱 두드러짐.

| Workload | THP | HawkEye | ET | Speedup over THP |
|----------|-----|---------|-----|-----------------|
| astar | 1.24× | 1.24× | 1.24× | +0% |
| omnetpp | 1.14× | 1.14× | 1.14× | +0% |
| streamcluster | 1.07× | 1.08× | 1.08× | +1% |
| BFS | 1.76× | 1.72× | 1.88× | +7% |
| canneal | 1.51× | 1.49× | 1.58× | +5% |
| XSBench | 2.17× | 2.10× | 2.35× | +8% |
| BTree | 2.04× | 1.99× | 2.43× | +19% |
| SVM | 1.22× | 1.21× | 1.22× | +0% |
| hashjoin | 4.24× | 4.41× | 5.76× | +36% |
| GUPS | 2.60× | 2.50× | 3.29× | +27% |
| **Geomean** | — | — | — | **+30% average, +150% max (hashjoin)** |

### 3.4 External Fragmentation (Native, Fig.11)

FMFI(Free Memory Fragmentation Index) [64] 50%/99% 시나리오.

**50% Fragmentation:**

| Workload | THP | mTHP | HawkEye | ET | ET-offline | vs. THP |
|----------|-----|------|---------|-----|------------|---------|
| BFS | 1.34× | — | 1.41× | 1.42× | 1.54× | +6% |
| XSBench | 1.23× | — | 1.41× | 1.50× | 1.75× | +22% |
| SVM | 0.99× | — | 1.01× | 1.03× | 1.24× | +4% |
| hashjoin | 1.01× | — | 1.06× | 1.10× | 1.24× | +9% |

**99% Fragmentation:**

| Workload | THP | mTHP | HawkEye | ET | ET-offline | vs. THP |
|----------|-----|------|---------|-----|------------|---------|
| BFS | 1.08× | — | 1.08× | 1.08× | 1.08× | equal |
| canneal | 1.42× | — | 1.54× | 1.54× | 1.54× | +8% |
| XSBench | 1.08× | — | 1.08× | 1.34× | 1.47× | +24% |
| BTree | 1.23× | — | 1.24× | 1.24× | 1.24× | +1% |
| SVM | 1.00× | — | 0.99× | 1.01× | 1.29× | +1% |
| hashjoin | 1.01× | — | 1.02× | 1.10× | 1.24× | +9% |

**Large Page Usage Reduction:** ET는 THP 대비 large page 사용량을 **평균 50%** 감소시키면서도 동등 이상의 성능 유지.

**Online vs. Offline:** SVM의 경우 offline hint가 proactive migration을 가능하게 하여 spool-up effect 극복.

### 3.5 Component Breakdown (Fig.12)

- **Low fragmentation:** CoalaPaging이 성능 향상의 주 원인.
- **High fragmentation:** Leshy + CoalaKhugepaged가 주요 기여. BFS는 CoalaPaging이 64KiB translation으로 early address space region을 커버.
- 예: hashjoin, XSBench는 TLB miss가 address space tail에 집중 → THP의 linear scan으로는 탐지 불가 → Leshy가 정확히 탐지 → CoalaKhugepaged가 우선 promotion.

### 3.6 Overhead Analysis

**Fault Latency CDF (Fig.15):**
- 4KiB fault: ~1µs (lockless per-CPU page list)
- CoalaPaging 64KiB: 4KiB보다 높지만, mTHP 64KiB synchronous fault보다 낮음 (synchronous zeroing 회피).
- CoalaPaging 32MiB: THP 2MiB fault와 유사한 latency, synchronous 32MiB fault보다 **order of magnitude** 낮음 (2MiB fault-time allocation에 의존하므로 32MiB zeroing 불필요).

**Memory Bloat (Fig.9):**
- ET 32MiB는 THP 2MiB 대비 추가 memory bloat 없음.
- Streamcluster: 64KiB translation이 2MiB를 대체 → memory bloat 감소.

**TLB Miss vs. Access-bit Sampling (Fig.13):** 50% fragmentation에서 TLB miss sampling 기반 hint가 access-bit sampling보다 더 높은 정확도.

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

- **Linux v5.18** 기반, ~4,500 LoC kernel modification.
- ARMv8-A server에서 검증 (Ampere Altra, NVIDIA GH200).
- **Artifact:** GitHub 공개 (GPLv2), DOI: 10.5281/zenodo.13621499.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2024MICRO-summarize/elastic-translations-fast-virtual-memory-with-multiple-translation-sizes.md|전체 요약 보기]]
