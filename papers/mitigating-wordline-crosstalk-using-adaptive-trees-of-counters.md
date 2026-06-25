---
tags: [dram, rowhammer, reliability, crosstalk]
venue: ISCA
year: 2018
summary_path: paper-summaries/2018ISCA-summarize/mitigating-wordline-crosstalk-using-adaptive-trees-of-counters.md
---

# Mitigating Wordline Crosstalk Using Adaptive Trees of Counters

## 개요

CAT(Counter-based Adaptive Tree)는 DRAM의 wordline crosstalk을 완화하기 위해 메모리 접근 패턴에 따라 카운터 분포를 동적으로 조정하는 기법입니다.

## 방법론

- **적응형 카운터 트리**: 메모리 행을 그룹으로 분할하고 각 그룹에 카운터를 동적 배정
- **분할 임계값(Split Threshold)**: 핫 행은 작은 그룹으로 정밀 관리, 콜드 행은 큰 그룹으로 관리
- **PRCAT**: 주기적(64ms) 트리 재구성
- **DRCAT**: 2비트 가중치 레지스터로 카운터 사용 빈도 추적, 콜드→핫 카운터 재배정

## 핵심 기여

1. DRAM 접근 지역성을 활용한 적은 수의 온칩 카운터로 효과적 crosstalk 완화
2. 확률적 기반 대비 더 정확한 행 탐지, deterministic 기반 대비 적은 카운터
3. Row Hammering 공격과 자연 발생적 crosstalk 모두 대응

## 주요 결과

- 갱신 전력 오버헤드: SCA 21%, Probabilistic 18% → **CAT 7%**
- 성능 오버헤드: ~0.5%
- 하드웨어 합성: 최소 면적 오버헤드로 온칩 구현 가능

## 한계점

- 분할 임계값 선택이 성능에 민감 (모델 기반 최적화 필요)
- DRAM 공정 변화에 따른 추가 검증 필요
- DDR4 TRR과의 상세한 통합 검증 미흡

## 관련 concept

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]
