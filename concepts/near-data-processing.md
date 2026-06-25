---
tags: [concept, near-data-processing, ndp, computational-storage]
source_count: 29
last_updated: 2026-06-25
---

# Near-Data Processing

## Summary

Near-Data Processing (NDP) moves computation closer to where data resides, reducing data movement energy and latency. This covers processing near DRAM banks (PIM), near storage controllers (computational storage), and near network interfaces (SmartNICs). NDP is closely related to PIM but generally refers to systems where processing logic is near (not inside) the memory array.

## Key Ideas

### Near-Memory Processing
- **CoNDA**: Cache coherence support for near-data accelerators ([conda-efficient-cache-coherence-support-for-near-data-accelerators.md])
- **Active-Routing**: Compute on the way for near-data processing ([active-routing-compute-on-the-way-for-near-data-processing.md])
- **MEDAL**: Scalable DIMM-based NDP for DNA seeding ([medal-scalable-dimm-based-ndp-accelerator-for-dna-seeding-algorithm.md])
- **TensorDIMM**: Near-memory processing for embeddings and tensor operations ([tensordimm-near-memory-processing-for-embeddings-and-tensor-operations.md])
- **ABC-DIMM**: Communication bottleneck alleviation in DIMM-based NDP ([abc-dimm-alleviating-the-bottleneck-of-communication-in-dimm-based-near-memory-processing.md])
- **FAFNIR**: Near-memory intelligent reduction for sparse gathering ([fafnir-accelerating-sparse-gathering-by-using-efficient-near-memory-intelligent-reduction.md])
- **Near-data acceleration with concurrent host access** ([near-data-acceleration-with-concurrent-host-access.md])
- **Beacon**: Scalable NDP for genome analysis with CXL support ([beacon-scalable-near-data-processing-accelerators-for-genome-analysis-near-memory-pool-with-the-cxl-support.md])
- **MCN**: Application-transparent NDP via Memory Channel Network — DDR 채널 위에서 이더넷 통신을 에뮬레이션하여 기존 MPI/Spark를 변경 없이 사용 가능 ([application-transparent-near-memory-processing-architecture-with-memory-channel-network.md])
- **AMS**: Adaptive scheduler for asymmetric memory hierarchies — 미스 곡선 기반 스케줄링으로 NDP/프로세서 다이 간 최적 배치 ([adaptive-scheduling-for-systems-with-asymmetric-memory-hierarchies.md])
- **GraphR**: ReRAM 기반 그래프 처리 가속기 — 크로스바에서 아날로그 SpMV 수행, CPU 대비 16× speedup, 34× energy 절감 ([paper-summaries/2018HPCA-summarize/graphr-accelerating-graph-processing-using-reram.md])

### Computational Storage
- **DeepStore**: In-storage acceleration for intelligent queries ([deepstore-in-storage-acceleration-for-intelligent-queries.md])
- **ASSASSIN**: Architecture support for stream computing on computational storage ([assasin-architecture-support-for-stream-computing-to-accelerate-computational-storage.md])
- **ICE**: 3D NAND-based in-memory computing for vector similarity search ([ice-an-intelligent-cognition-engine-with-3d-nand-based-in-memory-computing-for-vector-similarity-search-acceleration.md])
- **ParaBit**: Parallel bitwise operations in NAND flash SSDs ([parabit-parallel-bitwise-operations-in-nand-flash-memory-based-ssds.md])
- **GraFBoost**: FPGA 기반 플래시 가속 그래프 분석 — Sort-Reduce로 랜덤 접근을 순차 SSD 접근으로 변환, 1GB DRAM으로 테라바이트급 그래프 처리 ([paper-summaries/2018ISCA-summarize/grafboost-using-accelerated-flash-storage-for-external-graph-analytics.md])

### Near-Cache Computing
- **REDUCT**: Near-cache compute for DNN inference on multi-core CPUs ([reduct-near-cache-compute-for-dnn-inference-on-multi-core-cpus.md])
- **GenCache**: Leveraging in-cache operators for sequence alignment ([gencache-leveraging-in-cache-operators-for-sequence-alignment.md])

### NDP Software and Systems
- **SynCron**: Synchronization support for NDP systems ([synCron-efficient-synchronization-support-for-near-data-processing.md])
- Integration with CXL for cache-coherent NDP
- Programming models and compilation for NDP

## Related Papers

See also [[paper-wiki/concepts/pim.md|Processing-in-Memory]] ??significant overlap; PIM papers often cover NDP

## Cross-references

- **MPT**: Multi-dimensional Parallel Training on Memory-Centric Architecture — Winograd 변환의 intra-tile 병렬성을 활용한 NDP 기반 CNN 학습 가속, 최대 2.7배 성능 향상 ([paper-summaries/2018MICRO-summarize/multi-dimensional-parallel-training-of-winograd-layer-on-memory-centric-architecture.md])
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]] ??Overlapping concept space
- [[paper-wiki/concepts/storage.md|Storage]] ??Computational storage
- [[paper-wiki/concepts/cache.md|Cache]] ??Near-cache computing
- [[paper-wiki/concepts/dram.md|DRAM]] ??Near-DRAM processing
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]] ??NDP in disaggregated systems
