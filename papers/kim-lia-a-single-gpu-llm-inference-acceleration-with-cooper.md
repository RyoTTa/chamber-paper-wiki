---
tags: [paper, 2025, 2025ISCA, topic/cache, topic/disaggregation, topic/dram, topic/gpu, topic/llm-inference]
venue: ""
year: 2025
summary_path: "../paper-summaries/2025ISCA-summarize/lia-a-single-gpu-llm-inference-acceleration-with-cooperative-amx-enabled-cpu-gpu-computation-and-cxl-offloading.md"
---

# LIA: A Single-GPU LLM Inference Acceleration with Cooperative AMX-Enabled CPU-GPU Computation and CXL Offloading

**Venue:** 
**저자:** Hyungyo Kim, Nachuan Wang, Qirong Xia, Jinghan Huang, Amir Yazdanbakhsh, Nam Sung Kim

## 개요

LLM 파라미터 수가 급증(GPT-4, Llama-3, OPT-175B 등)하면서 단일 GPU memory capacity에 model parameters와 KV cache, activations를 저장할 수 없게 됨. 최신 H100(94GB HBM)도 OPT-175B에는 부족하고, 5개 H100 GPU 배포 시 $150,000의 비용이 소요되어 cost-inefficient함.

**기존 접근의 한계:**
- **Quantization/Pruning/Distillation:** Memory 요구량 감소는 가능하나 model accuracy 손실, 여전히 multi-GPU 필요.
- **System-level offloading (FlexGen 등):** Model parameters와 KV cache를 CPU memory에 저장 후 GPU로 on-demand 전송. 그러나 PCIe 5.0 bandwidth(64 GB/s)로 인해 data transfer가 dominate → OPT-175B parameter 전송만 ~5초.
- **Compute-offloading (FlexGen, FastDecode, PowerInfer):** Attention scoring sublayer를 CPU로 offload하나, 기존 CPU의 AVX512 throughput이 GPU의 1% 미만으로 효과 미미 (Figure 4: decoding latency reduction 최대 10.2%).

핵심 문제: CPU-GPU bandwidth bottleneck이 심각하고, CPU compute throughput이 너무 낮아 기존 compute-offloading이 충분한 효과를 내지 못함.

---

## LIA의 핵심 기여

### 1. AMX Matrix-Multiplication Throughput 분석 (§4)

Intel Xeon 4th Gen (SPR, 40-core) 및 6th Gen (GNR, 128-core)의 AMX throughput을 OPT-175B의 현실적 matrix/vector dimension에서 microbenchmark.

**GEMM (Compute-bound, FC1 sublayer 기반):**
| Platform | Throughput (BF16 TFLOPS) | vs. AVX512 | vs. A100 | vs. H100 |
|---|---|---|---|---|
| AVX512 (SPR) | ~3.7 | 1× | — | — |
| SPR-AMX (40c) | ~16.6 | 4.5× | 7–15% | 4–11% |
| GNR-AMX (128c) | ~40 | 9× | 16–30% | 8–22% |
| GNR-AMX (2-socket) | ~72 | — | ~30% | ~16% |

**GEMV (Memory-bound, Q×K^T sublayer 기반):**
| Platform | vs. P100 | vs. A100 | vs. H100 |
|---|---|---|---|
| SPR-AMX | 54% | 19% | 15% |
| SPR-AMX (small B/L) | 70% | 38% | 35% |
| GNR-AMX (12ch DDR5-5600) | SPR 대비 +70% | | |

**통찰 (Insight-3):** AMX는 AVX512 대비 4.5~9× throughput 향상을 제공하며, 이전 세대 GPU(P100, V100)와 경쟁 가능한 수준. 이로 인해 CPU compute-offloading이 실용적인 전략으로 부상.

## 방법론

모든 OPT 모델(30B, 66B, 175B)에서 3가지 주요 정책만 식별됨:

| 정책 | p vector | 적용 조건 |
|---|---|---|
| **Full CPU** | (1,1,1,1,1,1) | Prefill: B×L < ~850, Decoding: B < ~858 (OPT-175B 기준) |
| **Partial CPU** | (0,1,1,0,0,0) | Decoding: B > threshold (CPU: attention scoring, GPU: QKV mapping + FFN) |
| **Full GPU** | (0,0,0,0,0,0) | Prefill: B×L ≥ threshold |

**Model 간 차이:** 같은 B, L에서도 model size가 클수록 operations/byte가 달라져 policy 선택이 달라짐. GPU capability에 따라 H100이 A100보다 GPU-centric policy를 더 넓은 B,L 영역에서 선택.

## 핵심 기여

