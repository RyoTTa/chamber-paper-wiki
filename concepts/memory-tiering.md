---
tags: [concept, memory-tiering, cxl, numa, disaggregation]
source_count: 16
last_updated: 2026-06-25
---

# Memory Tiering

## Summary

Memory tiering manages multiple memory technologies with different performance/cost characteristics (e.g., DRAM + CXL-attached memory, DRAM + NVM) as a unified hierarchy. Research spans OS-level page management, hardware support, CXL-based disaggregated memory, and application-transparent tiering.

## Key Ideas

### Page Management and Migration
- **Nimble Page Management**: Efficient page management for tiered memory systems ([nimble-page-management-for-tiered-memory-systems.md])
- **PageSeer**: Using page walks to trigger page swaps in hybrid memory systems ([pageseer-using-page-walks-to-trigger-page-swaps-in-hybrid-memory-systems.md])
- **Hybrid2**: Combining caching and migration in hybrid memory systems ([hybrid2-combining-caching-and-migration-in-hybrid-memory-systems.md])
- **Jenga**: Responsive tiered memory management without thrashing ([jenga-responsive-tiered-memory-management-without-thrashing.md])

### CXL-based Disaggregated Memory
- **TMO**: Transparent memory offloading in datacenters ([tmo-transparent-memory-offloading-in-datacenters.md])
- **Clio**: Hardware-software co-designed disaggregated memory system ([clio-a-hardware-software-co-designed-disaggregated-memory-system.md])
- **Octopus**: Enhancing CXL memory pods via sparse topology ([octopus-enhancing-cxl-memory-pods-via-sparse-topology.md])
- **TRACE**: Unlocking effective CXL bandwidth via lossless compression ([trace-unlocking-effective-cxl-bandwidth-via-lossless-compression.md])

### Application-Specific Tiering
- **KLOCs**: Kernel-level object contexts for heterogeneous memory systems ([klocs-kernel-level-object-contexts-for-heterogeneous-memory-systems.md])
- **CARAT/CAKE**: Replacing paging via compiler-kernel cooperation ([carat-cake-replacing-paging-via-compiler-kernel-cooperation.md])
- **Memory-Harvesting VMs**: Dynamic memory reclamation in cloud platforms ([memory-harvesting-vms-in-cloud-platforms.md])
- **Improving DL training** with cache-coherent disaggregated memory ([enabling-efficient-large-scale-dl-training-with-cache-coherent-disaggregated-memory-systems.md])

### Heterogeneous Memory for Recommendations
- **SPACE**: Locality-aware processing in heterogeneous memory ([space-locality-aware-processing-in-heterogeneous-memory-for-recommendations.md])
- **Sentinel**: Efficient tensor migration for DL on heterogeneous memory ([sentinel-efficient-tensor-migration-on-heterogeneous-memory-systems-for-deep-learning.md])

### Dynamic Heterogeneous Memory Reconfiguration
- **CHAMELEON**: 캐시와 PoM을 동적으로 전환하는 하이브리드 이종 메모리 아키텍처 — PoM 대비 11.6%, 캐시 대비 24.2% 성능 향상 ([paper-summaries/2018MICRO-summarize/chameleon-a-dynamically-reconfigurable-heterogeneous-memory-system.md])
- **Beyond the Memory Wall**: 디바이스 사이드 인터커넥트에 메모리 노드를 집적하는 MC-DLA — DC-DLA 대비 2.8배 속도 향상 ([paper-summaries/2018MICRO-summarize/beyond-the-memory-wall-a-case-for-memory-centric-hpc-system-for-deep-learning.md])

### CXL Era Research
- Exploring memory tiering systems in the CXL era via FPGA-based prototyping ([exploring-memory-tiering-systems-in-the-cxl-era-via-fpga-based-prototyping.md])
- FPGA-based emulation and device-side management for CXL tiering ([fpga-based-emulation-and-device-side-management-for-cxl-based-memory-tiering-sys.md])
- Memory-side tiering telemetry limits study ([a-limits-study-of-memory-side-tiering-telemetry.pdf])
- Analyzing two-tier disaggregated memory protection schemes ([analyzing-a-two-tier-disaggregated-memory-protection-scheme-based-on-memory-repl.pdf])
- From good to great: improving tiering performance through parameter tuning ([from-good-to-great-improving-memory-tiering-performance-through-parameter-tuning.md])

## Related Papers

- [nimble-page-management-for-tiered-memory-systems.md]
- [clio-a-hardware-software-co-designed-disaggregated-memory-system.md]
- [tmo-transparent-memory-offloading-in-datacenters.md]
- [hybrid2-combining-caching-and-migration-in-hybrid-memory-systems.md]
- [jenga-responsive-tiered-memory-management-without-thrashing.md]
- [chameleon-a-dynamically-reconfigurable-heterogeneous-memory-system.md]
- [beyond-the-memory-wall-a-case-for-memory-centric-hpc-system-for-deep-learning.md]

## Cross-references

- [[paper-wiki/concepts/disaggregation.md|Disaggregation]] ??CXL and fabric-disaggregated memory
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]] ??NVM as slow tier
- [[paper-wiki/concepts/dram.md|DRAM]] ??DRAM as fast tier
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]] ??Page management for tiering
- [[paper-wiki/concepts/compression.md|Compression]] ??Compression for CXL bandwidth
