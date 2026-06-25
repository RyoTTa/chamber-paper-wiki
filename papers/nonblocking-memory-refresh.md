---
tags: [dram, refresh, reliability, server-memory]
venue: ISCA
year: 2018
summary_path: paper-summaries/2018ISCA-summarize/nonblocking-memory-refresh.md
---

# Nonblocking Memory Refresh

## 개요

Nonblocking Refresh는 DRAM의 갱신 연산 동안 읽기 요청을 차단하지 않고 백그라운드에서 갱신을 수행하는 기법입니다. 서버 메모리의 기존 중복 데이터를 활용하여 구현합니다.

## 방법론

- **부분 갱신 + 중복 데이터 활용**: 메모리 블록의 일부만 갱신하면서 Reed-Solomon 코드 등으로 누락된 데이터 계산
- **서버 메모리의 chipkill-correct 활용**: SCC, MCC, RAIM의 기존 체크 바이트를 갱신 중 데이터 계산에 재사용
- **쓰기 버퍼 관리**: Little's Law 기반 쓰기 버퍼 크기 결정, 쓰기 그룹 선택으로 갱신과 쓰기 동시 수행
- **장애 보존**: 오류 발견 시 재읽기로 기존 교정 능력 유지

## 핵심 기여

1. DRAM을 SRAM처럼 시스템 수준에서 배경 갱신 가능하도록 변환
2. 기존 중복 데이터 재사용으로 추가 하드웨어 비용 없이 구현
3. 16Gb 칩 16.2%, 32Gb 칩 30.3% 성능 향상

## 주요 결과

- 16Gb DRAM 칩: 평균 성능 16.2% 향상
- 32Gb DRAM 칩: 평균 성능 30.3% 향상
- 25% 갱신만 수행하는 시스템보다 2.5% 더 우수한 성능
- 5개 서버 메모리 시스템 모두에서 일관된 성능 향상

## 한계점

- 서버 메모리 시스템에 한정된 적용 (일반 PC/모바일 시스템에는 미적용)
- 영구 칩 장애 발생 시 해당 랭크는 차단 갱신으로 복귀
- 쓰기 버퍼 추가 비용 (약 28KB/채널)

## 관련 concept

- [[paper-wiki/concepts/dram.md|DRAM]]
