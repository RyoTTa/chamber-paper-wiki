---
tags: [paper, 2025, 2025OSDI, topic/cache, topic/disaggregation, topic/dram, topic/memory-tiering]
venue: ""
year: 2025
summary_path: "../paper-summaries/2025OSDI-summarize/osdi25-liu.md"
---

# Tiered Memory Management Beyond Hotness

**Venue:** 
**저자:** Jinshu Liu, Hamid Hadian, Hanchen Xu, Huaicheng Li (Virginia Tech)

## 개요

Tiered memory system은 fast tier (DRAM)와 slow tier (CXL memory)로 구성되며, tier 간 2-3×의 성능 격차가 존재함. 기존 tiering 설계는 **"자주 접근되는(hot) 데이터일수록 성능에 더 critical하다"** 는 가정에 기반하여 hotness tracking, memory allocation, page migration policy를 설계해 왔음 (TPP, Nomad, NBT, Colloid 등).

**핵심 문제: Hotness ≠ Performance.** 본 논문은 이 가정이 틀렸음을 정량적으로 입증:

- **Microbenchmark (Figure 1):** Sequential access (high MLP=7, "hot") thread와 pointer-chasing (low MLP=1, "cold") thread를 동시 실행. Sequential이 13.6× 더 hot함에도:
  - Hot-on-DRAM 배치: All-on-DRAM 대비 52.4% 성능 (48% 저하)
  - Cold-on-DRAM 배치: All-on-DRAM 대비 34% 더 나은 성능 (hotness-based의 "역배치"가 더 좋음)
  - TPP, Nomad, Colloid 모두 Cold-on-DRAM보다 성능이 나쁘고, 심지어 **NoTier(first-touch only)보다도 12-14% 낮은 성능**

- **56개 SPEC CPU 2017 + GAPBS workload 분석:** Memory access의 실제 성능 영향이 workload별로 **최대 4× 차이** (Figure 2c). LLC-Stalls per LLC-miss가 60~240 cycles 범위.

**원인:** Modern out-of-order CPU는 Memory-Level Parallelism(MLP)을 통해 latency를 masking. High-MLP access pattern (array traversal 등)은 slow-tier latency가 stall로 직결되지 않음. Low-MLP pattern (pointer chasing 등)은 latency에 민감. Hotness-based policy는 이 차이를 무시.

**기존 tiering의 추가 문제점:**
- **과도한 migration overhead:** Page migration 한 번에 평균 12µs 소요, 이 동안 해당 page 접근 thread stall. Hot하지만 non-performance-critical한 page를 불필요하게 promote. CXL 환경에서 DRAM 대역폭/지연 격차가 좁아지면서 overhead가 더 두드러짐.
- **Missed opportunities:** Performance-critical cold page가 hotness heuristic에 무시됨.

## 핵심 아이디어: AOL (Amortized Offcore Latency)

AOL은 memory access latency와 MLP를 통합하여 **각 memory access의 실제 성능 영향을 정량화**하는 metric:

$$\text{AOL} = \frac{\text{Latency}}{\text{MLP}}$$

- **Latency:** Average offcore request service time
- **MLP:** Average number of concurrent outstanding memory requests

이 metric을 기반으로 두 가지 tiering mechanism 설계:
- **Soar:** AOL 기반 object profiling → static allocation (near-optimal initial placement)
- **Alto:** AOL 기반 dynamic page migration regulation (unnecessary migration 제거)

---

## 방법론

### Part 1: AOL-Based Performance Prediction Model

#### 1.1 Base Predictor: LLC-Stalls (P)

**핵심 관찰:** Slow-tier에서의 성능 저하는 주로 LLC miss로 인한 CPU stall 증가 때문. Slowdown S는 다음과 같이 근사:

$$S = \frac{\Delta s_{\text{LLC}}}{c}$$

