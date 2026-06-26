---
tags: [paper, 2023, 2023MICRO, topic/cache, topic/nvm, topic/storage]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023MICRO-summarize/sweepcache-intermittence-aware-cache-on-the-cheap.md"
---

# SweepCache: Intermittence-Aware Cache on the Cheap

**Venue:** 
**저자:** 

## 개요

**Energy Harvesting Systems:**
- RF, WiFi 등 불안정한 ambient 에너지원으로 동작 → frequent & unpredictable power failure → **intermittent computation**.
- 전통적 해결책: NVM main memory + Nonvolatile Processor (NVP) with JIT (Just-In-Time) checkpointing.
- JIT: voltage monitor로 impending power failure 감지 → NVFF에 register backup → wake-up 시 복원.

**Motivation - Cache 도입의 필요성과 어려움:**
- Cache-free NVP의 한계: 모든 memory access가 NVM으로 → NVM access는 SRAM 대비 **수 배 높은 latency와 energy 소비**.
- SRAM cache 도입 시 문제: power failure 시 모든 volatile data (dirty cacheline 포함) 소실 → 단순 register 복원으로는 crash consistency 보장 불가.

**기존 접근법의 한계:**

| 접근법 | 문제점 |
|--------|--------|
| **Write-through cache** | 모든 store가 NVM write 동반 → 긴 store latency, 높은 energy 소비 |
| **NVSRAM (JIT cache backup)** | NVM backup storage 필요 → 32KB cache에 **4.8× area overhead**; capacitor degradation으로 failure-atomicity 위협; 큰 inrush current |
| **ReplayCache** | Per-store clwb → persist coalescing 상실, write amplification; 모든 store에 fence; JIT 의존성 여전히 존재 |

**Capacitor degradation 문제:**
- 7일 사용 시 capacitor 출력 **90%**로 감소 → 대비 위해 voltage threshold 상향 필요.
- Threshold 20% 증가 → **1.4× slowdown**. 40% 증가 → **2.5× slowdown**.

**Propagation delay 문제:**
- JIT의 voltage detector: backup 1.5 μs + restore 10.3 μs (20 μA).
- SweepCache의 simpler comparator: restore only 1.1 μs (12 μA).

## 방법론

### 3.1 Methodology

| 항목 | 구성 |
|------|------|
| **Simulator** | gem5 + ARM ISA, single-core in-order |
| **Cache** | L1D: 4KB, 2-way, 64B block (default) |
| **NVM** | 16MB ReRAM, write 120ns / read 20ns |
| **Capacitor** | 470 nF (실제 fabricated chip과 동일) |
| **Persist buffer size** | 64 entries × (addr + 64B data) |
| **Compiler** | LLVM 13.0.1 + MUSL C library |
| **Workloads** | MiBench(adpcm, g721, gsm, jpeg, mpeg2, pegwit, sha, susan) + Mediabench(basicmath, blowfish, dijkstra, fft, ifft, patricia, rijndael, typeset) = 총 26개 |
| **Power traces** | RFHome, RFOffice, solar, thermal (실제 수집) |
| **Baselines** | NVP (cache-free), ReplayCache, NVSRAM (dirty-only backup), NVSRAM-E (full backup), NvMR |

### 3.2 Power-Outage-Free Performance (Figure 5)

| Design | Speedup over NVP |
|--------|-----------------|
| ReplayCache | 5.10× |
| SweepCache (NVM Search) | 8.80× |
| SweepCache (Empty-Bit, default) | **8.91×** |
| NVSRAM | **11.53×** |

SweepCache vs. ReplayCache: **1.75× speedup** (Empty-Bit 기준).

**ReplayCache가 이 paper보다 낮은 이유:** libraries까지 compile했기 때문 (원논문은 application code만). SweepCache의 clwb/fence 제거 효과가 두드러짐.

Empty-Bit vs NVM Search: 1.18% 추가 speedup (cache miss rate가 너무 낮아 buffer search 빈도가 적기 때문).

### 3.3 Power-Outage Performance

**RFHome trace (Figure 6):**

