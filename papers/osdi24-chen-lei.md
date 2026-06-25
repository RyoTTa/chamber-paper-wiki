---
tags: [paper, 2024, 2024OSDI, topic/cache, topic/memory-tiering, topic/virtual-memory]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024OSDI-summarize/osdi24-chen-lei.md"
---

# A Tale of Two Paths: Toward a Hybrid Data Plane for Efficient Far-Memory Applications

**Venue:** 
**저자:** Lei Chen (University of Chinese Academy of Sciences), Shi Liu (UCLA), Chenxi Wang (UCAS), Haoran Ma (UCLA), Yifan Qiao (UCLA), Zhe Wang (UCAS), Chenggang Wu (UCAS), Youyou Lu (Tsinghua University), Xiaobing Feng (UCAS), Huimin Cui (UCAS), Shan Lu (Microsoft Research), Harry Xu (UCLA)

## 개요

### 1.1 Far Memory의 두 데이터 경로

데이터센터 메모리 활용률은 낮지만, 애플리케이션은 점점 더 memory-constrained 상황에 직면함. InfiniBand 등 현대 네트워크 패브릭이 제공하는 고대역폭·저지연을 활용하여 원격 서버 메모리를 로컬처럼 쓸 수 있는 **far memory** 기술이 주목받고 있음. 그러나 원격 접근은 로컬 대비 최소 10배 이상 느리므로, 데이터를 어떻게 가져올지(데이터 경로)가 성능을 좌우함.

기존 far memory 시스템은 두 가지 데이터 경로로 나뉨:

| 경로 | 대표 시스템 | 접근 단위 | 장점 | 단점 |
|------|------------|----------|------|------|
| **Paging path** (커널 기반) | Fastswap, InfiniSwap, Canvas, Hermit | Page (4KB) | 애플리케이션 투명, HW 지원(LRU, TLB)으로 리소스 효율적 | Random access에서 I/O amplification (한 페이지 내 유용 데이터 소량) |
| **Object-fetching path** (런타임 기반) | AIFM, Kona | Object (수~수백 바이트) | Fine-grained 접근으로 I/O amplification 최소화, semantics-aware prefetching 가능 | Object-level LRU, eviction에 막대한 CPU 리소스 필요 |

### 1.2 Object Fetching의 숨겨진 비용

Object fetching의 결정적 약점은 **compute overhead**임. AIFM은 수십 개의 profiling/eviction 스레드를 상시 구동하여 수십억 개 object의 hotness를 추적하고 LRU로 rank함. CPU 코어가 애플리케이션 스레드로 포화된 실제 환경에서는, 제한된 time budget 내에 충분한 object를 스캔하지 못해 cold/hot 구분 없이 임의의 object를 evict하게 되고, 이는 data thrashing을 유발함.

**Motivation 실험 (Figure 1(b), (c)):**
- Metis PageViewCount의 Reduce phase (sequential pattern)에서 AIFM은 Fastswap 대비 **3.3× 느림**. 이유: sequential phase에서는 page 단위 fetch가 이미 충분히 효율적이므로 object fetching의 CPU overhead만 부각됨.
- AIFM의 eviction은 Reduce phase 내내 **200~350% CPU**를 지속 소모하며, eviction throughput은 Fastswap 대비 **5× 낮음**. Fastswap은 첫 5초 내 eviction을 완료하고 100% 미만 CPU 사용.
- 반면 Map phase (random pattern)에서는 AIFM이 Fastswap 대비 **1.6× 빠름** — random access에서 I/O amplification 감소 효과가 큼.

즉, 최적의 데이터 경로는 **프로그램의 locality(→I/O amplification 크기)와 가용 compute 리소스(→object management overhead 감당 가능 여부) 사이의 tradeoff**에 달려 있음.

### 1.3 Offline Profiling의 한계

Mira 등 compiler 기반 offline profiling은 (1) 프로그램 입력이 바뀌면 access pattern이 달라지고 (Figure 1(d): Wikipedia Italian으로 입력 변경 시 Map phase의 sequential pattern 소멸), (2) Memcached 같은 interactive application은 사용자 요청에 따라 동작이 변하며, (3) CPU 리소스 경쟁 같은 환경 변화를 예측할 수 없음.

