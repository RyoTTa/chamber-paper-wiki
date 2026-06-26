---
tags: [paper, 2025, 2025ISCA, topic/cache, topic/disaggregation, topic/dram, topic/memory-tiering, topic/nvm, topic/virtual-memory]
venue: ""
year: 2025
summary_path: "../paper-summaries/2025ISCA-summarize/artmem-adaptive-migration-in-reinforcement-learning-enabled-tiered-memory.md"
---

# ArtMem: Adaptive Migration in Reinforcement Learning-Enabled Tiered Memory

**Venue:** 
**저자:** Xinyue Yi, Hongchao Du, Yu Wang, Jie Zhang, Qiao Li, Chun Jason Xue

## 개요

Memory가 서버 비용의 약 40%를 차지할 만큼 비중이 높아지고, DRAM density는 물리적 한계에 직면하면서, PM(Persistent Memory) 및 CXL 기반 tiered memory가 cost-efficient 대안으로 부상함. 그러나 capacity tier의 latency는 DRAM 대비 최대 2배 이상(실험에선 DRAM 92ns vs. PM 323ns)으로 높아, page placement가 system 성능의 결정적 요인이 됨.

기존 tiered memory system은 세 가지 공통 한계를 가짐 (synthetic access pattern S1~S4로 실증):

1. **Workload-dependent performance:** AutoNUMA, TPP, AutoTiering, Nimble, MEMTIS, Multi-clock, Tiering-0.8 7개 system을 S1~S4 패턴에 대해 평가한 결과, 모든 system이 일부 패턴에서 우수했지만 어떤 단일 system도 모든 패턴을 커버하지 못함. 예: Multi-clock은 S1(high spatial locality)에 매우 우수하나 S4(uniform access over 20GB, DRAM 16GB)에서는 82%의 page를 잘못 배치하여 성능 저하; MEMTIS는 S1에서 불필요 15GB migration, S2(recency-dominant)에서는 오히려 static baseline보다 성능 저하. **(Observation 1)**
2. **Static hotness threshold:** DRAM access ratio가 성능과 강한 상관관계를 보임(Pearson coefficient: MEMTIS 0.89, Nimble 0.81, AutoTiering 0.87). 기존 방식은 DRAM access ratio가 급락해도 heuristic-based static threshold로는 효과적 대응 불가. **(Observation 2)**
3. **Fixed migration scope:** MEMTIS의 hotness threshold를 workload별로 수동 조정했을 때 Liblinear 47%, XSBench 42% 성능 향상이 있었지만, 범용적인 자동 tuning mechanism은 없었음. **(Observation 3)**

---

## 방법론

ArtMem은 3계층 architecture (Figure 5): **Top:** RL framework, **Middle:** software functions (sampling, page sorting, threshold control), **Bottom:** hardware (PMU/PEBS, memory tiers).

### 1. Efficient RL Framework (§4.2)

System-wide level에서 Q-learning 기반 model-free RL 적용. Per-page RL은 수백만 page에 대해 impractical하므로 compact state/action space 설계.

**State (𝝉):**
- DRAM access ratio를 k+1=11개 discrete state로 변환. k=10.
- τ = ⌊(DRAM_access / (DRAM_access + PM_access)) × k⌋ (Equation 1)
- 별도 state k+1=11은 모든 event가 CPU cache hit인 경우(no sampling data) 대응.

**Action:**
- 2개의 독립 Q-table 운영: hotness threshold 조정용, migration volume 조정용.
- Threshold action: ±8, ±4, 0 (5개). 이전 threshold x에서 +4 적용 시 threshold = x+4.
- Migration volume action: 0MB(no migration), 16MB(8×2MB pages), 32MB, 64MB, 128MB, 256MB, 512MB, 1024MB, 2048MB (9개).

**Reward (Equation 2):**
```
r = τᵢ − β + λ(τᵢ − τᵢ₋₁)
```
- τᵢ: 현재 period의 DRAM access ratio state
- β: target DRAM access ratio (8~10 권장)
- λ: 이전 period migration 발생 여부에 따라 0 또는 1로 설정 (migration 없었으면 변동분 reward/penalty 없앰)

Reward 설계의 핵심: DRAM access ratio를 target 근처로 유지하면서, migration이 ratio를 개선하면 보상, 악화시키면 페널티. 이 구조는 **unnecessary migration을 억제하는 효과**가 있음.

### 2. Dynamic Adjustment of Migration Scope (§4.3)

**EMA-based access distribution capture (❶❷):**
- Per-page access count를 exponential bin(base 2)로 그룹화하여 access 분포를 압축 표현.
- 2 million sample마다 cooling operation: 모든 bin count와 per-page access record를 반으로 감소 → stale 정보 점진적 제거.
- Cooling 시 hotness threshold도 DRAM capacity 기준으로 reset, 이후 RL이 점진적 refinement.

