---
tags: [paper, 2024, 2024MICRO, topic/dram, topic/rowhammer, topic/security, topic/storage]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024MICRO-summarize/impress-securing-dram-against-data-disturbance-errors-via-implicit-row-press-mitigation.md"
---

# ImPress: Securing DRAM Against Data-Disturbance Errors via Implicit Row-Press Mitigation

**Venue:** 
**저자:** 

## 개요

DRAM scaling으로 인한 inter-cell interference는 Data-Disturbance Errors(DDE)를 유발하며, 이는 reliability뿐 아니라 심각한 security threat이다.

**Two modalities of DDE:**
1. **Rowhammer (RH):** Aggressor row의 반복적 activation → victim row에 bit-flip. TRH: 4.8K (LPDDR4, 2020).
2. **Row-Press (RP):** [Luo et al., ISCA 2023] Row를 장시간 open 상태로 유지 → 인접 row의 cell들이 bit-line으로 charge leakage → **18× ~ 156× 더 적은 activation으로 bit-flip 유발**. RH mitigation (TRH 기준 설계)을 TRH 미만 activation으로 break.

**기존 해결책 — ExPress (Explicit Row-Press)의 한계:**
- Memory Controller가 row-open time을 tMRO로 제한
- RH threshold를 T* (TRH보다 낮음)로 재설정
- **세 가지 문제:**
  1. **High performance overheads:** Early row closure → row buffer hit 감소 (특히 Stream workload에서 tMRO=66ns 시 ~10% slowdown). 낮은 threshold로 인한 추가 mitigation.
  2. **High storage overheads:** Counter-based tracker의 entries가 threshold에 반비례 → 2배 증가.
  3. **Incompatibility with in-DRAM trackers:** tMRO는 MC-only policy → in-DRAM tracker(Mithril, MINT)는 RP에 무방비.

**Goal:** tON 제한 없이, TRH 영향 없이, MC-based + in-DRAM tracker 모두에 적용 가능한 RP solution.

## 방법론

### 1. Unified Charge-Loss Model

RH와 RP의 damage를 단일 metric으로 통합:

**RH Charge-Loss:** K activation → TCL_RH = K (unit damage per tRC)

**RP Charge-Loss (Equation 2-3):**
```
TCL_RP = 1 + α × (tON − tRAS) / tRC
```
- tON: row-open time
- α (≤ 1): RP의 상대적 charge leakage rate per tRC
- α = 1이면 RP = RH (worst-case assumption, device-independent)

**CLM (Conservative Linear Model):**
- Short-duration RP (≤ 8 tRC): α = 0.35 (실측 데이터 기반)
- Long-duration RP (1~9 tREFI): α = 0.48 (Samsung/Hynix/Micron 3사 모든 디바이스 커버, Figure 7)
- Device-independent 설계를 위해 α = 1 사용 권장

**Key observations:**
1. RP는 RH보다 훨씬 느린 공격 (α ≤ 1).
2. RP에 소비되는 시간은 RH를 수행하지 못하는 시간 → standalone RH가 가장 빠른 공격.
3. Secure RP solution은 α에 의존하지 않거나 α=1로 보수적 설계해야 함.

### 2. ImPress-N (Naive Version)

**Design (Figure 9):**
- Time을 tRC window로 분할
- Window 내에 activation 발생 → 해당 row가 RH tracking에 참여
- Row가 full tRC window 동안 open → activation과 동등하게 간주, RH tracking에 참여
- **ORA (Open-Row Address) register**로 open row 추적

**Implementation:** Timer (1 byte) + ORA (3 bytes) = 4 bytes/bank. Underlying tracker 변경 불필요.

**Unmitigated RP bound (Figure 10):**
- 공격자가 tRC+tRAS 동안 row open, window 경계 직전에 decoy row로 precharge
- RH tracker는 activation 1회만 감지, 실제 RP damage는 1+α
- **Effective threshold: T* = TRH / (1+α)**
  - α=0.35 → T* = 0.74 TRH
  - α=1 → T* = 0.5 TRH (ExPress와 동일)

**MC-based tracker에 대한 영향:** ExPress와 threshold/performance/storage 영향 유사. But in-DRAM tracker에도 적용 가능 (tON 제한 없음).

### 3. ImPress-P (Precise Version) — Main Contribution

**Design (Figure 11):**
- Timer로 tON 측정 (row open 시 start, precharge 시 stop)
- **EACT = (tON + tPRE) / tRC** — Equivalent Activation Count
- EACT ≥ 1 보장, fractional value 가능 (e.g., tON = tRAS + tRC/2 → EACT = 1.5)

**Tracker adaptation:**
- **Counter-based (Graphene, Mithril):** Counter += EACT (instead of ++)
- **Probabilistic (PARA, MINT):** p̂ = p × EACT (instead of constant p)

**Storage requirements:**
- Timer: 10 bits/bank (DRAM cycle granularity, 2.66GHz → tRC = 128 cycles → division by tRC = right-shift 7)
- Counter fractional part: 7 bits

**Precision vs Threshold (Figure 12):**
| Fractional bits | Effective T* |
|----------------|--------------|
| 7 (precise) | 1.0 TRH |
| 6 | 0.985 TRH |
| 4 | 0.94 TRH |
| 0 (=ImPress-N) | 0.5 TRH |

