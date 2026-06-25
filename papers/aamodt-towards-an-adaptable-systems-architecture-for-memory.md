---
tags: [paper, 2023, 2023ASPLOS, topic/cache, topic/dram, topic/memory-tiering, topic/rowhammer, topic/storage, topic/virtual-memory]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023ASPLOS-summarize/towards-an-adaptable-systems-architecture-for-memory-tiering-at-warehouse-scale.md"
---

# Towards an Adaptable Systems Architecture for Memory Tiering at Warehouse-Scale

**Venue:** 
**저자:** 

## 개요

Google의 WSC (Warehouse-Scale Computing) 환경에서 DRAM은 infrastructure spend의 큰 비중을 차지하며, CPU/storage보다 빠르게 증가 — 일부 추정에 따르면 DRAM이 cost-effective compute capacity의 제한 요소가 될 전망. 해결 방안으로 conventional DRAM (tier1)의 일부를 더 저렴하지만 느린 memory media (tier2)로 교체하는 **directly-addressable tiered memory system**을 탐색.

**기존 접근과의 차이:**
- **Virtual memory/swap:** 매우 큰 swap device가 backing store 역할. Page fault 기반 → access latency orders of magnitude 높음.
- **zswap:** DRAM 내 압축 page 저장. 여전히 fault-first access.
- **Intel Optane "Memory Mode":** DRAM이 L4 cache 역할 — OS-transparent, application-specific 정책 불가.
- **NUMA balancing:** Tier 간 penalty 차이가 tiered memory보다 훨씬 작아 hot page mischaracterization 영향이 제한적.

TMTS의 tiered memory는 두 tier 모두 directly addressed + cached → **no page faults on access**. 대신 page placement와 virtual-to-physical mapping을 지속적으로 관리하여 frequently accessed (hot) pages를 tier1에, least accessed (cold) pages를 tier2에 유지.

**WSC 환경의 고유한 도전 과제:**
- Highly multi-tenant: HILS (High Importance Latency Sensitive)와 non-HILS (batch, ML training 등)가 co-located.
- Machine당 수백 개 task, cluster당 수만 대 machine, heterogeneous tier2 hardware.
- Workload behavior: daily change 또는 weeks-long stable 후 sudden change.
- Memory는 inelastic → OOM은 unacceptable. Conservative provisioning으로 rarely-needed memory의 offload 기회.

**설계 목표:** Fleet-wide memory cost reduction (per-machine tiered replacement ratio × fleet-wide 2-tier machine fraction)을 maximization하면서, overall machine throughput 유지 + 개별 application SLO 충족.

## 방법론

### 2. Machine-Level Proxy Metrics

TMTS는 tiering stack 자체를 평가할 두 가지 proxy metric 정의:

| Metric | 정의 | 목적 |
|--------|------|------|
| **STRR** (Secondary Tier Residency Ratio) | Allocated memory 중 tier2에 상주하는 비율 | Utilization impact proxy. Target: tier2 hardware capacity ratio (25%)에 근접 |
| **STAR** (Secondary Tier Access Ratio) | 전체 memory access 중 tier2에 상주하는 page로의 access 비율 | Performance degradation proxy. Lower = better |

**Operational target:** STAR median <0.5%, p95 <1.5% 유지하며 STRR이 25%에 근접 (memory utilization >75%일 때). Figure 1은 STAR와 application performance 간 상관관계: STAR <0.5%에서 aggregate performance degradation <5%.

### 3. Base Architecture for TMTS

TMTS는 4-layer architecture (Figure 2):

```
┌─────────────────────────────────┐
│ Cluster: Borg Scheduler         │ ← tier-aware scheduling hints
├─────────────────────────────────┤
│ Userspace: ufard (policy daemon)│ ← promotion/demotion policies,
│           Borglet (node agent)  │    perf events, BPF events
├─────────────────────────────────┤
│ Kernel: page access scan,       │ ← cold page detection (A-bit),
│         page migration,         │    promotion/demotion mechanisms
│         perf/PEBS sampling      │
├─────────────────────────────────┤
│ Hardware: NUMA nodes            │ ← DRAM (tier1) + Low-cost Memory (tier2)
└─────────────────────────────────┘
```

Linux는 tier2 memory device를 CPU-less NUMA node로 enumerate. TMTS는 memory node 위에 새로운 tiered hierarchy 정의 (2-tier 현재, CXL 등 multi-tier 확장 가능).

**Policy-mechanism separation:** 정책은 userspace (ufard/Borglet), 메커니즘은 kernel — production scale에서만 발견되는 subtle behavior에 대한 rapid iteration 가능.

### 3.1 Cold Page Detection and Demotion

Page demotion: tier1의 least frequently accessed pages를 식별하여 tier2로 이동.

