---
tags: [paper, 2024, 2024HPCA, topic/disaggregation, topic/dram, topic/pim]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024HPCA-summarize/mimdram-an-end-to-end-processing-using-dram-system-for-high-throughput-energy-efficient-and-programmer-transparent-multiple-instruction-multiple-data-computing.md"
---

# MIMDRAM: An End-to-End Processing-Using-DRAM System for High-Throughput, Energy-Efficient and Programmer-Transparent Multiple-Instruction Multiple-Data Computing

**Venue:** 
**저자:** Geraldo F. Oliveira, Ataberk Olgun, Abdullah Giray Yağlıkçı, F. Nisa Bostancı, Juan Gómez-Luna, Saugata Ghose, Onur Mutlu (ETH Zürich / Univ. of Illinois Urbana-Champaign)

## 개요

### 1.1 PUD(Processing-Using-DRAM)의 Granularity 문제

Processing-Using-DRAM (PUD)은 DRAM array의 아날로그 동작 특성을 활용하여 대량의 bit-serial SIMD 연산을 in-situ로 수행하는 PIM 접근법이다. Ambit[61], SIMDRAM[101] 등은 DRAM subarray의 모든 column을 SIMD lane으로 활용하여 **16,384~262,144-bit wide SIMD** 실행을 가능하게 했다.

그러나 이 **크고 고정된 granularity**가 세 가지 근본적 한계를 야기한다:

1. **SIMD Underutilization:** 애플리케이션의 SIMD 병렬성이 DRAM row 크기보다 작거나 배수가 아닐 때 대부분의 SIMD lane이 낭비됨
2. **연산 제한:** Wide DRAM row에 걸친 column 간 interconnect 구현 비용이 높아, parallel map 연산만 가능 (vector reduction 불가)
3. **Programmability Barrier:** 수만 개 data element를 수동으로 PUD hardware에 매핑해야 하며, 적절한 compiler 지원 부재

### 1.2 정량적 동기 분석

저자들은 117개 애플리케이션(SPEC 2017, SPEC 2006, Parboil, Phoenix, Polybench, Rodinia, SPLASH-2)을 대상으로 LLVM auto-vectorization 분석 수행:

| 발견 | 수치 |
|------|------|
| Vectorization factor 범위 | 8 ~ 134,217,729 |
| DRAM row (65,536) 이상 VF를 가진 loop 비율 | **0.11%** |
| SIMDRAM SIMD utilization (12개 app 평균) | 매우 낮음 |

결론: real-world 앱의 SIMD 병렬성은 매우 가변적이며, PUD의 very-wide SIMD와 극히 일부만 매칭된다.

## 방법론

### 3.1 실험 방법론

| 항목 | 구성 |
|------|------|
| **Simulator** | gem5 system emulation |
| **CPU Baseline** | Intel Skylake, 16-core, 4GHz, AVX-512 |
| **GPU Baseline** | NVIDIA A100, 6912 CUDA cores, 40GB HBM2 |
| **PUD Baseline** | SIMDRAM[101] |
| **PIM Comparisons** | DRISA[63] (3T1C), Fulcrum[104] |
| **DRAM Config** | DDR4-2400, 1ch/8chips/1rank, 16banks, 16mats/chip, 1K rows/mat, 512 cols/mat |
| **Applications** | 12개 (SPEC 2017 x264; Rodinia hw/km/bs; Phoenix pca; Polybench 2mm/3mm/cov/dg/fdtd/gmm/gs) |
| **Multi-programmed** | 495개 mix (8 apps, low/med/high VF 분류) |
| **MIMDRAM Config** | 8-entry mat queue, 2KB bbop buffer, 8 μProgram engines, Single subarray/bank (conservative) |

### 3.2 주요 결과

#### Single-Application: SIMD Utilization (Figure 9a)

| Metric | SIMDRAM | MIMDRAM |
|--------|---------|---------|
| Avg SIMD utilization | baseline | **15.6×** improvement |

MIMDRAM은 앱의 max VF에 맞춰 필요한 만큼의 DRAM mat만 활성화.

#### Single-Application: Energy Efficiency & Performance (Figure 9b)

