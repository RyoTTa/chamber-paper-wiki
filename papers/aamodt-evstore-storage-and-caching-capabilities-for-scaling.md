---
tags: [paper, 2023, 2023ASPLOS, topic/cache, topic/dram, topic/gpu, topic/llm-inference, topic/storage]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023ASPLOS-summarize/evstore-storage-and-caching-capabilities-for-scaling-embedding-tables-in-deep-recommendation-systems.md"
---

# EVStore: Storage and Caching Capabilities for Scaling Embedding Tables in Deep Recommendation Systems

**Venue:** 
**저자:** 

## 개요

Deep Recommendation System (DRS)은 modern online service의 핵심. Amazon 트래픽 30%, YouTube 60%, Netflix 75%가 recommendation algorithm에 의해 생성됨. DRS는 categorical(sparse) input feature 처리를 위해 **embedding vector (EV) table** 사용 — sparse feature를 dense vector로 변환하여 DNN input으로 제공.

**핵심 문제: EV table 크기의 폭증.**
- Real-world EV table은 수십억 개의 embedding vector 포함 → 수십 TB 메모리 요구 (e.g., 10억 rows × 400 dimensions × fp32 = 1.5 TB).
- EV table 크기는 2년마다 3배 증가 (연간 1.5×, Moore's Law 추세; Jouppi+ ISCA'21, Ardestani+ 2021).
- Facebook data center의 AI-related deployment 80%가 DRS를 직접 지원 (Gupta+ HPCA'20).
- Cloud high-memory instance 상한: AWS 24 TiB, Azure/GCP 12 TiB — 곧 한계 도달.
- Open-source DRS (DLRM, DCN)는 전체 EV table을 DRAM에 저장하며, memory 부족 시 backend storage fallback 기능 부재.

**기존 접근의 한계:**
- EV table을 backend storage (SSD/HDD)로 이동하는 연구 존재 (Bandana, FlashEmbedding, RecSSD). 그러나 custom device (custom SSD, FPGA) 필요 → commodity hardware 배포에 한계.
- GPU-resident cache, DRAM cache 최적화 연구는 training-focused이며 inference caching policy 무시.
- 전통적 cache replacement algorithm (LRU, LFU, ARC, CAR, Cacheus, ClockPro)은 DRS의 **all-or-nothing access pattern**을 고려하지 않음.

**All-or-nothing property:** DRS inference는 `lookup(A₁, B₄, C₆, ..., Z₉)` 형태로 최대 26개 EV table을 동시 조회. 단 하나의 key라도 cache miss → 전체 inference 지연 (backend storage access 필요). Figure 4에서 Criteo dataset 기준 cache size 0.5~20%일 때 individual hit rate 60~90%이나 perfect hit rate는 1~50%에 불과.

## 방법론

EVStore는 DRS pipeline 내에 3-layer EV caching system을 내장 (Figure 3).

```
lookup(A₁, B₄, C₆, ..., Z₉)
    ↓
┌──────────┐
│ L1 EVCache │ ← fp32, groupability 기반 replacement
├──────────┤
│ L2 EVMix   │ ← 저정밀도 (fp16/fp8/fp4) multi-tier
├──────────┤
│ L3 EVProx  │ ← surrogate key approximation
└──────────┘
    ↓ (miss 시)
Backend Storage (SSD/HDD)
```

## 핵심 기여

1. **3-layer EV caching architecture 제안**: EVCache(groupability), EVMix(mixed-precision multi-tier), EVProx(surrogate approximation)의 계층적 설계.
2. **Groupability 개념**: multi-key lookup의 all-or-nothing property를 cache replacement policy에 통합 — perfect hit rate metric + groupScore 기반 eviction.
3. **Mixed-precision으로 latency-accuracy Pareto frontier 확장**: L1/L2 precision 조합을 통한 configurable tradeoff.
4. **Practical system**: Commodity hardware + open-source DLRM integration. 94% memory reduction → 수억 달러 operational cost 절감 가능.
5. **Future work**: Better EV caching policy, L1-L2-L3 size arrangement optimization, GPU-accelerated caching, emerging memory technology integration.

## 주요 결과

**4.1 Perfect hit 문제 정의:**
- 기존 metric: individual hit rate = 요청된 key-value pair 중 cache에서 발견된 비율.
- EVStore metric: **perfect hit rate** = 한 inference의 *모든* N개 key가 cache에 존재하는 비율. Disk access zero → 최적 성능.

**4.2 Groupability 개념과 groupScore:**
DRS는 cardinality가 고정된 group access. EVCache는 각 cache key에 `groupScore` metadata를 부여하여 group membership 반영.

4개 fundamental operation:
1. **Cache lookup:** Grouped-key lookup (e.g., 26 keys) → 총 hit 수 k를 memorize. (e.g., 26개 중 20개 hit → score = 20)
2. **Cache state update:** Hit key의 groupScore ← max(currentScore, memorizedScore). e.g., key B₄의 기존 score 15 → 20으로 갱신.
3. **Cache insertion:** Miss key → backend에서 fetch 후 groupScore = memorizedScore로 삽입.
4. **Cache eviction:** 가장 낮은 groupScore 기준 eviction. `unordered_set` per score level → O(1) eviction.

**Scoring method 선택 근거:**
- Max-based: computation cheap, perfect-hit rate 기준 최고 성능.
- Average/sum/median: metadata size + computation cost 증가, perfect hit rate 열등.
- Incremental update (static +x): optimal x 결정 어려움, dynamic workload 대응 불가. 일부 시도에서 perfect hit rate 50% 감소, 30× 느림.

**4.3 세 가지 EVCache variant:**

| Variant | Base Algorithm | Group Score 통합 방식 | 특징 |
|---------|---------------|---------------------|------|
| **EV-LFU** | LFU | Frequency counter → groupScore 대체 | Stack algorithm (Belady anomaly free). Max score 도달 key가 maxScoreKeyCapacity(20%) 초과 시 X% flushing. Simple: 130 LOC (simulator). |
| **EV-ARC** | ARC | Group score metadata 추가, F-list에 EV-LFU counting/eviction 적용, R-ghost/F-ghost로 probationary/protected 동적 조절 | Recency + frequency adaptive. Individual hit rate 유지하며 perfect hit 개선. |
| **EV-CAR** | CAR (ARC+CLOCK) | Reference bit R에 group score 저장 (0/1 대신). Progressive decrement: O(n) rotation 내 eviction 보장. Max-based scoring on hit. | CLOCK hand 방식. Second-chance with score comparison. |

**EV-CAR progressive decrement:** CLOCK hand 회전 시 R값을 감소시켜 단일 rotation 내에 반드시 피해자 발견 (무한 대기 방지). Incoming key의 group score가 더 크면 eviction 거부 → second chance 부여.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2023ASPLOS-summarize/evstore-storage-and-caching-capabilities-for-scaling-embedding-tables-in-deep-recommendation-systems.md|전체 요약 보기]]
