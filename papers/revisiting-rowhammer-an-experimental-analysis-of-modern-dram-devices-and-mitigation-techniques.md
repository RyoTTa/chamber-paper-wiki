---
tags: [paper, 2020, 2020ISCA, topic/dram, topic/rowhammer]
venue: "2020 ACM/IEEE 47th Annual International Symposium on Computer Architecture (ISCA 2020)"
year: 2020
summary_path: "../paper-summaries/2020ISCA-summarize/revisiting-rowhammer-an-experimental-analysis-of-modern-dram-devices-and-mitigation-techniques.md"
---

# Revisiting RowHammer: An Experimental Analysis of Modern DRAM Devices and Mitigation Techniques

**Venue:** 2020 ACM/IEEE 47th Annual International Symposium on Computer Architecture (ISCA 2020)
**저자:** Jeremie S. Kim, Minesh Patel, A. Giray Yaglikci, Hasan Hassan, Roknoddin Azizi, Lois Orosa, Onur Mutlu (ETH Zurich, Carnegie Mellon University)

## 개요

- RowHammer는 DRAM 회로 수준의 취약점으로, 특정 행(row)을 반복적으로 활성화하면 인접 행의 데이터 비트가 뒤집히는 현상. 2014년 첫 보고 이후 DRAM 밀도 스케일링이 진행될수록 점점 더 심각해지고 있음.
- DRAM 제조사는 주로 밀도 스케일링을 통해 용량을 늘리는데, 이 과정에서 셀 간 간격이 줄어들어 RowHammer 취약성이 악화됨. 최신 DRAM 칩일수록 더 적은 활성화 횟수로 비트 플립이 발생.
- 기존 RowHammer 완화 메커니즘(refresh rate 증가, Probabilistic Adjacent Row Activation, counter 기반 접근 등)이 향후 더 취약해질 DRAM 칩에서 여전히 유효한지 불분명.
- 현대 DRAM 칩의 RowHammer 특성을 체계적으로 실험 분석한 연구가 부족하며, 기술 노드별/제조사별 취약성 차이를 정량화한 연구 필요.
- 최악의 RowHammer 조건에서 DDR3, DDR4, LPDDR4 칩의 체계적 특성 분석을 통해 미래 DRAM의 RowHammer 취약성을 예측하고 완화 메커니즘의 확장성을 평가하는 것이 본 논문의 목표.

## 방법론

### 3.1. 실험 인프라스트럭처

- **SoftMC 프레임워크**: DDR3/DDR4 칩 테스트용 FPGA 기반 인프라. Xilinx Virtex UltraScale 95 FPGA, DDR4 SODIMM 슬롯 2개, PCIe 인터페이스 사용. 온도 제어용 실리콘 고무 히터와 열전대 적용.
- **LPDDR4 테스트 인프라**: 업계 개발 하드웨어 기반, 패키지 온 패키지 LPDDR4 칩 지원. 정밀 온도 제어 기능 탑재.
- **물리적 주소 매핑 역공학**: DRAM 내부 논리-물리 주소 매핑을 역공학하여 최악의 RowHammer 테스트 조건(양쪽 물리적 인접 행 동시 활성화)을 정확히 수행.
- **온도 고정**: 모든 실험을 50°C 환경 온도에서 수행하여 온도 변수 통제.

### 3.2. 테스트 패러미터

- **Hammer Count (HC)**: 2K~150K 범위에서 양자화. 각 쌍의 활성화를 1회 hammer로 카운트.
- **데이터 패턴**: Solid0 (0x00), Solid1 (0xFF), Col-stripe0 (0x55), Col-stripe1 (0xAA), Checkered0/1, Rowstripe0/1 등 6가지 패턴 테스트.
- **간섭 요소 제거**: refresh, TRR, pTRR, ECC 등 모든 DRAM 수준/시스템 수준 완화 메커니즘 비활성화. 코어 루프는 32ms 이내 완료하여 retention failure와의 혼동 방지.

### 3.3. 알고리즘 구조

```
Algorithm 1: DRAM RowHammer Characterization
1: foreach DataPattern in [6 patterns]:
2:   write DataPattern into all cells
3:   foreach row in DRAM:
4:     set victim_row = row
5:     set aggressor_row1 = victim_row - 1
6:     set aggressor_row2 = victim_row + 1
7:     foreach HC in [HC sweep]:
8:       Disable DRAM refresh
9:       Refresh victim_row
10:      for n = 1 → HC:
11:        activate aggressor_row1
12:        activate aggressor_row2
13:      Enable DRAM refresh
14:      Record RowHammer bit flips
15:      Restore bit flips to original values
```

