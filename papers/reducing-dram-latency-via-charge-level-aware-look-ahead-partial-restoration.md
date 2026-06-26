---
tags: [paper, 2018, 2018MICRO, topic/cache, topic/dram]
venue: "MICRO 2018 (51st Annual IEEE/ACM International Symposium on Microarchitecture)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/reducing-dram-latency-via-charge-level-aware-look-ahead-partial-restoration.md"
---

# Reducing DRAM Latency via Charge-Level-Aware Look-Ahead Partial Restoration

**Venue:** MICRO 2018 (51st Annual IEEE/ACM International Symposium on Microarchitecture)
**저자:** Yaohua Wang (ETH Zürich / National University of Defense Technology), Arash Tavakkol (ETH Zürich), Lois Orosa (ETH Zürich / University of Campinas), Saugata Ghose (Carnegie Mellon University), Nika Mansouri Ghiasi (ETH Zürich), Minesh Patel (ETH Zürich), Jeremie S. Kim (Carnegie Mellon University), Hasan Hassan (ETH Zürich), Mohammad Sadrosadati (ETH Zürich), Onur Mutlu (ETH Zürich / Carnegie Mellon University)

## 개요

- DRAM 접근 지연시간(long latency)은 시스템 성능의 주요 병목으로, 수십 년 동안 크게 개선되지 않음
- DRAM 셀은 커패시터로 구성되어 데이터를 읽을 때 셀의 전하를 비트라인과 공유하고, 이를 복원(restoration)해야 함
- 복원 작업이 전체 DRAM 접근 지연시간의 최대 **43.6%**를 차지
- 기존 복원 트렁케이션(Restore Truncation) 메커니즘은 곧 리프레시될 셀의 전하를 부분적으로 복원하지만, 활성화 시간을 줄이는 상보적 메커니즘(ChargeCache)의 이점을 잠재울 수 있음
- 높은 전하 수준의 셀은 활성화 시간이 더 짧음 (ChargeCache [24]: tRCD 13.75ns → 9.7ns, tRAS 35ns → 23.8ns)
- 문제: 부분 복원이 지나치게 낮은 전하 수준으로 복원되면, 향후 활성화 시 시간 절감 이점을 상실

## 방법론

### 3.1. 타이머 테이블 구조

- 8-way 셋 어소시에이티브 캐시와 유사한 구조의 타이머 테이블
- 코어당 256개 엔트리, LRU 교체 정책
- 각 엔트리: DRAM 행의 다음 활성화 예상 시간 저장
- 타이머는 16ms 윈도우에 대해 15ms까지 카운트다운 (1ms 여유로 ACT-PRE 쌍 발행 보장)

### 3.2. 복원 지연시간 결정

| 조건 | tRAS (ns) | tWR (ns) | tRCD (ns) |
|------|-----------|----------|-----------|
| 기본값 (높은 전하) | 35 | 15 | 13.75 |
| 1ms 이내 히트 (높은 전하 유지) | 16.1 | 6.8 | 11.2 |
| 1-16ms 히트 (일반 전하) | 19.4 | 8.4 | 13.75 |

- **1ms 이내 재접근 시**: 높은 전하 수준이 유지되므로 tRAS/tWR/tRCD 대폭 감소
- **1-16ms 재접근 시**: Restore Truncation과 유사한 부분 복원
- **리프레시 임박 시**: 리프레시가 데이터를 올바르게 감지할 수 있을 만큼만 복원

### 3.3. 완전 복원 메커니즘

- 타이머가 만료되면 메모리 컨트롤러가 (ACT, PRE) 명령어 쌍을 즉시 발행
- 해당 행이 완전히 복원되도록 전체 활성화/복원 지연시간 사용
- 코당 최대 256개 엔트리에 대한 오버헤드: <0.1%

### 3.4. 보안 고려사항

- 타이머 테이블 플러시 시 최악의 경우 오버헤드: 100회/초 컨텍스트 스위칭에서 약 0.1%
- 에너지 오버헤드: 약 0.12%

## 핵심 기여

- CAL은 메모리 컨트롤러에서만 구현하여 DRAM 모듈 변경 없이 14.7% 성능 향상 및 11.3% 에너지 절감 달성
- 기존 ChargeCache 및 Restore Truncation과 호환되며, 상보적으로 작동
- 다음 접근 시간 예측과 리프레시 시간을 활용한 정밀한 부분 복원으로 상보적 메커니즘의 이점을 유지
- DRAM 지연시간 감소를 위한 실용적이고 효과적인 하드웨어 메커니즘 제시

## 주요 결과

| 항목 | 세부사항 |
|------|---------|
| **구현 위치** | 메모리 컨트롤러 (DRAM 모듈 변경 없음) |
| **하드웨어 추가** | 타이머 테이블 (코어당 256 엔트리, 8-way associative) |
| **시뮬레이터** | Ramulator (사이클 정확 DRAM 시뮬레이터) + Pin 기반 CPU/캐시 모델 |
| **DRAM** | DDR4-1600, 800MHz 버스 주파수, 1-2 채널, 1 랭크, 4 뱅크 그룹, 4 뱅크 |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/reducing-dram-latency-via-charge-level-aware-look-ahead-partial-restoration.md|전체 요약 보기]]
