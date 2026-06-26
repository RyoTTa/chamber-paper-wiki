---
tags: [paper, 2025, 2025ASPLOS, topic/dram, topic/rowhammer, topic/security]
venue: ""
year: 2025
summary_path: "../paper-summaries/2025ASPLOS-summarize/moat-securely-mitigating-rowhammer-with-per-row-activation-counters.md"
---

# MOAT: Securely Mitigating Rowhammer with Per-Row Activation Counters

**Venue:** 
**저자:** 

## 개요

Rowhammer 현상은 DRAM row를 반복적으로 activate하면 인접 row에서 bit-flip이 발생하는 보안 취약점으로, 지난 10년간 Rowhammer Threshold(T_RH)가 140K[24]에서 4.8K[21]까지 감소했다. 기존 in-DRAM 솔루션은 크게 두 가지 근본적 제약을 가진다:

- **Space challenge:** In-DRAM tracker의 SRAM budget이 bank 당 수 바이트에 불과하여 모든 aggressor row를 추적할 수 없음. DDR4 TRR은 1~30개 entry만 보유[11] → TRRespass[7], Blacksmith[14] 등으로 쉽게 우회됨.
- **Time challenge:** REF operation 동안 transparent하게 mitigation을 수행해야 하므로, mitigation rate(예: 1 aggressor row per 4 tREFI)가 낮으면 Feinting attack[27]으로 T_RH를 초과하는 activation 발생 가능 (Table 2: mitigation rate 1/4 tREFI에서 T_RH bound = 2195).

**Optimal SRAM tracker**는 수백~수천 개의 entry가 필요하여 상용 채택이 비현실적이다(Fig. 1a).

### PRAC+ABO Framework

JEDEC은 DDR5 specification에 **PRAC(Per-Row Activation Counting)**과 **ABO(Alert-Back-Off)**를 도입했다[1, 18]. PRAC은 각 DRAM row에 activation counter를 내장하고, ABO는 DRAM 칩이 memory controller에 ALERT 신호를 보내 추가 mitigation 시간을 확보하는 프로토콜이다 (Fig. 2). ABO 동작: ALERT assertion 후 180ns 동안 정상 동작 → 350ns × (1~4) RFM 수행 → 최소 1~4회 activation 후 다음 ALERT 가능. tPRE가 16ns→36ns로 증가하나 tRAS가 32ns→16ns로 감소하여 tRC는 48ns→52ns로 소폭 증가.

**핵심 문제:** PRAC+ABO는 framework일 뿐, 실제 security는 implementation에 의존한다. JEDEC은 의도적으로 구현을 DRAM vendor에게 맡겼다. Panopticon[3]이 PRAC+ABO의 영감이 되었으나, 본 논문은 Panopticon이 안전하지 않음을 입증한다.

## 방법론

### 1. Panopticon 공격: Jailbreak Pattern (§3)

**Panopticon 구조 (Fig. 3):** Bank 당 8-entry queue. Row counter의 threshold bit(예: bit-8 → T_RH=128)가 toggle되면 queue에 진입. Queue overflow 시 ALERT 발생. FIFO order로 mitigation. Queue에는 row address만 저장되고 counter value는 저장되지 않음.

**Deterministic Jailbreak:**
1. 8개 row(A-H)에 각각 128회 activation 수행 → 8개 row가 동일 tREFI 내에 queue 진입, H가 마지막
2. H를 tREFI 당 32회 계속 activation → queue overflow 방지 (ALERT 회피)
3. FIFO order로 mitigation되므로 H는 queue 체류 중 8×128=1024회 추가 activation → 총 **1152회 (9× threshold)**
4. Pattern은 threshold=128인 Panopticon에 대해 9배의 activation을 유발

**Randomized Panopticon 우회 (Fig. 4):**
- Phase 1: 8개의 random row(A-H)를 32회씩 circular access → heavy-weight row(counter 96-127, 확률 1/4)로 queue를 채움
- Phase 2: random row X에 1024회 activation
- 성공 확률: (1/4)^8 = 2^(-16) → iteration 당 256μs → 평균 **16초** 내 성공
- Fig. 5: 5분 내 1145회 activation 도달 (9× threshold)

### 2. MOAT 설계 (§4)

**핵심 통찰:** Proactive mitigation(during REF)은 한 번에 최대 1개의 aggressor row만 처리 가능 → multi-entry queue 대신 **single entry tracking**으로 충분.