1. **AMX의 실용적 가치 입증:** 최신 Intel CPU의 AMX가 AVX512 대비 최대 9×, 이전 세대 GPU(P100) 대비 competitive한 throughput을 제공하여 CPU가 LLM inference에서 단순한 memory 확장을 넘어 실질적인 compute offloading 대상이 될 수 있음.
2. **Adaptive offloading framework:** B, L에 따라 operations/byte가 급변하는 LLM의 특성을 formal optimization으로 모델링하여, 정적 policy 대비 최대 6.2× latency 개선.
3. **CXL memory의 strategic 활용:** Parameter는 CXL에, KV cache는 DDR에 배치하는 hybrid memory-offloading 정책으로 throughput 손실 없이 DDR 사용량 43% 절감, system cost ~9% 감소 (OPT-175B 기준 $6,300→$3,200).
4. **Single-GPU cost advantage:** Multi-GPU system(DGX-A100) 대비 10%의 system cost로 B=1에서는 더 높은 throughput을, B=64에서는 AMX 최적화 시 동등 이상의 성능을 달성 가능.

## 주요 결과

**Optimization-1: Granular GPU memory utilization.**
- FlexGen은 unused GPU memory에 "모든 decoder layer의 특정 sublayer"를 저장 → 4.7GB/layer 소모.
- LIA는 "최대한 많은 decoder layer 전체"를 GPU memory에 저장 → 1.2GB/layer로 더 granular하게 활용.
- OPT-30B, B=1, L=2016 기준: LIA는 62%의 decoder layers를 35GB에 저장 vs. FlexGen은 58%의 sublayers를 32GB에 저장.

**Optimization-2: Overlapping strategy divergence.**
- **Prefill:** FlexGen과 동일하게 batch를 mini-batch로 분할하여 overlapping (Figure 7).
- **Decoding:** FlexGen의 mini-batch overlapping을 적용하지 않음. Decoding에서는 compute time이 mini-batch size에 비선형적으로 scale하므로 pipeline bubble 감소 효과보다 overhead가 더 큼 → LIA가 1.1–1.3× lower latency 달성.

---

## 구현

- **Base framework:** Intel Extension for PyTorch (IPEX)를 확장. 원래 IPEX는 pytorch-cpu/CXX 기반으로 NVIDIA GPU와 호환되지 않으므로, pytorch-cuda distribution에 rebinding하여 재구축.
- **Modified libraries:** IPEX Transformers, HuggingFace Transformers.
- **Input:** Model parameters, B, L, system performance characteristics (PCIe BW, GPU/CPU compute throughput, memory BW).
- **Output:** 최적 offloading policy → execution schedule → cooperative inference.
- **Integration:** IPEX의 full-system framework로 통합되어 user에게 seamless한 API 제공.

---

## 평가

### 실험 환경 (Table 2)

| 항목 | SPR 시스템 | GNR 시스템 |
|---|---|---|
| **Server** | Supermicro X13DDW-A | Supermicro X13DDW-A (CPU만 교체) |
| **CPU** | Intel Xeon Platinum 8460H, 40 cores, 8ch DDR5-4800 | Intel Xeon 6th Gen, 128 cores, 12ch DDR5-5600 |
| **DDR** | 512 GB | 512 GB |
| **GPU 1** | A100 40GB HBM2, PCIe 4.0 | A100 40GB |
| **GPU 2** | H100 80GB HBM3, PCIe 5.0 | H100 80GB |
| **CXL** | Samsung CXL Type-3 Memory Expander ×2 (각 128GB DDR4) | 동일 |

### Workloads & Baselines

| Model | SPR-A100 | SPR-H100 | GNR-A100 | GNR-H100 |
|---|---|---|---|---|
| OPT-30B | ✓ | — | ✓ | — |
| OPT-66B | — | ✓ | — | ✓ |
| OPT-175B | ✓ | ✓ | ✓ | ✓ |
| Llama2-70B, Chinchilla-70B, Bloom-176B | analytical | model | 사용 | |

**Baselines:** IPEX (AMX-only CPU), FlexGen (AVX512+GPU), PowerInfer (sparsity-based CPU-GPU)

**Scenarios:** Online (B=1, latency-driven, s/query), Offline (B=64, B=900, throughput-driven, tokens/s)

### Latency Results (Figure 10)

| System | Model | vs. IPEX | vs. FlexGen |
|---|---|---|---|
| SPR-A100 | OPT-30B | 1.8–2.1× lower | 5.3–7.3× lower |
| SPR-A100 | OPT-175B | 1.1–1.3× lower | 8.5–12× lower |
| SPR-H100 | OPT-66B | 2.1–2.5× lower | 4.9–7.0× lower |
| SPR-H100 | OPT-175B | 1.1–1.5× lower | 4.0–5.1× lower |
| GNR-A100 | OPT-175B | — | 13–24× lower (online) |
| GNR-H100 | OPT-175B | — | 8.3–12× lower (online) |

