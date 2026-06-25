---
tags: [paper, 2021, 2021MICRO, topic/dram, topic/near-data-processing, topic/pim, topic/rowhammer]
venue: "MICRO 2021 (54th Annual IEEE/ACM International Symposium on Microarchitecture)"
year: 2021
summary_path: "../paper-summaries/2021MICRO-summarize/trim-enhancing-processor-memory-interfaces-with-scalable-tensor-reduction-in-memory.md"
---

# TRiM: Enhancing Processor-Memory Interfaces with Scalable Tensor Reduction in Memory

**Venue:** MICRO 2021 (54th Annual IEEE/ACM International Symposium on Microarchitecture)
**저자:** Jaehyun Park (Seoul National University), Byeongho Kim (Seoul National University), Sungmin Yun (Seoul National University), Eojin Lee (Inha University), Minsoo Rhu (KAIST), Jung Ho Ahn (Seoul National University)

## 개요

- 추천 시스템(Recommendation System, RecSys)은 Facebook, YouTube, Alibaba 등 주요 기업에서 딥러닝 기반으로 운영되며, Facebook의 경우 AI 추론 사이클의 **80%**를 차지할 정도로 산업적 중요성이 크다
- RecSys의 핵심 구성 요소인 **Tensor Gather-and-Reduction (GnR)** 연산은 임베딩 테이블에서 벡터를 수집(element-wise sum 등)하는 과정으로, **메모리 대역폭에 의해 병목**됨
  - GnR의 compute-to-memory 비율이 극도로 낮음 (수 KB~MB의 DRAM 읽기 vs. 수십~수백 GB의 임베딩 테이블)
  - DLRM에서 하나의 GnR 연산은 일반적으로 **20~80개의 lookups**을 수행하며, 벡터 길이(vlen)는 **32~256**
- 기존 NDP(Near-Data Processing) 솔루션인 **TensorDIMM**과 **RecNMP**는 rank-level parallelism을 활용하여 성능 향상을 달성했으나, DRAM 데이터 경로의 **계층적 트리 구조**에 내재된 충분한 전송 대역폭을 완전히 활용하지 못함
  - TensorDIMM: vertical partitioning (vP) 사용 → vlen이 작을 때(32~64) DRAM 대역폭 낭비 발생, ACT 에너지가 **4배** 증가
  - RecNMP: horizontal partitioning (hP) 사용 → load imbalance 문제로 성능 **10~20%** 감소
  - 두 방식 모두 rank 수(Nrank)에 제한되어 내부 대역폭 활용에 한계

## 방법론

### 3.1. TRiM 기본 개념

- DRAM 데이터 경로는 트리 구조: Memory Controller (depth-0) → Rank (depth-1) → Bank-group (depth-2) → Bank (depth-3)
- 각 메모리 노드에 PE를 배치하면 해당 노드의 데이터 경로를 독립적으로 활용 가능 → 채널 버스를 사용하지 않아도 됨
- 내부 대역폭 = channel bandwidth × Nnode (메모리 노드 수)
- TRiM-R: rank당 1 PE → Nnode = Nrank (최대 4~8)
- TRiM-G: bank-group당 1 PE → Nnode = Nrank × 8 (최대 16~64)
- TRiM-B: bank당 1 PE → Nnode = Nrank × 32 (최대 128~256)
- TRiM-B는 가장 높은 병렬성을 제공하지만, DRAM 면적이 **4배 이상** 증가하여 TRiM-G가 최적의 설계점으로 선택

### 3.2. Two-stage C-instr Transfer Scheme

- **C-instr**: 85비트 명령어로 하나의 임베딩 벡터 look-up을 제어
  - target-address (34비트), weight (32비트), nRD (5비트), batch-tag (4비트), opcode (3비트), skewed-cycle (6비트), vector-transfer (1비트)
- **1단계**: MC에서 buffer chip까지 C/A + DQ 핀을 함께 사용하여 전송
  - DDR5에서 624비트/8사이클 = **78비트/cycle** 대역폭 활용 가능 (기존 C/A only 대비 5.6배)
