---
tags: [paper, 2024, 2024ISCA, topic/cache, topic/disaggregation, topic/dram, topic/nvm, topic/virtual-memory]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024ISCA-summarize/mc-2-lazy-memcopy-at-the-memory-controller.md"
---

# (MC)²: Lazy MemCopy at the Memory Controller

**Venue:** 
**저자:** Aditya K. Kamath, Simon Peter (University of Washington)

## 개요

### 1.1 Memory Copy의 실질적 비용

Google 데이터센터 프로파일링 결과, 전체 CPU cycle의 **5% 이상**이 `memcpy`/`memmove` 연산에 소비된다. 이 중 대부분은 memory stall에 의한 것으로, CPU reorder buffer(ROB)가 memory access latency에 blocking되어 추가 instruction 발행이 중단된다. 저자들의 측정(Fig. 3)에서 Protobuf workload의 memcpy 동안:
- **25%+** data access가 cache miss → memory service 필요
- **90%+** 시간 동안 최소 1개 instruction이 memory 대기
- **60%+** cycle은 CPU가 완전히 stalled

DDR5는 DDR4 대비 bandwidth는 2배 향상되었으나 latency는 소폭 증가. 미래 CXL-attached DRAM/NVM으로 memory latency는 더 악화될 전망.

### 1.2 memcpy 사용 패턴 분석

핵심 관찰: 많은 memcpy 사용처에서 **복사된 데이터의 일부만 실제 접근/수정**된다:

| Use Case | 복사 오버헤드 | 접근 비율 |
|----------|-------------|----------|
| **Protobuf** (Google Fleetbench) | cycles의 68% | Serialize/deserialize 시 buffer 전체 복사 후 일부만 변환 |
| **MongoDB** (IO buffers) | 상당 | Indexing tree + log 복사, 일부 필드만 수정 |
| **Cicada (MVCC)** | write 시 tuple 복사 | TPC-C 워크로드: tuple의 1~2%만 update |
| **fork + COW** | huge page fault 시 99% | 2MB page 전체 복사 후 수~수십 바이트만 수정 |

또한 Protobuf memcpy 크기 분포(Fig. 4)에서 **56%가 1KB 이하**. 기존 OS 기반 회피 기법(zIO)은 page(≥4KB) 단위로만 동작하므로 대부분의 복사에 적용 불가.

### 1.3 기존 접근법의 한계

