---
tags: [paper, 2025, 2025MICRO, topic/dram, topic/rowhammer]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO) 2025"
year: 2025
summary_path: "../paper-summaries/2025MICRO-summarize/columndisturb-column-based-read-disturbance-in-real-dram.md"
---

# ColumnDisturb: Understanding Column-based Read Disturbance in Real DRAM Chips and Implications for Future Systems

**Venue:** IEEE/ACM International Symposium on Microarchitecture (MICRO) 2025
**저자:** Ismail Emir Yuksel, Ataberk Olgun, Nisa Bostanci, Haocong Luo, Abdullah Giray Yaglikci, Onur Mutlu (ETH Zurich, CISPA Saarbrücken)

## 개요

- DRAM 기술 노드 축소로 셀 간격이 줄어들면서 read disturbance 문제가 심화되고 있음
- RowHammer와 RowPress는 알려진 대표적 read disturbance 현상이지만, 단일 subarray 내의 인접 행에만 영향
- DRAM 리프레시 메커니즘은 리텐션 실패를 방지하기 위해 정기적으로 셀 충전을 복원하지만, 새로운 read disturbance 현상이 기존 리프레시 가정을 흔들 수 있음
- 216개 DDR4 및 4개 HBM2 DRAM 칩에서의 광범위한 실험을 통해 **ColumnDisturb**라는 새로운 widespread read disturbance 현상 최초 발견

## 방법론

### 3.1. 보급 및 스케일링 특성 (Observation 1-3)

- **모든 216개 DDR4 칩에서 ColumnDisturb 취약성 확인** (3대 제조사 모두)
- 최신 기술 노드일수록 ColumnDisturb 취약성이 악화:
  - SK Hynix: 8Gb A→D-die에서 최소 비트플립 유도 시간 **5.06배** 감소
  - Micron: 16Gb B→F-die에서 **2.98배** 감소
  - Samsung: 16Gb A→C-die에서 **2.50배** 감소
- **기존 DDR4 리프레시 윈도우(63.6ms) 내에서 이미 비트플립 발생** 확인 (Micron 16Gb F-die 모듈)

### 3.2. Column 기반 교란 메커니즘 (Observation 4-6)

- ColumnDisturb은 **3개 연속 subarray의 모든 행(3072행)에 비트플립 유도**
- RowHammer/RowPress는 aggressor 행의 +/-1 이웃 행에만 비트플립 유도
- aggressor subarray에서 **1.45배** 더 많은 비트플립 발생 (인접 subarray는 절반의 비트라인만 공유)
- 리프레시 윈도우 16초 기준, ColumnDisturb은 aggressor subarray에서 평균 2942.68 비트플립/행 유도 (리텐션 실패 대비 **7.07배**)

### 3.3. 비트플립 방향 및 데이터 패턴 (Observation 7-10)

- ColumnDisturb은 **1→0 비트플립만** 유도 (리텐션 실패와 동일, RowHammer/RowPress와 다름)
- aggressor 데이터 패턴이 all-0일 때 all-1 대비 최대 **11.52배** 더 많은 비트플립 유도
  - 원인: aggressor가 all-0이면 비트라인이 GND(0V), victim 셀이 VDD(1V) → 전압 차이 최대
- all-1 aggressor 패턴에서는 리텐션 실패보다 **2.73배 적은** 비트플립 발생 (전압 차이 0)

### 3.4. aggressor 행 열린 시간 및 전압 레벨 (Observation 11-12)

- tAggOn을 36ns에서 70.2μs로 증가 시 비트플립 최대 **2.45배** 증가
- 평균 비트라인 전압이 낮을수록 ColumnDisturb 취약성 크게 증가
  - VDD→GND로 평균 전압 감소 시 비트플립 최대 **26.31배** 증가 (Micron)
- **핵심 가설**: ColumnDisturb은 access transistor의 subthreshold leakage 또는 capacitor-bitline 간 dielectric leakage를 악화시킴

### 3.5.blast radius 및 리텐션 비교 (Observation 13-14)

- ColumnDisturb은 리텐션 실패보다 **최대 198배 더 많은 행에 비트플립 유도**
- 리프레시 윈도우 512ms, 65°C 기준:
  - SK Hynix: 평균 2행 vs 리텐션 2행
  - Micron: 평균 6행 vs 리텐션 최대 2행
  - Samsung: 평균 **232행** vs 리텐션 2행
- 리프레시 윈도우 증가에 따라 ColumnDisturb 영향 행 수가 크게 증가

### 3.6. HBM2 칩 및 ECC 영향 (Observation 15, 25-27)

- 4개 HBM2 칩에서도 ColumnDisturb 확인 (리텐션 대비 최대 **2.43배** 더 많은 비트플립)
- 기존 SECDED ECC로는 ColumnDisturb 비트플립을 정정/검출 불가능 (8바이트 청크에서 최대 15개 비트플립)
- 낮은 비용의 on-die SEC 코드는 2개 비트플립에서도 **88.5%** 오표정(miscorrection) 발생

## 핵심 기여

- ColumnDisturb는 **최초로 실험적으로 입증된 column-based read disturbance 현상**으로, 3대 DRAM 제조사의 모든 테스트 칩에서 확인
- RowHammer/RowPress와 근본적으로 다름: 수평적(row)이 아닌 수직적(column) 교란으로 **3개 subarray(3072행)에 동시 영향**
- 최신 기술 노드로 갈수록 악화되며, **이미 기존 DDR4 리프레시 윈도우 내에서 비트플립 발생**
- ColumnDisturb은 리텐션 실패보다 훨씬 더 많은 행에 영향을 미쳐, retention-aware refresh 메커니즘의 이득을 크게 저해
- ECC만으로는 ColumnDisturb을 완화하기 어려움 (대용량 패리티 오버헤드 필요)
- DRAM 기술 축소가 지속되면 미래 칩에서 ColumnDisturb 문제가 더욱 심각해질 것으로 예측
- ColumnDisturb에 대한 디바이스 레벨 연구, 새로운 완화 기법, robust한 시스템 설계가 시급

## 주요 결과

- **테스트 인프라**: DRAM Bender (FPGA 기반 DDR4/HBM2 테스트 플랫폼), SoftMC 기반
- **카드**: Xilinx Alveo U200 FPGA 보드
- **온도 제어**: 온도 센서 및 히터 패드로 DRAM 칩 온도 정밀 제어 (45°C~95°C)
- **물리적 행 주소 매핑**: RowClone 연산을 이용한 subarray 경계 역설계
- **테스트 칩**: 28개 모듈의 216개 DDR4 칩 (SK Hynix 64개, Micron 88개, Samsung 64개) + Samsung HBM2 4개

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]


## 전체 요약

[[../paper-summaries/2025MICRO-summarize/columndisturb-column-based-read-disturbance-in-real-dram.md|전체 요약 보기]]
