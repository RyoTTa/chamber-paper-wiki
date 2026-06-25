---
tags: [paper, 2025, 2025MICRO, topic/cache, topic/disaggregation, topic/dram]
venue: "MICRO 2025"
year: 2025
summary_path: "../paper-summaries/2025MICRO-summarize/re-architecting-end-host-networking-with-cxl-coherence-memory-and-offloading.md"
---

# Re-architecting End-host Networking with CXL: Coherence, Memory, and Offloading

**Venue:** MICRO 2025
**저자:** Houxiang Ji, Yifan Yuan, Yang Zhou, Ipoom Jeong, Ren Wang, Saksham Agarwal, Nam Sung Kim (UIUC/Meta/Yonsei/Intel)

## 개요

기존 PCIe 기반 NIC는 두 가지 구조적 한계를 가짐:
1. **DMA-only D2H 통신.** NIC → host CPU 간 데이터 전송은 DMA를 통해서만 가능. DMA는 setup/completion overhead로 인해 64B descriptor 교환 같은 frequent, small-size transfer에 비효율적. 64B 소형 패킷 기준 PCIe operation이 전체 loopback latency의 **52%**를 차지 (100+ Gbps line rate에서 sub-μs delay가 치명적).
2. **No shared memory / cache coherence.** Host CPU → NIC 방향은 MMIO만 지원: 512B transfer에 **>8 μs** latency, bandwidth **<0.3 GB/s**. Software-managed synchronization (explicit cache flush, memory pinning, memory barrier)이 필수 — 복잡도와 latency 모두 증가.

CXL은 PCIe physical layer 위에 hardware-managed unified memory + cache coherence를 제공하는 개방형 표준. 특히 **CXL Type-1/2 device**에서 제공하는 **CXL.cache** 프로토콜이 PCIe의 근본적 한계를 해결할 수 있으나, 기존 연구는 Type-3 memory expander에 집중되어 Type-1/2의 coherence 잠재력은 충분히 탐구되지 않음.

**Motivation data:**
- DPDK loopback 실측 결과: 64B packet에서 PCIe operation이 total latency의 **52%**, 1500B에서 **45%** 차지 (Figure 3)
- Throughput 1 → 64 Gbps 구간에서도 PCIe fraction은 57% → 52%로 소폭 감소할 뿐
- CXL.cache vs. PCIe microbenchmark (Figure 4):
  - CXL D2H NC-write (Rx) latency: PCIe DOCA-DMA 대비 **69% 감소** (64B)
  - CXL D2H NC-read (Tx) latency: DOCA-DMA 대비 **81% 감소** (64B)
  - Descriptor read: CXL NC-read가 PCIe DMA-read 대비 **85% 감소**
  - Completion signaling: CXL NC-write가 PCIe DMA-write 대비 **82% 감소**
  - H2D signaling: CXL NC-read polling이 MMIO write 대비 **29% 감소**
- CXL.mem H2D ld/st vs. MMIO: latency **5.6×/4.5× 감소** (Figure 7)

## 방법론

### 1. Type-1 CXL-NIC: Coherence-driven Datapath

**아키텍처 (Figure 5):** 4개 핵심 컴포넌트:
- **Network interface:** Ethernet MAC — bidirectional packet I/O
- **DMU (Descriptor Management Unit):** RxD/TxD fetch, packet buffer address extraction, descriptor status update. DCOH와 별도 port로 연결.
- **PFU (Packet Forwarding Unit):** 1 MB SRAM 버퍼 포함. DMU가 제공한 packet buffer address로 NC-write/NC-read 수행.
- **CSR/MMIO space:** CXL.io를 통해 host memory에 mapping — 초기화 및 runtime configuration에만 사용 (infrequent control).

**Rx datapath:**
1. Host CPU가 RxD ring buffer + packet buffers를 host memory에 할당하고 CXL.io로 DMU에 base address 설정
2. DMU가 **D2H CS-read**로 가용 RxD를 HMC (Host Memory Cache)에 prefetch (Shared state — read-only access에 최적)
3. Packet arrival 시 DMU가 HMC로부터 RxD를 **CO-read**로 획득 (Owned state, 3.3× faster than host DRAM)
4. PFU가 **D2H NC-write**로 packet을 host packet buffer에 direct write (device cache bypass → cache pollution 방지)
5. DMU가 **D2H NC-write**로 RxD status update (CO-read로 이미 ownership 확보 → race condition 없음)
6. Host CPU가 RxD polling → application delivery → buffer reclaim

**Tx datapath:**
1. **Tail index를 host memory에 유지** (PCIe NIC은 device register), host CPU가 st instruction으로 갱신
2. Host CPU가 packet buffer 할당 + pack + TxD ring buffer에 삽입 후 tail index st update (batching 지원)
3. DMU가 **D2H CO-read**로 tail index polling — cached in Owned state → host update 시 자동 invalidation → event-driven Tx path (Figure 6)
4. Tail 변화 감지 시 DMU가 TxD를 **NC-read**로 fetch → packet buffer address 추출
5. PFU가 **D2H NC-read**로 packet fetch 후 전송
6. DMU가 **D2H NC-write**로 TxD completion update → host가 buffer reclaim

