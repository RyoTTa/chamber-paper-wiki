---
tags: [paper, 2024, 2024HPCA, topic/dram]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024HPCA-summarize/agile-dram-agile-trade-offs-in-memory-capacity-latency-and-energy-for-data-centers.md"
---

# Agile-DRAM: Agile Trade-Offs in Memory Capacity, Latency, and Energy for Data Centers

**Venue:** 
**저자:** 

## 개요

데이터센터는 대규모 메모리 under-utilization 문제를 겪고 있음. 구체적 수치:

- Perlmutter 슈퍼컴퓨터 (2022년 Top500 8위): median memory utilization 13.3%, 평균 22.8%, 일부 workload만 98.6% 도달 [20]
- Google 2011년 production-tier cluster: 평균 memory utilization ~30%. 2019년 free-/batch-tier는 60%까지 개선되었으나 production-tier는 35%로 거의 변화 없음 (strict SLO로 인해 workload co-location 제한) [43]
- 클라우드 VM은 고정된 CPU-to-memory ratio로 할당되어 불필요한 memory 용량 낭비 발생 (e.g., 8 core + 2GB 필요해도 8 core + 16GB VM 선택)

데이터센터의 under-utilization 원인: (1) infrastructure over-provisioning, (2) 비효율적 workload scheduling (대규모 allocation unit), (3) VM configuration mismatch.

기존 연구들의 한계:
- TL-DRAM [19]: design-time trade-off, 3.15% area overhead, runtime adaptation 불가
- CLR-DRAM [25]: dynamic mode switching 가능하나 mode 전환 시 data 파괴 → 256GB DIMM rewriting에 >10초 소요, co-located workload에 service disruption 발생
- CHARM [37], CROW [11], MCR-DRAM [8]: design-time decision, area/complexity 증가

## 방법론

### 1. Mirrored Mat 구조

Conventional open-bitline 구조에서는 mat들이 BLSA를 연쇄적으로 공유 (1st mat ↔ 2nd mat BLSA, 2nd mat ↔ 3rd mat BLSA...). Agile-DRAM은 **mirrored mat** 구조를 도입하여 두 mat의 BLSA를 중앙에 배치하고, 상단/하단 mat의 bitline이 모두 중앙 BLSA에 연결되도록 함 (Figure 4).

- Odd column의 bitline → upper BLSA (△A, △C)
- Even column의 bitline → lower BLSA (△B, △D)
- Paired mat이 다른 mat과 BLSA를 공유하지 않음 → chaining effect 제거
- Area 증가 없음; bitline 길이는 BLSA 높이만큼만 미미하게 증가 (DRAM timing에 영향 없음)

### 2. Global Decoder 수정

기존 global decoder가 subarray 하나만 선택하던 것을, addr[10] (1024×1024 mat 기준 LSB subarray address)의 true/complementary 신호에 OR gate 추가 → paired subarray pair 동시 활성화 가능. 소요 logic gate 수: 수십 개.

### 3. 세 가지 Operation Mode

Agile-DRAM은 하나의 mode register로 세 mode를 제어:

#### Max-Capacity (MC) Mode (SINGLE)
- Single row activation, 기존 DRAM과 동일 동작
- Full capacity 제공
- Timing parameters: tRCD=13.8ns, tRAS=39.4ns, tWR=12.5ns, tRFC=260ns (DDR4-2400 기준)

#### Low-Latency (LL) Mode (DUAL)
- 한 bit를 paired mat의 두 cell에 complementary charge로 저장 (한 cell은 VDD, 다른 cell은 GND)
- 두 cell이 동시 activation → BLSA가 bitline (VDD 근처)과 bitline (GND 근처)을 differential sensing
- Complementary 신호로 인한 큰 voltage gap → 빠른 sensing
- SPICE simulation (22nm Rambus 기반, 65nm→22nm scaling, PTM HP 트랜지스터 모델, 1.2V supply):
  - **w/o ET (Early Termination):** tRCD 13.8→9.5ns (-31.2%), tRAS 39.4→32.3ns (-18.0%), tRFC 260→226ns (-13.1%)
  - **w/ ET:** DRAM cell을 VDD까지 완전 복원하지 않고 VET=1.1V에서 조기 종료. Strong sensing으로 partial restoration 가능. tRAS 32.3→18.7ns, tWR 12.5→7.2ns, tRFC 226→161ns. 단, tRCD는 9.5→9.8ns로 소폭 증가 (감소된 charge level 때문). ET는 거의 항상 유리하므로 기본 적용.

