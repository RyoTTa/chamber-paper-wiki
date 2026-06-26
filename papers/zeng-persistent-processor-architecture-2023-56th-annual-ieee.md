---
tags: [paper, 2023, 2023MICRO, topic/cache, topic/dram, topic/nvm, topic/security]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023MICRO-summarize/persistent-processor-architecture.md"
---

# Persistent Processor Architecture

**Venue:** 
**저자:** 

## 개요

### 1.1 NVM과 Whole-System Persistence의 도전

비휘발성 메모리(NVM: ReRAM, 3D XPoint, PCM, STT-MRAM)는 byte-addressable, 고밀도, in-memory persistence를 제공하나, 투명한 whole-system persistence(WSP) 달성은 어려움:

- **Intel Optane PMEM memory mode:** DRAM이 LLC로 PMEM 위에 위치하지만, PMEM은 volatile로 동작 — crash consistency 유지가 어렵기 때문.
- **App-direct mode (PSP):** 프로그래머가 persistent data structure, crash consistency, application-specific recovery code를 직접 작성해야 함. Undo/redo logging + clwb/sfence로 인한 성능 저하.
- **eADR (Intel):** 정전 시 전체 cache 내용을 PMEM으로 flush — 3400 mm³ supercapacitor 필요, large DRAM cache(1TB+)에서는 실용 불가.

### 1.2 핵심 관찰

Crash inconsistency의 근본 원인: committed store의 program order와 cache block이 NVM에 writeback되는 순서 간 불일치. 즉, younger store가 먼저 persist되고 older store는 cache에 남아 정전 시 소실됨.

**해법:** 정전 후 모든 committed store를 replay하면 inconsistency 교정 가능. 이를 위해 store register가 overwrite되지 않도록 보존(**store integrity**)하고, 정전 시 register를 checkpoint하여 복구 시 재실행.

### 1.3 ReplayCache의 한계

Compiler 기반 store integrity + region-level persistence (ReplayCache, 2022)는 server-class core에서 5× 평균 slowdown (Figure 1). 원인:
1. Compiler 분석 한계로 **region이 평균 12 instructions로 너무 짧음** — persistence latency를 ILP로 가리지 못함.
2. 매 store마다 clwb 삽입 → instruction count 2배, store queue pressure.

---

## 방법론

### 3.1 방법론 개요

| 항목 | 내용 |
|---|---|
| **Simulator** | gem5 cycle-accurate, full-system mode |
| **Processor** | 8-core x86_64 Skylake-X, 2GHz, 4-width OoO |
| **PRF** | 180 integer + 168 floating-point physical registers |
| **Cache** | L1I 32KB / L1D 32KB / L2 64KB / DRAM cache 4GB direct-mapped |
| **PMEM** | 32GB, Read 175ns / Write 90ns, 16-entry WPQ, 2.3GB/s bandwidth |
| **CSQ** | 40-entry FIFO |
| **Benchmarks** | 41개: SPEC CPU2006/2017, SPLASH3, STAMP, WHISPER, DOE Mini-apps |
| **Baseline** | PMEM memory mode (non-persistent), original binaries |
| **비교 대상** | Capri (SOTA WSP), ReplayCache, eADR/BBB (ideal PSP) |

### 3.2 성능 결과

**PPA vs Baseline (Figure 8):**
- 전체 평균 **2% run-time overhead** (Capri: 26%).
- WHISPER의 rb: 8.1% overhead (높은 NVM write traffic).
- 대부분의 benchmark: 1~3% 범위.

**PPA vs eADR/BBB (Ideal PSP, Figure 10):**
- High L2 miss rate applications(18~100%): PPA 3% vs BBB/eADR **1.39× 평균, 최대 2.4×** (libquantum).
- PPA는 DRAM cache 활용 → PMEM latency hiding.

**PPA vs DRAM-only system (Figure 9):**
- PPA의 persistent system은 DRAM-only 대비 16% 느림 — PMEM memory mode 자체의 overhead 14%와 유사.

### 3.3 Stall Cycle 분석 (Figure 11)

Region 경계에서 pipeline stall 비율: 평균 **3% 미만.** Region이 충분히 길어(평균 319 instructions) persistence latency가 완전히 overlap됨.

### 3.4 Region 크기 분석 (Figure 13)

- 평균 region: **301개 other instructions + 18개 store instructions**
- Capri: 평균 29 instructions (11배 차이)
- bzip2, libquantum 등 register-heavy workload는 region이 작음

### 3.5 Deep Cache Hierarchy 민감도 (Figure 14)

L3 cache(16MB, 44-cycle)를 DRAM cache 위에 추가해도 PPA overhead: **1%** — 여전히 region이 persistence latency를 흡수.

### 3.6 WPQ Size 민감도 (Section 7.7)

WPQ 8/16/24 entries 비교: PPA slowdown 변화 미미 — asynchronous writeback이 queue pressure를 효과적으로 분산.

### 3.7 PRF 압력 분석 (Figure 5)

Free register CDF: 75% cycle에서 138개 integer / 110개 FP register가 미사용 → PPA의 충분한 region length 보장.

---

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1 추가 하드웨어 구조

| Component | 크기/비용 |
|---|---|
| MaskReg | PRF 크기 bit vector (180+168 = 348 bits) |
| CSQ | 40-entry FIFO (각 entry: 8B index + 8B addr) |
| LCPC | 1 register (8B) |
| JIT Checkpointing Controller | 수백 logic gates |
| Capacitor | **21.7 μJ** (eADR: 550 mJ, 25,000배 차이) |

### 4.2 소프트웨어

- Clang/LLVM 13.0.1, -O3, static linking
- Ubuntu 18.04, Linux Kernel 5.4.46
- No source code modification, no recompilation 필요 (legacy binary 지원)

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/security.md|Security]]


## 전체 요약

[[../paper-summaries/2023MICRO-summarize/persistent-processor-architecture.md|전체 요약 보기]]
