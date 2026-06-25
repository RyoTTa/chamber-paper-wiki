---
tags: [paper, 2025, 2025MICRO, topic/cache, topic/disaggregation, topic/dram, topic/virtual-memory]
venue: "MICRO 2025 | **Authors:** Kaiyang Zhao, Yuang Chen, Xenia Xu (CMU), Dan Schatzberg (Meta), Nastaran Hajinaza, Rupin Vakharwala, Andy Anderson (Intel), Dimitrios Skarlatos (CMU)"
year: 2025
summary_path: "../paper-summaries/2025MICRO-summarize/learning-to-walk-architecting-learned-virtual-memory-translation.md"
---

# Learning to Walk: Architecting Learned Virtual Memory Translation

**Venue:** MICRO 2025 | **Authors:** Kaiyang Zhao, Yuang Chen, Xenia Xu (CMU), Dan Schatzberg (Meta), Nastaran Hajinaza, Rupin Vakharwala, Andy Anderson (Intel), Dimitrios Skarlatos (CMU)
**저자:** Kaiyang Zhao, Yuang Chen, Xenia Xu (CMU), Dan Schatzberg (Meta), Nastaran Hajinaza, Rupin Vakharwala, Andy Anderson (Intel), Dimitrios Skarlatos (CMU)

## 개요

데이터센터 메모리 용량 증가와 memory-intensive application 확산으로 가상 메모리 주소 변환이 주요 성능 병목이 되고 있음. 현재 표준인 radix page table은 최대 5단계의 sequential memory access를 요구하며, Google과 Meta 연구에서 전체 cycle의 약 **20%가 page walk에 소비**됨이 밝혀짐 [38, 95].

이 문제는 다음 요인으로 악화 중:
- **(i)** TLB scaling의 hardware 한계 — 현대 TLB latency는 L2 cache를 넘어섬 [91]
- **(ii)** CXL 등 terabyte-scale memory capacity 도래 [39, 76]
- **(iii)** memory-intensive application의 증가

기존 접근법은 두 가지로 분류됨:
1. **Contiguity 기반:** huge page, range translation 등으로 translation block을 키우는 방식 [5, 10, 27, 28, 47, 48, 66, 69, 94, 95]. 물리 메모리 contiguity가 부족한 데이터센터 환경에서 한계 [95].
2. **Hashed page table (HPT):** sequential access 대신 parallel access로 hash collision을 해결하는 방식 [77, 79, 80, 93]. Elastic Cuckoo Page Tables (ECPT) [77]가 state-of-the-art이나, 여전히 multiple memory access가 필요하고 memory traffic 증가와 cache pollution을 유발함 (3-way cuckoo는 translation당 3번 probe → 2번은 불필요한 fetch).

데이터베이스 분야의 **learned index** [21, 23, 50, 51, 54]는 key distribution을 학습하여 hash function을 대체하지만, 기존 learned index는 VM translation에 부적합:
- Hierarchical 구조로 인해 radix보다 더 많은 indirection 발생
- 수십 MB 크기, floating-point 연산 의존 → MMU caching/pipeline에 부적합
- 대규모 contiguous memory allocation 요구 (fragmented physical address space와 충돌)
- Static dataset 대상, dynamic update 지원 미흡
- Page size별 별도 index 필요

## 방법론

### 1. Virtual Address Space Regularity 분석 (Section 3.1)

저자들은 learned index 적용 가능성을 검증하기 위해 다양한 application의 virtual address space regularity를 분석. Metric으로 **virtual memory gap coverage**를 정의:

- `gap = 1`: `VPN_next - VPN_current = 1` (sequential page)
- gap=1 coverage: 전체 mapping 중 sequential한 비율

평가 대상: graph analytics (graphBIG), bioinformatics (MUMmer), caching (memcached), HPC (GUPS), DB (MongoDB), web serving (Finagle, hhvm), streaming (Kafka), Meta production workload 4종. C/C++/PHP/Java, jemalloc/tcmalloc allocator 모두 포함.

**결과:** 모든 workload에서 최소 **78%의 gap이 1** (주로 80-95% 범위). Production workload도 benchmark와 유사한 regularity. 이유: userspace allocator가 hole을 최소화하고, 불규칙한 allocation/free pattern을 buffering하며, large object는 contiguous allocation이 필수. Virtual address space가 per-process이므로 physical memory처럼 fragmentation 영향을 받지 않음.

또한 Meta 데이터센터 수만 대 서버 분석 결과 (Figure 3):
- 수백 MB contiguous free memory는 실질적으로 존재하지 않음 [95]와 일치
- 그러나 **수백 KB 단위의 contiguity는 highly fragmented 환경에서도 풍부** (free memory의 30%+)

