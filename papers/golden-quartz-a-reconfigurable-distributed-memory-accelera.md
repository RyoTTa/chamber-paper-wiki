---
tags: [paper, 2025, 2025MICRO, topic/cache, topic/dram, topic/storage, topic/virtual-memory]
venue: "MICRO 2025"
year: 2025
summary_path: "../paper-summaries/2025MICRO-summarize/quartz-a-reconfigurable-distributed-memory-accelerator-for-sparse-applications.md"
---

# Quartz: A Reconfigurable, Distributed-Memory Accelerator for Sparse Applications

**Venue:** MICRO 2025
**저자:** Courtney Golden, Axel Feldmann, Joel Emer, Daniel Sanchez (MIT CSAIL; Emer also with NVIDIA)

## 개요

Iterative sparse matrix computation은 scientific computing (linear solvers, convex optimization)과 graph analytics (BFS, SSSP, WCC)의 핵심 연산. 이 workload의 공통 특성:
- **High sparsity:** 99-99.9999% (matrix operand)
- **Low arithmetic intensity:** SpMV의 경우 matrix element당 단 1회 multiply (zero reuse)
- **Mixed sparsity:** Matrix operand는 static sparsity (system state), vector operand는 all-active (CG, PDHG) 또는 dynamic (BFS frontier)
- **Iterative:** Loop body가 수백~수천 회 반복 → preprocessing amortization 가능