- **2단계**: Buffer chip에서 DRAM chip까지 C/A 핀만 사용
  - Nrank개의 rank가 독립적으로 C-instr를 전송하므로 aggregate 대역폭이 Nrank배 증가
- DRAM 타이밍 제약(tRRD, tFAW)으로 인해 실제 요구 대역폭이 감소하여 2단계 전송으로 충분히 충족 가능

### 3.3. IPR 및 NPR 구조

- **IPR (In-memory-node PE for Reduction)**: bank-group 내부에 위치
  - 32비트 부동소수점 MAC(Multiply-Accumulate) 4개로 구성된 벡터 감소 유닛
  - C-instr 디코더 포함: C-instr를 ACT, RD, PRE 등의 DRAM 명령으로 변환
  - 각 bank의 read 데이터를 tCL 지연 후 누적
- **NPR (Near-memory-node PE for Reduction)**: buffer chip에 위치
  - 각 rank의 IPR로부터 부분 감소된 벡터를 수집하여 최종 감소 수행
  - C-instr 큐 포함: MC로부터 전송된 C-instr를 순차적으로 IPR에 전달
  - 벡터 전송 명령(RFU 명령 사용)을 통해 IPR→NPR간 부분합 전송 제어

### 3.4. Hot-entry Replication

- RecSys workload에서 임베딩 테이블의 접근 패턴이 **강한 skew**를 보임 (소수의 entry에 집중적 접근)
- 접근 빈도가 높은 hot entry들을 모든 bank-group에 복제
- 각 bank-group의 IPR이 동일한 hot entry에 접근할 때 동일한 부분합을 생성 → host에서의 중복 감소 비용 최소화
- load imbalance 완화: 기존 hP 방식의 불균형 문제를 추가 하드웨어 수정 없이 해결

### 3.5. 데이터 안정성

- TRiM의 읽기 전용(read-only) 특성을 활용한 데이터 안정성 확보 방안
- 기존 on-die ECC를 GnR 중에는 **검출 전용(detect-only)**으로 리퍼포징
- 기존 rank-level ECC는 NDP 구조에서 활용 불가하나, 읽기 전용 특성으로 인해 오류 검출만으로 충분

## 핵심 기여

- **핵심 Contribution**: DRAM 데이터 경로의 계층적 트리 구조를 활용한 NDP 아키텍처 TRiM을 제안하여, 기존 rank-level parallelism 기반 NDP 대비 최대 **3.9배** 성능 향상 달성
- **성능/에너지/면적 균형**: DDR5 기반 TRiM-G 최적 설계에서 **7.7배** speedup, **55%** 에너지 절감, **2.66%** 면적 오버헤드로 실용성 확보
- **Two-stage C-instr transfer**: DRAM 인터페이스를 크게 변경하지 않으면서 C/A 대역폭을 **5.6배** 증가시키는 실용적 방안 제시
- **Hot-entry replication**: RecSys workload의 특성을 활용한 load imbalance 해결 방안으로, 추가 하드웨어 수정 없이 기존 NDP 구조에 통합 가능
- **DRAM 읽기 전용 특성 활용**: on-die ECC를 detect-only로 리퍼포징하여 데이터 안정성 보장

## 주요 결과

| 항목 | 내용 |
|------|------|
| **시뮬레이터** | 기존 메모리 시뮬레이터 확장 |
| **기술 노드** | DRAM 기반 (DDR4/5) |
| **SRAM 셀** | IPR 내 32비트 MAC 4개 |
| **C-instr 크기** | 85비트 |
| **최대 주파수** | DDR5-4800 기준 |
| **면적 오버헤드** | DRAM 칩 대비 **2.66%** |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]


## 전체 요약

[[../paper-summaries/2021MICRO-summarize/trim-enhancing-processor-memory-interfaces-with-scalable-tensor-reduction-in-memory.md|전체 요약 보기]]
