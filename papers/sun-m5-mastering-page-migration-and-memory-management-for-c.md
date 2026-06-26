---
tags: [paper, 2025, 2025ASPLOS, topic/cache, topic/disaggregation, topic/dram, topic/memory-tiering, topic/near-data-processing, topic/virtual-memory]
venue: "ASPLOS 2025 (Volume 2)"
year: 2025
summary_path: "../paper-summaries/2025ASPLOS-summarize/m5-mastering-page-migration-and-memory-management-for-cxl-based-tiered-memory-systems.md"
---

# M5: Mastering Page Migration and Memory Management for CXL-based Tiered Memory Systems

**Venue:** ASPLOS 2025 (Volume 2)
**저자:** Yan Sun, Jongyul Kim, Zeduo Yu, Jiyuan Zhang, Tianyin Xu, Nam Sung Kim (UIUC), Hwayong Nam, Jaehyun Park, Eojin Na, Jung Ho Ahn (SNU), Yifan Yuan, Ren Wang (Intel Labs), Siyuan Chai, Michael Jaemin Kim

## 개요

CXL은 PCIe 기반의 memory interface로, DDR5 대비 3배 적은 pin으로 동일 bandwidth 제공 (PCIe 5.0 x16 = 32GB/s). 그러나 CXL DRAM access latency는 DDR DRAM보다 **140–170 ns 더 높아** tiered-memory system을 형성하며, 빈번한 CXL DRAM 접근을 최소화하기 위한 page-migration solution이 필수적임.

**기존 CPU-driven page migration의 3가지 접근법과 한계 (§2.1):**

| 접근법 | 메커니즘 | 대표 사례 | 한계 |
|---|---|---|---|
| Hinting Page Fault | PTE present bit reset → TLB invalidate → soft page fault 시 migration | ANB [5], TPP [42] | TLB invalidate + page fault handling에 막대한 CPU cycle 소모 (Redis p99 latency 34% 증가) |
| PTE Scanning | 주기적으로 모든 slow-memory PTE scan → access bit 확인 | DAMON [48] | Access bit은 Boolean — 횟수 불명. Epoch마다 대량의 CPU cycle 소모 (Redis p99 latency 39% 증가) |
| Address Sampling | PEBS로 LLC miss address sampling → frequency 기반 hot page 추정 | Memtis [31] | CXL memory에 대한 PEBS 미지원 (Intel 한계). Sampling rate ↑ → overhead ↑ |

공통적 한계: **warm page를 hot page로 오판**, **sparse page 감지 불가**, 그리고 hot page 식별 자체의 **성능 overhead**가 때로는 migration 이득을 상쇄함.

## CXL-driven Profiling: PAC & WAC (§3)

M5는 CXL controller의 near-memory processing 능력을 활용한 hardware access counter를 제안.

### Page Access Counter (PAC)
- **위치:** CXL controller의 AFU(Accelerated Function Unit)에 구현 (Figure 2).
- **구조:** Address-to-PFN converter → 4MB SRAM (PFN-indexed 16-bit counter) → adder/controller.
- **동작:** CXL IP에서 MC로 가는 모든 memory access address를 snoop → PA[47:6]을 6-bit right shift하여 PFN 획득 → 해당 PFN의 SRAM counter increment.
- **Capacity:** 4MB SRAM으로 1M page counter (16-bit each) → 최대 4GB CXL DRAM 커버. Scalability: SRAM을 cache로 사용하거나 주기적 flush to host/device memory.

### Word Access Counter (WAC)
- PAC와 동일 아키텍처, PFN 변환 없이 word address 그대로 사용.
- 128MB memory region 단위로 monitoring.

### Software Interface
- MMIO(CXL.io)로 SRAM 접근. 2MB MMIO window → 1MB data + 1MB config register.
- Base address register로 4MB SRAM을 4개 1MB window로 분할 접근.

