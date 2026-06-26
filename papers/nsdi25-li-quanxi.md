---
tags: [paper, 2025, 2025NSDI, topic/cache, topic/disaggregation, topic/dram, topic/memory-tiering]
venue: ""
year: 2025
summary_path: "../paper-summaries/2025NSDI-summarize/nsdi25-li-quanxi.md"
---

# Beehive: A Scalable Disaggregated Memory Runtime Exploiting Asynchrony of Multithreaded Programs

**Venue:** 
**저자:** Quanxi Li, Hong Huang, Ying Liu, Yanwen Xia (ICT, CAS / UCAS), Jie Zhang (Peking Univ.), Mosong Zhou, Yizhou Shan (Huawei Cloud), Xiaobing Feng, Huimin Cui (ICT, CAS / UCAS), Quan Chen (SJTU), Chenxi Wang (ICT, CAS / UCAS)

## 개요

Memory disaggregation은 원격 서버의 DRAM을 응용 프로그램에 제공하여 메모리 용량을 수 배에서 수십 배 확장할 수 있게 한다. 그러나 원격 메모리 접근은 **microsecond(µs)-scale latency** (최대 6µs, RDMA 기반 [88, 92])를 수반하여 로컬 메모리 접근 대비 수십 배 이상의 성능 저하를 초래한다.

### 1.1 기존 접근: Uthread 기반 Synchronous 모델의 한계

기존 SOTA runtime인 **AIFM**[92]은 Shenango uthread[82]를 사용하여 µs-scale latency를 숨긴다. 한 thread가 원격 접근을 발생시키면 해당 uthread를 suspend하고 즉시 다른 ready uthread로 전환하여 CPU idle을 방지한다 (Figure 1(a)). uthread context switching은 약 200 cycles로 kernel thread(≈2,000 cycles) 대비 10× 빠르다.

그러나 논문은 Multi-Grid PDE (MGP, NPB 벤치마크 [65])를 AIFM에서 실행하며 AIFM의 근본적 문제를 발견한다:

**문제 1: Poor data locality**. AIFM은 MGP에서 uthread switching을 최대 4×10^8회 발생시키며, 이로 인해 **LLC miss가 Hermit 대비 6.5× 증가**한다. 원인은 (1) application data가 uthread별로 partitioning되어 각 uthread가 자신만의 data hotspot을 가지며, (2) AIFM이 prefetching pool(17개 uthread)과 evacuation pool(40개 uthread)을 별도로 운용하여 총 121개의 uthread가 동작하여 WSS(working set size)가 급증하기 때문이다.

**문제 2: Thread scheduling overhead**. MGP 실행 시 **CPU time의 23%가 thread scheduling에 소비**된다. uthread switching frequency는 초당 2.2M회에 달하며, context switching(≈200 cycles) 자체보다 scheduling(대기열 삽입, lock operation) 비용이 10× 크다.

이로 인해 **병목이 remote memory access에서 local memory access + thread management로 이동**하는 현상이 발생한다. 또한 application별 optimal uthread 개수가 달라 unpredictable tuning overhead가 존재한다 (§5.4).

### 1.2 핵심 통찰 (Key Insight)

한 thread의 code는 data dependency가 없는 수많은 **tiny code block(coroutine)**들로 분할 가능하며, 이들은 asynchronous하게 실행될 수 있다. Coroutine 기반 실행은 thread switching 대비 **훨씬 작은 WSS**와 **훨씬 낮은 context switching overhead**를 가지므로, data locality 유지와 높은 remote access concurrency를 동시에 달성할 수 있다 (Figure 1(b)).

---

## 방법론

### 3.1 방법론 개요

| 항목 | 내용 |
|------|------|
| **Testbed** | Compute server 1대 + Memory server 1대, 각각 Intel Xeon Gold 6342 (2 sockets), 256GB DRAM |
| **Network** | 100 Gbps Mellanox ConnectX-5 InfiniBand (RDMA), 단일 memory server (scalability는 최대 24대) |
| **Baselines** | Fastswap[11], Hermit[88], AIFM[92] |
| **Workloads** (8개) | Llama2-7B (LMA)[102], Multi-Grid PDE (MGP)[65], Social Network (SN)[39], Key-Value Store (KVS)[4], LiveGraph BC (LG-BC)[114], Ligra CC (L-CC)[97], DataFrame Taxi (DF-T)[74], DataFrame Flight (DF-F)[74] |
| **Access patterns** | Regular (LMA), Mixed (MGP, LG-BC, L-CC, DF-T, DF-F), Random (SN, KVS) |
| **Local memory ratios** | 13%, 25%, 50%, 75%, 100% (100% = all-local for runtime overhead 측정) |
| **Metrics** | Throughput (execution time), Tail latency (90th, 99th percentile), LLC misses, Scheduling overhead |

### 3.2 Throughput 결과 (§5.2)

**Overall**: Beehive는 Fastswap 대비 **4.26×**, Hermit 대비 **3.05×**, AIFM 대비 **1.58×** 평균 throughput 향상 (13%~75% local memory, 8개 workload).

**Workload별 상세**:

**(a) LMA (Llama2-7B) & MGP (Multi-Grid PDE)** — Regular/Mixed, good spatial locality:
- 데이터가 thread별 tile로 partition되어 AIFM의 uthread switching 시 data locality 심각 저하
- MGP: AIFM은 Beehive 대비 LLC miss 3.5× (75% local) → 7.3× (13% local) 증가
- Beehive vs AIFM: LMA 1.58×, MGP 1.54× 평균 향상
- LMA의 경우 spatial locality가 excellent하여 모든 시스템에서 prefetching이 잘 동작, RDMA bandwidth가 주 병목

