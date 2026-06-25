---
tags: [paper, 2025, 2025ASPLOS, topic/cache, topic/dram, topic/gpu, topic/llm-inference, topic/storage, topic/virtual-memory]
venue: ""
year: 2025
summary_path: "../paper-summaries/2025ASPLOS-summarize/vattention-dynamic-memory-management-for-serving-llms-without-pagedattention.md"
---

# vAttention: Dynamic Memory Management for Serving LLMs without PagedAttention

**Venue:** 
**저자:** 

## 개요

### 1.1 LLM Serving과 KV Cache

LLM inference에서 batching은 throughput 향상의 핵심 기법이다. 각 request의 attention 연산을 위해 모든 이전 token의 key/value activation을 GPU 메모리에 저장해야 하는데, 이를 **KV cache**라 하며 GPU 메모리 사용량의 대부분을 차지한다. KV cache 메모리 할당이 어려운 이유는 (1) request당 KV cache가 iteration마다 1 token씩 증가하고, (2) 총 decode length를 사전에 알 수 없다는 점이다.

### 1.2 PagedAttention의 한계

vLLM이 제안한 **PagedAttention**은 OS demand paging에서 착안하여 KV cache를 고정 크기 block 단위로 on-demand 할당함으로써 internal fragmentation을 해결한다. 그러나 **물리 메모리를 동적으로 할당하기 위해 virtual memory 상에서도 KV cache를 non-contiguous하게 만드는 근본적 trade-off**를 갖는다.

**PagedAttention의 세 가지 문제점 (§3):**

| 문제 | 구체적 근거 |
|------|------------|
| **Kernel 재작성 필요** | Non-contiguous KV cache를 처리하기 위해 모든 attention kernel을 수정해야 함. vLLM의 paged kernel은 FlashAttention-2 대비 최대 2.8× 느림 (Table 7). Block size에 따라 kernel latency가 최대 1.9× 변동 (Figure 3). |
| **Serving framework 내 중복 구현** | Block-Table 관리 → OS의 virtual-to-physical address translation을 user space에서 중복 구현. Block-Table 준비 latency가 decode iteration의 최대 30% (개선 후에도 10%). |
| **Runtime overhead** | FlashAttention-2 paged prefill kernel: non-paged 대비 최대 **37%** 느림. FlashInfer paged prefill: 최대 **42%** 느림 (Figure 2). 원인: Block-Table lookup, 추가 분기문 → instruction 7-13% 증가, register spilling. TensorRT-LLM에서 Python frontend 사용 시 throughput 11% 저하 [5]. |

**근본 원인:** `cudaMalloc`은 virtual + physical memory를 동시에 할당 (reservation-based). OS demand paging과 달리 GPU에서는 virtual memory만 미리 확보하고 physical memory를 지연 할당하는 메커니즘이 기존에 LLM serving에 활용되지 않았음.

## 방법론

### 2.1 핵심 아이디어

> **KV cache의 virtual memory contiguity를 유지하면서 physical memory fragmentation을 방지한다.**

이를 위해 CUDA Virtual Memory Management (VMM) API를 활용하여 virtual memory 할당과 physical memory 할당을 **분리(decouple)** 한다.

### 2.2 Virtual Memory Pre-allocation (§5.1)

- **Buffer 크기:** `B × S` (B: 최대 batch size, S: request당 per-layer K/V cache 최대 크기)
- `S = L × H × D × P` (L: 최대 context length, H: KV head 수, D: head dimension, P: precision bytes)
- 예: Yi-34B, TP-2 기준 — B=500, L=200K, H=4, D=128, P=2 → `S = 200MB`, `B×S = 100GB` per layer
- 총 2×N개 buffer (N layers × {K, V}) → 60 layers × 2 × 100GB = 12TB virtual memory. 64-bit 시스템의 128TB user-addressable 공간 내에서 충분.

### 2.3 Request-level Indexing (§5.2.3)

Virtual tensor 내에서 각 request는 `reqId` (0 ~ B-1)로 식별되는 non-overlapping sub-region을 점유. K cache offset = `reqId × S`. Continuous batching 시 request hole이 생기면 FlashAttention의 `cache_batch_idx` 인자로 Q와 KV cache의 batch index를 remapping.

### 2.4 API 설계 (Table 4, Algorithm 1)

| API | 설명 |
|-----|------|
| `init(N, B, L, H, D, P, page-group-size)` | Virtual tensor pre-allocation |
| `alloc_reqid()` | 새 request에 reqId 할당 |
| `free_reqid(reqId)` | Request 종료 시 reqId 반환 |
| `step(seq_lengths[])` | 각 request의 현재 context length까지 physical page mapping 보장 |

