---
tags: [paper, 2024, 2024MICRO, topic/cache, topic/disaggregation, topic/dram, topic/memory-tiering]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024MICRO-summarize/starnuma-mitigating-numa-challenges-with-memory-pooling.md"
---

# StarNUMA: Mitigating NUMA Challenges with Memory Pooling

**Venue:** 
**저자:** 

## 개요

### 1.1 대규모 NUMA 시스템의 도전 과제

16소켓 이상의 대규모 멀티소켓 시스템(HPE Superdome FLEX, IBM Power10)은 수천 개 스레드가 테라바이트 단위 공유 메모리에 직접 접근하는 미션 크리티컬 워크로드(HPC, 트랜잭션 처리, 뱅킹)에 사용되며, 연간 $50억 규모 시장을 형성한다. 그러나 소켓 확장은 계층적 인터커넥트를 필요로 하여 NUMA 효과를 극대화시킨다:

- **지연시간 격차:** local 80ns → 1-hop(intra-chassis) 130ns → 2-hop(inter-chassis) 360ns (**4.5× 차이**)
- **대역폭 격차:** local memory > 200GB/s vs. UPI 41GB/s, NUMALink 26GB/s → 원격 접근에 심각한 queuing delay 발생

### 1.2 Vagabond Page 문제

불규칙 접근 패턴을 가진 워크로드(BFS, CC 등 그래프 분석)에서 핵심 병목은 **"vagabond page"** — 여러 소켓이 활발히 공유하여 최적의 home socket 위치가 존재하지 않는 페이지:

**BFS 워크로드 분석 (16소켓, Fig. 2):**
- 단 1개 소켓만 접근하는 페이지: 17%
- 16개 모든 소켓이 공유하는 페이지: 2% → 그러나 **전체 메모리 접근의 36%** 차지
- 8개 이상 소켓 공유 페이지(어떤 chassis도 home이 될 수 없음): 7%의 페이지가 전체 접근의 **68%** 차지
- 이 중 75%가 inter-chassis 접근 → 360ns 지연

**1차 근사 AMAT 계산 (unloaded 기준):** 64% × 80ns(local) + 36% × (25% × 130ns + 75% × 360ns) = **160ns**. Loaded 환경에서는 대역폭 제약으로 queuing delay 추가 → AMAT 300ns+.

**Strawman: 페이지 복제의 한계**
- BFS에서 대부분의 공유 페이지가 read-write → 소프트웨어 coherence로 복제본 일관성 유지 시 prohibitive overhead
- CXL directory는 평균 100ns마다 coherence 트랜잭션 처리 → 소프트웨어로는 불가능한 처리량
- Read-only 페이지만 복제 시에도 TC 같은 워크로드는 60% 이상의 데이터셋이 16개 소켓에 의해 접근 → 메모리 용량 낭비 심각

### 1.3 CXL 기반 메모리 풀의 기회

CXL 3.x는 타입-3 MHD(Multi-Headed Device)로 다중 호스트에 의한 coherent 공유 메모리를 지원하며, PCIe 6.0 (8GB/s/lane) 기반으로 높은 대역폭 제공. Pond [38]가 rack-scale에서 CXL 메모리 풀의 타당성을 입증했으나, scale-out(파티셔닝)에 초점. StarNUMA는 scale-up(active sharing) 맥락에서 메모리 풀을 NUMA 시스템의 새로운 architectural block으로 도입.

## 방법론

### 3.1 실험 방법론

| 항목 | 구성 |
|------|------|
| Target system | 16-socket HPE Superdome FLEX 기준, 4 chassis × 4 sockets |
| Core config | 28 OoO cores/socket, 2.4GHz, 4-wide, 256-entry ROB (full-scale) |
| Simulation scale-down | 4 cores/socket, 1 DDR5-4800 채널/socket, 링크 BW 비례 축소 |
| L1D/L1I | 32KB, 8-way, 4-cycle |
| L2 | 1MB, 16-way, 14-cycle |
| LLC | 2MB/core, 16-way, 30-cycle, shared per-socket, non-inclusive |
| Interconnect | UPI 20.8GB/s, NUMALink 13GB/s (full-scale 기준) |
| CXL | x8 per socket, 64GB/s raw → 40GB/s effective |
| Pool DRAM | DDR5-4800, 16 channels (full-scale) |
| Simulator | ChampSim 기반 custom multi-socket 모델 |
| Methodology | 3-step sampling: (A) Instruction + memory tracing on real HW → (B) Trace simulation for migration decisions → (C) Mixed-modality timing sim (1 detailed socket + 15 light sockets) |
| Phases | per-core 1B instr. 간격, 5-10 checkpoints, checkpoint당 100M instr. simulated |
| Workloads | Graph: BFS, CC, SSSP, TC (GAP suite, Kronecker graph 2²⁸ vertices); HPC: FMI, POA (GenomicsBench); Data Serving: Masstree (100GB, 50/50 R/W); Transaction: TPCC (64 warehouses on Silo DB) |
| Baselines | Baseline NUMA + perfect page knowledge migration; Baseline ISO-BW (UPI/NUMALink BW pool 총량만큼 증가); Baseline 2×BW (모든 coherent link 2×); StarNUMA Half-BW (CXL 20GB/s); Static oracular placement |

