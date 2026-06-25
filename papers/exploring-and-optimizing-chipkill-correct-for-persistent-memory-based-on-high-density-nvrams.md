---
tags: [paper, 2018, 2018MICRO, topic/nvm, topic/reliability, topic/ecc]
venue: "MICRO 2018"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/exploring-and-optimizing-chipkill-correct-for-persistent-memory-based-on-high-density-nvrams.md"
---

# Exploring and Optimizing Chipkill-Correct for Persistent Memory Based on High-density NVRAMs

**Venue:** MICRO 2018
**저자:** Da Zhang (Virginia Tech), Vilas Sridharan (AMD), Xun Jian (Virginia Tech)

## 개요

고밀도 NVRAM 기반 지속 메모리는 높은 원시 비트 오류율(RBER)로 인해 기존 DRAM chipkill-correct를 그대로 적용하면 >=69% 저장 비용이 발생한다. 이 논문은 부팅/런타임 오류 교정을 분리하고, VLEW와 칩 고장 보호 비트를 재사용하여 총 27% 저장 비용으로 chipkill-correct를 달성하는 효율적인 체계를 제안한다.

## 방법론

### 부팅/런타임 오류 교정 분리
- **부팅 시간**: 높은 RBER → VLEW로 효율적 데이터 생존 보장 (최소 저장 비용)
- **런타임**: 낮은 RBER → 칩 고장 보호 비트를 활용한 기회주의적 비트 오류 교정

### VLEW (Very Long ECC Word)
- 각 ECC 워드가 하나의 칩 내 256B 데이터를 보호
- 부팅 시간에 1주-1년 간의 데이터 생존을 최소 저장 비용으로 보장
- 칩 고장 보호 비트 재사용으로 추가 저장 비용 없음

### OMV LLC 캐싱 및 Bitwise Sum 쓰기
- 더러운 지속 메모리 블록의 이전 값을 LLC에 보존 (평균 98.6% 히트율)
- 쓰기 요청 시 새 데이터와 OMV의 비트wise 합을 전송
- NVRAM 칩 내부에서 비트wise 차로 새 데이터 복원 및 VLEW 코드 비트 업데이트

## 핵심 기여

1. 고밀도 NVRAM 기반 지속 메모리의 효율적인 chipkill-correct 제안
2. 부팅/런타임 오류 교정 분리로 저장 비용 69%+ → 27%로 대폭 절감
3. OMV LLC 캐싱과 Bitwise Sum 쓰기로 쓰기 대역폭 오버헤드 해결
4. 칩 고장 보호에 추가 저장 비용 없이 2% 성능 오버헤드로 달성

## 주요 결과

- **저장 비용**: 제안 27% (기존 DRAM chipkill 확장 >=69% 대비 크게 절감)
- **성능 오버헤드**: 평균 2% (ReRAM 기준), 2.3% (PCM 기준)
- **신뢰성 향상**: chipkill-correct 적용 시 40배 신뢰성 개선
- **OMV LLC 히트율**: 평균 98.6% → 오프칩 OMV 페칭 오버헤드 거의 없음
- **최악의 경우**: hashmap에서 14% 성능 오버헤드 (쓰기 전용 워크로드)

## 한계점

- NVRAM 칩에 BCH 인코더 내장 필요 (면적 0.1mm², 지연 1.6ns)
- 쓰기 수명 저하 가능 — 쓰기 지연 시간 증가로 보상
- 영구적 칩 고장 시 빈번한 VLEW 교정으로 성능 저하 가능

## 관련 개념

- [[paper-wiki/concepts/nvm.md|NVM]]: 고밀도 비휘발성 메모리의 신뢰성 문제
- [[paper-wiki/concepts/reliability.md|Reliability]]: 서버 메모리 시스템의 신뢰성 요구사항
- [[paper-wiki/concepts/ecc.md|ECC]]: 비트 오류 및 칩 고장 보호를 위한 ECC 기법

## 관련 논문 요약

- [paper-summaries/2018MICRO-summarize/exploring-and-optimizing-chipkill-correct-for-persistent-memory-based-on-high-density-nvrams.md]
