---
tags: [paper, 2024, 2024MICRO, topic/cache, topic/disaggregation, topic/dram, topic/gpu, topic/near-data-processing]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024MICRO-summarize/demystifying-a-cxl-type-2-device-a-heterogeneous-cooperative-computing-perspective.md"
---

# Demystifying a CXL Type-2 Device: A Heterogeneous Cooperative Computing Perspective

**Venue:** 
**저자:** 

## 개요

### 1.1 Cooperative Heterogeneous Computing (CHC)과 PCIe의 한계

- AI/ML 등 현대의 데이터 집약적 애플리케이션은 CPU의 처리 능력을 넘어서는 대량 데이터를 처리해야 하며, GPU와 같은 도메인 특화 가속기(ACC)와의 협력적 이종 컴퓨팅(CHC)이 필수적 [3], [4], [9], [10], [17], [20].
- 기존 PCIe 인터페이스는 throughput-oriented coarse-grained CHC(AI/ML)에는 적합하지만, **fine-grained CHC**(datacenter latency-sensitive applications, frequent small-data host-device transfers [12], [38], [39], [67])에는 다음 한계 존재:
  1. **MMIO over PCIe:** host CPU ld/st → 256B read latency >4µs, bandwidth <0.3GB/s (uncacheable, strict write ordering).
  2. **DMA over PCIe:** high setup cost → small transfer 시 MMIO보다도 높은 latency. DMA write는 host cache invalidation으로 인한 성능 저하.
  3. **No cache coherence:** 복잡한 software stack과 상당한 프로그래밍 노력 필요 → frequent small-data transfer는 비효율적이고 비용이 높음.

### 1.2 CXL Device Types

CXL은 PCIe physical layer 위에 구축된 interconnect 표준으로 세 가지 프로토콜 제공 [14], [15], [27], [57]:

| Device Type | Protocols | 지원 동작 | 주요 응용 |
|-------------|-----------|----------|----------|
| Type 1 | io+cache | Coherent D2H | Cache-coherent ACCs, SNICs |
| Type 2 | io+cache+mem | Coherent D2H + D2D + H2D | ACCs with local memory |
| Type 3 | io+mem | Fast H2D + D2D | Memory expanders, near-memory ACC |

- **CXL Type-3:** 가장 먼저 도입됨. Device memory를 host에 remote NUMA memory로 노출, ld/st로 접근 가능. 단, device ACC가 host memory 직접 접근 불가, cache coherence software 관리 필요.
- **CXL Type-2:** 최근 상용화되었으며(Intel Agilex 7 FPGA I-Series [24]), device ACC의 host memory 접근 + hardware cache coherence + device memory까지 지원 → 가장 versatile.

### 1.3 Motivation

CXL Type-2 device가 상용화되었으나 그 capability, 성능 특성, PCIe/CXL Type-3 대비 실제 이점이 충분히 이해되지 않음. 본 논문은 이 격차를 메우고자 함.

## 방법론

**Methodology:** Intel Xeon 6538Y+ (dual-socket, 5th gen), Agilex 7 CXL Type-2 device (400MHz FPGA LSU), CLDEMOTE로 LLC-only hit 보장.

### 3.1 D2H Accesses (Fig.3)

True D2H vs. emulated D2H(remote NUMA node):

| Access Type | LLC-1 Latency (vs. NUMA) | LLC-0 Latency (vs. NUMA) | Key Observation |
|-------------|-------------------------|-------------------------|-----------------|
| NC-read (nt-ld) | +38% | +2% | Read의 경우 LLC miss 시 latency 차이 작음 |
| CS-read (ld) | +96% | +18% | CXL protocol이 NUMA UPI보다 덜 성숙 |
| NC-write (nt-st) | +71% | +67% | Write ordering overhead |
| CO-write (st) | +56% | +57% | 마찬가지 |

**Bandwidth:** CXL interconnect(PCIe 5.0 ×16, 32Gbps/lane)가 UPI(18 lanes, 20Gbps/lane)보다 40% 높은 raw bandwidth → latency penalty가 적은 read access는 CXL이 NUMA보다 높은 bandwidth 제공.

