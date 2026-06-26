---
tags: [paper, 2024, 2024MICRO, topic/dram, topic/rowhammer, topic/security, topic/virtual-memory]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024MICRO-summarize/mint-securely-mitigating-rowhammer-with-a-minimalist-in-dram-tracker.md"
---

# MINT: Securely Mitigating Rowhammer with a Minimalist In-DRAM Tracker

**Venue:** 
**저자:** 

## 개요

Rowhammer(RH)는 DRAM row를 반복적으로 activation하면 인접한 victim row에 bit-flip이 발생하는 data-disturbance 오류이다. 공격자는 이를 악용해 page table bit-flip → privilege escalation, confidentiality breach 등을 수행할 수 있다. Rowhammer Threshold(TRH)는 DDR3 139K에서 LPDDR4 4.8K까지 급격히 감소했으며, 지속적인 DRAM scaling으로 인해 더욱 낮아질 전망이다.

**In-DRAM tracker의 두 가지 근본적 제약:**
1. **Refresh-synchronized mitigation:** DDR5에서는 tREFI(3.9µs)마다 REF 수행. DRAM 칩은 REF 시간의 일부를 steal하여 RH mitigation(aggressor row의 victim row refresh)을 수행하지만, 여러 aggressor row를 동시에 처리할 수 없고 bursty mitigation이 불가. 최대 1개 aggressor row / tREFI 처리.
2. **SRAM budget 한계:** DRAM chip 내 aggressor tracking용 SRAM budget은 bank당 수 bytes에 불과. DDR4의 TRR(1-30 entries)는 TRRespass, Blacksmith로 쉽게 break. Samsung DSAC, SK Hynix PAT도 불안전.

**기존 tracker 분류:**
- **Past-centric (counter-based):** Mithril, ProTRR. TRH=1K에서 1400 entries/bank 필요 → impractical.
- **Present-centric (probabilistic):** InDRAM-PARA (PARA를 in-DRAM에 적용). 각 activation을 p=1/73 확률로 sampling하여 SAR에 저장. 두 가지 문제: (1) Non-uniform mitigation probability — tREFI 내 위치에 따라 survival probability가 0.37~1.0으로 2.7x 차이 (2) Non-selection — 모든 73 activation slot이 사용되어도 37% 확률로 아무것도 선택되지 않음 → classic single/double-sided attack에 취약. TRH-D* = 3732.
- **PRCT (Per-Row Counter Table):** Idealized design, row당 counter 1개. TRH-D* = 623.

**Goal:** 1-entry tracker로 secure mitigation 달성 (TRH-D* = 1400 수준).

## 방법론

### 1. MINT의 핵심 아이디어: Future-centric selection

기존 tracker가 "과거" 행동(count)이나 "현재" activation을 기반으로 mitigation 대상을 결정하는 것과 달리, MINT는 **미래**의 어떤 activation이 mitigation 대상이 될지를 REF 시점에 미리 결정.

- **Intuition:** 각 REF마다 최대 1개 row만 mitigation 가능 → ideally 1-entry tracker면 충분. 기존 방식은 overwrite와 non-selection 문제로 1-entry 구현이 불가능했음.

### 2. MINT 동작 방식

MINT는 3개 register로 구성:
- **SAN (Selected Activation Number, 7-bit):** REF 시점에 URAND(1,73)로 설정. 다음 tREFI 구간에서 mitigation 대상이 될 activation 번호.
- **CAN (Current Activation Number, 7-bit):** tREFI 내에서 각 activation에 sequence number 부여 (1~M, M=73).
- **SAR (Selected Address Register, 18-bit + valid bit):** CAN == SAN 시점의 row address를 저장.

**Step-by-step (Figure 9):**
1. REF 시점: SAN ← URAND(1, 73), CAN ← 0, SAR.invalid
2. tREFI 동안: 각 ACT마다 CAN++. CAN == SAN이면 해당 row address → SAR.
3. 다음 REF: SAR이 valid이면 해당 row의 victim rows refresh. (blast radius 내 neighbor rows)

