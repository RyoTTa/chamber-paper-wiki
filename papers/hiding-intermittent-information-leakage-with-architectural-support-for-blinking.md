---
tags: [paper, 2018, 2018ISCA, topic/security]
venue: "ISCA 2018"
year: 2018
summary_path: "../paper-summaries/2018ISCA-summarize/hiding-intermittent-information-leakage-with-architectural-support-for-blinking.md"
---

# Hiding Intermittent Information Leakage with Architectural Support for Blinking

**Venue:** ISCA 2018
**저자:** Alric Althoff, Joseph McMahan, Luis Vega, Scott Davidson, Timothy Sherwood, Michael B. Taylor, Ryan Kastner (UC San Diego, UC Santa Barbara, UC Washington)

## 개요

전력 분석 공격에서 정보 유출은 시간에 따라 균일하지 않다. Computational Blinking은 소프트웨어로 제어되는 전기적 분리를 통해 가장 많이 유출되는 시간 구간만 선택적으로 보호하여, 15~30% 구간 보호로 75% 이상의 mutual information을 차단한다.

## 방법론

### 비균일 정보 유출
- TVLA 분석으로 시간별 유출량 측정
- −log(p-values) > 11.51 구간이 취약 구간
- 대부분 시간에서 유출 거의 없음, 특정 포인트에서 대량 유출

### Computational Blinking
- 3단계 순차 실행: Blink Computing → Discharge → Recharge
- on-chip 에너지 저장장치로 격리된 환경에서 연산
- 고정 시간으로 정보 누출 차단

### 최적화 알고리즘
- 집합 커버 문제로 유출 구간 커버리지 최적화
- 보호 비율에 따른 정량적 보안-성능 트레이드오프

## 핵심 기여

1. 정보 유출의 시간적 비균일성을 활용한 최초의 소프트웨어 제어형 방어
2. ISA 확장으로 blink 명령어 지원
3. 정량적 보안-성능 트레이드오프 곡선 제공

## 주요 결과

- **정보 차단**: 15~30% 구간 보호로 75%+ mutual information 감소
- **일부 구간**: mutual information 거의 0 수준
- **성능 트레이드오프**: 12% (약 절반 보호) ~ 2.7× (거의 완전 보호)
- **반복 측정 무용성**: 동일 blink 구간에서 정보 획득 불가

## 한계점

- Blink 구간의 에너지 요구량이 연산 복잡도에 비례
- 모든 시간 구간 보호 시 2.7× 성능 저하

## 관련 개념

- [[paper-wiki/concepts/security.md|Security]]
