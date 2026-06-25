---
tags: [persistent-memory, transactional-memory, crash-consistency, hardware-acceleration]
venue: ISCA
year: 2018
summary_path: paper-summaries/2018ISCA-summarize/dhtm-durable-hardware-transactional-memory.md
---

# DHTM: Durable Hardware Transactional Memory

## 개요

DHTM은 상용 하드웨어 트랜잭션 메모리(HTM)와 하드웨어 redo 로깅을 결합한 최초의 완전한 ACID 트랜잭션 메모리 솔루션입니다. 바이트 주소 가능한 영구 메모리에서 높은 성능으로 내구성을 보장합니다.

## 방법론

- **하드웨어 redo 로깅**: L1 캐시 컨트롤러가 LLC를 우회하여 영구 메모리에 직접 로그 항목 기록
- **로그 병합 메커니즘**: 로그 버퍼를 통한 동일 캐시 라인의 여러 저장 병합
- **L1→LLC 오버플로우**: 쓰기 세트가 L1에서 LLC로 확장 가능 (코어런스 프로토콜 미세 변경)

## 핵심 기여

1. ACID 트랜잭션을 위한 최초의 완전한 하드웨어 솔루션
2. L1 캐시 제한 없이 LLC까지 확장된 트랜잭션 크기 지원
3. 하드웨어 로깅과 로그 병합을 통한 효율적인 내구성 보장

## 주요 결과

- TATP, TPC-C 및 마이크로벤치마크에서 기존 기술 대비 21%~25% 성능 향상
- 재시도 로깅으로 빠른 커밋 및 abort 지원

## 한계점

- 상용 HTM(Intel RTM)에 대한 의존성
- 로그 버퍼 크기에 따른 트랜잭션 크기 제한 가능성

## 관련 concept

- [[paper-wiki/concepts/persistent-memory.md|Persistent Memory]]
- [[paper-wiki/concepts/transactional-memory.md|Transactional Memory]]
- [[paper-wiki/concepts/crash-consistency.md|Crash Consistency]]