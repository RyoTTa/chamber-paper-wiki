---
tags: [paper, 2023, 2023MICRO, topic/cache, topic/disaggregation, topic/dram, topic/memory-tiering]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023MICRO-summarize/demystifying-cxl-memory-with-genuine-cxl-ready-systems-and-devices.md"
---

# Demystifying CXL Memory with Genuine CXL-Ready Systems and Devices

**Venue:** 
**저자:** 

## 개요

CXL(Compute eXpress Link)은 PCIe 5.0 기반의 cache-coherent memory interface로, DDR5 대비 핀 수 약 3× 적고, PCIe 5.0 ×8 기준 ~64 GB/s 이론 대역폭을 제공하며, 비트당 에너지도 PCIe 4.0: 6 pJ/bit vs DDR4: 22 pJ/bit로 우수하다. CXL.mem 프로토콜을 통해 CPU는 CXL memory device를 remote NUMA node로 인식하고 load/store instruction으로 cache-coherent하게 접근할 수 있다.

그러나 그동안 상용 CXL hardware 부재로 인해 **대부분의 prior work는 multi-socket 시스템의 remote NUMA node에 DDR memory를 배치하여 CXL memory를 emulate**해왔다. 이 논문은 최초로 **4th-gen Intel Xeon (Sapphire Rapids)** + **3종의 실제 CXL memory device (CXL-A/B/C)** 를 사용하여 emulated CXL memory(DDR5-R)와 true CXL memory의 근본적인 차이를 규명한다.

**Testbed**:
| 항목 | 내용 |
|------|------|
| CPU | Dual-socket Intel Xeon 6430 @2.1GHz, 32 cores, 60MB LLC per socket, Hyper-Threading off |
| Local DDR | Socket 0: 8× DDR5-4800 channels |
| Emulated CXL | Socket 1: 1× DDR5-4800 channel (DDR5-R) |
| CXL devices | CXL-A (Hard IP, DDR5-4800, 38.4 GB/s), CXL-B (Hard IP, 2×DDR4-2400, 19.2 GB/s), CXL-C (Soft IP/FPGA, DDR4-3200, 25.6 GB/s) |
| SNC mode | Sub-NUMA Clustering (2 local DDR channels + 1 CXL channel) |

## Latency Characteristics (Section 4.1)

Microbenchmarks: Intel MLC (serialized pointer-chasing) + memo (parallel random access, per instruction type).

### 주요 관측 (O1–O3)

**(O1) Full-duplex CXL/UPI가 latency 단축에 기여.** Intel MLC의 serialized access는 full-duplex 이점을 활용 못하나, memo의 parallel access는 command/address와 data를 동시 송수신 → 평균 latency 절반 감소. memo 기준 DDR5-R의 ld latency는 MLC 대비 76% 낮음. CXL-A는 추가 3%p 더 감소 (O3 설명).

**(O2) CXL controller design에 따른 latency 편차 큼.** CXL-A의 ld latency는 DDR5-R 대비 35%만 증가, CXL-B는 ~2×, CXL-C는 ~3×. 동일 DDR4 DRAM이라도 CXL-C(DDR4-3200)가 CXL-B(DDR4-2400)보다 67% 더 높은 ld latency. 원인: FPGA-based soft IP vs ASIC-based hard IP + memory controller efficiency 차이.

**(O3) Emulated CXL memory가 true CXL memory보다 오히려 latency가 높을 수 있음.** 이유:
1. Emulated CXL memory는 remote CPU에 cache coherence check를 위해 inter-chip UPI를 거쳐야 하고, remote CPU의 intra-chip interconnect + memory controller까지 통과해야 함.
2. True CXL memory는 CPU 내 on-chip hardware structure로 cache coherence check를 빠르게 처리하며, device 내 interconnect도 짧음.
3. memo의 parallel access는 emulated CXL memory에 cache coherence traffic congestion을 유발 → ld latency 증가. True CXL은 local on-chip check로 이 문제에서 자유로움.
4. **Store latency**: Intel의 cache write-allocate policy로 인해 st는 LLC miss 시 implicit ld 발생 → UPI/CXL interface overhead 2배. emulated CXL은 cache coherence overhead까지 더해져 st, nt-st 모두 불리.
5. **nt-st latency**: CXL-A는 DDR5-R보다 25% 낮음 (cache coherence check overhead 차이).

**정량 예시**: memo 기준 CXL-A ld latency는 DDR5-L 대비 ~1.35×, CXL-C는 ~3×. 40-core SPR CPU에서 DDR5-R은 CXL-A보다 ld latency 4% 더 높음.

## Bandwidth Characteristics (Section 4.2)

Bandwidth efficiency (measured bandwidth / theoretical max) 기준:

