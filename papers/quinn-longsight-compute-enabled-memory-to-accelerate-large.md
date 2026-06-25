---
tags: [paper, 2025, 2025MICRO, topic/cache, topic/dram, topic/gpu, topic/llm-inference, topic/pim]
venue: "MICRO 2025"
year: 2025
summary_path: "../paper-summaries/2025MICRO-summarize/longsight-compute-enabled-memory-to-accelerate-large-context-llms-via-sparse-attention.md"
---

# LongSight: Compute-Enabled Memory to Accelerate Large-Context LLMs via Sparse Attention

**Venue:** MICRO 2025
**저자:** Derrick Quinn, E. Ezgi Yücel, Jinkwon Kim, José F. Martínez, Mohammad Alian (Cornell University; Kim also with SK hynix)

## 개요

Transformer 기반 LLM의 context window 확장 추세 (chain-of-thought, few-shot, RAG, multi-turn interaction, agentic AI)에 따라 KV cache 크기가 급증. Llama-3-8B 기준 1M token context의 KV cache는 HBM 용량을 크게 초과.

**Key observation:** Attention이 모든 과거 token에 uniformly 분포하지 않음 — 소수 token(Query vector와 높은 dot-product similarity를 보이는 Key vector)에 집중됨.

기존 접근의 한계:
- **Software sparse attention** (Reformer, Longformer, NSA): LSH 기반 filtering은 per-token O(L) overhead, hash bucket 재계산 비용, block-level sparsity로 인한 조대 granularity, task-specific fine-tuning 필요.
- **Hardware attention acceleration** (NeuPIMs, AttAcc, CENT): Full dense attention 사용 → PIM에서도 expensive. CENT는 BF16 MAC unit의 상당한 area/energy overhead. NeuPIMs는 dual row buffer 메커니즘의 DRAM 회로 수정 필요.
- **DynaX** [HPCA]: 4-6 bit quantization + structured sparsity → filtering 시 Key memory footprint의 최소 6.25%를 load해야 하는 bound.

**Target:** 계산 비용 → memory capacity 문제 + attention 계산 비용 동시 해결. Single GPU + single DReX로 **최대 1M tokens** 지원 (기존 single GPU로는 불가능).

## 방법론

### 1. Hybrid Dense-Sparse Attention Algorithm (§5)

**3-stage sparse attention pipeline:**

**(A) Filtering — Sign-Concordance Filtering (SCF):**
1-bit quantized filtering. Query Q와 Key K의 sign bit 일치 개수가 threshold TH 이상이면 통과:
\[
\text{SCF}(Q, K, \text{TH}) = \left[ \text{TH} \leq D - \sum_{i=1}^{D} (\text{SQ}[i] \oplus \text{SK}[i]) \right]
\]
Threshold는 **KV head별**로 할당 (Query-head별 할당은 tuning instability). Per-token filtering → PIM 가속에 적합.

**(B) Scoring:** Filter 통과한 Key들에 대해 full-precision dot-product로 attention score 계산.

**(C) Top-k Retrieval:** Attention score 기준 top-k(≤1024) Value vector 선택 → GPU로 전송되는 데이터 최소화.

