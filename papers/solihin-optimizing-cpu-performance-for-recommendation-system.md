---
tags: [paper, 2023, 2023ISCA, topic/cache, topic/dram, topic/pim, topic/storage]
venue: "ACM/IEEE 50th Annual International Symposium on Computer Architecture (ISCA) 2023"
year: 2023
summary_path: "../paper-summaries/2023ISCA-summarize/optimizing-cpu-performance-for-recommendation-systems-at-scale.md"
---

# Optimizing CPU Performance for Recommendation Systems At-Scale

**Venue:** ACM/IEEE 50th Annual International Symposium on Computer Architecture (ISCA) 2023
**저자:** Rishabh Jain, Scott Cheng, Vishwas Kalagi, Vrushabh Sanghavi, Samvit Kaul, Meena Arunachalam, Kiwan Maeng, Adwait Jog, Anand Sivasubramaniam, Mahmut T. Kandemir, Chita R. Das (Penn State University)

## 개요

- Deep Learning Recommendation Model (DLRM)은 전자상거래, 엔터테인먼트, 소셜 네트워크 등에서 개인화된 추천을 위해 광범위하게 사용되며, 데이터센터 AI 사이클의 주요 기여자
- DLRM의 **embedding lookup 단계**가 전체 실행 시간의 상당 부분 (모델에 따라 60%~90%)을 차지하며, 이 단계의 비정규화된 (irregular) 메모리 접근이 CPU 파이프라인의 주요 병목
- 최신 추천 모델은 파라미터 크기가 지속적으로 증가하여 embedding 테이블의 크기도 커지고, 접근 패턴의 비정규화 정도도 심화 → CPU의 on-chip cache가 working set을 수용하기에 부적합
- 기존 연구들은 하드웨어 변경 (PIM, SSD 기반 가속 등)에 의존하거나, 소규모 모델/데이터셋에서만 평가하여 최신 대규모 모델의 특성을 충분히 반영하지 못함
- embedding 단계의 **_REUSE DISTANCE_**: Low Hot 데이터셋의 경우 768MB 캐시도 cold miss를 완전히 제거하지 못하며, cold miss 비율이 최대 **72%**에 달함

## 방법론

### 3.1. Embedding Lookup의 메모리 접근 패턴

- DLRM은 4단계로 구성: Bottom MLP → Embedding Lookup → Feature Interaction → Top MLP
- embedding lookup은 **3단계 간접 참조 (three-level indirection)**를 통해 수행:
  - offset array → index array → embedding table row vector
- 각 샘플이 여러 테이블에 대해 여러 lookup을 수행하며, 각 lookup은 embedding_dim 크기의 row vector를 로드
- **Algorithm 1** (단순화된 메모리 접근 루프): batch → table → sample → lookup 순서로 중첩, SIMD/AVX 벡터 연산으로 load-add-store 수행
- embedding_dim은 일반적으로 4~8개 캐시 라인 (4~8KB)으로 spatial locality가 낮음

### 3.2. Reuse Distance와 캐시 효과 분석

- **네 가지 reuse 범주**:
  1. **Intra-table**: 동일 테이블 내 lookup 간 인덱스 공유 → 캐시 활용 가능하나 reuse distance가 캐시 용량을 초과하면 무용
  2. **Inter-table**: 서로 다른 테이블은 독립적 메모리 footprint → 이전 테이블 데이터를 캐시에서 evict시킴
  3. **Inter-batch**: 동일 테이블의 다른 batch에서 같은 인덱스 접근 가능 → 그러나 중간 접근으로reuse distance가 매우 큼
  4. **Inter-core**: 다중 코어 실행 시 LLC/DRAM 대역폭 공유 → constructive sharing (동일 테이블) 또는 destructive sharing (다른 테이블)
