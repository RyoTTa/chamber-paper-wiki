---
tags: [paper, 2024, 2024ISCA, topic/dram, topic/rowhammer]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO 2021)"
year: 2024
summary_path: "../paper-summaries/2024ISCA-summarize/a-deeper-look-into-rowhammer-sensitivities-experimental-analysis.md"
---

# A Deeper Look into RowHammer's Sensitivities: Experimental Analysis of Real DRAM Chips and Implications on Future Attacks and Defenses

**Venue:** IEEE/ACM International Symposium on Microarchitecture (MICRO 2021)
**저자:** Lois Orosa, A. Giray Yaglikci, Haocong Luo, Ataberk Olgun, Jisung Park, Hasan Hassan, Minesh Patel, Jeremie S. Kim, Onur Mutlu (ETH Zurich)

## 개요

- DRAM 셀 밀도와 셀 간 간격이 축소되면서 RowHammer 취약성이 악화되고 있으며, 공격에 필요한 최소 hammer count(Activation 수)가 지난 10년간 10배 이상 감소함 (2014년 DDR3 139K → 2020년 LPDDR4 9.6K)
- RowHammer는 공격 행(aggressor row)을 반복 활성화하여 인접 행(victim row)의 비트 플립을 유발하는 회로 수준 DRAM 취약성으로, privilege escalation, 데이터 유출, denial of service 등 심각한 보안 위협으로 악용 가능
- 기존 RowHammer 방어 메커니즘(TRR, RFM 등)은 새 DRAM 세대에서 점점 더 비용이 높아지며, 효과적이고 효율적인 방어를 위해 온도, aggressor row 활성 시간, 물리적 위치 등 근본 특성에 대한 정밀 실험적 분석이 필요
- 본 논문은 **248개 DDR4** 및 **24개 DDR3** DRAM 칩을 4개 주요 제조사(A, B, C, D)에서 실험하여, 기존에 엄밀하게 연구되지 않은 3가지 속성(온도, aggressor row 활성 시간, victim 셀의 물리적 위치)의 RowHammer 취약성 영향을 최초로 체계적으로 분석

## 방법론

### 3.1. 테스트 인프라 (SoftMC)
- **SoftMC FPGA 기반 테스트 플랫폼:** Xilinx Alveo U200(DDR4 DIMM용) 및 ML605(DDR3 SODIMM용) FPGA 보드 사용
- DDR3/DDR4 커맨드 타이밍을 각각 **2.50ns, 1.25ns** 정밀도로 제어 가능
- PCIe 연결로 호스트 머신과 통신하여 RowHammer 테스트 및 모니터링 수행

### 3.2. 온도 제어 시스템
- 실리콘 러버 히터를 DRAM 모듈 양면에 부착하여 온도 조절
- Maxwell FT200 온도 컨트롤러로 **±0.1°C 오차** 범위 내에서 50°C~90°C 범위를 5°C 단위로 정밀 제어
- 열전대(thermocouple)로 DRAM 칩 표면 온도 측정 (내부 온도와 강한 상관관계)

### 3.3. 테스트 방법론
- **Double-sided RowHammer** 공격 사용: victim row의 양쪽 물리적 인접 행을 교대로 활성화
- DRAM 리프레시, TRR 등 간섭 소스를 모두 비활성화하여 회로 수준 비트 플립 직접 관찰
- **WCDP(Worst-Case Data Pattern)** 탐지: 7개 패턴(colstripe, checkered, rowstripe, random 및 보복) 중 최악 패턴 사용
- 메트릭: **HCfirst** (최초 비트 에러 관찰 시 최소 hammer count), **BER** (비트 에러율, 행당 비트 플립 수)
- HCfirst는 이진 탐색으로 Δ=512 정밀도까지 측정

### 3.4. 테스트 대상 DRAM 칩
| 제조사 | DDR4 DIMM 수 | DDR3 SODIMM 수 | DDR4 칩 수 | DDR3 칩 수 | 밀도 | 조직 |
|--------|-------------|---------------|-----------|-----------|------|------|
| Mfr. A | 9 | 1 | 144 | 8 | 8Gb (4Gb) | x4 (x8) |
| Mfr. B | 4 | 1 | 32 | 8 | 4Gb (4Gb) | x8 (x8) |
| Mfr. C | 5 | 1 | 40 | 8 | 4Gb (4Gb) | x8 (x8) |
| Mfr. D | 4 | - | 32 | - | 8Gb | x8 |

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1. DRAM 셀 수준 온도 영향

- **관찰 1 (Obsv. 1):** 모든 vulnerable DRAM 셀은 고유한 연속 온도 범위 내에서만 RowHammer 비트 플립이 발생. 해당 셀의 취약 온도 범위 내 모든 온도점에서 비트 플립이 발생할 확률이 매우 높음 (Mfr. A: 99.1%, Mfr. B: 98.9%, Mfr. C: 98.0%, Mfr. D: 99.2%)
- **관찰 2 (Obsv. 2):** 상당 비율의 셀이 테스트한 전체 온도 범위(50°C~90°C)에서 모두 취약 (제조사별 9.6%~29.8%)
- **관찰 3 (Obsv. 3):** 일부 셀은 **매우 좁은 온도 범위(최소 5°C)** 내에서만 취약. 예: Mfr. A의 vulnerable 셀 중 0.4%가 70°C 단일 온도에서만 비트 플립 발생. 2.3%/1.8%/2.4%/1.6%의 셀이 5°C 이하 범위에서만 취약

### 4.2. DRAM 행 수준 온도 영향

- **BER 분석:** 온도 증가에 따라 BER가 변화하는 경향은 제조사에 따라 다름
  - Mfr. A, C, D: 온도 상승 시 BER 증가 (Mfr. A: 50→90°C에서 BER 50%↑ 이상)
  - Mfr. B: 온도 상승 시 BER 감소 (-20% 수준)
- **HCfirst 분석 (Obsv. 5~7):**
  - **Obsv. 5:** 온도 증가 시 행에 따라 HCfirst가 증가하거나 감소할 수 있음 (Mfr. A의 경우 50→55°C에서 65% 행은 HCfirst 증가, 35%는 감소)
  - **Obsv. 6:** 온도 변화폭이 커질수록 HCfirst가 전반적으로 감소하는 경향 (Mfr. D: 50→55°C에서 63% 행이 HCfirst↑ vs. 50→90°C에서 40% 행만 HCfirst↑)
  - **Obsv. 7:** 온도 변화폭이 클수록 HCfirst 변화 크기가 커짐. 누적 변화량이 50→90°C에서 50→55°C 대비 **3.8x~4.3x** 증가 (제조사별)

### 4.3. 회로 수준 정당화
- DRAM charge trap 모델에 따니 HCfirst는 온도 증가 시 감소하다가 **온도 변환점(inflection point)** 이후 증가하는 비단조(non-monotonic) 특성
- 각 셀의 변환점이 다양하여, DRAM 칩의 평균 변환점에 따라 온도-취약성 관계가 결정됨

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]


## 전체 요약

[[../paper-summaries/2024ISCA-summarize/a-deeper-look-into-rowhammer-sensitivities-experimental-analysis.md|전체 요약 보기]]
