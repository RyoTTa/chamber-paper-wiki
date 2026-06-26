---
tags: [paper, 2021, 2021ISCA, topic/cache, topic/compression, topic/dram, topic/gpu, topic/near-data-processing, topic/nvm, topic/pim, topic/storage]
venue: "ISCA 2021 (48th Annual IEEE/ACM International Symposium on Computer Architecture)"
year: 2021
summary_path: "../paper-summaries/2021ISCA-summarize/boss-bandwidth-optimized-search-accelerator-for-storage-class-memory.md"
---

# BOSS: Bandwidth-Optimized Search Accelerator for Storage-Class Memory

**Venue:** ISCA 2021 (48th Annual IEEE/ACM International Symposium on Computer Architecture)
**저자:** Jun Heo (Seoul National University), Seung Yul Lee (Seoul National University), Sunhong Min (Seoul National University), Yeonhong Park (Seoul National University), Sung Jun Jung (Seoul National University), Tae Jun Ham (Seoul National University), Jae W. Lee (Seoul National University)

## 개요

- 풀텍스트 검색은 가장 보편적인 웹 서비스 중 하나이며, 역방향 인덱스(Inverted Index)는 대부분의 검색 엔진에서 사용되는 표준 데이터 구조
- 웹 문서의 지속적인 증가로 역방향 인덱스의 규모가 계속 커지고 있으며, 기존 DRAM 기반 메모리 확장 방식은 CPU 소켓과 DIMM을 함께 추가해야 하므로 시스템 비용이 **초선형(super-linear)**으로 증가 (메모리 용량 2배 증가 시 시스템 비용 **3배** 증가)
- Storage-Class Memory(SCM)는 DRAM과 디스크 간의 간극을 메우는 새로운 메모리 계층으로, Intel Optane DCPMM 기준 채널당 최대 **512GB** (DRAM 대비 **4배**)를 지원하며 비트당 비용이 훨씬 저렴
- 그러나 SCM 기반 메모리 풀은 두 가지 대역폭 제약을 도입: (1) SCM 디바이스 자체의 대역폭이 DRAM 대비 **3~6배** 낮음, (2) 호스트 CPU까지의 공유 인터커넥트 대역폭이 DRAM 채널 대비 훨씬 낮아 대역폭-용량 비율이 크게 저하
- 기존 하드웨어 가속기(IIU 등)는 메모리 용량 문제를 해결하지 못했으며, CPU/GPU 기반 방식은 메모리 용량 제약과 높은 에너지 소비에 시달림

## 방법론

### 3.1. 전체 파이프라인 구조

- BOSS 코어는 **Block Fetch Module**, **Decompression Module(4개)**, **Intersection Module**, **Union Module**, **Scoring Module(4개)**, **Top-k Module**으로 구성
- 사용자 쿼리 → 역방향 인덱스 샤드에서 압축된 포스팅 리스트를 SCM에서 페칭 → 압축 해제 → 셋 연산(Union/Intersection) → 스코어링 → Top-k 선택 → 호스트로 결과 전송
- Block Fetch Module에서 **overlap check**를 통해 불필요한 블록을 건너뛰고, Union Module에서 **WAND(Window AND)** 알고리즘으로 평가 대상 문서를 추가 필터링

### 3.2. Early-Termination 메커니즘

- **Score Estimation Unit**: 블록 단위의 쿼리 스코어 상한선(upper-bound)을 추정하여, 상한선이 현재 최소 스코어보다 낮은 블록을 스킵
- **Block-level pruning**: 블록 내 모든 문서의 스코어를 계산하기 전에 블록 전체의 상한선으로 조기 종료
- **Document-level pruning (WAND)**: 개별 문서의 스코어 상한선이 임계값 미만이면 해당 문서의 스코어링을 건너뜀
- Union 쿼리(Q1, Q3, Q5): 용어 수가 많아질수록 효과 감소 (블록 간 문서 공유 가능성 감소로 상한선이 느슨해짐)
- Intersection 쿼리(Q2, Q4, Q6): 용어 수가 많아질수록 효과 증가 (교차 연산 반복 시 비교 대상 docID가 점점 줄어들어 불필요한 블록 스킵 가능)

### 3.3. 멀티터미 쿼리 최적화 및 Top-k 모듈

- **중간 데이터 제거**: 기존 방식에서 교차/합집합 연산 결과를 호스트로 전송后再 처리하나, BOSS는 하드웨어 파이프라인 내에서 중간 결과를 직접 처리하여 중간 데이터 이동 완전히 제거
- **Top-k Selection Module**: 스코어링된 결과를 하드웨어 내에서 실시간으로 상위 k개 유지 (shift register 기반), 최종 결과만 호스트로 전송
- 호스트-가속기 인터커넥트 대역폭 소비를 대폭 절감하여 메모리 풀 확장 시 대역폭 병목 문제 완화

### 3.4. 프로그래밍 가능한 압축 해제 모듈

- **5가지 압축 방식 지원**: Bit-Packing(BP), VariableByte(VB), OptPForDelta(OptPFD), Simple16(S16), Simple8b(S8b)
- 각 역방향 인덱스 포스팅 리스트에 대해 최적의 압축 방식을 사전에 선택하고, 압축 해제 모듈은 해당 방식으로 동작
- 재구성 가능한 decompression 하드웨어로 다양한 압축 스킴을 유연하게 지원

## 핵심 기여

- **핵심 Contribution**: 역방향 인덱스 검색을 위한 최초의 NDP 가속기 아키텍처 제시, SCM 기반 메모리 풀에서의 대역폭 문제를 해결하는 종합 솔루션
- **성능**: 8코어 Lucene 대비 지오평균 **8.1배** speedup, 에너지 **189배** 절감
- **실용성**: Chisel3로 구현된 합성 가능한 RTL, TSMC 40nm 기준 8.27mm²/3.2W로 실용적인 면적/전력
- **SCM 활용**: DRAM 대비 4배 큰 용량과 낮은 비트당 비용으로 대규모 역방향 인덱스를 비용 효율적으로 호스팅
- **확장성**: 대역폭 효율이 높아 SCM 디바이스 대역폭이 향将来도 BOSS는 추가 코어를 효과적으로 활용 가능

## 주요 결과

| 항목 | 내용 |
|------|------|
| **구현 언어** | Chisel3 (Scala 기반 HDL) → Verilog 변환 → Synopsys Design Compiler 합성 |
| **기술 노드** | TSMC 40nm |
| **BOSS 코어 수** | 8개 (각 1.0GHz) |
| **단일 코어 면적** | 1.003 mm² |
| **전체 면적** | 8.27 mm² (코어 8.02 + Command Queue 0.078 + Query Scheduler 0.001 + MAI 0.127) |
| **전력** | 3.2W (호스트 CPU 74.8W 대비 **23.3배** 절감) |
| **메모리 시스템** | SCM 4채널, 순차 읽기 25.6GB/s, 랜덤 읽기 6.6GB/s, 쓰기 2.3GB/s |
| **호스트 CPU** | Intel Xeon Scalable 8280M @ 2.70GHz, DDR4 2666 6채널 384GB |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2021ISCA-summarize/boss-bandwidth-optimized-search-accelerator-for-storage-class-memory.md|전체 요약 보기]]
