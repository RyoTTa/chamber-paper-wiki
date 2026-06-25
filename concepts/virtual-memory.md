---
tags: [concept, virtual-memory, tlb, page-table, mmu]
source_count: 27
last_updated: 2026-06-25
---

# Virtual Memory

## Summary

Virtual memory research focuses on address translation efficiency as data-intensive workloads with large working sets strain traditional TLB-based designs. Key themes include new translation architectures, huge page support, GPU address translation, virtualization, and compression-based approaches.

## Key Ideas

### Translation Architecture Innovations
- **Midgard**: Intermediate address space between virtual and physical; VMA-based translation with Virtual Lookaside Buffer (VLB) - only ~10 entries needed ([rebooting-virtual-memory-with-midgard.md])
- **Elastic Cuckoo Page Tables**: Parallel virtualized memory translation using cuckoo hashing ([parallel-virtualized-memory-translation-with-nested-elastic-cuckoo-page-tables.md])
- **Translation Ranger**: OS support for contiguity-aware TLBs ([translation-ranger-os-support-for-contiguity-aware-tlbs.md])
- **BabelFish**: Fusing address translations for containers ([babelfish-fusing-address-translations-for-containers.md])

### TLB and Page Walk Optimization
- **PTEMagnet**: Fine-grained physical memory reservation for faster page walks ([ptemagnet-fine-grained-physical-memory-reservation-for-faster-page-walks-in-public-clouds.md])
- **Every Walk's a Hit**: Making page walks single-access cache hits ([every-walks-a-hit-making-page-walks-single-access-cache-hits.md])
- **Agile TLB Prefetching**: Exploiting page table locality for TLB prefetching ([exploiting-page-table-locality-for-agile-tlb-prefetching.md])
- **HawkEye**: Efficient fine-grained OS support for huge pages ([hawkeye-efficient-fine-grained-os-support-for-huge-pages.md])
- **NOCSTAR**: 분산 TLB 슬라이스 + 경량 단일 사이클 인터커넥트로 공유 TLB 지연시간 감소 — 14-hop traversal 한 사이클 처리, 에너지 절감 ([paper-summaries/2018MICRO-summarize/scalable-distributed-last-level-tlbs-using-low-latency-interconnects.md])
- **LATR**: Lazy TLB coherence로 IPI 없이 비동기적 TLB 무효화 처리 — Apache에서 59.9% 성능 향상, munmap()에서 70.8% 지연 시간 감소 ([paper-summaries/2018ASPLOS-summarize/latr-lazy-translation-coherence.md])

### Huge Pages
- Large page sizes (2MB/1GB) reduce TLB misses but introduce management complexity
- Memory fragmentation, promotion/demotion, and migration overheads
- **DyLeCT**: Achieving huge-page-like translation performance for hardware-compressed memory ([dylect-achieving-huge-page-like-translation-performance-for-hardware-compressed-memory.md])

### GPU Virtual Memory
- **DVM (Devirtualized Memory)**: Identity Mapping(VA==PA)으로 가속기의 VM 오버헤드 1.7-3.5%로 감소 — Permission Entry로 컴팩트 페이지 테이블, AVC로 TLB/PWC 대체 ([paper-summaries/2018ASPLOS-summarize/devirtualizing-memory-in-heterogeneous-systems.md])
- Improving address translation in multi-GPUs ([improving-address-translation-in-multi-gpus.md])
- Designing virtual memory system of MCM GPUs ([designing-virtual-memory-system-of-mcm-gpus.md])
- **Mitosis**: Transparently self-replicating page tables for large-memory machines ([mitosis-transparently-self-replicating-page-tables-for-large-memory-machines.md])
- **Filtering Translation Bandwidth with Virtual Caching**: GPU 가상 캐시 계층을 통한 주소 번역 대역폭 필터링 — 이상적 MMU 대비 98% 성능, 대역폭 60% 감소 ([paper-summaries/2018ASPLOS-summarize/filtering-translation-bandwidth-with-virtual-caching.md])

### Memory Compression and Translation
- Translation-optimized memory compression for capacity ([translation-optimized-memory-compression-for-capacity.md])
- DAXVM: Stressing the limits of memory as a file interface ([daxvm-stressing-the-limits-of-memory-as-a-file-interface.md])
- Compressed memory systems need translation support for efficient access

### Virtualization and Containers
- **vMitosis**: Fast local page tables for virtualized NUMA servers ([fast-local-page-tables-for-virtualized-numa-servers-with-vmitosis.md])
- Page table locality exploitation in virtualized environments

## Related Papers

- [devirtualizing-memory-in-heterogeneous-systems.md]
- [rebooting-virtual-memory-with-midgard.md]
- [parallel-virtualized-memory-translation-with-nested-elastic-cuckoo-page-tables.md]
- [exploiting-page-table-locality-for-agile-tlb-prefetching.md]
- [improving-address-translation-in-multi-gpus.md]
- [dylect-achieving-huge-page-like-translation-performance-for-hardware-compressed-memory.md]

- **Neighborhood-Aware Address Translation**: 비정형 GPU 워크로드의 주소 변환 근방 인식 합치기 — 메모리 접근 37% 감소, 1.7배 가속 ([paper-summaries/2018MICRO-summarize/neighborhood-aware-address-translation-for-irregular-gpu-applications.md])

## Cross-references

- [[paper-wiki/concepts/gpu.md|GPU]] ??GPU virtual memory is a distinct sub-area
- [[paper-wiki/concepts/compression.md|Compression]] ??Translation-aware memory compression
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]] ??Page migration and translation in tiered systems
- [[paper-wiki/concepts/dram.md|DRAM]] ??Physical memory substrate for virtual memory