### 1.4 핵심 인사이트

**Always-on profiling으로 access pattern을 실시간 식별하고, paging과 object fetching을 동적으로 전환하는 hybrid data plane**을 제안. 추가로 object fetching은 시간적 근접성이 높은 object를 contiguous 공간으로 이동시켜 locality를 점진적으로 개선 → 이후 접근이 paging에 더 적합해지는 선순환 구조.

---

## 방법론

### 3.1 Methodology

| 항목 | 내용 |
|------|------|
| **Testbed** | Compute server 1대 + Memory server 1대, 200Gbps InfiniBand switch 연결 |
| **CPU** | Intel Xeon Gold 6342 × 2 (24 cores each), TSX 지원 |
| **Memory** | 각 256 GB |
| **NIC** | Mellanox ConnectX-5 100Gbps InfiniBand |
| **OS** | Ubuntu 18.04, Linux kernel 5.14-rc5 (Atlas 수정) |
| **Baselines** | Fastswap (paging 대표), AIFM (object-fetching 대표) |
| **Workloads** | 8종: MCD-CL, MCD-U, GraphOne PageRank, Aspen TriangleCount, Metis WC, Metis PVC, DataFrame, WebService |
| **Access patterns** | Random (MCD-CL/U), Evolving graph (GPR, ATC), Phase-changing (MWC, MPVC, DF), Mixed (WS) |
| **Local memory ratios** | 13%, 25%, 50%, 75%, 100% (cgroup으로 제한) |
| **Metrics** | Throughput, tail latency (90th percentile), eviction throughput, CPU utilization, runtime overhead breakdown |

### 3.2 Throughput

**Overall:** Atlas는 Fastswap 대비 **3.2×**, AIFM 대비 **1.5×** throughput 향상 (8개 애플리케이션, 13%~75% local memory 평균).

**100% local memory 시 runtime overhead:**
- Atlas: **19.1%** (barrier 10.2% 포함)
- AIFM: **14.0%** (barrier 2.3%)

**Application별 분석:**

| Application | Atlas vs. Fastswap | Atlas vs. AIFM | 주요 이유 |
|-------------|-------------------|----------------|----------|
| **MCD-CL** (skewed) | 6.4× | 1.2~2.5× (ratio별) | Fastswap: 26× 더 많은 데이터 fetch. Atlas: eviction throughput 4.6× 높고, evacuator로 18% 더 많은 페이지가 paging path로 전환 |
| **MCD-U** (uniform) | — | up to 1.4× | Skewness 없어 locality 개선 제한적이나, page-level eviction이 더 효율적 |
| **GPR** | 3.1× | 1.8× | 82% 페이지가 PSF runtime→paging으로 flip. Lazy relocation으로 locality 점진 개선 |
| **ATC** | — | 2.0× | 38% 페이지 flip + evacuation으로 hot object segregation → remote access 24% 감소 |
| **MWC** | 1.5× | 1.2× | Two-phase behavior. Map phase random, Reduce phase sequential → 적응적 전환 |
| **MPVC** | 1.4× | 1.2× | Figure 7(c): phase change 감지 즉시 PSF=paging 페이지 급증 |
| **DF** | — | 1.2~1.4× | Copy(sequential) ↔ Shuffle(random) 간 적응적 전환. AIFM은 remote vector resizing overhead로 51.4% overhead |
| **WS** | — | 1.3× | AIFM: LRU list에 수많은 object → eviction thread starvation → data thrashing. Atlas eviction throughput 5.8× 높고, 5.9 cycles/byte (AIFM 43.7 cycles/byte → 7.4× 효율) |

### 3.3 Tail Latency

**WebService (Figure 5):**
- Atlas peak throughput: **0.57 MOPS** (AIFM 0.36, Fastswap early saturation)
- 90th latency @ 0.23 MOPS: Atlas ≈ 수백 µs, Fastswap > 10^5 µs
- AIFM과 Atlas는 50th percentile까지 comparable, 이후 Atlas 우위 (locality 개선으로 remote access 감소)

