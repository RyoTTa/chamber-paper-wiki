---
tags: [paper, dram, latency-reduction, charge-level, partial-restoration]
venue: MICRO 2018
year: 2018
summary_path: paper-summaries/2018MICRO-summarize/reducing-dram-latency-via-charge-level-aware-look-ahead-partial-restoration.md
---

# Reducing DRAM Latency via Charge-Level-Aware Look-Ahead Partial Restoration

## 개요

- DRAM 복원 지연시간을 줄이되 상보적 메커니즘(ChargeCache)의 이점을 유지하는 CAL 메커니즘 제안
- 메모리 컨트롤러에서만 구현 (DRAM 모듈 변경 없음)
- 다음 접근 시간 예측과 리프레시 시간을 활용한 정밀한 부분 복원

## 방법론

- **타이머 테이블**: 8-way 셋 어소시에이티브, 코어당 256 엔트리, LRU 교체 정책
- **복원 수준 결정**: 다음 접근 시간 예측 + 리프레시 시간 기반
  - 1ms 이내 재접근: 높은 전하 유지 → tRAS/tWR/tRCD 대폭 감소
  - 1-16ms 재접근: Restore Truncation과 유사한 부분 복원
  - 리프레시 임박: 리프레시가 데이터를 올바르게 감지할 수 있을 만큼만 복원
- **완전 복원 메커니즘**: 타이머 만료 시 (ACT, PRE) 명령어 쌍으로 완전 복원

## 핵심 기여

- Charge-Level-Aware Look-Ahead Partial Restoration (CAL) 메커니즘 제안
- 기존 ChargeCache 및 Restore Truncation과 호환되는 상보적 기술
- 메모리 컨트롤러에서만 구현하여 DRAM 모듈 변경 불필요

## 주요 결과

- 8코어 시스템 평균 **14.7%** IPC 가속도
- DRAM 에너지 소비 **11.3%** 감소
- ChargeCache(11.2%) 및 Restore Truncation보다 우수한 성능
- 메모리 집약도가 높을수록 큰 성능 향상

## 한계점

- 타이머 테이블 플러시 시 오버헤드 (컨텍스트 스위칭 시)
- 코어당 256 엔트리의 면적 오버헤드 (미미하지만 존재)
- 모든 워크로드에서 동일한 효과를 보장하지 않음

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/cache.md|Cache]]
