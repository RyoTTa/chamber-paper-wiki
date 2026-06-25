---
tags: [paper, 2018, 2018ISCA, topic/security]
venue: "ISCA 2018"
year: 2018
summary_path: "../paper-summaries/2018ISCA-summarize/guaranteeing-local-differential-privacy-on-ultra-low-power-systems.md"
---

# Guaranteeing Local Differential Privacy on Ultra-Low-Power Systems

**Venue:** ISCA 2018
**저자:** Woo-Seok Choi, Matthew Tomei, Jose Rodrigo Sanchez Vicarte, Pavan Kumar Hanumolu, Rakesh Kumar (Univ. of Illinois)

## 개요

ULP(Ultra-Low-Power) 시스템에서 저해상도/고정소수점 하드웨어의 제약으로 인해 Laplace 분포 노이즈를 정확히 생성할 수 없어 LDP 보장이 불가능하다. Resampling과 Thresholding 기술로 이 문제를 해결하는 DP-Box 하드웨어 모듈을 제안한다.

## 방법론

### ULP 환경의 문제
- 저해상도/고정소수점으로 인한 양자화 오차
- 최소 표현 간격 제한으로 충분한 확률 분포 표현 불가
- 이론적 ε-DP 보장이 실제로는 위반됨

### Resampling
- 고정소수점 샘플을 반복 샘플링하여 effective 해상도 향상
- r배 반복으로 Laplace 분포에 수렴

### Thresholding
- 고정소수점 경계에서의 왜곡 보정
- Resampling과 결합하여 실제 ε-DP 보장 달성

### DP-Box 하드웨어
- 프로세서/센서 컨트롤러에 통합 가능한 LDP 하드웨어 모듈
- I2C 인터페이스로 센서 연결

## 핵심 기여

1. ULP 시스템에서의 첫 LDP 구현
2. Resampling/Thresholding으로 저해상도 제약 극복
3. 프라이버시 예산 제어 알고리즘 제시

## 주요 결과

- **개인정보 보장**: DP-Box로 다양한 ε에서 안정적 LDP 달성
- **유틸리티**: 부동소수점 LDP 대비 낮은 오버헤드로 유사 유틸리티
- **Randomized Response**: 범주형 데이터도 지원
- **하드웨어 오버헤드**: 미미한 면적/전력 추가

## 한계점

- 단일 센서 기반 LDP, 다중 센서 집계 시 추가 연구 필요
- 고주파 센서 읽기에서는 오버헤드 증가 가능

## 관련 개념

- [[paper-wiki/concepts/security.md|Security]]
