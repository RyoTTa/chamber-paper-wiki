---
tags: [paper, 2023, 2023ISCA, topic/disaggregation, topic/dram, topic/nvm, topic/storage]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023ISCA-summarize/decoupled-ssd-rethinking-ssd-architecture-through-network-based-flash-controllers.md"
---

# Decoupled SSD: Rethinking SSD Architecture through Network-based Flash Controllers

**Venue:** 
**저자:** Jiho Kim, Myoungsoo Jung, John Kim (KAIST)

## 개요

### 1.1 Modern SSD의 구조적 병목

Modern SSD는 multi-channel, multi-way, multi-plane 구조로 높은 parallelism을 제공하며, NVMe interface와 결합하여 고속 I/O 처리. 그러나 **Garbage Collection(GC)** 수행 시 I/O와 GC가 동일한 system resource(core, DRAM, system-bus)를 공유하면서 **front-end ↔ back-end tightly coupled** 구조가 치명적 간섭을 유발함.

**GC 시 데이터 이동 과정 (Fig. 1):**
1. Victim flash block의 valid page를 flash die에서 read → ECC engine으로 error check (system-bus 경유)
2. Page data를 DRAM buffer로 이동 (system-bus 경유)
3. FTL이 destination flash die로 write 명령 발행 → DRAM에서 다시 system-bus 통해 flash로 전송

Flash-to-flash 데이터 복사에 system-bus와 DRAM을 왕복하는 중대한 비효율.

### 1.2 System-bus 경합의 심각성 (Fig. 2)

Multi-plane 명령으로 flash bandwidth가 증가할수록 system-bus contention이 더욱 심각:
- **Low bandwidth(4KB):** GC trigger 시 I/O bandwidth 하락 (system-bus utilization drop).
- **High bandwidth(32KB, 8-plane):** I/O bandwidth 하락폭이 훨씬 심각. System-bus utilization for I/O가 GC 중 급감.

단순히 system-bus bandwidth를 높이는 것은 비용 증가를 수반할 뿐 근본적 해결책이 아님 — front-end와 back-end가 여전히 coupled.

### 1.3 기존 접근의 한계

| 기법 | 한계 |
|------|------|
| Preemptive GC [24] | GC를 미루지만 결국 system-bus 간섭 발생 |
| Tiny-tail [42] | Partial/non-blocking GC로 tail-latency 개선하나 system-bus 경합 불가피 |
| Parallel GC [35] | Plane-level 병렬화로 GC 자체는 빨라지나 더 bursty한 traffic → system-bus contention 순간 증폭 |
| Copyback command [31] | Error propagation 문제로 modern SSD에서 거의 사용 불가 |

## 방법론

### 3.1 dSSD Architecture Overview (Fig. 3)

기존 SSD 대비 두 가지 주요 하드웨어 변경:

- **Decoupled Flash Controller (C_D):** 각 flash channel에 위치. ECC engine 통합, decoupled buffer(dBUF), network interface 포함.
- **Flash-controller Network-on-Chip (fNoC):** Flash controller 간 packet 기반 통신을 위한 on-chip interconnect.

**Decoupled GC data path (Fig. 3):**
1. Flash controller가 victim die에서 valid page read → dBUF 저장
2. Integrated ECC error check/correction
3. Packetization 후 fNoC 통해 destination controller로 전송
4. Destination controller가 page write — **system-bus/DRAM 미사용**

**Decoupled Flash Controller 세부 구조 (Fig. 4):**
- Channel command controller, command queue, page buffer (기존)
- ECC engine (추가)
- dBUF (decoupled buffer): flash-to-flash 전용
- Network interface + router: fNoC 연결
- Bus interface: 기존 system-bus 연결 (I/O request용)

### 3.2 Global Copyback Command (핵심 기법 1)

**기존 copyback의 문제:**
- Error propagation: die 내 error correction 한계로 거의 사용 안 됨
- **Local copyback** only: source/destination이 동일 plane(die)으로 제한

**dSSD의 Global Copyback (Fig. 4):**

**단계별 실행:**
1. FTL이 source/destination address를 포함한 global copyback 명령을 system-bus 통해 source C_D로 전송.
2. C_D가 low-level read command 발행 → flash die에서 page read.
3. Page data를 dBUF에 저장 (I/O page buffer와 분리).
4. ECC engine이 error detection/correction 수행.
5. Destination이 다른 channel이면 packetization: page data + command/address → packet.
6. Router 통해 fNoC에서 destination으로 routing.
7. Destination C_D에서 packet parsing → command queue 등록 + data dBUF 저장.
8. Destination controller가 write command 발행.