**MCD-CL (Figure 6):**
- Atlas > AIFM > Fastswap 순. 40%의 개선이 evacuation의 hot object grouping에 기인.

### 3.4 Performance Drill Down

#### Adaptive Path Switching (Figure 7)

- **MCD-CL:** churn behavior에 따라 PSF=paging 비율이 주기적으로 상승/하강. Hot spot 이동 시 page 재구성.
- **GPR:** 3 batch의 graph update → 각 batch의 analytics iteration에서 rapid locality establishment → PSF=paging 페이지 급증 (82%).
- **MPVC:** two-phase behavior를 정확히 감지 → Reduce phase 진입 즉시 PSF=paging 비율 증가.

#### Computation Offloading (Figure 8)

- Atlas + offload: DF에서 **1.5×**, WS에서 **1.6×** throughput 향상.
- AIFM + offload와 comparable (offloading이 fetching 차이를 희석).

#### Runtime Overhead Breakdown (Figure 9, Table 2)

| Overhead source | Atlas | AIFM | 비고 |
|----------------|-------|------|------|
| Barrier (location check + sync) | ~10.2% (전체 53%) | ~2.3% (전체 16%) | Atlas는 TSX 기반 location check로 AIFM보다 무거우나, fine-grained scope로 sync 비용 감소 |
| Card Profiling | Atlas 전용 | — | 3~7% |
| Dereference Trace Profiling | 공통 (전체의 14%) | 공통 (전체의 19%) | Remote memory 환경에서는 Atlas가 paging path로 많은 데이터가 전환되어 더 낮음 |
| Evacuation | 공통 | 공통 | Atlas는 non-blocking 설계로 CPU yield rate가 AIFM보다 order of magnitude 낮음 |
| Remote DS Management | — | AIFM 전용 | AIFM의 DF에서 최대 2/3의 overhead 차지 |

**Memory-intensive 앱(MWC, MPVC, DF)이 가장 큰 barrier overhead**를 보이나, 1회 dereference당 수십 회 raw pointer 접근으로 amortize됨.

#### CAR Threshold Sensitivity (Figure 10)

- Optimal: 80~90%. Threshold = 100%: MCD-CL에서 25% throughput 감소 (너무 보수적 → 대부분 runtime path). Threshold = 50%: I/O amplification으로 성능 저하.
- 80% 선택 이유: 현대 네트워크(InfiniBand) 대역폭이 높아 약간의 추가 데이터 전송 overhead 감수 가능.

#### Hotness Tracking: Access Bit vs. LRU (Figure 11)

- Atlas의 single access bit 설계가 CacheLib의 LRU-like policy 대비 **3.3~7.5% 더 높은 throughput** (MCD-CL, MCD-TWT, MCD-U). 이유: LRU의 linked-list maintenance overhead (최대 9%)가 정확도 향상의 이점을 상쇄.
- 2-bit access로 확장해도 유의미한 차이 없음.

---

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

| Component | 규모 | 상세 |
|-----------|------|------|
| **Runtime library** | 7,675 lines | C/C++. Log-structured allocator, evacuator, smart pointer/barrier 구현 |
| **Kernel modification** | Linux 5.14-rc5 기반 | Page management: PSF per-page metadata, deref count, CAT integration, swap-out path 수정 |
| **Application porting** | 263~391 lines/app | Metis 263, Aspen 278, GraphOne 219, Memcached 391. Smart pointer 선언 + dereference scope 추가. 개발자 1인이 수 시간 소요 |
| **Dependencies** | jemalloc (allocator), Intel TSX (RTM), InfiniBand (RDMA) | Remote memory는 swap partition으로 추상화, Mellanox MLNX_OFED 5.5 필요 |

Huge object (>4KB)는 별도 huge-object space에서 kernel 직접 관리.

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2024OSDI-summarize/osdi24-chen-lei.md|전체 요약 보기]]
