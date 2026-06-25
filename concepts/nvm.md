---
tags: [concept, nvm, persistent-memory, pmem, scm]
source_count: 34
last_updated: 2026-06-26
---

# Non-Volatile Memory

## Summary

Non-Volatile Memory (NVM), also known as persistent memory or storage-class memory (SCM), bridges the gap between DRAM and storage. Research covers crash consistency, programming models, security, performance optimization, and hybrid DRAM/NVM system design.

## Key Ideas

### Crash Consistency and Persistency
- **SSP**: Eliminating redundant writes in failure-atomic NVRAMs via shadow sub-paging ([ssp-eliminating-redundant-writes-in-failure-atomic-nvrams-via-shadow-sub-paging.md])
- **HOOP**: Efficient hardware-assisted out-of-place update for NVM ([hoop-efficient-hardware-assisted-out-of-place-update-for-non-volatile-memory.md])
- **MorLog**: Morphable hardware logging for atomic persistence ([morlog-morphable-hardware-logging-for-atomic-persistence-in-non-volatile-main-memory.md])
- **Relaxed Persist Ordering**: Using strand persistency ([relaxed-persist-ordering-using-strand-persistency.md])
- **Distributed logless atomic durability** with persistent memory ([distributed-logless-atomic-durability-with-persistent-memory.md])
- **MOD**: Minimally ordered durable datastructures ([mod-minimally-ordered-durable-datastructures-for-persistent-memory.md])
- **DHTM**: 최초의 완전한 하드웨어 ACID 트랜잭션 메모리 솔루션 — 상용 HTM + 하드웨어 redo 로깅 결합, L1→LLC 오버플로우 지원, 기존 기술 대비 21%~25% 성능 향상 ([paper-summaries/2018ISCA-summarize/dhtm-durable-hardware-transactional-memory.md])
- **Lazy Persistency**: 캐시의 자연적 퇴출을 통해 NVM으로 데이터 전송 — Eager Persistency 대비 실행 시간 9%→1%, 쓰기 증폭 21%→3%로 대폭 감소. Modular Checksum으로 오류 탐지(2×10⁻⁹ 미만), 재계산 기반 복구 ([paper-summaries/2018ISCA-summarize/lazy-persistency-a-high-performing-and-write-efficient-software-persistency-technique.md])

### Programming Models and Software
- **Espresso**: Java에서 NVM 활용 통합 지속성 프레임워크 — PJH(Persistent Java Heap)와 PJO(Persistent Java Object)로 기존 프로그램 호환성 유지 + 최대 256x speedup ([paper-summaries/2018ASPLOS-summarize/espresso-brewing-java-for-more-non-volatility-with-non-volatile-memory.md])
- **AsymNVM**: Framework for persistent data structures on asymmetric NVM ([asymnvm-an-efficient-framework-for-persistent-data-structures-on-asymmetric-nvm-architecture.md])
- **Supporting legacy libraries** on NVM with user-transparent approach ([supporting-legacy-libraries-on-non-volatile-memory-a-user-transparent-approach.md])
- **Finding and fixing performance pathologies** in PM software stacks ([finding-and-fixing-performance-pathologies-in-persistent-memory-software-stacks.md])
- **Revamping SCM** with hardware-automated memory-over-storage solution ([revamping-storage-class-memory-with-hardware-automated-memory-over-storage-solution.md])

### Secure NVM
- **Anubis**: Ultra-low overhead and recovery for secure NVMs ([anubis-ultra-low-overhead-and-recovery-for-secure-nvms.md])
- **Lelantus**: Fine-granularity copy-on-write for secure NVMs ([lelantus-fine-granularity-copy-on-write-operations-for-secure-non-volatile-memories.md])
- **SuperMem**: Application-transparent secure persistent memory ([supermem-enabling-application-transparent-secure-persistent-memory-with-low-overheads.md])
- **Triad-NVM**: Persistency for integrity-protected encrypted NVMs ([triad-nvm-persistency-for-integrity-protected-and-encrypted-non-volatile-memories.md])
- **DeWrite**: 암호화된 NVM의 성능과 수명을 향상시키는 중복 제거 기반 쓰기 최적화 — 쓰기 54% 감소, 쓰기 속도 4.2배 향상, IPC 82% 향상 ([improving-the-performance-and-endurance-of-encrypted-non-volatile-main-memory-through-deduplicating-writes.md])
- **Selective Counter-Atomicity**: 암호화된 NVMM 시스템에서 crash consistency와 메모리 암호화 간의 상호작용 분석 — 선택적 counter-atomicity를 통해 1~8코어 시스템에서 6~40% 성능 향상 ([paper-summaries/2018HPCA-summarize/crash-consistency-in-encrypted-non-volatile-main-memory-systems.md])

### NVM Architecture
- **NVDIMM-C**: Byte-addressable NVM module compatible with DDR interfaces ([nvdimm-c-a-byte-addressable-non-volatile-memory-module-for-compatibility-with-standard-ddr-memory-interfaces.md])
- **Unbounded HTM**: Hardware transactional memory for hybrid DRAM/NVM systems ([unbounded-hardware-transactional-memory-for-a-hybrid-dram-nvm-memory-system.md])
- **P-INSPECT**: Architectural support for programmable NVM frameworks ([p-inspect-architectural-support-for-programmable-non-volatile-memory-frameworks.md])
- **In-Memory Data Parallel Processor**: ReRAM 기반 인메모리 데이터 병렬 프로세서 — TensorFlow 컴파일러와 SIMD 실행 모델로 Parsec에서 7.5x, Rodinia에서 763x speedup ([paper-summaries/2018ASPLOS-summarize/in-memory-data-parallel-processor.md])

### Hybrid DRAM/NVM Systems
- **Binary Star**: Coordinated reliability in heterogeneous memory systems ([binary-star-coordinated-reliability-in-heterogeneous-memory-systems.md])
- **Stealth-Persist**: Architectural support for persistent applications in hybrid memory ([stealth-persist-architectural-support-for-persistent-applications-in-hybrid-memory.md])

### NVM Characterization
- **Characterizing and Modeling NVM Systems** ([characterizing-and-modeling-non-volatile-memory-systems.md])
- **TVARAK**: Software-managed hardware offload for NVM storage redundancy ([tvarak-software-managed-hardware-offload-for-redundancy-in-direct-access-nvm-storage.md])
- **BOSS**: Bandwidth-optimized search accelerator for SCM ([boss-bandwidth-optimized-search-accelerator-for-storage-class-memory.md])

## Related Papers

- [espresso-brewing-java-for-more-non-volatility-with-non-volatile-memory.md]
- **PiCL**: Software-transparent crash consistency for NVMM — 멀티-언도 로깅 + 캐시 기반 로깅으로 1% 미만 오버헤드 달성 ([paper-summaries/2018MICRO-summarize/picl-a-software-transparent-persistent-cache-log-for-nonvolatile-main-memory.md])
- [improving-the-performance-and-endurance-of-encrypted-non-volatile-main-memory-through-deduplicating-writes.md]
- See `paper-summaries/` for ISCA, MICRO, HPCA (2019??026)

## Cross-references

- [[paper-wiki/concepts/storage.md|Storage]] ??NVM bridges memory and storage
- [[paper-wiki/concepts/dram.md|DRAM]] ??NVM as complement/alternative to DRAM
- [[paper-wiki/concepts/security.md|Security]] ??Secure NVM design
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]] ??NVM as tier in heterogeneous memory
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]] ??NVM in disaggregated systems