### 3.2 성능 결과 (T₁₆)

**AMAT 및 IPC (Fig. 8):**

| 워크로드 | Baseline AMAT | StarNUMA AMAT | AMAT 감소 | Speedup |
|----------|--------------|--------------|----------|---------|
| SSSP | ~900ns | ~250ns | 72% | 1.63× |
| BFS | ~850ns | ~175ns | 79% | 2.17× |
| CC | ~250ns | ~150ns | 40% | 1.52× |
| TC | ~225ns | ~125ns | 44% | 1.63× |
| Masstree | ~250ns | ~175ns | 30% | 1.19× |
| TPCC | ~175ns | ~130ns | 26% | 1.21× |
| FMI | ~175ns | ~125ns | 29% | 1.22× |
| POA | ~80ns | ~80ns | 0% | 1.00× |
| **평균** | — | — | **48%** | **1.54×** |

**StarNUMA의 2중 AMAT 감소 메커니즘:**
1. **Unloaded latency 직접 감소:** Pool 배치로 inter-chassis(360ns) 접근을 pool 접근(180ns)으로 전환 → 2-hop access 비율 감소
2. **Contention 완화:** CXL 링크의 추가 대역폭이 inter-socket 링크의 queuing delay를 경감 (특히 SSSP, BFS 등 bandwidth-bound 워크로드)

**T₀ vs T₁₆:** T₀(simpler)도 1.35× speedup 달성 — wide sharing 식별만으로 대부분의 이득 확보 가능.

### 3.3 Ablation Studies

**Static oracular placement vs dynamic migration (Fig. 9):**
- StarNUMA Static: dynamic 대비 약간 우수 (migration overhead 제거) → 공유 패턴이 시간에 따라 크게 변하지 않음
- **Baseline Static은 baseline dynamic 대비 이득 없음** → 기존 NUMA 아키텍처에는 vagabond page를 위한 좋은 위치가 구조적으로 부재. Pool의 architectural significance 입증.

**CXL 지연시간 민감도 (Fig. 10):**
- CXL switch 추가로 190ns overhead → end-to-end 270ns (여전히 2-hop 360ns보다 25% 낮음)
- 평균 speedup: 1.54× → **1.34×** (TC가 가장 영향: 1.63× → 1.11×, latency reduction에만 의존하므로)

**대역폭 영향 (Fig. 11):**
- **Baseline ISO-BW:** UPI 26.4GB/s, NUMALink 17GB/s → baseline 대비 1.14× (SSSP 1.4×, BFS 1.29×). 그러나 StarNUMA 대비 40% 낮음
- **Baseline 2×BW:** 68개 coherent link 2배로 1.2TB/s 추가 → 비현실적(pin 2배). 평균 StarNUMA 대비 12% 낮음. BFS만 StarNUMA 능가 — pool로의 집중된 트래픽이 CXL 링크 contention 유발
- **StarNUMA Half-BW (20GB/s):** 여전히 Baseline ISO-BW보다 11% 우수

**Pool 용량 영향 (Fig. 12):**
- Pool 4× 축소 (chassis → socket급, capacity 20% → 5%): 평균 speedup 1.54× → **1.48×** — 미미한 영향
- 대부분의 원격 접근이 소수의 가장 hot한 페이지에 집중 → 작은 pool로도 충분

**Page replication vs pooling (Fig. 13, TC):**
- TC는 read-only 페이지가 대부분(60%가 16개 소켓 공유) → replication은 coherence-free지만 용량 압박
- BFS는 read-write 공유가 대부분 → replication 시 coherence overhead prohibitive
- 결론: replication과 pooling은 상호보완적

### 3.4 시뮬레이션 방법론 검증 (Fig. 14)

3가지 Simulation Configuration으로 BFS/TC/FMI 재실험:
- SC1(default): 100M instr/phase
- SC2: 300M instr/phase (3× 상세 시뮬레이션)
- SC3: 8 cores/socket, 2× BW (2배 시스템 스케일)
- 결과: **정량적 일관성** (SC2/SC3 모두 SC1과 유사하거나 더 나은 speedup) → 방법론 견고성 입증

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

| Component | Specification |
|-----------|--------------|
| Simulator | ChampSim 기반 확장, multi-step sampling + mixed-modality |
| Tracing | Intel PinTool (ChampSim tracer + Memory Access tracer 결합) |
| Trace simulation | Memory-only trace simulator로 migration decision 생성 |
| Timing simulation | 1 detailed OoO socket + 15 light cores (memory trace injection, IPC-regulated rate) |
| Interconnect module | UPI, NUMALink, CXL topology + routing + congestion 모델링 |
| Coherence | MESI directory, socket/pool에 분산 |
| Memory controller | DRAMSim3 (DDR5-4800) |
| Migration | PTW extensions, TLB annex counter, marker bit, hardware TLB shootdown directory |

**추가 하드웨어 요구사항:**
- TLB annex counter: i-bit/entry
- Marker bit: 1bit/TLB entry
- Metadata region: 128MB (T₁₆, 16TB system)
- Authorization unit (lex order): no storage

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]


## 전체 요약

[[../paper-summaries/2024MICRO-summarize/starnuma-mitigating-numa-challenges-with-memory-pooling.md|전체 요약 보기]]
