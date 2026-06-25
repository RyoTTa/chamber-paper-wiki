---
tags: [paper, 2025, 2025HPCA, topic/dram, topic/rowhammer, topic/virtual-memory]
venue: "2025 IEEE International Symposium on High Performance Computer Architecture (HPCA 2025)"
year: 2025
summary_path: "../paper-summaries/2025HPCA-summarize/auto-rfm-scaling-low-cost-in-dram-trackers-to-ultra-low-nrh.md"
---

# AutoRFM: Scaling Low-Cost In-DRAM Trackers to Ultra-Low Rowhammer Thresholds

**Venue:** 2025 IEEE International Symposium on High Performance Computer Architecture (HPCA 2025)
**저자:** Moinuddin Qureshi (Georgia Institute of Technology)

## 개요

- Rowhammer는 DRAM 행(row)을 반복 활성화(activation)하여 인접 행에서 bit-flip을 유발하는 데이터 무결성 오류 [21].
- 공격자가 page table 등 보호된 데이터 구조의 비트를 뒤집어 **privilege escalation** [5], [6], [46], **기밀성 침해** [25] 가능.
- Rowhammer threshold (TRH)는 DRAM 세대가 진행될수록 급감:
  - **DDR3-old (2014):** TRH-S = 139K [21]
  - **DDR3-new:** TRH-D = 22.4K [17]
  - **DDR4 (2018):** TRH-D = 10K–17.5K [17]
  - **LPDDR4 (2020):** TRH-D = 4.8K–9K [17], [23]
- In-DRAM mitigation은 DRAM 칩 내에서 투명하게 Rowhammer를 해결하므로 매력적이지만, **공간**(aggressor row tracking)과 **시간**(victim refresh 수행) 두 자원이 모두 필요함.
- **Low-cost in-DRAM tracker (MINT [37]):** single-entry tracker, N개 activation window에서 무작위로 한 aggressor를 선택. Window 크기(W)에 따라 TRH-D 결정:
  - W=4 → TRH-D=96, W=8 → TRH-D=182, W=16 → TRH-D=356, W=32 → TRH-D=702
- **RFM (Refresh Management, DDR5):** MC가 bank 단위 RAA 카운터로 activation 수를 세고, 임계치 도달 시 RFM 명령을 삽입 → bank가 tRFM (205ns–410ns) 동안 차단(blocking). 문제는:
  - RFM-32 (TRH-D=702): slowdown **0.2%** → 무시 가능
  - RFM-16 (TRH-D=356): slowdown **4.4%**
  - RFM-8 (TRH-D=182): slowdown **12.9%**
  - **RFM-4 (TRH-D=96): slowdown 33%** (Figure 1(d), Figure 3)
  - 일부 workload (roms, fotonik3d, lbm)에서 50% 가까운 slowdown 발생

- **핵심 동기:** threshold가 sub-100으로 감소하는 추세에서 low-cost tracker의 확장을 가로막는 주요 병목은 **RFM의 blocking latency**임.

## 방법론

1. 연속된 요청이 같은 subarray에 매핑될 확률을 무시할 수준으로 낮출 것 → **Randomized Memory Mapping**
2. SAUM이 mitigation 완료 후 반드시 해제되어 demand activation 수용 → 결정적 지연 시간 보장 (200ns)
3. Transitive attack 방어 시 재귀적 mitigation 없이 단일 mitigation round로 충분 → **Fractal Mitigation**

---

## 3. 설계/메커니즘

### 3.1 AutoRFM 동작 방식

1. **Tracker + Schedule:** MINT tracker가 AutoRFMTH 개의 activation window 내에서 무작위 aggressor 선정.
   - AutoRFMTH=4이면 4개의 activation (A,B,C,D) 중 하나 (예: 세 번째 slot C)가 mitigation 대상으로 미리 선택됨 (Figure 6).
   - window의 마지막 PRE에서 mitigation 시작 → 4회 victim refresh 수행 (aggressor ±2 행, 총 4행).
   - 최소 AutoRFMTH=4 (mitigation에 4 tRC 소요).

2. **SAUM 관리:** 한 bank 내에서 동시에 최대 1개의 SAUM만 존재. SAUM은 현재 window에서 MINT의 대상에서 제외 → 다음 window에서 반드시 해제됨.

3. **MC 변경 (Figure 7):**
   - Bank당 **busy bit** + **timestamp** (tM = 200ns later) 유지.
   - ACT 실패 시 bank를 busy로 마킹하고, timestamp 이후 busy 해제.
   - Busy 상태인 bank에는 demand request 전송 금지.
   - **SRAM overhead: bank당 2B (busy-bit 1b + timestamp 15b), 64-bank system에서 128B.**
   - 단순 설계로 per-entry metadata 회피; conflict가 드물면 복잡한 설계와 동등한 성능.

