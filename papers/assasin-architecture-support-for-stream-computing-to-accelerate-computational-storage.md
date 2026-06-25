---
tags: [paper, 2022, 2022MICRO, topic/cache, topic/disaggregation, topic/dram, topic/near-data-processing, topic/storage]
venue: "55th IEEE/ACM International Symposium on Microarchitecture (MICRO 2022)"
year: 2022
summary_path: "../paper-summaries/2022MICRO-summarize/assasin-architecture-support-for-stream-computing-to-accelerate-computational-storage.md"
---

# ASSASIN: Architecture Support for Stream Computing to Accelerate Computational Storage

**Venue:** 55th IEEE/ACM International Symposium on Microarchitecture (MICRO 2022)
**저자:** Chen Zou, Andrew A. Chien (University of Chicago; Argonne National Laboratory)

## 개요

- NAND flash의 급격한 스케일링으로 leading 엔터프라이즈 SSD의 대역폭이 6.95 GB/s, IOPS 900K를 초과하여, 데이터 센터에서 저장 대역폭을 컴퓨팅이 따라잡는 문제가 발생.
- 기존 disaggregated storage는 compute와 storage를 별도로 스케일링하지만, flash 대역폭 확장에 맞춘 interconnect와 패킷/데이터 처리 부담이 급증하며 핫스팟 문제가 대두.
- Computational SSD가 flash 대역폭 확장 문제를 해결하기 위한 대안으로 주목되지만, **SSD 내부의 메모리 벽(memory wall)** 문제에 직면: compute engine이 flash 데이터를 SSD DRAM을 통해 접근할 때 DRAM 대역폭이 병목이 됨.
- 기존 일반 목적 computational SSD 아키텍처(Figure 4)에서 필터 함수의 경우 flash 채널 대역폭(1.6~3.2 GB/s) 대비 0.63 GB/s에 불과하며, 메모리 접근 stall이 3배 성능 저하 유발(Figure 5).
- SSD 수준에서 8개 8-bit flash 채널(12.8 GB/s)의 경우 SSD DRAM 대역폭 요구량이 최소 25.6 GB/s으로 LPDDR4의 한계(16 GB/s)를 초과.

## 방법론

### 3.1. 메모리 벽 분석 및 동기 부여

- 기존 computational SSD(Figure 4): flash 컨트롤러 → SSD DRAM → 캐시 → compute engine 순으로 데이터가 이동.
- Filter 함수의 사이클 분해(Figure 5): compulsory miss와 DRAM 접근이 3배 성능 저하 유발.
- 캐시는 스트리밍 데이터에 low reuse로 효과 미미; multi-channel/HBM은 SSD의 전력/비용 제약에 비실용적.
- ASSASIN은 flash 데이터 스트림을 inline에서 처리하는 새로운 메모리 계층을 제안.

### 3.2. ASSASIN SSD 아키텍처 구성

- flash 배열과 SSD DRAM 사이에 **통합된 compute engine 세트(unified compute engines)** 배치 → SSD DRAM 병목 제거.
- **SSD 레벨 크로스바 인터커넥트:** compute engine과 flash 채널 간 all-to-all 연결로 데이터 분배 및 처리.
  - flash 레이아웃 불균일 시에도 crossbar가 데이터를 재분배하여 성능 보장.
  - 기존 채널 로컬 compute 방식 대비 skew 상황에서 최대 **3~8배** 성능 향상(Figure 19).
- FTL 독립성 보존: flash 페이지 레이아웃 관리를 FTL에 맡겨 일반성(generality) 유지.

### 3.3. ASSASIN 코어 아키텍처

- RISC-V 기반 in-order 코어(1 GHz)에 ISA 확장 적용.
- **스트림 버퍼(Stream Buffer):**
  - flash 데이터 스트림의 헤드(head-only)에 대한 소규모 prefetch FIFO.
  - 64B 와이드 인터페이스에서도 0.5ns 사이클 달성(Figure 20).
  - `StreamLoad`/`StreamStore` 명령으로 주소 계산 및 포인터 관리 명령 제거.
  - dcache 대체 시 클럭 주기 11% 단축(IF stage가 critical path로 이동).
- **스크래치패드(Scratchpad):**
  - 함수 상태(function states)에 대한 랜덤 접근 지원.
  - 64KB 크기에서 8B 인터페이스도 1GHz 코어에서 2사이클 필요 → 스트림 버퍼 대비 성능 불리.

## 핵심 기여

- **핵심 기여:** Computational SSD의 메모리 벽 문제를 flash 데이터 스트림에서의 inline 연산으로 해결하는 최초의 일반-purpose 아키텍처.
- **스트리밍 메모리 계층:** 스트림 버퍼 + 스크래치패드 + ISA 확장으로 저전력, 저지연 flash 데이터 접근 달성.
- **성능:** Offload 함수에서 **1.5~2.4x** speedup, end-to-end 데이터 분석에서 **1.1~1.5x** speedup.
- **효율:** **2.0x 전력 효율**, **3.2x 면적 효율** 향상.
- **일반성:** FTL 독립성 보존으로 flash 레이아웃 관리와 computational storage를 동시에 지원.
- **의의:** disaggregated storage의 대안으로서 computational SSD의 실용성을 입증하고, flash 대역폭 확장에 맞춘 효율적인 in-SSD 컴퓨팅 아키텍처를 제시.

## 주요 결과

- **구현 언어:** SystemVerilog (ISA 확장 및 스트림 버퍼/스크래치패드).
- **기술 노드:** SAED 14nm 기술 라이브러리.
- **코어 기반:** ibex RISC-V 코어(classical 5-stage pipeline: IF, DE/RR, EX, MEM, WB).
- **시스템 구성:** flash 배열(8개 8-bit 채널, 8 GB/s) + SSD DRAM(LPDDR4) + ASSASIN 코어们 + 크로스바 인터커넥트.
- **평가 도구:** Gem5 시뮬레이터, Cacti(@14nm)로 캐시 성능 측정, Design Compiler로 면적/전력 합성.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2022MICRO-summarize/assasin-architecture-support-for-stream-computing-to-accelerate-computational-storage.md|전체 요약 보기]]
