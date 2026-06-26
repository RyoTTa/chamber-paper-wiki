---
tags: [paper, 2023, 2023ATC, topic/cache, topic/disaggregation, topic/dram, topic/gpu, topic/memory-tiering, topic/storage, topic/virtual-memory]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023ATC-summarize/atc23-yang-shao-peng.md"
---

# Overcoming the Memory Wall with CXL-Enabled SSDs

**Venue:** 
**저자:** 

## 개요

- NLP 모델 파라미터 수는 연 14.1× 증가하나 GPU 메모리 용량은 연 1.3× 증가에 그침 (Figure 1). GPT-3, MT-NLG, GShard 등 모델 크기(parameters)와 GPU memory(40GB→80GB) 격차가 **memory wall**로 심화.
- Flash memory(SSD)는 terabyte-scale density와 3D stacking/scaling으로 DRAM 대비 압도적 용량을 제공하나, 다음 3가지 근본적 challenge가 main memory로의 직접 사용을 가로막음:
  1. **Granularity mismatch**: 64B cache line flush → 16KiB flash page read-modify-write (read 16KiB, update 64B, program 16KiB to new location). Write amplification 극심.
  2. **Microsecond-level latency**: DRAM 46ns vs. ULL flash 3µs read / 100µs program / 1000µs erase (Table 1). Load/store instruction 기반 memory access에서 µs-level latency는 치명적.
  3. **Limited endurance**: SLC 100K, MLC 10K, TLC 3K program/erase cycles. Memory write traffic을 SSD처럼 OS page cache/buffering으로 흡수 불가.

- CXL Type 3 device는 load/store 기반 coherent memory access로 PCIe device의 host-managed device memory (HDM) 접근을 가능케 하여, flash를 CXL memory expansion device로 사용할 가능성 열림.
- Motivation: CXL + flash의 feasibility를 최초로 open-source in-depth study. Physical memory trace tool과 CXL-flash simulator를 개발하여 design space를 체계적으로 탐색.

## 방법론

### 1. Physical Memory Trace 수집 Tool

기존 도구(Valgrind Cachegrind)는 virtual address trace만 생성 → V2P mismatch로 prefetcher accuracy를 과대평가 (Table 3: virtual vs. physical trace 간 sub-µs latency error 최대 50.3%).

**Tool workflow (Figure 2):**
1. Valgrind로 application의 load/store instructions instrumentation → Cachegrind로 LLC miss/eviction만 filtering.
2. Kernel 수정: `do_anonymous_page()`, `do_set_pte()` 함수에서 page fault 시 VPN→PFN mapping을 `/proc` file system에 저장 (target PID 기준).
3. Virtual access trace + page table update log를 결합하여 **physical memory trace** 생성.

**검증:** 5개 synthetic workload (hash map, matrix multiply, min heap, random, stride)의 virtual vs. physical scatter plot 비교 (Figure 3). Virtual pattern은 예측 가능하나 physical pattern은 memory utilization, allocation order에 따라 동적으로 변화. 동일 workload도 run마다 physical access pattern이 상이 (Figure 3k-3o: CDF curves 불일치).

### 2. CXL-flash Hardware Architecture (Figure 4)

MQSim 기반 CXL-flash simulator 구현. 핵심 구성 요소:

- **DRAM Cache** (§4.1): 0~8GiB cache size 실험. Cache 없으면 queuing delay로 평균 latency 수백 µs. Cache는 성능 향상 + flash traffic 감소 dual 역할. 단, memory footprint가 cache보다 작아도 inter-arrival time이 짧으면(38ns~329ns, Table 2) flash backend saturation으로 평균 latency 여전히 DRAM 대비 높음. **Caching alone is insufficient.**

- **MSHR (Miss Status Holding Register)** (§4.2): Repeated reads (이미 fetch 중인 4KiB flash page에 대한 추가 64B miss) 방지. Synthetic workload에서 hash map/matrix multiply/min heap은 **90% 이상의 flash read가 repeated reads** (Figure 6). MSHR이 long-tail latency를 크게 감소 (Figure 7). Storage domain과 달리 CXL-flash에는 request merging software layer가 없으므로 hardware MSHR 필수.

- **Prefetcher** (§4.3): Next-N-line prefetcher (degree N, offset Y). Degree 증가 시 matrix multiply의 sub-µs request fraction 64%→76%로 개선되나 큰 degree는 cache pollution 유발 (Figure 8a). Offset은 workload-dependent: stride workload는 offset 증가에 비례 개선, random은 insensitive, hashmap/matrix multiply/min heap은 offset=16에서 peak (Figure 8b).

