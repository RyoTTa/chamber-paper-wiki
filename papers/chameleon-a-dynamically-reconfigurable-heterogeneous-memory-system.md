---
tags: [heterogeneous-memory, cache, pim, memory-tiering, hw-sw-codesign]
venue: MICRO
year: 2018
summary_path: paper-summaries/2018MICRO-summarize/chameleon-a-dynamically-reconfigurable-heterogeneous-memory-system.md
---

# CHAMELEON: A Dynamically Reconfigurable Heterogeneous Memory System

## 개요

- 캐시의 성능과 PoM(Part of Memory)의 용량을 동시에 달성하는 하이브리드 이종 메모리 아키텍처
- OS-하드웨어 공동 설계로 PoM↔캐시 모드를 동적으로 전환
- PoM 대비 11.6%, 지연 최적화 캐시 대비 24.2% 성능 향상
- ISA-Alloc/ISA-Free 두 가지 명령어로 OS-하드웨어 통신 구현

## 방법론

- **Chameleon:**
  - 메모리 사용량이 클 때: PoM 모드 → 최대 용량 활용
  - 메모리 사용량이 작을 때: 빈 공간을 하드웨어 관리 캐시로 활용
  - OS가 페이지 할당/해제를 하드웨어에 알림
- **하드웨어 메커니즘:**
  - SRRT(Segment Restricted Remapping Table)에 ABV, Mode Bit, Dirty Bit 추가
  - 세그먼트 그룹 단위로 스택/오프칩 드램 간 동적 리매핑
- **Chameleon-Opt:** 능동적 세그먼트 리매핑으로 캐시 히트율 추가 향상

## 핵심 기여

- 캐시와 PoM의 본질적 트레이드오프를 동적으로 해결하는 하이브리드 아키텍처 최초 제시
- OS-하드웨어 공동 설계를 통한 최소한의 ISA 변경으로 실현
- 이종 메모리 시스템의 새로운 설계 패러다임 제시

## 주요 결과

- PoM 대비 **11.6%** 성능 향상
- 지연 최적화 캐시 대비 **24.2%** 성능 향상
- PoM과 동등한 OS 가시 메모리 용량 유지
- 동적 모드 전환으로 멀티프로그래밍 워크로드에서 최적适应

## 한계점

- ISA-Alloc/ISA-Free 호출 오버헤드 (2KB 세그먼트 → 1024회 호출/2MB THP)
- 세그먼트 스왑 시 잠재적 성능 간섭 (on-demand 접근과 동시에 writeback)
- 메타데이터(SRRT) 오버헤드가 세그먼트 그룹 수에 비례

---

**관련 개념:** [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]], [[paper-wiki/concepts/compression.md|Compression]], [[paper-wiki/concepts/dram.md|DRAM]]
