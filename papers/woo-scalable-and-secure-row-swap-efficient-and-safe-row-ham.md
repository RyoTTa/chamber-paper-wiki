---
tags: [paper, 2023, 2023HPCA, topic/dram, topic/rowhammer]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023HPCA-summarize/scalable-and-secure-row-swap-efficient-and-safe-row-hammer-mitigation-in-memory-systems.md"
---

# Scalable and Secure Row-Swap: Efficient and Safe Row Hammer Mitigation in Memory Systems

**Venue:** 
**저자:** 

## 개요

Randomized Row-Swap (RRS) [ASPLOS 2022]는 aggressor-focused mitigation으로, TRH에 도달하기 전에 aggressor row를 random row와 swap하여 물리적 adjacency를 깨는 방식이다. 그러나 RRS에는 두 가지 근본적 문제가 있다.

**RRS 동작 recap:**
- Swap threshold TS (e.g., TRH=4800일 때 TS=800 → swap rate 6)
- Row가 TS activation마다 random row와 swap
- 동일 refresh window 내에서 재 swap 발생 시 먼저 unswap 후 swap (unswap-swap)
- RIT (Row Indirection Table): tuple 기반 row mapping tracking (CAT 구조)

### 1.1 RRS가 안전하지 않은 이유: Juggernaut Attack

Swap 동작 자체가 aggressor row의 원래 physical location에 **latent activation**을 유발한다 (Fig. 2):
- Swap 시 5단계 중 마지막 단계(Row_rand data를 Row_aggr 위치로 write)에서 1회의 latent activation 발생
- 이후 Unswap-swap 시 추가로 최대 2회의 latent activation 발생 (unswap 1회 + swap 1회) (Fig. 3)
- 최적화된 swap buffer 사용 시에도 평균 1.5회 latent activation/round

**Juggernaut 공격 = Latent activation + Random guess hybrid:**

1. **Bias phase:** 특정 aggressor row에 N회의 unswap-swap을 의도적으로 유발 → latent activation 누적
   - 예: N=800이면 2×800+1 = 1601회 latent activation + TS(800) direct activation = 2401회 누적 (TRH=4800 기준)
2. **Random guess phase:** Birthday paradox 기반 random guess로 남은 activation (TRH - 2401 = 2399)을 채움
   - 800 activation씩 3회만 성공하면 됨 (swap rate 6 대신 3)

**결과 (Fig. 6):** TRH=4800, TS=800, swap rate 6에서 **단 4시간 만에 RRS breakthrough** (원래 RRS가 주장한 >3년 대비). TRH=2400 이하에서는 단일 refresh interval(64ms) 내에도 break 가능.

### 1.3 RRS가 확장성 없는 이유

낮은 TRH에서 swap rate가 급증 → 성능/저장공간 overhead 폭발:
- TRH=4800에서 RRS slowdown 0.3% → TRH=1200에서 4%
- TRH=512에서는 RRS slowdown 14%
- RIT size도 TRH=1200에서 bank당 250KB로 급증 (Table IV)

**이 논문의 목표 3가지:**
1. RRS를 1일 이내에 break할 수 있는지 입증
2. Juggernaut 및 미래의 unknown attack에도 안전한 방어 설계
3. 낮은 TRH에서도 낮은 swap rate로 확장 가능한 솔루션

## 방법론

### 3.1 방법론

| 항목 | 구성 |
|------|------|
| Simulator | USIMM (DDR4 protocol, modified) |
| Processor | 8-core OoO, 3.2 GHz, ROB=192, fetch/retire width=4 |
| LLC | 8 MB shared, 16-way, 64 B lines |
| Memory | 32 GB DDR4, 1.6 GHz, 16 banks × 1 rank × 2 ch |
| RH Threshold | TRH = 1200 (primary), 512/2400/4800 (sensitivity) |
| Row tracker | Misra-Gries (default), Hydra (sensitivity) |
| Workloads | SPEC2006, SPEC2017, GAP, BIOBENCH, PARSEC, COMMERCIAL (78 total) |
| Baselines | Not-secure baseline, RRS |

### 3.2 Performance (Fig. 14)

TRH=1200 기준:
- **Scale-SRS:** 평균 slowdown **0.7%** (78 workload 평균)
- **RRS:** 평균 slowdown **4%**
- Worst-case: gcc에서 RRS 26.5% slowdown → Scale-SRS는 minimal
- hmmer, bzip2, zeusmp, astar, sphinx, xz_17 등에서 RRS >10% slowdown

### 3.3 TRH Sensitivity (Fig. 15)

| TRH | Scale-SRS slowdown | RRS slowdown |
|-----|-------------------|--------------|
| 4800 | <0.5% | <0.5% |
| 2400 | <1% | ~2% |
| 1200 | 0.7% | 4% |
| 512 | 4% | 14% |

Scale-SRS는 낮은 TRH에서도 graceful degradation.

### 3.4 Tracker Sensitivity (Fig. 16)

Hydra tracker 사용 시:
- TRH=512: Scale-SRS 5.9% slowdown vs. RRS 26.8% slowdown
- Hydra는 activation counter를 DRAM에 저장 → RRS의 잦은 swap이 과도한 memory access 유발

### 3.5 Storage Analysis (Table IV)

Bank당 SRAM overhead:

| 구조 | TRH=4800 | | TRH=2400 | | TRH=1200 | |
|------|----------|----------|----------|----------|----------|----------|
| | RRS | Scale-SRS | RRS | Scale-SRS | RRS | Scale-SRS |
| RIT | 35 KB | 9.4 KB | 130 KB | 35 KB | 250 KB | 67.5 KB |
| Swap-Buffer | 1 KB | 1 KB | 1 KB | 1 KB | 1 KB | 1 KB |
| Place-Back Buffer | - | 8 KB | - | 8 KB | - | 8 KB |
| Epoch Register | - | 19 bits | - | 19 bits | - | 19 bits |
| Pin Buffer | - | 289 B | - | 420 B | - | 420 B |
| **Total** | **36 KB** | **18.7 KB** | **131 KB** | **44.4 KB** | **251 KB** | **76.9 KB** |

Scale-SRS는 RRS 대비 **3.3×** 낮은 저장공간 overhead (TRH=1200 기준).

### 3.6 Power Analysis (Table V)

TRH=4800, channel당:
- RRS: DRAM power 0.5% 증가 + SRAM power 903 mW
- Scale-SRS: DRAM power 0.2% 증가 + SRAM power 703 mW (**23% lower**)

낮은 swap rate가 DRAM power 감소의 주 요인, 작은 SRAM 구조가 on-chip power 감소.

### 3.7 Analytical Model 검증 (Section III-B)

수식 기반 analytical model + 100,000-iteration Monte Carlo event-driven simulation으로 cross-validation (Fig. 6). 두 결과가 close match.

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

- **Simulator:** USIMM memory system simulator에 Scale-SRS, RRS module을 C로 구현
- **Artifact (DOI 10.5281/zenodo.7445036):**
  - Security analysis: C++ Monte Carlo event-driven simulator
  - Performance analysis: Scale-SRS/RRS structures + operations in C (USIMM memory controller module)
  - 실행 환경: Ubuntu 20.04/22.04, g++/gcc 9.4.0+
  - Security simulation: single-core, 3분 소요
  - Performance simulation: 78 benchmarks, 64+ cores / 128 GB+ 필요, ~15시간

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]


## 전체 요약

[[../paper-summaries/2023HPCA-summarize/scalable-and-secure-row-swap-efficient-and-safe-row-hammer-mitigation-in-memory-systems.md|전체 요약 보기]]