### 3. Flash Technology 및 Parallelism Sensitivity (§4.4)

- **Technology**: ULL vs SLC는 cache 존재 시 성능 차이 미미 (Figure 9a). MLC/TLC는 현저한 성능 저하. 수명: ULL/SLC는 1GiB+ cache로 4년+ 보장 (Figure 9b).
- **Parallelism**: 충분한 cache 시 8×4 parallelism도 충분 (Figure 10). Random workload는 cache size에 민감, stride workload는 parallelism에 민감.

## 핵심 기여

1. **CXL-enabled flash device로 memory wall 극복 가능성 입증**: 68~91% memory request가 sub-µs latency 달성, lifetime 3.1년+ (최소).
2. **Physical memory trace의 중요성 규명**: V2P address translation이 virtual trace 기반 평가를 크게 왜곡 (prefetcher accuracy 99%→42%).
3. **Hardware 설계 원칙**: DRAM cache + MSHR 조합 필수. CFLRU clean-first eviction이 write-intensive workload에서 효과적.
4. **Prefetcher 한계**: State-of-the-art prefetcher도 V2P translation으로 인한 physical address pattern obfuscation으로 3/5 workload에서 성능 저하 발생.
5. **Host-kernel cooperation 제안**: Kernel-level access pattern hint → HUM→hit 전환으로 추가 성능 향상 가능 (BERT: +5pp).
6. **Cost-effectiveness**: Performance-per-cost 기준 DRAM-only 대비 11~91× 우위.

## 주요 결과

5개 real workload: BERT (NLP), Page rank (Graph), Radiosity (HPC), XZ (SPEC), YCSB (KVS) — Table 5.

**Default config (Table 6):** 64MiB DRAM cache, 46ns DRAM latency, 8×8 flash parallelism, ULL flash.

#### 4.1 Cache Replacement Policies (§5.1)

4개 정책 실험: FIFO, Random (baseline), LRU, CFLRU (clean-first eviction). Set associativity 1/4/16.

- Associativity 증가 → 성능 향상 (miss penalty가 큰 환경에서 hit rate 증가 효과 지배적).
- **CFLRU 우수**: BERT/XZ/YCSB에서 write traffic 현저히 감소 (Figures 11-12) → sub-µs request fraction 증가. BERT: CFLRU 16-way → flash writes 0.7M only, sub-µs 84%.
- High locality workload (Radiosity: spatial locality 0.93, temporal 0.87)는 policy insensitive → sub-µs 83%+.
- Low locality + high write ratio workload (Page rank)는 최대 65% sub-µs에 그침.

#### 4.2 Prefetching Policies (§5.2)

5개 prefetcher 평가: NP (no prefetch), NL (Next-N-line), FD (Feedback-directed), BO (Best-offset), LP (Leap).

**Observation #1:** State-of-the-art prefetcher도 3개 workload(BERT, XZ, YCSB)에서 **성능 저하** 발생 (Figure 13a). BO prefetcher: Radiosity sub-µs 36% 증가, BERT는 감소.

**Observation #2:** 최악 Page rank에서도 lifetime **3.1년+** (Figure 13c). Radiosity는 403년.

**Observation #3:** Performance-per-cost: DRAM $5/GB vs NAND $0.05~0.30/GB → **11~91× benefit** (Figure 14). BO prefetcher + Radiosity workload 기준.

**Observation #4:** Prefetcher 성능 향상은 accuracy가 결정 — Leap: Radiosity 85% accuracy, BERT만 27% (Figure 15).

**Observation #5:** Low accuracy 시 cache pollution이 성능 저하 주원인. BO는 low accuracy 상황에서 prefetching disable로 pollution 최소화.

**Observation #6:** **V2P address translation이 prefetcher의 accuracy와 coverage를 크게 저하** (Figure 17). Page rank: virtual trace BO accuracy 99% → physical trace 42%. BERT: coverage 76%→26%.

**Observation #7:** Host kernel이 access pattern hints 제공 시 HUM→cache hit 전환으로 성능 향상 (Figure 18). BERT: top 10% intensively accessed addr에 10% hint chance → sub-µs 86%→91%.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/storage.md|Storage]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2023ATC-summarize/atc23-yang-shao-peng.md|전체 요약 보기]]
