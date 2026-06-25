---
tags: [paper, 2023, 2023ASPLOS, topic/cache, topic/dram, topic/nvm, topic/storage]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023ASPLOS-summarize/re-architecting-io-caches-for-emerging-fast-storage-devices.md"
---

# Re-architecting I/O Caches for Emerging Fast Storage Devices

**Venue:** 
**저자:** 

## 개요

Enterprise SAN(Storage Area Network) 환경에서 I/O caching은 비용 효율적 성능 향상을 위해 SSD cache + HDD array 구성으로 널리 사용되어 왔다. 최근 P5800X Optane SSD(1.5M IOPS, 6μs latency), Intel Persistent Memory DIMM(sub-μs latency), RAMDisk 등 **ultra-fast storage device**가 등장하면서, 이들을 I/O cache device로 사용하고 backend를 SSD array로 구성하는 **modern fast SAN**이 현실화되고 있다.

그러나 저자들은 **기존 I/O cache architecture가 modern fast SAN에서는 완전히 다른, 예상치 못한 성능 특성을 보인다**는 점을 발견했다:

- Traditional SAN (SSD cache + HDD backend): OpenCAS, DM-Cache, EnhanceIO 모두 **78K IOPS**로 device bottleneck에 수렴 (Figure 2a).
- Modern SAN (RAMDisk cache + SSD backend): **335K~1.5M IOPS**로 cache architecture에 따라 최대 **5배 차이** 발생.
- Cache hit rate 100%→85% 감소 시: Traditional SAN에서는 성능 저하, Modern SAN에서는 **오히려 15% 성능 향상** (Figure 2b) — fast SSD backend가 load balancing 기회를 제공하기 때문.

**기존 연구의 한계:** SSD caching for HDD array 연구는 많으나, ultra-fast device + SSD backend 조합에서 I/O cache의 아키텍처 수준 분석은 전무. 산업용 I/O cache는 60,000 LOC(OpenCAS)에 달하는 복잡한 소프트웨어로, 단순 시뮬레이션으로는 실제 거동을 포착할 수 없다.

## 방법론

### 3.1 Lookup Logic — Finding 1 (Figure 6)

**HT+FG (OpenCAS)가 유일하게 near-linear scalability 제공 (최대 2.2M IOPS):**
- LT+FG (EnhanceIO): 4 jobs에서 350K IOPS로 포화, 이후 swapper process CPU 증가.
- HT+CG (DM-Cache): jobs 증가 시 spin-lock overhead가 CPU cycle의 80% 이상 → 급격한 성능 저하.
- HT+FG: core 수에 비례하여 2.2M IOPS까지 선형 확장, locking/swapper 비중 일정.

### 3.2 Read Miss Management (Promotion Logic + Cache Line Size)

**Finding 2a (Figure 8):** 일반적인 controlled uniform workload에서 **nhit-2**(miss 시 1회 지연 후 promote)가 always 대비 최대 **3배 IOPS 향상**. 이는 fast SSD backend와 cache 간 load balancing 효과. 그러나 nhit-16처럼 과도하게 지연하면 high hit rate에서 기회 손실. Highly skewed workload(zipf 1.1)에서는 nhit-2가 always 대비 약 10% 향상 — cache pollution 방지 효과.

**Finding 2b (Figure 9):** Cache line size는 promotion logic과 강하게 상호작용:
- always policy: 4KB workload + 4KB cache line이 최적. 32KB로 키우면 최대 75% 성능 저하 (large block fetch → partial miss overhead).
- nhit policy: 큰 cache line(32KB)에서도 성능 유지, 8KB/16KB workload에서 최대 **2배 speedup**.

**Finding 2c (Figure 10):** Tail latency(QoS) 관점에서 **nhit-4**가 가장 예측 가능한 성능 제공:
- Low locality(25% hit rate): 99.99%-ile tail latency가 always 대비 **최대 76배 감소**.
- High locality(85% hit rate): 감소폭은 6배로 축소.

### 3.3 Write Request Management (Flushing Logic)

**Finding 3 (Figures 13, 14):** Write burst로 cache가 full-dirty 상태일 때:
- **Lazy flushing**이 aggressive flushing 대비 **10% IOPS 향상**, **QoS 4.3배 개선**(99.99% tail latency 기준).
- 원인: Aggressive flushing은 victim block eviction 시 cache lock contention 유발. Lazy는 write miss를 SSD backend로 bypass → cache device + backend 간 load balancing.
- Low hit rate workload에서는 flushing 정책 차이가 미미 (대부분 backend에서 serve).

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

| Workload | 특성 | Optimal Arch → Non-optimal 향상 |
|----------|------|-------------------------------|
| **VDI** | Read-intensive, 35% hit rate, 30% write | **2.3× IOPS** (100K vs. 44.9K), **2.6× read tail latency** |
| **MS Exchange** | Half-read half-write, 55% hit rate | **1.7× IOPS**, **30× write tail latency** |
| **TPCC (OLTP)** | Write-intensive, 85% hit rate, 32 parallel jobs | **11× IOPS** (1.1M vs. 100K) |

**일관된 최적 구성:**
- Lookup: **HT+FG**
- Flushing: **lazy** or aggr-128
- Cache line: **16~32KB** (workload avg request size에 매칭)
- Promotion: **nhit-2** or **nhit-4**

Tail latency 최적화 시 promotion logic은 예외 — backend SSD array latency(수백 μs)의 영향으로, 매우 낮은 hit rate 환경에서는 nhit-8/16이 tail latency에 더 유리할 수 있음.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2023ASPLOS-summarize/re-architecting-io-caches-for-emerging-fast-storage-devices.md|전체 요약 보기]]
