---
tags: [paper, 2024, 2024MICRO, topic/cache, topic/disaggregation, topic/dram, topic/memory-tiering, topic/virtual-memory]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024MICRO-summarize/neomem-hardware-software-co-design-for-cxl-native-memory-tiering.md"
---

# NeoMem: Hardware/Software Co-Design for CXL-Native Memory Tiering

**Venue:** 
**저자:** 

## 개요

CXL(Compute Express Link)은 PCIe 5.0 물리 계층 위에서 cache-coherent, byte-addressable interconnect를 제공하며, CXL.mem 프로토콜을 통해 CPU가 CXL 메모리 디바이스를 load/store 명령으로 직접 접근할 수 있게 한다. 이로 인해 DDR DRAM(로컬 fast tier)과 CXL memory(slow tier) 간 heterogeneous memory system이 자연스럽게 형성된다[Fig.1].

**성능 격차:** Intel FPGA 기반 CXL 메모리 프로토타입에서 latency 측정 결과, CXL 메모리는 약 430 ns로 로컬 DDR5 DRAM(약 118 ns) 대비 약 3.6× 높은 latency를 보인다[Fig.3(a)]. 실제 워크로드에서 CXL 메모리만 사용 시 Redis에서 64%에서 Page-Rank에서 295%까지 slowdown 발생[Fig.3(b)].

기존 memory tiering의 핵심은 hot page detection이며, 기존 세 가지 기법 모두 근본적 한계를 가진다:

1. **PTE-scan:** 주기적으로 Page Table Entry의 Accessed bit를 리셋 후 스캔. epoch당 page당 1회 access만 감지 가능(low time resolution). DAMON 등으로 region sampling하면 space resolution이 희생됨. 대규모 메모리에서 scan 수 초 소요[Fig.4(a)].
2. **Hint-fault monitoring (TPP, AutoNUMA):** PTE에 protection bit을 설정하여 접근 시 page fault 유발. TLB shootdown + page fault overhead로 인해 sampling 불가피 → 낮은 coverage. 또한 TLB miss만 추적하므로 true LLC miss와 correlation이 약함[Fig.4(b)].
3. **PMU sampling (PEBS):** LLC miss를 직접 추적 가능. 그러나 sampling interval을 10,000에서 10으로 줄이면 50% 이상 slowdown[Fig.4(c)]. 낮은 sampling frequency 사용 시 resolution 희생. CPU vendor-specific (Intel PEBS ≠ AMD IBS).

Linux 커뮤니티에서도 "The biggest problem for memory tiering still appears to be page promotion (when a page has become hot)"이라는 consensus가 형성되어 있음.

---

## 방법론

### 3.1 전체 아키텍처 개요

NeoMem의 핵심 아이디어: **memory profiling을 CPU에서 CXL device-side controller의 전용 하드웨어 유닛(NeoProf)으로 offload**[Fig.5].

- **NeoProf (HW):** CXL memory controller 내 하드웨어 유닛. CXL channel을 통해 들어오는 memory access request를 snoop하여 page 단위로 분석. Hot page detection + state monitoring 수행.
- **NeoProf Driver (Kernel):** MMIO를 통해 NeoProf와 통신. Command(Table II)를 전송하고 statistics를 읽어옴.
- **NeoMem Daemon (Kernel):** NeoProf에서 hot page 정보를 주기적으로 읽어 page migration(promotion) 수행. Cold page demotion은 기존 Linux LRU 2Q 메커니즘 활용.
- **Migration Policy (User space):** `/sys/kernel/mm/neomem` 인터페이스를 통해 동적 threshold 조정 수행.

### 3.2 NeoProf 하드웨어 — Hot Page Detector [Fig.6,7,8]

**Strawman 접근과 실패 이유:** 512GB CXL memory expander 기준 128M개의 4KB page. 각 page에 32-bit counter 할당 시 512MB buffer 필요. 매 access마다 counter update 시 DRAM bandwidth 부담, hot page 식별 위한 전체 counter scan latency 큼.

**채택된 방식 — Count-Min Sketch 기반 [Fig.7]:**

CM-Sketch는 parameters (ε, δ)로 구성되며, width W = ⌈2/ε⌉, depth D = ⌈log₂(1/δ)⌉의 2D array `A[1..D][1..W]`. 각 entry는 **counter**(16-bit) + **hot bit**(1-bit) + **valid bit**(1-bit)로 구성.

Page address P가 도착하면, D개 독립 hash function {h₁, …, h_D}로 각 lane에서 offset Δᵢ = hᵢ(P) 계산 후:

```
A[i][Δᵢ] ← A[i][Δᵢ] + 1   (for i ∈ [1, D])
```

추정 access frequency:

```
â(P) = min(A[1][Δ₁], A[2][Δ₂], …, A[D][Δ_D])   (Eq.2)
```

Error bound (with probability 1 − δ):

```
a(P) ≤ â(P) ≤ a(P) + εN   (Eq.3, N=total accesses)
```

**Hot page 판정 (Eq.4):** threshold θ에 대해 `â(P) > θ` → hot page.

**Hot-Page Filtering (중복 방지):** sketch entry의 Hot bit들을 Bloom filter처럼 활용. 모든 hashed entry의 Hot bit가 True면 이미 기록된 page로 간주하여 skip. 하나라도 False면 새로운 hot page → Hot bits set 후 hot page buffer로 전송.