### 핵심 차별점
PEBS와 달리 **모든** DRAM access address를 counting — precise profiling 가능. Dynamic binary instrumentation(Pin)보다 훨씬 transparent.

## Analysis: CPU-driven Solutions Considered Harmful (§4)

PAC/WAC을 이용한 정밀 profiling으로 밝혀낸 사실들:

### Observation 1: Warm pages misidentified as hot (Figure 3)

12개 memory-intensive benchmark에 대해 ANB와 DAMON이 식별한 hot page의 access count를 PAC의 true top-K hot page와 비교:
- **ANB:** true hot pages access count의 평균 **21%** 수준 (0.21 access-count ratio)
- **DAMON:** 평균 **29%** 수준
- 대부분 benchmark에서 access-count ratio < 0.4 → **CPU-driven solution이 식별하는 "hot" page는 실제 hot page의 1/3~1/5 수준.**

### Observation 2: Sparse pages prevalent in key workloads (Figure 4)

WAC으로 page 내 접근되는 unique 64B word 수 측정 (4KB page = 64 words):
- **Redis:** 페이지의 **86%**가 16개 이하 word만 접근 (≤25% sparsity)
- **Memcached:** 76% / **CacheLib:** 74%
- **SPEC CPU 2017:** 대부분 densely accessed (87–92% 페이지에서 ≥75% word 접근)
- **GAP benchmark:** BC, BFS, CC, TC에서 notable sparsity

**Implication:** Sparse page migration → fast memory capacity 낭비 + cache pollution. 기존 solution은 sparse/dense 구분 불가.

### Observation 3: Hot page identification overhead can degrade performance

ANB와 DAMON이 hot page 식별에만 소모하는 kernel CPU cycle:
- ANB: average **159%** 증가 (최대 487%)
- DAMON: average **277%** 증가 (최대 733%)
- Redis p99 latency: ANB +34%, DAMON +39%
- Best-effort workload execution time: ANB up to +4.6%, DAMON up to +8.6%

## M5 Architecture (§5)

### 1. HPT & HWT: Cost-Efficient Top-K Trackers (§5.1)

**왜 PAC/WAC을 online으로 쓸 수 없는가?**
- 256GB CXL DRAM 기준: PAC 128MB, WAC 8GB storage 필요.
- Top-K 식별에 모든 counter fetch + sort → 수백 ms 소요 → agile migration 불가.

**해결: CM-Sketch 기반 Top-K Tracker (Figure 5)**

두 단계 구조:

**CM-Sketch Unit:** H rows × W columns의 SRAM array. 각 entry는 access count 저장.
- Memory address → H개 hash function (parallel) → 각 row의 해당 column counter increment.
- Comparator tree로 H개 increment된 counter 중 minimum 선택 → estimated access count.

**Sorted CAM Unit:** K entries, 각 entry = {address, access count}. Access count 기준 정렬.
- Hit → CM-Sketch에서 얻은 count로 CAM entry update.
- Miss → CM-Sketch count > CAM의 minimum count이면 minimum entry를 새 address로 replace.

**요구사항:** DDR4 3200의 tCCD = 2.5ns → **400MHz 이상** 동작 필요. FPGA synthesizable.

**Preciseness vs. entry 수 (Figure 7):**
- CM-Sketch N=32K: average access-count ratio **0.97** (PAC 기준)
- Space-Saving N=50: average **0.49**
- ⇒ CM-Sketch가 작은 N에서는 hash collision으로 부정확하지만, **충분히 큰 N**에서는 Space-Saving 대비 우수 (FPGA timing constraint도 만족).

**Area (Table 4):** CM-Sketch 32K entries = **46,930 µm²** (vs. Space-Saving 50 entries = 3,649 µm²).

## 방법론

(요약 파일의 설계/메커니즘 섹션 참조)

## 핵심 기여

