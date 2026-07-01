---
tags: [concept, cache, prefetching, replacement, llc]
source_count: 18
last_updated: 2026-07-02
---

# Cache

## Summary

Cache research covers caching policy, prefetching, replacement algorithms, and novel cache architectures. Recent work focuses on adapting traditional caching techniques to emerging workloads (LLM, recommendation systems) and memory technologies (NVM, disaggregated memory).

## Key Ideas

### Prefetching
- **Page-Size-Aware Cache Prefetching**: Adapting prefetch granularity to page size ([page-size-aware-cache-prefetching.md])
- **Agile TLB Prefetching**: Exploiting page table locality for faster address translation ([exploiting-page-table-locality-for-agile-tlb-prefetching.md])
- TLB prefetching overlaps with cache prefetching in modern prefetcher designs
- **IP-CaT**: L1I 프리페칭의 주소 변환 지연과 L2 캐시 내 코드 라인의 가변적 재사용 행동을 동시 해결 — tPB(64 엔트리)로 sTLB MPKI 31.6% 감소, TIPRP로 L2 캐시 교체 정책 최적화, 0.79KB 저장 오버헤드로 EPI+IP-CaT 6.1% geomean 스피드업 ([paper-summaries/2026ARXIV-summarize/enhancing-instruction-prefetching-via-cache-and-tlb-management.md])

### Criticality-Aware Cache Design
- **CATCH (Criticality Aware Tiered Cache Hierarchy)**: 하드웨어 기반 criticality 감지 + TACT 프리패처로 critical load를 L1 지연 시간으로 서비스 — L2 완전 제거 시 4.5% IPC 향상 + 30% 면적 절감, 기본 8.4~10.3% IPC 향상 ([paper-summaries/2018ISCA-summarize/criticality-aware-tiered-cache-hierarchy-a-fundamental-relook-at-multi-level-cache-hierarchies.md])

### Replacement Policy
- Research focuses on ML-based and adaptive replacement policies
- Coordination between cache levels (L1, L2, LLC) for global optimization
- DRAM cache replacement policies for data center workloads

### LLM KV Cache
- KV caching is a specialized form of caching unique to Transformer inference
- Sparse attention and token-level caching blur the line between algorithm and caching policy
- See [[paper-wiki/concepts/llm-inference.md|LLM Inference]] for detailed KV cache research

### Cache for New Memory Technologies
- **Native DRAM Cache**: Re-architecting DRAM as a large-scale cache for data centers ([native-dram-cache-re-architecting-dram-as-a-large-scale-cache-for-data-centers.md])
- NVM-aware cache policies for hybrid memory systems
- **REDUCT**: Near-cache compute for DNN inference on multi-core CPUs ([reduct-near-cache-compute-for-dnn-inference-on-multi-core-cpus.md])
- **AMS**: 비대칭 메모리 계층에서 미스 곡선 기반 LLC 파티셔닝을 통한 스케줄링 최적화 — NDP/프로세서 다이 간 최적 스레드 배치 ([adaptive-scheduling-for-systems-with-asymmetric-memory-hierarchies.md])
- **SILO**: 다이 스택 DRAM 기반 프라이빗 LLC로 서버 프로세서의 공유 LLC 한계 극복 — 각 코어 위에 직접 스택된 DRAM 볼트로 11.5ns 접근 지연 시간 달성, 5-54% 성능 향상 ([farewell-my-shared-llc-a-case-for-private-die-stacked-dram-caches-for-servers.md])

### VIPT Cache Optimization
- **SEESAW**: Superpage의 넓은 page offset을 활용하여 VIPT L1 캐시의 associativity 제약 극복 — 2MB superpage에서 way 수 동적 감소로 latency/energy 절감, coherence lookup 에너지 대폭 절감 ([paper-summaries/2018ISCA-summarize/seesaw-using-superpages-to-improve-vipt-caches.md])

### Cache Security
- **CEASER**: LLC에서 암호화된 주소 공간과 동적 리매핑으로 conflict-based 캐시 공격 완화 — 1% 오버헤드로 100년 이상 보안 강건성 ([paper-summaries/2018MICRO-summarize/ceaser-mitigating-conflict-based-cache-attacks-via-encrypted-address-and-remapping.md])

### Cache Compression
- **LATTE-CC**: GPU의 동적 레이턴시 내성 특성을 활용한 적응형 캐시 압축 관리 기법 — 세 가지 압축 모드(비압축, 저레이턴시, 고용량)를 동적으로 선택하여 캐시 민감 GPGPU 애플리케이션의 성능을 최대 48.4% 향상, 에너지 소비를 평균 10% 절감 ([paper-summaries/2018HPCA-summarize/latte-cc-latency-tolerance-aware-adaptive-cache-compression-management-for-energy-efficient-gpus.md])
- **Attaché**: 메모리 압축 시 메타데이터 대역폭 오버헤드 제거 기법 (MICRO '18)
- **Compresso**: OS-투명 메인 메모리 압축 기법 (MICRO '18)
- **Touché**: 태그 영역 오버헤드 없이 임의 주소 압축 블록 배치 — 축약된 시그니처(9비트)로 여러 태그를 하나의 태그 엔트리에 저장, TADA 메커니즘으로 전체 태그를 데이터 배열에 저장, 평균 12% 가속 (이상적 13%), 최대 91% 가속(gcc) ([paper-summaries/2019MICRO-summarize/touch-towards-ideal-and-efficient-cache-compression-by-mitigating-tag-area-overheads.md])

### Near-Cache Computing
- Processing near the cache hierarchy to reduce data movement
- Cache as a compute substrate for simple operations
- In-cache operators for sequence alignment (GenCache: [gencache-leveraging-in-cache-operators-for-sequence-alignment.md])
- **Neural Cache**: LLC 캐시를 대규모 병렬 연산 유닛으로 재활용하여 DNN 추론 가속 — 비트 직렬 연산으로 CPU 대비 18.3×, GPU 대비 7.7× 지연 시간 향상, 전력 50% 절감 ([paper-summaries/2018ISCA-summarize/neural-cache-bit-serial-in-cache-acceleration-of-deep-neural-networks.md])

## Related Papers

- [page-size-aware-cache-prefetching.md]
- [native-dram-cache-re-architecting-dram-as-a-large-scale-cache-for-data-centers.md]
- [gencache-leveraging-in-cache-operators-for-sequence-alignment.md]
- [reduct-near-cache-compute-for-dnn-inference-on-multi-core-cpus.md]
- [ceaser-mitigating-conflict-based-cache-attacks-via-encrypted-address-and-remapping.md]
- [farewell-my-shared-llc-a-case-for-private-die-stacked-dram-caches-for-servers.md]

## Cross-references

- [[paper-wiki/concepts/llm-inference.md|LLM Inference]] ??KV cache as a dominant cache use case
- [[paper-wiki/concepts/dram.md|DRAM]] ??DRAM as a cache tier
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]] ??Near-cache computing
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]] ??Multi-tier caching
