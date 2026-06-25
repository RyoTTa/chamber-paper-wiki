---
tags: [paper, 2023, 2023HPCA, topic/cache, topic/compression, topic/dram, topic/nvm, topic/storage]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023HPCA-summarize/baryon-efficient-hybrid-memory-management-with-compression-and-sub-blocking.md"
---

# Baryon: Efficient Hybrid Memory Management with Compression and Sub-Blocking

**Venue:** 
**저자:** 

## 개요

Hybrid memory는 빠른 DRAM(fast memory)과 느리지만 대용량인 NVM(slow memory)을 결합하여 높은 성능과 큰 용량을 동시에 달성한다. 그러나 제한된 fast memory 용량과 slow memory 대역폭이 성능의 병목이 된다.

기존 기법들의 한계:
- **Sub-blocking** (sectoring): 데이터 블록을 여러 sub-block으로 분할하여 실제 필요한 sub-block만 fast memory로 fetch. 기존 설계들은 한 physical block이 단일 data block의 sub-block만 담을 수 있어, 미사용 sub-block 공간이 낭비됨 (Fig. 1a).
- **Memory compression**: 이웃 데이터 간 값 유사성을 활용하여 여러 block을 하나로 압축. 압축률이 낮은 block은 공간 낭비 (Fig. 1b).
- **둘을 결합할 때의 문제:** (1) fine-grained 관리로 인한 metadata storage 폭증 — remap table이 32×까지 증가 가능, (2) 압축 + sub-blocking으로 인한 복잡하고 불규칙하며 빈번하게 변하는 data layout 관리의 어려움.

## 방법론

### 3.1 방법론

| 항목 | 구성 |
|------|------|
| Simulator | zsim (Pin-based) |
| Processor | x86-64, 3.2 GHz, 16 cores |
| LLC | 16 MB shared, 16-way, 38-cycle |
| Fast memory | DDR4-3200, 4 GB, 4 channels |
| Slow memory | NVM, 32 GB (1:8 ratio), 1333 MHz, read 76.92 ns / write 230.77 ns |
| Baselines (cache) | Unison Cache (sub-blocking only), DICE (compression only), Simple (neither) |
| Baselines (flat) | Hybrid2 (sub-blocking only, fully-associative) |
| Workloads | SPEC CPU2017 (16-copy rate), GAP (twitter, web-sk-2005), ResNet50/ResNext50 (OneDNN), memcached + YCSB-A/B |

### 3.2 Cache Mode 성능 (Fig. 9)

Baryon vs. Unison Cache: 평균 **1.38×**, 최대 **2.46×** speedup.
Baryon vs. DICE: 평균 **1.27×**, 최대 **1.68×** speedup.
Baryon-64B (64 B sub-block) vs. Unison Cache: 1.27× (compression + sub-blocking 효과).
Baryon-64B vs. DICE: 1.13×.
256 B sub-block 사용이 64 B 대비 추가 12.2% 성능 향상.

**예외:** 519.lbm_r은 write-intensive + CF ≈ 1.0으로 compression overhead만 추가되어 Unison Cache보다 느림.

### 3.3 Flat Mode 성능 (Fig. 10)

Baryon-FA vs. Hybrid2: 평균 **1.18×**, 최대 **2.50×** speedup.

### 3.4 성능 분석 (Fig. 11)

- **Fast memory serve rate:** pr.twi에서 37% (Unison), 44% (DICE) → 77% (Baryon)
- **Bandwidth bloat factor:** pr.twi에서 3.2 (Unison), 2.4 (DICE) → 1.8 (Baryon)
- 520.omnetpp_r은 serve rate 이미 높으나 fast memory bandwidth 49% 절감 → 1.64× speedup

### 3.5 Energy

Baryon: Unison Cache 대비 31.9% energy 절감, DICE 대비 13.0% 절감.
Baryon-FA: Hybrid2 대비 14.5% energy 절감.

### 3.6 Compression Scheme 분석 (Fig. 12)

- Zero block support (Z bit): CF 1.85 → 2.00, YCSB-A에서 8% 성능 향상
- Cacheline-aligned compression 필수: 미사용 시 11%~61% 성능 저하
- 5-cycle decompression latency의 영향: <1% (무시 가능)
- Adjacent block same CF 제한의 영향: 최대 12% 손실 (520.omnetpp_r)

### 3.7 Ablation Studies (Fig. 13)

- **Stage area size:** No stage area → 평균 34.5% 성능 저하. 8 MB로도 일부 workload 동작, 64 MB optimal.
- **Super-block size:** 8 blocks optimal. 너무 크면 conflict miss 증가 (505.mcf_r에서 50% 저하).
- **Two-level replacement:** Sub-block-only replacement 대비 25% 성능 저하.
- **Selective commit (k):** k=0 (write traffic only) 또는 k=∞ (stability only)보다 적절한 k가 우수. k=1,2,4 모두 유사 성능.

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

- Simulator modification: zsim에 cache/flat mode 지원 확장
- Stage tag array: 448 kB on-chip SRAM (8192 sets × 4 ways)
- Remap cache: 32 kB on-chip SRAM (super-block granularity)
- Total SRAM: 480 kB (prior works와 comparable)
- CACTI 7로 SRAM 구조 모델링
- Decompressor: FPC + BDI, 5-cycle latency

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2023HPCA-summarize/baryon-efficient-hybrid-memory-management-with-compression-and-sub-blocking.md|전체 요약 보기]]
