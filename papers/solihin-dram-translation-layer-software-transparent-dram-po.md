---
tags: [paper, 2023, 2023ISCA, topic/cache, topic/disaggregation, topic/dram, topic/memory-tiering, topic/storage, topic/virtual-memory]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023ISCA-summarize/dram-translation-layer-software-transparent-dram-power-savings-for-disaggregated-memory.md"
---

# DRAM Translation Layer: Software-Transparent DRAM Power Savings for Disaggregated Memory

**Venue:** 
**저자:** Wenjing Jin, Wonsuk Jang, Haneul Park, Jongsung Lee, Soosung Kim, Jae W. Lee (Seoul National University, Samsung Electronics)

## 개요

### 1.1 Disaggregated Memory와 Power Challenge

Memory disaggregation은 CXL(Compute Express Link) 기반으로 여러 compute node가 대용량 pooled memory를 공유하는 유연한 아키텍처. AMD Genoa, Intel Sapphire Rapids 등 최신 CPU가 이미 CXL memory expansion을 지원.

**Power 문제 심각성:**
- Meta 보고서 [57]: DRAM power는 datacenter system total power의 **38%** 도달 전망.
- Terabyte-scale disaggregated DRAM 도입 시 compute-to-memory capacity ratio 하락 → DRAM power 비중 더욱 증가.
- DRAM capacity utilization은 datacenter에서 평균 **40-60%** 에 불과 [34, 38, 46, 52]. Microsoft Azure VM trace 분석에서도 평균 <50% 확인 (Fig. 1).

### 1.2 기존 DRAM Power Management의 한계

JEDEC 표준 저전력 상태:
- **Self-Refresh (SR):** Data retention 유지, standby power의 **10-20%** 소비, exit latency 수백 ns.
- **Maximum Power Saving Mode (MPSM):** Data retention 없음, standby power의 **3.4-6.8%** 소비, exit latency 수백 ns.

기존 방식의 deployment 장벽:
- Fine-grained rank interleaving(rank-level parallelism 최대화용)이 rank-level power-down을 방해.
- 모든 기존 제안(RAMZzz [59], GreenDIMM [34], ESKIMO [27], RTC [28], DimmStore [30] 등)은 OS, memory controller(MC), 또는 DRAM device 자체의 **intrusive modification** 필요 → DRAM vendor, CPU vendor, datacenter operator 간 multi-party coordination 요구 → 현실적 deployment 어려움.

### 1.3 Rank-level Parallelism의 Diminishing Returns

CloudSuite 10종 benchmark 실측 결과 (Fig. 2): 2-rank vs 8-rank configuration에서 평균 성능 저하 **0.7%** 에 불과. Bank/channel-level parallelism만으로도 충분한 수준. CXL의 long-latency 환경에서는 이 효과 더욱 미미 (Fig. 5: 1.4%).

## 방법론

### 3.1 Address Translation (Fig. 4)

**Segment granularity:** 2MB segment. (4MB 대비 cold segment 비율 61.5% vs 33.2%로 우수 — Fig. 10)

**Two-level Segment Mapping Cache (SMC):**
- L1: 64-entry fully-associative
- L2: 1024-entry 4-way set associative
- L1 miss rate: 14.7%, L2 miss rate: 15.4%

**Miss path — 3-level table walk:**
- Host Base Address Table (SRAM): Host ID → AU table base
- AU Table (SRAM): AU ID → AU base address (AU=2GB, 최소 vMemory 단위)
- Segment Mapping Table (DRAM): AU offset → DSN (HSN-to-DSN mapping)

**Latency 영향:** AMAT = 214.2ns (vanilla CXL 210ns + 4.2ns) → execution time 증가 **0.18%**.

### 3.2 DRAM Physical Address Bit Mapping (Fig. 6)

Channel bits를 segment offset 바로 위에 배치하여 channel interleaving 적용. Rank bits를 MSB로 배치하여 rank interleaving 미적용 → rank-level power-down 가능. 1TB CXL device 기준: 4 channels × 8 ranks/channel.

### 3.3 Rank-level Power-down (첫 번째 Power-saving 기법)

**동작 방식 (Fig. 7):**
1. VM deallocation 발생 → unallocated capacity 확인.
2. 활용률 가장 낮은 **rank-group**(동일 rank index × 전체 channel)을 victim으로 선정.
3. Victim rank-group의 live segment를 다른 rank-group으로 migration.
4. Victim rank-group 전체를 **MPSM** 진입 → background power 최소화.
5. 새 VM allocation 시 capacity 부족하면 MPSM exit → allocation (기존 VM 영향 없음 — initialization 단계에서만 발생).

**Virtual rank-group:** Hotness-aware self-refresh로 인해 channel별 idle rank index가 상이 → 서로 다른 rank ID의 idle rank들을 virtual rank-group으로 묶어 MPSM 진입.

**예시:** 24GB segment migration 시간: **1.3초** (VM configuration interval 대비 극히 짧음).

### 3.4 Hotness-aware Self-refresh (두 번째 Power-saving 기법)

MPSM 진입 rank 외에 active rank에서 추가 power saving. 기본 아이디어: cold segment를 victim rank로 수집 → SR 진입.

**Migration Table (SRAM):** 각 segment entry에 3개 field — access bit, rank number, segment number. CLOCK 알고리즘 유사 방식으로 cold/hot swap plan 관리. TSP(Target Segment Pointer)로 cold segment 탐색.

