---
tags: [paper, 2023, 2023MICRO, topic/cache, topic/disaggregation, topic/dram]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023MICRO-summarize/clip-load-criticality-based-data-prefetching-for-bandwidth-constrained-many-core-systems.md"
---

# CLIP: Load Criticality based Data Prefetching for Bandwidth-constrained Many-core Systems

**Venue:** 
**저자:** 

## 개요

Hardware data prefetcher는 off-chip DRAM access를 숨기는 latency-hiding 기법이지만, **constrained DRAM bandwidth를 가진 many-core 시스템에서는 state-of-the-art prefetcher조차 성능 저하를 유발**한다.

**Motivation data** (Figures 1–3, 64-core system, DDR4-3200):
- **Berti** (SOTA L1 prefetcher, average accuracy 82.9%): 4 DRAM channels → 24% slowdown, 8 channels → 16% slowdown. 64 channels에서는 35% improvement.
- 모든 SOTA prefetcher(Berti, IPCP, Bingo, SPP-PPF)가 낮은 DRAM bandwidth에서 공통적으로 성능 저하.
- 원인: prefetch accuracy는 높지만, 낮은 bandwidth로 인해 **prefetch lateness가 4ch→19%, 8ch→13%** 로 급증 (64ch에서는 1%). 이는 DRAM response latency 증가 → L3/L2/L1 MSHR, on-chip interconnect, 각종 queue에 cascading delay 유발로 이어짐.
- 평균 L2/L3 demand miss latency가 no-prefetching 대비 1.9× 이상 증가 (4, 8 channels).

**핵심 질문**: "constrained DRAM bandwidth many-core 시스템에서, 어떤 load address를 prefetch해야 prefetching으로 인한 추가 latency 문제를 완화할 수 있는가?"

**Ideal solution**: 100% accuracy + ROB head에서 retiring stall을 유발하는 critical load만 prefetch. 그러나 500+ entry ROB를 가진 aggressive OoO processor는 L3 miss latency의 상당 부분을 숨길 수 있어, 모든 L3 miss가 costly한 것은 아님.

## Why Existing Solutions Fail (Section 3)

### Load criticality predictors (Figure 4–5)

기존 predictor들은 IP 기반으로 critical load를 예측하나, average accuracy 41%에 불과. 원인:
- 동일 IP에서 생성된 load address라도 항상 critical하지 않음 (dynamic-critical vs static-critical)
- Branch history, conditional branch에 따라 criticality가 달라짐
- Predictor별 한계 (Table 1): CATCH (dependency graph기반, branch vicinity loads over-predict), FP (ROB stall count 기반, L3 miss 대부분을 critical로 tagging), FVP (data dependency chain root를 모두 tagging → over-prediction), ROBO/CBP (한 번 critical이면 계속 critical로 간주), CRISP (LLC miss + MLP만 고려, L1/L2 miss 무시)

### Prefetch throttlers (Figure 6)

FDP, HPAC, SPAC, NST 등: prefetch accuracy 기반 coarse-grained throttling. SOTA prefetcher는 이미 accuracy가 높아 marginal improvement. 특정 load만 선택적으로 prefetch해야 하는 fine-grained need를 충족하지 못함.

### Shared resource management

LLC replacement(Mockingjay) + prefetch-aware NOC/DRAM controller: Berti의 높은 accuracy 덕분에 LLC pollution은 minimal. Average improvement < 0.72%.

### Hermes, DSPatch

Hermes: off-chip load만 predict하나, constrained bandwidth 상황에서는 L2/LLC hit도 ROB stall의 60%를 차지 → insufficient.
DSPatch: per-controller bandwidth 기반 → myopic. Low bandwidth에선 prefetch coverage 모드로 전환 → accuracy 희생 → 문제 악화.

## 방법론

CLIP은 **two-stage critical + accurate load predictor**로, two 조건을 모두 만족하는 load만 prefetch:
1. ROB head를 stall시키는 **critical load**여야 함
2. Underlying prefetcher가 해당 trigger IP에 대해 **높은 accuracy**로 prefetch 가능해야 함

### Stage I: Critical Load Detection 및 Filtering

