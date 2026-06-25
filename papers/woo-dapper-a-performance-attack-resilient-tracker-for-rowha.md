---
tags: [paper, 2025, 2025HPCA, topic/cache, topic/dram, topic/rowhammer, topic/security, topic/storage]
venue: "HPCA 2025"
year: 2025
summary_path: "../paper-summaries/2025HPCA-summarize/dapper-a-performance-attack-resilient-tracker-for-rowhammer-defense.md"
---

# DAPPER: A Performance-Attack-Resilient Tracker for RowHammer Defense

**Venue:** HPCA 2025
**저자:** Jeonghyun Woo, Prashant J. Nair (University of British Columbia)

## 개요

RowHammer 방어를 위한 host-side 저비용 tracker들(Hydra[ISCA'22], CoMeT[HPCA'24], START[HPCA'24], ABACUS[USENIX Security'24])은 shared counter, group counter, LLC, DRAM-resident counter cache를 사용해 storage cost를 줄임. 그러나 이러한 **공유 구조는 Performance Attack(Perf-Attack)에 취약**.

**Perf-Attack의 두 가지 유형:**
1. **Shared Counter Cache Miss 유도:** Hydra의 RCC(Row Counter Cache) set-conflict miss를 유발하여 추가 DRAM access(read-modify-write) 발생 → DRAM bandwidth 감소. 예: 32-way RCC에서 64-row targeting → 87% miss probability, 평균 61% 성능 저하(510.parest 최대 88%). START는 LLC reserved region overflow → 평균 65% 저하.
2. **Redundant Mitigative Refresh 유도:** CoMeT의 128-entry RAT(Recent Aggressor Table) overflow → 전체 row refresh(2.4ms blocking) 반복 → 평균 90% 성능 저하. ABACUS의 shared MG(Misra-Gries) tracker overflow → spillover counter 포화로 평균 72% 저하.

**Perf-Attack vs Cache Thrashing (NRH=500):** cache thrashing은 평균 40% 저하, Perf-Attack은 60~90% 저하 — 16~49% 더 심각.

## 방법론

### 3.1 Methodology

| Component | Configuration |
|-----------|--------------|
| Simulator | Ramulator (cycle-accurate) |
| CPU | 4-core OoO, 4GHz, 4-wide, 128-entry ROB |
| LLC | 8MB, 16-way, 64B lines |
| Memory | DDR5 6400MT/s, 2ch, 2 ranks, 8 bank groups × 4 banks, 64K rows/bank (8KB), 64GB |
| Timing | tRC=48ns, tRFC=295ns, tREFI=3.9µs |
| Benchmarks | SPEC2006, SPEC2017, TPC, Hadoop, MediaBench, YCSB → 57 apps, homogeneous 4-core |
| NRH sweep | 125, 250, 500, 1K, 2K, 4K (default 500) |
| Attack config | 4-core 중 1 core가 attacker, 3 core가 benign (3:1) |
| Baselines | Hydra, CoMeT, START, ABACUS, BlockHammer, PARA, PrIDE, PRAC/QPRAC |

### 3.2 Perf-Attack 하 성능 (NRH=500)

| Mechanism | Perf-Attack 평균 성능 저하 | 최대 저하 |
|-----------|--------------------------|----------|
| Hydra | 61% | 88% (510.parest) |
| START | 65% | 91.2% |
| CoMeT | 90% | — |
| ABACUS | 72% | 91% |
| **DAPPER-H** | **0.9%** | 4.7% (streaming), 2.3% (refresh) |

### 3.3 Benign 성능 (Perf-Attack 없음)

NRH=500: DAPPER-H 평균 0.1% 저하, 최대 4.4% (429.mcf).
NRH sensitivity: NRH ≥ 500 → <1% overhead. NRH=125: benign 4%, refresh attack 6%.

### 3.4 Sensitivity Studies

**Blast Radius (BR=2):** NRH=500, refresh attack → 1.8% (vs BR=1 0.9%). NRH=125 → 9.2%.

**DRFMsb vs VRR:** DRFMsb(Same-Bank DRFM)는 8 bank group × 1 bank씩 blocking → NRH=500에서 8% 저하 (VRR 0.9%). NRH=125에서 27.1% (VRR 6%). → per-bank granularity command의 필요성 시사.

**LLC Size/Channel 수 확장:** 5MB/core LLC, 8ch → cache thrashing 20%, Perf-Attack 30~79%. 단순 HW 확장으로 Perf-Attack 방어 불가.

### 3.5 Storage & Energy

- **Storage:** 2× RGC table (32KB SRAM) + per-bank bit-vector (32KB) = **96KB SRAM per 32GB DDR5**. Die area overhead: 0.038mm². 기존 tracker 대비: Hydra 56.5KB SRAM+23KB CAM, CoMeT 112KB, ABACUS 19.3KB CAM.
- **Energy (DRAMPower):** NRH=500 benign 0.1%, streaming 0.2%, refresh 1.1%. NRH=125: benign 4.5%, refresh 7.5%.

### 3.6 타 기법 비교

**BlockHammer[HPCA'21]:** NRH=125에서 66% 저하 (throttling indiscriminate). DAPPER-H: 4%.

**PARA[ISCA'14], PrIDE[ISCA'24] (probabilistic):** NRH=125에서 PARA 8.5%, PrIDE 16.7% (benign). Perf-Attack: PARA 14.6%, PrIDE 22.8%. DAPPER-H: 4% benign, 6% attack.

**PRAC/QPRAC[HPCA'25]:** NRH=4K benign에서 PRAC 7% (counter update overhead 고정). DAPPER-H: <0.3%. Perf-Attack: PRAC는 정밀 tracking으로 Perf-Attack 영향 적음, DAPPER-H는 NRH≥500에서 0.9%.

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

- LLBC: CEASER/MIRAGE와 유사한 4-round Low-Latency Block Cipher, SCARF와 같은 경량 cipher도 사용 가능
- Hash + RGC lookup: 단일 cycle(0.25ns) 내 완료, tRRD_S 2.5ns 이내
- Open source: Ramulator 기반 (ABACUS repository 활용)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]
- [[paper-wiki/concepts/security.md|Security]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2025HPCA-summarize/dapper-a-performance-attack-resilient-tracker-for-rowhammer-defense.md|전체 요약 보기]]