**(b) SN (Social Network) & KVS (Key-Value Store)** — Random access:
- Fine-grained object granularity로 Fastswap/Hermit의 I/O amplification 회피: Beehive vs Fastswap 8.27× (SN), 5.14× (KVS)
- SN (skewed): Beehive vs AIFM 2.21× 평균 — remote access 자체가 적어 data locality improvement 영향 큼
- KVS (uniform, shared data): LLC miss 차이는 2.6%에 불과하나 scheduling overhead가 6.9× 감소 → 1.28× throughput 향상

**(c) LG-BC (LiveGraph) & L-CC (Ligra)** — Mixed access, memory-intensive:
- Beehive vs AIFM: LG-BC 1.13×, L-CC 1.23× — 제한적 성능 향상
- 원인: (1) 복잡한 graph 구조가 intricate PDG를 생성 → layer당 평균 3.8개 pararoutine만 생성 (L-CC), (2) LG-BC는 RDMA bandwidth 8.7GB/s(13% local)로 network-bound

**(d) DF-T (DataFrame Taxi) & DF-F (DataFrame Flight)** — Mixed access:
- Column이 chunk로 slicing되어 uthread별로 할당 → AIFM의 thread switching으로 인한 locality 저하 심각
- DF-T: AIFM 대비 LLC miss 2.8× 증가, Beehive vs AIFM **1.54×**
- DF-F: AIFM 대비 LLC miss 8.8× 증가, Beehive vs AIFM **2.27×**

**All-local (100%) overhead**: Beehive는 runtime barrier, profiling, bookkeeping overhead로 인해 Hermit 대비 MGP에서 최대 21% overhead. 그러나 이는 remote memory 사용 시 얻는 이득이 훨씬 크다.

### 3.3 Latency 결과 (§5.3)

16 cores, 13% local memory, SN과 KVS의 90th tail latency 측정:

| Workload | Load (Mops) | Beehive vs Hermit | Beehive vs AIFM |
|----------|-------------|-------------------|-----------------|
| SN | 0.64 | Hermit already saturated at 0.1 | **5.5×** (at 0.64 Mops) |
| KVS | 2.0 | **2,869×** | **5.5×** |

Beehive의 우수한 tail latency는 (1) LLC miss 40% 감소 → core compute capacity 향상 → queuing latency 감소, (2) scheduling overhead 80% 감소에 기인한다. 특히 KVS는 SN과 달리 균일 분포(uniform distribution)로 인해 Hermit의 I/O amplification이 심각하게 발현된다.

### 3.4 Ablation & Sensitivity Studies (§5.4, Appendix)

**(a) Thread count sensitivity** (Figure 10):
- AIFM: uthread 수 증가에 따라 성능이 증가하다가 sweet spot 이후 LLC miss + scheduling overhead로 저하 → application별 optimal uthread 수가 다름 (예: MGP=64, DF-T=128)
- Beehive: cooperative scheduling으로 core당 1개의 active uthread만 유지 → **uthread 수에 insensitive** (성능 변동 ≤4%)

**(b) LLC miss & Scheduling overhead** (Figure 11):
- Beehive vs AIFM: **LLC miss 57% 감소**, **scheduling overhead 82% 감소** (average over MGP, DF-T, SN, L-CC, 13% local)

**(c) Memory server scalability** (Figure 12):
- 최대 24대 memory server로 확장 시 성능 저하 ≤2.5%
- SN만 유의미한 성능 변동(fluctuation) 관찰 — random access + large memory footprint로 인한 잦은 QP switching이 원인

**(d) Async transformation impact** (Figure 13, Appendix A.2):
- Beehive-sync (compiler transformation 비활성화, synchronous model로 실행): AIFM 대비 1.09× (optimized evacuator + atomic instruction 효과)
- Beehive-async vs Beehive-sync: MGP **72.6%**, DF-T **70.9%**, SN **81.1%**, L-CC **32.8%** 성능 향상

**(e) Preemptive scheduling** (Figure 15, Appendix A.3):
- SN의 heavy-tailed request (Compose Post: 0.7-76µs service time)에 대해, preemptive scheduling이 cooperative 대비 short request의 99th tail latency를 **85% 감소**
- Heavy-tailed request는 30% latency 증가하나 전체 SLO 개선에 기여

---

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

| Component | 규모 | 기술 스택 |
|-----------|------|----------|
| Beehive core | ~8,000 LOC (Rust + C++) | Rust nightly (coroutine feature), C++ for RDMA |
| Programming model | `pararoutine!` 매크로, RemPtr/RemRef API | Rust ownership type system |
| Compiler passes | PDG, layering, fusion, scheduling | Rust compiler plugin (proc macro) |
| Runtime | Scheduler, evacuator, allocator | Log-structured allocator, per-thread waiting queue |
| Network data plane | RDMA | Mellanox InfiniBand verbs |
| Application modifications | 코드베이스의 **<5%** 수정 | 각 workload의 Rust 재구현 + pararoutine annotation |

Beehive는 Rust가 널리 사용되며 system community에서 익숙하다는 이유로 Rust로 구현되었지만, ownership type system 기반 PDG 분석은 다른 언어에도 적용 가능하다.

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]


## 전체 요약

[[../paper-summaries/2025NSDI-summarize/nsdi25-li-quanxi.md|전체 요약 보기]]
