---
tags: [paper, 2024, 2024ISCA, topic/cache, topic/compression, topic/dram, topic/virtual-memory]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024ISCA-summarize/dylect-achieving-huge-page-like-translation-performance-for-hardware-compressed-memory.md"
---

# DyLeCT: Achieving Huge-page-like Translation Performance for Hardware-compressed Memory

**Venue:** 
**저자:** 

## 개요

### 1.1 Hardware Memory Compression의 Translation Overhead

Hardware memory compression [6][7][27][33]은 MC가 데이터를 투명하게 압축·이전하여 effective capacity 확장. 이를 위해 **CTE**라는 새로운 address translation layer 추가:

- CTE table: 모든 OS-visible 4KB page당 하나의 CTE (8B)를 DRAM에 저장하는 flat table.
- CTE cache: MC 내 small cache (128KB)로 CTE 캐싱.
- LLC miss/writeback 시 CTE 조회 후 physical→DRAM address 변환.

**Translation reach**: 128KB CTE cache ÷ 8B/CTE × 4KB/page = **64MB** → TLB의 huge page reach(>2GB) 대비 **32배 낮음**.

### 1.2 Irregular Workload + Huge Page 상황의 문제

- Real-system (Intel W-3175X): 2MB huge page 사용 시 4KB page 대비 **1.75× 평균 speedup** (Fig. 3).
- TMCC [27] (prior art):
  - Low compression (1.3×): no compression 대비 14% 성능 저하.
  - High compression (2.8×): 18% 성능 저하 (Fig. 4).
  - 주된 원인: CTE cache miss rate가 28%(GraphBig, 128KB cache)로 높음 (Fig. 5).
  - CTE cache를 512KB로 8배 늘려도 miss rate 34%→24% 감소에 그침.
- TMCC의 PTB embedding 최적화는 **huge page 환경에서 무용화**: huge page는 TLB miss(및 page walk)가 20배 감소하여 embedding이 적용될 기회가 거의 없음.

### 1.3 Naive 접근법의 실패

**Coarse-granularity compression** (2MB/page):
- Translation reach는 huge page와 동일해지지만, 2MB 전체를 compress/decompress 하면 bandwidth overhead가 극심.
- Irregular workload는 huge page 내에서도 access skew [20] → 2MB 이동 시 대부분의 데이터가 불필요하게 이동.
- Compression granularity를 4KB→128KB로 증가시켜도 high compression(2.8×)에서는 오히려 성능 악화 (Fig. 6: 4KB=18% → 128KB=46% slowdown). Decompression 빈도 증가 시 coarse granularity의 bandwidth overhead가 translation reach 이득을 상쇄.

---

## 방법론

### 3.1 방법론 (Table 3)

| 항목 | 상세 |
|------|------|
| **Simulator** | Gem5 [4] + Ramulator [18] + DRAMPower [5] |
| **CPU** | 4 OoO cores, 2.8 GHz, 4-wide, 224-entry RoB |
| **Cache** | L1D$/L1I$ 32KB, L2$ 256KB (1KB walker cache [23]), L3$ 2MB×4 (8MB) |
| **TLB** | 1024-entry |
| **Memory** | DDR4-3200, 1 channel, 8 ranks, FR-FCFS |
| **CTE cache** | 128KB (DyLeCT: 1MB reach/block, TMCC: 32KB reach/block) |
| **CTE cache hit latency** | 2 memory clocks |
| **Workloads** | GraphBig (9) + SPEC2017 (mcf, omnetpp) + PARSEC 3.0 (canneal) — huge page |
| **Compression** | Low (1.3× avg), High (2.8× avg) |
| **Warmup** | KVM fast-forward → atomic 5s warmup → 10ms detailed warmup → 40ms measurement |

### 3.2 성능 (Fig. 18)

| Compression | DyLeCT vs TMCC |
|-------------|:---:|
| Low (1.3×) | **+11%** |
| High (2.8×) | **+9.5%** |
| **Overall avg** | **+10.25%** |

- canneal: 최대 +17% (low compression, 가장 irregular한 access pattern).
- canneal high compression: +10% (ML0 축소로 CTE hit rate 하락 때문).
- DyLeCT 성능은 hypothetical upper bound (CTE always hit)에 근접.

### 3.3 CTE Cache Hit Rate (Fig. 19)

| Compression | TMCC | DyLeCT |
|-------------|:---:|:---:|
| Low (1.3×) | 70% | **96%** |
| High (2.8×) | 67% | **91%** |

- DyLeCT hit breakdown (High comp): pre-gathered block 77% + unified block 14%.
- High compression에서 hit rate 감소는 ML0 page 수 감소 때문 (Fig. 20).

### 3.4 Latency (Fig. 21)

LLC miss latency 증가량 (no compression 대비):

| Compression | TMCC | DyLeCT |
|-------------|:---:|:---:|
| Low (1.3×) | +9.5 ns | **+2.9 ns** |
| High (2.8×) | +12.8 ns | **+5.8 ns** |

### 3.5 Memory Traffic (Fig. 22, 23)

- DyLeCT의 CTE miss traffic: TMCC 대비 감소 (miss rate 개선).
- Total traffic per instruction: DyLeCT = TMCC의 93% (성능 향상으로 instruction count 증가).

### 3.6 DRAM Energy (Fig. 24)

- DyLeCT는 2× DRAM chips를 가진 no-compression 시스템 대비 **평균 60% DRAM energy per instruction** (16 ranks vs 8 ranks).
- Idle power(refresh, standby) 감소가 주요 요인.

### 3.7 Sensitivity Analysis (Fig. 25)

- DRAM page group size G=3 (2-bit short CTE)가 sweet spot: 66% of uncompressed pages in ML0.
- G=7 (3-bit short CTE)로 늘려도 ML0 비율 크게 증가하지 않음 + translation reach 감소 → 오히려 성능 저하.

---

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

- **Simulation only** (Gem5 기반). 실제 silicon 구현 없음.
- **Modified components**: Memory controller only (TMCC는 MC+L2 cache+page walker 수정 → DyLeCT가 더 단순).
- **Compression algorithm**: TMCC와 동일한 DEFLATE ASIC (4KB page decompression latency: 280ns).
- **Hardware 추가 logic**:
  - Static hash function (shifters + modulo).
  - Promotion/demotion comparator (5-bit access counter 비교).
  - Pre-gathered Table write logic (ML0 promotion 시 update).
- **Multi-MC 시스템**: 각 MC가 독립적인 DyLeCT 모듈, local DRAM만 관리 → coherence 불필요. Slightly restricted interleaving 영향 minimal [27].

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2024ISCA-summarize/dylect-achieving-huge-page-like-translation-performance-for-hardware-compressed-memory.md|전체 요약 보기]]
