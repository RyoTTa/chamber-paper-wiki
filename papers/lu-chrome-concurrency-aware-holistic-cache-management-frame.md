---
tags: [paper, 2024, 2024HPCA, topic/cache]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024HPCA-summarize/chrome-concurrency-aware-holistic-cache-management-framework-with-online-reinforcement-learning.md"
---

# CHROME: Concurrency-Aware Holistic Cache Management Framework with Online Reinforcement Learning

**Venue:** 
**저자:** Xiaoyang Lu, Hamed Najafi, Jason Liu, Xian-He Sun (Illinois Institute of Technology / Florida International University)

## 개요

### 1.1 캐시 관리 기법의 단편화

최신 프로세서의 LLC(Last-Level Cache) 관리는 크게 세 가지 기법으로 구성됨:
- **Cache Replacement** (Hawkeye, Glider, CARE 등): 재사용 거리가 긴 블록을 우선 eviction
- **Cache Bypassing** (Mockingjay 등): 한 번만 접근되는 블록을 캐시에 삽입하지 않음
- **Hardware Prefetching** (next-line, stride, streamer, IPCP): 미래 접근을 예측하여 선제적 fetch

기존 SOTA 기법들은 이 세 가지를 **개별적으로 최적화**하여 상호 보완 효과를 놓침. 구체적 데이터:

- **Figure 2(a):** 4-core 시스템(12MB shared LLC)에서 Glider 사용 시, eviction되는 LLC 블록의 **83.7%가 재사용되지 않음**. 이 중 28.0%는 나중에 다시 요청되지만 eviction 전에 재사용되지 않은 것이고, 55.7%는 영원히 재사용되지 않는 dead block.
- **Figure 2(b):** 재사용 없이 eviction된 블록의 **70.0%가 prefetch로 유입**된 블록. 즉, prefetcher가 가져온 불필요한 데이터가 캐시를 오염시키고 유용한 블록을 밀어냄.

### 1.2 정적 정책의 비적응성

Mockingjay는 replacement + bypassing + prefetching을 통합했지만 **정적 정책**에 의존. Figure 3은 prefetch 구성 변경 시 성능이 불안정해지는 현상을 보여줌:

- **Figure 3(a):** L1=next-line, L2=stride prefetcher 구성에서 Mockingjay는 일부 워크로드(soplex, wrf, cc-urand)에서 Glider보다 열등.
- **Figure 3(b):** L1=stride, L2=streamer로 prefetcher 구성만 변경했을 때 Mockingjay가 **모든 워크로드에서 Glider보다 성능 저하**.

→ 정적/직관 기반 정책은 다양한 워크로드와 시스템 구성 변화에 대응할 수 없음. **온라인 적응형 학습이 필요.**

---

## 방법론

### 3.1 Methodology

| 항목 | 내용 |
|------|------|
| **Simulator** | ChampSim (IPC-1 release), cycle-accurate |
| **Processor model** | Intel Alder Lake-like, 4/8/16 cores, 4GHz, 6-wide, 512-entry ROB, Perceptron branch predictor |
| **L1 Cache** | Private, 48KB D-cache, 64B line, 12-way, 5-cycle |
| **L2 Cache** | Private, 1.25MB, 64B line, 20-way, 10-cycle |
| **LLC** | Shared, 3MB/core, 64B line, 12-way, 40-cycle |
| **DRAM** | 8GB, 2ch, DDR4-3200MT/s |
| **Default Prefetcher** | L1: next-line, L2: stride |
| **Workloads** | SPEC CPU2006 (14 apps × 20 traces), SPEC CPU2017 (13 apps × 22 traces), GAP (5 algorithms × 3 datasets = 15 traces) |
| **Workload 구성** | Homogeneous (n copies), Heterogeneous (150 mixes for 4-core, 25 for 8/16-core) |
| **Warmup/Sim** | 50M / 200M instructions per core |
| **Baselines** | LRU, Hawkeye, Glider, Mockingjay, CARE |
| **Metric** | Normalized weighted speedup over LRU |

### 3.2 4-Core 결과 (Figure 6-10, SPEC)

**Overall speedup (homogeneous, with prefetching):**

| Scheme | Avg Speedup | LLC Demand Miss Ratio | EPHR |
|--------|------------|----------------------|------|
| LRU | 1.000 (baseline) | — | — |
| Hawkeye | +5.7% | 75.9% | 27.9% |
| Glider | +5.6% | 75.7% | 23.0% |
| Mockingjay | +7.6% | 73.6% | 33.2% |
| CARE | +7.6% | 72.4% | 22.9% |
| **CHROME** | **+9.2%** | **71.1%** | **41.4%** |

**Bypass 성능 (vs Mockingjay, Figure 9):**
- CHROME bypass coverage: **41.5%** (incoming block 중 bypass 비율)
- CHROME bypass efficiency: **70.8%** (bypass된 block 중 이후 demand 요청 없는 비율)
- Mockingjay보다 coverage와 efficiency 모두 우수