#### Low-Power (LP) Mode (DUAL)
- LL mode와 동일한 DUAL configuration 사용. 차이는 memory controller의 timing parameter 설정.
- 한쪽 paired cell은 GND 상태로 charge leakage가 거의 없음 → charged cell이 ½ VDD 이하(0.16V)까지 떨어져도 sensing 가능
- SPICE simulation: tREF 7.8μs → 27.3μs (+3.5×). tREFI 7.8μs → 54.6μs (×7). Row 수가 절반으로 줄어들어 refresh operation 횟수 86% 감소 (8K → 4K)
- w/ ET: tRCD 13.8→12.3ns, tRAS 39.4→21.4ns, tWR 12.5→7.2ns, tRFC 260→175ns

## 핵심 기여

1. **핵심 아이디어:** 데이터센터의 만성적인 memory under-utilization을 낭비가 아닌 latency/power 최적화 resource로 전환. Under-utilized capacity를 complementary cell pair로 활용.

2. **주요 기여:**
   - 최초의 non-destructive, agile mode switching DRAM architecture
   - LP mode를 통한 refresh power 85.7% 절감 (기존 연구들은 latency만 고려)
   - 거의 0에 가까운 area overhead (70 NAND2 gates) → vendor adoption 장벽 최소화

3. **Broader significance:**
   - 데이터센터 operator에게: 추가 hardware cost 없이 performance/power trade-off 최적화 가능
   - DRAM vendor에게: single design으로 high-end/low-cost 시장 모두 커버 가능
   - CXL memory pooling 등장 시에도 local memory의 Agile-DRAM 적용 가능 (far memory에도 확장 가능)

## 주요 결과

Agile-DRAM의 핵심 차별점: **non-destructive, low-latency mode switching**. Mode register는 SINGLE / DUAL / TRANSITION 세 state를 가짐.

#### LL-to-MC (130ns)
1. Hypervisor가 memory controller programming: all-bank precharge (15ns) → MRS로 DUAL→SINGLE 전환 (15ns) → 최대 16개 bank reactivation (~100ns)
2. 총 ~130ns, tRFC보다 짧은 overhead
3. Odd subarray의 host physical address를 새 VM에 할당 → 독립 cell로 사용

#### MC-to-LL (64ms wait, data non-destructive)
1. VM deactivation 시 hypervisor가 memory controller programming
2. MRS로 DRAM을 TRANSITION state로 전환
3. TRANSITION state: paired row activation 시 time delay 적용 (Figure 8). ACT1(기존 data) → bitline 구동 → delay (>tRCD) → ACT2(미사용 row에 complementary 신호 overwrite). RowClone [36]과 유사한 원리
4. 64ms (one refresh period) 대기: auto-refresh가 모든 cell을 replenish → full data duplication 보장
5. 대기 중에도 남은 VM은 MC mode parameter로 memory 접근 가능 (conventional DRAM과 동일 latency)
6. 이후 MRS로 DUAL 전환 + timing parameter 갱신 (130ns)
7. 남은 VM은 even subarray만 사용, odd subarray는 complementary storage로 활용 → LL mode 동작

#### LP-to-LL (64ms wait)
1. Hypervisor가 memory controller refresh interval을 LL mode에 맞게 조정 (LP mode에서 depleted charge 보상)
2. 64ms간 auto-refresh로 cell replenish
3. 이후 LL mode timing parameter 적용
4. DRAM은 계속 DUAL state 유지 → MRS 불필요

#### LL-to-LP (instant)
1. Hypervisor가 timing parameter만 LP mode로 변경
2. DRAM DUAL state 유지 (MRS 불필요)
3. Auto-refresh interval 완화 → standby power 감소
4. DDR5 deep power-down 대비 장점: re-initialization 불필요 → 빠른 재활성화