- $s_{\text{LLC}}$: LLC miss로 인한 CPU stall cycles
- $c$: Total CPU cycles on fast-tier
- $\Delta s_{\text{LLC}}$: Slow-tier에서의 stall 증가량

56개 workload에서 $\frac{\Delta s_{\text{LLC}}}{c}$의 예측 오차 <4% (Figure 2a).

**Online prediction을 위한 간소화:** $\Delta s_{\text{LLC}} \approx k \times s_{\text{LLC}}$ (workload 간 상관관계 기반) → Base predictor $P = \frac{s_{\text{LLC}}}{c}$.

$P$는 85% workload에서 slowdown과 강한 상관관계 (Pearson 0.869). 그러나 high-MLP workload (MLP>4) 에서는 **과대 추정** 경향 — 모든 LLC miss가 동등하게 stall에 기여한다고 가정하기 때문.

#### 1.2 AOL-Based Correction Factor K

**문제:** High-MLP workload에서 $P$가 slowdown을 과대 추정. MLP가 latency를 masking하는 효과를 반영해야 함.

$K = \frac{S}{P}$로 정의. $K$-vs.-AOL 관계는 **hyperbolic curve** (Figure 2d):

$$K = f(\text{AOL}) = \frac{1}{a + \frac{b}{\text{AOL}}}$$

- $a$, $b$: **Hardware-dependent, workload-independent** constants. Offline calibration으로 microbenchmark (sequential + pointer-chasing) 사용해 결정 가능. 사용자마다 반복 벤치마킹 불필요.
- Low AOL (high MLP): $K \rightarrow$ 0에 가까움 → $P$를 크게 scale down
- High AOL (low MLP, serialized): $K \rightarrow$ 1 → $P$ 거의 그대로

**Final Predictor:**

$$S = P \times K = \frac{s_{\text{LLC}}}{c} \times \frac{1}{a + \frac{b}{\text{AOL}}}$$

Pearson correlation 0.951로 base predictor 대비 크게 개선 (Figure 2e). Time-series prediction도 지원 (Figure 2f).

#### 1.3 Lightweight Measurement (4 PMU Counters)

AOL과 predictor에 필요한 모든 값은 단 4개의 Intel PMU counter로 측정 가능 (Table 1):

| Counter | Symbol | 의미 |
|---------|--------|------|
| CPU_CLK_UNHALTED.THREAD | $c$ | Total cycles |
| CYCLE_ACTIVITY.STALLS_L3_MISS | $s_{\text{LLC}}$ | LLC stall cycles |
| OFFCORE_REQUESTS_OUTSTANDING.CYCLES_WITH_DEMAND_DATA_RD | $A_1$ | Cycles with ≥1 pending request |
| OFFCORE_REQUESTS.DEMAND_DATA_RD | $A_3$ | Total demand requests to uncore |

계산:
- $\text{Latency} = \frac{A_1}{A_3}$
- $\text{MLP} = \frac{A_2}{A_1}$ (where $A_2$ = ORO.DEMAND_DATA_RD, accumulative inflight requests)
- $\text{AOL} = \frac{\text{Latency}}{\text{MLP}} = \frac{A_1}{A_3}$

### Part 2: Soar — Rank-Based Static Object Allocation

#### 2.1 Profiling Workflow (Figure 3)

Soar는 workload를 fast-tier에서 **한 번만 실행**하여 profiling. 세 가지 data flow 수집:

| Flow | 수집 방법 | 내용 |
|------|---------|------|
| **Object Flow** ($F_O$) | LD_PRELOAD로 malloc/free, mmap/munmap intercept, backtrace()로 call chain grouping | {T_alloc, T_free, vaddr, size, type} |
| **Memory Access Flow** ($F_M$) | Intel PEBS로 LLC-miss sampling (rate=3000, negligible overhead) | {T, vaddr} |
| **Performance Flow** ($F_P$) | 1s 주기 PMU counter 수집 → AOL-based predictor | {T, slowdown, AOL} |

#### 2.2 Object Scoring (Algorithm 1)

