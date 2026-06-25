---
tags: [paper, 2024, 2024MICRO, topic/cache, topic/dram, topic/gpu, topic/storage]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024MICRO-summarize/cachecraft-enhancing-gpu-performance-under-memory-protection-through-reconstructed-caching.md"
---

# CacheCraft: Enhancing GPU Performance under Memory Protection through Reconstructed Caching

**Venue:** 
**저자:** 

## 개요

### 1.1 GPU ECC의 두 가지 방식

현대 GPU는 메모리 오류 방지를 위해 ECC(Error Correcting Codes)를 사용하며, HBM과 GDDR에서 서로 다른 접근 방식을 취함:

- **Side-band ECC (HBM):** HBM은 ECC redundancy를 위한 별도의 셀과 핀을 갖추고 있어 데이터와 redundancy를 동시 전송 가능. 대역폭 손실 없음. 예: H100은 5개의 HBM3 스택으로 3.3TB/s 대역폭 달성. 그러나 HBM은 패키징 복잡성으로 인한 높은 비용과 제한된 공급이 문제.
- **In-band ECC (GDDR):** GDDR은 비ECC 칩을 사용하므로 데이터와 redundancy를 동일 채널에서 순차 전송. NVIDIA L40S는 12개의 GDDR6 칩으로 0.86TB/s. GDDR6 칩은 2개 채널로 분할되어 32B 최소 접근 단위를 유지.

### 1.2 In-band ECC의 구체적 비용

NVIDIA의 in-band ECC 구현 (NVIDIA 특허 기반):

- **데이터 레이아웃:** 2KiB GDDR row에 15개의 128B 데이터 블록 + 1개의 128B redundancy 블록 배치. 각 32B 데이터 청크당 2B redundancy 할당 → redundancy ratio 6.25%, storage efficiency 93.75%.
- **32B 섹터 접근 비용:** 단일 섹터 요청에 2번의 순차적 32B 메모리 접근 필요 (redundancy block 먼저 fetch 후 data block). tCCDL 지연 추가 + 100% 대역폭 오버헤드.
- **Redundancy Cache (RCache):** 각 memory partition에 32B RCache를 두어 redundancy block 재사용. Full cache line (128B) 접근 시 5회 접근으로 감소 (4 data + 1 redundancy) → 25% 오버헤드.
- **그러나 fine-grained memory interleaving이 RCache 효과를 제한:** 256B channel interleaving + BankGroup interleaving으로 4KiB 페이지가 32개 BankGroup에 분산. Redundancy block의 32B 중 8B만 동일 cache line에 속하고 나머지 24B는 다른 페이지/4KiB 떨어진 데이터에 속함 → spatial locality 저하.

### 1.3 실측 데이터 (NVIDIA T4 GPU)

ECC On/Off 비교 실험 결과 (Rodinia, Lonestar, DOE MiniApps, SPEC ACCEL):

- **메모리 접근 증폭(amplification factor):** 평균 41.9%, 최대 147% (SPEC ACCEL ep). 32개 벤치마크 중 27개가 25% 초과, 14개가 50% 초과.
- **IPC 저하:** 메모리 바운드 워크로드에서 증폭률과 비례. 예: ostencil은 39% 증폭 → 40% IPC 저하, kmeans는 35% 증폭 → 26% 저하.
- **ECC 비활성화 시:** SPEC ACCEL 기준 실행 시간 최대 120% 단축, 에너지 최대 115% 절감 (NVIDIA Tesla K40c).

**핵심 문제:** 32B 섹터 크기를 유지하면서 2B redundancy를 별도 접근으로 가져오는 cache-centric 설계가 근본 원인.

## 방법론

### 3.1 방법론

| 항목 | 구성 |
|------|------|
| **Simulator** | Accel-Sim, cycle-level GPU simulator |
| **Target GPU** | NVIDIA RTX3070 (Ampere), 46 SMs, 1132MHz |
| **Memory** | 8 GDDR6, 16 channels, 14Gbps, 448GB/s |
| **L1 Cache** | 256KiB, 8 banks (CacheCraft: 5 banks) |
| **L2 Cache** | 4MiB, 16-way, 128B lines |
| **Schemes** | Non-ECC, Baseline (in-band+RCache), CacheCraft (balanced) |
| **Workloads** | 30개: Rodinia (13), Polybench (5), Parboil (7), GraphBIG (5) |
| **분류** | Low(<25%), Mid(25-50%), High(≥50%) bandwidth utilization |

### 3.2 Memory Access Amplification (Fig. 8a)

- **Baseline:** 평균 41.9% 증폭, 범위 15.2% (RO-PTF) ~ 96.9% (GB-SSSP).
- **CacheCraft:** 평균 21.9% 증폭, 범위 10.2% (GB-SSSP) ~ 28.2% (RO-KM).
- **개선폭:** 평균 47.8% 감소, 최대 89.4% 감소 (GB-SSSP: 96.9% → 10.2%). GraphBIG 5개 중 4개 워크로드에서 80% 이상 감소.

### 3.3 System Performance (IPC Slowdown, Fig. 8b)

| Bandwidth Utilization | Baseline | CacheCraft |
|----------------------|----------|------------|
| Low | ~1% | ~1% (PA-SGM 예외: 2% vs 10%, on-chip congestion) |
| Mid | 23.3% (RO-HBS) | 7.4% (RO-HBS) |
| High | 평균 33.2% | 평균 18.1% |
| 최대 개선 | - | PA-SPMV: 52.6% → 16.6% (23.5% speedup) |

### 3.4 DRAM Energy (Fig. 8c)

- Baseline 평균 에너지 증가: +29.0% (저/중/고 utilization: 20.2%/41.9%/45.9%).
- CacheCraft 평균 에너지 증가: +14.1% → **extra energy 51.3% 감소**.
- Activation energy는 30B-only row 접근으로 인한 추가 activate/precharge로 소폭 증가.

### 3.5 Memory Layout 비교 (Fig. 10)

- BO layout: 최고 성능이나 87.5% storage overhead.
- CO layout: 93.75% storage이나 RMW overhead로 일부 워크로드에서 baseline보다 열등.
- Balanced layout: BO에 근접한 성능 + 92.31% storage → 최종 채택.

### 3.6 Reliability 분석

CacheCraft는 더 작은 블록(30B/8B)을 동일한 2B redundancy로 보호:

- **Uncorrectable error rate:** 32B 블록 대비 11.44% 감소 (더 작은 블록에서 multi-bit error 확률 감소).
- **Undetected error rate:** 20.8% 감소. 이유: (1) 블록 크기 감소로 3+ bit error 확률 16.7% 감소, (2) 사용되는 syndrome 수 감소 (256 vs 272)로 miscorrection 확률 0.39% vs 0.41%.

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

- Accel-Sim 시뮬레이터 기반 구현.
- L1 cache bank 수: 4→5로 증가.
- Coalescer-L1 간 추가 포트.
- 128B cache line 및 tag logic 유지로 software-agnostic.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2024MICRO-summarize/cachecraft-enhancing-gpu-performance-under-memory-protection-through-reconstructed-caching.md|전체 요약 보기]]
