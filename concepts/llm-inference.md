---
tags: [concept, llm, inference, transformer, kv-cache]
source_count: 27
last_updated: 2026-07-02
---

# LLM Inference

## Summary

Large Language Model (LLM) inference has become a major research focus as models grow to hundreds of billions of parameters. The key challenges are the memory bottleneck of KV caching, the distinct compute/memory profiles of prefill and decode phases, and the need for efficient serving infrastructure. Research spans algorithmic innovations (sparsity, quantization), system-level optimizations (phase splitting, scheduling), and hardware acceleration.

## Key Ideas

### Autoregressive Inference Phases
- **Prefill Phase** (Prompt Processing): Processes all input tokens in parallel ??**compute-bound**, high GPU utilization, high power
- **Decode Phase** (Token Generation): Generates tokens one-by-one ??**memory-bound**, low GPU utilization, low power
- These phases have fundamentally different resource requirements, motivating phase-splitting approaches ([splitwise-efficient-generative-llm-inference-using-phase-splitting.md])

### KV Cache Management
- KV caching stores previously computed Key/Value tensors to avoid recomputation
- KV cache size grows linearly with sequence length and batch size, often exceeding GPU memory
- **ALISA**: Sparse Window Attention achieves 80% sparsity with <5% accuracy loss; 3-phase dynamic scheduling for GPU-CPU memory hierarchy ([alisa-accelerating-llm-inference-via-sparsity-aware-kv-caching.md])
- **Splitwise**: Separates prefill and decode onto different machines; optimized KV-cache transfer via InfiniBand ([splitwise-efficient-generative-llm-inference-using-phase-splitting.md])
- **KV compression**: INT8 quantization of KV tensors with negligible accuracy impact

### LLM Inference Acceleration
- **LLMCompass**: Enables efficient hardware design for LLM inference ([llmcompass-enabling-efficient-hardware-design-for-large-language-model-inference.md])
- **MECLA**: Memory-compute-efficient LLM accelerator ([mecla-memory-compute-efficient-llm-accelerator.md])
- **REDUCT**: Near-cache compute for DNN inference on multi-core CPUs ([reduct-near-cache-compute-for-dnn-inference-on-multi-core-cpus.md])
- Sparse attention acceleration with synergistic in-memory pruning and on-chip recomputation ([sparse-attention-acceleration-with-synergistic-in-memory-pruning-and-on-chip-recomputation.md])
- **GeneSys**: EA 기반 학습 시스템을 위한 HW-SW 프로토타입 — EvE(학습 가속기)와 ADAM(추론 가속기)로 2-5 orders of magnitude 에너지 효율성 향상 ([genesys-enabling-continuous-learning-through-neural-network-evolution-in-hardware.md])

### Wafer-Scale LLM Inference
- **WaferLLM**: 최초의 웨이퍼 스케일 LLM 추론 시스템 — PLMR 모델로 수백만 코어 병렬성, MeshGEMM/MeshGEMV로 비균일 지연시간 해결, A100 대비 GEMV 606배 가속, 멀티-GPU 대비 LLM 추론 10~20배 가속 ([paper-summaries/2025OSDI-summarize/20260630-064008-waferllm-large-language-model-inference-at-wafer-scale.md])

### Edge LLM Inference
- **PIMPAL**: LUT 기반 PIM으로 엣지 기기에서 sLLM GEMV 가속화 — 서브어레이 수준 병렬 룩업, LCM, LAG로 기존 LUT 기반 PIM 대비 17.8배 성능 향상, PU 기반 PIM 대비 40% 영역 오버헤드 감소 ([paper-summaries/2025DAC-summarize/pimpal-accelerating-llm-inference-on-edge-devices-via-in-dram-arithmetic-lookup.md])

### PIM-based LLM Inference
- **DAWN**: 청크 기반 워크로드 할당으로 PIM-LM 추론의 재구성 오버헤드와 부하 불균형 해결 — throughput 최대 44.2% (평균 34.8%) 향상 ([paper-summaries/2026IEEECAL-summarize/dawn-efficient-distribution-of-attention-workload-in-pim-enabled-systems-for-llm-inference.md])
- **REFLEX**: DRAM 행 구조와 sparse attention 정렬로 재쓰기 없는 PIM 디코딩 — 처리량 1.64배, 에너지 효율 1.36배 향상 ([paper-summaries/2026DAC-summarize/reflex-rewrite-free-row-aligned-sparse-attention-for-efficient-llm-execution-on-pim.md])
- **PIMphony**: TCP/DCS/DPA 공동 설계로 긴 컨텍스트(최대 1M 토큰) PIM-LM 추론 비효율성 해결 — PIM 전용 최대 11.3배 성능 향상 ([paper-summaries/2025HPCA-summarize/pimphony-overcoming-bandwidth-and-capacity-inefficiency-in-pim-based-long-context-llm-inference-system.md])

### Serving Systems
- **Splitwise cluster design**: 3-tier machine pools (Prompt, Token, Mixed) with two-level scheduling (CLS + MLS)
- **Heterogeneous clusters**: High-performance GPUs (H100) for prefill, lower-cost GPUs (A100) or power-capped GPUs for decode
- **Provisioning framework**: Event-driven simulator exploring trade-offs in cost, power, throughput, and SLO satisfaction
- **LLMServingSim 2.0**: 이종적이고 분리된 LLM 서빙 인프라를 위한 통합 시뮬레이터 — 런타임 기반 하드웨어-소프트웨어 상호작용 모델링, 평균 오차 0.95%로 성능/메모리/전력 지표 재현, 시뮬레이션 시간 약 10분 유지 ([paper-summaries/TEMP-summarize/llmservingsim-2-0-a-unified-simulator-for-heterogeneous-and-disaggregated-llm-serving-infrastructure.md])

### Trends
- LLM inference is increasingly a **memory problem** rather than a computation problem
- Phase splitting enables significant throughput gains (1.4-3횞) and power reduction (25%)
- Model parallelism (tensor/pipeline) across GPUs adds communication complexity
- Speculative decoding, prefix caching, and continuous batching are complementary techniques

## Related Papers

- [alisa-accelerating-llm-inference-via-sparsity-aware-kv-caching.md]
- [splitwise-efficient-generative-llm-inference-using-phase-splitting.md]
- [llmcompass-enabling-efficient-hardware-design-for-large-language-model-inference.md]
- [mecla-memory-compute-efficient-llm-accelerator.md]
- [sparse-attention-acceleration-with-synergistic-in-memory-pruning-and-on-chip-recomputation.md]
- [cxl-speckv-a-disaggregated-fpga-speculative-kv-cache.md]
- [genesys-enabling-continuous-learning-through-neural-network-evolution-in-hardware.md]
- [fastserve-iteration-level-preemptive-scheduling-for-large-language-model-inference.md] - Iteration-level preemptive scheduling for LLM inference
- [paper-summaries/TEMP-summarize/llmservingsim-2-0-a-unified-simulator-for-heterogeneous-and-disaggregated-llm-serving-infrastructure.md] - LLMServingSim 2.0: A Unified Simulator for Heterogeneous and Disaggregated LLM Serving Infrastructure

## Cross-references

- [[paper-wiki/concepts/cache.md|Cache]] ??KV cache as a specialized cache
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]] ??PIM accelerators for LLM
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]] ??GPU memory hierarchy for LLM
- [[paper-wiki/concepts/gpu.md|GPU]] ??GPU as primary LLM inference engine
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]] ??NDP for LLM workloads
