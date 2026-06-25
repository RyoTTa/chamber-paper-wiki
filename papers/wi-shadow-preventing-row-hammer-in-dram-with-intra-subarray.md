---
tags: [paper, 2023, 2023HPCA, topic/dram, topic/rowhammer]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023HPCA-summarize/shadow-preventing-row-hammer-in-dram-with-intra-subarray-row-shuffling.md"
---

# SHADOW: Preventing Row Hammer in DRAM with Intra-Subarray Row Shuffling

**Venue:** 
**저자:** 

## 개요

Row Hammer (RH)는 DRAM에서 특정 row(aggressor)를 반복적으로 activate할 때 물리적으로 인접한 row(victim)에서 bit-flip이 발생하는 현상이다. RH는 privilege escalation, cross-VM attack, 정보 탈취 등 심각한 보안 위협으로 발전해왔다.

**악화되는 상황:**
- 공정 미세화로 인해 RH threshold (Hcnt)가 급격히 낮아짐: 2014년 139K → 2022년 4.8K (29× 감소, Table I)
- Non-adjacent RH attack (blast attack): aggressor row가 인접하지 않은 row까지 영향을 미침 (blast radius 최대 6)

**기존 HW 기반 RH 방어의 한계:**
- **TRR (Target Row Refresh):** victim row를 추가 refresh. Blast radius가 커지면 multiple victim refresh 필요 → 성능/에너지 overhead 증가. Half-double attack에 취약.
- **Throttling:** 의심스러운 thread의 ACT frequency 제한. 낮은 Hcnt에서 과도한 지연 발생, misidentification 위험.
- **RRS (Randomized Row-Swap):** MC에서 aggressor row를 random row와 swap. Row-swap 시 memory channel 전체를 blocking (4000+ ns) → latency-critical workload에 치명적.
- **Counter structure:** 대부분의 기법이 SRAM/CAM 기반 tracking table 필요. MC-side는 pessimistic 설계로 거대한 저장공간 소모 (RRS: bank당 43KB SRAM → 16 rank 기준 20MB+). DRAM-side는 엄격한 area budget 제약. Hcnt가 낮아질수록 counter 수가 거의 exponential하게 증가.

## 방법론

### 3.1 방법론

| 항목 | 구성 |
|------|------|
| 실제 시스템 | Intel Core i9-7940X @ 3.10 GHz, 14 cores, DDR4-2666 4ch 16GB |
| Architecture simulator | McSimA+ (DDR5-4800) |
| SPICE simulation | 55nm Rambus DRAM → 22nm scaling, PTM models |
| Synthesis | Synopsys Design Compiler, CMOS 40nm → 22nm DRAM process |
| Workloads | SPEC CPU2017 (spec-high/med/low 분류), GAPBS (Kronecker graph 2^26), NPB (class-C), mix-high(14), mix-blend(14), mix-random(32) |
| Baselines | PARFM, Mithril-perf (10KB CAM/bank), Mithril-area (RAAIMT=32), DRR (double refresh rate), BlockHammer, RRS |

### 3.2 보안 분석 (Table II)

목표: DDR5-4800 rank(32 banks)에서 연간 bit-flip 확률 <1%.

**Attack scenario I:** 공격자가 RFM interval마다 다른 PA row를 activate → Birthday paradox 패턴. Incremental refresh로 window 제한 → N_row 크기로 제한.
**Attack scenario II:** 공격자가 subarray 내 여러 aggressor 동시 activate → row-shuffle target이 되지 않을 확률 이용.
**Attack scenario III:** 공격자가 multiple subarray에 걸쳐 aggressor 분산.

| RAAIMT | Hcnt=8K | Hcnt=4K | Hcnt=2K |
|--------|---------|---------|---------|
| 128 | 2E-15 | 4E-01 | 1 |
| 64 | 2E-43 | 1E-14 | 5E-01 |
| 32 | 0 | 1E-43 | **9E-15** |

Hcnt=2K에서도 RAAIMT=32로 near-complete protection 달성.

### 3.3 실제 시스템 성능 (Fig. 8)

- **Single-thread:** spec-high에서도 2% 미만 성능 저하 (tRCD 증가에도 불구)
- **Multi-thread/multi-program:** SHADOW는 PARFM과 comparable 또는 superior, 특히 낮은 Hcnt에서 우수
- Mithril-perf는 더 낮은 overhead이나 10KB CAM/bank 필요 → DRAM 제조에 부적합
- **Worst-case synthetic adversarial pattern:** 3% (RFM 없음) / 9% (RFM 포함) 미만 성능 저하

### 3.4 tRCD Sensitivity (Fig. 9)

tRCD'를 23~27 tCK로 변화시켜도 Hcnt=2K에서 overhead <4% (빈번한 RFM command가 주된 요인).

### 3.5 Blast Radius Sensitivity (Fig. 10)

Blast radius >2에서 SHADOW 성능이 PARFM, Mithril보다 우수. RAAIMT=2K 기준, blast radius 증가에도 성능 저하 minimal.

### 3.6 Architecture Simulation (Fig. 11)

Hcnt=4K 이하에서 SHADOW가 가장 우수한 성능:
- **RRS:** 낮은 Hcnt에서 memory channel blocking으로 인한 과도한 overhead (기존 연구들에서 지적된 문제)
- **BlockHammer:** 낮은 Hcnt에서 지연 시간 과다, misidentification 증가
- **SHADOW:** DRAM 내부 bandwidth 활용, row-shuffle 효율적 (178~186 ns)

### 3.7 Area (Synthesis 결과)

- SHADOW logic: DDR5 chip 대비 **0.47%** area overhead (0.35 mm²)
- DRAM capacity: 추가 rows로 **0.6%** (empty rows + remapping-rows), 기존 spare-row scheme 범위 내
- Per-bank SHADOW controller: ACT counter, 6×9-bit latch, 7-bit latch, MUX, control logic
- Per-subarray: MUX + DEMUX
- PRINCE RNG unit: DRAM chip 대비 <0.1%

**핵심:** Prior works(RRS 등)와 달리, SHADOW의 area overhead는 Hcnt와 무관하게 고정 (SRAM/CAM counter table 불필요).

### 3.8 Power (Fig. 12)

System-level power overhead: Hcnt=2K, memory-intensive workload에서도 **0.63% 미만**. Power 소비의 주원인은 row-shuffle보다 추가 remapping-row access.

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

- **SHADOW Controller (Verilog):** Synopsys Design Compiler로 CMOS 40nm 합성, 22nm DRAM process로 scaling (ASIC 대비 10× less dense)
- **SPICE 회로 모델:** 55nm Rambus DRAM → 22nm ITRS roadmap scaling, PTM HP/LP models
- **RNG:** PRINCE block cipher (Gbit/sec throughput), LFSR 옵션 (DDR5 이미 LFSR 보유)
- **RFM emulation:** 실제 시스템에서 tREFI 축소로 RFM 효과 재현 (Intel PCM tool 활용)
- **Simulator modification:** McSimA+에 DDR5-4800 설정 추가

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]


## 전체 요약

[[../paper-summaries/2023HPCA-summarize/shadow-preventing-row-hammer-in-dram-with-intra-subarray-row-shuffling.md|전체 요약 보기]]