### 2. Cache Line State Control Optimization (§4.3)

CXL.cache의 4가지 request type (NC, NC-P, CS, CO)을 datapath 단계별로 전략적으로 선택:

| Operation | Request | Rationale |
|---|---|---|
| **RxD prefetch** | CS-read | Shared state caching (read-only before arrival), no ownership overhead |
| **TxD polling** | CO-read | Owned state → local poll without CXL traffic until host update → 자동 invalidation |
| **Rx packet transfer** | NC-write | Device cache bypass → packet copy 미존재 → cache pollution 방지 |
| **Tx packet transfer** | NC-read | Device cache bypass → host buffer 재사용 시 invalidation traffic 없음 |
| **RxD/TxD completion** | NC-write | CO-read로 이미 ownership 확보, NC-write가 cached descriptor 자동 invalidate |

**CC-NIC [ASPLOS'24] 대비 차별점:**
- CC-NIC은 UPI coherence에 의존 → software CLFLUSH로 Tx buffer cache copy 제거 필요 → global buffer pool 강제 → multi-pool/scalability 제약
- CXL-NIC은 NC-read/write로 cache bypass → CLFLUSH 불필요 → per-queue/tenant buffer pool 자유롭게 할당 가능

### 3. Type-2 CXL-NIC: Coherent NIC Memory (§5)

CXL Type-2 device = Type-1 + CXL.mem (coherent device DRAM). Host CPU가 **ld/st**로 NIC memory에 cache line granularity access → NIC memory가 remote NUMA node로 인식됨.

**데이터 배치 유연성 (Figure 8):** Producer-consumer model 기반 4가지 배치 패턴:
- (a) Producer=CPU, buffer in **host memory**
- (b) Producer=CPU, buffer in **NIC memory**
- (c) Consumer=CPU, buffer in **host memory**
- (d) Consumer=CPU, buffer in **NIC memory**

각 경우 cache-based path (CPU LLC ↔ NIC cache)와 memory-based path (nt-st bypass + D2H/D2D read)의 조합으로 2가지 datapath 존재.

**Key asymmetry:**
- **Device-bias mode:** Device-local D2D access가 host coherence check bypass → low latency
- **Hardware heterogeneity:** Agilex-7 FPGA @400 MHz ≪ host CPU → H2D/D2H asymmetric
- CC-NIC은 UPI의 symmetric NUMA coherence 가정 → CXL-NIC은 device-bias + heterogeneity를 명시적으로 고려

**Naive NIC-memory placement 위험 (Figure 13):**
Rx/Tx packet buffer를 NIC memory에 단순 배치할 경우 (L2-L4), L1(all host) 대비 median latency:
- L2 (Rx NIC, Tx host): **23% 증가** (64B)
- L3 (Rx host, Tx NIC): **54% 증가** (64B)
- L4 (both NIC): **71% 증가** (64B)

원인: (1) CPU가 CXL interconnect를 통해 NIC memory 접근, (2) host-bias mode coherence protocol overhead. → Uninformed placement는 오히려 성능 저하.

## 핵심 기여

CXL-NIC은 PCIe NIC의 근본적 한계 (non-coherent DMA/MMIO, no shared memory)를 CXL.cache + CXL.mem으로 해결하는 최초의 end-host networking re-architecture. 핵심 기여:

1. **CXL.cache cache line state control** (NC/CS/CO)을 datapath 단계별로 전략적 매핑 → low latency + minimal coherence overhead
2. **Type-2 NIC memory**의 asymmetric placement 최적화 → device-bias mode + NC-P로 latency-optimal configuration 도출
3. **NC-P adaptive gating**으로 LLC pollution을 제어하면서 cache injection benefit 유지
4. **FPGA prototype**으로 실현 가능성 입증: packet loopback tail latency **49% 감소**, KVS tail latency **39% 감소**

Broader significance: CXL의 개방형 coherence model이 proprietary UPI 기반 CC-NIC보다 우수함을 실험적으로 증명, 차세대 data center networking architecture의 foundational design space를 제시.

## 주요 결과

CXL 고유의 **NC-P write**: DCOH가 cache line을 DMC에 update한 후 **host LLC로 push** 후 device cache에서 invalidate.

**문제:** DDIO와 유사하게 과도한 cache injection이 LLC saturation 유발 → 미처리 데이터 eviction ("leaky DMA" problem).

**CXL-NIC의 adaptive NC-P:**
1. **Adaptive push-write gating:** Runtime configurable flag register (host CPU가 CXL.io로 설정). LLC utilization threshold 초과 시 NC-P disable → NC-write로 fallback.
2. **Post-push write-back:** NC-P 후 **N cycles delay** 뒤 동일 address로 delayed NC-write → host LLC에서 invalidate 후 device memory로 write-back. N 값은 workload에 따라 host CPU가 tuning.

**사용 사례 (Figure 8d):** RxD completion을 NIC memory에 기록 후 NC-P로 host LLC에 push → host ld latency 감소. 단, N window 내에 host가 접근하지 않으면 benefit 상실.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2025MICRO-summarize/re-architecting-end-host-networking-with-cxl-coherence-memory-and-offloading.md|전체 요약 보기]]