- **Cold detection:** Threshold t — t초 동안 access 없었던 page = cold. Kernel daemon의 periodic page A-bit scan으로 idle age 판별.
- **Cold memory 분포 (Figure 3):** 6개 cluster의 aggregate workload에서 2m threshold 기준 28~42%가 cold. 대부분의 job이 25% tier2 설계 지점을 충분히 지원하나 job별 편차 큼.
- **Per-application demotion age:** ufard가 각 task의 cgroup에 cold age threshold 설정. HILS = 8m, non-HILS = 2m (8m_2m 정책).
- **Cold age histogram:** Kernel이 userspace에 inter-access interval frequency distribution 제공 → ufard가 adaptive policy 조정에 활용.
- **Demotion constraints:** (a) Swap-backed pages만 demotion candidate (anonymous + tmpfs; file-backed <2%). (b) No direct allocations to tier2 — task memory는 항상 tier1에 할당 후 demotion으로 tier2 채움.

### 3.2 Hot Page Promotion

Directly-addressed tier2는 page fault 없이 access 가능 → fault-based 접근 불가. TMTS는 **two-pronged proactive detection**:

**A. PMU-based Sampling (PEBS on Intel):**
- LLC miss event sampling, tier2 load로 filtering된 precise event 사용 (store는 HW 미지원).
- Sampling rate: tier2 memory load의 1%. 식별된 모든 page 즉시 promotion.
- Median promotion latency: <1 second (vs. 13~25s for scan-only).

**B. Periodic A-bit Scanning:**
- Hot scan period: 30초. Page hot age = 연속 access된 scan period 수.
- Base policy: 2회 이상 연속 hot scan period에서 access된 page promotion (60s+PMU).
- TLB invalidation 없이 scan → accuracy tradeoff 있으나 실제 영향 미미.

**Thrashing 방지:** Demotion 전 page가 extended period (O(min)) 동안 access 없었음을 보장 → short-lived allocation의 promotion-demotion ping-pong 방지.

### 3.3 Policy Management

ufard는 `perf_event_open()`으로 PMU sampling 설정. 소형 BPF program을 kernel에 설치하여 in-kernel page A-bit scanner의 tier2 hot page age + address를 per-NUMA node BPF ring buffer로 수집. Promotion은 custom system call을 통해 수행.

### 3.4 Hardware Constraints

Tier2 = Intel Optane Persistent Memory variant (Cascade Lake):
- Idle read latency: ~325 ns (DRAM의 3.5×).
- Bandwidth: DDR4의 <1/10 (Table 1: Sequential Read 6.9 GB/s, Random Write 0.5 GB/s).
- Tier2 DIMM이 DRAM과 memory channel 공유 → bandwidth saturation 시 DRAM latency도 영향.
- **정책 제약:** (a) No direct allocations to tier2. (b) No demotions to remote socket tier2 (NUMA jailing — remote QoS feedback signal의 cross-socket latency로 인해 효과 급감).

## 핵심 기여

1. **최초의 production-scale non-faulting tiered memory system 분석.** 2년간 수천 개 production service를 성공적으로 serving. 25% DRAM replacement → <5% performance degradation.
2. **STAR/STRR proxy metric framework:** Machine-level에서 tiering stack 효과성을 정량화하고, fleet-wide cost reduction과 application SLO를 연결하는 추상화 제공.
3. **Fault-less promotion의 설계 공간 개척:** PMU-based sampling이 scan-only 대비 promotion latency를 orders of magnitude 단축하고 STAR를 45% 감소. Page fault 없는 directly-addressable tier2의 장점 입증.
4. **WSC scale에서의 system challenge 규명:** (a) Hugepage와 tiering의 상충 — access fragmentation 문제, (b) Hardware QoS constraint (NUMA jailing), (c) Noisy neighbor 문제.
5. **Adaptive cross-layer policies:** Borg cluster scheduling hints, per-application demotion age, application-hinted allocation — vertical integration으로 tail performance impact 완화.
6. **미래 방향:** CXL 기반 memory로 hardware constraint 완화, compiler/profile-guided optimization으로 access fragmentation 해결, 더 aggressive한 tier2 replacement ratio 가능.

## 주요 결과

### 방법론 개요

| 항목 | 내용 |
|------|------|
| **Testbed** | Google production fleet. 2-socket Intel Xeon + DDR4 tier1 + Optane tier2. 2200 experimental (2-tier, 75% DRAM + 25% Optane), 1000 control (1-tier, 100% DRAM) |
| **Deployment** | 6개 geographically distributed clusters, 2년간 production serving |
| **A/B Testing** | Live production traffic. Borg scheduler가 동일 algorithm으로 양쪽에 job 배치. 4주 typical duration. 100K+ distinct jobs (HILS 25%, non-HILS 75%) |
| **Metrics** | STRR, STAR, Memory Utilization, IPC (Instructions Per Cycle) difference, Application throughput, TLB misses, DRAM latency |
| **Baselines** | 1-tier all-DDR4 control machines. 다양한 demotion/promotion policy 비교 |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]
- [[paper-wiki/concepts/storage.md|Storage]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2023ASPLOS-summarize/towards-an-adaptable-systems-architecture-for-memory-tiering-at-warehouse-scale.md|전체 요약 보기]]
