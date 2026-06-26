---
tags: [paper, 2025, 2025ISCA, topic/cache, topic/storage]
venue: ""
year: 2025
summary_path: "../paper-summaries/2025ISCA-summarize/magicache-a-virtual-in-cache-computing-engine.md"
---

# MagiCache: A Virtual In-Cache Computing Engine

**Venue:** 
**저자:** Renhao Fan, Yikai Cui, Weike Li, Mingyu Wang, Zhaolin Li

## 개요

Data-parallel application (neural network 등)의 폭발적 증가로 인해 대규모 vector 연산과 memory 접근이 요구되면서, 전통적 computing architecture의 memory bandwidth와 전력 소모에 심각한 부담이 발생함. SRAM 기반 In-Cache Computing(ICC)은 processor-cache 간 data movement를 제거하여 높은 병렬성과 에너지 효율을 제공하는 유망 솔루션.

**기존 array-level ICC의 한계 (SplitCache = EVE [3] baseline 기준):**
1. **Static & coarse-grained partition:** Cache space를 SRAM array 단위로 computing space와 storage space로 정적 분할. Computing array의 모든 row가 computing line으로 고정되어, runtime에 실제 사용되는 computing line만 소수인데도 나머지가 idle 상태로 남음 → cache capacity 및 associativity의 심각한 손실.
2. **Bursty in-cache data movement:** In-cache computing의 높은 parallelism(예: Duality Cache의 수백만 thread, EVE의 2048-element vector)으로 인해 한 번의 memory instruction이 대량의 cache 접근을 유발. Cache miss 시 제한된 MSHR(Miss-Status Handling Register) 수로 인해 stall이 증폭.

**Motivation data points:**
- matmul과 backprop를 다양한 computing array ratio(25%~75%)로 정적 설정 시 최적 비율이 각각 62.5%, 50%로 다름 (Figure 2).
- Matrix multiplication vector 프로그램에서는 32개 register 중 v0, v1만 사용 → array-level EVE에서는 30개 register의 공간이 낭비됨 (Figure 3).
- L2 cache 512KB, 32 MSHRs 환경에서 vector length 65536 bits (=128 cachelines per unit-stride access) → MSHR 한계로 인한 심각한 stall.

---

## 방법론

MagiCache는 L2 cache를 기반으로 하며, 3개의 핵심 component로 구성: (1) cacheline-level ICC architecture, (2) virtual engine, (3) instruction chaining.

### 1. Cacheline-Level In-Cache Computing Architecture (§4.2)

**Fused array 설계:**
- 기존처럼 array 단위로 computing/storage를 분리하지 않고, 하나의 SRAM array 내에서 일부 row는 computing line, 나머지는 cacheline으로 동작.
- Super array 개념: 여러 fused array를 수평 결합하여 한 row = 한 cacheline 크기 (예: 256×256 array 2개 → 256 row × 512 column super array).
- **Tag 확장:** 2개의 추가 indicator bit — `Computing bit` (cacheline인지 computing line인지), `Presence bit` (cache coherence 용).

**Cacheline → Computing line 변환 (4단계, Figure 5):**
1. Valid cacheline이면 eviction (dirty면 writeback to LLC)
2. Computing bit 외 모든 indicator bit clear
3. LRU bit를 invalid로 설정 (replacement policy가 재선택하지 않도록)
4. Computing bit = 1로 설정

Computing line은 virtual engine이 관리하며, cache controller는 접근/교체 불가. Storage space 관점에서는 해당 set의 associativity가 1 감소.

**Peripheral circuits (Figure 4c):**
5개 layer로 구성:
- **Logic layer:** Bit-line computation으로 AND, NAND, OR, NOR, XOR, XNOR 동시 생성.
- **Add layer:** Bit-line 간 carry chain 구성으로 addition 수행.
- **Shift layer:** 좌/우 shift 연산.
- **Register layer:** Bit-line당 1-bit register로 shift 중간값 저장 + memory instruction의 read/write coalescing 용 line buffer.
- **Writeback layer:** 결과 선택 후 destination row에 저장.

**Micro-code execution:** Bit-parallel layout 기반. Addition/logic = 2 cycles, multiplication = ~160 cycles (=32×5, iterative shift-add). 각 fused array는 array sequencer로 virtual register row 번호를 관리.

### 2. Virtual Engine for Space Management (§4.3)

Virtual engine은 physical ICC 구조와 RISC-V vector ISA 사이의 virtual middle layer (Figure 6). 4개 module로 구성:

