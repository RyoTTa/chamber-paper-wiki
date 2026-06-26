---
tags: [paper, 2023, 2023MICRO, topic/cache, topic/dram, topic/storage, topic/virtual-memory]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023MICRO-summarize/utopia-fast-and-efficient-address-translation-via-hybrid-restrictive-and-flexible-virtual-to-physical-address-mappings.md"
---

# Utopia: Fast and Efficient Address Translation via Hybrid Restrictive & Flexible Virtual-to-Physical Address Mappings

**Venue:** 
**저자:** 

## 개요

**Motivation:** 기존 가상 메모리(virtual memory) 프레임워크는 virtual address를 임의의 physical address로 유연하게 매핑(flexible mapping)할 수 있도록 설계되어 있다. 이 유연성 덕분에 (i) 프로세스 간 데이터 공유, (ii) swap space 접근 회피 등의 핵심 VM 기능이 가능하다. 그러나 이러한 flexible mapping은 모든 virtual-to-physical 매핑을 저장하는 **page table (PT)**을 필요로 하며, 특히 data-intensive 워크로드에서 PT 접근이 심각한 성능 병목이 된다.

**구체적 수치 (Figure 3, 4, 7 기반):**
- 11개 data-intensive 워크로드(그래프 분석, DLRM, GenomicsBench 등)에서 baseline 1.5K-entry L2 TLB의 평균 MPKI는 **39**, 최대 **77**. 64K-entry L2 TLB로 확장해도 평균 MPKI는 **24**까지밖에 낮아지지 않음.
- Baseline radix page table walk (PTW) 평균 latency: **137 cycles** (x86-64 4-level radix tree).
- State-of-the-art ECH (Elastic Cuckoo Hashing)도 평균 PTW latency **86 cycles** 유지.
- PT 데이터가 **L2 cache 용량의 최대 38%**를 점유 (Radix: 33%, ECH: 57%).
- PTW로 인한 DRAM row buffer conflicts 증가: baseline 대비 **30% 증가**.
- Perfect L1 TLB 대비 baseline의 성능 headroom: **30%**.

**Strawman: All-Restrictive Mapping.** 주소 매핑 유연성을 제한(restrictive hash-based mapping; virtual address의 특정 bit로 physical address를 직접 결정)하면 translation overhead를 크게 줄일 수 있다. 그러나 전체 physical address space에 restrictive mapping을 적용하면 swap space 접근이 **2.2× (122%) 증가**하고, 프로세스 간 데이터 공유가 불가능해진다.

**핵심 인사이트:** flexible mapping과 restrictive mapping을 동일 시스템에서 **공존**시켜, 각 page의 translation cost에 따라 적절한 매핑 방식을 선택하자는 것.

## 방법론

### 3.1 Methodology

| 항목 | 구성 |
|------|------|
| **Simulator** | Sniper (CMU-SAFARI/Utopia, open-source) |
| **Core** | 4-way OoO x86, 2.6 GHz |
| **TLB** | L1 I-TLB: 128-entry 8-way; L1 D-TLB: 64-entry(4KB)+32-entry(2MB) 4-way; L2 Unified: 1536-entry 12-way |
| **Cache** | L1: 32KB I+D 8-way; L2: 2MB 16-way; L3: 2MB/core 16-way |
| **Memory** | 32GB DDR4-3200; tRCD=12.5ns, tCL=12.5ns |
| **Page sizes** | 4KB + 2MB (Transparent Huge Pages) |
| **RestSeg config** | 2 × 512MB RestSegs (4KB + 2MB), 16-way assoc |
| **Workloads** | 11개: GraphBIG(BC, BFS, CC, GC, PR, TC, SSSP), XSBench, GUPS(RND), DLRM(DLRM), GenomicsBench(GEN) |
| **Baselines** | Radix (4-level PT), POM-TLB (64K-entry SW L3 TLB), ECH (Elastic Cuckoo Hash, n=4), RMM (Redundant Memory Mappings), Perfect TLB |

### 3.2 Single-Core Results

| Metric | Radix | POM-TLB | ECH | RMM | Utopia | P-TLB |
|--------|-------|---------|-----|-----|--------|-------|
| **Speedup** | 1.00× | 1.03× | 1.08× | 1.13× | **1.24×** | 1.30× |
| **Translation Latency Reduction** | - | 16% | 39% | 15% | **69%** | - |
| **DRAM Row Buffer Conflicts** | 1.00 | +3% | +50% | -6% | **-20%** | -30% |
| **Memory Requests (MT)** | 1.00 | 0.92 | 1.62 | 0.81 | **0.12** | 0.00 |

Utopia는 Perfect TLB 성능의 **95%** 달성.

### 3.3 Multi-Core Results (Figure 22)

| Core count | ECH | POM-TLB | RMM | Utopia | P-TLB |
|------------|-----|---------|-----|--------|-------|
| 2-core | 1.15× | 1.14× | 1.12× | **1.28×** | 1.33× |
| 4-core | 1.17× | 1.14× | 1.14× | **1.28×** | 1.33× |
| 8-core | 1.17× | 1.14× | 1.19× | **1.24×** | 1.37× |

8-core에서 P-TLB 대비 **91%** 성능 달성.

### 3.4 Ablation Studies

**RestSeg Size Sensitivity (Figure 27):**
- 1MB: baseline과 동일 (costly-to-translate page 저장 불충분).
- 512MB: 2GB 대비 1.3% 이내 성능 → cost/performance trade-off 최적.
- 2GB: 최대 27% speedup.

**Hash Function Sensitivity (Figure 30):**
- Modulo hash = Prime Displacement = XOR-Mod = Mersenne Modulo → 모두 1.85× speedup.
- Modulo가 가장 낮은 hardware complexity.

**Context Switch Sensitivity (Figure 31):**
- CSQ 20ms~100ms: Utopia 평균 **24.9%** speedup (Radix 대비).
- CSQ 증가에도 성능 안정적.

**Non-Translation-Bound Workloads (Figure 29):**
- SPEC CPU2017 8종 (L2 TLB MPKI < 2): 평균 **< 0.05%** 성능 저하.

**Parallel RSW vs Serial (Figure 28):**
- Utopia-Parallel > Utopia-Serial: **+3%** speedup.
- Utopia-Serial도 Radix-Serial 대비 21% speedup → RSW 자체가 근본적 이점.

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

- **Simulator:** Sniper 기반 + TLB multi-page-size, radix PTW, PWC, buddy allocator, page migration latency 정밀 모델링 추가.
- **MMU 확장:** RestSeg walker FSM + 2×2KB TAR/SF SRAM caches.
- **Compiler:** LLVM 13.0.1 기반. Region partitioning + live-out register checkpointing + loop unrolling.
- **OS 수정:** Boot-time RestSeg creation (runtime contiguity search 방지), page allocation/free, migration, context switch 시 TAR/SF base register reload.
- **Area:** TAR/SF cache 추가로 **0.64% area overhead** (Intel Raptor Lake 대비, McPAT 45nm).
- **Power:** **0.72% power overhead** per core.
- **Code base:** 오픈소스 https://github.com/CMU-SAFARI/Utopia.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/storage.md|Storage]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2023MICRO-summarize/utopia-fast-and-efficient-address-translation-via-hybrid-restrictive-and-flexible-virtual-to-physical-address-mappings.md|전체 요약 보기]]
