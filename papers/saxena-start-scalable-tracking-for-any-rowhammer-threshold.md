---
tags: [paper, 2024, 2024HPCA, topic/cache, topic/dram, topic/rowhammer, topic/storage, topic/virtual-memory]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024HPCA-summarize/start-scalable-tracking-for-any-rowhammer-threshold.md"
---

# START: Scalable Tracking for Any Rowhammer Threshold

**Venue:** 
**저자:** 

## 개요

Rowhammer Threshold (TRH)는 2014년 139K(DDR3) → 2020년 4.8K(LPDDR4)로 30배 감소했으며, 이 추세가 지속되면 2020년대 말 sub-100 도달 예상 (Figure 1a). TRH 감소에 따라 potential aggressor row 수가 반비례로 증가하여 tracking resource 요구량도 비례 증가.

현존 tracker의 한계:
- **Graphene [36]:** TRH 4K에서 340KB이지만 TRH 64에서 8MB 이상 (counter 5-bit + row-id 17-bit 조합 시 bank당 109KB가 ideal tracker의 bank당 80KB보다 큼). Design-time에 worst-case storage 결정 필요.
- **DSAC-TRR [19]:** Samsung의 industrial tracker. 13.9% escape probability로 secure하지 않음. Effective threshold = TRH/2 − ACT_tREFI (ACT_tREFI 최대 255) → TRH 500 미만으로 확장 불가.
- **Hydra [37]:** SRAM 186KB로 TRH 256까지는 동작하나, TRH 64에서는 SRAM 544KB 필요하고 proportional storage 없으면 slowdown 34%. Group-level → row-level 전환 시 imprecise tracking.

**핵심 통찰:** 64GB memory (8M rows) 중 typical workload는 64ms 내 평균 ~300K rows(4%)만 touch (Table III). Demand-driven allocation으로 dedicated SRAM을 대체 가능.

## 방법론

### 1. START-Static (Naive Design)

16MB 16-way LLC 중 8-way를 고정 reserved하여 8M rows의 1-byte counter 저장. 각 cache line(64B)이 64개 row의 untagged counter 저장. Row address hashing으로 set index → 3-bit로 way 선택 → 6-bit로 byte-in-line 선택.

**문제:** LLC capacity 50% 상실 → 평균 7.4% slowdown.

### 2. START-Dynamic (Optimized Design)

**핵심 아이디어:** 64ms 주기마다 0-way에서 시작, demand에 따라 set별로 1-way → 2-way → 8-way로 allocation 증가.

#### Set Allocation Counter (SAC) Table
- 16K sets × 2-bit/set = 4KB SRAM (LLC 크기에만 의존, TRH와 무관)
- SAC=00: 0-way (default)
- SAC=01: 1-way reserved, 32 tagged entries (9-bit row-tag + 7-bit counter = 2 bytes/entry)
- SAC=10: 2-way reserved, 각 way 32 tagged entries, even/odd tag로 분할
- SAC=11: 8-way reserved, 512 untagged entries (모든 row가 designated byte 보유)

#### Operation
1. Row activation 시 memory controller가 LLC에 row address 전송
2. LLC가 row address hash → set + SAC 조회
3. SAC=00이면 way allocation 후 tracking entry 생성 (counter=1), SAC→01
4. 기존 allocation이면 tagged entry search → counter increment
5. Counter가 TRH 도달 시 reset + memory controller에 mitigation signal

#### Periodic Reset과 Threshold
- 64ms마다 SAC table과 reserved way reset → 0-way로 복귀
- Reset이 refresh와 unsynchronized → attacker가 reset 전 (T-1) + reset 후 (T-1) activations 가능
- Effective TRH = T/2로 설정 (common in prior trackers [36], [37]). TRH 256 target 시 T=128로 tracking.

#### START-LITE 변형
- Maximum SAC=01로 제한 (최대 LLC 6.25% 사용)
- 1-way(32 entries) 초과 시 memory-mapped로 fallback
- 512K entries capacity가 평균 workload의 unique rows(~330K)를 수용 → metadata memory access infrequent

### 3. Memory-Mapped START (START-M)

Large-memory systems (512GB, 64GB/core) 또는 higher TRH (4K: 12-bit row-tag + 11-bit counter) 지원.

#### Memory-Mapped Tracking Table (MTT)
- 512GB memory, 64M rows, TRH 4K: MTT 82MB를 addressable memory space에 배치
- START-D와 동일하게 demand-driven SAC 기반 allocation (0→1→2→8 way)
- 각 tracking entry 3 bytes (12-bit row-tag + 11-bit counter), 64B line당 21 entries

#### Cold Miss Avoidance
- 64ms reset 후 first-time access는 MTT를 접근하지 않고 counter=1로 LLC에 install
- Set 내 entry eviction 발생 시에만 MTT 접근 (해당 set의 MTT counter를 lazily reset)
- 8-way allocation 시 2.75M entries 저장 가능 → workload의 64ms 내 unique rows(최대 2.2M)를 초과하여 virtually zero MTT access

## 핵심 기여

1. **핵심 아이디어:** Rowhammer tracking의 dedicated SRAM을 LLC의 demand-driven dynamic allocation으로 대체. 대부분의 workload는 64ms 내 소수의 row만 접근하므로 평균 LLC 9.4%만 사용하여 ideal tracker 수준의 성능 달성.

2. **주요 기여:**
   - 최초의 configurable Rowhammer tracker (boot-time TRH 설정만으로 sub-100까지 지원)
   - 4KB SRAM only로 모든 prior tracker 대비 100× 이상 storage 절감
   - START-M으로 512GB+ large-memory까지 확장 가능