| Component | 기능 |
|---|---|
| **Instruction Queue** (16-entry) | Vector instruction buffering으로 scalar core block 방지 |
| **Control Status Registers (CSRs)** | vl (effective vector length), vtype (element type) 등 유지 |
| **Request Generator** | 각 vector element의 주소 계산 → cache controller로 전송 |
| **Vector Register Mapping Table (VRMT)** | Computing line → vector register 매핑 (32 rows × Q columns) |

**VRMT 구조:**
- 각 vector register는 Q개의 segment로 구성, 각 segment = 하나의 computing line.
- 32개 register의 동일 index segment는 동일 fused array에 매핑 (bit-line 공유로 in-cache computation 가능).
- 서로 다른 index segment는 서로 다른 fused array에 매핑 (병렬 computation).
- j-th segment는 `(j mod N)`-th array에 할당 (N = 총 fused array 수).
- Table entry: `{valid bit, row index}`.

**Formulas:**
```
Maximum Vector Length = Q × W bits  (Equation 1, W = cacheline width)
Size(VRMT) = 32 × Q × (1 + log₂H) bits  (Equation 2)
Maximum Occupancy = (32 × Q × W) / (N × H × W)  (Equation 3)
```

**Lazy initialization (Algorithm 1):**
- Register는 instruction에 의해 실제 사용될 때만 allocation. Unused register와 segment는 allocation 안 함 → cache space 절약.
- `vset(i)vl(i)` instruction으로 vl 변경 시 필요한 segment 할당/해제.
- Register release는 compiler-level liveliness analysis로 life cycle 추출 → life cycle 종료 지점에 vl=0 설정하는 instruction 삽입 (overhead < 0.5%).

**Allocation policy: FFA (Find-First-Available):**
- Random 위치에서 circular scan으로 `valid=0` (free) 또는 `computing=0` (available) cacheline 탐색.
- Free line 우선, 없으면 available line 선택.
- 기존 LRU/pseudo-LRU 대비 hardware overhead 최소화, L2 miss rate 증가 < 1%.
- Minimum associativity threshold: 각 set별로 available associativity가 threshold 이하로 떨어지면 해당 set의 cacheline allocation 금지.

**Strawman vs. MagiCache (Figure 3):**
- EVE: computing array의 capacity를 32개 register에 균등 static 분배 → matmul에서 30개 register 낭비.
- MagiCache: v0, v1만 동적 allocation, 나머지 row는 cacheline으로 유지 → 거의 100% utilization.

### 3. Instruction Chaining (§4.4)

Bursty memory access latency 완화를 위한 hardware-implemented technique.

**문제 (Figure 7a):** Vector memory instruction은 각 fused array가 MSHR stall → load/store → sync stall 3단계를 거치며, 마지막 array까지 완료되어야 instruction commit 가능.

**해결 (Figure 7b):** Conflict 없는 인접 instruction들을 하나의 group으로 묶고, 각 fused array가 독립적으로 group 내 모든 instruction을 asynchronous하게 실행. Inter-array synchronization은 group 경계에서만 수행.

**Group boundary (conflict conditions):**
1. Configuration instructions (`vset(i)vl(i)`) — global vector state 변경
2. Permutation instructions (`vrgather`, `vslide`) — inter-array element 이동
3. Store instructions whose address ranges interleave with other memory instructions (data hazard)  
   단, same address range (예: two unit-stride with same base+stride)는 hazard-free → 예외

**Implementation:** Virtual engine이 runtime에 conflict-free group을 식별. Conflict 발생 시 sync pseudo-instruction 삽입 → group boundary 표시.

---

## 핵심 기여

1. **Cacheline-level ICC 최초 제안:** Array-level의 static/coarse-grained partition을 cacheline-level dynamic allocation으로 대체하여, computing과 storage를 동일 array에서 융합. Lazy initialization으로 unused register의 공간 낭비를 제거.
2. **Virtual engine abstraction:** Physical ICC 구조와 vector ISA 사이의 middle layer로, VRMT를 통한 runtime register 관리 (개수/길이/위치/life cycle 전부 동적 구성) → average cache utilization 55.9%→97.1%.
3. **Instruction chaining:** Hardware-implemented async execution으로 bursty access의 sync stall을 45.3% 감소. Compiler-level modification 없이 hardware만으로 overlap 달성.
4. **Overhead:** 6.5KB extra storage + 6.8% area 증가로 1.39× speedup 달성. Different data layouts, peripheral circuits, programming frameworks에도 적용 가능한 general technique.

