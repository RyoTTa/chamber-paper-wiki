---
tags: [paper, 2024, 2024ISCA, topic/dram, topic/pim, topic/rowhammer]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024ISCA-summarize/dramscope-uncovering-dram-microarchitecture-and-characteristics-by-issuing-memory-commands.md"
---

# DRAMScope: Uncovering DRAM Microarchitecture and Characteristics by Issuing Memory Commands

**Venue:** 
**저자:** 

## 개요

### 1.1 Reverse-Engineering 필요성

- DRAM 제조사는 chip density, energy 효율, 제조 수율 최적화를 위해 subarray 구조, row decoder, column mapping, on-die ECC 등을 proprietary로 유지 [61].
- 기존 연구들은 scattered public documents [19][21]에 기반한 가정으로 진행되어 **잘못된 결론**에 도달한 사례 다수: non-adjacent RowHammer [25], half-row [85], spare row misinterpretation [3][66].

### 1.2 세 가지 Reverse-Engineering 도구 (Table I)

| Tool | 원리 | 용도 |
|------|------|------|
| **AIB** (RowHammer + RowPress) | Aggressor row 활성화 시 물리적으로 가장 가까운 row에 bitflip 발생 | Row adjacency, subarray boundary 탐지 |
| **RowCopy** | Source row ACT → PRE 후 짧은 간격으로 dest row ACT → BL charge sharing으로 data copy | Subarray 내 row 간 adjacency, open/folded BL 구조 식별, even/odd BL 구분 |
| **Retention time test** | DRAM cell은 charged state → discharged state로 leakage | True-cell / anti-cell 구분 |

**Testbed**: Xilinx Alveo U200/U280 FPGA + SoftMC [14] + DRAM Bender [47] 개조. DDR4 RDIMM (75°C), HBM2 (상온). tCK=1.25ns(DDR4)/1.67ns(HBM2).

### 1.3 Common Pitfalls — Address/Data Mapping (Fig. 5)

연구자들이 흔히 간과하는 3가지 함정:

1. **RCD chip의 row address inversion** [21]: RDIMM/LRDIMM에서 B-side DRAM chip으로 전달되는 row/bank address가 전력 절감 목적으로 기본 활성화된 inversion에 의해 반전됨. 이를 무시하면 non-adjacent RowHammer 등 허상 관측.
2. **DRAM chip internal row remapping**: Mfr. A만 internal row remapping 사용, Mfr. B/C는 미사용. Single-sided RowHammer로 복원.
3. **DQ twisting** (Fig. 5c): DIMM의 DQ pin이 각 chip에 twisting되어 연결됨. 예: 0x55를 써도 chip은 0x33/0xCC/0x99 등 수신 → data pattern 실험 결과 왜곡.

---

## 방법론

### 3.1 Top/Bottom Cell 분류 (Fig. 11, Table IV)

6F² 구조에서 각 P-substrate는 cell pair를 공유. Top cell은 upper WL이 passing gate(PG), lower WL이 neighboring gate(NG). Bottom cell은 반대. 한 row 내에서 top/bottom cell이 BL index 증가에 따라 교대로 나타남.

### 3.2 RowPress 특성 (O7) — Fig. 12a-d

- **Charged state(data=1)에서만 bitflip** 발생 (RowPress 특성 [39]).
- Alternating BER pattern → top/bottom cell의 PG/NG 교대를 정확히 반영.
- Upper/lower aggressor, even/odd WL victim row 변화 시 **pattern이 반전** (6F² reversed-symmetry).

### 3.3 RowHammer 특성 (O8, O9, O10) — Fig. 12e-h

| Observation | 내용 |
|-------------|------|
| **O8** | RowHammer도 alternating pattern. Upper/lower aggressor, even/odd WL, data=0/1에 따라 pattern 반전 |
| **O9** | RowHammer는 **두 gate type 모두**(PG+NG)에서 발생 |
| **O10** | 주어진 victim cell은 **한 번에 한 gate type에만** 취약. Written data(0/1) 변경 시 취약 gate type이 반전 |

