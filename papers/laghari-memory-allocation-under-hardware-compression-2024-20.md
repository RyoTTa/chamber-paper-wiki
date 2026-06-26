---
tags: [paper, 2024, 2024MICRO, topic/cache, topic/compression, topic/dram, topic/virtual-memory]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024MICRO-summarize/memory-allocation-under-hardware-compression.md"
---

# Memory Allocation Under Hardware Compression

**Venue:** 
**저자:** 

## 개요

DRAM density scaling이 물리적으로 둔화됨에 따라, hardware memory compression을 통해 논리적 density를 확장하는 접근이 주목받고 있다. Meta 데이터센터의 평균 압축비는 3×에 달하며, 이미 hyperscale provider들(Meta, Google)은 OS memory compression을 사용 중이다.

그러나 **OS memory compression**은 compressed page 접근 시 costly page fault → OS가 page decompression을 위해 개입 → 데이터센터에서 전체 페이지의 5-20%만 압축 가능(cold pages에 국한). Hardware memory compression은 memory controller가 transparent하게 compression/decompression을 수행하여 이 한계를 극복한다.

**핵심 문제 — Memory Layer Decoupling:**
Hardware compression은 **physical memory**(OS 관리)와 **machine-physical memory**(실제 DRAM)를 분리한다. Memory controller는 각 physical page에 대해 압축률에 따라 가변적인 machine-physical memory를 소비한다. 이 새로운 machine-physical memory layer에는 자신만의 memory allocation interface가 존재하지 않아 두 가지 문제 발생:

1. **Imprecise allocation:** OS가 job에 S bytes의 machine-physical memory를 할당하려면 S·C의 physical memory를 할당해야 하지만, compression ratio C는 OS가 알 수 없고 제어할 수도 없음. Overestimate → 다른 job의 메모리 부족 유발, underestimate → 해당 job의 과도한 compression으로 성능 저하.
2. **Sometimes impossible:** 모든 virtual page에 physical page가 할당된 process(fully in-memory)에는 더 이상 physical page를 할당할 수 없으므로 machine-physical memory도 늘릴 수 없음.

**실제 영향 측정:** 24-core server (190GB DRAM), GraphBig (98GB RSS) + file-processing job (140GB file via mmap) collocation 실험.
- Precise allocation (DMU): Job 1이 안정적 성능 유지
- Imprecise allocation (without DMU): Job 1 평균 8× slowdown, 성능 변동폭 19-89%

## 방법론

### 1. 핵심 관찰: 모든 memory layer에는 specialized allocation interface가 필요

Virtual memory → malloc/mmap, Physical memory → page tables + MMU. Machine-physical memory만 전용 interface 부재 → 모든 문제의 근원.

### 2. Objective-based Allocation (vs Page-based Allocation)

**Traditional page-based allocation의 한계:**
- OS가 "어떤" machine-physical page를 할당할지 지정해야 함
- Memory controller가 transparent하게 compression → OS는 어떤 page가 free인지 모름
- Per-job free list 관리가 복잡 (64개 free list × job 수)

**DMU의 Objective-based Allocation:**
- OS는 "얼마나"(Total Allocation Objective)만 지정 — 64B control block에 단일 8B 필드로 기록
- Hardware는 자유롭게 data placement 결정 (어디에든 저장 가능)
- Page가 아닌 objective(bytes) 기반 → allocation이 O(1) 연산

### 3. DMU Architecture

**Control Blocks:** 각 C-job(Collectively-compressed Job)당 64B control block이 machine-physical memory 할당을 기록.
- **Total Allocation Objective (8B):** OS가 설정하는 정밀 할당 목표 (e.g., 19GB)
- **Unused Allocation (READ-ONLY):** 현재 할당량 중 실제 사용되지 않은 양. MC가 page compression 시 += freed bytes, expansion 시 -= used bytes.
- **Unused Allocation Objective:** OS가 "compress해서 추가 확보할 목표량" 지정 (best-effort)
- **Min Uncompressed Cache Objective:** 최소 uncompressed cache 크기 (e.g., 100MB → private L4 cache 효과)
- **#Accesses to Compressed Pages:** Host가 성능 영향 추정에 활용

**Implicit Control Block (CB 0):** 전체 DRAM을 초기 할당. Power-up 시 모든 physical page가 여기에 매핑. User job에 allocation 시 implicit block에서 차감, deallocation 시 반환.

**Recency Nodes:** 각 physical page의 recency node에 control block ID 필드 추가 → OS가 page allocation 시 해당 process의 control block ID를 기록.

