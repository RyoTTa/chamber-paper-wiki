---
tags: [paper, 2025, 2025ASPLOS, topic/cache, topic/disaggregation, topic/dram, topic/memory-tiering]
venue: ""
year: 2025
summary_path: "../paper-summaries/2025ASPLOS-summarize/systematic-cxl-memory-characterization-and-performance-analysis-at-scale.md"
---

# Systematic CXL Memory Characterization and Performance Analysis at Scale

**Venue:** 
**저자:** 

## 개요

CXL (Compute Express Link)은 PCIe 기반 메모리 확장 인터커넥트로, 서버/랙 레벨의 메모리 scale-up/out을 가능하게 한다. CXL 메모리는 socket-local DRAM (~100ns)보다 높은 지연시간을 가지며, Figure 1에서 보이듯 locally-attached CXL은 ~200-400ns, CXL+NUMA는 그 이상, CXL+Switch는 ~600ns까지 지연시간이 증가한다. Bandwidth 또한 18-52GB/s로 device별 편차가 크다.

**기존 연구의 한계:**
- CXL 성능을 평균 latency/bandwidth만으로 평가 → tail latency, latency stability 무시
- 소규모 workload set (주로 cloud/HPC) 대상 coarse-grained 분석에 국한
- CXL의 CPU pipeline-level 영향, prefetcher 효율 저하 메커니즘 미규명
- CXL+NUMA 조합 시 발생하는 비직관적 성능 저하 원인 불명

**핵심 질문:**
1. CXL device 간 latency stability 차이는 어느 정도이며 tail latency는 어느 수준인가?
2. 다양한 workload가 sub-µs CXL latency에 얼마나 tolerant한가?
3. CXL-induced slowdown의 근본 원인을 어떻게 체계적으로 분석할 수 있는가?

## 방법론

### 3.1 Methodology

| 항목 | 내용 |
|------|------|
| Testbed | 5 Intel servers: SPR2S, EMR2S, EMR2S', SKX2S, SKX8S |
| CXL Devices | 4개: CXL-A(ASIC/DDR4), CXL-B(ASIC/DDR5), CXL-C(FPGA/DDR4), CXL-D(ASIC/DDR5, 16 lanes) |
| Latency Regimes | 7개: 140ns, 190ns, 214ns, 239ns, 271ns, 394ns, 410ns |
| Workloads | 265개: SPEC CPU 2017, PARSEC, GAPBS, PBBS, CloudSuite, Redis/VoltDB, GPT-2, Llama, MLPerf, Spark, Phoronix |
| Metrics | Slowdown S = (P_DRAM/P_CXL - 1)×100%, Spa component breakdown, tail latency CDF |
| Baselines | Local DRAM, NUMA, 2-hop-NUMA |

### 3.2 Device Characterization Results

- **Tail latency:** CXL-B/CXL-C는 p99.9에서 160ns 이상 증가. Local/NUMA는 45ns/61ns에 불과.
- **Loaded latency:** Bandwidth utilization 50-86%에서 CXL average latency 60ns+ 증가, local/NUMA는 90-95%까지 안정.
- **Bandwidth saturation 시:** CXL-A/B는 ~350ns→~1.2µs로 spike, CXL-C는 3µs 도달.
- **Read/write ratio 영향:** CXL device별 peak bandwidth 도달 ratio가 다름 (CXL-D: 3:1/4:1, CXL-A: 2:1).

### 3.3 Workload Slowdown

- **CDF 분석 (Figure 8a):** NUMA(193ns)에서 98% workload가 50% 미만 slowdown. CXL-D: 94%, CXL-A: 87%, CXL-B: 80%.
- **10% 미만 slowdown 비율:** CXL-D 60%, CXL-A 54%, CXL-B 32%.
- **5% 미만 slowdown 비율:** CXL-D 43%, CXL-A 35%, CXL-B 22%.
- **Tail slowdown:** 7% workload가 CXL-A/B에서 1.5-5.8× slowdown (bandwidth-bound: 603.bwaves, 619.lbm, 649.fotonik3d, 654.roms).
- **410ns에서도:** 16% workload 10% 미만 slowdown, 30% 50% 미만.

### 3.4 Spa Breakdown (Figure 14)

- 519.lbm: slowdown 대부분이 Store Buffer stall → 높은 UPI non-data traffic + write bandwidth
- 649.fotonik3d: cache-related slowdown이 주요 원인
- GAPBS workload: 주로 DRAM demand read stall
- ML workload (DLRM, GPT-2): 90%가 DRAM slowdown
- 15% workload: 5% 이상 cache slowdown (prefetcher inefficiency)
- 40% workload: 5% 이상 demand read slowdown

## 핵심 기여

Melody는 최대 규모(265 workloads, 4 devices, 7 latency regimes, 5 platforms)의 CXL 성능 분석 프레임워크로, 다음의 핵심 기여를 제공한다:

1. **CXL tail latency의 첫 공개 및 분석:** CXL device가 local/NUMA 대비 불안정하고 높은 tail latency를 가지며, 특히 CXL+NUMA 조합에서 최대 2.9×의 비직관적 slowdown을 유발함을 밝힘.
2. **CPU tolerance 정량화:** 60% workload가 CXL-D에서 10% 미만 slowdown을 보여 CXL이 많은 real-world application의 drop-in replacement로 viable함을 입증. 단, bandwidth-bound workload는 여전히 큰 slowdown.
3. **Spa:** 단 9개 CPU 카운터로 95%+ accuracy의 CXL slowdown root-cause 분석 방법론 제시. Pipeline component별 (DRAM, L1/L2/L3 cache, Store Buffer, Core) slowdown breakdown 가능.
4. **Prefetcher inefficiency 규명:** CXL latency가 L2→L1 prefetcher cascade를 통해 cache slowdown을 유발하는 메커니즘을 실험적으로 입증.

**Broader significance:** CXL 기반 memory tiering/pooling system 설계 시 tail latency가 QoS에 미치는 영향을 고려해야 하며, Spa는 memory placement 최적화 (예: 605.mcf slowdown 13%→2%) 및 tiering policy 설계에 직접 활용 가능한 실용적 도구이다.

## 주요 결과

- **Melody tools:** Intel MLC, custom MIO microbenchmark, Intel Pin instrumentation, addr2line
- **Spa profiler:** Linux perf 기반, 9개 CPU 카운터 수집, time-based→instruction-based 변환 로직
- **Codebase:** Python 기반 분석 스크립트 + CXL device driver 설정
- **오픈소스:** https://github.com/MoatLab/Melody (tools + datasets)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]


## 전체 요약

[[../paper-summaries/2025ASPLOS-summarize/systematic-cxl-memory-characterization-and-performance-analysis-at-scale.md|전체 요약 보기]]