**Phase 1 — Profiling (Fig. 8):**
1. 각 channel에서 최소 access rank를 victim으로 선정.
2. Victim rank 내 hot segment access 시, TSP가 가리키는 target rank의 cold segment와 rank/segment number swap (실제 데이터 이동은 아직 없음).
3. Access bit=1이면 0으로 reset 후 TSP 이동 (CLOCK 방식).
4. Timeout 40ns (단일 DRAM access latency 미만) 도달 시 다음 target rank로.
5. Profiling time threshold 내(기본 50ms) hypothetical victim rank에 access 없으면 migration phase로 전환.

**Phase 2 — Migration:**
Victim rank 내 hot segment와 target rank 내 cold segment 간 실제 data swap → segment mapping table 갱신 → segment mapping cache invalidation → victim rank를 SR 진입.

**Exit/Re-entry:** SR 중인 rank의 segment access → standby 복귀 → profiling 재시작 → 대부분 segment가 여전히 cold이므로 빠른 재진입.

### 3.5 Data Migration Mechanism

**Two queues per channel:** Foreground request queue + migration queue. Migration queue는 foreground queue가 idle일 때만 issue → foreground 성능 보장.

**Atomicity:** Segment migration을 cache line-sized request로 분할 수행. Internal counter로 진행 추적. Foreground write request가 migration 중인 segment에 도달 시: completion bit 확인 → 이미 migrated 완료면 new DSN으로, 진행 중이면 retry (3회 초과 시 migration queue tail로 재배치).

**Data structures (DRAM reserved area):** Allocated segment queue, free segment queue, reverse mapping table (DSN→HSN).

## 핵심 기여

DTL은 CXL memory device 내에서 HPA→DPA address translation layer를 도입하여 **OS, hypervisor, host MC, DRAM device 모두 수정 없이** 두 가지 rank-level power saving 기법을 실현. Rank-level power-down: 31.6% energy saving(1.6% perf cost), hotness-aware self-refresh: 추가 최대 14.9% saving. 핵심 contribution: (1) disaggregated memory 환경에서 FTL-inspired indirection의 최초 적용, (2) VM deallocation 기반 rank consolidation을 통한 MPSM 활용, (3) CLOCK-inspired profiling으로 cold/hot page 분리 및 SR 진입. 향후 reliability, availability, security 등 flexible memory management로의 확장 가능성 제시. Terabyte-scale CXL 디바이스까지 확장 가능한 경량 설계.

## 주요 결과

### 4.1 Methodology

| 항목 | 내용 |
|------|------|
| **Server** | Intel Xeon Gold 6258R 28-core @ 2.7GHz, DDR4-2933 |
| **DRAM** | 1TB (384GB used), 6 channels, 2 DIMMs/channel |
| **CXL emulation** | Quartz [54], latency 210ns |
| **VM traces** | Microsoft Azure public dataset, 400 VMs, 6시간 schedule |
| **Benchmarks** | CloudSuite 10종 (data-analytics, caching, serving, graph, web 등) |
| **Simulator** | Custom trace-driven (20B instructions/workload) |
| **Power measurement** | Intel PCM |
| **Metrics** | DRAM energy, execution time overhead, segment reuse distance |

### 4.2 Rank-level Power-down 결과 (Fig. 12)

- DRAM energy **31.6%** 감소
- Execution time overhead: **1.6%** (rank interleaving 해제 1.4% + translation 0.18% + migration negligible)
- 2-rank active configuration에서 DRAM power **65.2%** 감소 (baseline 8-rank 대비)
- Background power **35.3%** 감소, total power **32.7%** 감소 (Fig. 13)

### 4.3 Hotness-aware Self-refresh 결과 (Fig. 14)

- 추가 DRAM energy saving: **최대 14.9%** (8-rank, allocated 304GB)
- 208GB allocated 6-rank: 20.3% 추가 saving (warmup 10-60초 후 stable phase)
- 240GB allocated: channel당 unallocated가 rank-pair capacity의 50% 미만 → cold segment 수집 어려움 → 일부 workload 미진입
- SRAM access power: DRAM energy의 <0.1%, SR exit latency: warmup time의 <0.001% → 무시 가능

### 4.4 통합 결과 (Fig. 15)

Rank-level power-down + Hotness-aware self-refresh 병행 시:
- 첫 기법으로 rank-group 1개 MPSM 진입 → 20.2% saving
- 두 번째 기법으로 추가 **5.4-12.1%** → total **25.6-32.3%** saving
- 8-rank(all active): hotness-aware self-refresh만으로 **14.9%** saving

### 4.5 Hardware Overhead (Table 5, 6)

**384GB CXL device:**
- On-chip SRAM: ~0.5MB (L1/L2 SMC + host base/addr/AU tables + migration table)
- DRAM structures: ~1.9MB (segment mapping + reverse mapping + queues) → DRAM size의 0.0005%
- Power/Area(7nm): 25.7mW / 0.165mm²

**4TB CXL device (projected):**
- SRAM: 5.3MB, DRAM: 22.6MB
- Power/Area(7nm): 36.2mW / 1.1mm² → 실용적 수준

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/storage.md|Storage]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2023ISCA-summarize/dram-translation-layer-software-transparent-dram-power-savings-for-disaggregated-memory.md|전체 요약 보기]]