### 2. LVM Learned Index 구조 (Section 4.2)

LVM은 hashed page table의 fixed hash function을 **learned index로 대체**하여 single-access translation을 목표로 함.

**Index hierarchy:**
- **Internal nodes:** virtual address space를 더 작은 subset으로 분할. Input: VPN → Output: child node의 location.
- **Leaf nodes:** 최종 PTE 위치 예측. Input: VPN → Output: PTE의 physical address.

**Model:** Linear function `y = ax + b` 사용 (slope `a`, intercept `b`). 이유:
- Virtual address space regularity로 linear model로도 충분한 정확도
- 연산: multiplication 1회 + addition 1회 (극히 단순)
- Node당 16 bytes (slope 8B + intercept 8B)

**Gapped Page Tables (GPTs):**
각 leaf node는 자체 page table (GPT) 보유. GPT는 gapped array 구조 [21] — build 시 empty slot (gap)을 미리预留하여 추후 insertion 지원. `ga_scale = 1.3`: 실제 필요한 slot 수의 1.3배로 table 할당.

**Physical contiguity 완화:**
GPT는 leaf node별로 독립적으로 다른 physical address에 할당. OS allocator가 제공하는 가용 contiguity 크기에 따라 leaf node 수를 동적으로 조정 — 최소 4KB (x86 base page) 단위까지 가능. 대규모 contiguous page table 불필요.

**Internal node layout:**
같은 depth의 internal node들은 physical memory에 연속 저장. 각 node는 offset으로 식별 가능 → child node PA를 저장할 필요 없음 → node 크기 최소화.

### 3. Cost Model (Section 4.2.3)

Learned index의 depth, width, collision rate 간 trade-off를 최적화하기 위한 cost model:

```
C(n) = x₁ · d + x₂ · s + x₃ · cr · ma
```

- `d`: index depth (indirection 횟수)
- `s`: index size (bytes)
- `cr`: collision rate
- `ma`: collision당 추가 memory access 수
- `x₁ = 10, x₂ = 5, x₃ = 200` (empirically tuned)

**동작 방식:**
1. Node 내 key들에 대해 RadixSpline [50] 방식으로 spline point 수 계산 → 최적 child node 수 추정 가능
2. 추정치 ±2 범위 내에서 cost 평가 → greedy하게 최적 child 수 선택
3. **Hard constraints:**
   - `d_limit = 3`: 최대 depth 제한 (radix의 indirection 수에 대응; PTE fetch 포함 max 4회)
   - Coverage/byte 제약: 동일 level radix 대비 충분한 coverage 확보 못하면 더 이상 child 생성 불가 → pathological case에서도 index 비대화 방지

## 핵심 기여

1. **핵심 기여:** 기존 learned index의 한계(대규모 크기, FP 의존, static dataset, contiguous allocation 요구)를 모두 극복한 **최초의 practical hardware learned index** 설계. Cost model로 depth/size를 bound하고, rescaling + minimum insertion distance로 dynamic update를 효율화, fixed-point quantization으로 hardware 구현 가능.

2. **성능:** Radix 대비 avg 14% speedup (4KB), ECPT 대비 avg 5% speedup. **Ideal page table (항상 single-access) 성능의 1% 이내** 달성. Memory traffic을 radix 대비 43% 감소시키면서 ECPT 대비 2.9-3.1× 적은 traffic.

3. **Scalability:** Index 크기가 memory footprint와 무관하여 미래 memory capacity 증가에도 대응 가능. PWC가 선형 확장되어야 하는 radix와 근본적 차이.

4. **Broader significance:** LVM framework는 TLBs, BTBs, L1 cache 등 다른 VA-indexed hardware structure에도 적용 가능. Physically-indexed structure (LLC 등)의 conflict miss 감소에도 응용 가능성.

## 주요 결과

**Internal node training:**
- Cost model이 child 수 결정 → child nodes용 memory 할당
- VPN과 child index 간 linear function 학습 (perfect linear relationship이므로 lightweight)

**Leaf node training:**
- OS allocator에 가용 physical contiguity query → contiguity에 맞춰 sibling leaf node 수 결정
- Linear regression으로 (VPN, position) pairs 학습
- `ga_scale` (1.3)로 scale하여 gapped array에 분산 → 미래 insertion 공간 확보
- Predicted position이 occupied이면 exponential search로 다음 available slot에 insert

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2025MICRO-summarize/learning-to-walk-architecting-learned-virtual-memory-translation.md|전체 요약 보기]]