| Device | All Read | ld | nt-ld | st | nt-st |
|--------|----------|-----|-------|-----|-------|
| DDR5-R | 70% | higher | higher | lower | higher |
| CXL-A | 46% | lower | lower | **higher** (vs DDR5-R +12%p) | lower |
| CXL-B | 47% | higher | higher | higher | ~same as DDR5-R |
| CXL-C | 20% | lowest | lowest | lowest | lowest |

**(O4) Bandwidth는 CXL controller efficiency에 크게 의존.** CXL-A의 All-Read efficiency는 DDR5-R보다 23%p 낮음 (DDR5-4800 동일 DRAM). Write ratio 증가 시 CXL-A가 역전: '2:1-RW'에서 DDR5-R보다 23%p 높음. CXL-A memory controller는 interleaved read/write 처리에 최적화된 것으로 추정.

**(O5) True CXL memory는 store에서 competitive한 bandwidth efficiency.** st는 implicit ld + cache coherence check overhead로 모든 device에서 ld보다 낮은 efficiency. emulated CXL의 st efficiency degradation이 true CXL보다 큼 → CXL-A, CXL-B의 st efficiency가 DDR5-R보다 각각 12%p, 1%p 높음. nt-st의 DDR5-R vs CXL-A gap은 nt-ld의 26%p → 6%p로 축소.

FPGA 기반 CXL-C는 모든 지표에서 가장 낮은 efficiency (ld에서 CXL-B 대비 26%p 낮음).

## Cache Hierarchy Interaction (Section 4.3)

**(O6) CXL memory는 SNC mode에서 LLC isolation을 깨뜨린다.** Intel SPR SNC mode: local DDR memory의 L2 eviction은 동일 SNC node의 LLC slice로만 가지만, **CXL memory(및 모든 remote memory)의 L2 eviction은 모든 SNC node의 LLC slice에 분산**된다.

**검증**: 32MB buffer (1개 SNC node LLC = ~15MB < 32MB < 4개 SNC node LLC = ~60MB) 대상 실험:
- CXL-A buffer access: avg 41 ns (전체 LLC 활용 가능)
- DDR5-L buffer access: avg 76.8 ns (자신의 SNC node LLC만 사용)
- **CXL memory access가 오히려 더 낮은 latency를 보임** — cache-friendly workload의 경우 CXL memory latency penalty가 더 큰 effective LLC capacity로 상쇄됨.

이는 prior emulation 기반 연구에서 포착하지 못한 핵심 차이.

## Application Performance Impact (Section 5)

CXL-A 사용 (가장 균형 잡힌 latency/bandwidth).

### 5.1 Latency-sensitive Applications

**Redis** (YCSB-A, uniform key distribution):
- DDR 100% → CXL 100%: 85K QPS에서 p99 latency 105% 증가 (10% → 73% → 105% as QPS increases)
- CXL 25%/50%/75%: p99 각각 9%/23%/45% 증가
- 𝜇s-scale 응답시간으로 인해 memory access latency에 극도로 민감

**Redis + TPP** (Transparent Page Placement):
- CXL 100% 시작 → TPP가 DDR로 75% migration 후 측정
- TPP는 static 25% allocation 대비 p99 latency 174% 증가
- 원인: 지속적인 small-scale page migration overhead (page copy + page table update가 memory controller blocking 유발)

**DeathStarBench** (social network microservices):
- compose posts, read user timelines, mixed workloads 모두 CXL 100% vs DDR 100% 간 p99 latency 차이 미미
- 원인: (1) p99 latency의 대부분은 frontend/logic component(DDR memory 사용)에서 소비, (2) 𝑚s-scale latency는 memory access latency에 둔감
- Mixed workloads는 일부 QPS 구간에서 CXL 100%가 더 나은 성능 — bandwidth-intensive하기 때문 (32 GB/s 소비 vs compose posts: 7 GB/s)

**FIO** (page cache on CXL):
- 4KB block: CXL ≈ +3% p99 latency (kernel operation overhead dominant)
- 8KB: +4.5% (kernel op amortized, memory latency exposed)
- >128KB: page cache hit rate 감소 → storage I/O + DDIO dominant → memory latency effect 감소

### 5.2 Throughput

**DLRM embedding reduction** (bandwidth-bound):
- 32 threads에서 CXL 63% allocation → DDR 100% 대비 88% throughput 증가
- 특정 CXL allocation 비율에서 최대 throughput 존재 (CXL bandwidth capability dependent)

**Redis** (latency-bound throughput):
- CXL 25%/50%/75%/100% allocation → DDR 100% 대비 8%/15%/22%/30% throughput 감소

**Key Finding (F4)**: memory-bandwidth-intensive application에서 default 50% CXL allocation이 오히려 DDR 100%보다 낮은 throughput을 줄 수 있음 → dynamic policy 필요성.

### 5.3 LLC Interference