**DMU Backend — Fan Structure (Figure 15):**
- **Blades:** Control block별 독립적인 MRU-LRU linked list (해당 C-job의 uncompressed physical page recency nodes)
- **Wheel:** Compression이 필요한 control blocks를 circular ring으로 연결
- **Scheduling:** Round-robin으로 ring을 순회하며 각 block의 LRU end에서 OS-configurable 개수의 page를 compression
- **Local recency ranking:** Global LRU 대신 per-job LRU → memory-intensive job이 다른 job을 과도하게 압축하는 것 방지

**Compressed Memory Fault:**
- Unused Allocation ＜ 0 → fault raise (interrupt)
- Fault handler: 해당 C-job의 값 spill out + Cgroup memory.limit cap
- "Grace amount" (e.g., 10MB) 할당 후 retry → 두 번째 fault에서만 job pause
- Page-based allocation과 달리 빠른 bulk allocation 가능 → 대부분 첫 fault만으로 해결

## 핵심 기여

1. Hardware memory compression이 decouple하는 **machine-physical memory layer**에는 전용 allocation interface가 필요 — 기존 physical memory allocation interface를 재사용하면 imprecise allocation, impossible allocation 문제 발생.
2. **Objective-based allocation**은 page-based allocation의 한계를 극복: OS는 "얼마나"만 지정, hardware는 자유롭게 배치. O(1) arithmetic operation으로 bulk allocation 가능.
3. **DMU**는 MMU에 대응되는 새로운 hardware unit — per-job recency ranking(fan structure)으로 job 간 compression interference 제거.
4. FPGA prototype 입증: collocation 시 1-2% 성능 변동만 발생 vs without DMU 19-89% 변동.
5. 소프트웨어 오버헤드 1.3%, 하드웨어 오버헤드 0.035mm² @ 7nm — 실용적.

## 주요 결과

1. **Total Allocation Objective:** 가장 엄격. 위반 시 compressed memory fault.
2. **Unused Allocation Objective:** Best-effort target. DMU가 background에서 지속적으로 compression 수행하여 목표 달성 시도.
3. **Min Uncompressed Cache Objective:** 최소 uncompressed page 수 보장. Hot page는 uncompressed로 유지.

## 평가

### Methodology

- **Prototype:** Genesys 2 Kintex-7 FPGA, RISC-V softcore 2개, Linux boot
- **Memory:** 1GB DRAM onboard, 4× logical capacity (3979736 KB)
- **Baseline:** TMCC (recency-aware hardware compression) + IBM MXT-style out-of-memory interrupts
- **Compression:** LZ portion of ASIC Deflate Verilog (FPGA 크기 제약)
- **Workloads:** GAP benchmarks (SSSP 등) + SPEC CPU2006 Integer + file-processing job

### Performance Variation Under Collocation

| Collocation Scenario | With DMU | Without DMU |
|---------------------|----------|-------------|
| Small file-processing job | 100% (reference) | - |
| Medium file-processing job (800MB) | 99% (GAP avg) | 81% |
| Large file-processing job (2GB) | 98% (GAP avg) | 11% |

SPEC CPU2006 Integer (280MB allocation):
- Medium job: 98% (DMU) vs 87% (without)
- Large job: 97% (DMU) vs 42% (without)

Without DMU의 문제 원인: TMCC baseline은 global recency ranking → Job 1이 덜 memory-intensive → 과도한 compression → swap out까지 발생.

**#Accesses to Compressed Pages:** DMU 사용 시 reference execution과 noise range(2.5%) 이내로 유지 → compression degree 일관성 입증.

### Overheads

**Software Overhead:** Kernel modification (page allocation/free 시 control block ID 기록/삭제) → x86 Linux Server 측정 결과 평균 1.3% overhead, worst 3%.

**Hardware Overhead:** DMU + recency-aware compression 합성 결과 (Synopsys, 7nm):
- Area: 0.035mm²
- Frequency: 3GHz (ASIC compressor/decompressor 제외)

## 구현

- **FPGA Platform:** OpenPiton RISC-V framework, Genesys 2 Kintex-7
- **Kernel Module:** Machine-physical Memory Module (MPM) — loadable kernel module, 17 lines kernel code 추가
- **Linux Version:** Kernel with ZSMalloc integration
- **Video Demo:** https://youtu.be/-1JG3JnIY3U
- **ASIC Synthesis:** 7nm process node, Synopsys tools

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2024MICRO-summarize/memory-allocation-under-hardware-compression.md|전체 요약 보기]]
