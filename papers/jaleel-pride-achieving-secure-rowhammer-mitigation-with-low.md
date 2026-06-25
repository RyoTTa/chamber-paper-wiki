---
tags: [paper, 2024, 2024ISCA, topic/dram, topic/rowhammer]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024ISCA-summarize/pride-achieving-secure-rowhammer-mitigation-with-low-cost-in-dram-trackers.md"
---

# PrIDE: Achieving Secure Rowhammer Mitigation with Low-Cost In-DRAM Trackers

**Venue:** 
**저자:** Aamer Jaleel (NVIDIA), Gururaj Saileshwar (University of Toronto), Stephen W. Keckler (NVIDIA), Moinuddin Qureshi (Georgia Tech)

## 개요

### 1.1 Rowhammer와 TRH 추세

DRAM 셀 밀도 증가에 따른 셀 간 간섭(cell interference)으로 Rowhammer 공격이 발생하며, 공격 행(aggressor row)에 대한 빠른 반복 활성화(activation)가 인접 행(victim row)의 비트 플립을 유발한다. Rowhammer threshold (TRH)는 지난 10년간 DDR3 139K(TRH-S, 2014)에서 LPDDR4 4.8K(TRH-D, 2020)까지 급감했으며 (Table II), 이는 Rowhammer가 단순 신뢰성 문제를 넘어 권한 상승(privilege escalation), 기밀성 파괴 등 시스템 탈취로 이어질 수 있는 심각한 보안 위협임을 의미한다.

### 1.2 In-DRAM Tracker의 자원 제약과 보안 취약성

Rowhammer 완화는 일반적으로 aggressor row를 식별하는 tracking 메커니즘과 식별된 행의 인접 행을 refresh 하는 mitigative action으로 구성된다. DDR4의 TRR(Targeted Row Refresh)을 비롯한 상용 in-DRAM tracker는 DRAM 모듈의 logic space 제약으로 bank당 1~30개 수준의 극소수 entry만 보유한다:

- **TRR (DDR4):** 최대 30 entry/bank. TRRespass로 tracker capacity 초과 시 tracked aggressor eviction, Blacksmith로 deterministic insertion policy 우회 — 수 분 내 파괴.
- **DSAC (Samsung):** 20 entry/bank. min-counter 기반 확률적 insertion. TRRespass + Blacksmith 패턴으로 공격 행에 9K+ activation 허용 (TRH=500 설계치 대비).
- **PAT (SK Hynix):** 8 entry/bank. 기존 대비 30% 낮은 failure rate 주장하나 기존 설계가 수 분 내 파괴되므로 PAT 역시 수 분 내 파괴.

### 1.3 근본 원인: Access-Pattern Dependent Policy Decisions

저자들은 저비용 in-DRAM tracker의 취약성 근본 원인이 **activation counter 값에 의존하는 정책 결정**(insertion policy, eviction policy, mitigation policy)에 있다고 진단한다. Attacker가 dummy row의 access frequency를 조작하여 tracker의 insertion/eviction/mitigation decision을 임의로 조작할 수 있기 때문에, counter-driven policy로는 **모든 access pattern에 대한 worst-case failure rate의 a priori bound가 불가능**하다 (Fig. 1b). 이러한 access-pattern dependence로 인해 특정 패턴을 craft하여 tracker를 파괴하는 것이 가능해진다.

### 1.4 목표

저비용이면서 **모든 access pattern에 대해 provably secure**한 (time-to-fail이 수 년~수 만 년 범위) in-DRAM tracker 개발. 핵심 통찰: **tracker의 policy decision이 access pattern에 independent해야 worst-case failure rate의 해석적 boundedness가 가능**하다.

## 방법론

### 3.1 방법론

| 항목 | 구성 |
|------|------|
| **Simulator** | Gem5 |
| **CPU** | 4-core OoO, 3GHz, 8-wide fetch, 192-entry ROB |
| **LLC** | 4MB, 16-way, 64B lines |
| **Memory** | 32GB DDR5, 32 banks × 1 rank × 1 channel |
| **Timing** | tRCD-tCL-tRP-tRC = 14.2-14.2-14.2-45 ns |
| **Rows** | 128K rows, 8KB row buffer |
| **Workloads** | 17 SPEC2017 rate + 17 mixed workloads |
| **Simulation** | Skip 25B instructions, simulate 250M |
| **RFM overhead** | 180ns bank unavailable (2 rows each side refresh) |
| **Target-TTF** | 10,000 years/bank |

