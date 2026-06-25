---
tags: [paper, 2023, 2023ISCA, topic/cache]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023ISCA-summarize/emissary-enhanced-miss-awareness-replacement-policy-for-l2-instruction-caching.md"
---

# EMISSARY: Enhanced Miss Awareness Replacement Policy for L2 Instruction Caching

**Venue:** 
**저자:** 

## 개요

### 1.1 Not All Cache Misses Are Equal

기존 cache replacement policy는 miss count 최소화에 집중했으나, 모든 cache miss가 동일한 성능 비용을 갖지 않는다. 현대 OoO 프로세서의 aggressive front-end는 많은 L1I miss를 완전히 tolerate할 수 있다. Decoupled front-end + FDIP(Fetch-Directed Instruction Prefetching)는 branch predictor, BTB, pre-decoder를 통해 decode stage보다 수십~수백 instruction 앞서 fetch하므로, 상당수의 L1I miss가 **decode starvation 없이** 처리된다.

- FDIP baseline만으로도 **33.1% geomean speedup** (no-FDIP 대비)
- 이 FDIP baseline 위에서 추가 개선은 매우 어려움 — prior work에서 perfect prefetcher조차 5.4% gain에 불과

### 1.2 Cost-Aware Replacement의 부재 (Instruction Cache)

기존 cost-aware cache replacement(LIN, LACS, Critical Cache 등)은 모두 **data cache**를 대상으로 설계됨. Instruction fetch는 data access와 근본적으로 다른 패턴을 보이므로 그대로 적용 불가.

### 1.3 Decode Starvation Behavior의 특성 (Figure 2)

Reuse distance 분석 (13개 datacenter workload):

| Reuse Category | Distance | L2 behavior | % of Accesses | % of Starvation Cycles |
|---|---|---|---|---|
| **Short** | [0-100) | L1I hit | ~50% | <5% |
| **Mid** | [100-5000) | L1I miss, L2 hit | ~30% | <5% |
| **Long** | [>5000) | L2 miss | <20% | **>90%** |

핵심 통찰: L2 miss를 일으키는 Long Reuse line은 전체 access의 20% 미만이지만 **전체 starvation cycle의 90% 이상**을 유발 → 소수의 cache line에 priority를 집중하는 전략이 유효.

---

## 방법론

### 3.1 Methodology Overview

| 항목 | 내용 |
|---|---|
| **Simulator** | gem5 Full System (cycle-accurate), Alderlake-like model |
| **ISA** | Aarch64 (64-bit ARM) |
| **Cache Hierarchy** | L1I: 32KB 8-way, L1D: 64KB 8-way, L2: 1MB 16-way unified (inclusive), L3: 2MB 16-way exclusive victim |
| **Front-end** | FDIP with TAGE/ITTAGE predictor, 16K entry BTB, 24-entry FTQ (192-instruction buffer) |
| **Core Config** | 8-wide fetch/decode/issue/commit, 512 ROB, 240 IQ |
| **Baseline** | TPLRU + FDIP |
| **Benchmarks** | 13 datacenter workloads: tomcat, kafka, tpcc, wikipedia, data-serving, media-stream, web-search, xapian, specjbb, finagle-http, finagle-chirper, verilator, speedometer2.0 |
| **Code Footprint** | Average 1.05MB (0.29MB~2.57MB) |
| **Metrics** | Speedup, L2 Instruction MPKI, decode starvation reduction, energy (McPAT), stall breakdown |

### 3.2 Parameter Selection (Table 5)

`r`과 `N`에 대한 sweep 결과:
- **Best `r` = 1/32** (prior work BIP와 일치)
- **Best `N` = 8** (16-way cache의 절반). verilator만 `N=14`까지 계속 개선
- `P(8):S&E&R(1/32)`가 가장 많은 benchmark에서 best

### 3.3 Performance: Speedup vs Baseline (Figure 5, Figure 7)

| Policy | Geomean Speedup | Max Speedup |
|---|---|---|
| M:0 (LIP) | -0.35% | — |
| M:R(1/32) (BIP) | +0.05% | — |
| SRRIP | -2.48% | — |
| BRRIP | -2.90% | — |
| DRRIP | -3.36% | — |
| PDP | -3.36% | — |
| DCLIP | -2.48% | — |
| P(8):S&E | +1.29% | — |
| **P(8):S&E&R(1/32)** | **+2.49%** (all 13) / **+3.24%** (12, tpcc 제외) | **+23.7%** |

- `P(8):S&E&R(1/32)`가 가장 우수. Random filter가 추가되어 `P(8):S&E` 대비 개선
- tpcc는 L2 instruction MPKI가 매우 낮아 제외 시 geomean speedup 3.24%

