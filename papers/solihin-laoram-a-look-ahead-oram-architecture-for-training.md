---
tags: [paper, 2023, 2023ISCA, topic/cache, topic/dram, topic/gpu, topic/security, topic/storage, topic/virtual-memory]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023ISCA-summarize/laoram-a-look-ahead-oram-architecture-for-training-large-embedding-tables.md"
---

# LAORAM: A Look Ahead ORAM Architecture for Training Large Embedding Tables

**Venue:** 
**저자:** 

## 개요

### 1.1 Embedding Table의 메모리 주소 노출 문제

추천 시스템(Recommendation Models, e.g. DLRM)과 NLP 모델(e.g. XLM-R)은 categorical feature를 학습하기 위해 **Embedding Table**을 사용한다. 대규모 Embedding Table(수 TB 규모)은 GPU VRAM에 전부 탑재할 수 없어, CPU DRAM에 저장하고 GPU가 training batch마다 필요한 embedding entry만 fetch하는 **hybrid training**이 널리 사용됨 (예: cDLRM, AIBox).

이때 CPU DRAM으로의 메모리 접근 주소는 embedding entry index를 그대로 노출하며, 이는 심각한 privacy leak으로 이어진다. 예를 들어 사용자가 시청한 영화 카테고리, 정치 성향, 광고 클릭 이력 등이 embedding table index에 1:1 매핑되어 유출된다.

- **Figure 2**: DLRM의 Kaggle dataset에서 첫 10,000 training sample에 대한 embedding table 접근 패턴 — 대부분 random access이며 소수 인덱스만 반복 접근됨.

### 1.2 기존 ORAM 접근법의 한계

**PathORAM**은 모든 data block 접근마다 root→leaf 경로 전체를 fetch하고, 접근 후 block의 path를 random reassign하여 address obfuscation을 제공한다. 그러나 PathORAM의 이론적 하한은 다음과 같다:

- PathORAM: t개 block 접근 시 `t × [log₂(N) − 1]` 개의 data block fetch 필요 (N = total blocks)
- 예: 8M entries → tree height `log₂(8M)` ≈ 23 levels → 한 block당 ~22 block 추가 fetch → bandwidth ~23배 증가

**PrORAM**은 과거 접근 이력을 기반으로 superblock을 형성하여 path fetch 수를 줄이려 했으나, embedding table 접근 패턴이 random하기 때문에 superblock hit rate가 극히 낮다:
- Kaggle dataset: superblock hit rate **6%**
- XNLI dataset: superblock hit rate **12%**
- Permutation/Gaussian dataset: hit rate ≈ **0%**

따라서 PrORAM은 PathORAM 대비 성능 향상이 거의 없다.

### 1.3 ML Training의 Lookahead 속성

ML training pipeline은 **training batch를 미리 생성**하는 것이 일반적이다 (random seed에 의해 결정론적). 따라서 **미래의 embedding table 접근 패턴을 미리 알 수 있다**는 unique property가 존재한다. LAORAM은 이 **lookahead knowledge**를 활용하여 superblock을 aggressive하게 형성한다.

---

## 방법론

### 3.1 Dynamic Superblock Formation via Lookahead

**핵심 아이디어**: Preprocessor가 미래 training batch를 scan하여, **함께 접근될 embedding table entry들을 superblock으로 묶고**, superblock 전체를 ORAM tree의 **단일 path**에 할당한다.

**알고리즘 (Preprocessing)**:
1. **Dataset Scan**: Preprocessor가 superblock size S를 입력으로 받아, upcoming training batch의 S개 entry를 하나의 superblock bin에 할당. 가능한 많은 batch(epoch 전체 등)를 미리 scan.
2. **Superblock Path Generation**: 각 superblock bin에 대해 `U(1, L)`에 따라 random path 할당 (L = leaf 수). 이 `(superblock → future path)` mapping을 Trainer_GPU에 secure하게 전송.

**PathORAM과의 차이**: PathORAM의 경우 한 block 접근 시 path 하나를 통째로 fetch. LAORAM은 S개 block이 superblock으로 묶이면 **S개 block을 1개 path fetch로 처리** → path fetch 횟수 1/S로 감소.

**Data Independence**: Write-back 시 각 block은 **미래의 locality에 따라 독립적으로** 다른 superblock에 할당되며, 이전 superblock membership은 미래 path assignment에 영향을 주지 않는다.

### 3.2 Fat-Tree Structure for Stash Efficiency

**문제**: Superblock size가 커질수록, 여러 block을 **단일 path에 write-back**해야 하므로 stash에 남을 확률이 증가 → stash overflow → background eviction(dummy read) 증가 → 성능 저하.

**Key Observation**: ORAM tree에서 **상위 레벨(root에 가까울수록) 노드는 더 많은 path들이 공유**하므로, block이 write-back될 확률이 높다:
- Root(node level 0): write될 확률 0.5
- Level 1: 0.25
- Level 2: 0.125
- ... (level L로 갈수록 확률 1/2^L)

**Fat-Tree Design**: Root 쪽 bucket size를 더 크게, leaf 쪽은 더 작게 — 선형 감소(linear decay). 예: leaf bucket size=5, root bucket size=10 (level 6 tree).

**Strawman (uniform bucket size increase)와 비교**:
- Uniform doubling: tree capacity 2배 증가
- Fat-tree: 동일 capacity에서 **12.4% 적은 dummy read** + **16.6% 적은 메모리** 소비

**구현 예시** (8M entries, level L=23 tree):
- Normal tree: 모든 레벨 bucket size = 4
- Fat-tree: root bucket = 8, leaf bucket = 4, 중간은 선형 감소

**Stash Usage 비교 (Figure 7)**: 12500 access 후 stash occupancy:
- Normal/S4: ~10,600 blocks
- Fat/S4: ~3,600 blocks (66% 감소)
- Normal/S8: ~15,500 blocks
- Fat/S8: ~4,700 blocks (70% 감소)

### 3.3 Two-Stage Pipeline

```
[Preprocessor] → (superblock metadata) → [Trainer_GPU]
Trainer_GPU: request paths → [Server_storage] → return path blocks
Trainer_GPU: gradient update → write-back updated blocks
```

Preprocessing은 GPU training과 pipeline되어 있으므로, training critical path에 포함되지 않는다. Initial preprocessing time for one epoch: ~10분 (GPU training time에 비해 무시할 수준).

---

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1 Path Obliviousness of Superblocks

LAORAM의 superblock 접근이 기존 PathORAM과 동일한 obliviousness를 보장함을 수학적으로 증명:

**Theorem**: LAORAM에서 임의의 data block d의 next path가 path p로 할당될 확률은 uniform distribution `U(1, N)`을 따름.

```
Pr(NEXT_PATH(d) = p) = Σ Pr(p ∈ b_i) · Pr(d ∈^ b_i) = Σ (1/N) · Pr(d ∈^ b_i) = 1/N
```

- 첫 번째 등호: total probability
- 두 번째 등호: superblock의 path assignment가 data block 내용과 **독립적**
- 세 번째 등호: Σ Pr(d ∈^ b_i) = 1

### 4.2 Server_storage 접근 패턴

Server_storage 입장에서는 **path granularity의 random path 요청**만 관찰된다. 이는 PathORAM의 접근 패턴과 동일하며, adversary는 두 memory access를 구별할 수 없다.

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/security.md|Security]]
- [[paper-wiki/concepts/storage.md|Storage]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2023ISCA-summarize/laoram-a-look-ahead-oram-architecture-for-training-large-embedding-tables.md|전체 요약 보기]]