**구조 (Fig. 6):**
- **CTA (Current Tracked Addr):** Bank 당 1개. Row address + counter value 저장. Mitigation period 내 가장 높은 counter를 가진 row tracking.
- **CMA (Current Mitigated Addr):** 현재 mitigation 중인 row address.
- **Dual thresholds:**
  - **ETH (Eligibility Threshold):** Proactive mitigation 대상 선정. Counter > ETH이고 CTA의 현재 counter보다 크면 CTA overwrite.
  - **ATH (ALERT Threshold):** Counter > ATH이면 ALERT 신호 발생 → reactive mitigation.

**동작:**
1. Row activation 시 counter increment (in-DRAM array + CTA)
2. Counter > ETH이고 CTA.counter보다 크면 CTA 갱신
3. 5 tREFI 주기마다 mitigation: CTA→CMA transfer, CMA의 aggressor row에 대해 4 victim row refresh + counter reset
4. Counter > ATH이면 즉시 ALERT → CTA row를 CMA로 latch → reactive mitigation

**Safe counter reset on refresh (Fig. 7):**
- Spatial contiguous refresh grouping (8K groups, 8 rows each)
- Refresh된 group의 마지막 2개 row counter를 SRAM에 복사 (bank 당 2 bytes)
- 다음 group refresh 시 이전 group 완전 safe → SRAM counter는 해당 row activation 시 increment, ALERT trigger에도 사용

**T_RH bound:** ALERT가 stop-the-world + instantaneous라고 가정하면 T_RH ≈ ATH+2 (ATH=64 → T_RH=66).

### 3. Delayed ALERT의 영향: Ratchet Attack (§5)

JEDEC ABO spec은 ALERT 간 minimum activation이 존재 (ABO Level 1: 4 ACTs, Level 4: 7 ACTs — Fig. 8). 이 inter-ALERT activation을 악용하여 ATH보다 훨씬 많은 activation을 유발 가능.

**Ratchet Attack (Fig. 9):**
1. **Pool 생성:** Feinting attack으로 ATH까지 도달한 candidate row pool 구축
2. **Staggered ALERT:** 한 row의 ALERT trigger → Before-RFM ACTs(3회) + After-RFM ACTs(1회)를 나머지 candidate rows에 분산
3. Row가 mitigation되면서 pool이 축소 → 마지막 남은 row에 모든 activation 집중

**결과 (Fig. 10):** ATH=64, Level 1에서 Ratchet attack으로 최대 99회 activation 가능 → **MOAT with ATH=64 → T_RH=99**. ATH=128 → T_RH=161.

**중요:** Current ABO spec으로는 T_RH < 50을 tolerate하는 것이 비현실적(ABO Level 1, ATH=32에서 T_RH=69, slowdown 2.94%).

## 핵심 기여

1. **Panopticon 취약성 최초 입증:** Jailbreak pattern으로 threshold=128인 Panopticon을 9배(1152 activations) 초과. Deterministic은 즉시, randomized는 평균 16초 내 break.
2. **MOAT: Provably secure + low overhead:** Dual threshold(ETH/ATH) + single-entry tracking으로 T_RH=99(ATH=64)에서 0.27% slowdown, 7 bytes/bank SRAM. PRAC+ABO framework의 실용적 reference implementation.
3. **Delayed ALERT의 보안 영향 최초 분석:** Ratchet attack으로 inter-ALERT activation이 T_RH에 미치는 영향 정량화. Current ABO spec으로 T_RH < 50 tolerating은 비현실적.
4. **성능 공격 분석:** TSA attack으로 최대 52% throughput loss 가능하나, 기존 memory contention 공격과 유사한 수준 → DoS 우려 아님.
5. **Design 권고사항:** (a) Queue는 짧을수록 좋음 (b) Queue entry에 counter 포함 필수 (c) ABO Level-1(tALERT=530ns) 권장 (d) BAT-RFM은 불필요.

## 주요 결과

### 실험 환경 (Table 3)

| 항목 | 구성 |
|------|------|
| Simulator | Cycle-level multi-core + detailed memory model |
| Core | 8-core, 4GHz, 4-wide, 256-entry ROB, OoO |
| LLC | 8MB, 16-way, 64B lines |
| Memory | 32GB DDR5 (JESD79-5C), 32 banks × 2 sub-channels × 1 rank |
| Rows/bank | 64K rows, 8KB rows |
| Mapping | Coffee Lake mapping, closed-page policy |
| tALERT | 530ns (180ns normal + 350ns RFM) |
| Workloads | SPEC-2017 15종 (ACT-PKI ≥ 0.5) + GAP suite 6종 |
| 실행 | 8-core rate-mode, core당 1B instructions |