> **Insight 1:** Emulated CXL Type-2(NUMA remote node)는 application의 latency/bandwidth sensitivity에 따라 misleading한 성능을 보일 수 있음.

### 3.2 D2D Accesses (Fig.4)

Host-bias vs. Device-bias mode:

| Case | Host-bias | Device-bias | Difference |
|------|-----------|-------------|------------|
| NC-write/CO-write, DMC hit | Higher (LLC cache-line invalidation) | 60% lower latency | Device-bias가 host cache check 회피 |
| NC-read/CS-read, DMC hit | Similar | Similar (shared state, no invalidation) | Negligible |
| NC-read/CS-read, DMC miss | Higher (LLC shared check) | Lower | Device-bias가 LLC check 회피 |
| NC-write/CO-write bandwidth | Lower | 8–13% higher | — |

> **Insight 2:** Device-bias mode는 near-memory processing 등 memory-intensive workload에서 더 높은 성능 제공하나, software cache coherence 관리 비용 발생.

### 3.3 H2D Accesses: CXL Type-2 vs. Type-3 (Fig.5)

| Access | Type-2 vs. Type-3 Latency | Type-2 vs. Type-3 Bandwidth |
|--------|--------------------------|----------------------------|
| ld | +5% | -4% |
| nt-ld | +4% | -4% |
| st | +5% | -4% |
| nt-st | +2% | -4% |

**Counter-intuitive finding:** DMC hit 시 오히려 DMC miss보다 latency가 **더 높음** (owned: +11–17%, modified: +36–40%):
- DMC는 device ACC 전용, host CPU는 DMC 접근 불가 → H2D request 시 DCOH가 항상 DMC state 확인/갱신 후 device memory 접근 → 추가 latency.
- Modified cache-line은 writeback까지 필요 → 최대 +40% latency 증가.

> **Insight 3:** CXL Type-2를 memory expander로 사용 시, DMC cache-line은 shared 상태 유지하거나 flush해야 host CPU의 H2D access 성능 저하를 방지.

**NC-P의 효과:** Device ACC가 host CPU가 곧 접근할 64B word를 NC-P로 host LLC에 미리 push → H2D access가 LLC hit으로 처리 → latency 82–87% 감소, bandwidth 4.1–6.7× 증가.

### 3.4 Transfer Efficiency: CXL vs. PCIe (Fig.6)

H2D access (≤1KB transfer):

| Method | Latency (vs. CXL-ST, 256B) | Bandwidth 특성 |
|--------|---------------------------|----------------|
| **CXL-ST** | Baseline | LD/ST queue limit → >1KB에서 성능 저하 |
| PCIe-MMIO | +83% | Very low |
| PCIe-DMA (Agilex 7) | +72% | ~30GB/s saturation (×16 Gen5) |
| PCIe-RDMA (BF-3) | +81% | ~40GB/s (×32 Gen5) |
| PCIe-DOCA-DMA (BF-3) | +92% | RDMA보다 낮음 [63] |
| **CXL-DSA** | Comparable to DMA | >1KB에서 CXL-ST 대체, ~30GB/s |

D2H access:
- **CXL-LD** (CS-read): PCIe-RDMA 대비 **~3× lower latency** across all transfer sizes.
- CXL D2H write = NC-P로 host LLC에 직접 write (Intel DDIO [26]와 동일 효과).
- CXL-ST: N=16, 64B random access에서도 400MHz LSU로 25.6GB/s — ASIC 기반이면 더 높은 bandwidth 가능.

> **Insight 4:** NC-P를 지능적으로 사용하면 device memory 접근의 긴 latency를 LLC hit으로 대체 가능.
> **Insight 5:** CXL Type-2는 small transfer size에서 PCIe 대비 현저히 낮은 latency. D2H access가 H2D보다 latency가 더 낮으므로, 선택권이 있다면 D2H를 우선 사용.

## 핵심 기여