## 핵심 기여

- **1580개 실칩 실험을 통해 최신 DRAM 칩이 기술 스케일링과 함께 RowHammer에 훨씬 더 취약해짐을 최초로 체계적으로 증명**: DDR3 69.2K→LPDDR4-1y 4.8K로 HCfirst 대폭 감소.
- **기존 완화 메커니즘은 현재 칩에서는 합리적 오버헤드이나, 미래 칩에서는 확장 불가**: PARA는 HCfirst=128에서 80% 성능 손실.
- **이상적 refresh 기반 메커니즘에 상당한 개선 여지 존재**: HCfirst=128에서도 93.53% 성능 유지하나, 매우 낮은 HCfirst에서는 성능 저하 시작.
- **두 가지 유망한 미래 연구 방향 제시**: (1) DRAM-시스템 협력적 접근, (2) 프로파일 기반 메커니즘 (취약 셀/영역 사전 탐지).
- **DRAM 기술 노드가 1z/1a 노드로 진화할수록 RowHammer 문제는 더욱 심각해질 것이며, 근본적인 회로 수준 해결책이나 새로운 아키텍처적 접근이 필요**.

## 주요 결과

### 4.1. 기술 스케일링에 따른 취약성 변화

- **DDR3**: DDR3-old에서 DDR3-new로 HCfirst가 69.2K→22.4K로 감소(제조사 기준 최솟값). 제조사 B, C의 DDR3-new 칩에서 RowHammer 비트 플립이 크게 증가.
- **DDR4**: DDR4-old(17.5K)→DDR4-new(10K)로 HCfirst 감소. 모든 제조사에서 동일한 트렌드 관찰.
- **LPDDR4**: LPDDR4-1x(16.8K)→LPDDR4-1y(4.8K)로 HCfirst 대폭 감소. 최소 4800회 활성화만으로도 첫 비트 플립 발생(LPD4-1y, 제조사 A).
- **핵심 관찰**: DRAM 기술 노드가 작아질수록 셀 용량 감소와 밀도 증가가 결합되어 cell-to-cell 간섭이 증가하고, 결과적으로 RowHammer 취약성이 크게 악화됨.

### 4.2. 데이터 패턴 의존성

- **Observation 2**: 어떤 단일 데이터 패턴도 전체 RowHammer 비트 플립을 완전히 포착하지 못함. 여러 패턴 조합 필수.
- **Observation 3**: 최악 데이터 패턴은 동일 제조사/DRAM 유형-노드 구성 내에서 일관적. 예: DDR4-new에서 제조사 A/B는 RowStripe0, 제조사 C는 Checkered1이 최악 패턴.
- LPDDR4 칩에서는 on-die ECC로 인해 단일 비트 에러가 숨겨져 데이터 패턴 효과 해석이 더 복잡해짐.

### 4.3. 공간적 분포 특성

- **Observation 6**: 최신 기술 노드 칩에서는 더 많은 행과 더 먼 거리에서 RowHammer 비트 플립 발생. LPDDR4-1y에서는 victim row로부터 6행 떨어진 곳까지 비트 플립 관찰.
- **Observation 7**: victim row에서 멀어질수록 비트 플립 수 감소 (cell-to-cell 간섭 거리 감쇠).
- **Observation 8**: 64비트 워드당 최대 4개의 비트 플립 발생 가능. 단일 오류 정정 ECC(SEC-DEC)로는 보호 불충분.

### 4.4. ECC 효과 분석

- **Observation 12**: 단일 오류 정정 ECC는 DDR4-old/new에서 HCfirst를 최대 2.78× 향상시킴.
- **Observation 13**: 이중→삼중 오류 정정 ECC 전환 시 DDR4에서 수율 감소 효과, DDR3-new에서는 추가 개선 지속.
- LPDDR4 칩의 on-die ECC(128비트 SEC)로 인해 시스템 수준 ECC 분석에서 제외.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]


## 전체 요약

[[../paper-summaries/2020ISCA-summarize/revisiting-rowhammer-an-experimental-analysis-of-modern-dram-devices-and-mitigation-techniques.md|전체 요약 보기]]