**Guaranteed properties:**
- Overwrite 불가: tREFI 당 최대 1개 row만 SAR에 저장.
- Continuous activation 보호: 동일 row가 M번 연속 activation되면 반드시 선택됨 → classic single/double-sided attack 무력화.

### 3. Security Analysis

**Worst-case pattern 도출:**
- MINT는 tREFI 내 동일 row의 activation 횟수에 비례하여 selection probability 증가 (n회 → n/73).
- 따라서 최적 공격은 tREFI 당 attack row를 **1회만** activation (stealth 극대화).
- **Pattern-2 (Multi-Row, Single-Copy):** k개 attack row를 tREFI 당 1회씩 activation. k=73일 때 TRH* = 2763.
- Pattern-3 (Multi-Row, Multi-Copy)는 copies 증가 시 TRH* 급감 → 비효과적.

**Transitive Attack (Half-Double) 방어:**
- Row-C의 continuous RH 공격 → MINT가 매 REF마다 Row-C neighbor (Row-B, D) refresh → mitigative refresh 자체가 Row-A, E에 silent damage.
- MINT 해결책: **Transitive Mitigation** — SAN 선택 시 74개 slot 사용 (0~73). SAN=0이면 "transitive mitigation" → SAR에 저장된 row의 victim-of-victim refresh.
- 수정 후 TRH* = 2800 (74 slot → p=1/74).

**Spatial Correlation Attack 면역:**
- Counter-based tracker는 double-sided 공격에서 victim이 양쪽 aggressor로부터 2T activation을 받기 전에 mitigation이 안 되면 실패.
- MINT는 probabilistic selection이므로 Row-B 선택 시 Row-A,C refresh, Row-D 선택 시 Row-C,E refresh → victim(Row-C)은 B+D의 합산 확률로 보호 → TRH-D* = 1400.

## 핵심 기여

1. **Future-centric selection** 패러다임: 과거/현재 기반 tracking 대신 "미래의 어떤 activation을 mitigation할지 미리 결정" → 1-entry로 secure RH mitigation 가능.
2. MINT는 TRH-D* = 1482를 15 bytes/bank로 달성. 677-entry counter-based tracker와 동등한 보안성, PRCT 대비 1.9x threshold.
3. **DMQ**는 refresh postponement 문제를 해결하는 general solution — 모든 low-cost tracker에 적용 가능.
4. RFM co-design으로 TRH-D* = 356까지 확장 가능 (0%~2.5% performance overhead).
5. **JEDEC PRAC (Per-Row Activation Counting)의 대안**: PRAC는 9% area overhead, 10% tRC 증가를 요구. MINT는 negligible cost로 유사한 보호 수준 제공 → 저비용 DRAM에서 PRAC 선택을 회피 가능.
6. ImPress와 결합 시 Row-Press까지 방어하는 통합 DDE mitigation 플랫폼.

## 주요 결과

DDR5는 최대 4개 REF 연기 가능 → 최대 365 activation (73×5)이 mitigation 없이 발생.

**DMQ 없을 때:** MINT, PARFM 등 low-cost tracker는 decoy로 첫 73개 activation 소비 후 나머지 292개 activation을 attack row에 집중 → **478K activations (!)** 을 무방비로 허용.

**DMQ (Delayed Mitigation Queue):**
- NumACTs > M (73)이면 pseudo-mitigation 수행 → 선택된 row address를 4-entry FIFO (DMQ)에 삽입.
- 실제 REF 시 DMQ의 oldest entry를 mitigation. DMQ가 비었으면 tracker 정상 동작.
- TRH-D* = 1404 (기본), Adaptive Attack(ADA)에서 최대 1482.
- DMQ로 인한 storage overhead: 9.5 bytes/bank.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]
- [[paper-wiki/concepts/security.md|Security]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2024MICRO-summarize/mint-securely-mitigating-rowhammer-with-a-minimalist-in-dram-tracker.md|전체 요약 보기]]