- **Zero-copy API (Demikernel 등):** 프로그램 재설계 필요, fine-grained ownership tracking 복잡
- **zIO [Stamler+, OSDI'23]:** page table entry를 copy-on-access로 마킹 → userfaultfd로 page fault 시 복사. Page remapping/TLB shootdown 오버헤드로 **16KB 미만 복사는 오히려 성능 저하**. Page fault 기반이므로 접근 시 penalty 큼.
- **DMA engine:** 초기화 오버헤드가 커서 작은 복사에 부적합 (수십 μs 수준)
- **Cache-based accelerator:** Source가 cache에 있을 때만 효과적

## 방법론

### 3.1 방법론

| 항목 | 구성 |
|------|------|
| **Simulator** | gem5 v22.1 |
| **CPU** | 8-core OoO, 4 GHz |
| **L1 Cache** | 64 KB/CPU, stride prefetcher |
| **Shared L2** | 2 MB, stride prefetcher |
| **DRAM** | 3 GB, DDR4, 2 channels |
| **CTT** | 2,048 entries, 0.79 ns latency |
| **BPQ** | 8 entries |
| **OS** | Linux 5.7.0, Ubuntu 20.04 |
| **Baselines** | Native memcpy, zIO |

### 3.2 Microbenchmark: Copy Latency (Fig. 10)

Uncached source buffer 기준:

| Copy Size | (MC)² | zIO | Speedup vs memcpy |
|-----------|-------|-----|-------------------|
| 64B (1 CL) | - | - | (MC)² no benefit (overhead > gain) |
| 1KB | - | page fault | (MC)² **55% faster** |
| 16KB+ | - | worse than memcpy | (MC)² **11× faster** |
| 4MB | - | 23× | (MC)² ~similar to zIO |

zIO는 page 단위 미만 size에서 elision 불가 → 16KB까지 memcpy보다 오히려 느림.

**Cached source buffer:** (MC)²는 16KB 이상에서 cached memcpy와 유사한 latency → source cache 여부와 무관하게 일관된 성능 제공.

### 3.3 Overhead Breakdown (Fig. 11)

memcpy_lazy의 주요 오버헤드:
- **Cacheline writeback (CLWB):** 1KB 이하에서는 parallel issue로 영향 미미. 1KB+에서는 load/store queue + ROB saturation으로 serialize.
- **MCLAZY packet 전송:** Parallel로 진행되어 영향 적음
- **개선 여지:** Full-cache writeback(INVD 유사) 도입 시 copy size 무관하게 fixed overhead 가능

### 3.4 Sequential Destination Access (Fig. 12)

4MB source→destination copy 후 destination을 sequential read:

| Access % | (MC)² runtime | zIO runtime |
|----------|-------------|-------------|
| 0% (no access) | ~70% | **~30%** |
| 25% | ~60% | ~100% |
| 50% | ~65% | ~140% |
| 100% | **~80%** | ~160% |

(MC)²는 모든 access proportion에서 memcpy보다 우수 (prefetcher가 bounce latency 은닉). zIO는 50%+ access 시 page fault overhead로 memcpy보다 열화. Source-destination aligned 시 (MC)² runtime 최대 **57%** (bounce 1회).

### 3.5 Random Destination Access (Fig. 13)

Pointer-chasing으로 prefetch 불가능한 random access:

| Access % | (MC)² runtime | zIO runtime |
|----------|-------------|-------------|
| 12.5% | **~92%** | ~210% |
| 100% | ~92% | ~130% |

(MC)²의 writeback optimization (완료된 destination을 memory write)이 핵심 → 없으면 runtime 최대 1.6×. Aligned 시 최대 88%.

### 3.6 Application Workloads

| Workload | (MC)² Improvement |
|----------|------------------|
| **Protobuf** (Google Fleetbench) | **43% runtime reduction** (Fig. 14) |
| **MongoDB** (YCSB load, 100KB fields) | **15.5% lower insertion latency** (Fig. 15) |
| **Cicada MVCC** (RMW, ≤25% update) | **Up to 78% higher throughput** (Fig. 16) |
| **Cicada MVCC** (write-only, non-temporal) | 모든 write fraction에서 baseline 능가 (Fig. 17) |

zIO는 Protobuf에서 모든 memcpy가 sub-page → elision 불가. MongoDB에서 insert latency 9.7% 악화 (page fault overhead).

### 3.7 OS-level Improvements

| Operation | (MC)² Improvement |
|-----------|------------------|
| **Huge page COW fault** (2MB) | **250× lower latency spike** (Fig. 18) |
| **Linux pipe transfer** (>16KB) | **~2× throughput** (Fig. 19) |

Huge page COW: Native kernel이 455× latency spike 발생, (MC)²는 최대 2×. 이는 in-memory database가 huge page를 기피하는 문제를 해결.

### 3.8 Sensitivity Studies

**CTT entries + copy threshold (Fig. 20):** 1,024~2,048 entries, 30~90% threshold에서 Protobuf 성능 차이 <5%. 2,048 entries + 50% threshold에서 CPU stall 없이 compact.

**BPQ size (Fig. 21):** 1→2 entries: 35% speedup. 8→16 entries: 추가 2%로 diminishing returns. **8 entries로 충분.**

**Scalability (Fig. 22):** 8 threads 이상에서 CTT parallel free 없으면 stall 발생. Parallel free로 memory bandwidth proportional하게 확장 가능.

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

| 항목 | 세부사항 |
|------|---------|
| **CTT** | 2,048 entries × 16B = 32KB SRAM/MC |
| **CTT area** | 0.14 mm² (22nm), I/O die (~100mm²) 대비 0.14% |
| **BPQ** | 8 entries, WPQ에 추가 |
| **Interface** | MCLAZY + MCFREE 2개 instruction |
| **Software** | memcpy_lazy() + copy_interpose.so (LD_PRELOAD) |
| **Kernel mods** | copy_user_huge_page, pipe_write/read |
| **Source code** | https://github.com/AKKamath/MCSquare-ISCA24 |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2024ISCA-summarize/mc-2-lazy-memcopy-at-the-memory-controller.md|전체 요약 보기]]
