---
tags: [paper, 2025, 2025HPCA, topic/dram, topic/rowhammer, topic/security]
venue: "2025 IEEE International Symposium on High Performance Computer Architecture (HPCA 2025)"
year: 2025
summary_path: "../paper-summaries/2025HPCA-summarize/variable-read-disturbance-an-experimental-analysis-of-temporal-variation-in-dram-read-disturbance.md"
---

# Variable Read Disturbance: An Experimental Analysis of Temporal Variation in DRAM Read Disturbance

**Venue:** 2025 IEEE International Symposium on High Performance Computer Architecture (HPCA 2025)
**저자:** Ataberk Olgun, F. Nisa Bostancı, İsmail Emir Yüksel, Oğuzhan Canpolat, Haocong Luo, Geraldo F. Oliveira, A. Giray Yağlıkçı (ETH Zürich), Minesh Patel (Rutgers University), Onur Mutlu (ETH Zürich)

## 개요

- **Read disturbance:** DRAM 행을 반복 활성화(RowHammer [1])하거나 장시간 open 유지(RowPress [4])하면 인접 행에서 bitflip 발생.
- **Read Disturbance Threshold (RDT):** victim row에 첫 bitflip을 유발하는 데 필요한 aggressor row activation 수 (hammer count).
- 기존 read disturbance mitigation 메커니즘 (PRAC [121], [126], [138], [139], [144], Graphene [83], PARA [1], MINT [218] 등)은 **모든 DRAM 행의 최소 RDT를 정확히 식별할 수 있다는 가정**에 기반.
- 이 가정이 성립하지 않으면 mitigation의 **security guarantee가 무너짐**.

### 핵심 질문
> DRAM 행의 RDT는 시간에 따라 변하는가? 변한다면, 얼마나 정확하고 효율적으로 측정 가능한가?

---

## 방법론

### 3.1 VRD 현상의 존재 (Figure 1)

RDT는 시간에 따라 **유의미하고 예측 불가능하게 변화**. 예시 victim row:
- 100,000회 측정 중 최소 RDT가 **16,926번째** 측정에서 처음 나타남
- 전체 tested row 기준: 최소 RDT가 **최대 94,467번째** 측정에서 최초 등장
- RDT=1,000 기준, 1회 측정 시간 ≈0.1ms → 94,467회 ≈ **9.5초** (단일 행)
- 256K행 bank의 모든 행을 94,467회 측정: **약 29일**

### 3.2 RDT 분포의 통계적 특성 (Figure 4)

- RDT histogram은 정규분포와 유사 (Chi-square goodness-of-fit test, minimum p-value=0.18 → α=0.05에서 null hypothesis 기각 불가).
- 측정된 RDT 값의 개수(unique bins)는 module마다 다름: M1=11,947 bins, H1=37,761 bins, Chip1=134 bins.
- 연속 동일 값 측정: Chip1에서 최대 14회 연속, M1에서 2회 연속 (Figure 5).

### 3.3 예측 불가능성 (Figure 6)

**Finding 4:** RDT는 예측 불가능하게 변화. Autocorrelation Function (ACF) 분석 결과:
- RDT measurement series의 ACF는 Gaussian random number series의 ACF와 유의미한 차이 없음.
- 반복 패턴이 발견되지 않음.

**Takeaway 1:** RDT는 무작위적이고 예측 불가능하게 변화 → 신뢰성 있는 정확한 RDT 식별이 어려움.

### 3.4 Hypothetical Explanation (VRD 원인 가설)

- Electron migration/injection이 read disturbance의 주요 오류 메커니즘 [172], [175], [176], [187], [210], [211].
- 이 메커니즘은 aggressor/victim cell 간 shared active region의 Si/SiO₂ interface charge traps에 의해 촉진.
- **가설:** VRD는 이러한 trap의 randomly changing occupied/unoccupied states에 기인 [212], [213] — VRT(variable retention time) [147–153]과 유사한 메커니즘.
- Device-level 연구가 필요하며, 본 논문에서는 가설 수준에서 제시.

---

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1 VRD의 보편성

**Finding 5:** 모든 tested 행이 최소 1개 test parameter 조합에서 non-zero coefficient of variation (CV) 보유.
- 최대 CV = **0.52** (50번째 percentile의 CV = 0.03).