**분석:** FlexGen 대비 개선은 CPU-GPU transfer reduction (31× ~ 222,524×)에서 기인. IPEX 대비 개선은 unused GPU memory 활용 + compute-intensive prefill을 GPU로 offload. Model이 커질수록 LIA-IPEX gap은 감소(GPU에 저장 가능한 decoder layer 감소), LIA-FlexGen gap은 증가(상대적 transfer량 감소).

### Throughput Results (Figure 11)

| System | Model | vs. IPEX | vs. FlexGen |
|---|---|---|---|
| SPR-A100 | OPT-30B | 1.5–6.0× higher | 2.0–5.9× higher |
| SPR-A100 | OPT-175B | 1.1–6.1× higher | 1.3–6.0× higher |
| SPR-H100 | OPT-66B | 1.3–8.3× higher | 1.2–3.3× higher |
| SPR-H100 | OPT-175B | 1.2–10× higher | 1.5–3.7× higher |

**CXL offloading (Table 3):** OPT-30B, B=900에서 CXL memory에 parameter offload 시 throughput 유지 (within 1%), DDR memory 사용량 최대 43.1% 감소. 동일 DDR footprint 내에서 batch size 증가로 최대 1.45× throughput 향상 (B: 900→1,580).

### Ablation Study (Table 4)

| Component | B=1 impact | B=64 impact | B=900 impact |
|---|---|---|---|
| No Optimization-1 | 2.0× slower | 1.12× slower | negligible |
| No Optimization-2 | no impact | 1.12× slower | 1.52× slower |
| FlexGen's policy | 6.2× slower | 3.5× slower | 1.9× slower |

**분석:** Optimization-1은 small B에서 GPU memory의 granular 활용이 핵심, large B에서는 GPU memory가 포화되어 효과 감소. Optimization-2는 large B에서 transfer-compute overlap이 효과적. LIA policy는 모든 B에서 FlexGen policy보다 우수하고, B=900에서는 policy가 동일해도 AMX compute throughput 향상으로 1.9× 이득.

### Energy Efficiency (Figure 12)

- LIA vs. IPEX: 1.1–5.8× higher energy efficiency
- LIA vs. FlexGen: 1.6–10.3× higher energy efficiency
- Small B(≤64) + short L(=32): LIA의 짧은 latency가 static power 비중을 줄여 FlexGen 대비 에너지 효율 극대화.
- Large B(=900): latency gap 감소로 energy benefit 감소하나, GPU가 compute-intensive task를 energy-efficient하게 처리.

### GNR Scaling (§7.6, Table 6)

- CPU upgrade (SPR→GNR): LIA-IPEX gap 14% 감소 (IPEX는 CPU에 전적으로 의존), LIA-FlexGen gap 1.7× 증가 (LIA의 CPU compute 의존도가 더 높음).
- Cost-efficiency: GNR-A100은 SPR-H100 대비 system cost 1.7× 낮고 energy-efficiency 1.6× 높음 — CPU upgrade가 GPU upgrade보다 더 cost-effective할 수 있음.

### Multi-GPU vs. LIA (§7.8, Figure 14)

- B=1: LIA (GNR-A100)가 DGX-A100 (8×A100, TP=8) 대비 per-GPU throughput 1.4–1.8× 높고 cost 1.5–2.0× 낮음.
- B=64: LIA throughput은 multi-GPU의 70% 수준이나, AMX가 이론 성능의 50%에 도달 시 1.1–1.3× 역전 가능.
- System cost: GNR-A100 = $22K, DGX-A100 = $200K → LIA는 10% cost.

### PowerInfer Comparison (§7.9, Figure 15)

Llama2-70B, GNR-A100에서 LIA는 PowerInfer 대비 1.4–9.0× lower latency, 1.5–15× higher throughput. PowerInfer는 B=900에서 CUDA OOM 발생. PowerInfer의 intra-layer hot/cold neuron communication이 PCIe transfer를 유발하여 LIA의 AMX 활용보다 불리.

### Model Generalizability (§7.7)

Llama2-70B, Chinchilla-70B, Bloom-176B에서 LIA는 FlexGen 대비 6.1–11× lower latency, 1.2–7.6× higher throughput. MoE architecture의 경우 experts 증가에 따라 policy diversity 증가 (e.g., p = (0,1,1,0,1,1)).

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]


## 전체 요약

[[../paper-summaries/2025ISCA-summarize/lia-a-single-gpu-llm-inference-acceleration-with-cooperative-amx-enabled-cpu-gpu-computation-and-cxl-offloading.md|전체 요약 보기]]
