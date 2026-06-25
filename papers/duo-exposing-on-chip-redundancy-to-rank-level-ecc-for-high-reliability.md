---
tags: [paper, 2018, 2018HPCA, topic/dram]
venue: "HPCA 2018"
year: 2018
summary_path: "../paper-summaries/2018HPCA-summarize/duo-exposing-on-chip-redundancy-to-rank-level-ecc-for-high-reliability.md"
---

# DUO: Exposing On-chip Redundancy to Rank-Level ECC for High Reliability

**Venue:** HPCA 2018
**저자:** Seong-Lyong Gong (UT Austin), Jungrae Kim (Microsoft), Sangkug Lym (UT Austin), Michael Sullivan (NVIDIA), Howard David (Huawei), Mattan Erez (UT Austin)

## 개요

DRAM 기술의 지속적인 스케일링으로 인해 고유 결함(inherent faults) 발생률이 증가하고 있으며, 기존 row/column sparing 기술로는 예상되는 높은 고유 결함률을 효율적으로 처리할 수 없습니다. In-DRAM ECC(IECC)는 스케일링 에러를 해결할 수 있지만, 높은 신뢰성이 요구되는 시스템에서 rank-level ECC(RECC)와 결합 시 비효율이 발생합니다.

DUO(Dual Use of On-chip Redundancy)는 IECC 모듈을 우회하여 온칩 중복성을 RECC에 직접 전달하는 메커니즘으로, IECC의 비효율성을 해결하면서 높은 신뢰성을 달성합니다.

## 방법론

### IECC 우회 모드
- 기존 IECC 모듈을 우회하여 온칩 중복성을 메모리 채널을 통해 직접 전달
- IECC의 인코딩/디코딩, 오버페치, read-modify-write 오버헤드 방지
- 현재 DRAM 설계에 대한 significant 변경 없이 구현 가능

### DUO SDDC 설계
- 긴 코드워드를 통한 근본적으로 높은 검출 및 정정 능력
- 여러 가지 2차 정정 기법 통합으로 정정 능력 추가 확장
- 다양한 결함 오류 모델에서의 높은 신뢰성 검증

### 다양한 DRAM 구성 지원
- 낮은 신뢰성 시스템(非ECC DIMM) 지원
- 높은 신뢰성 시스템 지원
- DDR5와 같은 향후 인터페이스에서의 좁은 rank 구성 지원

## 핵심 기여

1. IECC의 비효율성을 해결하면서 높은 신뢰성을 달성하는 DUO 메커니즘 제안
2. 온칩 중복성의 이중 활용으로 성능, 에너지 효율, 신뢰성 동시에 향상
3. 향후 DRAM 스케일링에 대비한 강건한 ECC 솔루션 제시

## 주요 결과

- **성능**: IECC 대비 평균 2-3% 성능 저하 수준 (동등하거나 더 나은 성능)
- **에너지**: IECC 대비 평균 4-14% 낮은 DRAM 에너지 소비
- **신뢰성**: IECC 또는 최신 ECC 기법보다 높은 신뢰성 제공

## 한계점

- 상업용 DRAM 칩에서의 온칩 중복성 포함 가정으로 인한 일반화 제한
- 다양한 DRAM 구성에서의 추가 검증 필요
- 실제 상용 시스템에서의 실증 평가 필요

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]

## 관련 논문

- [paper-summaries/2018HPCA-summarize/duo-exposing-on-chip-redundancy-to-rank-level-ecc-for-high-reliability.md]