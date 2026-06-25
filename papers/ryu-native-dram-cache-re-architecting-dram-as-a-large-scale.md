---
tags: [paper, 2024, 2024ISCA, topic/cache, topic/dram]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024ISCA-summarize/native-dram-cache-re-architecting-dram-as-a-large-scale-cache-for-data-centers.md"
---

# Native DRAM Cache: Re-architecting DRAM as a Large-Scale Cache for Data Centers

**Venue:** 
**저자:** Yesin Ryu†§ (Samsung Electronics / Sungkyunkwan Univ.), Yoojin Kim†, Giyong Jung†, Jung Ho Ahn‡ (Seoul Nat'l Univ.), Jungrae Kim† (Sungkyunkwan Univ.)

## 개요

### 1.1 코어 수 급증과 LLC 용량 요구

데이터센터 CPU 코어 수는 AMD Bergamo 128코어, Intel Sierra Forest 288코어, 2037년 IRDS 예측 640코어까지 급증하고 있다. 현재 LLC는 코어당 1.5~4MB 수준이나, 코어 수 증가에도 LLC가 비례 확장되지 않으면 코어당 캐시 용량 감소로 성능·에너지 효율이 크게 저하된다.

### 1.2 기존 LLC 확장 접근법의 한계

- **SRAM 3D V-Cache (AMD):** SRAM 캐시 다이를 코어 다이 위에 TSV로 적층. 8MB/코어 추가. SRAM 밀도는 logic 대비 scaling이 느림 (IRDS: 2022-2037 logic 13.5× vs L3 SRAM 10.6×).
- **HBM2E DRAM Cache (Intel Sapphire Rapids):** 64GB DRAM을 cache layer로 활용. 1GB/코어의 대용량 제공 가능.

**DRAM cache의 장점:** 1T-1C 셀 구조로 6T SRAM 대비 우수한 밀도, 대용량에서 높은 hit ratio 기대. **단점:** 긴 access latency (charge sensing), metadata overhead.

### 1.3 기존 DRAM Cache 설계의 구조적 문제

**Tags-in-DRAM 접근법 (LH-Cache, Accord, DEC 등)의 근본적 한계:**
- **Metadata 접근 오버헤드:** 16-way 6B/way metadata = 96B. HBM3의 tCCD_L=2.5ns로 metadata block 3개 순차 전송 시 최소 7.5ns 추가 latency. Tag matching이 DRAM 외부에서 수행되어 data 접근 전에 metadata 블록을 off-chip 전송해야 함.
- **LH-Cache [Loh&Hill, MICRO'11]:** 한 DRAM row = 한 cache set. Metadata 3블록 + data 29블록. RD 시 metadata 3회 read 후 tag matching, hit 시 data 1회 추가 read → `CL + 3×tCCD_L + CL` latency. MissMap(수 MB SRAM)으로 miss latency 완화하나 hit latency는 여전히 큼.
- **Alloy-Cache [Qureshi&Loh, MICRO'12]:** Metadata+Data를 하나의 TAD로 통합, extra pin으로 동시 전송. 단일 RD로 hit 시 즉시 data 제공. 그러나 **direct-mapped로 제한**되어 conflict miss에 취약. Write hit 시에도 metadata read + data write 2회 전송 필요.

**핵심 진단:** 기존 설계는 핵심 cache 기능(tag matching, way selection)을 DRAM **외부**에서 수행하므로, 고집적도의 set-associative cache를 구현하려면 metadata off-chip 전송량이 associativity에 비례하여 증가 → 성능·에너지 모두 불리. "Tag matching과 way selection을 DRAM **내부**에서 수행하는 근본적 재설계"가 필요.

## 방법론

### 3.1 방법론

| 항목 | 구성 |
|------|------|
| **Simulator** | gem5, DRAM cache tailored framework |
| **CPU model** | AMD EPYC 7773X chiplet (Zen 3), 8 cores, 3.2 GHz, 8-wide issue, 192-entry ROB |
| **L1 I/D** | 32KB/thread, 8-way |
| **L2** | 256KB/thread, 8-way |
| **DRAM Cache (LLC)** | 1GB, HBM3-6400 기반, 4 channels (8 pseudo), 51.2 GB/s/ch |
| **DRAM Cache timing** | tRCD=7.5ns, tRP=7.5ns, CL=7.5ns, 1KB rows |
| **Main memory** | DDR4-3200, 1 channel, 2GB, 15ns tRCD/tRP/CL |
| **Inter-chiplet** | 60ns round-trip (Zen 4 기준) |
| **Workloads** | SPEC CPU 2017 (7 mixes, Table IV), NPB, GAP benchmark suite |
| **Simulation** | Fast-forward 1B instr. → warmup 100M → measure 100M |

### 3.2 비교 대상

| Scheme | Associativity | 특징 |
|--------|--------------|------|
| **BEAR** [Chou+, ISCA'15] | Direct-mapped | Alloy-Cache 개선, MAP-I predictor |
| **LH16** [Loh&Hill, MICRO'11] | 16-way | Tags-in-DRAM, MissMap 256KB, HBM row size 맞춤 |
| **Accord** [Young+, ISCA'18] | 4-way | LH-cache + Way predictor |
| **DEC** [Hameed+, 2020] | 16-way | Tag-Data Decoupling, metadata/data concurrent access across banks |
| **NDC8** | 8-way | Half row 사용, 에너지 최소화 |
| **NDC16** | 16-way | Full row 사용, 4KB page conflict miss zero |

NDC는 predictive mechanism (MissMap, MAP)을 사용하지 않음 → on-chip SRAM overhead zero.

### 3.3 Latency (SPICE Simulation)

20nm-class DRAM, SS corner, 100°C 조건 (Table I):

| Parameter | 4-way | 8-way | 16-way |
|-----------|-------|-------|--------|
| tPCD (pre-compare) | 0.80 ns | 0.23 ns | 0.86 ns |
| tCOMP (compare) | 1.03 ns | 0.83 ns | 0.23 ns |
| **ΔCL (total)** | **1.03 ns** | **1.06 ns** | **1.09 ns** |

16-way에서도 read latency 증가는 **1.09ns 미만**. 기존 DRAM 대비 2 cycle (1.25ns) 추가로 반영.

### 3.4 성능 (Fig. 13)

**IPC speedup (vs DEC, geomean):**

| Workload | NDC16 vs DEC |
|----------|-------------|
| SPEC CPU 2017 | **+2.8%** (max +8.4%) |
| NPB | **+52.5%** (max +140.6%) |
| GAP | **+44.2%** (max +85.5%) |

**Hit ratio 분석 (Fig. 13b):**
- NDC16, LH16, DEC 모두 16-way로 cache hit ratio는 유사
- NDC16은 row buffer hit ratio에서 우위 (동일 row 내 모든 way 접근 가능)
- BEAR는 direct-mapped로 cache hit ratio 열세

**Average hit latency (Fig. 13c):**
- LH16/Accord/DEC는 추가 metadata transfer로 인해 BEAR 대비 2~3배 높은 hit latency
- NDC16은 in-subarray tag matching + high row buffer hit으로 BEAR보다도 낮은 hit latency

### 3.5 DRAM 에너지 (Fig. 14)

| Workload | NDC16 vs DEC (energy reduction) |
|----------|-------------------------------|
| SPEC | **-17.7%** (up to -24.4%) |
| NPB | **-25.8%** (up to -33.7%) |
| GAP | **-34.6%** (up to -47.4%) |

요인:
- High row buffer hit ratio → activation energy (IDD0) 감소
- Off-chip metadata transfer 제거 → read/write energy (IDD4R/IDD4W) 감소
- Read miss 시 불필요 data transfer 제거 → 추가 절감

### 3.6 Area Overhead

HBM3 die (11×11 mm²) 기준:
- Column 당 2 NMOS 추가 (N3, N4) × subarray 내 column 수
- Way selection circuit: D-MAT 확장 영역 내 배치 (추가 면적 없음)
- **Total die area increase: 0.6%**
- Bank peripheral (victim buffer 등): <0.03%, negligible

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

| 항목 | 세부사항 |
|------|---------|
| **Subarray 구조** | MD-MAT + D-MAT. MD-MAT에 tag 저장, D-MAT에 data 저장 |
| **CAM 구현** | Column-based, precharge transistor 재활용. 추가 transistor: N3, N4 (column당 2개) |
| **Way selection** | Random replacement, V/D bit 기반 우선순위 |
| **Victim buffer** | 16-entry, credit management |
| **Interface** | CR pin 1개 추가, RES command 1개 추가 |
| **Die size** | +0.6% |
| **기준 공정** | 20nm-class DRAM, HBM3 기준 |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2024ISCA-summarize/native-dram-cache-re-architecting-dram-as-a-large-scale-cache-for-data-centers.md|전체 요약 보기]]