**Page sorting via LRU lists (❸):**
- 각 memory tier가 active/inactive LRU list 유지.
- Promotion candidates: capacity tier의 **active list head**에서 선택.
- Demotion candidates: fast tier의 **inactive list tail**에서 선택.
- Aggressive insertion policy: migrated page는 fast tier의 **active list head**에 직접 삽입 → premature demotion 방지, 최근 접근 page가 즉시 priority 획득.

**Strawman 극복:**
- Static threshold + DRAM capacity → S1에서 15GB 불필요 migration, S4에서 47GB migration thrashing.
- RL이 실시간 feedback으로 적절한 migration number를 자동 학습.

### 3. Integration: RL in Tiered Memory (§4.4)

**Sampling threads (ksampled):**
- CPU core별 1개 할당. PEBS로 target PID의 memory load event address를 periodic sampling.
- Period: hardware event 200회당 1회 기록, 2ms마다 data 수집 및 counter update → sampling overhead 최대 3% CPU.
- Sampling data로 page sorting, EMA bin update, fast tier access ratio 계산.

**Migration thread (kmigrated):**
- RL이 action을 전달하면 우선 DRAM free space 확인.
- Free space < promotion volume → demotion 먼저 실행 (fast tier inactive list tail부터).
- Free space 확보 후 → capacity tier active list head에서 fast tier active list head로 promotion.

**Communication channels:**
- cgroup directory 아래 pseudo-filesystem mount point 2개: `memory.hit_ratio_show` (state read), `memory.action_show` / `memory.threshold_show` (action write).
- User-space에서 RL algorithm 구현 가능 → parameter 조정과 비교 실험 용이.

## 핵심 기여

1. **핵심 contribution:** Tiered memory에 **RL을 실용적으로 통합**한 최초의 kernel-level system. Compact state/action space 설계로 overhead를 최소화하면서도 다양한 access pattern에 적응.
2. **Broader significance:** DRAM access ratio 기반 reward 설계는 다른 system resource management (cache, SSD I/O, prefetching)에도 적용 가능. User-space RL agent + kernel back-end 분리 아키텍처는 다른 kernel subsystem에도 확장 용이.
3. **Open source:** 전체 구현이 GitHub에 공개되어 재현 및 확장 가능.

## 주요 결과

```
1: Q(k, 0) ← 1, 나머지 Q-table은 0으로 초기화
2: τᵢ₋₁ ← k (초기 state: 모든 access가 DRAM에서 발생)
3: while program not finished:
4:     ε-greedy로 τᵢ₋₁에 대한 action 선택 (ε=0.3)
5:     Migration thread가 updated parameter로 page migration 수행
6:     Sampling data에서 새로운 state τᵢ 관측
7:     r ← τᵢ − β + λ(τᵢ − τᵢ₋₁)
8:     Q(τᵢ₋₁, a) ← Q(τᵢ₋₁, a) + α[r + γ·maxₐ′Q(τᵢ, a′) − Q(τᵢ₋₁, a)]
9:     τᵢ₋₁ ← τᵢ
10: end
```

Hyperparameter: α=e⁻² (learning rate), γ=e⁻¹ (discount), ε=0.3 (exploration), β=8~10, migration interval=10s.

---

## 구현

- **Kernel:** Linux v5.15.19 기준, ~2,970 lines of kernel modification.
- **Page unit:** 2MB huge page (compound_page의 unused struct page를 활용해 추가 memory overhead 없이 access data 저장).
- **User-space RL agent:** pseudo-filesystem interface 통해 kernel과 통신.
- **Heuristic minimum threshold:** 16 accesses/page. RL이 exploration 단계에서 과도하게 낮은 threshold를 설정하는 것을 방지.
- **Memory overhead:** Q-table 2개 < 10KB.
- **Q-table computation overhead:** 최대 0.07% CPU.

---

## 평가

### 실험 환경 (Table 2)

| 항목 | 사양 |
|---|---|
| **CPU** | Intel Xeon Gold 6330, 28 cores/socket, 1 socket 사용 |
| **Fast tier** | 64GB DDR4 DRAM, latency 92ns, BW 81GB/s |
| **Slow tier** | 512GB Intel Optane PM, latency 323ns, BW 26GB/s |
| **PM 구성** | ndctl로 remote memory node로 설정 |
| **Memory ratio** | 2:1, 1:1, 1:2, 1:4, 1:8, 1:16 (cgroup으로 통제) |

### Workloads (Table 3)