**Pipeline 구조 [Fig.8]:** 3-stage pipeline — (1) Hash index computation (H3 hash, M-stage reduction tree), (2) Hot page checking (counter update + threshold 비교), (3) Hot page filtering. Sketch array는 K개 memory sub-block으로 분할하여 pipelined access.

### 3.3 Error-Bound Estimation — Histogram 기반 [Fig.9]

단순히 sketch array 전체를 읽어 sort하면 CXL channel 대역폭 낭비 + CPU cycle 소모. NeoProf Core에 **64-bin Histogram Unit**을 내장.

1. Host CPU가 `SetHistEn` command로 histogram 계산 trigger
2. Histogram unit이 첫 번째 row의 counter들을 읽어 frequency distribution 추정
3. Host는 `GetHist`로 histogram bin만 읽고, 간단한 알고리즘으로 p-percentile frequency 계산

Tight error bound `e`는 sorted counters의 (W · ⌈δ^(1/D)⌉)-percentile 값으로 결정. `â(P) > θ`이면 `a(P) > θ − e` 보장.

### 3.4 NeoMem Migration Policy — 동적 Threshold 조정 [Algorithm 1]

고정 threshold의 한계(workload phase 변화 대응 불가)를 극복하기 위해, NeoProf의 rich profiling 정보를 기반으로 **매 threshold update period마다** hotness threshold θ를 동적 조정.

**입력 변수:**
- `F`: NeoProf histogram → access frequency distribution (line 4)
- `B`: bandwidth utilization = (read_cycles + write_cycles) / total_cycles (line 5)
- `P`: ping-pong severity = #ping-pong_events / #promoted_pages (line 6)
- `E`: estimated error bound (line 7)
- `M`: 직전 period의 migrated pages 수 (line 8)

**동작 알고리즘:**

```
p ← p_init  (top p% pages를 hot으로)
while enabled:
    F ← histogram, B ← bandwidth util, P ← ping-pong count, E ← error bound, M ← migrate count

    if M < m_quota:  // migration quota 미달 시 threshold 낮춤
        p ← p · (1+B)^α / (1+P)^β
        p ← bound(p_min, p_max, p)
    else:             // quota 초과 시 threshold 높임
        p ← max(p_min, p/2)

    if QF(1−p) < E:   // error bound가 threshold 초과 → 신뢰도 낮음
        p ← max(p_min, p/2)

    θ ← QF(1−p)       // top-p access frequency를 새 threshold로
    update threshold(θ)
    wait(period)
```

**직관:**
- **Access frequency↑** → p 감소 → θ 낮춤 → 더 많은 page를 hot으로 분류
- **Bandwidth utilization↑** (B↑) → θ ∝ 1/B → 더 많은 page promotion → fast tier 활용
- **Ping-pong severity↑** (P↑) → θ ∝ P → threshold 높여 불필요한 migration 억제
- **Error bound > threshold** → sketch saturation 의심 → p/2로 threshold 높임
- **Migration quota (m_quota)** 초과 → threshold 높여 migration 양 제한

---

## 핵심 기여

**핵심 Contribution:**
1. CXL device-side controller에 전용 하드웨어 profiler(NeoProf)를 통합하는 **CXL-native memory tiering** 개념 제안 — host CPU 수정 불필요, drop-in compatibility
2. Count-Min Sketch 기반의 **고해상도·저오버헤드 hot page detector** 설계: per-access granularity profiling, hot-page filtering으로 중복 제거, histogram 기반 error-bound estimation
3. 풍부한 profiling 정보(access frequency distribution, bandwidth util, ping-pong severity, error bound)를 활용하는 **동적 hotness threshold 조정 알고리즘**
4. Real FPGA CXL platform + Linux v6.3에서의 **end-to-end 프로토타입 검증**

**Broader Significance:**
- 기존 profiling 기법(PTE-scan/hint-fault/PMU)의 근본적 한계를 해결하는 새로운 패러다임 제시
- CXL 생태계 확장에 따라 device-side intelligence의 가치를 입증
- Future work: virtualization 지원, multi-device scalability, memory interleaving 상황에서의 profiling 통합

## 주요 결과

### 4.1 하드웨어 (NeoProf)

- **Description:** Verilog, Intel Agilex 7 I-Series FPGA (Quartus 22.3 합성)
- **Parameters (default):** W = 512K, D = 2, counter = 16-bit, 128 pipeline stages, hot page buffer = 16K entries, 32-bit page address (최대 16TB per controller)
- **FPGA resource:** 93.8K ALMs (10%), 1.5K BRAMs/M20K (12%), DSP 미사용[Fig.10(a)]
- **ASIC estimation (TSMC 22nm):** 5.3 mm² area, 152.2 mW power @ 400MHz, 0.8V. SRAM macros 54% of area (sketch array, hot-bit array, hot-page buffer)[Fig.18]

### 4.2 소프트웨어

- **Base:** Linux kernel v6.3
- **NeoMem driver + daemon:** kernel space. Hot page promotion은 kernel `migrate_pages()` 함수 활용
- **User-space interface:** `/sys/kernel/mm/neomem/` — threshold, migration_interval, clear_interval 등 설정
- **Default parameters (Table V):**
  - `migration_interval`: 10ms
  - `clear_interval`: 5s (NeoProf counter reset 주기)
  - `thr_update_interval`: 1s
  - `p_min`: 0.01%, `p_max`: 1.56%, `p_init`: 0.1%
  - `m_quota`: 256 MB/s
  - `α/β`: 1/2

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2024MICRO-summarize/neomem-hardware-software-co-design-for-cxl-native-memory-tiering.md|전체 요약 보기]]
