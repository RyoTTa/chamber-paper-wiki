---
tags: [paper, 2021, 2021HPCA, topic/dram, topic/rowhammer]
venue: "2021 IEEE International Symposium on High-Performance Computer Architecture (HPCA '21)"
year: 2021
summary_path: "../paper-summaries/2021HPCA-summarize/blockhammer-preventing-rowhammer-at-low-cost.md"
---

# BlockHammer: Preventing RowHammer at Low Cost by Blacklisting Rapidly-Accessed DRAM Rows

**Venue:** 2021 IEEE International Symposium on High-Performance Computer Architecture (HPCA '21)
**저자:** A. Giray Yağlıkçı (ETH Zürich), Minesh Patel (ETH Zürich), Jeremie S. Kim (ETH Zürich), Roknoddin Azizi (ETH Zürich), Ataberk Olgun (ETH Zürich), Lois Orosa (ETH Zürich), Hasan Hassan (ETH Zürich), Jisung Park (ETH Zürich), Konstantinos Kanellopoulos (ETH Zürich), Taha Shahroodi (ETH Zürich), Saugata Ghose (University of Illinois at Urbana–Champaign), Onur Mutlu (ETH Zürich)

## 개요

- 공정 기술 스케일링으로 인해 현대 DRAM 칩의 셀 밀도가 증가하면서 **RowHammer** 취약성이 악화: 2014년 대비 2020년에 비트플립을 유발하는 데 필요한 행 활성화 수가 **10배 이상 감소** (139.2K → 9.6K)
- RowHammer는 공격자 행(aggressor row)을 반복 활성화하면 인접 피해 행(victim row)에서 비트플립이 발생하는 현상으로, 프라이버시 침해 및 권한 상승 공격에 악용 가능
- DDR4/LPDDR4 칩에서도 RowHammer 취약성이 확인되며, TRRespass 연구에 의해 기존 DRAM 내부 완화 메커니즘(TRR)을 우회하는 것이 입증
- 기존 완화 메커니즘의 두 가지 핵심 과제:
  - **Challenge 1: 확장성 부족** - RowHammer 취약성이 심화될수록 성능/에너지/면적 오버헤드가 급격히 증가
  - **Challenge 2: 상용 DRAM 호환성 부족** - 물리적 격리 및 반응형 리프레시 메커니즘이 DRAM 내부 행 주소 매핑이라는 독점 정보를 필요로 하거나 DRAM 칩 수정이 필요
- 물리적 격리 메커니즘은 메모리 용량 손실 증가, 반응형 리프레시는 성능 오버헤드 급증, 기존 선제적 쓰로틀링은 모든 행에 대한 카운터가 필요하여 면적 비용 과다

## 방법론

### 3.1. RowBlocker (행 차단기)

- **목적**: 공격자가 특정 행을 RowHammer 임계값 이상으로 활성화하는 것을 원천 차단
- 두 가지 하위 구성 요소로 구성:

#### 3.1.1. RowBlocker-BL (블랙리스트 관리)

- **Dual Counting Bloom Filter (D-CBF)**: 두 개의 Counting Bloom Filter를 시간 교차 방식으로 사용하여 행 활성화율 추적
  - 각 CBF는 1024개의 12비트 포화 카운터로 구성
  - 4개의 H3 클래스 해시 함수 사용 (비트 시프트 및 마스크 연산으로 구현)
  - 블랙리스트 임계값(N_BL): RowHammer 임계값의 약 1/4 (32K 기준 8K)
  - D-CBF 동작: 모든 행 활성화 시 두 CBF에 동시에 삽입, 활성 CBF가 블랙리스트 결정, 에포크 종료 시 활성/수동 교대 및 클리어
  - **False-negative-free**: Bloom 필터의 특성상 삽입된 요소에 대해 항상 true 반환 (오탐 가능, 미탐 불가)
  - 해시 함수 시드 값 변경으로 오탐으로 인한 특정 행의 반복적 블랙리스트 방지

#### 3.1.2. RowBlocker-HB (활성화 이력 버퍼)

- **FIFO 기반 이력 버퍼**: 최근 t_Delay 시간 윈도우 내의 모든 행 활성화 기록 저장
- 각 행 활성화 시 해당 행 주소, 타임스탬프, 유효 비트를 버퍼에 삽입
- **내용 주소 지정 메모리(CAM)** 배열로 행 주소 병렬 검색 지원
- 블랙리스트된 행이 최근 활성화되었으면 새로운 활성화 차단 (t_Delay 시간 경과 후 허용)
- 크기: 16뱅크 DDR4 랭크당 887개 엔트리

#### 3.1.3. 지연 시간 계산 (t_Delay)

- RowHammer 안전 활성화율 보장을 위한 수학적 공식:
  - t_Delay = (t_CBF – (N_BL × t_RC)) / ((t_CBF/t_REFW) × N_RH – N_BL)
  - t_CBF: CBF 수명 (64ms = t_REFW)
  - N_BL: 블랙리스트 임계값 (8K)
  - N_RH: RowHammer 임계값 (32K)
  - t_RC: ACT-to-ACT 지연 시간 (46.25ns)
  - t_REFW: 리프레시 윈도우 (64ms)
  - 이론적 최대 지연: 7.7µs, 실제 양성 워크로드에서는 P50=1.7µs, P90=3.9µs

### 3.2. AttackThrottler (공격 쓰로틀러)

- **목적**: RowHammer 공격이 양성 애플리케이션에 미치는 성능 영향을 완화
- **RowHammer Likelihood Index (RHLI)**: 각 <스레드, 뱅크> 쌍의 공격 가능성 정량화
  - RHLI = 블랙리스트된 행 활성화 횟수 / ((N_RH × t_CBF/t_REFW) – N_BL)
  - 0: 공격 아님, 1에 가까울수록 공격 가능성 높음
- **대역폭 제한**: RHLI에 반비례하여 인플라이트 메모리 요청 할당량 적용
  - RHLI가 높을수록 할당량 감소 → 공격 스레드의 메모리 대역폭 점유율 감소
  - 양성 스레드는 RHLI=0으로 쓰로틀링 없음
- **구현**: 각 <스레드, 뱅크> 쌍당 2개의 카운터 (시간 교차 방식), 총 512바이트 (8스레드, 16뱅크 기준)

### 3.3. 다방향 RowHammer 공격 대응

- **blast radius (r_blast)**: 공격자의 영향이 도달하는 최대 물리적 거리 (현대 DRAM에서 6행)
- **blast impact factor (c_k)**: 거리 k만큼 떨어진 행에 대한 공격 영향 비율 (c_k = 0.5^(k-1))
- N_RH' = N_RH / (2 × Σ(k=1 to r_blast) c_k)으로 수정하여 누적 효과 보정
- 이중 공격(double-sided) 모델: N_RH' = N_RH/2 (r_blast = c_k = 1)

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

- **반박을 통한 증명**: BlockHammer를 우회하는 메모리 접근 패턴이 존재하지 않음을 수학적으로 증명
- 5가지 에포크 유형(T0-T4)으로 모든 가능한 행 활성화 패턴을 분류
- 제약 조건 분석을 통해 N_RH 이상의 활성화가 불가능함을 입증
- **포괄적 위협 모델**: 공격자가 메모리 대역폭을 완전 활용, 각 요청을 정밀 타이밍, BlockHammer/DRAM 구현 세부 사항을 정확히 알고 있는 경우에서도 안전 보장

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]


## 전체 요약

[[../paper-summaries/2021HPCA-summarize/blockhammer-preventing-rowhammer-at-low-cost.md|전체 요약 보기]]
