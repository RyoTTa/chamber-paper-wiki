---
tags: [paper, 2025, 2025ASPLOS, topic/dram, topic/llm-inference, topic/storage, topic/virtual-memory]
venue: ""
year: 2025
summary_path: "../paper-summaries/2025ASPLOS-summarize/virtuoso-enabling-fast-and-accurate-virtual-memory-research-via-an-imitation-based-operating-system-simulation-methodology.md"
---

# Virtuoso: Enabling Fast and Accurate Virtual Memory Research via an Imitation-based Operating System Simulation Methodology

**Venue:** 
**저자:** 

## 개요

### 1.1 Virtual Memory의 성능 병목

VM은 현대 컴퓨팅 시스템의 핵심 추상화이나, 데이터 집약적 workload의 등장으로 주요 성능 병목이 되었다:
- **Long-running workload (>100s):** Address translation이 총 실행 시간의 평균 **25%** (최대 40%) 차지 (Figure 1). GraphBIG, HPCC, XSBench 등의 불규칙 메모리 접근 패턴이 원인.
- **Short-running workload (<1s):** Physical memory allocation이 총 실행 시간의 평균 **32%** (최대 95%). Function-as-a-Service, LLM inference 등의 짧은 수명이 allocation overhead를 amortize하지 못함.

### 1.2 기존 시뮬레이션 방법론의 한계

VM 연구는 HW/OS co-design이 필수적이지만, 평가 인프라가 이를 따라가지 못함.

| 유형 | 예시 | OS 모델링 | 속도 | 정확도 | 개발 난이도 |
|------|------|----------|------|--------|-----------|
| **Emulation-based** | Sniper, ChampSim, Ramulator2 | First-order approximation (고정 latency) | Fast | **Low** | Low |
| **Full-system** | gem5-FS, QFlex | Real OS kernel | **Slow** | Very High | **High** |

**Emulation-based의 문제:** VM overhead는 workload와 system state에 따라 극심한 variability를 보이므로 고정 latency로 모델링 불가:
- Minor page fault latency: THP enabled 시 평균 2.2µs, 표준편차 >50µs. Outlier (>10µs)가 총 latency의 67% 차지 (Figure 2).
- PTW latency: workload에 따라 39 cycles (I/O-heavy)에서 >180 cycles (SSSP)까지 변동 (Figure 3).
- Baseline Sniper (fixed PTW latency)는 real system 대비 IPC 오차 **35%** (§7.2).

**Full-system의 문제:** gem5-FS는 gem5-SE 대비 simulation time **77%** 증가, memory 사용량 **1.69×** 증가 (§7.3). Production OS 커널 수정과 검증은 비전문가에게 진입 장벽이 높음.

## 방법론

| Simulator | 유형 | 통합 방식 |
|-----------|------|----------|
| **Sniper** | Execution-driven | Dynamic instrumentation → instruction stream을 core model에 직접 주입 |
| **ChampSim** | Trace-based | Application trace + MimicOS instruction trace를 core model이 동적 전환 |
| **Ramulator2** | Trace-based (memory-only) | MimicOS instruction trace를 offline pre-processing 후 ChampSim format으로 변환 |
| **gem5-SE** | Emulation-based | 기존 emulation tool 재사용하여 MimicOS instruction stream을 core model에 주입 |
| **MQSim** | SSD simulator | I/O-intensive workload의 page fault → swap-in/out latency 정확한 모델링 |

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1 Methodology

| 항목 | 내용 |
|------|------|
| Baseline Simulator | Sniper (Virtuoso 통합 버전) |
| Real System (Validation) | Intel Xeon Gold 6226R 2.90GHz, 256GB DDR4-2400, Linux 5.15.0-60 |
| Simulated Core | 4-way OoO x86 2.9GHz |
| MMU | L1 I-TLB 128-entry, L1 D-TLB 64-entry (4KB) + 32-entry (2MB), L2 TLB 2048-entry, 3 PWCs |
| Cache | L1I/D 32KB, L2 2MB, L3 2MB/core |
| MimicOS Config | Linux-like THP (4KB+2MB), HugeTLBFS, 4GB swap, 80% baseline fragmentation |
| Workloads | Long-running: GraphBIG, HPCC, XSBench; Short-running: FaaS, LLM inference (Llama/Bagel/Mistral), Image processing |

### 4.2 Accuracy Validation (§7.2)

- **IPC accuracy:** Virtuoso+Sniper **80%** vs baseline Sniper **66%** → **21% improvement** (Figure 8). Virtuoso는 workload별 동적 PTW latency 변화를 반영.
- **L2 TLB MPKI accuracy:** **82%** (vs real system)
- **PTW latency accuracy:** **85%**
- **Page fault latency:** Cosine similarity 기준 최대 **0.93** (1.0 = 완전 일치). THP enabled/disabled 모두에서 **66-79%** accuracy (Figure 9).

### 4.3 Simulation Time Overhead (§7.3)

| Simulator | MimicOS overhead | Memory overhead |
|-----------|-----------------|-----------------|
| Sniper | **35%** | 2.08× (0.8GB) |
| ChampSim | **28%** | 2.28× |
| Ramulator2 | **2%** | 1.02× |
| gem5-SE | **13%** | 1.45× |
| **Average** | **20%** | 1.45× |

- gem5-FS (full-system) 대비 MimicOS 사용 시 **49% faster** simulation.
- Memory 사용량: MimicOS+Sniper 0.8GB vs gem5-FS 1.6GB → **2×** lower.
- Simulation time은 MimicOS instruction 수와 strong correlation (1.5× factor, Figure 12).

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/storage.md|Storage]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2025ASPLOS-summarize/virtuoso-enabling-fast-and-accurate-virtual-memory-research-via-an-imitation-based-operating-system-simulation-methodology.md|전체 요약 보기]]