**Training phase**:
1. ROB stall flag: ROB가 retiring을 멈추면 set
2. Miss-level flag: load response가 L2/LLC/DRAM에서 오면 1 (L1 hit = 0)
3. ROB stall flag==1 AND miss-level flag==1 → 해당 IP를 criticality filter에 insert
4. Criticality filter: 128-entry (32-set 4-way), per-entry: 6-bit IP tag, 2-bit criticality count, 6-bit hit count, 6-bit issue count, is-critical-and-accurate bit
5. Criticality count가 threshold(4) 도달 시 underlying prefetcher trigger 시작 + per-IP prefetch accuracy monitoring

**Accuracy tracking**:
- Utility buffer: 64-entry circular CAM (prefetch address → trigger IP mapping)
- Demand request가 utility buffer에서 match → 해당 IP의 hit count increment
- Exploration window: L1D miss 1024회마다 evaluation. Per-IP hit rate ≥ 90% → is-critical-and-accurate bit set

### Stage II: Criticality Prediction

**Critical signature** (기존 IP-only signature의 한계 극복):
```
critical_sig = hash(IP ⊕ virtual_address ⊕ global_branch_history[31:0] ⊕ global_criticality_history[31:0])
```
- 32-bit branch history + 32-bit criticality history (last 32 branches/loads)
- 이 signature로 criticality predictor (512-entry, 128-set 4-way, 6-bit tag, 3-bit saturating counter) indexing
- Saturating counter: L1 miss + ROB stall → increment, L1 hit or miss without stall → decrement

**Prediction decision**:
```
if (saturating_counter.msb == 1 AND per_IP_accuracy_high):
    issue prefetch with criticality_flag = 1
else:
    drop prefetch request
```

### Phase Change Detection

APC (Accesses Per Cycle at L1D) 기반: last 16 windows 평균 APC 대비 현재 APC > 15% 차이 → phase change → 모든 table reset + prefetching 중단.

### L2 Prefetcher 적용

IP 정보가 없는 L2 prefetcher(SPP-PPF 등)의 경우: IP hit rate 대신 page hit rate 사용.

### Criticality-conscious NOC 및 DRAM

CLIP이 선택한 prefetch request에 criticality flag를 append → NOC router와 DRAM controller에서 demand load와 동일한 priority 부여.

### Storage Overhead

| Structure | Size |
|-----------|------|
| Criticality Filter (128 entries) | 336 B |
| Criticality Predictor (512 entries) | 640 B |
| Utility Buffer (64 entries) | 512 B |
| ROB extension (miss-level flag) | 64 B |
| Branch/Criticality history | 8 B |
| ROB stall flag | 1 bit |
| APC/exploration window registers | 32 bits |
| **Total per core** | **1.56 KB** |

기존 criticality predictor는 3–5 KB/core, throttler는 4–수십 KB/core 필요.

## 핵심 기여

**핵심 contribution**: Constrained DRAM bandwidth many-core 시스템에서 hardware prefetcher의 효과를 복원하는 fine-grained critical load predictor. 기존 coarse-grained 접근(IP-only criticality, prefetch accuracy throttling)의 근본적 한계를 극복.

**Key insights**:
1. **Not all L3 misses are critical**: 큰 ROB window는 상당한 latency를 숨기며, 오히려 L2/LLC hit이 ROB stall의 60%를 차지
2. **Dynamic-critical IPs**: 동일 IP라도 branch context에 따라 criticality가 달라짐. IP + branch history + criticality history 기반 signature로 dynamic behavior capture
3. **Accuracy without coverage sacrifice**: critical + accurate 조건을 모두 만족하는 load만 prefetch → prefetch traffic 50% 감소에도 불구하고 performance improvement

**Quantified impact**:
- Berti 성능 24% 향상 (homogeneous), 9% 향상 (heterogeneous) on 64-core 8ch
- Load criticality prediction accuracy: 93% (prior best: 41%)
- Storage overhead: 1.56 KB/core (prior 대비 1/2 ~ 1/10)
- Dynamic energy: 18.21% improvement

## 주요 결과

### 방법론

