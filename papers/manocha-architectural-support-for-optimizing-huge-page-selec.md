---
tags: [paper, 2023, 2023MICRO, topic/cache, topic/dram, topic/storage, topic/virtual-memory]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023MICRO-summarize/architectural-support-for-optimizing-huge-page-selection-within-the-os.md"
---

# Architectural Support for Optimizing Huge Page Selection Within the OS

**Venue:** 
**저자:** Aninda Manocha, Zi Yan, Esin Tureci, Juan L. Aragón, David Nellans, Margaret Martonosi (Princeton University / NVIDIA / University of Murcia)

## 개요

Irregular, memory-intensive 애플리케이션은 높은 TLB miss rate로 인해 상당한 address translation overhead를 겪는다. 2MB huge page는 TLB entry당 커버리지를 512배 증가시켜 miss rate를 낮추는 효과적인 수단이지만, 실제 시스템에서는 memory fragmentation과 memory pressure로 인해 huge page 사용이 제한된다.

**구체적 동기 데이터:**
- 2MB huge page로 모든 데이터를 backing하면 4KB 대비 **geomean 1.3× speedup**, TLB miss rate **2.9× 감소** (Figure 1).
- 그러나 memory가 **50% fragmented**일 때 Linux의 greedy THP 정책은 4KB baseline 대비 성능 향상을 거의 얻지 못함 (Figure 1).
- Linux의 synchronous promotion은 최대 **90초**까지 page fault latency spike 발생 가능.
- Prior work인 HawkEye[44]는 소프트웨어 기반 access coverage metric을 사용하지만, 256GB RAM 시스템에서 64M 페이지(4GB struct page metadata)를 스캔해야 하며, 30초 sleep 주기를 두어도 OS-level overhead가 큼.

**핵심 인사이트:** 모든 페이지가 huge page promotion에서 동일한 이득을 보는 것이 아니다. 저자들은 page reuse distance 분석을 통해 세 가지 access 유형을 식별:
1. **TLB-Friendly Accesses:** 4KB로도 TLB hit rate가 높아 promotion 이득 없음.
2. **HUBs (High reUse TLB-sensitive data):** 4KB에서는 TLB miss가 많지만 2MB에서는 reuse distance가 낮아 promotion 시 최대 이득.
3. **Low-Reuse TLB-Sensitive Accesses:** 페이지 크기와 무관하게 reuse distance가 높아 promotion 효과 낮음.

**목표:** HUBs를 식별하여 제한된 huge page 자원을 가장 효과적으로 사용하는 hardware-OS co-design.

---

## 방법론

### 3.1 Methodology

| 항목 | 내용 |
|------|------|
| **Testbed** | Intel Xeon E5-2667 v3 @ 3.20GHz, 2 sockets, 8 cores/socket, 64GB DDR4/socket |
| **OS** | CentOS 7, Linux v5.15 (modified) |
| **TLB** | L1 D-TLB: 64-entry (4KB) + 32-entry (2MB), L2 TLB: 1024-entry (4KB&2MB) |
| **PCC Config** | Per-core 128-entry, 40-bit tag, 8-bit counter, 30s interval |
| **Workloads** | BFS, SSSP, PageRank (GAP suite, 3 datasets each), PARSEC (canneal, dedup), SPEC2017 (mcf, omnetpp, xalancbmk) |
| **Memory footprint** | 10GB~38GB (graph), 252MB~5GB (SPEC) |
| **Baselines** | 4KB-only, Linux THP, HawkEye[44] |

**Two-step evaluation:**
1. **Offline Pin simulation:** TLB + PCC 동작 모델링, promotion candidate trace 생성.
2. **Real-system execution:** Trace 기반으로 kernel module이 실제 promotion 수행, wall-clock time 측정.

### 3.2 단일 스레드 성능 (Figure 5)

**Graph workloads:**
- Application footprint의 **1~4%만 huge page로 backing** 시:
  - BFS: **1.33×** speedup (이상적 huge page 성능의 77%)
  - SSSP: **1.19×** speedup (69%)
  - PageRank: **1.25×** speedup (73%)
- PTW rate: 평균 **18% 감소**.

**PCC vs HawkEye:**
- 모든 application에서 PCC가 HawkEye 능가. 주된 이유:
  1. HawkEye는 interval당 4096 페이지만 스캔 → promotion 수 제한.
  2. HawkEye의 access coverage metric은 spatial distribution만 고려, PTW frequency 정보 부재.
  3. HawkEye는 huge page region utilization이 threshold 미만이면 TLB miss가 많아도 promotion 불가.

**TLB-insensitive application (dedup, mcf):** 성능 저하 없음 → general-purpose system에서 항상 enable 가능.

### 3.3 PCC Size Sensitivity (Figure 6)

- 4→32 entry 구간에서 speedup 급격히 증가.
- 128-entry에서 diminishing return 진입, 모든 application에서 실질적 성능 포화.

### 3.4 Memory Fragmentation 조건 (Figure 7)

- **50% fragmentation:** PCC가 Linux 대비 **1.14×** speedup.
- **90% fragmentation:** PCC가 Linux 대비 **1.16×** speedup, HawkEye 대비 **1.15×**.
- PCC는 제한된 huge page 자원으로 highest-utility candidate만 골라내기 때문에 fragmentation에 강건함. 반면 Linux greedy 정책은 TLB-insensitive data에 huge page를 낭비.

**Demotion 효과:** 평가 workload에서는 phase change가 크지 않아 demotion으로 인한 추가 이득은 미미. (미래 multi-phase application에서 더 중요)

### 3.5 멀티스레드 성능 (Figure 8)

- 2 threads: **1.07~1.18×** speedup (이상적 성능의 85~94%)
- 4 threads: **1.04~1.13×** (85~93%)
- 8 threads: **1.04~1.12×** (86~92%)
- 단일 스레드 대비 speedup이 낮은 이유: (1) TLB shootdown 충돌 증가, (2) atomic operation serialization.
- **Highest PCC frequency 정책**이 round-robin보다 근소하게 우수 (load imbalance 해소).

### 3.6 멀티프로세스 성능 (Figure 9)

- **Case 1:** PageRank (TLB-sensitive) + mcf (TLB-insensitive): frequency 기반 정책이 PageRank에 집중 투자 → **1.1×** speedup (mcf 영향 없음).
- **Case 2:** PageRank + SSSP (둘 다 TLB-sensitive): round-robin이 더 나음 (frequency 기반 시 한쪽 starvation 가능). 16% footprint cover 시 PageRank **1.23×**, SSSP **1.19×** speedup.

---

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

- **Kernel:** Linux v5.15 기반, synchronous userspace promotion syscall 추가 (Google의 RFC patchset[58] 유사).
- **Simulation:** Intel Pin tool + custom TLB/PCC simulator.
- **보장 사항:** `randomize_va_space=0`으로 simulation과 real-system 간 virtual address 일치 보장, `numactl`로 NUMA effect 제거.
- **PCC HW:** 128-entry fully-associative, 768B storage → 상용 구현 feasibility 높음 (area < 1% of L1D).

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/storage.md|Storage]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2023MICRO-summarize/architectural-support-for-optimizing-huge-page-selection-within-the-os.md|전체 요약 보기]]
