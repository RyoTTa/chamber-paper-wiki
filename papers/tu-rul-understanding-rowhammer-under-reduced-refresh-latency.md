---
tags: [paper, 2025, 2025HPCA, topic/dram, topic/rowhammer]
venue: "2025 IEEE International Symposium on High Performance Computer Architecture (HPCA 2025)"
year: 2025
summary_path: "../paper-summaries/2025HPCA-summarize/understanding-rowhammer-under-reduced-refresh-latency.md"
---

# Understanding RowHammer Under Reduced Refresh Latency: Experimental Analysis of Real DRAM Chips and Implications on Future Solutions

**Venue:** 2025 IEEE International Symposium on High Performance Computer Architecture (HPCA 2025)
**저자:** Yahya Can Tuğrul, A. Giray Yağlıkçı, İsmail Emir Yüksel, Ataberk Olgun, Oğuzhan Canpolat, Nisa Bostancı, Mohammad Sadrosadati (ETH Zürich), Oğuz Ergin (TOBB ETÜ / Univ. of Sharjah), Onur Mutlu (ETH Zürich)

## 개요

- **RowHammer:** DRAM 행(row)을 반복 활성화(hammering)하면 인접 행(victim row)에서 bitflip이 발생하는 read disturbance 현상 [2].
- RowHammer threshold (NRH)는 DRAM 세대가 진행됨에 따라 급감:
  - 2012–2013년 제조 칩: 수만 회 activation 필요
  - 2020년 제조 칩: **4.8K activation**으로 bitflip 발생 [63] → 한 자릿수(order of magnitude) 감소
- 최근 HBM2도 DDR4/LPDDR4만큼 취약 [90], [91].
- **기존 RowHammer mitigation 메커니즘 분류:**
  1. **High-performance-overhead mitigations:** PARA [2], RFM [139] — trigger algorithm이 간단하여 area overhead는 낮지만, 많은 false-positive로 인해 **불필요한 preventive refresh를 다량 수행** → 높은 성능/에너지 overhead.
  2. **High-area-overhead mitigations:** PRAC [142], Hydra [122], Graphene [111] — 정교한 trigger algorithm으로 aggressor row를 정확히 탐지, preventive refresh는 적으나 높은 area overhead.

- **Motivation analysis (Figure 3):** 60개 multi-programmed 4-core workload 대상 5개 RowHammer mitigation, NRH=1K~32 구간 분석:
  - NRH가 감소할수록 모든 mitigation의 preventive refresh 시간 비율 급증.
  - RFM worst-case 43.05%, PARA 19.19%, PRAC 10.95% (NRH=32에서).
  - Graphene: 가장 낮은 성능 overhead, but NRH=32에서 **4.45% chip area** (10.38mm², dual-rank 16-bank 기준).
  - Hydra: preventive refresh 시간은 가장 적으나(2.68%), **DRAM에 counter metadata 저장**으로 인한 memory channel 점유로 system-level slowdown 큼 [128–130].

- **핵심 질문:** preventive refresh의 charge restoration latency(tRAS)를 줄이면 RowHammer vulnerability에 어떤 영향이 있을까?

### Motivational 분석 (Figure 4)

Mfr. H, S 두 DDR4 모듈에서 tRAS를 33ns(nominal)에서 감소시키며 5가지 지표 측정:
1. **Preventive Refresh Latency:** tRAS + tRP로 계산, tRAS에 비례 감소.
2. **RowHammer Threshold (NRH):** tRAS 64%(Mfr. H)/36%(Mfr. S) 감소 시 NRH 변화 <5%.
3. **Preventive Refresh Count:** 1/NRH에 비례, NRH 감소로 증가.
4. **Total Time Cost:** (Refresh Count × Refresh Latency) → **inflection point 존재** (Mfr. H: 36% tRAS, Mfr. S: 45% tRAS). 최적 지점에서 Total Time Cost 43%(Mfr. H)/28%(Mfr. S) 감소.
5. **Total Energy Cost:** 유사한 inflection point (Mfr. H: 36%, Mfr. S: 64%)에서 40%/19% 감소.