**통합:** $F_O$와 $F_M$을 병합하여 각 object의 memory access time-series ($T_M$) 생성. $T_M$과 $F_P$를 병합하여 per-object profile.

**Key insight:** Modern hardware는 per-object 성능 기여도를 직접 측정할 수 없음. Soar는 access frequency와 MLP 기반 heuristic 사용:

- **MLP=1 (no overlap):** Predicted slowdown $p$를 access ratio $R$에 비례 배분 → $s = R \times p$
- **High MLP (significant overlap):**
  - High-frequency objects (likely high MLP): score를 **amortize** (scale down) → $s = R \times p / \text{factor}$
  - Low-frequency objects (likely low MLP): score를 **amplify** (scale up) → $s = R \times p \times \text{factor}$
- Factor 값: AOL에 따라 stepwise 결정. 예: AOL low → factor=8 (sequential MLP=7 대응), pointer-chasing object는 2-8× amplify

**Unit Score:** Object 크기를 고려하여 $s' = \frac{s}{\text{sizeof}(O)}$. 대형 object일수록 동일 score 대비 fast-tier 배치 가치가 낮음.

#### 2.3 Allocation Policy

Object를 unit score 기준 정렬 → top-N object를 fast-tier에 bind (numa_alloc() 사용):

- Fast-tier 수용 가능한 최대 개수의 top object 배치
- Short-lived object의 경우 interleaving allocation 고려하여 max size 사용
- 공간 부족 시 lower-ranked object를 slow-tier로 demote (rarely 발생)
- Call chain 기반으로 allocation site 식별 → application code 변경 불필요, multi-language (C/C++, Python) 지원

#### 2.4 Use Cases & Limitations

- Graph processing, ML/AI, HPC 등 pre-allocation object가 많은 workload에 적합
- Offline profiling 필요 (datacenter에서 profile-guided optimization은 이미 보편적)
- Object 내 heterogeneous access pattern은 미고려 (future work)

### Part 3: Alto — AOL-Based Adaptive Page Migration Regulation

#### 3.1 Core Idea

Alto는 AOL을 사용하여 page migration이 **실제 성능 이득을 주지 못하는 구간**을 식별 → migration intensity를 동적으로 조절.

**Two AOL Thresholds (Algorithm 2):**

| AOL 범위 | 동작 | Scale |
|----------|------|-------|
| AOL ≤ AOL_low (=40) | High MLP, latency masking dominant → page promotion 중단 | 0 |
| AOL ≥ AOL_high (=100) | Serialized, latency-sensitive → full-speed promotion | 1 |
| AOL_low < AOL < AOL_high | Transitional → stepwise function $F(l)$로 부분 promotion | 0~1 |

Thresholds는 microbenchmark 기반 calibration (pointer-chasing: AOL=40/100, sequential: AOL=25/95 on two platforms).

#### 3.2 Integration with Existing Systems

Alto는 기존 tiering system 위에 최소한의 변경으로 통합 가능 (~30 LOC kernel side):

| 시스템 | 통합 방식 |
|--------|---------|
| **Alto+TPP** | TPP의 aggressive NUMA hinting fault 기반 promotion에서, 일정 비율의 candidate page만 실제 promote (예: 10개 중 2개) |
| **Alto+NBT** | VMA scanning 시 PAGE_NONE으로 설정할 page 수를 제한 → promotions регулирование |
| **Alto+Nomad** | NBT와 유사하게 scanning 제한 + Nomad의 non-exclusive migration에 적용 |
| **Alto+Colloid** | Colloid의 양방향 sampling 중 slow→fast promotion만 규제 |

---

## 핵심 기여

본 논문은 tiered memory management의 근본 가정인 **"hotness = performance criticality"를 정량적으로 반박**하고, MLP를 명시적으로 반영한 AOL metric을 제안.

