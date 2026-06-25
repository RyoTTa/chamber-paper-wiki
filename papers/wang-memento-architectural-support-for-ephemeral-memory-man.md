---
tags: [paper, 2023, 2023MICRO, topic/dram, topic/virtual-memory]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023MICRO-summarize/memento-architectural-support-for-ephemeral-memory-management-in-serverless-environments.md"
---

# Memento: Architectural Support for Ephemeral Memory Management in Serverless Environments

**Venue:** 
**저자:** 

## 개요

### 1.1 Serverless에서 Memory Management의 비용

Serverless computing은 fine-grained pay-for-what-you-use billing으로 인기를 얻고 있으나, **short-lived function execution** 모델이 memory management에 새로운 과제를 제기. Function은 수명이 짧아 memory allocation/deallocation 비용을 amortize할 기회가 없이 userspace와 kernel 양쪽에서 **full critical-path cost**를 지불.

### 1.2 상세 분석 결과 (Section 2.2)

저자들은 Python, C++, Golang의 14개 function + 4개 data processing application + 3개 serverless platform operation을 분석:

**Allocation 크기 (Figure 2):**
- 93%의 allocation이 **512 bytes 미만** (Data proc: 98%, Serverless platform: 99%)
- Python workloads: small allocations >98%

**Object Lifetime (Figure 3, Table 1):**
- Bimodal 분포: 71%는 **short-lived** (동일 size class 16개 allocation 내에 freed), 27%는 **long-lived** (function exit 시 batch-freed)
- Combined: 61% small+short-lived, 32% small+long-lived
- 언어별 차이: C++는 대부분 short-lived, Python은 long-lived 비중 높음, Golang은 GC 미호출로 대부분 long-lived

**Kernel 영향 (Table 2):**
- Python: memory management의 **52%가 kernel** (page fault, mmap/munmap)
- Golang: 46% kernel
- C++: 96% userspace (작은 heap working set)
- Data processing: 62% kernel

### 1.3 Design Implications

1. Small + varying size classes (≤512B)에 최적화 필요.
2. Short-lived object의 강한 allocation metadata locality를 활용.
3. Userspace + kernel **양쪽 모두** 최적화해야 함 — 어느 한쪽만 해결하면 최대 52% overhead 잔존.

---

## 방법론

### 3.1 방법론 개요

| 항목 | 내용 |
|---|---|
| **Simulator** | QEMU + SST + DRAMSim3 full-system |
| **CPU** | 4-issue OoO, 3GHz, 256-entry ROB, 64-entry LSQ |
| **Cache** | L1I 32KB / L1D 32KB / L2 256KB / LLC 2MB slice, 16-way |
| **DRAM** | 64GB DDR4-3200, 16 banks |
| **HOT** | 3.4KB direct-mapped, 2-cycle, 1.32mW, 0.0084mm² |
| **AAC** | 32-entry direct-mapped, 1-cycle, 0.43mW, 0.0023mm² |
| **OS** | Ubuntu 20.04, Linux 5.18 |
| **Benchmarks** | 14개 function (FunctionBench, SeBS, pyperformance, DeathStarBench) + 4개 data processing (Redis, Memcached, Silo, SQLite3) + OpenFaaS platform ops |
| **Languages** | Python (CPython 3.8), C++ (jemalloc), Golang (go-1.13) |

### 3.2 Speedup (Figure 8, 9)

**Functions 평균: 16% speedup (8~28%)**
- Python: 8~28% (html: 28%, bfs: 25%)
- C++ (DeathStarBench): 평균 16%
- Golang: 8~15%

**Speedup breakdown (Figure 9):**
- obj-alloc: 33%
- obj-free: 32%
- page-mgmt: 33%
- bypass: 2% (최대 17%)

**Data processing: 5~11%** (Redis 11%, Silo 7.5%, Memcached 6.5%, SQLite3 5%)

**Serverless platform ops: 4~7%**

### 3.3 Memory Bandwidth (Figure 10)

평균 **30% main memory traffic 감소**.
- 일부 workload(UM, CM): 31~35% 감소
- Data processing: 33% 감소

### 3.4 Aggregate Memory Usage (Figure 11)

- Functions: **15% 감소** (userspace 10%, kernel 28%)
- Data processing: **23% 감소** (userspace 5%, kernel 50%)
- Python/Golang: userspace는 약간 증가(shared free page 미구현으로 인한 fragmentation)하나 kernel 29% 감소로 상쇄

### 3.5 Function Pricing (Figure 14)

AWS Lambda pricing 모델 기반: **29% runtime cost 절감**. End-to-end 포함 시 11~31%.

### 3.6 Characterizing Memento

- **HOT hit rate (Figure 12):** Alloc 99.8%, Free 83% (Python의 interpreter-level long-lived object로 낮음). C++/Golang은 매우 높음.
- **Arena list ops (Figure 13):** <1% allocations, <0.6% frees.
- **Fragmentation:** 3.68% 평균 internal fragmentation — software allocator 대비 ±2%.

### 3.7 Sensitivity Studies (Section 6.6)

- **MAP_POPULATE (eager page allocation):** Golang 3% 성능 향상 but physical memory 8.6× 증가 → 비경제적.
- **Multi-process:** HOT flush overhead는 context switch (μs) + 빈도(수 ms) 대비 negligible.
- **Cold-start:** Cold start 환경에서도 7~22% speedup 유지.

### 3.8 Mallacc 비교 (Section 6.7)

Idealized Mallacc(always hit, zero latency): 8% speedup (C++ only). **Memento: 16%** (동일 workload, 2배). Memento는 Python/Golang도 지원하며 kernel management도 해결 — Mallacc는 userspace-only.

---

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1 하드웨어 추가 비용

| Component | Spec | Area | Power |
|---|---|---|---|
| HOT | 3.4KB, 64-entry direct-mapped | 0.0084mm² | 1.32mW |
| AAC | 32-entry direct-mapped | 0.0023mm² | 0.43mW |
| Total | — | **0.0107mm²** | **1.75mW** |

22nm technology node, CACTI 6.5 기반 추정.

### 4.2 소프트웨어 통합

- ISA extension: `obj-alloc`, `obj-free` — 2개 instruction 추가
- malloc에서 size ≤512B 확인 → Memento 사용, 초과 → 기존 software path
- GC runtime(Python reference counting, Golang mark-and-sweep)과 자연스럽게 통합 — GC가 free 시 obj-free 호출

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2023MICRO-summarize/memento-architectural-support-for-ephemeral-memory-management-in-serverless-environments.md|전체 요약 보기]]