| 항목 | 내용 |
|------|------|
| Simulator | ChampSim (DPC-3) + detailed NOC (8×8 mesh) + DRAMSim |
| CPU | 64-core, 4GHz, 6-issue, 512-entry ROB, hashed perceptron branch predictor |
| L1I/L1D | 32KB 8-way / 48KB 12-way, Berti prefetcher |
| L2 | 512KB 8-way, SRRIP, non-inclusive |
| LLC | 2MB/core, 16-way, Mockingjay, non-inclusive |
| DRAM | DDR4-3200, 8 channels, PADC scheduler, 64-entry RQ/WQ |
| Workloads | 45 homogeneous + 200 heterogeneous 64-core mixes (SPEC CPU2017 + GAP), CloudSuite, CVP traces |
| Warmup | 100M instr/core, stats: 200M instr/core |
| Metrics | Weighted speedup (normalized to no prefetching) |
| Baselines | Berti, IPCP, Bingo, SPP-PPF, Hermes, DSPatch |

### 주요 결과

**CLIP + Berti** (Figures 9–16):
- 45 homogeneous mixes: **24% improvement** (Berti의 16% slowdown → 8% improvement)
- 200 heterogeneous mixes: **9% improvement**
- 77.5%의 성능 이득은 criticality filtering + prediction에서, 나머지는 accuracy filtering에서
- Criticality-conscious NOC/DRAM contribution: 2.8%

**Latency improvement** (Figure 11):
- Average L1 miss latency: 168 → 132 cycles (−36 cycles, −21.4%)
- 일부 mix(lbm dominant): 최대 900 cycles 이상 감소
- Prefetch lateness: 13% → 5.8%

**Prefetch traffic reduction** (Figure 16):
- Average 50% prefetch request 감소, 최대 90% (cactuBSSN)
- Berti average accuracy: 82.9% → 94.2%
- Notable: cactuBSSN_2421B: 12% → 89.65%, mcf_1536B: 51.1% → 93%

**Load criticality prediction** (Figures 13–14):
- Average accuracy: **93%** (best prior predictor: 41%)
- Average coverage: 76% of critical loads
- Average critical+accurate IPs per core: ~20 (out of hundreds of total IPs)
- 약 50%가 dynamic-critical IPs (static-critical predictor로는 포착 불가)

**Prefetch coverage trade-off** (Figure 12):
- L1 coverage: 7% 감소, L2: 2% 감소, LLC: 3% 감소
- Miss latency improvement가 coverage loss를 상쇄 → net performance gain

**Dynamic energy**: homogeneous mixes에서 Berti 대비 18.21% improvement (prefetch traffic 50% 감소 + runtime 단축 효과)

**CLIP across prefetchers** (Figure 9):
- Berti, IPCP, Bingo, SPP-PPF 모두에 동등하게 효과적

**CloudSuite / CVP workloads** (Figure 17):
- SPEC 대비 효과는 작음 (이 workload들은 기본적으로 prefetcher가 predict하기 어려움)

### Ablation / Sensitivity

- **Table size** (Figure 18): 0.25× → 7%+ performance drop. 2×/4× → marginal improvement (일부 3.23% 추가 gain)
- **DRAM channels** (Figures 19–20): 4ch, 8ch에서 highly effective. 16ch에서는 marginal (bandwidth 충분)
- **Core count**: 8–128 cores에서 consistent effectiveness (2–4 cores/channel 이하일 때만 효과 감소)
- **LLC size**: 512KB/core → most effective (Berti slowdown 29% → CLIP이 크게 개선). 4MB/core → Berti slowdown 9%로 완화, CLIP 효과도 감소하나 여전히 positive

### CLIP vs Hermes/DSPatch (Figure 21)

- Berti+Hermes: 4ch/8ch에서 Berti+CLIP보다 열등. DRAM-bound load만 target → L2/LLC hit stall 무시 + DRAM traffic reduction marginal (<1%)
- Berti+DSPatch: low bandwidth → prefetch coverage 모드 → accuracy 희생 → L1 miss latency 증가 → poor performance
- 16ch에서는 Hermes가 CLIP 능가 (Hermes의 original contribution과 일치)

## 구현

- **Hardware structures**: Per-core criticality filter(128-entry CAM-like), criticality predictor(512-entry, 3-port), utility buffer(64-entry CAM)
- **ROB modification**: miss-level flag 1-bit per entry (512 entries)
- **Replacement policies**: Criticality filter → LFU based on crit. count bits. Criticality predictor → NRU
- **Phase detection**: APC-based, threshold 15%

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2023MICRO-summarize/clip-load-criticality-based-data-prefetching-for-bandwidth-constrained-many-core-systems.md|전체 요약 보기]]