**이전 연구와의 차이**: Prior work [12][58]는 victim data=1일 때 NG, data=0일 때 PG에서 charge injection으로 설명했으나, RowPress와 RowHammer의 gate type 관계가 반대임이 관측되어 정확한 gate type 확정이 어려움.

### 3.4 Horizontal Data Pattern 의존성 (O11, O12) — Fig. 14, 15

**Observation-11 (Victim horizontal 영향)**: 특정 victim cell Vic₀에 대해, horizontal adjacent victim cell Vic₋₂,₋₁,₁,₂가 모두 반대 값일 때 BER 최대화. **Vic₋₂,₂ (distance-2)가 Vic₋₁,₁ (distance-1)보다 더 큰 영향** — 최대 1.54× vs 1.12×. 6F² 구조상 물리적 거리 차이가 2배보다 작기 때문.

**Observation-12 (Aggressor horizontal 영향)**: Aggr₋₂,₋₁,₁,₂도 RowHammer에 영향. Aggressor는 **가까울수록 영향이 큼** (victim과 반대 경향). Aggr₀ 값 변경 시 BER 0.58×~0.72× 감소.

### 3.5 Adversarial Data Patterns (O13, O14)

**Observation-13 — Hcnt 감소 공격** (Fig. 15):
- Vic₋₂,₋₁,₁,₂ + Aggr₋₂,₋₁,₀,₁,₂를 모두 Vic₀의 반대 값으로 설정.
- Hcnt (첫 bitflip까지 activation 횟수)를 baseline 대비 **최대 0.81×로 감소** (81%).
- Distance-2 cell이 distance-1보다 Hcnt 감소 효과 큼 (O11과 일관).

**Observation-14 — BER 증폭 공격** (Fig. 16, 17):
- 256개 4-bit repeating pattern 조합 평가.
- Worst case: Victim=0x33, Aggressor=0xCC → baseline(0xFF/0x00) 대비 **1.69× BER 증가**.
- 수직 방향 반대 값 + 2-bit repeating pattern이 1-bit alternating보다 악성 (O11에 부합).
- 기존 Pinpoint RowHammer [22], RAMBleed [30]는 **row-wise(vertical) data pattern만** 고려 → column-wise(horizontal) 영향 무시.

---

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1 Coupled-Row Activation이 초래하는 위협

- **MC-side row tracking 우회**: Attacker가 coupled-row pair에 activation을 분산시키면 counter-based mitigation이 두 개의 다른 row로 오인.
- **Row swapping 방어 무력화**: Randomized Row-Swap [60][75]은 row-A만 relocate → row-B(coupled)는 그대로 victim.
- **Memory massaging/templating 성공률 증가**: Attacker가 두 row를 동시에 점유 가능 → adjacency 보장 확률 상승.

### 4.2 제안 방어

**Coupled-row 대응**:
- MC가 coupled-row 관계(예: (n, n+64K))를 인지하고 activation tracking에 반영.
- DDR5 DRFM(Directed Refresh Management) [20] + Mode Register/SPD에 coupled-row 정보 공개 시 MC가 효율적 tracking 가능.
- 궁극적으로 in-DRAM mitigation이 더 적합 (제조사별 상이한 coupled-row 관계).

**Adversarial data pattern 대응**:
- **Data scrambling 강화**: 기존 Intel/AMD의 MC-side memory scrambling을 row+column address 모두를 PRNG seed로 활용하도록 확장 → cold boot attack 방어 [83]과 유사한 원리.
- **ECC 알고리즘 개선**: Data pattern-aware ECC/coding theory 접근.

### 4.3 Side-Channel 및 PIM 영향

- Edge subarray / coupled-row activation은 DRAM power consumption을 2배로 증가 → **power-based side-channel** 분석 가능성 [2].
- RowCopy와 coupled-row activation이 결합되면 의도치 않은 row에 data copy → PIM 기법의 confidentiality 위협.

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]


## 전체 요약

[[../paper-summaries/2024ISCA-summarize/dramscope-uncovering-dram-microarchitecture-and-characteristics-by-issuing-memory-commands.md|전체 요약 보기]]
