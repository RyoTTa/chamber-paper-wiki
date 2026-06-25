---
tags: [concept, dram, reliability, scaling]
source_count: 31
last_updated: 2026-06-25
---

# DRAM

## Summary

DRAM (Dynamic Random Access Memory) is the primary main memory technology in modern computing systems. Research from 2019??026 focuses on DRAM reliability under scaling pressure, cell characterization, refresh optimization, new interfaces (HBM, CXL), and vulnerability to disturbances like RowHammer.

## Key Ideas

### DRAM Cell Scaling and Reliability
- As DRAM technology scales to smaller nodes, cell capacitance decreases, making cells more vulnerable to disturbance and retention failures
- Studies show that newer DRAM chips are increasingly susceptible to RowHammer-induced bit flips ([revisiting-rowhammer-an-experimental-analysis-of-modern-dram-devices-and-mitigation-techniques.md])
- Temperature, data patterns, and access patterns significantly affect DRAM error rates

### Refresh and Latency
- Traditional refresh mechanisms consume significant power and impact performance
- CLR-DRAM enables dynamic capacity-latency trade-offs by exploiting DRAM timing margins ([clr-dram-a-low-cost-dram-architecture-enabling-dynamic-capacity-latency-trade-off.md])
- CryoGuard explores DRAM design for cryogenic computing, enabling near-refresh-free operation ([cryoguard-a-near-refresh-free-robust-dram-design-for-cryogenic-computing.md])
- **CAL**: Charge-Level-Aware Look-Ahead Partial Restoration으로 복원 지연시간 14.7% 감소 — 메모리 컨트롤러에서만 구현, ChargeCache/Restore Truncation과 호환 ([paper-summaries/2018MICRO-summarize/reducing-dram-latency-via-charge-level-aware-look-ahead-partial-restoration.md])

### HBM (High Bandwidth Memory)
- HBM provides significantly higher bandwidth than traditional DDR but faces thermal and integration challenges
- PIM-HBM integrates processing units directly into HBM banks for near-data processing ([hardware-architecture-and-software-stack-for-pim-based-on-commercial-dram-technology.md])
- Software-defined address mapping for 3D-stacked memory enables flexible data placement ([software-defined-address-mapping-a-case-on-3d-memory.md])

### DRAM Microarchitecture
- DRAMScope uncovers DRAM microarchitecture by issuing memory commands and observing timing ([dramscope-uncovering-dram-microarchitecture-and-characteristics-by-issuing-memory-commands.md])
- In-DRAM ECC functions can be reverse-engineered through bit-exact ECC recovery (BEER) techniques

### New DRAM Structures
- Precharge-free DRAM (PF-DRAM) reduces the precharge time overhead ([pf-dram-a-precharge-free-dram-structure.md])
- Native DRAM Cache re-architects DRAM as a large-scale cache for data centers ([native-dram-cache-re-architecting-dram-as-a-large-scale-cache-for-data-centers.md])
- CODIC provides a low-cost substrate for custom in-DRAM functionalities and optimizations ([codic-a-low-cost-substrate-for-enabling-custom-in-dram-functionalities-and-optimizations.md])
- **SILO**: 다이 스택 DRAM을 활용한 프라이빗 LLC 구현 — 지연 시간 최적화 설계로 45% 지연 시간 감소, 11.5ns 접근 지연 시간 달성 ([farewell-my-shared-llc-a-case-for-private-die-stacked-dram-caches-for-servers.md])

### DRAM Reliability and ECC
- **DUO**: 온칩 중복성의 이중 활용으로 IECC 비효율성 해결 — IECC 대비 평균 2-3% 성능 저하 수준, 평균 4-14% 낮은 에너지 소비, 높은 신뢰성 달성 ([paper-summaries/2018HPCA-summarize/duo-exposing-on-chip-redundancy-to-rank-level-ecc-for-high-reliability.md])

### DRAM Parallelism and Resource Management
- **ERUCA**: 효율적인 서브뱅킹 및 주파수 확장 가능한 DRAM 아키텍처 — 거의 제로의 면적 오버헤드(<0.3%)로 15% 성능 향상 ([paper-summaries/2018HPCA-summarize/eruca-efficient-dram-resource-utilization-and-resource-conflict-avoidance-for-memory-system-parallelism.md])

## Related Papers

- [revisiting-rowhammer-an-experimental-analysis-of-modern-dram-devices-and-mitigation-techniques.md] ??Large-scale DRAM characterization for RowHammer
- [dramscope-uncovering-dram-microarchitecture-and-characteristics-by-issuing-memory-commands.md] ??DRAM microarchitecture discovery
- [clr-dram-a-low-cost-dram-architecture-enabling-dynamic-capacity-latency-trade-off.md] ??Dynamic capacity-latency trade-off
- [cryoguard-a-near-refresh-free-robust-dram-design-for-cryogenic-computing.md] ??Cryogenic DRAM
- [pf-dram-a-precharge-free-dram-structure.md] ??Precharge-free DRAM
- [codic-a-low-cost-substrate-for-enabling-custom-in-dram-functionalities-and-optimizations.md] ??Custom in-DRAM functionalities
- [figaro-improving-system-performance-via-fine-grained-in-dram-data-relocation-and-caching.md] ??In-DRAM data relocation
- [dve-improving-dram-reliability-and-performance-on-demand-via-coherent-replication.md] ??Coherent replication for DRAM reliability
- [farewell-my-shared-llc-a-case-for-private-die-stacked-dram-caches-for-servers.md] ??Die-stacked DRAM for private LLC

## Cross-references

- [[paper-wiki/concepts/rowhammer.md|RowHammer]] ??DRAM disturbance vulnerability
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]] ??PIM builds on DRAM bank-level parallelism
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]] ??DRAM as fast tier in heterogeneous memory
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]] ??NVM as alternative/complement to DRAM
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]] ??Processing near DRAM arrays