### 성능 결과

**MOAT 기본 (Fig. 11a, ATH=64, ETH=32):**

| Metric | ATH=64 | ATH=128 |
|--------|--------|---------|
| Average slowdown | **0.27%** | ~0% |
| Worst slowdown | roms: 1.6% | 거의 0% |
| ALERT per tREFI (avg) | 0.024 | ≈0 (roms 제외) |
| T_RH tolerated | **99** | 161 |

ALERT는 sub-channel을 REF(410ns)와 유사한 시간(350ns) 동안 stall시키나, ALERT 빈도가 REF의 약 1/40 → overhead negligible.

**ETH sensitivity (Table 5, ATH=64):**

| ETH | Mitigations+ALERT/tREFW | Avg. Slowdown |
|-----|------------------------|---------------|
| 0 | 1729 (2.1× baseline) | 0.20% |
| 16 | 1329 (1.6×) | 0.20% |
| **32** | **835 (1×)** | **0.27%** |
| 48 | 505 (0.6×) | 0.64% |

ETH=32가 mitigation overhead와 performance의 최적 균형.

**Higher ABO Levels (Fig. 14, Table 6, ATH=64):**

| Design | ABO Level | Avg. Slowdown | T_RH | SRAM/bank |
|--------|-----------|---------------|------|-----------|
| MOAT-L1 | 1 | 0.27% | 99 | 7 bytes |
| MOAT-L2 | 2 | 0.33% | 87 | 10 bytes |
| MOAT-L4 | 4 | 0.39% | 82 | 16 bytes |

### 성능 공격 분석 (§7)

**ALERT 중 throughput:** tRC=52ns(1 unit) 기준, ALERT 중 11 units 동안 4 ACTs → throughput 4/11=0.36×.

**Single-row attack (Fig. 13a):** ATH=64에서 65 ACTs + ALERT(11 units) = 76 units 동안 69 ACTs → throughput 0.9× (10% 손실).

**TSA (Torrent-of-Staggered-ALERT) Attack (Fig. 12):** Multiple bank에서 ALERT를 staggered 방식으로 trigger. 4 bank에서 24% throughput loss, 17 bank(tFAW limit)에서 52% loss.

**→ Row-buffer conflict 등 기존 memory contention 공격과 유사한 수준. DoS로 간주되지 않음.**

**Benign workload의 낮은 slowdown 원인:** Benign workload는 99.6%의 activation이 benign → activations-per-ALERT가 6500+로 attack(65)의 100배 → slowdown도 100배 낮음.

### Row-Press 대응: MOAT-RP (§9)

**설계:**
- Row-open time(tON)을 equivalent activation 수로 변환
- tEPOCH=180ns, DPE(Damage-Per-Epoch)=1.5×[26]
- tONALERT=3600ns: row가 이 시간 이상 open되면 ALERT 강제 발생
- Tardiness Damage(TD)=20 (tONALERT 동안 missed counter update)

**T_RH = DPE × (ATH + ABOActs + TD)** (Equation 1)

| Config | ATH=64 | ATH=128 |
|--------|--------|---------|
| MOAT-RP T_RH | 179 | 272 |
| Avg. Slowdown | 3.0% | 0.6% |

## 구현

- **SRAM overhead:** Bank 당 CTA(3 bytes) + CMA(2 bytes) + safe-reset counters(2 bytes) = **7 bytes**. Chip 당(32 banks) = 224 bytes.
- **Energy overhead:** Micron Power Calculator 기준, refresh가 전체 전력의 11% 차지. MOAT의 ALERT 당 1 aggressor row mitigation은 평균 40 tREFI 당 1회 → 추가 전력 0.3% 미만.
- **Counter update timing:** tPRE=36ns 동안 read-modify-write 수행. tRC=52ns.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]
- [[paper-wiki/concepts/security.md|Security]]


## 전체 요약

[[../paper-summaries/2025ASPLOS-summarize/moat-securely-mitigating-rowhammer-with-per-row-activation-counters.md|전체 요약 보기]]
