---
tags: [paper, 2024, 2024MICRO, topic/cache, topic/virtual-memory]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024MICRO-summarize/mosaic-harnessing-the-micro-architectural-resources-of-servers-in-serverless-environments.md"
---

# Mosaic: Harnessing the Micro-architectural Resources of Servers in Serverless Environments

**Venue:** 
**저자:** Jovan Stojkovic, Esha Choukse†, Enrique Saurez†, Íñigo Goiri†, Josep Torrellas (University of Illinois at Urbana-Champaign, †Microsoft Azure Research - Systems)

## 개요

### 1.1 Serverless의 Micro-architectural Inefficiency

Serverless 컴퓨팅은 lightweight function을 실행 단위로 사용하지만, 현대 서버급 프로세서에서 비효율적으로 동작함:

- **Frequent context switch:** Oversubscribed 환경에서 함수 간 빈번한 context switch 발생 → cache, TLB, branch predictor 등의 stateful 구조에서 state가 evict됨 (Figure 1).
- **State loss impact:** 완전한 state loss (ClearAll) 시 함수 실행 시간 **2.9× 증가**. Microsoft Azure production trace 분석 결과, 한 코어에서 8개/16개 이상의 함수가 interleave될 확률이 각각 21%/9%.

### 1.2 Oversized Hardware Structures

Serverless 함수는 monolithic application과 fundamentally 다른 특성을 보임:

| 특성 | Serverless 함수 (평균) | Monolithic |
|------|----------------------|------------|
| **LLC occupancy** | 2.9 MB | 15 MB (full) |
| **Data working set** | 2 MB | 8 GB |
| **Instruction working set** | 12 MB | 700 MB |
| **Branch working set** | 1.5 MB | 300 MB |

- LLC way를 15→2로 줄여도 함수 실행 시간은 **2.8%만 증가** vs. monolithic은 50% 증가 (Figure 4).
- L2 cache + LLC 동시 축소에도 함수는 거의 영향 없음 (Figure 2). Branch predictor도 32× 축소 시 hit rate 0.9%만 감소 (Figure 5).
- 그러나 일부 함수(MLSrv, ImgProc 등)는 큰 코어에서만 acceptable → **heterogeneity 존재** (Table I).

### 1.3 Processor Generality의 필요성

Specialized core만으로 serverless 전용 서버를 만들 수 없는 이유:
1. 함수별 이질성 (RnnSrv는 8-way L2 필요, WordCnt는 2-way로 충분 — Figure 6)
2. Serverless는 클라우드 workload의 일부일 뿐이며, separate cluster는 TCO 증가 (fragmentation, Figure 22)
3. End-to-end 앱은 serverless + monolithic service 조합으로 구성

---

## 방법론

### 3.1 Methodology

| 항목 | 내용 |
|------|------|
| **Simulation** | QEMU + modified SST + DRAM-Sim2, Ubuntu 20.04 full-system |
| **Base architecture** | 16-core, 6-issue OoO, Golden Cove micro-arch (Intel Sapphire Rapids 기반), 3.6GHz |
| **Core params** | L1 I/D 32/48KB 8-way, L2 2MB 16-way, LLC slice 1.8MB 15-way, TAGE-SC-L predictor 32KB, BTB 12K-entry (Table II) |
| **Memory** | 128GB DDR |
| **Baselines** | (1) Baseline, (2) Baseline+Affinity, (3) Baseline+MosaicScheduler (SW-only, Intel CAT partitioning), (4) Mosaic, (5) Jukebox, (6) Manycore (128× ARM A15, iso-area) |
| **Workloads** | 8 functions: ImgProc, MLSrv, EvStr, RiskQ, WordCnt, HotelB, SocNet, WebSrv. 71,434 invocations from MS Azure traces |
| **Hardware overhead** | 43.5KB storage/core = 1.06% core storage, 0.42% core area. Total area overhead: **0.05%** |

### 3.2 Latency

**P99 Tail Latency (Figure 14a):**
- Baseline+Affinity: -15.5%
- Baseline+MosaicScheduler (SW-only): 추가 -12.8%
- **Mosaic: -74.6%** (range: 64.8%~79.9%)
- Short-duration 함수(EvStr), frequent context switch 함수(HotelB)에서 특히 효과적.

**Average Latency (Figure 14b):**
- Baseline+MosaicScheduler: -28.7%
- **Mosaic: -59.6%** (over Baseline)

**구조별 기여도:** L2 cache state 미저장 시 +46% tail latency 증가, BTB 미저장 시 +34%.

### 3.3 Throughput (Figure 15)

**Mosaic: +225% throughput** (Baseline 대비, SLO = 5× unloaded execution time).

vs. Manycore: Manycore는 serverless 함수에서 +271% throughput이나, monolithic application에서 **-68% throughput**.

### 3.4 Power (Figure 20)

**Mosaic: -22% 평균 전력 소비** (Baseline 대비). Energy-delay product **-80%**.

### 3.5 Comparison Studies

| 비교 대상 | Mosaic 우위 |
|-----------|------------|
| **Jukebox** (instruction prefetching만) | Tail latency 71.1% 감소, on-chip area 더 작음 (Figure 16) |
| **Manycore** (128× A15) | Monolithic app throughput Baseline 유지 (Manycore는 -68%) (Figure 17) |
| **SMT** (2/4/8-way) | 모든 SMT 구성에서 latency 우위. 8-SMT는 contention으로 오히려 악화 (Figure 18) |
| **MXFaaS** (SW serverless platform) | Orthogonal: MXFaaS -53.1%, MXFaaS+Mosaic -79.3% (Figure 19) |

### 3.6 Sensitivity Studies

- **Load sensitivity:** Low/Medium/High load에서 tail latency 각각 -59.8%, -72.7%, -80.9%. Load↑ → benefit↑ (Figure 23).
- **Core count:** Mosaic 4-core = Baseline 16-core 수준 latency. **4× cost reduction** (Figure 24).
- **Oversubscription:** 20 functions/core에서도 Mosaic per-function throughput 68% 우위 (Figure 25).
- **64 functions 실험:** 8 functions 결과와 거의 동일 (tail -76.5%, avg -62.1%).

### 3.7 Co-location & Cost at Scale

- **Serverless + Monolithic co-location:** avg latency -49.8%, tail -67.8% (Figure 21).
- **Data center scale (1000+ servers):** Mosaic → Baseline+Manycore 대비 **10~24% 적은 서버** 필요. Serverless CPU-hour 비율이 0~100%인 모든 구간에서 least servers (Figure 22).

---

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

- MosaicScheduler: Intel Sapphire Rapids에서 프로토타입. Tail latency -28.3% (SW-only).
- Full-system simulation (QEMU+SST+DRAM-Sim2)으로 MosaicCPU 검증.
- 모델링된 overhead: chunk eviction 시 tag walk + writeback + invalidate (평균 500-600ns), voltage rail 전환 (5 cycles).

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2024MICRO-summarize/mosaic-harnessing-the-micro-architectural-resources-of-servers-in-serverless-environments.md|전체 요약 보기]]