**Heterogeneous 150 mixes (Figure 10):**
- CHROME geo-mean speedup: **+9.6%** (Hawkeye +6.7%, Glider +7.4%, Mockingjay +8.6%)
- 150개 mix 중 **119개에서 CHROME이 1위**, 137개에서 Mockingjay보다 우수

### 3.3 Scalability (Figure 11)

| Cores | CHROME (homo) | CARE (homo) | CHROME (hetero) | CARE (hetero) |
|-------|-------------|------------|----------------|--------------|
| 4 | +9.2% | +7.6% | +9.6% | — |
| 8 | +10.6% | +8.6% | +12.9% | +11.3% |
| 16 | +12.9% | +10.2% | +14.4% | +10.8% |

**핵심:** core 수 증가에 따라 CHROME의 상대적 우위 확대. 16-core homo에서 CARE 대비 **+2.5%p**, hetero에서 **+3.2%p** 우위.

### 3.4 Unseen Workloads: GAP (Figure 13)

Hyper-parameter tuning에 사용되지 않은 GAP 워크로드에서의 일반화 성능:

| Cores | CHROME | CARE | Mockingjay |
|-------|--------|------|------------|
| 4 | +9.5% | +6.5% | +5.5% |
| 8 | +12.1% | +8.3% | +6.8% |
| 16 | +16.0% | +12.5% | +10.1% |

→ 미학습 워크로드에서도 우수한 일반화 성능 입증.

### 3.5 Ablation Studies

#### Concurrency-awareness 효과 (N-CHROME vs CHROME, Figure 12)

C-AMAT 기반 system feedback 제거 시 (N-CHROME):

| Cores | CHROME | N-CHROME | Δ |
|-------|--------|----------|---|
| 4 | +9.2% | +8.3% | +0.9%p |
| 8 | +10.6% | +9.1% | +1.5%p |
| 16 | +12.9% | +10.0% | +2.9%p |

→ concurrency-awareness 이득이 core 수에 비례하여 증가.

#### Prefetch 구성 변경 (Figure 14)

| Prefetch 구성 | CHROME | Mockingjay |
|--------------|--------|------------|
| L1=stride, L2=streamer | +5.9% | +5.2% |
| IPCP (DPC-3 winner) | +7.2% | +5.7% |

→ CHROME은 prefetch 구성 변경에도 일관된 우위 유지.

#### Feature 중요도 (Figure 15)

| State features | Speedup |
|---------------|---------|
| PC only | +7.2% |
| PN only | +3.6% |
| **PC + PN** | **+9.2%** |

→ control-flow + data-access feature의 상호 보완 효과 입증.

#### EQ FIFO size (Table VII)

| FIFO Size | Speedup | UPKSA | Overhead |
|-----------|---------|-------|----------|
| 20 | +7.8% | 857.0 | 9.1KB |
| 24 | +8.2% | 830.6 | 10.9KB |
| **28** | **+9.2%** | **805.2** | **12.7KB** |
| 32 | +8.0% | 781.4 | 14.5KB |
| 36 | +7.5% | 759.1 | 16.3KB |

→ 28 entries가 observation window와 update frequency 간 최적 균형.

#### Hyper-parameter sensitivity (Figure 16)

- **α:** 1e⁻³에서 최적 (1e⁻⁹~1e⁰ 범위 탐색). 너무 크면 불안정, 너무 작으면 학습 느림.
- **γ:** 1e⁻¹에서 최적. 너무 낮으면 근시안적(immediate reward만), 너무 높으면 과도하게 far-sighted.
- **ε:** 0.001에서 최적. 0.01 이상에서는 exploration이 과도하여 학습된 policy 활용 저하.

---

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

- **시뮬레이터:** ChampSim (C++), IPC-1 버전 기반
- **추정 도구:** CACTI 7.0 (면적/전력/지연)
- **하드웨어 추가 요소:**
  - Q-Table: 32KB SRAM (2 features × 4 sub-tables × 2048 entries × 16 bits)
  - EQ: 12.7KB (64 FIFOs × 28 entries × 58 bits)
  - EPV: cache block당 2-bit → 12MB LLC 기준 48KB
- **면적/전력:** 1.55 mm², 76.05 mW (EQ: 0.30 mm², 7.27 mW)
- **Latency:** Q-Table lookup ≈ 2 cycles (off critical path)
- **Hyper-parameter tuning:** 1회성 off-line grid search. 20개 SPEC trace, 1000개 combination 평가.

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]


## 전체 요약

[[../paper-summaries/2024HPCA-summarize/chrome-concurrency-aware-holistic-cache-management-framework-with-online-reinforcement-learning.md|전체 요약 보기]]