### 3.4 Contextualizing the Gains (Section 5.6)

| 기준 | Speedup |
|---|---|
| FDIP over no-FDIP | 33.1% |
| Perfect Prefetcher over FDIP | 5.4% |
| EIP-128KB Prefetcher over FDIP | 4.3% (128KB storage) |
| Zero-cycle L2 Inst Miss Latency (unrealizable) over FDIP | 15.0% |
| **EMISSARY over FDIP** | **3.24% (4KB storage)** |
| EMISSARY / Unrealizable Ideal | **21.6%** |

### 3.5 Decode Starvation Reduction (Figure 5, even rows)

`N` 증가에 따라 starvation cycle이 monotonic하게 감소. P(8):S&E&R(1/32)는 최대 50% starvation 감소 (verilator).

### 3.6 MPKI Behavior (Figure 5, odd rows)

- 일부 benchmark에서 MPKI도 함께 감소 (EMISSARY가 불필요한 single-reference line을 low-priority로 분류 → cache pollution 감소)
- 그러나 대부분의 speedup gain은 **MPKI 변화 없이** starvation reduction에서 발생 — 전형적인 cost-aware replacement 효과

### 3.7 Front-End vs Back-End Stall Breakdown (Figure 6)

P(8):S&E&R(1/32) 적용 시:
- **Front-end stall**: 평균 감소 (starvation 감소의 직접적 효과)
- **Back-end stall**: 일부 benchmark에서 증가 (L2를 instruction line이 더 점유 → data line capacity 감소) — 그러나 total stall은 감소

### 3.8 Cache Set Saturation Analysis (Figure 8)

`P(8):S&E`는 finagle-chirper, tomcat, tpcc, verilator에서 **모든 set이 saturation** (high-priority 8개). 반면 `P(8):S&E&R(1/32)`는 set의 25% 미만만 saturation → random filter가 과도한 protection을 방지. 128M instruction마다 priority bit reset으로 saturation 관리 가능 (성능 영향 negligible).

### 3.9 Energy Savings (Figure 7)

| Policy | Geomean Energy Reduction | Max Energy Reduction |
|---|---|---|
| **P(8):S&E&R(1/32)** | **2.12%** | **17.67%** |

Energy saving은 speedup과 강한 correlation. 추가 hardware(2 bits/line)가 미미하기 때문.

---

## 핵심 기여

### Contributions
1. **최초의 instruction-specific cost-aware replacement policy**: Decode starvation을 cost signal로 활용. Bimodal selection + persistent treatment의 orthogonal decomposition으로 policy space를 체계화
2. **Persistence 개념 도입**: Priority를 insertion 시점뿐 아니라 line의 **전체 cache lifetime** 동안 유지 → `M` (short-lived bimodality) 대비 근본적 우위
3. **FDIP baseline 위에서 3.24% speedup**: 이미 aggressive front-end로 최적화된 baseline에 대해, unrealizable ideal L2 cache gain의 21.6%를 단 4KB hardware로 달성
4. **에너지 효율**: 복잡한 prediction, history tracking, prefetcher coordination 없이 starvation signal만으로 2.12% energy savings

### Broader Significance
- Instruction working set이 커지고 있는 datacenter workload에서 기존 RRIP 계열(SRRIP/BRRIP/DRRIP)이 FDIP 위에서 모두 역효과를 보이는 현실에서 유일하게 consistent gain 제공
- Starvation signal은 이미 모든 현대 프로세서에 존재 → **추가 cost 없는 drop-in enhancement**
- Bimodal selection과 treatment의 분리된 설계 공간은 향후 다른 cost signal(예: branch misprediction penalty, LLC miss latency)을 통합하는 데 확장 가능
- Unified L2 cache에서 data line과의 균형을 자동으로 조절하는 self-regulating property

## 주요 결과

- **Simulator**: gem5 FS mode, QEMU + FS_Lapidary tool로 checkpoint 생성 (Apple M1 + KVM 가속)
- **TPLRU**: Way-1 bits per tree, low/high priority용 dual tree
- **Priority bit**: 1 bit per line, L1I miss 시 starvation 관찰로 설정
- **Total hardware**: ~4KB (L1I: 1024 bits, L2: 32,768 bits)
- **Binary optimization**: BOLT (Facebook) 적용 (verilator)

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]


## 전체 요약

[[../paper-summaries/2023ISCA-summarize/emissary-enhanced-miss-awareness-replacement-policy-for-l2-instruction-caching.md|전체 요약 보기]]