4. **DRAM 칩 변경:**
   - (a) SAUM에 대해 내부적으로 victim refresh 수행 회로 (기존 in-DRAM tracker 지원 회로 활용).
   - (b) SAUM 주소 저장 및 incoming ACT의 subarray 비교 회로. 충돌 시 ACT skip.
   - (c) DRAM interface: ALERT 신호 재사용 (DDR5 spec [14]와 유사) → ACT 실패 통지.

### 3.2 Randomized Memory Mapping (Rubix)

**문제:** AMD Zen mapping은 4KB 페이지의 두 cache line을 같은 행(row)에 배치하고 페이지를 32개 bank에 분산 → 연속 접근이 같은 subarray 충돌 유발.

- Baseline (AMD-Zen) + AutoRFM-4: 평균 slowdown **16.5%**, roms 40%+, fotonik3d/lbm 30%+ (Figure 8a).
- ALERT/ACT 비율 평균 **3.7%** — 256 subarray에서 기대값 0.4% 대비 9배 이상 높음 (Figure 8b).

**해결: Rubix [42]**
- Low-latency block cipher (**K-cipher [24]**, latency 3 cycles)로 line address → encrypted line address 변환.
- Address encryption으로 spatial correlation 완전 제거 → 모든 subarray에 거의 균등 분포.
- Row-buffer hit 희생하나 bank-level parallelism 증가로 상쇄.

**결과:**
- Randomized Mapping + AutoRFM-4: 평균 slowdown **3.1%** (Figure 8a).
- ALERT/ACT 비율 **0.22%** — AMD-Zen 대비 16x 감소 (Figure 8b).
- 3.1% 중 1.5%는 randomized mapping 자체 오버헤드, 1.6%는 SAUM 충돌.

### 3.3 Fractal Mitigation (FM)

**문제: Transitive Attack [48]**
- 낮은 threshold에서 victim refresh 자체가 먼 행에 Rowhammer를 유발 (예: Half-Double [23]).
- 기존 MINT의 recursive mitigation: victim row도 확률적으로 mitigation 트리거 → level-2, level-3, ... 재귀적 mitigation 발생 (Figure 9).
  - MINT window N에 대해 N+1 slot에서 선택 → row 당 선택 확률 감소 (N=4에서 25%→20%) → tolerated threshold 증가 (TRH-D=96).
  - **결정적 문제:** 재귀적 mitigation이 SAUM을 여러 라운드 동안 붙잡아 → busy 시간이 200ns~2000ns로 비결정적 → repeated ACT failure, DoS 우려.

**FM 설계 (Figure 10):**
- 4회 victim refresh 중 **d=1** (immediate neighbors) 2회는 항상 수행.
- 나머지 2회는 확률적으로 먼 neighbor에 할당:
  - d=2: 확률 1/2
  - d=3: 확률 1/4
  - d=4: 확률 1/8
  - d=x: 확률 2^(1-x)

- **구현:** 16-bit random number의 **leading zero 개수**를 이용 → leading zero가 exponential 분포를 따르므로 d = 2 + leading_zeros(Rand)로 간단히 구현.
  - Leading zero 0개 (50%): d=2
  - Leading zero 1개 (25%): d=3
  - ...

- **보안 분석 (Appendix B):**
  - 공격자가 FM의 mitigative refresh를 이용해 먼 행을 공격하는 모델: Damage = 1.25·p·N, Escape prob ≈ e^(-Damage/2.5).
  - Target MTTF=10K년 → Escape prob=10^(-18) → 최대 Damage=104 → **TRH-D ≥ 53에서 안전** (Equation 10).
  - MINT-4는 TRH-D=74, FM은 TRH-D=52 → **FM의 공격이 MINT보다 항상 비효율적**이므로 MINT+FM의 effective threshold는 MINT 단독의 74 (Figure 16).
  - Mixed attack (FM 손상 + direct activation)도 direct-only보다 낮은 성공률.

- **이점:**
  1. SAUM이 정확히 200ns 후 해제 (재귀 없음) → **결정적 latency overhead.**
  2. MINT가 N slot에서 선택 (N+1 대신) → selection probability 증가 → 더 낮은 threshold.
  3. AutoRFMTH=4 기준 FM은 TRH-D=74, Recursive Mitigation은 TRH-D=96 (Table VI).

### 3.4 왜 Randomized Mapping + RFM으로는 해결되지 않는가

