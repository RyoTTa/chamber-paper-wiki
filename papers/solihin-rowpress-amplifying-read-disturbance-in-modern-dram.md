---
tags: [paper, 2023, 2023ISCA, topic/dram, topic/rowhammer]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023ISCA-summarize/rowpress-amplifying-read-disturbance-in-modern-dram-chips.md"
---

# RowPress: Amplifying Read Disturbance in Modern DRAM Chips

**Venue:** 
**저자:** 

## 개요

DRAM의 memory isolation은 시스템 신뢰성·보안·안전성의 핵심이다. RowHammer는 repeatedly opening/closing (hammering)으로 victim row에 bitflip을 유발하는 잘 알려진 read-disturb 현상이며, 공격자는 이를 악용해 privilege escalation, memory leak 등을 수행할 수 있다. RowHammer의 AC_min (최소 bitflip 유발 activation 횟수)은 최근 10년간 14× 감소했으며 [Kim+, ISCA 2020], 기술 노드가 축소될수록 악화된다.

본 논문은 **RowPress**라는 또 다른 read-disturb 현상을 최초로 실험적으로 입증한다: DRAM row를 **오래 열어두는 것(keeping open)**만으로도 인접 row에 bitflip을 유발할 수 있다.

**핵심 동기 데이터 (Fig. 1):** 164개 실험용 DDR4 칩(3개 제조사)에서 t_AggON(aggressor row on time)을 36ns→7.8µs→70.2µs→30ms로 증가시키며 AC_min을 측정:
- t_AggON = 7.8µs (t_REFI): AC_min 평균 17.6× 감소 (최대 40.7×)
- t_AggON = 70.2µs (9× t_REFI, JEDEC 허용 최대): AC_min 평균 159.4× 감소 (최대 363.8×)
- t_AggON = 30ms: **단 1회 activation으로도 bitflip 발생** (AC_min=1)

---

## 방법론

### 1. RowPress vs RowHammer: 서로 다른 현상

**Cell Overlap 분석 (§4.3, Fig. 9):**
- t_AggON ≥ 7.8µs에서 RowPress-vulnerable cell과 RowHammer-vulnerable cell 간 overlap은 **0.013% 미만** (평균)
- RowPress-vulnerable cell과 retention failure-vulnerable cell 간 overlap은 **0.34% 미만**
- 즉, RowPress는 RowHammer·retention failure와 **완전히 다른 cell set**에 영향을 미침 → 다른 failure mechanism

**Bitflip Direction (§4.3, Fig. 10):**
- Checkerboard data pattern (aggressor=0xAA, victim=0x55)에서:
  - RowHammer (t_AggON=36ns): dominant direction = **0→1**
  - RowPress (t_AggON ≥ 7.8µs): dominant direction = **1→0** (Mfr. S, H는 100% 도달)
- RowHammer가 victim cell에 전자 주입(inject)하는 반면, RowPress는 전자를 끌어당기는(attract) 방향으로 작용한다는 device-level 가설 제시 (Samsung 연구진의 "passing gate effect"와 일치 [Hong+, arXiv 2023])

### 2. t_AggON vs AC Trade-off (§4.2, Fig. 8)

AC가 증가할수록 필요한 최소 t_AggON(t_AggON_min)은 감소:

| AC | 평균 t_AggON_min (Mfr. S/H/M) |
|----|------------------------------|
| 1  | 43.3ms / 48.3ms / 44.5ms    |
| 10K | 4.3µs / 4.8µs / 4.5µs      |

Log-log scale에서 t_AggON_min 감소 기울기는 세 제조사 모두 약 -1.0으로 일관됨 → **RowPress가 DRAM 기술에 내재된(intrinsic) 현상**임을 시사.

극단 사례: Mfr. S 8Gb D-Die에서 AC=1로 t_AggON_min=9.2ms만으로도 bitflip 발생.

### 3. RowPress-ONOFF Pattern (§5.3, Fig. 18)

t_AggON과 t_AggOFF의 상호작용을 이해하기 위해, activation-to-activation interval(Δt_A2A)을 고정하고 t_AggON 비율을 0%→100%로 변화시키는 RowPress-ONOFF pattern 실험:

- **Single-sided, small Δt_A2A (≤1200ns):** t_AggON 증가 → BER **감소** (RowHammer device-level 연구[Park+, 2016; Yang+, 2019]와 일치)
- **Single-sided, large Δt_A2A (≥2400ns):** t_AggON 증가 → BER **증가** (기존 device-level 연구로 설명 불가 — 그들은 50~72.5ns 범위만 테스트)
- **Double-sided:** 모든 Δt_A2A에서 t_AggON 증가 → BER **일관되게 증가**
- 온도 증가(50°C→80°C) 시 large Δt_A2A+t_AggON에서 BER이 최대 7.5× 증가

> **Takeaway:** RowPress는 기존 device-level 연구의 실험 범위를 벗어난 영역에서 발생하며, 더 깊은 물리적 이해가 필요하다.

## 핵심 기여

1. **RowPress는 RowHammer와 다른, 새로운 DRAM read-disturb 현상이다.** Cell overlap <0.013%, bitflip direction 반대, temperature/access pattern sensitivity가 다름.

2. **RowPress는 DRAM의 read-disturb 취약성을 극단적으로 증폭한다.** AC_min을 1~2 order of magnitude 감소시키며, 극단적으로는 단 1회 row activation만으로도 bitflip 유발.

3. **RowPress는 모든 주요 제조사의 실제 DRAM 칩에 광범위하게 존재하며**, 기술 스케일링에 따라 악화된다.

4. **실제 시스템에서도 RowPress 공격이 가능하다.** On-die TRR이 존재하는 DDR4 시스템에서 user-level program으로 RowPress bitflip을 유발했으며, 동일 조건에서 RowHammer는 bitflip을 유발하지 못했다.

5. **기존 RowHammer mitigation을 저비용으로 RowPress에도 adaptation 가능하다.** Graphene-RP는 평균 -0.63%, 최대 6.4%의 추가 overhead만으로 RowHammer+RowPress를 동시 방어한다.

**Broader significance:** 이 발견은 DRAM-based system의 memory isolation을 보장하기 위해 read-disturb mitigation이 RowHammer만 고려해서는 불충분하며, RowPress를 반드시 함께 다루어야 함을 시사한다. 저자들은 multi-level(device→circuit→architecture→system)에서의 추가 연구를 촉구한다.

## 주요 결과

RowHammer에서는 double-sided가 single-sided보다 항상 더 효과적(AC_min이 더 작음)이다. 그러나 RowPress에서는 **t_AggON이 증가할수록 single-sided가 double-sided보다 더 적은 activation으로 bitflip을 유발**하는 역전 현상이 발생:

- t_AggON=1536ns, Mfr. S 8Gb B-Die, 50°C: single-sided AC_min이 double-sided보다 평균 4210회 적음
- 80°C에서 그 차이는 8699회로 확대
- t_AggON ≥ 7.8µs에서는 거의 모든 die revision에서 single-sided AC_min < double-sided AC_min

→ 이는 RowPress가 RowHammer와 근본적으로 다른 메커니즘임을 재확인한다.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]


## 전체 요약

[[../paper-summaries/2023ISCA-summarize/rowpress-amplifying-read-disturbance-in-modern-dram-chips.md|전체 요약 보기]]
