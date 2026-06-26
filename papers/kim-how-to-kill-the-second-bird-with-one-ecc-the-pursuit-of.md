---
tags: [paper, 2023, 2023MICRO, topic/dram, topic/rowhammer, topic/security]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023MICRO-summarize/how-to-kill-the-second-bird-with-one-ecc-the-pursuit-of-row-hammer-resilient-dram.md"
---

# How to Kill the Second Bird with One ECC: The Pursuit of Row Hammer Resilient DRAM

**Venue:** 
**저자:** 

## 개요

DRAM-based main-memory systems는 공정 미세화에 따른 random error 증가에 대응하기 위해 **on-die ECC (OECC)** 와 **rank-level Chipkill** (SCC: single-chip correction) 을 도입해왔다. 그러나 Row Hammer(RH)는 row 전체에 걸친 burst error를 유발하여 ECC의 correction capability를 초과하는 uncorrectable error(UE)를 발생시키므로, 강력한 Chipkill조차 𝑇𝑅𝐻를 2–3× 증가시키는 데 그칠 뿐이다 (Figure 5; Double-Chipkill 기준 평균 ×2.6 증가).

실제 208개 DDR4 chip (2 vendor, 14 DIMM) 대상 FPGA 기반 RH 실험 결과, RH victim row가 OECC UE 혹은 Chipkill UE에 도달하는 시점에는 **수십 개의 OECC codeword가 동시에 single error를 갖는 분포**를 보인다 (Observation-1; Figure 4). 또한 𝑇𝑅𝐻는 139K (PARA 시절) → 4K까지 급감해왔으며, 기존 probabilistic RH 방어 기법(PARA, SRS)은 낮은 𝑇𝑅𝐻에서 실용적이지 않은 오버헤드를 보인다 (예: SRS, 𝑇𝑅𝐻=2K에서 weighted speedup degradation 최대 43%).

**Threat model**: (1) Attacker는 bank 내 PA row의 full knowledge 보유, (2) 최대 frequency로 activation stream 발생 가능, (3) aggressor가 𝑇𝑅𝐻에 도달하면 OECC+SCC Chipkill을 무력화할 만큼의 bitflip 발생, (4) Blinded attack(𝐴𝑡𝑘_𝐵𝑙𝑖𝑛𝑑𝑒𝑑)은 임의 victim에서 두 개 이상의 chip symbol이 𝑇𝑅𝐻 adjacent hammering을 겪을 때 성공, (5) Targeted attack(𝐴𝑡𝑘_𝑇𝑎𝑟𝑔𝑒𝑡𝑒𝑑)은 특정 victim row에서 동일 조건 성공, (6) Non-RH hard error는 RH error 발생 시점에 공존하지 않음 (RAS feature로 사전 제거됨).

## 방법론

Cube는 (1) chip-wise PA-to-DA mapping scramble과 (2) OECC error profile 기반 RH victim diagnosis의 두 가지 기술로 구성된다.

## 핵심 기여

**핵심 contribution**: 기존 ECC(Chipkill + OECC)가 RH에 취약한 근본 원인은 모든 chip에서 victim row가 동일한 Chipkill codeword에 집중되기 때문. Cube는 chip별로 PA-to-DA mapping을 다르게 scramble하여 RH victim을 여러 codeword로 분산시킴으로써, 단일 Chipkill codeword에서 multi-chip error(DRH)를 확률적으로 극도로 낮춘다.

**Key insight**: OECC의 detection capability와 Chipkill의 correction capability를 synergistic하게 결합 — OECC scrubbing의 error profile로 RH victim을 탐지·진단하고, SCC Chipkill로 proactive correction. 이는 "one ECC로 두 마리 새(RH + random error)를 잡는" 접근.

**Quantified impact**:
- Probabilistic RH protection scheme과 결합 시 failure probability 최대 ×10²⁵ 감소
- SRS의 performance overhead 24.3% 감소, table size 39.9% 감소 (𝑇𝑅𝐻=2K, target 10⁻¹⁰/year)
- 하드웨어 추가 비용: scramble function < 0.2ns latency, 1.37% tREFI overhead for scrubbing

## 주요 결과

각 chip 𝑖의 PA-to-DA mapping function 𝐹𝑖(PA) = DA는 다음 세 요건을 충족해야 한다:

- **R-i) No collision of Set_victim**: 임의의 PA_agg에 대해 모든 chip에서의 victim PA 집합(𝐹⁻¹_𝑖(𝐹_𝑖(PA_agg) ± 1)) 내에서 어떤 두 PA도 충돌하지 않아야 함. 단일 PA_agg hammering이 동일 Chipkill codeword에서 두 chip을 동시에 손상시키는 DRH(double RH success) 방지.
- **R-ii) No aliasing**: 𝑁_row → 𝑁_row permutation. 단순 hashing(Bloom filter 등)은 aliasing이 있으므로 사용 불가.
- **R-iii) Efficient hardware**: ACT command critical path에 위치. AES나 Fisher-Yates shuffle은 너무 느리거나 면적이 큼.

