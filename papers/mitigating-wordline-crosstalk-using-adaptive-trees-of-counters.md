---
tags: [paper, 2018, 2018ISCA, topic/dram, topic/rowhammer]
venue: "International Symposium on Computer Architecture (ISCA) 2018"
year: 2018
summary_path: "../paper-summaries/2018ISCA-summarize/mitigating-wordline-crosstalk-using-adaptive-trees-of-counters.md"
---

# Mitigating Wordline Crosstalk Using Adaptive Trees of Counters

**Venue:** International Symposium on Computer Architecture (ISCA) 2018
**저자:** Seyed Mohammad Seyedzadeh (University of Pittsburgh), Alex K. Jones (University of Pittsburgh), Rami Melhem (University of Pittsburgh)

## 개요

- DRAM 기술 축척이 셀 신뢰성을 저하시키는 부작용으로 인접 셀 간의 결합(crosstalk)이 증가
- 높은 접근 빈도의 행(row)이 인접 행의 데이터 손실을 유발할 수 있음 (wordline crosstalk)
- **Row Hammering**: 악의적으로 특정 행을 반복 접근하여 인접 셀의 충전 상태를 변경하는 공격
- 자연 발생적(inadvertent) Row Hammering도 비\application 접근 패턴의 불균형으로 인해 발생 가능
- 기존 완화 기술의 한계:
  - 전체 행의 갱신 빈도를 높이는 방법: 불필요하게 높은 전력/성능 오버헤드
  - 확률적 접근(Probabilistic): RNG 기반 → 쓸모없는 갱신 발생, hot row 탐지 부정확
  - Deterministic (SCA): 행당 카운터 1개 배정 → 막대한 면적/전력 오버헤드
  - DRAM의 접근 지역성(access locality)으로 인해 많은 카운터가 저utilization

## 방법론

### 3.1. 트리 구조 및 동작 원리
- 메모리 행을 그룹으로 분할하고 각 그룹에 카운터를 배정
- M개의 카운터로 최대 L레벨까지 동적으로 트리 성장
- 리프 노드가 하나의 그룹을 관리하며, 각 그룹은 특정 수의 행을 담당
- refresh threshold T에 도달하면 해당 그룹의 모든 행을 갱신

### 3.2. 분할 임계값(Split Threshold) 결정 모델
- 분할 임계값 T₁, T₂, ...의 값이 트리 형태를 결정
- 균형 트리(uniform) vs 비균형 트리(non-uniform) 간의 최적화
- 예시: 4카운터 예제에서 x > 3w일 때 비균형 트리가 더 적은 갱신 필요
- 일반화된 모델로 M=64 카운터, L=10 레벨에 대한 최적 임계값 계산

### 3.3. PRCAT (Periodically Reset CAT)
- 자동 갱신 간격(64ms)마다 트리를 재구성
- 장점: 구조가 간단하고 정확한 접근 추적 가능
- 단점: 접근 패턴 변화가 없을 때도 불필요한 재구성 발생

### 3.4. DRCAT (Dynamically Reconfigured CAT)
- 2비트 가중치(weight) 레지스터로 각 카운터의 사용 빈도 추적
- 핫 영역의 카운터가 최대 가중치에 도달하면 → 콜드 영역의 카운터 2개를 병합하여 해제
- 해제된 카운터로 핫 영역을 재분할(split)
- PRCAT의 두 가지 단점을 소규모 추가 비용으로 해결

### 3.5. 하드웨어 구현
- 포인터 추적(pointer chasing) 기반 데이터 구조
- 중간 노드 배열과 리프 노드 테이블로 트리 표현
- 가중치 레지스터 배열로 재구성 정보 관리

## 핵심 기여

- CAT는 DRAM의 접근 지역성을 활용하여 적은 수의 온칩 카운터로 효과적인 crosstalk 완화 달성
- 갱신 전력 오버헤드를 7%로 감소 (기존 18~21% 대비)
- 성능 오버헤드 0.5%로 미미
- Row Hammering 공격과 자연 발생적 crosstalk 모두에 대응 가능
- 하드웨어 구현이 실용적인 면적 오버헤드로 가능

## 주요 결과

- 온칩 카운터 수: M=64개 기준 실험
- 하드웨어 합성 평가: 최소 면적 오버헤드
- 메모리 컨트롤러에 CAT 로직 통합
- DDR4 TRR 메커니즘과 호환 가능

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]


## 전체 요약

[[../paper-summaries/2018ISCA-summarize/mitigating-wordline-crosstalk-using-adaptive-trees-of-counters.md|전체 요약 보기]]
