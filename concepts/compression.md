---
tags: [concept, compression, data-reduction, encoding]
source_count: 13
last_updated: 2026-06-25
---

# Compression

## Summary

Memory and storage compression research focuses on reducing data footprint to increase effective capacity and bandwidth. Techniques range from cache-line-level deduplication to hardware-software co-designed compression for disaggregated memory.

## Key Ideas

### Memory Compression
- **BCD Deduplication**: Effective memory compression using partial cache-line deduplication ([bcd-deduplication-effective-memory-compression-using-partial-cache-line-deduplication.md])
- **DyLeCT**: Achievement of huge-page-like translation performance for hardware-compressed memory ([dylect-achieving-huge-page-like-translation-performance-for-hardware-compressed-memory.md])
- **Translation-Optimized Memory Compression**: Compression-aware address translation for capacity ([translation-optimized-memory-compression-for-capacity.md])
- **WLCRC**: Word-Level Compression + Restricted Coset Encoding으로 MLC PCM의 세밀한 인코딩 세밀화 — 16비트 세밀화에서 기존 기법 대비 39% 쓰기 에너지 절감 ([paper-summaries/2018HPCA-summarize/enabling-fine-grain-restricted-coset-coding-through-word-level-compression-for-pcm.md])
- **LATTE-CC**: GPU의 동적 레이턴시 내성 특성을 활용한 적응형 캐시 압축 관리 기법 — 세 가지 압축 모드를 동적으로 선택하여 캐시 민감 GPGPU 애플리케이션의 성능을 최대 48.4% 향상, 에너지 소비를 평균 10% 절감 ([paper-summaries/2018HPCA-summarize/latte-cc-latency-tolerance-aware-adaptive-cache-compression-management-for-energy-efficient-gpus.md])

### Storage Data Reduction
- **FIDR**: Scalable storage for fine-grain inline data reduction ([fidr-scalable-storage-for-fine-grain-inline-data-reduction.md])
- **CIDR**: Cost-effective in-line data reduction for SSD arrays ([cidr-a-cost-effective-in-line-data-reduction-system-for-terabit-per-second-scale-ssd-arrays.md])
- **SMASH**: Co-designing software compression and HW indexing ([smash-co-designing-software-compression-and-hw-indexing.md])
- **Dynamic Multi-Resolution Data Storage** ([dynamic-multi-resolution-data-storage.md])

### Compression for CXL
- **TRACE**: Unlocking effective CXL bandwidth via lossless compression ([trace-unlocking-effective-cxl-bandwidth-via-lossless-compression.md])
- Compression as a way to overcome bandwidth limitations in disaggregated memory

### OS-Transparent Main Memory Compression
- **Compresso**: 데이터 이동 최적화를 통한 실용적 메인 메모리 압축 — OS 수정 없이 1.85× 압축률, LCP 대비 24-27% 성능 향상, 추가 메모리 접근 63%→15% 감소 ([paper-summaries/2018MICRO-summarize/compresso-pragmatic-main-memory-compression.md])

### Metadata Bandwidth Mitigation
- **Attaché**: BLEM과 COPR를 통해 데이터 압축 시 Metadata 접근 대역폭 오버헤드를 거의 완전히 제거 — Sub-Ranking 기반 시스템에서 이상적 압축 대비 89.6% 속도 향상 달성 ([paper-summaries/2018MICRO-summarize/attache-towards-ideal-memory-compression-by-mitigating-metadata-bandwidth-overheads.md])

### KV Cache Compression
- INT8 quantization of KV tensors for LLM inference (see [[paper-wiki/concepts/llm-inference.md|LLM Inference]])
- Sparse attention as a form of selective compression

### DNN Training Memory Compression
- **Gist**: 레이어별 손실/손실 없는 인코딩으로 DNN 학습 메모리 최대 4.1× 절감 — Binarize(1비트 인코딩, 32× 압축), SSDC(희소성 활용), DPR(정밀도 축소)로 feature maps 압축, 4% 오버헤드 미만 ([paper-summaries/2018ISCA-summarize/gist-efficient-data-encoding-for-deep-neural-network-training.md])

## Related Papers

- [bcd-deduplication-effective-memory-compression-using-partial-cache-line-deduplication.md]
- [trace-unlocking-effective-cxl-bandwidth-via-lossless-compression.md]
- [fidr-scalable-storage-for-fine-grain-inline-data-reduction.md]
- [attache-towards-ideal-memory-compression-by-mitigating-metadata-bandwidth-overheads.md]
- [compresso-pragmatic-main-memory-compression.md]

- **PERM DNN**: 순열 대각 행렬 기반 DNN 압축 — EIE 대비 3.3~4.8배 처리량, CIRCNN 대비 11.51배 처리량 향상 ([paper-summaries/2018MICRO-summarize/permdnn-efficient-compressed-dnn-architecture-with-permuted-diagonal-matrices.md])
- **Gist**: DNN 학습 feature maps 레이어별 인코딩 — 최대 4.1× 메모리 절감, 4% 오버헤드 ([paper-summaries/2018ISCA-summarize/gist-efficient-data-encoding-for-deep-neural-network-training.md])

## Cross-references

- [[paper-wiki/concepts/llm-inference.md|LLM Inference]] ??KV cache compression
- [[paper-wiki/concepts/storage.md|Storage]] ??Storage data reduction
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]] ??Compression for CXL
- [[paper-wiki/concepts/cache.md|Cache]] ??Compressed caches