**Serving loop:** `alloc_reqid` → `step(cache_seq_len)` → `model.forward()` → 완료된 request는 `free_reqid`

### 2.5 Continuous Batching 지원

FlashAttention의 `cache_batch_idx` API를 활용. Request composition 변경 시 running request의 Q tensor가 `reqId` 기반으로 올바른 KV cache sub-tensor를 참조하도록 매핑 업데이트.

## 3. 최적화 (§6)

### 3.1 Latency Hiding: Overlapping Allocation with Compute (§6.1.1)

**도전 과제:** CUDA VMM API `cuMemMap` + `cuMemSetAccess` 호출은 page-group당 약 40µs. Yi-34B (60 layers, 120 calls)에서 request당 약 **5ms** latency 추가.

**해결책 (decode phase):**
- Decode phase에서 iteration i-1의 `step` 호출 시 background thread로 iteration i에 필요한 physical page-group을 미리 mapping
- Per-iteration latency (10-100ms)가 API latency를 충분히 흡수 → critical path에서 제거

**결과:** Overlapping 적용 시 latency spike (5-15ms)가 사라짐 (Figure 12).

### 3.2 Deferred Reclamation + Eager Allocation (§6.1.2)

**Deferred reclamation:** Request R1 종료 후 physical page-group을 즉시 회수하지 않고, 새 request R2에 R1의 reqId를 재할당 → R1의 이미 mapping된 physical memory를 그대로 사용. R2의 context length > R1인 경우에만 추가 할당.

**Eager allocation:** Background thread가 inactive reqId 하나에 미리 page-group을 mapping → 새 request 도착 시 즉시 사용 가능.

**결과:** Prefill phase에서 CUDA VMM API 호출을 거의 완전히 제거 (Figure 13). Synchronous allocation 대비 prefill overhead 1.15× → 1.00×.

### 3.3 Mitigating Internal Fragmentation: 64KB Pages (§6.2)

**도전 과제:** CUDA VMM API는 기본적으로 2MB page 단위로만 할당 가능 → KV cache block size가 너무 커져 internal fragmentation 발생.

**해결책:** Open-source NVIDIA unified memory driver를 수정하여 **64KB, 128KB, 256KB** page-group 지원 추가 (Table 3). 새로운 `vMemMap`, `vMemRelease` 등의 API 구현.

**Page size별 block size (Table 8):**

| Page-Group | Yi-6B (TP-1) | Llama-3-8B (TP-2) | Yi-34B (TP-2) |
|------------|-------------|-------------------|---------------|
| 64KB | 64 tokens | 64 tokens | 32 tokens |
| 2MB | 2048 tokens | 2048 tokens | 1024 tokens |

**TLB thrashing 없음:** 64KB page 사용 시에도 attention kernel latency에 부정적 영향 없음 (Figure 14). Llama-3-70B, GPT-3-175B 규모에서도 동일.

**Batch size 향상 (Figure 15):** 64KB pages → Yi-6B 최대 batch 240 (2MB: 187), Llama-3-8B 최대 258 (2MB: 203), Yi-34B 최대 68 (2MB: 56).

### 3.4 Tensor Slicing (대안, §8.2)

Driver 수정 없이도 2MB page의 fragmentation을 줄이는 방법: K/V cache를 `[B, L, N, H, D]` 형태의 단일 virtual tensor로 할당하고 layer 간 slicing → fragmentation 1/N로 감소. 단, attention kernel이 strided memory access를 지원해야 함 (FlashAttention-2는 지원, 초기 FlashInfer는 미지원).

## 핵심 기여

vAttention은 LLM serving에서 KV cache의 **virtual contiguity를 유지하면서 physical memory를 동적으로 할당**하는 새로운 패러다임을 제시한다.

**핵심 기여:**
1. **PagedAttention의 근본적 한계 극복:** Virtual memory contiguity를 포기하지 않고도 fragmentation 해결. 이는 kernel 재작성 부담, Block-Table 관리 overhead, portability 저하라는 PagedAttention의 3대 문제를 동시에 해소.
2. **CUDA VMM API의 실용적 적용:** Overlapping allocation, deferred reclamation, eager allocation, 64KB page 지원 등 LLM-specific 최적화로 API latency를 critical path에서 제거.
3. **성능:** Prefill 최대 1.36×, End-to-end 최대 1.23× throughput 향상. 특히 prefill-bound workload에서 두드러짐.
4. **Portability:** FA3, SDPA (cuDNN-9) 등 최신 kernel을 코드 변경 없이 즉시 지원 → serving framework가 kernel innovation에 신속히 대응 가능.