1. **문제:** CXL Type-2 device가 상용화되었으나, 그 architecture, capability, PCIe/CXL Type-3 대비 성능 특성이 시스템 커뮤니티에 충분히 이해되지 않음.

2. **기여:**
   - CXL Type-2 device의 **세 가지 cache-coherent memory access**(D2H, D2D, H2D)에 대한 architecture-level 분석.
   - **Comprehensive microbenchmarking:** D2H (5가지 request type × LLC hit/miss), D2D (host-bias/device-bias × DMC hit/miss), H2D (Type-2 vs. Type-3), CXL vs. PCIe (MMIO/DMA/RDMA) 전반.
   - **End-to-end use case:** Linux kernel memory optimization(zswap, ksm)의 device ACC offload → CPU- 및 PCIe-based 구현 대비 우수성 입증.

3. **결과:**
   - cxl-zswap: cpu-zswap의 **8.1× tail latency 증가**를 **1.20×**로 감소, offloading latency **64%** 감소.
   - cxl-ksm: cpu-ksm의 **5.4× tail latency 증가**를 **1.16×**로 감소.
   - Coding complexity: PCIe-RDMA(1,300 LoC) 대비 CXL(20–50 LoC)로 대폭 단순화.

4. **의의:** CXL Type-2 device의 fine-grained CHC capability가 datacenter latency-sensitive application의 kernel feature offloading에 실질적 혜택을 제공함을 최초로 입증. 향후 CXL 기반 accelerator 설계와 system software 연구의 기초 자료로 활용 가능.

## 주요 결과

CXL Type-2의 fast cache-coherent D2H/H2D access를 활용해 Linux kernel memory optimization feature(zswap, ksm)의 data-plane을 device ACC로 offload.

### 4.1 CXL-based zswap (cxl-zswap, Fig.7)

**zswap 개요:** Linux kswapd의 swap page를 압축하여 DRAM 내 zpool에 저장 → 실제 backing device I/O 회피.

**cxl-zswap 구현:**
1. kswapd가 LRU page source addr + zpool dest addr을 device memory의 shared region에 nt-st로 전달 → host cache pollution 회피.
2. Device ACC: D2D CS-read로 shared region polling → addr 수신.
3. kswapd: 즉시 CPU core yield → co-running application에 양보 (~10µs sleep).
4. Device ACC:
   - NC-read(최저 latency)로 host → device 4KB page transfer.
   - FPGA compression IP로 압축 (CPU 대비 1.8–2.8× faster).
   - NC-write로 compressed page를 **device memory의 zpool에 직접 저장** (PCIe 대비 추가 transfer 불필요).
   - 2), 4), 5) pipeline 처리 (streaming compression + cache-line granularity transfer).
5. Completion: compressed page size를 shared region에 D2D NC-write → kswapd wakeup → control-plane 완료.

**Decompression:** D2D CS-read로 compressed page fetch → decompress → D2H NC-P로 decompressed page를 host LLC에 직접 push → host의 H2D read가 LLC hit으로 처리.

**FPGA utilization:** 32% LUTs.

### 4.2 CXL-based ksm (cxl-ksm)

**ksm 개요:** VM 간 동일 content page를 deduplication → physical memory 용량 효율화.

**cxl-ksm 구현:**
- xxhash checksum computation + byte-by-byte page comparison을 device ACC에서 hardware로 수행.
- D2H NC-read로 page transfer + comparison pipelining.
- Completion: 결과를 D2H NC-P로 host LLC에 직접 반환.

**FPGA utilization:** 23% LUTs.

### 4.3 Coding Complexity

| Implementation | LoC Modification |
|---------------|-----------------|
| cxl-ksm | ~20 LoC |
| cxl-zswap | ~50 LoC |
| pcie-rdma-* (STYX [32]) | ~1,300 LoC |

CXL ld/st 기반의 단순한 interface가 PCIe RDMA verbs 대비 훨씬 적은 코드 수정으로 구현 가능.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]


## 전체 요약

[[../paper-summaries/2024MICRO-summarize/demystifying-a-cxl-type-2-device-a-heterogeneous-cooperative-computing-perspective.md|전체 요약 보기]]