Default: 7 bits → TRH unchanged.

**Tracker별 ImPress-P 적용:**

| Tracker | Entries (No-RP) | Entries (ImPress-P) | Storage Overhead |
|---------|----------------|---------------------|-----------------|
| Graphene (TRH=4K) | 448/bank | 448 (28-bit each) | 1.25× |
| Mithril (TRH=4K, RFMTH=80) | 383/bank | 383 (with 7-bit frac) | 1.25× |
| MINT | 4 bytes | 5 bytes (CAN 7→14 bit) | 1.25× |

vs ExPress/ImPress-N (TRH=4K): Graphene 896 entries (2×), Mithril 1545 entries (4×).

## 핵심 기여

1. **"Row-open time → equivalent activation" 통찰**: RP damage를 RH framework의 언어로 변환 → 기존 RH tracker를 수정 없이(ImPress-N) 또는 최소 수정(ImPress-P)으로 RP 대응 가능.
2. **ImPress-P는 ideal properties 달성**: tON 제한 없음, TRH 불변, 모든 tracker(MC + in-DRAM) 호환, α-independent → device-independent 설계.
3. **1.25× storage overhead**로 ExPress/ImPress-N의 2×~4× overhead 대비 획기적 개선.
4. ImPress-P는 Graphene/PARA/Mithril/MINT 모두에 적용 가능한 **universal DDE mitigation framework**.
5. PRAC(per-row activation counting)과도 결합 가능 → ultra-low TRH까지 확장.

## 주요 결과

### Methodology

- **Simulator:** ChampSim (cycle-level multi-core) + DRAMSim3 (DDR5 enhanced)
- **CPU:** 8-core OoO @ 4GHz, 6-wide, 352-ROB, 16MB LLC
- **Memory:** DDR5, 64GB, 2 channels, 32 banks × 1 rank × 2 sub-channels
- **Workloads:** SPEC2017 (10), Stream (4), Mixed Stream (6)
- **RH parameters:** TRH = 4K, target bank failure rate = 0.1 FIT (~30× lower than natural error rate)
- **RFM:** RFMTH = 80, RFM latency = 205ns (half tRFC)

### Performance Results

**Graphene:**
- No-RP baseline: ~1.0 (all workloads)
- ExPress (α=1): SPEC negligible, Stream significant slowdown
- ImPress-P (α=1): Negligible overhead across all workloads (no tON restriction, no threshold reduction)

**PARA (Figure 13b):**
- ExPress: Stream workload significant slowdown due to early row closure + increased mitigations
- ImPress-P: Significantly reduced overhead vs ExPress

**In-DRAM (MINT, Figure 13c):**
- ImPress-N (α=1): Threshold 1.6K → 3.1K (RFM-40 required)
- ImPress-P (α=1): Performance identical to No-RP

### Activation and Energy Overheads (Figure 14)

| Config | Demand ACTs | Mitigative ACTs | Total |
|--------|------------|----------------|-------|
| Graphene No-RP | 1.0 | <1% | ~1.0 |
| Graphene ExPress | 1.56 | low | +56% |
| Graphene ImPress-P | 1.0 | low | +1% |
| PARA No-RP | 1.0 | baseline | ~1.0 |
| PARA ExPress | 1.56 | + | +61% |
| PARA ImPress-P | 1.02 | +12% | +14% |

DRAM energy 증가: ExPress → +6-7%, ImPress-P → +1-2%.

### Scalability to Lower TRH (Figure 15)

| TRH | Graphene No-RP | ExPress | ImPress-P |
|-----|---------------|---------|-----------|
| 4K | 1.0 | ~1.0 | ~1.0 |
| 2K | ~1.0 | small | ~1.0 |
| 1K | ~1.0 | 0.956 | ~1.0 |

| TRH | PARA No-RP | ExPress | ImPress-P |
|-----|-----------|---------|-----------|
| 4K | 1.0 | ~0.98 | ~0.99 |
| 2K | ~0.99 | ~0.95 | ~0.97 |
| 1K | ~0.985 | ~0.91 | ~0.92 |

낮은 TRH에서도 ImPress-P가 ExPress 대비 우수한 성능 유지. PRAC(per-row counter) 결합 시 7-bit fractional EACT를 counter에 통합 가능.

### Comparison Summary (Table III)

| Property | ExPress | ImPress-N | ImPress-P |
|----------|---------|-----------|-----------|
| Limits tON | Yes | No | No |
| Affects Threshold | Up to 2× | Up to 2× | No (1×) |
| Performance Overheads | High | Medium | Low |
| More Tracking Entries | Up to 2× | Up to 2× | No (1×) |
| Wider Entries | No | No | Minor (7-bit) |
| In-DRAM Trackers | Incompatible | Compatible | Compatible |
| Device Dependency | α-dependent | α-dependent | None |

## 구현

- **Framework:** C++ performance model + analytical security model
- **Simulator integration:** ChampSim + DRAMSim3 (enhanced for DDR5)
- **Storage overhead:** ImPress-N: 4 bytes/bank, ImPress-P: 10-bit timer + 7-bit fractional counter extension

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]
- [[paper-wiki/concepts/security.md|Security]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2024MICRO-summarize/impress-securing-dram-against-data-disturbance-errors-via-implicit-row-press-mitigation.md|전체 요약 보기]]