| Metric vs. | SIMDRAM | CPU | GPU |
|------------|---------|-----|-----|
| Energy Efficiency | **14.3×** | **30.6×** | **6.8×** |
| Performance | **34×** | varies* | varies* |

*Single subarray/bank 기준. Multi-bank/subarray 확장 시 CPU/GPU 능가 (see §3.4).

**개선 요인 분석:**
1. Independent bbop parallelization: execution time 2.8× 감소 (pca, 3mm, fdtd)
2. PUD vector reduction: execution 1.6×, energy 266× 감소
3. Partial mat activation (low SIMD): energy 325× 감소 (VF < 65K apps)

#### Multi-Programmed Workloads (Figure 10)

Single subarray/bank MIMDRAM vs. SIMDRAM (N banks):

| Metric | vs SIMDRAM:2 | vs SIMDRAM:4 | vs SIMDRAM:8 |
|--------|:-----------:|:-----------:|:-----------:|
| Weighted Speedup | **1.68×** | **1.54×** | **1.52×** |
| Harmonic Speedup | **1.33×** avg | | |
| Fairness (max slowdown) | **1.32×** better | | |

Single bank MIMDRAM이 8-bank SIMDRAM보다 높은 throughput 달성.

**CPU 대비:** 10개 multi-app mix에서 throughput **19% 향상** (Figure 11).

#### PIM Architecture 비교 (Figures 12-13)

| Architecture | DRAM Area Overhead | Performance/Area vs MIMDRAM |
|-------------|-------------------|----------------------------|
| MIMDRAM | **1.11%** | 1.0× (baseline) |
| DRISA[63] | 21% | 0.85× (MIMDRAM = 1.18× DRISA) |
| Fulcrum[104] | 82% | 0.52× (MIMDRAM = 1.92× Fulcrum) |

MIMDRAM은 최소 면적으로 최대 performance/area 달성.

### 3.3 Ablation: SALP & BLP 확장 (Figure 14)

16 banks × 64 subarrays/bank 사용 시:
- MIMDRAM: **13.2× CPU performance** (2× GPU performance)
- SIMDRAM: 0.08× CPU (확장해도 CPU 미달)

### 3.4 면적 분석

| Component | Overhead |
|-----------|----------|
| DRAM bank (mat isolation transistors, row decoder latches, mat selectors, matlines, inter-mat MUX) | **1.15%** |
| DRAM chip I/O (chip select + mat identifier logic) | 116.3 μm² @ 22nm |
| **Total DRAM chip** | **1.11%** |
| Control unit (bbop buffer + mat scoreboard + 8 μProgram engines) | 0.253 mm² |
| Transposition unit | 0.06 mm² |
| **Total CPU die** (vs Intel Xeon E5-2697 v3) | **0.6%** |

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

**핵심 Contributions:**
1. **최초의 end-to-end MIMD PUD 시스템:** DRAM mat 단위 fine-grained activation으로 하나의 subarray에서 독립적 PUD 연산 동시 실행
2. **Low-cost interconnects:** Inter-mat (GB-MOV) + Intra-mat (LC-MOV) → vector reduction 연산을 DRAM 내에서 완결
3. **Programmer-transparent compiler:** 수정 없는 C/C++ 코드 → 자동 vectorization → mat scheduling → PUD instruction 생성
4. **실험적 입증:** SIMDRAM 대비 34× 성능, 14.3× 에너지 효율; 1.11% DRAM, 0.6% CPU die 면적 overhead

**Broader Significance:** PUD의 "very-wide SIMD" 패러다임에서 "flexible MIMD" 패러다임으로의 전환을 제시. DRAM의 계층적 구조(mat/subarray/bank)를 PIM 가속기 설계에 체계적으로 활용하는 방법론을 정립. RowHammer 방어 기법들을 위한 row tracking 하드웨어와 동일한 계층 구조를 공유하므로 통합 설계 가능성 시사.

---

*요약 재작성일: 2026-05-09 (FastServe-level rewrite)*

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2024HPCA-summarize/mimdram-an-end-to-end-processing-using-dram-system-for-high-throughput-energy-efficient-and-programmer-transparent-multiple-instruction-multiple-data-computing.md|전체 요약 보기]]