**핵심 기여:**
1. **AOL metric + predictor:** 단 4개의 PMU counter로 workload 및 time-series 수준에서 slow-tier slowdown을 정확히 예측 (Pearson 0.951). Hardware-dependent but workload-independent → 다양한 플랫폼에 쉽게 배포 가능.
2. **Soar:** AOL 기반 object ranking으로 **static allocation만으로 near-optimal placement 달성**, runtime migration overhead 제거. 90% slow-tier ratio에서도 <20% slowdown.
3. **Alto:** 기존 tiering system에 **~30 LOC만으로 통합**하여 unnecessary page migration을 최대 127.4× 감소, 성능 최대 471% 개선. AOL thresholds에 robust.

**Broader significance:** CXL이 데이터센터의 주류 memory interconnect로 부상함에 따라, 성능 중심(performance-driven) tiering으로의 패러다임 전환이 필요함을 입증. AOL은 이러한 전환의 핵심 enabler로, 향후 memory management 전반에 걸쳐 활용 가능한 foundational metric.

## 주요 결과

### 방법론

| 항목 | SKX/NUMA | SPR/CXL |
|------|----------|---------|
| **CPU** | Dual-socket Intel Skylake, 2×10-core | Intel Sapphire Rapids, 32-core |
| **Fast-tier** | 90ns latency, 49 GB/s BW (NUMA emulation) | 114ns latency, 218 GB/s BW (DDR5) |
| **Slow-tier** | 190ns latency, 17 GB/s BW (uncore freq lowering) | 271ns latency, 26 GB/s BW (ASIC CXL expander) |
| **Latency ratio** | 2.1× | 2.4× |
| **Baselines** | NoTier, TPP, NBT, Nomad, Colloid | Same |
| **Workloads** | GAPBS (bc-kron, bc-twitter, bc-urand, sssp-kron, tc-twitter), SPEC 602.gcc, GPT-2, Redis | Same |
| **Slow-tier ratio** | 10–90% of RSS | 10–90% of RSS |
| **Threads** | 8 (default) | 8 (default) |

### Soar 결과

**bc-urand (Figures 4, 5, Tables 2-3):**

- Soar: **90% slow-tier ratio에서도 20% 미만 slowdown** 유지
- Nomad: 최대 217% slowdown → 심각한 불안정성
- NBT, Colloid: slow-tier ratio 증가에 따라 꾸준히 저하 (>60%)
- 80%+ slow-tier ratio에서 **모든 baseline이 NoTier보다 10-20% 낮은 성능** — migration overhead가 tiering 이점을 상쇄. Soar만 NoTier보다 일관되게 우수

**Object ranking 분석 (Table 2-3):**
- Soar는 $O_2$ (bitmap, high MLP → low hotness but high AOL contribution)를 2위로 평가
- First-touch나 Frequency-only는 $O_3$-$O_5$ (sequential access, high hotness but low AOL sensitivity)를 우선 → $O_2$를 slow-tier에 방치 → 성능 저하
- $O_8$ (graph data)에 대해 FT/Freq는 동시에 promote+demote 발생 → 불필요한 churn

**Soar on CXL (Figure 6):**
- Nomad: 최대 588% slowdown, Colloid: 최대 92%
- Soar: 최악 42% slowdown — NoTier보다 항상 우수

**Soar across all workloads (Table 4):**
- Soar: slowdown ≤18%, 모든 workload에서 최저
- Colloid, NBT, Nomad, TPP, NoTier: 최대 58%, 68%, 123%, 1246%, 67%
- Soar가 next-best 대비 4-42% 우수 (tc-twitter 제외, Colloid에 1% 열세)

### Alto 결과

**Alto vs. baselines (Figures 7, Table 5, Figure 8):**

| Integration | Improvement over baseline |
|-------------|--------------------------|
| **Alto+TPP** | 2–471% (SKX), 2–178% (CXL) |
| **Alto+NBT** | 1–23% |
| **Alto+Nomad** | -2–35% |
| **Alto+Colloid** | 0–18% |