| Design | Speedup over NVP |
|--------|-----------------|
| ReplayCache | 4.26× |
| NVSRAM | 7.37× |
| SweepCache (NVM Search) | 14.60× |
| SweepCache (Empty-Bit) | **14.86×** |

SweepCache vs. ReplayCache: **3.49× speedup**.

**RFOffice trace (Figure 7):**

| Design | Speedup over NVP |
|--------|-----------------|
| ReplayCache | 4.20× |
| NVSRAM | 7.32× |
| SweepCache (NVM Search) | 14.31× |
| SweepCache (Empty-Bit) | **14.60×** |

SweepCache vs. ReplayCache: **3.47× speedup**.

**JIT-checkpoint-free의 성능 우위 원인:**
- No hard-won energy for JIT backup → 더 많은 harvested energy가 computation에 사용 → **power failure 빈도 감소** (Table 2).
- No NVFF, backup/restore controller overhead.
- 더 짧은 propagation delay (restoration 1.1 μs vs 10.3 μs).

### 3.4 Sensitivity Studies

**Cache size (Figure 8):**
- 512B → 16KB로 증가 시 성능 비례 향상.
- SweepCache가 모든 cache size에서 ReplayCache, NVSRAM 능가.

**Capacitor size (Figure 9, Table 2):**

| Capacitor | NVP outages | SweepCache outages |
|-----------|-------------|-------------------|
| 100 nF | 458.26 | **34.11** |
| 470 nF | 144.65 | **14.42** |
| 1 μF | 50.85 | **6.23** |
| 10 μF | 7.23 | **0.35** |

- SweepCache가 동일 capacitor에서 항상 더 적은 outage 수 → 더 높은 에너지 효율.
- 1 μF SweepCache ≈ 10 μF NVSRAM 성능 (area cost 1.43× 절감).

**Power traces (Figure 10):**
- RF trace: SweepCache가 최고 성능 (power failure 빈도 높을수록 유리).
- Solar/thermal: NVSRAM 성능 접근 (안정적 전원에서는 JIT overhead 감소).

**Propagation delay (Figure 11):**
- SweepCache delay를 JIT 수준으로 늘리거나, JIT delay를 최소로 줄여도 SweepCache의 우위는 capacitor size에 따라 유지.

### 3.5 Energy Efficiency (Figure 13)

Normalized total energy (vs. NVP):
- ReplayCache: **20.86%**
- NVSRAM: **12.37%**
- SweepCache: **10.21%**

Backup/restore energy: SweepCache **0.28%** vs. ReplayCache 23.74%, NVSRAM 15.42%.

### 3.6 Write Amplification (Figure 16)

- SweepCache NVM writes: NVSRAM 대비 **4.62×** (region-level persistence의 double write).
- 그러나 NVM write는 전체 에너지의 **0.23%**에 불과 → parallelism으로 latency hiding.

### 3.7 Region Size & Store Count (Figure 12)

- Average region size: **19.47 instructions**.
- Average stores per region: **3.92**.
- Threshold=64 대비 매우 낮은 utilization → persist buffer empty 상태 설명.

### 3.8 Cache Miss Rate (Figure 15)

- SweepCache cache miss rate: NVSRAM 대비 **7.50% 증가**뿐 (power outage 수가 적어 cold miss 감소).

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

- **Compiler:** LLVM 13.0.1 + region partitioning, live-out checkpointing, loop unrolling, callsite boundary placement.
- **Architecture:** 2 persist buffers (NVM-resident), 2 empty-bits, 4 phaseComplete bits, 2×64-bit write-back-instructive SRAM tables (4KB cache 기준 total **134 bits** 추가).
- **DMA:** Commodity MCU (MSP430 시리즈)의 DMA 활용 → buffer→NVM transfer에 CPU 개입 없음.
- **Hardware cost:** Minimal — JIT 대비 NVFF, NVSRAM backup storage, voltage monitor complexity 모두 제거.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2023MICRO-summarize/sweepcache-intermittence-aware-cache-on-the-cheap.md|전체 요약 보기]]
