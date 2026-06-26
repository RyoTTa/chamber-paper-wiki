---
tags: [persistent-memory, logging, crash-consistency, hardware]
venue: HPCA
year: 2018
summary_path: paper-summaries/2018HPCA-summarize/steal-but-no-force-efficient-hardware-undoredo-logging-for-persistent-memory-systems.md
---

# Steal but No Force: Efficient Hardware Undo+Redo Logging for Persistent Memory Systems

## 개요

이 논문은 하드웨어 undo+redo 로깅을 통한 영속 메모리 시스템의 성능 및 에너지 효율성을 향상시키는 시스템을 제안합니다.

## 방법론

- 하드웨어 undo+redo 로깅 스킴
- 캐시 강제 쓰기 되돌리기(force-write-back) 메커니즘
- 쓰기 순서 제어 완화를 통한 성능 향상

## 핵심 기여

1. 하드웨어 undo+redo 로깅을 통한 영속 메모리 시스템 성능 향상
2. 쓰기 순서 제어 완화로 인한 시스템 처리량 증가
3. 메모리 트래픽 감소를 통한 동적 에너지 절약
4. 기존 메모리 시스템과의 호환성 유지

## 주요 결과

- 시스템 처리량 크게 향상
- 동적 에너지 및 메모리 트래픽 감소
- 소프트웨어 방식보다 강력한 일관성 보장
- 영속 메모리 마이크로벤치마크 및 실제 워크로드에서 모두 우수한 성능

## 한계점

- 하드웨어 로깅 로직의 추가 복잡성
- 특정 프로세서 아키텍처에 대한 의존성
- 다양한 워크로드에서의 성능 변동

## 관련 concept 페이지

- [[paper-wiki/concepts/persistent-memory|Persistent Memory]]
- [[paper-wiki/concepts/crash-consistency|Crash Consistency]]
- [[paper-wiki/concepts/logging|Logging]]

## 관련 논문 요약

- [paper-summaries/2018HPCA-summarize/steal-but-no-force-efficient-hardware-undoredo-logging-for-persistent-memory-systems.md]