| Workload | Footprint | Domain |
|---|---|---|
| YCSB (A,B,C,D,F) | 32GB | In-memory DB (Memcached) |
| CC (Connected Components) | 69GB | Graph analytics (GAP) |
| SSSP | 64GB | Graph analytics (GAP) |
| PR (PageRank) | 25GB | Graph analytics (GAP) |
| XSBench | 69GB | HPC |
| DLRM | 72GB | Deep Learning Recommendation |
| Btree | 24GB | In-Memory Index Lookup |
| Liblinear | 68GB | Machine Learning |

### Baselines (7)

AutoNUMA, Nimble, Multi-clock, TPP, Tiering-0.8, AutoTiering, MEMTIS

### 결과 요약

- **Overall:** 7 baseline 대비 평균 132%, 124%, 104%, 91%, 72%, 67% 성능 향상 (각 baseline별 aggregate). 전체 scenario 평균 114% improvement.
- **In-memory DB (YCSB):** Multi-clock과 유사한 selective promotion으로 65% 평균 향상.
- **Graph (CC, SSSP, PR):** 12%~509% improvement. Graph algorithm locality를 RL이 효과적으로 학습. Fast memory tier가 축소되어도 migration priority를 동적으로 조정하여 runtime 유지.
- **HPC (XSBench):** 16%~311% improvement. Recency + frequency 기반으로 hot region을 DRAM에 신속 배치.
- **DLRM:** 5%~110% improvement. Embedding table의 random access는 불리하지만, dense feature의 sequential access를 RL이 학습.
- **Btree:** Multi-clock과 7% 이내 근접, 타 baseline 대비 4%~36% 향상. Multi-clock이 Btree에 강하지만 XSBench 등 다른 workload에 취약한 반면, ArtMem은 모든 domain에서 consistent.
- **Liblinear:** MEMTIS 대비 9% 낮았으나 전체 평균 76% 향상. 초기 gradient descent phase에서 DRAM access ratio가 0%로 급락 후 70%까지 복구되는데, sampling frequency 증가(+5.91% overhead)로 17.11% 추가 성능 향상 가능.

### Ablation Study (§6.3.1)

- **RL component**가 가장 큰 기여 (특히 DRAM 비율이 낮을수록 영향 증가).
- **Page sorting** component는 전체 평균보다 PR, XSBench 등 특정 workload에서 10%+ 성능 gain.
- Heuristic-only는 DRAM이 충분할 때는 괜찮으나 DRAM 부족 시 한계.

### Ablation: Migration Volume (§6.3.3)

- CC workload에서 MEMTIS는 약 10× 더 많은 migration overhead를 발생.
- DLRM의 경우 ArtMem은 CC 대비 30,000회 적은 migration 수행 → skewed access만 learning으로 식별, 나머지는 unnecessary migration 방지.
- ArtMem과 AutoNUMA는 모든 scenario에서 낮은 migration volume 유지.

### DRAM Access Ratio Analysis (§6.3.2)

- SSSP: RL이 heuristic보다 모든 ratio에서 높은 DRAM access ratio 달성.
- CC: DRAM:PM = 1:4에서 두 방법 수렴 — Figure 10의 DAMON heatmap에서 CC는 hot/cold 구분이 명확하여 충분한 DRAM이 확보되면 migration이 straightforward.

### Mixed Workloads (§6.3.10)

- SSSP+XSBench, SSSP+Btree, Btree+XSBench 동시 실행: 평균 11% improvement over second-best.
- TPP는 초기 migration 후 DRAM access ratio가 양호하나, 이후 변동에 효과적 대응 실패 → migration volume 17.5배.
- ArtMem은 initial exploration 후 Q-table이 안정화되면 action=0을 높은 확률로 선택하여 불필요 migration 방지.

### Robustness (§6.3.6)

- 서로 다른 workload로 training한 Q-table을 cross-application에 재사용: 5×5 = 25 combination 중 7개만 10%+ 성능 저하.
- Suboptimal Q-table에서 시작 시 1~6 iterations (평균 3) 이내에 95%+ 성능 도달.

### Latency Sensitivity (§6.3.9)

- Slow tier latency 152ns(remote DRAM), 323ns(local PM), 407ns(remote PM)로 변화 시, latency gap 증가할수록 ArtMem의 advantage도 증가.

### Hyperparameter Sensitivity (§6.3.7)

모든 hyperparameter는 workload/ratio 조합에 robust: α=e⁻², γ=e⁻¹, ε=0.3, β=8~10, migration interval=5~15s 범위에서 안정적.

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2025ISCA-summarize/artmem-adaptive-migration-in-reinforcement-learning-enabled-tiered-memory.md|전체 요약 보기]]