**결론:** charge restoration latency 감소는 RowHammer mitigation overhead를 낮추는 유망한 접근법이나, **안전한 감소 한계를 알기 위해 실제 DRAM 칩의 특성을 이해하는 것이 필수적**.

---

## 방법론

### 3.1 Effect on RowHammer Threshold (NRH)

**Takeaway 1:** Charge restoration latency는 NRH에 유의미한 영향 없이 안전한 최소값까지 감소 가능.

- **Figure 6 (box-and-whiskers, 모든 tested row):**
  - Mfr. H: tRAS **64% 감소**(0.36tRAS)까지 NRH 변화 <3%
  - Mfr. M: tRAS **82% 감소**(0.18tRAS)까지 NRH 변화 <3% → 가장 큰 guardband
  - Mfr. S: tRAS **36% 감소**(0.64tRAS)까지 NRH 변화 <3%
  - 매우 낮은 tRAS (예: 0.18tRAS)에서는 일부 cell이 data retention failure (NRH=0)

**Takeaway 2:** Lowest observed NRH (모듈 내 최저 NRH 행)도 유의미한 변화 없음.

- **Figure 7:** Lowest NRH → Mfr. M은 73% tRAS 감소에도 변화 없음. Mfr. H 36%, Mfr. S 19% 감소까지 <3% 변화.

**Row-level 분석 (Figure 8):**
- Mfr. H (H8): 0.45tRAS에서 NRH 25% 이상 감소 행 <0.45%
- Mfr. S (S1): 0.45tRAS에서 NRH 25% 이상 감소 행 10.34%
- NRH가 낮은 행(nominal에서 취약한 행)이 reduced tRAS에서 반드시 더 취약해지지는 않음 (x=10K → y≈1.0).

### 3.2 Effect on RowHammer BER

**Takeaway 3:** Charge restoration latency는 BER을 유의미하게 증가시키지 않고 안전한 최소값까지 감소 가능.

- **Figure 9:** BER은 superlinear하게 증가. Mfr. H/M/S 각각 36%/82%/19% tRAS 감소까지 BER 증가 <3%.

### 3.3 Combined Effect of Temperature

**Takeaway 4:** 온도는 charge restoration latency와 RowHammer vulnerability의 관계에 유의미한 영향 없음.

- **Figure 10:** 50°C→80°C 변화에도 normalized NRH 변화 0.31%(Mfr. H)/0.08%(Mfr. S), BER 변화 1%/9%.

### 3.4 Effect of Repeated Partial Charge Restoration

**Takeaway 5:** Reduced charge restoration latency는 다수의 연속 preventive refresh에서도 안전하게 사용 가능, 단 횟수 제한 필요.

- **Figure 11 (box-and-whiskers, 1-5회 반복):**
  - Mfr. H: 반복 횟수에 관계없이 NRH 거의 동일
  - Mfr. S: 반복 횟수 증가 시 NRH 감소 경향
  - 매우 낮은 tRAS(0.27tRAS)에서 반복 복원이 data retention failure 유발 가능

- **Figure 12 (H7, S6, 최대 15K회, 0.36tRAS):**
  - Mfr. H (H7): 15K회까지 NRH 변화 1.24%
  - Mfr. S (S6): 2.5K회에서 일부 data retention failure, 1K회까지 안전
  - NPCR (Max Consecutive Partial Restorations): Mfr. H 15K, Mfr. S 1K

### 3.5 Effect on Half-Double Access Pattern

- **Figure 13:** Mfr. S 모듈은 Half-Double bitflip 미발생. Mfr. H 모듈:
  - 0.36tRAS에서 Half-Double bitflip 행 비율 39.31% 감소(오히려 개선)
  - 반복 횟수(1~5회)에 따른 변화 1.50% → 영향 미미
  - Double-sided RowHammer가 Half-Double보다 훨씬 효과적인 공격 패턴.