**Broader significance:** vAttention은 "demand paging을 OS가 아닌 user space에서 구현"하는 PagedAttention 접근법의 근본적 결함을 지적하고, GPU virtual memory abstraction을 올바르게 활용하는 principled approach를 제시한다. 본 논문의 NVIDIA driver 확장은 향후 CUDA가 공식적으로 finer-grained page 지원을 채택할 경우 표준화될 수 있는 방향성을 제시하며, LLM serving 시스템의 memory management 설계에 장기적 영향을 미칠 것으로 기대된다.

## 주요 결과

### 4.1 Methodology

| 항목 | 내용 |
|------|------|
| Hardware | 1× A100 (Yi-6B), 2× A100 w/ NVLink (Llama-3-8B, Yi-34B), 1-2× H100 (FA3) |
| Models | Yi-6B (32 layers, 4 KV heads), Llama-3-8B (32 layers, 8 KV heads), Yi-34B (60 layers, 8 KV heads) |
| Serving Framework | vLLM v0.2.7 기반 통합 |
| Attention Backends | FlashAttention-2 v2.5.9, FlashInfer v0.4.0, FlashAttention-3 |
| Baselines | FA2_Paged, FI_Paged, vLLM decode kernel |
| Page-group size | vAttention: 64KB (default); PagedAttention: 16 (vLLM/FlashInfer), 256 (FlashAttention-2) |
| Workloads | arXiv-Summarization dataset: context 22K-192K tokens, decode 6-5153 tokens |

### 4.2 Prefill 성능 (Figure 7, Table 6)

- **Short context (1K-8K):** Attention 비중이 낮아 FA2_vAttention ≈ FA2_Paged. FI_vAttention은 FlashInfer의 Block-Table 관리 overhead 제거로 small context에서도 throughput 향상.
- **Long context (192K):** FA2_vAttention이 FA2_Paged 대비 **1.24×** (Yi-6B), **1.26×** (Llama-3-8B), **1.24×** (Yi-34B) throughput. FlashInfer 대비 최대 **1.36×** (Llama-3-8B, 16K).
- **Attention time 감소:** 192K context Yi-6B에서 vAttention으로 attention kernel만 7.0s→5.5s (1.27× faster). Gains의 거의 전부가 더 빠른 attention kernel에서 기인.

### 4.3 Decode 성능 (Figure 8, Table 7)

- **FA2_vAttention ≈ FA2_Paged** (decode kernel은 memory-bound → paging overhead가 memory stall에 은폐됨)
- **vLLM 대비:** FA2_vAttention이 vLLM decode kernel 대비 최대 **1.99×** (Yi-6B, BS=32), **1.58×** (Llama-3-8B), **1.53×** (Yi-34B)
- vLLM kernel latency는 FlashAttention-2 대비 최대 2.8× (Yi-6B). Batch size 증가에 따라 상대적 gains도 증가 (BS 4→32: 1.05×→1.58×).

### 4.4 End-to-End 성능

**Offline (Figure 9):**
| Model | FA2_vAttention vs FA2_Paged | FA2_vAttention vs FI_Paged |
|-------|---------------------------|--------------------------|
| Yi-6B | **1.18×** | **1.19×** |
| Llama-3-8B | **1.15×** | **1.23×** |
| Yi-34B | **1.13×** | **1.14×** |

Gains는 P:D ratio와 context length에 비례 (prefill-bound workload에서 더 큰 이득).

**Online (Figure 10):** FA2_vAttention이 median request latency를 FA2_Paged 대비 Yi-6B 최대 42% (QPS 0.25), Llama-3-8B 28% (QPS 0.3), Yi-34B 29% (QPS 0.1) 감소. Faster prefill이 queuing delay를 줄이기 때문.

### 4.5 Portability: FlashAttention-3 (Figure 11)

FA3 (H100 Hopper 최적화)는 출시 당시 PagedAttention 미지원. vAttention은 **코드 변경 없이** FA3를 즉시 지원. FA3_vAttention이 FA2_vAttention 대비 추가 **1.26-1.50×** throughput 달성.

### 4.6 Ablation Studies (§7.6)

- **Latency hiding:** Overlapping 미적용 시 5-15ms latency spike 발생, 적용 시 완전히 은폐 (Figure 12).
- **Deferred reclamation:** Synchronous allocation 대비 prefill overhead 제거 (64KB: 1.15×→1.00×, Figure 13).
- **Page size 영향:** 64KB vs 2MB page 간 attention kernel latency 차이 없음 (Figure 14).
- **Memory allocation bandwidth:** 64KB page에서도 7.6GB/s (TP-1), 최대 70.3GB/s (TP-2, 2MB) — LLM inference의 최대 요구량 750MB/s 대비 10배 이상 여유 (Table 9).

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/storage.md|Storage]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2025ASPLOS-summarize/vattention-dynamic-memory-management-for-serving-llms-without-pagedattention.md|전체 요약 보기]]