**Command queue tracking:** 각 copyback entry는 status field로 현재 stage 추적 (R=read done, RE=error correction done, etc.) 및 source/destination index 유지.

**핵심 이점:** System-bus와 DRAM을 전혀 사용하지 않음. ECC 적용으로 error propagation 해결. Destination이 어떤 channel이든 가능 → 완전한 유연성.

### 3.3 fNoC 설계 (핵심 기법 2)

- **Topology:** 1D mesh (flash controller floorplan에 적합)
- **Routing:** Dimension-order (minimal)
- **Channel bandwidth:** Flash channel bandwidth의 2× 정도면 충분 (bisection bandwidth `B_b = N/2 × B_f`, bidirectional)
- **Buffer size:** 충분한 bandwidth 시 작은 buffer로도 충분 (Fig. 13)

**Sensitivity studies (Fig. 12, 13):**
- Channel 수 증가 → 더 많은 router channel bandwidth 필요하지만 saturation 존재
- Way 수 증가 → ×2 router bandwidth에서 saturation
- 1D mesh vs ring vs crossbar: bandwidth 충분할 때 1D mesh ≈ crossbar 성능
- Ring은 serialization latency로 불리

### 3.4 Dynamic Superblock Management (핵심 기법 3)

**Static superblock의 문제 (Fig. 5(a)):**
Superblock은 channel별 동일 block ID로 구성 → parallelism 최대화. 하지만 process variation으로 한 sub-block에서 uncorrectable error 발생 시 **전체 superblock이 "dead"** 로 처리 → 멀쩡한 sub-block도 낭비.

**dSSD 해법 — Recycled Block + Dynamic Superblock (Fig. 5(b), 6):**

**두 가지 table (각 C_D가 개별 유지):**
- **Recycle Block Table (RBT):** Dead superblock에서 살아있는 sub-block들을 recycling bin처럼 보관. FTL에게는 invisible.
- **Superblock Remapping Table (SRT):** Dynamic superblock의 hardware-based address remapping. Source blockID → New blockID 매핑. FTL에 transparent.

**Walk-through 예시 (Fig. 6):**

1. Superblock 0에서 uncorrectable error 발생 → FTL이 valid page를 새 superblock으로 복사. 동시에 C_D가 생존 sub-block들을 RBT에 등록 (block A).

2. 이후 Superblock 3에서 sub-block D에 uncorrectable error → C_D는 FTL에 알리지 않고 RBT에서 recycle block A를 찾음.

3. SRT에 `D → A` 매핑 삽입. Global copyback으로 D의 valid page를 A로 이동.

4. FTL은 Superblock 3을 여전히 유효하다고 인식. 내부적으로는 dynamic superblock으로 동작.

**Reservation-based Dynamic Superblock (추가 기법):**
최초 bad superblock 발생 전에도 endurance 개선 위해, 일정 비율(7%)의 block을 초기부터 RBT에 reserve. 첫 bad superblock 발생을 **65%** 지연.

### 3.5 정성적 비교 (Table 3)

| 기법 | I/O 성능 | Tail-latency | GC 성능 | Bus 간섭 | FTL 변경 | 추가 비용 |
|------|----------|-------------|---------|----------|---------|----------|
| Preemptive GC | ++ | o | o | + | o | FTL 변경 |
| Tiny-tail | + | ++ | + | + | + | Parity pages |
| PaGC | o | – | ++ | – | o | FTL 변경 |
| **dSSD** | **++** | **++** | **++** | **++** | **+** | **fNoC** |

## 핵심 기여

dSSD는 SSD architecture의 근본적 재설계를 통해 front-end(system-bus, DRAM)와 back-end(flash memory)를 decoupling한 최초의 아키텍처. 핵심 기여: (1) **fNoC 기반 global copyback**으로 system-bus/DRAM을 우회하는 flash-to-flash direct communication → I/O **42.7%**, GC **63.8%** 개선, (2) GC datapath 분리로 tail-latency **31.4×** 개선, (3) **hardware-based dynamic superblock management**로 FTL 변경 없이 endurance **~23%** 개선. 기존 GC 최적화 기법들과 orthogonal하게 적용 가능하며, 향후 flash bandwidth 증가에 따라 system-bus contention이 더욱 심화될 미래 SSD에서 핵심적 설계 원칙을 제시.

## 주요 결과

### 4.1 Methodology

