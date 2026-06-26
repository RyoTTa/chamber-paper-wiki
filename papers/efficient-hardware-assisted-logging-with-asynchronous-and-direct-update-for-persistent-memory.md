---
tags: [paper, 2018, 2018MICRO, topic/cache, topic/dram, topic/nvm, topic/storage]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/efficient-hardware-assisted-logging-with-asynchronous-and-direct-update-for-persistent-memory.md"
---

# Efficient Hardware-Assisted Logging with Asynchronous and Direct-Update for Persistent Memory

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Jungi Jeong, Chang Hyun Park, Jaehyuk Huh, Seungryoul Maeng (KAIST)

## 개요

- 비휘발성 메모리(NVM: PCM, STT-MRAM, ReRAM)는 DRAM에 가까운 접근 지연과 높은 저장 밀도를 제공하는 새로운 스토리지 클래스 메모리(SCM)로 부상
- 그러나 시스템 실패 시 데이터 일관성을 보장하기 위해 **원자적 지속성(Atomic Durability)** 지원 필요
- 기존 WAL(Write-Ahead Log) 기반 소프트웨어 로깅 기법은 성능 오버헤드가 큼:
  - 추가 명령어 삽입으로 실행 사이클 증가
  - 명시적 캐시 플러시 및 메모리 펜스 명령으로 인한 느린 순서 강제
- HW 기반 로깅 기법이 제안되었으나, 각 접근법에 성능 트레이드오프 존재:
  - **Undo 접근**: 이전 값만 로깅 → 동기적 제자리 업데이트 필요 → 긴 임계 경로
  - **Redo 접근**: 새 값만 로깅 → 간접 업데이트로 NVM 읽기 대역폭 추가 소비
  - **Undo+Redo 접근**: 이전 값과 새 값 모두 로깅 → 로그 크기 2배 증가 → 더 많은 로그 쓰기

## 방법론

### 3.1. DRAM 캐시 활용

- **목적**: NVM 쓰기를 임계 경로에서 분리하고, 기존 Redo의 간접 업데이트 문제 해결
- **구성**:
  - 전체 DRAM에서 작은 영역(기본 32MB)을 NVM 라이트 캐시로 예약
  - Dedicated DIMM이나 적층 메모리 불필요
  - 메타데이터 테이블(오프셋 테이블 + 트랜잭션 테이블)에 추가 8MB 필요
- **트랜잭션 관리**:
  - L1 캐시의 각 캐시라인에 트랜잭션 비트 추가
  - 트랜잭션 커밋 시 트랜잭션 비트가 설정된 캐시라인을 DRAM 캐시로 플러시
  - **오프셋 테이블**: 물리 주소 → DRAM 캐시 내 상대 오프셋 변환 (48비트 주소, 15비트 TxID, 1비트 valid)
  - **트랜잭션 테이블**: TxID, 시작/마지막 로그 주소, 블록 카운트 관리

### 3.2. 제자리 데이터 업데이트

- **DRAM 캐시에서 NVM로의 쓰기백 정책**:
  - **Eager 정책**: 캐시라인 도착 시 즉시 NVM로 플러시 → 최소 DRAM 캐시 사용
  - **LRU 정책**: DRAM 캐시가 가득 찰 때까지 유지 → 업데이트 병합 가능, 읽기 캐싱 기회 증가
- 트랜잭션 커밋 후에는 DRAM 캐시의 캐시라인을 임의 순서로 NVM에 기록 가능

### 3.3. NVM 읽기 지연 완화

- **HW 필터**: DRAM 캐시 조회 오버헤드를 줄이기 위한 블룸 필터
  - **Eager 정책용**: 카운팅 블룸 필터 (1K 엔트리, 4비트/엔트리, 512B SRAM)
    - DRAM 캐시에 저장된 데이터를 정확히 보고
  - **LRU 정책용**: 비카운팅 블룸 필터 (32K 엔트리, 1비트/엔트리, 4KB SRAM)
    - 거짓 양성/음성 가능, 거짓 양성율 50% 초과 시 리셋
  - 필터가 미스를 보고하면 DRAM 캐시와 NVM을 **동시에** 접근

### 3.4. 로그 관리 및 복구

- **로그 관리**: 글로벌 로그 영역을 순차적으로 할당, Log Start/Log Offset 레지스터로 관리
  - 커밋된 트랜잭션의 모든 캐시라인이 NVM에 플러시된 후에만 로그 제거 가능
  - 로그 제거 시 전체 트랜잭션 로그 범위를 한 번에 제거 (로그 영역 내 교차된 엔트리 문제 해결)
- **복구**: 기존 Redo 로깅과 동일 — 미커밋 트랜잭션 로그 무시, 커밋된 트랜잭션 로그를 제자리 데이터로 복사

## 핵심 기여

- **핵심 기여**: HW 보조 로깅의 디자인 공간을 체계적으로 탐구하고, 기존 기법들의 트레이드오프를 분석
- **제안 기법 (ReDU)**: Redo 기반 로깅 + DRAM 캐시를 활용한 직접/비동기 데이터 업데이트
- **성능**: 기존 최적화된 기법들 대비 **8.6-23.6%** 처리량 향상
- **실용성**: DRAM의 작은 영역만 사용하여 NVM 쓰기 오버헤드를 효과적으로 완화
- **범용성**: 다양한 쓰기 패턴(대규모 순차, 소규모 무작위)에서 모두 우수한 성능
- **의의**: NVM 기반 시스템에서 원자적 지속성을 지원하는 HW 로깅의 최적 설계 방향을 제시, 향후 NVM 시스템 설계에 실질적 가이드라인 제공

## 주요 결과

- **시뮬레이터**: gem5 시뮬레이터 SE 모드
- **프로세서**: 2GHz x86 아웃오브오더, 8-way L1 I/D (32KB), 8-way L2 (256KB), 16-way L3 (8MB)
- **DRAM**: DDR3-1600, 4GB, 단일 채널
- **NVM**: 단일 채널, 읽기 50ns, 쓰기 150ns
- **벤치마크**:
  - 마이크로: Vector, Swap, HashMap, B-Tree, RB-Tree (NVML 라이브러리)
  - 매크로: YCSB (20%/80% 삽입/업데이트), TPCC (New Order), ECHO
  - 데이터 세트: Large (1KB-16KB 객체), Random (Rand.(n) — n개 객체에서 단일 워드 업데이트)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/efficient-hardware-assisted-logging-with-asynchronous-and-direct-update-for-persistent-memory.md|전체 요약 보기]]