Rubix는 bank당 activation 수 자체를 증가시키므로 (spread 증가), RFM의 bank-level activation 카운팅 기반 메커니즘에서는 **더 많은 RFM이 발행되어 오히려 slowdown이 증가**함:
- RFM-4 + Rubix: 35.1% slowdown vs. RFM-4 + Zen: 33.1% (Appendix C, Figure 17).

---

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1 실험 방법론

| 항목 | 구성 |
|------|------|
| **Simulator** | memsim [1] — cycle-level multi-core simulator + 상세 메모리 모델 |
| **CPU** | 8-core OoO, 4GHz, 4-wide, 256-entry ROB |
| **LLC** | 8MB shared, 16-way, 64B line |
| **Memory** | 32GB DDR5 (Table I timing 준수), 32 banks × 2 sub-channel × 1 rank, 128K rows/bank, 4KB rows, 256 subarrays/bank |
| **Memory Mapping** | AMD Zen [13] (baseline) / Rubix Randomized Mapping |
| **Workloads** | **SPEC 2017** 11종 (bwaves, fotonik3d, lbm, parest, mcf, roms, omnetpp, xz, cam4, blender, wrf), **GAP** 6종 (ConnComp, PageRank, TriCount, BFS, BC, SSSPath), **Stream** 4종 (add, triad, copy, scale) |
| **Metric** | Weighted speedup; 1B instruction per core rate mode |
| **ACT-PKI range** | 1.0 (wrf) ~ 80.7 (ConnComp) |
| **ACT-per-tREFI range** | 6.6 (wrf) ~ 35.0 (ConnComp), avg per bank |

### 4.2 AutoRFM vs. RFM 성능

| Threshold regime | RFM slowdown | AutoRFM slowdown | TRH-D (AutoRFM+FM) |
|------------------|-------------|-----------------|---------------------|
| RFMTH=32 / AutoRFMTH=32 | 0.2% | – | 702 |
| RFMTH=16 / AutoRFMTH=16 | 4.4% | – | 356 |
| RFMTH=8 / AutoRFMTH=8 | **12.9%** | **2.3%** | 161 |
| RFMTH=4 / AutoRFMTH=4 | **33.0%** | **3.1%** | **74** |

- AutoRFM-4에서 bwaves는 Rubix의 bank-level parallelism 증가로 speedup (Figure 11).
- 동일 AutoRFMTH 값에서 FM이 RM보다 낮은 TRH-D 제공 (Table VI):
  - AutoRFMTH=4: RM TRH-D=96, FM TRH-D=74
  - AutoRFMTH=5: RM TRH-D=117, FM TRH-D=96
  - AutoRFMTH=8: RM TRH-D=182, FM TRH-D=161

### 4.3 AutoRFM vs. PRAC+ABO

- PRAC (Per-Row Activation Counting, DDR5 optional): row당 activation counter 추가 → 면적 오버헤드 큼 (Hynix 설계 [20]). tRP 150% 증가 → **tRC 증가로 high threshold에서도 4% slowdown 상존** (Figure 13).
- ABO (Alert Back-Off): ALERT 사이에 허용된 activation이 공격에 악용 가능 → 추가 20-30 activation 발생 [34], [36] → 실질적 TRH ≥ 50.
- **AutoRFM:** TRH-D 74에서 3.1% slowdown → **high threshold에서 PRAC보다 낮은 오버헤드, low threshold에서 RFM보다 훨씬 낮은 오버헤드** (Figure 13).

### 4.4 Power 및 Energy

- Micron DRAM power model [32], DDR5 파라미터 기반 분석 (Figure 12):
  - Standalone Rubix: 추가 activation으로 **+36 mW**.
  - AutoRFM-8 mitigations: **+28 mW** → 총 +64 mW.
  - AutoRFM-4 mitigations: **+55 mW** → 총 +91 mW.
- DRAM이 시스템 전력의 10% 차지 시 **전체 시스템 전력 증가 1.25–2.5%**.
- Idle 시 추가 전력 없음 → energy proportionality 충족.

### 4.5 Storage Overhead

| 위치 | 항목 | 크기 |
|------|------|------|
| MC | Busy bit + timestamp per bank × 64 banks | **128 B SRAM** |
| DRAM chip | SAUM 식별 (valid bit + 8b) + MINT tracker (4B) | **5 B/bank** |
| DRAM chip | PRNG for random numbers | negligible |

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2025HPCA-summarize/auto-rfm-scaling-low-cost-in-dram-trackers-to-ultra-low-nrh.md|전체 요약 보기]]