## 주요 결과

### 실험 환경

| 항목 | 상세 |
|---|---|
| **Process node (array)** | TSMC 40nm |
| **Process node (logic)** | TSMC 28nm |
| **Fused array area overhead** | 8.9% over vanilla SRAM (sub-array sharing으로 17.7%→8.9%) |
| **Bit-line computation** | 54% more energy, 60% more latency than read/write (1.6ns vs. 1.0ns) |
| **Virtual engine area** | 26,434 µm² (logic only, VRMT SRAM 별도) |
| **Virtual engine power** | 27.01 mW |
| **Extra storage** | 6.5 KB (4.5KB VRMT + 2KB tag bits) |

### Benchmarks (Table 5)

| Benchmark | Size | Access Pattern | Cross-element | Masked |
|---|---|---|---|---|
| vvadd | 8192K | unit-stride | × | × |
| matmul | 1024×2048 | unit-stride | × | × |
| jacobi-2d | 2000×2000 | unit-stride | slide | × |
| pathfinder | 10×5000K | unit-stride | slide | × |
| k-means | 50000×10 | unit+strided | × | √ |
| backprop | 512K | unit+strided | reduce | × |

### Configurations (Table 4)

| Name | Fused Arrays per VReg | Max VL (bits) | Max Occupancy |
|---|---|---|---|
| Split-8 | 8 (static) | 65536 | 50% fixed |
| Fused-1/2/4 | 1/2/4 | 16384/32768/65536 | 12.5%/25%/50% |
| Chain-1/2/4 | 1/2/4 | 16384/32768/65536 | 12.5%/25%/50% |

### 성능 결과 (Figure 8, Table 6)

- **Chain-4 vs. Split-8:** 1.39× geomean speedup (1.19×~1.61× per benchmark).
- **Fused-x vs. Split-8:** Occupancy 증가에 따라 성능 향상 (더 큰 vector length = 더 많은 병렬성).
- **Chain-x vs. Fused-x:** Instruction chaining으로 평균 10% 추가 speedup.
- **Best per-benchmark:** matmul 1.61×, k-means 1.58×, jacobi-2d 1.46×.

### Execution Breakdown (Figure 9)

- Split-8의 computation time이 다른 config의 2배 (computing/fused array 수에 반비례).
- **Synchronization time:** Instruction chaining으로 평균 45.3% 감소 (sync 횟수 감소).
- **MSHR stall + load/store time:** Vector length 증가에 따라 증가하나, sync time 감소폭이 더 커서 전체 memory access time은 감소.
- Strided access (k-means, backprop): vector length 증가해도 MSHR usage가 고정 → near-serial execution → 성능 차이 미미.

### MSHR Usage (Table 7)

- Chain-4는 Split-8 대비 vector access의 평균 MSHR usage 2.76 entries 증가 (더 많은 element를 동시 처리).
- MSHR usage는 Chain-1 → Chain-4로 vector length 증가에 따라 상승.

### Cache Utilization on Multi-Application (§6.3, Table 8)

Two-core 구조: Core 1 = vector app, Core 2 = scalar app (add: sequential, mmul: strided, spmv: random).

- **Cache utilization:** Split-8 평균 55.9% → Chain-4 평균 97.1% (42% improvement).
- **Miss rate reduction (Figure 10):** add 36% 감소, spmv 14% 감소. mmul은 strided access가 L1 miss → L2 hit → LRU timestamp 갱신으로 working set이 L2에 상주하여 miss rate near-zero.
- **Time-sampled utilization (Figure 11):** Chain-4는 90%+의 space를 caching에 사용, Split-8은 50%만 사용. 동일 time interval에서 Chain-4 11 iterations vs. Split-8 9 iterations.

### Energy & Area (§6.4)

- Bit-line computation: read/write 대비 54% more energy, 전체 fused array의 ~17% 차지 → average power 9% 증가. 그러나 H-tree network 제거 효과로 overall energy efficiency 개선.
- MagiCache는 SplitCache 대비 6.8% 추가 area overhead + 6.5KB extra storage.
- 전체적으로 SplitCache는 scalar-only 대비 4.81× speedup, MagiCache는 추가 1.39× speedup.

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2025ISCA-summarize/magicache-a-virtual-in-cache-computing-engine.md|전체 요약 보기]]