### 3.6 Effect on Data Retention Time

- **Figure 14 (S4):** 0.36tRAS에서 10회 partial restoration 후에도 256ms retention 시 bitflip 발생 없음.
  - 그러나 일부 행에서 data retention time 감소 (256ms→128ms 등).

---

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1 Overview

**PaCRAM (Partial Charge Restoration for Aggressive Mitigation):** memory controller에 구현, 기존 RowHammer mitigation과 통합.

- **2가지 preventive refresh latency 사용:**
  - **Nominal latency:** full charge restoration (tRAS_nominal + tRP)
  - **Reduced latency:** partial charge restoration (tRAS_reduced + tRP)
- Periodic refresh는 영향 없음.

### 4.2 두 가지 도전 과제와 해결

**Challenge 1: NRH 감소 (Takeaway 1)**
- 해결: 실험적 characterization 데이터 기반으로 기존 RowHammer mitigation의 NRH 값을 감소시켜 설정.
- 예: Mfr. H 모듈 H5의 tRAS_reduced=0.27tRAS에서 lowest NRH = 10.2K → 9.4K (8% 감소). PaCRAM-H는 NRH=1024 등을 942로 scale-down.

**Challenge 2: 반복 partial restoration으로 인한 failure (Takeaway 5)**
- 해결: 각 DRAM 행을 2가지 state로 관리:
  - **F-state (Full):** nominal latency로 refresh 필요
  - **P-state (Partial):** reduced latency로 refresh 가능
- 초기 모든 행 = F-state.
- Full restoration 수행 시 → P-state로 전환.
- 주기적으로 모든 행을 F-state로 reset → 연속 partial restoration 횟수 제한.

### 4.3 Full Charge Restoration Interval (tFCRI)

- 수식: `tFCRI = NPCR × (NRH × tRC + tRAS_reduced + tRP)`
  - NPCR: characterization으로 얻은 최대 연속 partial restoration 횟수
  - NRH: scale-down된 RowHammer threshold
- 예: S6, tRAS_reduced=0.36tRAS, NRH=3.9K, NPCR=2K → tFCRI = **374ms**
- tFCRI > tREFW(64ms)이면 periodic refresh가 full restoration을 수행하므로 모든 preventive refresh에 reduced latency 사용 가능.

### 4.4 FR (Fully Restored) Bit Vector

- 각 DRAM 행당 **1 bit** SRAM 저장.
- 64K rows/bank → **8KB/bank**.
- Dual-rank 16-bank 시스템: **0.09% of Intel Xeon die area [144]** (1.35% of memory controller area [222]).
- CACTI [221] 분석: SRAM access latency **0.27ns** — DRAM row activation latency(14ns)에 의해 완전히 가려짐.
- Metadata 크기가 NRH에 독립적 → RowHammer vulnerability 증가에도 scalable.

### 4.5 Security Analysis

PaCRAM은 기존 RowHammer mitigation mechanism의 security guarantee를 그대로 유지:
- NRH를 characterization 기반으로 정확히 감소시켜 설정 → under-mitigation 방지
- 연속 partial restoration 제한 → data retention failure 방지
- 기존 mitigation의 security property는 PaCRAM 통합 후에도 동일

### 4.6 On-DRAM-die Mitigation 지원

PRAC [142], Self-Managing DRAM [133] 등 on-DRAM-die mitigation에서도 PaCRAM 구현 가능:
- DRAM chip 내 FR 저장, Mode Register (MR)에 refresh latency 정보 저장.
- Self-Managing DRAM에서는 memory controller 변경 없이 DRAM 내부에서 완전 구현 가능.

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]


## 전체 요약

[[../paper-summaries/2025HPCA-summarize/understanding-rowhammer-under-reduced-refresh-latency.md|전체 요약 보기]]
