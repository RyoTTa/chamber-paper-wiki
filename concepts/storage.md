---
tags: [concept, storage, ssd, flash, nand, ftl]
source_count: 44
last_updated: 2026-06-25
---

# Storage

## Summary

Storage research covers NAND flash memory and SSD technologies, focusing on performance, endurance, data reduction, and new interfaces. Key areas include flash cell optimization, computational storage, key-value stores, and storage-class memory bridging.

## Key Ideas

### NAND Flash Technology
- **3D NAND scaling**: Increasing layers (64??28??56+) for higher density
- **Read disturb**: Similar to RowHammer in DRAM ??adjacent cell reads cause bit errors
- **Reprogramming**: Exploiting TLC flash reprogrammability for larger, faster SSDs ([constructing-large-durable-and-fast-ssd-system-via-reprogramming-3d-tlc-flash-memory.md])
- **Flash-Cosmos**: In-flash bulk bitwise operations using inherent NAND computation ([flash-cosmos-in-flash-bulk-bitwise-operations-using-inherent-computation-capability-of-nand-flash-memory.md])
- **ParaBit**: Parallel bitwise operations in NAND flash SSDs ([parabit-parallel-bitwise-operations-in-nand-flash-memory-based-ssds.md])
- **IDA Coding**: 비트 무효화 시 읽기 지연 시간을 감소시키는 고비트 밀도 플래시 코딩 — 전압 조정으로 MSB 읽기 4회→1-2회, CSB 읽기 2회→1회로 감소, TLC에서 28% 읽기 성능 향상 ([invalid-data-aware-coding-to-enhance-the-read-performance-of-high-density-flash-memories.md])
- **HeatWatch**: 3D NAND 플래시에서 self-recovery 및 온도 효과를 최초로 특성화 — 새로운 신뢰성 모델(오차 4.9%) 개발, dwell time과 온도에 적응적 읽기 참조 전압 최적화로 플래시 수명 3.85배 향상 ([paper-summaries/2018HPCA-summarize/heatwatch-improving-3d-nand-flash-memory-device-reliability-by-exploiting-self-recovery-and-temperature-awareness.md])

### SSD Performance
- **SOML Read**: Rethinking read granularity of 3D NAND SSDs ([soml-read-rethinking-read-granularity-of-3d-nand-ssds.md])
- **Bad block management**: Efficient handling with cluster similarity ([efficient-bad-block-management-with-cluster-similarity.md])
- **Networked SSD**: Flash memory interconnection network for high-bandwidth SSDs ([networked-ssd-flash-memory-interconnection-network-for-high-bandwidth-ssd.md])
- **Shaving Retries**: Sentinels for fast read over high-density 3D flash ([shaving-retries-with-sentinels-for-fast-read-over-high-density-3d-flash.md])
- **Amber (SimpleSSD 2.0)**: 풀시스템 시뮬레이션 환경에서 SSD의 모든 HW/SW 리소스를 정밀 모델링 — gem5 통합, SATA/UFS/NVMe/OCSSD 지원 ([amber-enabling-precise-full-system-simulation-with-detailed-modeling-of-all-ssd-resources.md])

### Computational Storage / SmartSSD
- **DeepStore**: In-storage acceleration for intelligent queries ([deepstore-in-storage-acceleration-for-intelligent-queries.md])
- **ASSASSIN**: Architecture support for stream computing on computational storage ([assasin-architecture-support-for-stream-computing-to-accelerate-computational-storage.md])
- **ICE**: 3D NAND-based in-memory computing for vector similarity search ([ice-an-intelligent-cognition-engine-with-3d-nand-based-in-memory-computing-for-vector-similarity-search-acceleration.md])

### Hybrid Storage / Byte-Addressable SSD
- **2B-SSD**: 바이트 주소 지정과 블록 주소 지정을 동시에 지원하는 SSD 아키텍처 — SSD 내부 DRAM을 BA-buffer로 활용하여 MMIO 기반 직접 접근, sub-1μs 쓰기 지연 시간, 1.2×~2.8× 처리량 향상 ([paper-summaries/2018ISCA-summarize/2b-ssd-the-case-for-dual-byte-and-block-addressable-solid-state-drives.md])
- **FlatFlash**: Exploiting byte-accessibility of SSDs ([flatflash-exploiting-the-byte-accessibility-of-ssds-within-a-unified-memory-storage-hierarchy.md])

### Key-Value Stores and Databases
- **LightStore**: Software-defined network-attached key-value drives ([lightstore-software-defined-network-attached-key-value-drives.md])
- **Check-In**: In-storage checkpointing for key-value store systems ([check-in-in-storage-checkpointing-for-key-value-store-system-leveraging-flash-based-ssds.md])
- **GraphSSD**: Graph semantics-aware SSD ([graphssd-graph-semantics-aware-ssd.md])

### Flash-Based Graph Analytics
- **GraFBoost**: FPGA 기반 플래시 스토리지로 대규모 그래프 분석 — Sort-Reduce 알고리즘으로 랜덤 접근을 순차 SSD 접근으로 변환, 1GB DRAM으로 40억 정점/1280억 엣지 처리 ([paper-summaries/2018ISCA-summarize/grafboost-using-accelerated-flash-storage-for-external-graph-analytics.md])

### Data Reduction
- **FIDR**: Scalable storage for fine-grain inline data reduction ([fidr-scalable-storage-for-fine-grain-inline-data-reduction.md])
- **CIDR**: Cost-effective in-line data reduction for SSD arrays ([cidr-a-cost-effective-in-line-data-reduction-system-for-terabit-per-second-scale-ssd-arrays.md])
- **SMASH**: Co-designing software compression and HW indexing ([smash-co-designing-software-compression-and-hw-indexing.md])

### CXL-based Storage
- CXL memory-semantic SSDs bridge storage and memory ??ByteFS provides system support ([bytefs-system-support-for-cxl-based-memory-semantic-solid-state-drives.md])
- Full-system simulation framework for CXL-based SSD memory systems ([full-system-simulation-framework-for-cxl-based-ssd-memory-system.md])

### Secure Storage
- **StrongBox**: 스트림 암호 기반 전체 드라이브 암호화 — LFS 특성과 TEE 카운터를 활용하여 AES-XTS보다 읽기 성능 평균 1.72배 향상, 강화된 무결성 보장 제공 ([paper-summaries/2018ASPLOS-summarize/strongbox-confidentiality-integrity-and-performance-using-stream-ciphers-for-full-drive-encryption.md])

## Related Papers

- [invalid-data-aware-coding-to-enhance-the-read-performance-of-high-density-flash-memories.md]
- See `paper-summaries/` directories for MICRO, ATC, ISCA (2019??026)

## Cross-references

- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]] ??Storage class memory
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]] ??Computational storage as NDP
- [[paper-wiki/concepts/compression.md|Compression]] ??Data reduction techniques
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]] ??CXL-based storage disaggregation
- [[paper-wiki/concepts/dram.md|DRAM]] ??Read disturb analogy to RowHammer