- SNC-0만 CXL 100%, 다른 3개 SNC는 DDR 100% → SNC-0의 DLRM throughput이 단독 실행 대비 47% 감소 (effective LLC capacity가 다른 SNC node의 traffic으로 오염)
- CXL memory의 LLC isolation breaking이 인접 SNC node의 성능도 2% 저하시킴

## Caption: CXL-Memory-Aware Dynamic Page Allocation Policy (Section 6)

## 방법론

Caption은 3개 runtime module로 구성:

**(M1) Monitor**: Intel PCM으로 다음 counter를 주기적(1s) 샘플링, 5-sample moving average 적용.
- L1 miss latency (ns)
- DDR read latency (ns)
- IPC

**(M2) Estimator**: linear regression model
```
𝑌 = β₀ + β₁·𝑋₁ + β₂·𝑋₂ + ...
```
𝑋ₙ = counter 값, βₙ = DLRM training data로 fitting한 weight. simple linear model → OS-level low overhead.

**(M3) Tuner**: greedy binary-search-like tuning.
1. estimator로 current memory-subsystem performance 측정
2. prev보다 improve되었으면 같은 방향으로 step 유지
3. degrade되었으면 step을 반대 방향으로 ×(−0.5) (reverse + halving)
4. step size는 minimum floor 존재 (9%)
5. Application phase change 시 모든 state reset

mempolicy (Linux kernel patch)를 통해 DDR:CXL allocation ratio를 설정.

## 핵심 기여

**핵심 contribution**: 최초로 genuine CXL-ready hardware(SPR CPU + 3종 CXL device)로 true CXL memory의 성능 특성을 포괄적으로 분석하고, NUMA emulation과의 결정적 차이점을 규명.

**Key insights**:
1. **CXL memory ≠ remote NUMA memory**: true CXL memory는 cache coherence check 방식, LLC interaction, instruction-type별 latency/bandwidth 특성이 emulation과 근본적으로 다르다. Prior emulation-based 연구의 conclusion과 design decision이 재검토되어야 할 수 있음.
2. **CXL memory의 bandwidth expander 가능성**: memory-bandwidth-intensive workload에서 적절한 비율로 CXL memory를 활용하면 throughput을 유의미하게 개선할 수 있으나, static allocation은 suboptimal.
3. **SNC mode + CXL = larger effective LLC**: cache-friendly application에서는 CXL memory latency penalty가 더 큰 effective LLC capacity로 상쇄되어 DDR memory보다 더 낮은 latency를 보일 수 있음.

**Caption의 의의**: device-specific bandwidth capability, memory intensiveness, memory access latency를 runtime에 반영하여 CXL memory allocation ratio를 자동 조정하는 최초의 dynamic policy. 최대 24% throughput 향상.

**Broader impact**: CXL memory가 memory tiering, disaggregation, swapping 등 다양한 시스템 연구 분야에서 emulation을 넘어 실제 hardware 기반 연구로 전환되어야 함을 시사.

## 주요 결과

| 항목 | 내용 |
|------|------|
| Workloads | DLRM, SPECrate CPU2017 memory-intensive (fotonik3d, mcf, roms, cactuBSSN), Redis, mixed |
| Baselines | Static 100% DDR, Static 50:50 DDR:CXL |

**DLRM**: Caption이 100% DDR 대비 80% 높은 throughput, 50:50 대비 4% 높음.
**SPEC-Mix**: Caption이 50:50 static 대비 최대 24% 높은 throughput (mcf+roms).
**개별 SPEC**: fotonik3d +19%, mcf +18%, roms +8%, cactuBSSN +20% (best static policy 대비).
**Redis+DLRM mix**: +4% (best static 대비).
**Redis 단독**: +3.2% (50:50 vs), −8.6% (100% DDR vs) — latency-bound임을 학습하여 DDR 선호 방향으로 수렴.

Steady-state convergence: workloads에 따라 29%–41% CXL allocation. Pearson correlation: model output과 actual throughput 간 대부분 positive 유지 → direction-based greedy tuning에 충분.

## Differences from Emulation: Summary

| 측면 | Emulated (DDR5-R) | True CXL (CXL-A/B/C) |
|------|-------------------|---------------------|
| Cache coherence | remote CPU UPI 통과 → congestion | local on-chip structure → 빠름 |
| St latency | cache coherence overhead 大 | 상대적으로 낮음 |
| nt-st | 더 높은 latency | CXL-A 25% 낮음 |
| LLC interaction (SNC) | (multi-socket이므로 애초에 다름) | SNC isolation breaking → larger effective LLC |
| Device diversity | 없음 (DDR5 고정) | IP type(hard/soft) + DRAM tech 다양 |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]


## 전체 요약

[[../paper-summaries/2023MICRO-summarize/demystifying-cxl-memory-with-genuine-cxl-ready-systems-and-devices.md|전체 요약 보기]]