3. **Broader significance:**
   - Design-time worst-case provisioning 문제 해결 → 시스템 수명 내 threshold 감소에 자동 적응
   - Mitigation action과 orthogonal → 어떤 mitigative action과도 결합 가능 (victim refresh, row swap, rate control 등)
   - Predictor virtualization paradigm [30]을 Rowhammer security domain에 최초 적용

## 주요 결과

### Methodology

| 항목 | 내용 |
|------|------|
| Simulator | ChampSim [15] (cycle-level multi-core) + DRAMSim3 [31] (DDR5) |
| Processor | 8 OoO cores, 4GHz, ROB 352, 6-wide fetch/dispatch, 5-wide retire |
| L1-I/D | 32KB, 8-way |
| L2 (private) | 512KB, 8-way |
| LLC (shared) | 16MB, 16-way, 64B lines, SRRIP, non-inclusive |
| Memory | 64GB DDR5, 2ch (32GB DIMM/ch), 4800 MT/s, 32 banks×1 rank×2 sub-ch |
| Rows | 64K rows/bank, 8KB row size, 총 8M rows |
| Timing | tRCD=tCL=tRP=16.6ns, tRC=48.6ns |
| Workloads | SPEC2017 10종, LIGRA 13종 (graph), PARSEC 5종 — 총 28종 |
| Metrics | Normalized IPC, weighted speedup, LLC capacity loss, cache misses |
| Power | CACTI 7.0 (22nm), Micron DDR power model |

### Single-Program Performance (Figure 6)

**TRH=256:**
- Ideal tracker: 0.2% slowdown (mitigation only)
- START-S: 7.4% slowdown (50% LLC loss)
- START-D: 1.1% slowdown (within 1% of ideal)

**TRH=64:**
- Ideal tracker: 1.3% slowdown
- START-D: 2.2% slowdown (within 1% of ideal)

### LLC Capacity Loss (Figure 7)

- START-S: constant 50%
- START-D: 평균 9.4%, 25/28 workloads가 10% 미만 사용
- 3 workloads만 500K+ rows touch (fotonik3D: 2.1M, mcf: 1.2M, CF: 677K)

### Cache Misses (Figure 8)

- START-S: baseline 대비 평균 21% 증가
- START-D: baseline 대비 평균 2.3% 증가 (about 1/10 of START-S)

### Sensitivity to Cache Size (Figure 9)

12MB 12-way LLC (8-way reserved) 및 24MB 12-way LLC (4-way reserved)에서도 START-D는 ideal tracker와 거의 동일한 slowdown 유지. 1-way 이상 reservation이 exceedingly rare.

### Blast Radius Sensitivity (Figure 10)

BR=1,2,4 평가:
- TRH=256, BR=4: START-D 1.3%, ideal 0.5%
- TRH=64, BR=4: START-D 11.2%, ideal 10.2%
- 모든 case에서 within 1% of ideal

### START-M: Large-Memory (Figure 13, 14)

512GB memory (64GB/core), TRH=256:
- START-M: 1.3% slowdown (ideal 0.2%)
- TRH=64: 2.3% (ideal 1.3%)
- LLC capacity loss: 평균 11.4%

### Threshold Scalability (Figure 15)

TRH 4K → 16까지 평가:
- TRH 4K: START 1% overhead (ideal negligible)
- TRH 16: START 9% overhead (ideal 8%)
- 전 구간에서 within 1% of ideal

### Multi-Programmed/Multi-Threaded (Figure 16)

51 workloads (single + mix + CloudSuite), TRH=64:
- START-D: 평균 1.9% slowdown (ideal 1%)
- START-LITE: 2.7% slowdown (Hydra-544KB의 3.2%보다 낮음, SRAM은 136× 적음)
- Hydra-186KB: 8.6% slowdown
- START-D 최대 slowdown: 6.7% vs Hydra-544KB: 18.6%

### Storage & Power

- Dedicated SRAM: 4KB SAC table + 2B TRH register
- DRAM power: 105mW 증가 (0.3% overhead)
- Cache dynamic power: 93mW 증가 (11.5%), but leakage 포함 overall cache power 0.9% 증가

### Security Analysis

**Theorem-1:** START는 각 row에 대해 (a) TRH/2 activations에서 mitigation 발행, (b) 이후 매 TRH/2 activations마다 mitigation 발행.

Proof: Phase-1(reset→first mitigation): counter = T_true 항상 exact. Phase-2(mitigation간): counter reset 후 exact tracking 계속.

**Adaptive attack resistance:**
- Reserved way는 replacement algorithm에서 제외 → cache line eviction으로 tracking entry 공격 불가
- Tracking access는 demand access의 critical path 외부 → timing side channel 없음
- Half-Double [2] 공격 대응: victim refresh로 인한 activation도 count에 포함

## 구현

- ChampSim multi-core simulator에 START 구현
- DRAMSim3에 DDR5 configuration (2 sub-channels/channel, BL=16, 64B line) 추가
- SAC table: 4KB SRAM, set index로 direct lookup
- LLC controller 수정: SAC 기반으로 lookup/replacement에서 way exclusion
- Open-source: https://github.com/Anish-Saxena/rowhammer_champsim (Apache 2.0)

## Hydra와의 비교 (Table IV, TRH=64)

| 속성 | Hydra-544KB | START-D |
|------|-------------|---------|
| Dedicated SRAM | 544KB | 4KB |
| Memory-mapped Storage | 5MB | 0 |
| Performance Overhead | 3.2% | 1.9% |
| SRAM Provisioned Dynamically | ✗ | ✓ |
| Scales to Arbitrary TRH | ✗ | ✓ |
| Precise Tracking | ✗ | ✓ |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]
- [[paper-wiki/concepts/storage.md|Storage]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2024HPCA-summarize/start-scalable-tracking-for-any-rowhammer-threshold.md|전체 요약 보기]]