- **Figure 7**의 reuse distance 분석: L1D$ hit rates가 매우 낮으며, 특히 Medium/Low Hot 데이터셋에서 cold miss 비율이 높음
- VTune 분석: RM2_1 모델 기준 baseline L1D$ hit rate 72%~84%, 평균 load latency 23~90 cycles

### 3.3. 하드웨어 프리페처와 컴파일러 프리페처의 한계

- Intel CPU의 4개 하드웨어 프리페처 (L1D$/L2$ 전용)는 간접 접근 패턴 감지에 비효율 → 프리페처 ON/OFF가 성능에 미미한 영향
- 컴파일러 자동 삽입 프리페처 (state-of-the-art)도 DLRM의 무작위/입력 의존적 접근 패턴에 효과적이지 못함 → baselines 대비 거의 개선 없음
- **핵심 원인**: embedding 테이블 접근은 stride 패턴이 아닌 indirection을 통한 무작위 접근으로, 기존 프리페처의 패턴 감지 메커니즘이 작동하지 않음

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1. Application-Specific Software Prefetching

- **What to prefetch?**: 소프트웨어가 indices 배열을 미리 살펴보고 미래 접근 주소를 계산 → demand load와 함께 look-ahead prefetch 요청 발행
- **When to prefetch?**: lookup granularity로 look-ahead 거리를 결정 → 최적 거리 = **4 lookups** (약 200개 명령어 간격), Figure 10(b)에서 검증
- **How to prefetch?**: `_mm_prefetch` intrinsic 사용 → `_MM_HINT_T0`로 L1D$에 prefetch (가장 가까운 위치)
- **Where to prefetch?**: L1D$ (32KB)에 prefetch하지만 캐시 오염 방지를 위해 적절한 거리 유지 필요
- **Algorithm 3**: embedding_bag 연산자에 prefetch 로직 삽입, `pf_dist=4`, `pf_blocks = ddim/16` 설정으로 각 lookup마다 미래 embedding row vector prefetch
- **효과**: baseline 대비 캐시 miss rate 최대 **26.8% 감소**, embedding lookup 단계 최대 **47% speedup**, 전체 추론 최대 **46% speedup**
- 다중 코어에서 캐시/대역폭 스트레스 증가 → hyperthreading과 결합하여 완화

### 4.2. Model-Parallel Hyperthreading (MP-HT)

- **기존 hyperthreading의 문제**: naive 두 인스턴스 동시 실행 (DP-HT)은 tail latency 악화 → SLA 위반 (RM2_3 Low Hot에서 SLA 대비 152ms 초과)
- **핵심 아이디어**: Bottom MLP (compute-bound)와 embedding lookup (memory-bound)은 독립적 작업 → 물리적 코어의 2개 스레드에서 동시 실행
- **MP-HT 구현**: PyTorch thread pool을 hyperthreading-aware로 수정, 동일 물리적 코어의 2개 스레드가 하나의 task queue를 공유 → 다른 코어가 inference task를 탈취 불가
- **왜 효과적인가**:
  - Bottom MLP의 working set은 수 MB로 작아 embedding 스레드와 캐시/대역폭 경쟁 최소화
  - embedding 스레드가 메모리 대기 시 Bottom MLP 스레드가 파이프라인 자원 활용 → CPU_Utilization 극대화
- **효과**: 단독 사용 시 최대 **37% 추론 시간 개선**

### 4.3. SW-PF + MP-HT의 시너지 효과

- prefetching이 embedding 스레드의 성능을 개선하면 메모리 명령어가 더 빨리 파이프라인 자원을 해제 → Bottom MLP 스레드에 더 많은 자원 제공
- Bottom MLP는 compute-heavy이므로 prefetching이 캐시/대역폭 리소스를 더 효율적으로 활용
- **비선형적 상승 효과**: 단순 합산보다 높은 성능 향상 달성 → 최대 **1.59x** speedup

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2023ISCA-summarize/optimizing-cpu-performance-for-recommendation-systems-at-scale.md|전체 요약 보기]]
