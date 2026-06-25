---
tags: [paper, nvm, crash-consistency, wal, persistent-memory, 2018]
venue: MICRO 2018
year: 2018
summary_path: paper-summaries/2018MICRO-summarize/picl-a-software-transparent-persistent-cache-log-for-nonvolatile-main-memory.md
---

# PiCL: A Software-Transparent Persistent Cache Log for Nonvolatile Main Memory

## 개요

- 소프트웨어 투명 크래시 일관성을 1% 미만 성능 오버헤드로 구현하는 WAL 메커니즘
- 멀티-언도 로깅, 캐시 기반 로깅, 비동기 캐시 스캔을 결합
- 기존 1.5~5.0배 성능 저하를 1% 미만으로 대폭 개선

## 방법론

- 멀티-언도 로깅: 여러 에포크의 동시 로깅 가능
- 캐시 기반 로깅: read-log-modify 시퀀스 우회, 온칩 언도 버퍼 활용
- 비동기 캐시 스캔: 캐시 플러시를 크리티컬 패스에서 제거
- DDR NVDIMM 인터페이스와의 완전 호환

## 핵심 기여

- 캐시 플러시와 랜덤 접근 문제를 동시에 해결하는 메커니즘 조합
- FPGA 프로토타입(OpenPiton)을 통한 실현 가능성 검증
- 기존 소프트웨어와의 완전 호환 (소프트웨어 투명)

## 주요 결과

- 1% 미만의 성능 오버헤드 달성 (단일/멀티코어)
- 기존 방식 대비 1.5~5.0배 성능 저하 제거
- 캐시 플러시와 비순차적 로깅이 기존 오버헤드의 주요 원인 확인

## 한계점

- NVM의 랜덤 접근 성능에 여전히 의존
- 에포크 길이에 따른 내구성-성능 트레이드오프
- FPGA 프로토타입 수준 (상용 구현 미검증)

## 관련 concept 페이지

- [[paper-wiki/concepts/nvm|Non-Volatile Memory]]
