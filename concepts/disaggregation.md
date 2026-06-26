---
tags: [concept, disaggregation, cxl, fabric, rack-scale]
source_count: 15
last_updated: 2026-06-19
---

# Disaggregation

## Summary

Memory and storage disaggregation separates compute, memory, and storage into independent resource pools connected via fabric (CXL, InfiniBand, Ethernet). This enables better resource utilization, independent scaling, and failure isolation in data centers. CXL has emerged as the dominant interconnect for memory disaggregation.

## Key Ideas

### CXL-based Memory Disaggregation
- **Clio**: Hardware-software co-designed disaggregated memory system ([clio-a-hardware-software-co-designed-disaggregated-memory-system.md])
- **ThymesisFlow**: Software-defined HW/SW co-designed interconnect for rack-scale memory ([thymesisflow-a-software-defined-hw-sw-co-designed-interconnect-stack-for-rack-scale-memory-disaggregation.md])
- **TMO**: Transparent memory offloading in datacenters ([tmo-transparent-memory-offloading-in-datacenters.md])
- **COSMOS**: CXL-based full in-memory system for approximate nearest neighbor search ([cosmos-a-cxl-based-full-in-memory-system-for-approximate-nearest-neighbor-search.md])
- **Cohet**: CXL-driven coherent heterogeneous computing framework ([cohet-a-cxl-driven-coherent-heterogeneous-computing-framework-with-hardware-calibrated-full-system-simulation.pdf])

### Remote Memory / Far Memory
- **Software-Defined Far Memory** in warehouse-scale computers ([software-defined-far-memory-in-warehouse-scale-computers.md])
- **Rethinking software runtimes** for disaggregated memory ([rethinking-software-runtimes-for-disaggregated-memory.md])
- **DeACT**: Architecture-aware virtual memory support for fabric-attached memory ([deact-architecture-aware-virtual-memory-support-for-fabric-attached-memory-systems.md])

### GPU Disaggregation
- Enabling large-scale DL training with cache-coherent disaggregated memory ([enabling-efficient-large-scale-dl-training-with-cache-coherent-disaggregated-memory-systems.md])
- GPU memory pooling over CXL fabric

### CXL Protocols and Architectures
- **CXL-SpeckV**: Disaggregated FPGA speculative KV cache ([cxl-speckv-a-disaggregated-fpga-speculative-kv-cache.md])
- **Octopus**: Enhancing CXL memory pods via sparse topology ([octopus-enhancing-cxl-memory-pods-via-sparse-topology.md])
- **TRACE**: Lossless compression for CXL bandwidth ([trace-unlocking-effective-cxl-bandwidth-via-lossless-compression.md])
- **Hailstorm**: Disaggregated compute and storage for LSM databases ([hailstorm-disaggregated-compute-and-storage-for-distributed-lsm-based-databases.md])

### Key Challenges
- Coherency and consistency across disaggregated nodes
- Page migration and fault handling over fabric
- Security and isolation in shared memory pools
- Performance overhead of fabric access vs local DRAM

## Related Papers

- [clio-a-hardware-software-co-designed-disaggregated-memory-system.md]
- [software-defined-far-memory-in-warehouse-scale-computers.md]
- [thymesisflow-a-software-defined-hw-sw-co-designed-interconnect-stack-for-rack-scale-memory-disaggregation.md]
- [tmo-transparent-memory-offloading-in-datacenters.md]
- [3779212-3790121.md] - A Programming Model for Disaggregated Memory over CXL

## Cross-references

- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]] ??Disaggregated memory as part of tiering
- [[paper-wiki/concepts/cache.md|Cache]] ??Caching for remote memory
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]] ??Address translation for disaggregated memory
- [[paper-wiki/concepts/storage.md|Storage]] ??CXL-based storage disaggregation
- [[paper-wiki/concepts/security.md|Security]] ??Security for fabric-attached memory