기존 distributed-SRAM architecture는 두 가지 한계:
1. **Specialized (Azul [MICRO'24]):** 좁은 domain의 fixed-function control flow → programmability 부족
2. **General-purpose (Dalorex [HPCA'23]):** In-order RISC core PE → instruction fetch, bookkeeping, address calculation으로 대부분의 issue slot 낭비 → **compute throughput이 memory bandwidth를 충분히 활용하지 못함** (underutilization)

**Reconfigurable compute with shared memory hierarchy** (PolyGraph, Alrescha): conventional cache hierarchy로 인해 memory bandwidth bottleneck (PolyGraph: 512 GB/s, Alrescha: 288 GB/s) — distributed-SRAM 대비 두 자리 수 낮은 bandwidth.

**Gap:** Distributed-SRAM + reconfigurable compute의 조합은 기존에 탐구되지 않음. 이 조합이 달성 가능한 핵심 과제는 **task-level dataflow execution model**과 **static-dynamic sparsity를 동시에 처리하는 data partitioning**.

## 방법론

### 1. Programming Model: Einsum → Task Translation

Quartz의 프로그래머 인터페이스는 **Einsum cascade**. 이를 task로 변환하는 3-step process:

**Step 1 — Einsum Cascades:** 문제 specification을 Einsum cascade로 표현. Iteration은 iterative rank로 명시. 예: SpMV = \( Z_m = A_{m,n} \cdot B_n \) (binary map = multiply, reduce = add). 6개 application 모두 4~16개 task type으로 분해됨.

**Step 2 — Partitioned Einsum Cascade:** Partitioning을 Einsum에 명시적으로 도입 — partition rank 추가. 세 가지 partitioned tensor type:
- **Strictly partitioned:** 각 nonzero = 단일 partition
- **Duplicate partitioned:** 같은 값이 여러 partition에 복제 (예: \( LB \) — vector element가 필요한 모든 tile에 전송)
- **Shard partitioned:** Partial sums가 여러 partition에 분산 후 reduction (예: \( LZ \))

Inter-partition communication은 **distribution tensor** (\( T1, T2 \))로 표현: \( T1_{p,n} = 1 \) = partition \( p \)가 element \( B_n \) 필요. Communication tensor는 hardware에서 coordinate list/bitmap으로 효율적 저장.

**Step 3 — Dataflow Choice & Loop Fusion:** Partition + iteration rank를 특정 값으로 고정 → task instance 생성. 남은 loop는 최대 2개. Quartz는 task당 1개 loop만 허용 → outer loop를 여러 task로 분할. **Loop fusion**으로 동일 tile의 data-dependent task에서 intermediate storage 제거.

**SpMV 예시 — 4 task types:**
1. `SendColumnValue`: Tile이 소유한 column index \( n \)과 \( B \)-value를 해당 column의 matrix nonzero가 존재하는 모든 tile에 multicast
2. `ScaleColumn`: 도착한 vector element로 해당 column의 모든 local matrix nonzero scale → local row partial sum에 reduce. **Task**: `for m in M: LZ_p[m] += A_p[m,n] * LB_p[n]` (n → m dataflow, column value reuse)
3. `SendPartialSum`: Row index \( m \)과 partial sum을 최종 \( Z_m \) 소유 tile로 전송
4. `UpdateRowSum`: 도착한 partial sum을 최종 row sum에 reduce

**BFS 예시 — 4 task types:**
1. `SendPriorFrontierElement`: Frontier node index + distance → 모든 neighbor tile로 multicast
2. `TraverseEdges`: Local neighbors traverse, visited 여부 filter, local distance update
3. `SendFrontierCandidate`: Candidate frontier node index + pending distance → global distance 소유 tile로 전송
4. `UpdateFrontier`: Global distance 대비 filter, 최종 frontier 확정 + distance update

### 2. Hardware Architecture (§4)

**System scale (Table 2):**
- **8 chiplets × 2048 tiles/chiplet = 16,384 tiles total**
- **SRAM:** 452 KB/tile (448 KB data + 4 KB task queue/config) → 7.1 GB aggregate
- **Clock:** 1 GHz, SRAM access: 2 cycles, highly banked (8 banks, 128-bit width)
- **Network:** 2D bidirectional torus, 128-bit links, 1 cycle/hop (inter/intra-chiplet), 8 TB/s bisection bandwidth

**Tile architecture (Figure 7):**
- **PE** = Update fabric + Send fabric (deadlock prevention: receiver/sender 분리)
- **Reconfigurable fabrics:** Fabric units (load/store units + FPADD/FPMUL/FPDIV/INT ALU) connected by configurable connection nodes (muxes). 각 unit은 valid/ready handshake FIFO port.
- **Double-buffered configuration:** Fifer [MICRO'21] 방식 — 이전 task 실행 중 next task bitstream preload → reconfiguration latency minimal
- **Reconfiguration size:** 147 B (update fabric), 33 B (send fabric)
- **Loop execution:** Load/store unit이 affine pattern generator (Symphony와 유사, single loop descriptor) → strided SRAM access, 1 element/cycle throughput

**Task-level dataflow (active messages):**
- 각 task는 단일 trigger (network message or local task completion)로 시작
- 나머지 operand는 local scratchpad에서 fetch → multi-input 대기 불필요 (conventional instruction-level dataflow 대비 간소화)
- Task 구조: (1) input receive + local read, (2) compute (conditional branch with steering), (3) local write + network send

### 3. Sparsity Support (§4.3)

Quartz는 sparse computation을 세 가지 기법으로 효율화:

**(1) Task-level outer loop splitting:** 2-rank computation(e.g., matrix-vector)에서 하나의 dataflow 방향만 reuse 가능. Reuse 있는 방향 선택 → single outer-loop iteration당 1 task. 예: SpMV에서 vector element 1개를 받아 column-wise scaling → coordinate intersection이 degenerate (단순 sparse vector scaling) → 전용 intersection unit/merger 불필요.

**(2) Static sparsity pre-storage:** 모든 matrix operand는 static sparsity. Compile time에 각 vector coordinate/value를 어느 tile로 보낼지 미리 결정 가능. 예: BFS에서 각 tile은 자신이 소유한 node의 outgoing edge가 존재하는 모든 tile의 index를 저장.

**(3) Partitioning-guaranteed intersection:** Elementwise op에서 operand를 동일 partition에 co-locate → coordinate intersection trivial. PDHG의 `x_next`와 `x_bar`를 identically partition → filter/merge hardware 불필요.

## 핵심 기여

Quartz는 distributed-SRAM + reconfigurable compute의 최초 결합으로, iterative sparse computation에서 programmability와 peak performance를 동시에 달성.

**핵심 기여:**
1. **Einsum → task 체계적 translation:** Extended Einsum notation으로 computation + communication + partitioning을 통합 표현 → small, reconfigurable-friendly task type으로 자동 분해 (4~16 types/app)
2. **Task-level dataflow PE:** Active message-triggered short tasks (tens of ops avg), double-buffered reconfiguration, loop는 affine pattern generator로 streaming → in-order RISC core 대비 **5.7× throughput**
3. **Static-dynamic sparsity partitioning:** Hypergraph (all-active) + two-phase graph-then-hypergraph (non-all-active) → 기존 single-objective partitioning (round-robin/row-based/CNB/SparseP) 대비 **3.7×** 추가 성능, 최초로 dynamic sparsity에 대한 communication + load balance 동시 최적화

**Broader significance:** Distributed-SRAM architecture에서 reconfigurable compute의 viability를 입증. Dalorex++ 대비 **gmean 21.4×**, H100 GPU 대비 **gmean 93× speedup**, **21× area efficiency**, **2,223× energy efficiency**. SRAM-dominated area/power profile → technology scaling에 유리. Road graph partitioning 사례처럼 practical impact도 큼 (navigation queries with static graph, millions of runs).

## 주요 결과

**Objectives:**
1. **Load balance work among tiles** — PE underutilization 방지
2. **Minimize inter-tile communication** — NoC bandwidth bottleneck 방지

**기존 접근의 한계:**

| Technique | Communication | Load Balance | 
|---|---|---|
| Row-based (coordinate-space tiling) | Good (rows co-located) | Bad (power-law degree skew) |
| Round-robin | Bad (rows/columns scattered) | Good |
| Contiguous Nonzero Blocks (CNB) | Moderate | Bad (vector element weight variance) |
| SparseP (2D variable-size tiles) | Worse than CNB | Bad (vector distribution artifacts) |

**Quartz's three-part approach:**

**(A) Hypergraph partitioning** (Azul에서 차용): Data dependence를 hypergraph로 변환 — node = 각 nonzero, hyperedge = 동일 연산에 관여하는 node들. PaToH v3.3으로 hypergraph partitioning → hyperedge cut 최소화 = communication 최소화 + partition size 균등화 = load balance. All-active algorithm (CG, CHB, PDHG)에 적용.

**(B) Recursive hypergraph partitioning** (physical locality): Chiplet → tile level로 재귀적 hypergraph partitioning → dependent data가 다른 partition에 배정되더라도 물리적으로 가까운 tile에 위치. Average hop per message **21% 감소**, overall throughput **5% 향상**. All-active에 적용.

**(C) Two-phase partitioning** (dynamic sparsity, non-all-active): BFS/SSSP/WCC에서 hypergraph partitioning만으로는 load imbalance — frontier가 graph의 일부 지역에 집중될 때 해당 지역의 tile만 활성화.

- **Phase 1 — Graph partitioning:** Input graph 자체를 standard graph partitioning으로 clustering (locality 보존하되 cluster 크기는 tile보다 크게)
- **Phase 2 — Per-cluster hypergraph partitioning:** 각 cluster를 recursive hypergraph로 모든 tile에 분산

**효과:** Round-robin 대비 **3.6× throughput**, recursive hypergraph 대비 **1.4×** (NoC traffic은 2.5× 증가하나 load balance 개선이 더 큰 이득).

**Partitioning cost:** gmean **18.5분** (amortized over 수천~수십억 iterations). Graph500 Fugaku submission 대비 1000× 짧은 preprocessing. 실제로 recursive/two-phase가 plain hypergraph (20.9분)보다 빠름 (문제를 작은 조각으로 분해).

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/storage.md|Storage]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2025MICRO-summarize/quartz-a-reconfigurable-distributed-memory-accelerator-for-sparse-applications.md|전체 요약 보기]]