1. **PAC/WAC:** CXL controller의 near-memory processing을 활용한 최초의 **precise, transparent offline profiling** 도구 — 모든 DRAM access 완전 계측. CPU-driven page migration solution의 부정확성을 정량적으로 증명.

2. **CPU-driven solution의 실패 원인 규명:**
   - Warm page → hot page 오식별 (access-count ratio 0.21–0.29)
   - Sparse page 감지 불가 (Redis 86% sparse) → capacity waste + cache pollution
   - Hot page 식별 overhead가 benefit을 능가할 수 있음 (kernel CPU cycle +487%)

3. **M5 platform:** CXL controller에 CM-Sketch 기반 HPT/HWT를 통합 → **47% 더 hot한 page 식별**, **14% 더 높은 성능** (심지어 simple policy로도). Virtually zero CPU overhead로 hot page 식별.

4. **산업적 의의:** M5는 CPU architecture 변경 없이 **commodity FPGA 기반 CXL device**에 통합 가능 — 기존 server에 즉시 적용 가능한 실용적 설계.

## 주요 결과

### 실험 환경

- **Testbed:** Dual Intel Xeon Gold 6430 (32-core Sapphire Rapids), 64GB DDR5 + Intel Agilex-7 FPGA CXL device (8GB DDR4 CXL memory).
- **Migration cost:** ~54 µs per page (측정).
- **Workloads:** Redis, Memcached, CacheLib, SPECrate CPU 2017 (mcf_r, cactuBSSN_r, fotonik3d_r, roms_r), GAP benchmark (bc, bfs, cc, pr, sssp, tc), Liblinear.
- **Memory 할당:** Initially all pages in CXL DRAM. DDR DRAM capacity = 3GB.

### HPT Access-Count Ratio (Figure 8)

| Method | Avg. Access-Count Ratio |
|---|---|
| ANB (best CPU-driven) | ~0.49 |
| DAMON (best CPU-driven) | ~0.49 |
| M5 Space-Saving (N=50) | ~0.49 |
| M5 CM-Sketch (N=32K) | **0.72** (47% higher than CPU-driven) |

CM-Sketch 기반 HPT가 time-window 기반이라 PAC의 whole-execution top-K와 차이 있으나, **짧은 interval 내 hot page를 정확히 포착** → migration 효과 큼.

### End-to-End Performance (Figure 9)

| Method | vs. No Migration | vs. ANB | vs. DAMON |
|---|---|---|---|
| ANB | +81% | — | — |
| DAMON | +81% | +6% | — |
| **M5 (HPT)** | **+106%** | **+14%** | **+14%** |
| M5 (HWT) — Redis | +10% vs ANB / +43% vs DAMON | — | — |

**Redis 특이사항:** DAMON은 Redis 성능을 **16% 저하** — migration equilibrium 도달 후에도 PTE scanning을 계속하여 overhead만 발생. ANB는 equilibrium에서 page unmapping을 거의 하지 않아 overhead 적음.

**Liblinear:** M5 +24% over ANB, +14% over DAMON — highly skewed access distribution (Figure 10)이 precise hot page identification의 혜택을 극대화.

**PageRank:** 모든 solution 유사 성능 — page 간 hotness 차이가 작아 migration cost가 benefit을 상쇄.

### Scalability (Figure 11)

CM-Sketch 32K entries의 정확도는 memory footprint가 64배 증가해도 0.7 이상 유지 — address cardinality 증가에도 강건.

### M5 vs. IFMM (Intel Flat Memory Mode)

IFMM [74]은 DDR ↔ CXL word 단위 swap — page migration overhead(TLB shootdown, PTE update, 4KB copy) 제거. 그러나 **one-to-one mapping으로 DDR/CXL capacity 동일 요구.** M5는 IFMM과 상호보완적: IFMM으로 sparse hot word를, M5로 dense hot page를 migration.

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2025ASPLOS-summarize/m5-mastering-page-migration-and-memory-management-for-cxl-based-tiered-memory-systems.md|전체 요약 보기]]
