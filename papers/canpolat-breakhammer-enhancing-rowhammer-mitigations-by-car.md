---
tags: [paper, 2024, 2024MICRO, topic/dram, topic/rowhammer, topic/security]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024MICRO-summarize/breakhammer-enhancing-rowhammer-mitigations-by-carefully-throttling-suspect-threads.md"
---

# BreakHammer: Enhancing RowHammer Mitigations by Carefully Throttling Suspect Threads

**Venue:** 
**저자:** 

## 개요

### 1.1 RowHammer 위협과 방어의 역설

DRAM 셀 밀도 증가로 RowHammer 취약성이 악화됨. 2012-2013년 제조 칩 대비 2018-2020년 제조 칩은 훨씬 적은 row activation으로 bitflip 발생 [62]. DDR5 표준은 Per Row Activation Counting (PRAC)이라는 on-DRAM-die 방어 메커니즘을 도입했으나, NRH(Neighbor Row Hammer threshold)가 낮아질수록 RowHammer-preventive action (예: victim row refresh) 빈도가 급증함.

**공격자-방어자 역설:** RowHammer 방어 메커니즘 자체가 새로운 공격 표면이 됨. malicious thread가 고의로 많은 RowHammer-preventive action을 유발하여 DRAM bandwidth를 고갈시키는 **memory performance attack**이 가능. 이는 benign application의 성능을 심각하게 저하시킴.

### 1.2 기존 해결책의 한계

- **BlockHammer [88]:** 자주 activate되는 row를 blacklist하고 refresh까지 차단. NRH가 낮아지면 benign application조차 많은 row를 blacklist에 등록하게 되어 성능이 급격히 저하됨. NRH 64에서 98.0% 성능 저하.
- 기존 RowHammer mitigation들 (PARA, Graphene, Hydra, TWiCe, AQUA, REGA, RFM, PRAC)은 공격자 식별 능력이 없어 모든 thread에 동등하게 preventive action을 적용.

**핵심 문제:** 누가 RowHammer-preventive action을 유발하는지 식별하고, 해당 thread만 선별적으로 제한하는 메커니즘 부재.

## 방법론

### 3.1 방법론

| 항목 | 구성 |
|------|------|
| **Simulator** | Ramulator2, cycle-accurate |
| **Processor** | 4-core, 4.2GHz, 4-wide issue, 128-entry instr window |
| **LLC** | 8MB, 64B line, 8-way |
| **Memory** | DDR5, 1ch, 2 ranks, 8 bank groups × 2 banks, 64K rows/bank |
| **Scheduler** | FR-FCFS+Cap (Cap=4) |
| **RowHammer Mechanisms** | PARA, Graphene, Hydra, TWiCe, AQUA, REGA, RFM, PRAC (8종) |
| **Workloads** | 90개 4-core mixes: SPEC2006/2017, TPC, MediaBench, YCSB |
| **Mix Categories** | HHHH, HHMM, MMMM, HHLL, MMLL, LLLL (각 15개) |
| **NRH Range** | 4096, 2048, 1024, 512, 256, 128, 64 |
| **Metrics** | Weighted speedup, unfairness (max slowdown), DRAM energy |
| **Config** | TH_window=64ms, TH_threat=32, TH_outlier=0.65, P_oldsuspect=1, P_newsuspect=10 |

### 3.2 Under RowHammer Attack (Attacker Present)

**성능 (NRH=1K, Fig. 6):**
- 평균 **84.6%** weighted speedup 향상, 최대 **170.0%**.
- 90개 모든 workload에서 attacker 탐지 및 throttling 성공.

**Unfairness (NRH=1K, Fig. 7):**
- 평균 **45.8%** unfairness 감소, 최대 **90.6%**.
- LLLA mix에서 가장 큰 개선(55.9%), HHHA에서 가장 작은 개선(24.7%) — high memory intensity application이 attacker에 대한 자연스러운 interference 제공.

**NRH Scaling (Fig. 8, NRH 4K→64):**
- 전 NRH 범위 평균 **90.1%** speedup, 최대 **162.4%**.
- NRH < 256에서 PARA, NRH < 512에서 AQUA는 throttling 후에도 성능 저하 지속 (PARA: stateless probabilistic refresh, AQUA: costly row migration).

**RowHammer-Preventive Actions 감소 (Fig. 10):**
- 평균 **71.6%** 감소, 최대 **91.8%**.
- NRH 감소에 따라 모든 baseline 메커니즘의 preventive action 폭증.

**Memory Latency (NRH=64, Fig. 11):**
- 모든 메커니즘에서 memory latency 감소, 일부는 No Defense baseline보다 낮은 latency 달성. Attacker의 메모리 계층 전반(memory request scheduler, caches) 간섭이 크게 감소했기 때문.

**DRAM Energy (Fig. 12, NRH 4K→64):**
- 평균 **55.4%** energy 절감, 최대 **67.4%**.
- NRH 64에서 AQUA는 22.4×, RFM은 3.7× 에너지 오버헤드 발생.

### 3.3 No RowHammer Attack (All Benign)

- **성능 (NRH=64, Fig. 13):** 평균 **0.7%** 성능 향상, 최대 2.4%. 거의 무시할 수준.
- **Unfairness (NRH=1K, Fig. 14):** 평균 **0.9%** 증가. 2.2% 시뮬레이션에서만 benign thread가 suspect로 오식별.
- **NRH Scaling (Fig. 15):** NRH < 1024에서 모든 메커니즘에 대해 소폭 성능 향상.

### 3.4 BlockHammer 비교 (Fig. 18)

- BreakHammer-paired 메커니즘이 모든 NRH 값에서 BlockHammer 능가.
- BlockHammer는 NRH 4K에서 78.6% 성능 향상이나 NRH 64에서 **98.0% 성능 저하**. Row blacklisting이 benign application까지 차단.
- BreakHammer는 최악의 scaling을 보이는 AQUA, PARA와 결합해도 BlockHammer보다 우수.

### 3.5 Sensitivity Analysis (Fig. 19)

TH_threat, TH_outlier, TH_window에 대한 sensitivity 평가. 넓은 범위에서 안정적 성능. TH_threat=32, TH_outlier=0.65가 최적 균형.

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

| 항목 | 상세 |
|------|------|
| **구현 언어** | Chisel HDL → Verilog (Synopsys Design Compiler 합성) |
| **Process** | 65nm |
| **Counter per thread** | 2× 32-bit score + 1× 16-bit activation + 2× 1-bit suspect flag |
| **면적** | 0.000105 mm²/channel → Intel Xeon 대비 **0.0002%** |
| **Pipeline** | 8-stage, fully pipelined |
| **클럭** | 1.5GHz (~0.67ns) — DDR5 tRRD(5ns)보다 빠름 |
| **위치** | Memory controller 근처, DRAM 칩/인터페이스 변경 없음 |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]
- [[paper-wiki/concepts/security.md|Security]]


## 전체 요약

[[../paper-summaries/2024MICRO-summarize/breakhammer-enhancing-rowhammer-mitigations-by-carefully-throttling-suspect-threads.md|전체 요약 보기]]