**Vanilla Scramble Function**:
```
𝐹ᵢ(PA) := (PA × 𝑐ᵢ) mod 𝑁_row
```
- 모든 𝑐ᵢ가 서로 다르고, 어느 두 𝑐ᵢ도 (𝑁_row − 𝑐ⱼ)와 충돌하지 않으면 R-i 만족.
- 모든 𝑐ᵢ가 홀수이면 Euler's totient theorem에 의해 R-ii 만족 (2^𝑘와 coprime이므로 permutation).
- 상수 곱셈 + modular (shift 연산)만 필요 → R-iii 만족; 합성 결과 0.2ns 미만 (TSMC 40nm).

Blast radius가 2 이상이면 double key (2 × 𝑐ᵢ), 3이면 triple key 사용.

### 4.2 Scramble Function Confidentiality

Vanilla scramble은 단일 query(공격자가 PA_agg1 hammering으로 victim PA 획득)로 𝑐⁻¹_𝑖 노출 위험 존재:
```
𝐹⁻¹_𝑖(PA_agg × 𝑐ᵢ + 1) − 𝐹⁻¹_𝑖(PA_agg × 𝑐ᵢ − 1) = 2𝑐⁻¹_𝑖
```

이를 방지하기 위해 **global Feistel cipher**를 MC 단에서 적용:
```
Encrypted Scramble: 𝐹ᵢ(PA) := (Enc(PA) × 𝑐ᵢ) mod 𝑁_row
```

구현은 4-round unbalanced Feistel cipher (LLBC 기반). 17-bit input → 8-bit L + 9-bit R. S-box는 4 XOR gate latency. Boot-time random key 𝑘_enc. 전체 scramble function latency < 0.2 ns. Worst-case tRCD +1 cycle overhead는 모든 workload에서 weighted speedup 0.5% 미만.

Dynamic remapping scheme (SRS, SHADOW 등)과 결합 시 DynRand(PA, time)이 Enc(PA) 역할을 대체하며, chip-wise 𝑐ᵢ는 design-time 고정 가능.

### 4.3 RH Diagnosis using OECC Error Profile

Observation-1에 기반: RH victim row는 다수의 OECC codeword에 error를 갖는다. JEDEC 표준화된 OECC scrubbing (ECS mode)을 활용.

**동작 방식**:
1. 각 chip은 PA_scrub register를 가지며, {𝐹⁻¹_𝑖(𝐹_𝑖(PA_scrub) ± 1)}에 해당하는 victim row들을 scrubbing
2. 32Gb DRAM 기준, 10분 scrubbing window → 1.37% reduced tREFI (112 additional REFab per tREFW)
3. Per chip: scrubbed address (17-bit) + error count per row (3-bit) → 70B buffer
4. 매 tREFW마다 MC가 모든 chip의 error profile을 수집
5. Aggregate error count가 DiagTH(기본값=6)를 초과하면 Chipkill correction 개시

Diagnosis threshold DiagTH=6에서 false-negative 0 (multi-bit error의 undetectable 확률 0.018–0.2%는 별개), false-positive도 non-RH scaling fault와의 구분 가능 (Figure 7).

**RH victim proactive correction**: OECC scrubbing으로 RH victim을 진단하면, victim address에 대한 application access를 기다리지 않고 즉시 Chipkill correction 수행. 이로써 attacker는 DRH를 단일 scrubbing window(10분) 내에 성공시켜야 하며, 보안 수준이 추가로 최대 ×10⁶ 향상.

### 4.4 동작 예시

Conventional Chipkill에서 PA=100을 hammering하면 2개의 victim row(PA=99, PA=101)에서 multi-bit burst error → Chipkill UE (Figure 6a). Cube에서는 각 chip에서 victim PA가 모두 달라: chip 0은 PA=𝐹⁻¹₀(𝐹₀(100)−1), chip 16은 PA=𝐹⁻¹₁₆(𝐹₁₆(100)+1), ... → 36개 victim row 각각이 서로 다른 Chipkill codeword에 분산 → 각각 SCC Chipkill로 correctable (Figure 6b).

## 보안 분석

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]
- [[paper-wiki/concepts/security.md|Security]]


## 전체 요약

[[../paper-summaries/2023MICRO-summarize/how-to-kill-the-second-bird-with-one-ecc-the-pursuit-of-row-hammer-resilient-dram.md|전체 요약 보기]]