### 3.2 성능 (Fig. 14)

- **PrIDE:** slowdown **0%** (mitigation이 DDR5 spec의 tRFC window 내 처리)
- **PrIDE+RFM40:** slowdown **0.1%**
- **PrIDE+RFM16:** slowdown **1.6%**

### 3.3 Target-TTF 민감도 (Table VIII)

| Target-TTF | TRH-S* | TRH-D* |
|------------|--------|--------|
| 100 years | 3.42K | 1.71K |
| 1K years | 3.63K | 1.81K |
| 10K years (default) | 3.83K | 1.92K |
| 100K years | 4.04K | 2.02K |
| 1M years | 4.25K | 2.12K |

### 3.4 Device TRH별 System Time-to-Fail (Table IX)

| Device TRH-D | PrIDE | PrIDE+RFM40 | PrIDE+RFM16 |
|-------------|-------|-------------|-------------|
| 4800 (현재) | > 1M years | > 1M years | > 1M years |
| 2000 | 2,936 years | > 1M years | > 1M years |
| 1800 | 36 years | > 1M years | > 1M years |
| 1600 | 153 days | > 1M years | > 1M years |
| 1400 | 2 days | > 1M years | > 1M years |
| 1200 | 32 min | > 1M years | > 1M years |
| 1000 | 23 sec | 674 years | > 1M years |
| 800 | < 1 sec | 42 days | > 1M years |
| 600 | < 1 sec | 10 min | > 1M years |
| 400 | < 1 sec | < 1 sec | 140 years |

### 3.5 공격 패턴 실증 평가 (Fig. 15)

500개 TRRespass + Blacksmith 기반 랜덤 패턴, 100개 seed 반복:
- **PrIDE:** Max Disturbance = 1,300 activations
- **PrIDE+RFM40:** 566 activations
- **PrIDE+RFM16:** 266 activations
- 다른 probabilistic tracker (PRoHIT, DSAC, PARA-MC, PARFM): 8,000+ activations

### 3.6 에너지 오버헤드 (Table X)

| Config | ACT Energy | Non-ACT Energy | Total Energy |
|--------|-----------|----------------|-------------|
| Base (No Mitig) | 1x | 1x | 1x |
| PrIDE | 1.054x | 1.002x | **1.006x** |
| PrIDE+RFM40 | 1.086x | 1.002x | **1.008x** |
| PrIDE+RFM16 | 1.226x | 1.010x | **1.024x** |

ACT energy 증가 (5~23%)는 mitigative refresh + RNG access에 기인하나, activation energy가 전체의 13%에 불과해 총 오버헤드는 미미.

### 3.7 Ablation: Buffer Size vs TRH*

Buffer size가 5 이상에서 Tardiness 증가로 TRH*가 재상승. 4-entry에서 3.79K로 최적, 16-entry는 4.42K로 열화. **"큰 buffer가 항상 좋은 것은 아니다."**

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

| 항목 | 세부사항 |
|------|---------|
| **Tracker structure** | 4-entry circular FIFO buffer |
| **Entry format** | 17-bit row-id + 3-bit mitigation level (20-bit total) |
| **Storage per bank** | **10 bytes SRAM** |
| **PRNG** | 7-bit TRNG, 0.00025 mm², 0.08 mW/bank leakage, 24.9 pJ/activation (10 nm) |
| **MC-side RFM** | RAA counter 1 byte/bank |
| **비교:** Graphene (TRH=4K) | 42.5 KB/bank |
| **비교:** TWiCe (TRH=4K) | 300 KB/bank |
| **비교:** CAT (TRH=4K) | 196 KB/bank |
| **비교:** Graphene (TRH=400) | 425 KB/bank |

PrIDE는 Graphene 대비 **4,250배 적은 SRAM** 사용 (10 bytes vs 42.5 KB).

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]


## 전체 요약

[[../paper-summaries/2024ISCA-summarize/pride-achieving-secure-rowhammer-mitigation-with-low-cost-in-dram-trackers.md|전체 요약 보기]]