| 항목 | 내용 |
|------|------|
| **Simulator** | Simple-SSD [10] standalone + BookSim [14] fNoC integration |
| **SSD config** | 8 channels, 8 ways, 1 die, 8 planes, ULL flash (4KB page, read 5μs, write 50μs) |
| **System-bus** | 8GB/s (baseline), PCIe 3.0 x8 |
| **fNoC** | 1D mesh, 8 nodes, dim-order routing |
| **Workloads** | Synthetic (4KB/128KB seq/rand) + MSR trace workloads [23] |
| **Superblock eval** | TLC-based (16KB page), P/E variation model: E(x)=5578, σ(x)=826.9 |
| **Baselines** | Baseline(PaGC), BW(system-bus 1.25×), dSSD_b(dedicated bus), Preemptive GC, Tiny-tail |
| **Metrics** | I/O bandwidth, GC performance, tail-latency, system-bus utilization |

### 4.2 I/O 및 GC 성능 (Fig. 7)

| Config | I/O 개선 | GC 개선 |
|--------|---------|---------|
| BW (system-bus 증가만) | 11.8% | 10.9% |
| **dSSD** | **42.7%** | **63.8%** |
| dSSD_b (dedicated bus) | 미미 | 미미 (serialization bottleneck) |
| dSSD_f (fNoC) | dSSD와 유사 | dSSD와 유사 |

System-bus utilization: dSSD_f는 baseline 대비 DRAM hit I/O: 18.1%↑, flash miss I/O: **66.9%↑**.

### 4.3 Bandwidth Scaling Sensitivity (Fig. 8)

- **Low bandwidth:** System-bus 2× 증가해도 I/O 4.6%, GC 13.6% 개선에 그침 — bus contention이 원래 크지 않음.
- **High bandwidth:** Baseline ×1.5: I/O +13.5%, GC +19.9%. 동일 bandwidth에서 dSSD_f ×1.5: I/O **+39.4%**, GC **+68%** — decoupling이 bandwidth 증가보다 훨씬 효과적.

### 4.4 Latency Breakdown (Fig. 9)

Multi-plane 수 증가 시:
- Baseline: system-bus contention이 dominant
- dSSD_f: system-bus contention 제거, fNoC latency가 발생하나 copyback 전용이므로 낮은 수준 유지

### 4.5 Tail-latency (Fig. 10, 11)

DRAM-cached I/O(100% hit) 시:
- BW: 최대 I/O bandwidth 도달 불가 (54.6%), long tail
- dSSD_f: **최대 bandwidth 달성**, tail-latency Baseline 대비 **77×**, BW 대비 **39×** 개선

Workload traces 평균 (Fig. 11):
- Tail-latency: Baseline 대비 **31.4×**, Tiny-tail 대비 **5.17×** 개선
- Preemptive GC 대비 **20.8×** 개선 (prn_0 workload에서)

### 4.6 Dynamic Superblock — Endurance (Fig. 14)

- RECYCLED: Baseline 대비 endurance **~19%** 개선 (낮은 bad block 수 기준)
- RESERV(7%): **~35%** 개선, 첫 bad superblock **65%** 지연
- Block-wear variation(σ) 증가 시 RECYCLED 효과 증대
- RESERV는 low variation에서는 RECYCLED와 유사, high variation에서 추가 이득

**vs WAS(software-based) [40]:** WAS가 더 높은 endurance 달성 가능하나, block endurance 정보 수집을 위해 page read 필요 → 최대 **2×** I/O latency degradation. dSSD는 hardware remapping으로 FTL performance overhead 없음.

### 4.7 Dynamic Superblock — Performance Trade-off (Fig. 15)

- **SRT entries 증가:** Endurance는 개선되나 remapping으로 channel/bank conflict 증가 가능
- Worst-case: TLC + random write에서 SRT 2048 entries 시 최대 **~2×** 성능 저하
- **Workload traces:** endurance/perf_overhead metric 기준 대부분 workload에서 baseline 대비 우수 (read-intensive: average **21.7%↑**, write-intensive: **6%↑**)

### 4.8 Hardware Overhead

| Component | Overhead |
|-----------|----------|
| ECC per controller (LDPC, 14nm) | ~1.5% of SSD controller area |
| Router (45nm) | ~0.02mm², <0.25% area |
| dBUF (2×32KB per C_D) | 2.46% area |
| RBT | ~32 bits per controller (기본), ~1KB/channel (7% RESERV) |
| SRT (1024 entries) | ~4KB per controller |
| **Total** | SSD controller 면적 대비 미미한 수준 |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2023ISCA-summarize/decoupled-ssd-rethinking-ssd-architecture-through-network-based-flash-controllers.md|전체 요약 보기]]