**Finding 6:** **97.1%** 행이 모든 test parameter 조합에서 VRD 보임. 나머지 2.9%도 최소 1개 조합에서 VRD.

- Worst-case temporal variation: **max RDT / min RDT = 3.5×** (1,000회 측정 기준, Figure 7).

### 4.2 적은 횟수 측정의 한계 (Figure 8)

Monte Carlo simulation (10,000 iterations, N=1,3,5,10,50,500 random sampling):

**Finding 7:** N=1 측정으로 min RDT를 찾을 확률: median 행(P50) **0.2%**. 22.4% 행은 ≤0.1%.

**Finding 8:** 낮은 확률(≤0.1%)로 min RDT를 놓치는 행의 expected RDT는 minimum 대비 **최대 1.9×**.

**Finding 9:** 측정 횟수 증가에 따른 min RDT 검출 확률 개선:

| N | Median(P50) 확률 |
|---|-----------------|
| 1 | 0.2% |
| 3 | 0.7% |
| 5 | 1.1% |
| 10 | 2.1% |
| 50 | 10.0% |
| 500 | **75.3%** |

- N=500에서도 일부 행은 **50.0% 확률**에 불과 (1,000회 중 1회만 min RDT).

**Takeaway 2:** N<500으로는 min RDT를 높은 확률로 식별 불가. 반복 측정으로 정확도 향상 가능하나 한계 존재.

### 4.3 Die Density & Technology Node 효과 (Figure 9)

**Finding 10:** VRD profile은 chip마다 상이:
- N=1, median 행의 expected normalized min RDT: Mfr. M 1.08×, Mfr. S 1.05×, Mfr. H 1.05×.
- Worst-case 행: Mfr. S 최대 **3.21×** (N=1).

**Finding 11:** **Higher density / advanced technology node → worse VRD.**
- Mfr. M 예: 8Gb-R → 16Gb-E → 16Gb-F로 density/node 발전에 따라 N=1 expected normalized min RDT 증가 (median: 1.06× → 1.07× → 1.08×, worst-case: 1.45× → 1.78×).
- 모든 제조사, 모든 N 값에서 동일 경향.

### 4.4 Data Pattern 효과 (Figure 10)

**Finding 12:** VRD profile은 data pattern에 따라 변화. Mfr. H N=1 median 행 예: 1.04×~1.06× 범위.

**Finding 13:** 모든 chip에 대해 worst VRD를 유발하는 단일 data pattern은 없음:
- Mfr. M: Checkered0, Mfr. S: Rowstripe1, Mfr. H: Checkered1, HBM2: Rowstripe0.

**Takeaway 3:** Lowest RDT의 시간적 변화 양상은 data pattern에 의존.

### 4.5 tAggOn 효과 (Figure 11)

**Finding 14:** VRD profile은 tAggOn에 따라 변화.
- Mfr. H N=1 median: min tRAS=1.054×, tREFI=1.049×, 9×tREFI=1.046×.

**Finding 15:** tAggOn 증가에 따라 VRD가 개선되거나 악화될 수 있음 (방향성 일관되지 않음). Mfr. M, H는 tAggOn 증가 시 개선, Mfr. S는 비단조적.

### 4.6 Temperature 효과 (Figure 12)

**Finding 16:** VRD profile은 온도에 따라 변화.
- Mfr. M 16Gb-E, N=1 median: 50°C=1.06× → 80°C=1.07×, worst-case: 1.22× → 1.29×.
- 모든 tAggOn, data pattern에서 일관된 경향.

**Takeaway 4:** 한 온도/한 tAggOn에서의 VRD profile이 전체 동작 범위를 대표하지 않음.

### 4.7 True-/Anti-Cell Layout 효과 (Figure 13)

**Finding 17:** True-cell vs anti-cell layout은 RDT 분포에 유의미한 영향 없음 (M0 모듈 한정).

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]
- [[paper-wiki/concepts/security.md|Security]]


## 전체 요약

[[../paper-summaries/2025HPCA-summarize/variable-read-disturbance-an-experimental-analysis-of-temporal-variation-in-dram-read-disturbance.md|전체 요약 보기]]
