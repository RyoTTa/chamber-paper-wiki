---
tags: [paper, 2018, 2018MICRO, topic/nvm, topic/persistent-memory, topic/logging]
venue: "MICRO 2018"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/efficient-hardware-assisted-logging-with-asynchronous-and-direct-update-for-persistent-memory.md"
---

# Efficient Hardware-Assisted Logging with Asynchronous and Direct-Update for Persistent Memory

**Venue:** MICRO 2018
**저자:** Jungi Jeong, Chang Hyun Park, Jaehyuk Huh, Seungryoul Maeng (KAIST)

## 개요

지속 메모리(NVM)에서 원자적 지속성을 지원하기 위한 HW 보조 로깅 기법에서, 기존 접근법들은 로그 쓰기 효율과 데이터 업데이트 효율 사이에 트레이드오프가 존재한다. ReDU는 DRAM 캐시를 활용한 직접/비동기 데이터 업데이트로 기존 기법들 대비 8.6-23.6% 성능 향상을 달성한다.

## 방법론

### HW 보조 로깅의 설계 공간
- **로그 쓰기 효율화**: Coalescing (변수 크기 로깅) + Packing (NVM 쓰기 횟수 감소)
- **데이터 업데이트 속성**: 동기/비동기 × 직접/간접 × SW/HW 플러시

### ReDU 아키텍처
- **DRAM 캐시 활용**: NVM 쓰기를 임계 경로에서 분리
  - 트랜잭션 커밋 시 캐시에서 수정된 캐시라인을 DRAM 캐시로만 동기적으로 플러시
  - DRAM 캐시에서 NVM로는 비동기적으로 쓰기
- **직접 업데이트**: DRAM 캐시에서 직접 NVM로 새 데이터 쓰기 (간접 업데이트의 NVM 읽기 불필요)
- **HW 필터**: 블룸 필터로 DRAM 캐시 조회 오버헤드 완화

### 로그 관리
- 글로벌 로그 영역을 순차적으로 할당
- 커밋된 트랜잭션의 모든 캐시라인이 NVM에 플러시된 후에만 로그 제거

## 핵심 기여

1. HW 보조 로깅의 디자인 공간을 체계적으로 탐구하고 트레이드오프 분석
2. DRAM 캐시를 활용한 직접/비동기 데이터 업데이트 제안 (ReDU)
3. 기존 기법들의 한계를 극복하는 범용 로깅 메커니즘

## 주요 결과

- **대규모 순차 쓰기**: Redo 대비 21.2%, Undo+Redo 대비 35.4% 향상
- **소규모 무작위 쓰기**: Undo 대비 16.7%, Redo 대비 12.1%, Undo+Redo 대비 21.7% 향상
- **전체 평균**: Undo/Redo/Undo+Redo 대비 8.6%/14.2%/23.6% 성능 향상
- **읽기 전용 워크로드**: HW 필터가 DRAM 캐시 조회 오버헤드 효과적으로 완화
- **LRU 쓰기백 정책**: HashMap에서 최대 30.4% 성능 향상

## 한계점

- DRAM 캐시 오버헤드: 데이터 블록 32MB + 메타데이터 8MB = 총 40MB
- 읽기 지연 시간 증가: HW 필터로 완화하나 완전히 제거 불가
- 오버플로 시 트랜잭션 중단 필요 (소프트웨어 경로로 폴백)

## 관련 개념

- [[paper-wiki/concepts/nvm.md|NVM]]: 비휘발성 메모리의 지속성 지원 메커니즘
- [[paper-wiki/concepts/persistent-memory.md|Persistent Memory]]: 원자적 지속성을 위한 로깅 기법

## 관련 논문 요약

- [paper-summaries/2018MICRO-summarize/efficient-hardware-assisted-logging-with-asynchronous-and-direct-update-for-persistent-memory.md]