#### CLR-DRAM과의 비교
| 항목 | CLR-DRAM | Agile-DRAM |
|------|----------|------------|
| Mode switching | Destructive (data loss) | Non-destructive |
| MC→HP/LL 전환 | 전체 data read-rewrite (>10s for 256GB) | TRANSITION mode + 64ms wait |
| Service disruption | 있음 (co-located workload까지 차단) | 없음 (전환 중에도 memory 접근 가능) |
| Area overhead | 3.2% (insulating transistor + column I/O) | negligible (70 NAND2 gates) |
| Additional mode | 없음 | LP mode (refresh reduction) |

## 평가

### Methodology

| 항목 | 내용 |
|------|------|
| Simulator | Ramulator [17] + Pintool [24] trace extraction (100M instruction fast-forward) |
| Processor | 1-4 core, 4GHz, 4-wide issue, 16 MSHRs/core |
| LLC | 64B cacheline, 8-way, 8MB total |
| DRAM | DDR4-2400, 1ch, 1 rank, 4Gb density, FR-FCFS-Cap scheduling |
| Benchmarks | SPEC CPU2006 23종 (11 memory-intensive: MPKI>1, 12 non-intensive) |
| Energy | DRAMPower [4]로 command trace 기반 추정 |
| Synthesis | Synopsys Design Compiler, 32nm library |

### Single-Core Performance (Figure 9)

**LL mode w/ ET:**
- 전체 평균 speedup: 6.9%
- Memory-intensive: 14.3%, Non-intensive: 0.19%
- 최대 speedup: CactusADM 25.8% (high MPKI + low row buffer hit ratio)
- libquantum은 high MPKI지만 high row buffer hit ratio → 4.0%로 낮음

**LP mode w/ ET:**
- 전체 평균 speedup: 5.0%
- Memory-intensive: 10.3%, Non-intensive: 0.1%
- 최대: CactusADM 20.5%

**DRAM Energy:**
- LL mode: 9.0% 감소 (평균), memory-intensive 15.5% 감소, 최대 CactusADM 22.4%
- LP mode: 7.4% 감소 (평균), memory-intensive 12.7% 감소

### Multi-Core Performance (Figure 10)

4-core random mix 15종 (H/M/L = 5/5/5):
- H category (3+ memory-intensive workloads): LL mode 17.0% speedup, LP mode 9.2%
- M category: 중간 수준
- L category (3+ non-intensive): LL mode 1.9%, LP mode 1.2%

### Standby Power (Figure 11)

Micron DDR power model [26] 기반:
- IDD5 (processor idle 시 DRAM current): LP mode 31.6% 감소
- IDD6 (self-refresh current): LP mode 85.7% 감소
- IDD5 savings가 낮은 이유: static current로 precharge state 유지 비중이 큼

### Hardware Overhead

SystemVerilog synthesis 결과:
- 추가 logic: global row decoder + command decoder에 mode register 및 delay logic
- 면적: bank당 75μm² (~30 NAND2 gate equivalents)
- 16-bank chip 기준 mode register와 delay logic 공유 → 총 70 NAND2 gates
- 100mm² DRAM die에서 negligible (사실상 0%)

## 구현

- DRAM cell array 변경 없음. 수정은 peripheral logic에만 국한:
  - Mirrored mat 구조 (bitline routing 방향만 변경)
  - Global decoder: OR gate 2개 추가
  - Command decoder: mode register + delay logic + MRS command handler
- 70 NAND2 equivalent gate → 기존 DRAM die의 unused space에 흡수 가능
- Memory controller 수정: mode별 timing parameter table, mode switching sequence 관리

## 관련 연구와의 비교 (Table III)

| 기법 | DRAM Type | Max Speedup | Agile Switch | Capacity Reduction | Area Penalty |
|------|-----------|-------------|--------------|--------------------|--------------|
| Dynamic Asymmetric Subarray [23] | DDR3-1066 | 21% | No | 0% | 3% |
| TL-DRAM [19] | DDR3-1600 | 8.9% | Yes | 0% | 3.15% |
| CLR-DRAM [25] | DDR4-2400 | 59.8% | No (destructive) | 0-50% | 3.2% |
| **Agile-DRAM** | **DDR4-2400** | **25.8%** | **Yes (agile)** | **0-50%** | **0%** |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2024HPCA-summarize/agile-dram-agile-trade-offs-in-memory-capacity-latency-and-energy-for-data-centers.md|전체 요약 보기]]