**(D) ITQ (Iterative Quantization) Enhancement:**
Llama 모델의 KV representation이 origin 주변에 clustering → SCF filter efficiency 저하. ITQ [CVPR'11]로 rotation matrix 학습 → sign-bit distribution 균형화. 각 KV head별로 1K-token sequence로 training (1분 이내, task-specific data 불필요). Runtime에는 Query/Key projection 후 ITQ matrix 곱셈 적용. Computational overhead: Query vector 계산 비용의 <3%, inference request 비용의 <0.5%(Llama-3-1B).

**(E) Hybrid Attention:**
- GPU HBM: 최근 W=1024 tokens의 KV → **dense attention** (sliding window)
- DReX: Window 이전 전체 KV → **sparse attention** (SCF + Top-k)
- GPU가 dense/sparse 결과 통합하여 softmax + SV 수행

**Algorithm Results (Figure 3, Table):**

| Config | Llama-3-1B (128K ctx, PG) | Llama-3-8B (32K ctx, PG) |
|---|---|---|
| Sparse only, no ITQ, k=128 | ~10× filter ratio | ~10× |
| Sparse only, no ITQ, k=1024 | ~4× | ~4× |
| Hybrid (W=1024), no ITQ, k=128 | ~20× (+39% filter ratio vs. dense only) | ~15× (+7%) |
| **Hybrid + ITQ, k=128** | **~1220× (6.4× over hybrid alone)** | **~537× (46× over hybrid alone)** |
| Hybrid + ITQ, k=1024 | ~2961× (at 128K) | ~1564× (at 32K) |

Perplexity: 모든 configuration에서 dense attention 대비 **5% 이내**. DynaX 대비: 동일 1% perplexity 증가 조건에서 LongSight **91.92% sparsity** (12.4× filter ratio) — DynaX의 91.77%와 competitive.

**Pareto frontier (Figure 4):** k=1024, W=1024에서 wide range accuracy target 충족. W>1024는 highest accuracy에서만 유용.

### 2. System Integration: GPU + DReX via CXL (§6)

**DReX baseline** [MICRO'24]: Compute-enabled CXL Type-3 memory expander (512 GB LPDDR5X, 8 packages × 8 channels × 128 banks = 1,024 PFUs, 8 NMAs).

**Execution flow (Figure 2b):**
1. **Prefill stage:** GPU가 HBM에 KV 누적 → threshold 도달 시 128개 KV 단위로 Key Sign/Object/Value Object 준비하여 DReX에 CXL write (off critical path)
2. **Decode stage, 각 attention layer:**
   - GPU가 Request Descriptor(UID, layer, Q vectors)를 DReX MMIO Request Queue에 write
   - GPU가 HBM window에 대해 **dense QKT + softmax + SV** 수행 (DReX offload와 overlap)
   - GPU polling으로 DReX completion 확인
   - DReX로부터 수신한 top-k QKT + Value로 **hybrid softmax + SV** 완료

**Hybrid의 3가지 이점:**
1. 최근 token의 dense attention → accuracy 향상 (Longformer와 동일 insight)
2. HBM 용량 활용 → memory efficiency
3. Batch KV update → communication overhead 감소 (token당 전송 대비)

### 3. Hardware Architecture Extensions (§7)

**DReX CXL Controller (DCC) Extensions:**
- **Polling Register** (512-bit): GPU가 completion polling
- **Request Queue** (depth=512, FIFO): GPU가 write한 descriptor → DCC가 NMA에 분배
- **Response Buffers** (512개): User ID → Response Buffer CAM mapping → GPU가 1회 read하여 전체 generation phase에서 재사용

**Data Layout Hierarchy (Figure 6):**

| Level | Structure | Capacity | Parallelism |
|---|---|---|---|
| Key Block | 128 Keys + Sign Objects, bank-local | 1 bank | PFU 1 cycle/128 Keys |
| Context Slice | Key Blocks across all banks in a package | 131,072 Keys (128 banks) | Bank-level filtering parallel |
| Multi-Layer Context Slice | Context Slices concatenated across layers | Sequential layer access | Within-head pipeline |
| User Partition | MLCS per KV head, mapped to distinct packages | ~64K tokens/head | Head-level (package) parallel |

**Key placement constraints:**
- Key Sign Object: 단일 DRAM bank 내 (128 Keys의 동일 dimension이 128-bit column을 구성 → PFU가 1 cycle에 처리)
- Full-precision Key: 8 channels across package에 interleaved → NMA scoring 시 channel bandwidth saturation
- Strided physical address → GPU가 contiguous write 불가 (LongSight kernel이 explicit scatter)

**NMA Controller:** State machine — in-memory filtering (PFU bitmap generation) ↔ near-memory similarity score evaluation 교대. Filtering은 multi-epoch (epoch당 128K Keys/package), 각 PFU가 128-bit bitmap 반환. Key ID: 32-bit (7-bit bank + 7-bit bitmap index + 18-bit epoch).

## 핵심 기여

LongSight는 LLM large-context attention을 위한 algorithm-hardware co-design framework.

**핵심 기여:**
1. **Hybrid dense-sparse attention** — GPU HBM의 sliding window dense attention + DReX의 SCF-based sparse attention 결합 → quality-preserving while achieving massive KV cache filtering
2. **ITQ-enhanced SCF** — Llama 모델의 clustering 문제를 rotation matrix로 해결 → filter ratio **최대 46× 개선** (Llama-3-8B)
3. **DReX repurposing** — Dense retrieval accelerator를 attention offload engine으로 확장 (DCC extension, NMA controller, hierarchical data layout) → 추가 hardware overhead minimal
4. **CXL-based GPU-DReX collaboration** — SCADA API로 GPU가 load/store로 DReX memory 직접 접근 → CPU 개입 불필요

**System impact:**
- Single GPU + single DReX로 **1M token context 지원** (기존 single GPU 불가)
- Max single-GPU context length에서 **8.1-9.6× throughput**, **3.6-11.9× per-token latency 개선**
- LPDDR DRAM을 HBM 수준의 value로 elevate → cost-effective large-context inference infrastructure
- DynaX와 competitive한 sparsity (91.92% vs. 91.77%) + hardware acceleration으로 practical advantage

## 주요 결과

- **Attention sink tokens:** 16 tokens (StreamingLLM [41] 기반, Llama-3 모델이 early token에 heavy attend하는 현상 대응)
- **Sliding window:** W=1024 (default). Multi-user 시 GPU보다 DReX가 bottleneck → window maximize; few-user 시 per-token latency target 기반 선택.
- **Top-k:** Threshold=0에서 perplexity 0.5-1% 증가하는 k 선택 → k=256 (32K), 512 (64K), 1024 (128K+).
- **SCF thresholds:** 모든 threshold=0 시작 → lowest filter ratio KV head부터 iterative 증가 → perplexity 5% 도달 시 이전 iteration 기록.

## 구현

**Evaluation setup (Table 2):**

| Component | Specification |
|---|---|
| Host CPU | 16× Intel Xeon Max 9462 @3.5 GHz, SMT off, 8×128 GB DDR5-4400 |
| GPU | NVIDIA H100 SXM, 80 GB HBM3 (3.35 TB/s), 989 TF/s BF16 |
| DReX (simulated) | 512 GB LPDDR5X, 8 NMAs, 8,192 PFUs, 1.1 TB/s (NMAs), 104.9 TB/s (PFUs) |

**Simulation framework:**
- GPU: HuggingFace transformers에서 Llama-3-1B/8B dense attention 실측 + sliding window/softmax overlap 측정
- DReX: DRAMSim3 cycle-accurate + PFU/NMA RTL synthesis (16nm → 7nm scaling) + Ramulator LPDDR5 timing
- CXL interface: Dual-socket Intel Xeon 실측 (memory copy + polling overhead)
- LongSightAttn PyTorch module: ITQ transformation + sliding window attention + DReX top-k integration

**Models (Table 1):**

| Parameter | Llama-3-1B | Llama-3-8B |
|---|---|---|
| Attention | GQA | GQA |
| Query/KV Heads | 32/8 | 32/8 |
| Head Dim | 64 | 128 |
| Layers | 16 | 32 |
| Precision | BF16 | BF16 |

**Area/Power (DReX):**
- PFU area overhead: 6.7% of DRAM die
- NMA (16nm): 15.1 mm², 1.072 W peak
- Per LPDDR5X package: 18.7 W peak
- **Total DReX: 158.2 W** (8 packages + 8 NMAs)

## 평가

### 평가 방법론 요약

| 항목 | 내용 |
|---|---|
| **Configurations** | 1-GPU dense, 2-GPU dense (data-parallel), AttAcc [ASPLOS'24], LongSight (1 GPU + DReX) |
| **Context lengths** | 32K, 64K, 128K, 256Kˣ, 512Kˣ, 1Mˣ tokens (ˣ: projected from 128K perf) |
| **Users** | 1–64 (Llama-3-1B), 1–32 (Llama-3-8B) |
| **Datasets** | Project Gutenberg (PG, long-form books), WikiText-2 (Wiki2, concatenated) |
| **Primary metrics** | Perplexity (accuracy proxy), decode-stage throughput (tokens/sec), per-token latency |

### Inference Performance (Figure 7)

**1-GPU dense vs. LongSight, max context length supportable by 1 GPU:**

| Model | Throughput | Per-token Latency |
|---|---|---|
| Llama-3-1B (128K ctx) | **8.1× higher** | **3.6× lower** |
| Llama-3-8B (32K ctx) | **9.6× higher** | **11.9× lower** |

**Key findings:**
- 2-GPU, AttAcc → shorter context에서 LongSight보다 높은 throughput (CXL Value transfer overhead 때문). 그러나 **128K+ context에서 LongSight가 최고 throughput** — sparse attention의 효과.
- LongSight는 DReX의 large capacity로 더 많은 concurrent user 지원 → SLO 유지하며 throughput 증가.
- Throughput은 user 수 증가 시 plateau → DReX capacity가 user context pre-staging을 가능케 하여 GPU utilization 향상.
- **1M token context 지원:** Single GPU로는 2-GPU 구성에서만 가능했던 context length를 LongSight가 single GPU + DReX로 달성.

### DReX Latency Breakdown (Figures 8-9)

**Single-user (Figure 8):**
- Short context → CXL Value read가 주요 bottleneck
- Context length 증가 → dot-product 비용 비율 증가, Value read는 fixed per-user overhead

**Multi-user (Figure 9), system-level breakdown:**
- Few users → GPU-bound (regardless of context length)
- DReX fully utilized, short context → DReX-bound (high per-user Value loading overhead)
- Long context → fewer users, more DReX resources/user → GPU-bound (GPU가 end-to-end bottleneck)

### Comparison with Sliding Window (Figure 10)

Pareto frontier: LongSight가 sliding window-only 대비 **substantial Pareto expansion** (parameter tuning 시). 단, optimal parameter(window size, k, SCF thresholds)가 context length/data-dependent → 실무 tuning overhead.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2025MICRO-summarize/longsight-compute-enabled-memory-to-accelerate-large-context-llms-via-sparse-attention.md|전체 요약 보기]]