- TPP의 extreme outlier (482% slowdown)이 Alto+TPP에서 제거
- Nomad는 non-exclusive migration으로 migration 감소 효과가 제한적 → Alto+Nomad가 일부 workload에서 2% 열세
- Page promotion 감소: TPP 대비 최대 **127.4×**, NBT 9.4×, Nomad 4.4×, Colloid 14.9×

**Alto mechanism 분석 (Figure 9, tc-twitter):**
- 처음 100s: AOL low (high MLP) → Alto가 TPP의 1.6M promotion을 190K로 **8.4× 감소**
- 이후 AOL 상승에 따라 promotion rate 점진적 증가
- 최종: TPP 대비 3.5× 적은 migration으로 더 나은 성능

### Sensitivity Analysis

**Soar (Section 6.8):**
- $L_0$ (AOL threshold) 70~100 범위: object ranking 변화 minimal (top object 동일, 성능 동일)
- $R_{\text{min}}$, $R_{\text{max}}$ (0.02~0.04, 0.6~0.8) 범위: 순위 약간 변동, 최종 placement 동일, 성능 영향 없음

**Alto (Figures 10-11):**
- AOL thresholds (0~140): 대부분의 조합에서 slowdown 16-22% → robust. 극단값 (0/∞)에서는 성능 저하
- Sampling interval: 100ms~1s — 성능에 minimal 영향
- Default thresholds (40/100 on SKX): near-optimal (16% vs 14% slowdown 최적치)
- Max performance variation across all thresholds: 14%

### Bandwidth Contention

**Soar (Figure 12):**
- Intel MLC threads로 fast-tier 대역폭 경합 생성 (0→9 threads, BW 0→48 GB/s = 98% utilization, latency 2× 증가)
- Soar: next-best 대비 4-41% 우수 유지 (contention 증가 시 gains 감소, 9 MLC threads에서 4%)
- 모든 state-of-the-art (Colloid, Nomad, NBT)는 contention 하에서 NoTier보다 저조 → migration overhead가 치명적
- Soar만 모든 contention level에서 baselines 능가

**Alto (Figures 12-13):**
- 5 MLC threads (81% BW utilization, latency 56% 증가): Alto+Colloid가 Colloid 대비 1-10% 개선, promotion 최대 51% 감소
- AOL range shift: 40-140 → 40-250 → runtime의 14.2%만 AOL>100 → Alto regulation 효과 유지
- 9 MLC threads (extreme): Alto+Colloid가 Colloid에 3% 열세 (단 1 case). AOL thresholds를 90/150으로 상향 시 slowdown 33%→23%로 개선, Colloid(30%) 능가 → contention-aware AOL tuning 필요 (future work)

---

## 구현

- **Soar:** User-level profiler + libnuma 기반 LD_PRELOAD allocator. PEBS sampling, PMU counter collection. Application code 변경 불필요.
- **Alto:** User-level AOL monitoring daemon + ~30 LOC 커널 수정 (Linux memory subsystem). Linux perf로 PMU counter 주기적 수집 (default 1s).
- **Open source:** https://github.com/MoatLab/SoarAlto

---

## 관련 연구

- **Heterogeneous memory management:** X-Mem (offline profiling, static access pattern classification), Thermostat, HeMem (PEBS-based page access sampling). Soar/Alto는 MLP-aware 성능 예측 측면에서 차별화.
- **Memory tiering systems:** TPP, NBT, Nomad, Colloid, Memtis, HeMem — 모두 hotness 기반. Soar/Alto는 hotness의 한계를 극복하는 orthogonal design.
- **Memory performance modeling:** CPU stall, LLC miss, ML 기반 predictor 등 존재하나, MLP로 인한 latency masking 효과를 명시적으로 모델링한 것은 AOL이 최초.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]


## 전체 요약

[[../paper-summaries/2025OSDI-summarize/osdi25-liu.md|전체 요약 보기]]
