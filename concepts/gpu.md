---
tags: [concept, gpu, cuda, memory-management, multi-tenancy]
source_count: 15
last_updated: 2026-06-25
---

# GPU

## Summary

GPU research focuses on memory management, virtual memory, multi-tenancy, and architectural support for emerging workloads (LLM, recommendation, scientific computing). Key themes include efficient address translation, memory partitioning for multi-tenant GPU systems, and characterization of GPU memory errors.

## Key Ideas

### GPU Memory Architecture
- **HBM integration**: GPU and HBM co-design for maximum bandwidth
- **Multi-GPU systems**: Coherent memory across GPU clusters
- Improving address translation in multi-GPUs ([improving-address-translation-in-multi-gpus.md])
- Designing virtual memory system of MCM (multi-chip module) GPUs ([designing-virtual-memory-system-of-mcm-gpus.md])
- **Filtering Translation Bandwidth with Virtual Caching**: GPU 가상 캐시 계층을 통한 주소 번역 대역폭 필터링 — 이상적 MMU 대비 98% 성능 달성, 주소 번역 대역폭 60% 감소 ([paper-summaries/2018ASPLOS-summarize/filtering-translation-bandwidth-with-virtual-caching.md])
- **LTRF**: 컴파일 시간 구간 분석을 활용한 하드웨어/소프트웨어 협력 레지스터 프리페칭 — 31% IPC 향상, 46% 전력 소비 감소, 8배 용량 확장 ([paper-summaries/2018ASPLOS-summarize/ltrf-enabling-high-capacity-register-files-for-gpus.md])

### GPU Multi-Tenancy
- **Page Walk Stealing**: Improving GPU multi-tenancy by stealing page walks between contexts ([improving-gpu-multi-tenancy-with-page-walk-stealing.md])
- Memory partitioning and QoS for concurrent GPU workloads
- Spatial and temporal sharing of GPU memory resources

### GPU Reliability
- Characterizing and mitigating soft errors in GPU DRAM ([characterizing-and-mitigating-soft-errors-in-gpu-dram.md])
- ECC coverage analysis for GPU memory
- Radiation-induced errors in HPC GPU deployments

### Neural Processing Units (NPUs) / DNN Accelerators
- **Brainwave (Project Brainwave)**: 클라우드 규모 DNN 추론을 위한 configurable NPU — 단일 스레드 SIMD ISA + HDD로 배치 없이 35 TeraFLOPS 달성, GPU 대비 10배+ 지연 시간 개선 ([paper-summaries/2018ISCA-summarize/a-configurable-cloud-scale-dnn-processor-for-real-time-ai.md])
- **Bit Fusion**: 비트 수준 동적 융합/분해를 지원하는 DNN 가속기 — BitBrick 기반 공간적 융합으로 Eyeriss 대비 3.9× 속도, 5.1× 에너지 절감 ([paper-summaries/2018ISCA-summarize/bit-fusion-bit-level-dynamically-composable-architecture-for-accelerating-deep-neural-network.md])

### GPU for Emerging Workloads
- LLM training and inference on GPUs (see [[paper-wiki/concepts/llm-inference.md|LLM Inference]])
- GPU-accelerated recommendation systems
- GPU NUMA effects for attention optimization ([optimizing-attention-on-gpus-by-exploiting-gpu-architectural-numa-effects.md])

### GPU Virtualization and Security
- **Sugar**: GPU 가상화를 활용한 웹 브라우저 GPU 가속 보안 — 전용 가상 그래픽 폴레인으로 완전한 웹 앱 격리, 이중 GPU 동시 렌더링으로 성능 향상 ([paper-summaries/2018ASPLOS-summarize/sugar-secure-gpu-acceleration-in-web-browsers.md])
- **RCoal**: GPU 타이밍 공격 완화를 위한 서브워프 기반 무작위화된 코얼레싱 기법 — FSS, RSS, RTS 조합으로 24~961배 보안 향상, 5~28% 성능 저하 ([paper-summaries/2018HPCA-summarize/rcoal-mitigating-gpu-timing-attack-via-subwarp-based-randomized-coalescing-techniques.md])

## Related Papers

- [improving-address-translation-in-multi-gpus.md]
- [improving-gpu-multi-tenancy-with-page-walk-stealing.md]
- [characterizing-and-mitigating-soft-errors-in-gpu-dram.md]
- [designing-virtual-memory-system-of-mcm-gpus.md]

- **Neighborhood-Aware Address Translation**: 비정형 GPU 워크로드의 주소 변환 병목 해결 — 캐시 라인 내 PTE 합치기로 페이지 테이블 접근 37% 감소, 1.7배 가속 ([paper-summaries/2018MICRO-summarize/neighborhood-aware-address-translation-for-irregular-gpu-applications.md])

## Cross-references

- [[paper-wiki/concepts/llm-inference.md|LLM Inference]] ??GPU as primary LLM inference engine
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]] ??GPU virtual memory
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]] ??GPU + PIM hybrid systems
- [[paper-wiki/concepts/dram.md|DRAM]] ??GPU DRAM (HBM) reliability
