---
tags: [overview, landscape]
last_updated: 2026-06-19
---

# Computer Architecture Research Landscape (2019??026)

## Key Themes

### 1. The Data Movement Bottleneck

The central problem across virtually all research areas is the **cost of moving data**. Energy and latency of data movement dominate computation costs:
- DRAM ??processor: ~100횞 more energy than FP operation
- CXL fabric access: 2-5횞 latency of local DRAM
- GPU-CPU KV cache transfer: dominates LLM inference time

This drives research in PIM, NDP, compression, caching, and disaggregation.

### 2. LLM Inference as a Memory Problem

The rise of large language models has fundamentally shifted the research landscape. LLM inference is increasingly recognized as a **memory-bound problem** rather than compute-bound:
- KV cache size grows with sequence length and batch, exceeding GPU memory
- Phase splitting separates memory-bound decode from compute-bound prefill
- Sparse attention and KV compression reduce memory footprint
- PIM/NDP accelerators target LLM-specific operations

### 3. CXL as a Unifying Fabric

Compute Express Link (CXL) has emerged as the dominant interconnect for memory disaggregation and tiering:
- Memory pooling across servers
- Cache-coherent fabric-attached memory
- Tiered memory systems (local DRAM + CXL far memory)
- Computational storage over CXL

CXL adoption creates new research problems in coherency, page migration, security, and resource management.

### 4. DRAM Scaling Crisis

DRAM technology faces fundamental scaling challenges:
- RowHammer vulnerability worsens with each generation
- Retention times decrease with smaller cells
- Refresh power becomes a significant fraction of total power
- In-DRAM ECC and TRR add complexity and cost

### 5. Processing-in-Memory Matures

PIM has moved from academic proposals to commercial reality:
- Samsung PIM-HBM: commercial HBM with integrated processing
- UPMEM: real PIM hardware with software stack
- Bank-level and crossbar-based designs targeting different workloads
- Full software stacks, compilers, and memory allocators

### 6. Specialization vs. Generality

The tension between specialized accelerators and general-purpose processors shapes the landscape:
- PIM/NDP for specific workloads (recommendation, genomics, graph)
- LLM-specific accelerators and KV cache management
- GPU specialization for ML training and inference
- CXL-based composable infrastructure for flexible specialization

## Timeline

| Year | Key Developments |
|---|---|
| 2019 | Foundation: RowHammer characterization, NVM persistency, early PIM |
| 2020 | DRAM scaling analysis, counter-based RowHammer mitigation, PIM acceleration |
| 2021 | Samsung PIM-HBM announced, Midgard virtual memory, commercial DRAM PIM |
| 2022 | CXL-based disaggregation, LLM inference optimization, compression for caching |
| 2023 | Phase splitting (Splitwise), sparse KV caching (ALISA), LLM inference systems |
| 2024 | CXL ecosystem matures, LLM inference at scale, computational storage advances |
| 2025 | CXL 3.0, memory tiering at scale, PIM software maturity, full-system disaggregation |
| 2026 | CXL-based SSDs, disaggregated LLM inference, next-gen RowHammer defenses |

## Open Challenges

1. **Coherent disaggregation**: Making CXL-attached memory truly transparent and efficient
2. **LLM inference at scale**: Cost-effective serving for billion-parameter models
3. **RowHammer endgame**: As DRAM scales below 10nm, can any mitigation keep pace?
4. **PIM programmability**: Making PIM accessible to mainstream programmers
5. **Memory security**: Encryption, integrity, and isolation for disaggregated and persistent memory
6. **Unified tiering**: Automatic, workload-aware data placement across memory tiers
7. **GPU memory capacity**: Breaking the HBM capacity wall for large models
8. **Cross-layer optimization**: Co-design across algorithms, systems, and hardware
