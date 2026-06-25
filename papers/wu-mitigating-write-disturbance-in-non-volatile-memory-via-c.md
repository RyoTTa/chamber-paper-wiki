---
tags: [paper, 2024, 2024HPCA, topic/cache, topic/compression, topic/disaggregation, topic/dram, topic/nvm, topic/rowhammer, topic/storage]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024HPCA-summarize/mitigating-write-disturbance-in-non-volatile-memory-via-coupling-machine-learning-with-out-of-place-updates.md"
---

# Mitigating Write Disturbance in Non-Volatile Memory via Coupling Machine Learning with Out-of-Place Updates

**Venue:** 
**저자:** Ronglong Wu, Zhirong Shen, Zhiwei Yang, Jiwu Shu (Xiamen University)

## 개요

### 1.1 Write Disturbance (WD) 문제

NVM(Non-Volatile Memory: PCM, STT-RAM, ReRAM)은 DRAM에 준하는 접근 성능과 높은 집적도를 제공하지만, **Write Disturbance (WD)** 문제에 취약하다. WD는 메모리 셀을 프로그래밍(특히 RESET)할 때 발생한 열 확산(heat diffusion)이 인접 셀의 값을 의도치 않게 변경('0'→'1')시키는 현상이다. PCM 기준으로 WD 에러율은 wordline 방향 9.9%, bitline 방향 11.5%에 달한다[45][77].

WD 에러는 메모리 신뢰성을 저하시킬 뿐 아니라, VnR(Verify-and-Restore) 과정에서 반복적인 읽기/쓰기를 유발하여 **쓰기 지연(write latency) 증가**와 **쓰기 내구성(write endurance) 저하**를 초래한다. NVM 셀 간 거리가 지속적으로 좁아짐에 따라 WD는 NVM 상용화의 1차적 장애물이 되고 있다.

### 1.2 기존 접근법

기존 WD 완화 기법은 크게 세 분류:
| 분류 | 예시 | 한계 |
|------|------|------|
| Data Encoding | DIN[45] (FPC 압축+인코딩), DMPart[89] (최소 빈도 패턴 마스킹), MinWD[68] (level-shift 인코딩), CEnT[39] | WD-prone 데이터 패턴(연속된 0)을 줄이지만, 모두 **in-place update** 가정 |
| Error Correction 최적화 | SD-PCM[77], ESD-PCM[46], DEFT[85] | VnR 지연을 숨기거나 지연시키지만, reactive 접근 |
| HW 보조 | SIWC[43] (write cache), Decongest[93] (page remapping) | 반복 쓰기 방지에 초점 |

### 1.3 핵심 관찰: Out-of-Place Update의 기회

대부분의 기존 연구는 **in-place update**를 가정한다. 그러나 많은 NVM 기반 시스템(key-value store, log-structured FS, hash index, disaggregated memory)은 **out-of-place update**를 사용한다. Out-of-place update에서는 새 데이터를 새로운 위치에 쓰고 기존 데이터를 invalidate하므로, **어떤 stale block을 덮어쓸지 선택할 수 있는 자유도**가 생긴다.

저자들은 15개 real-world 데이터셋으로 분석하여, stale block을 무작위 선택(RandSel)하는 대신 WD-prone cell이 가장 적은 블록을 골라 덮어쓰면 WD 에러를 **7.9%(n=10 후보) ~ 34.7%(n=1000 후보)** 추가 감소시킬 수 있음을 보였다(Figure 4). 그러나 enumeration 기반 선택은 최대 48배의 쓰기 지연을 초래한다.

## 방법론

### 3.1 실험 방법론

| 항목 | 구성 |
|------|------|
| **Testbed** | Intel Core i5-9400F, 4GB RAM, Ubuntu 20.04 |
| **NVM 모델** | SLC/MLC PCM, WD error rate: wordline 9.9%, bitline 11.5% |
| **데이터셋** | 15개 real-world (UCI ML Repository, Kaggle): Numerical 5개, Multimedia 4개, Textual 6개 |
| **Data Encoding Baselines** | DCW[100], DIN[45], DMPart[89], MinWD[68] |
| **비교 방식** | RandSel (random stale block 선택) + 각 encoding vs. LearnWD + 각 encoding |
| **Metrics** | WD errors per write, write cost (endurance), write energy, write latency |
| **Trace** | 50K stale blocks + 50K write requests (Poisson arrival) |
| **LearnWD Config** | k-means (k=16), MinHash (h=8), retrain every 20K writes |

### 3.2 주요 결과

#### Exp#1: WD Error 감소

| Encoding | RandSel 평균 WD errors/write | LearnWD 추가 감소율 |
|----------|-------------------------------|---------------------|
| DCW | ~25 | **31.2%** |
| DIN | ~18 | **28.4%** |
| DMPart | ~15 | **9.5%** |
| MinWD | ~12 | **11.1%** |

전체 평균 20.1% 추가 감소. Bitline 방향 평균 21.7% 추가 감소.

#### Exp#2-4: Write Cost, Energy, Latency

| Metric | DCW | DIN | DMPart | MinWD |
|--------|-----|-----|--------|-------|
| Write Cost (endurance) | −21.9% avg | − | − | − |
| Write Energy | −15.6% | −13.4% | −4.5% | −7.8% |
| Write Latency | −16.4% | −14.3% | −5.2% | −8.1% |

종합: LearnWD는 **평균 11.0% write latency 감소, 21.9% write endurance 향상**.

#### Exp#5: MLC PCM 확장

MLC PCM에서도 DCW 대비 **28.8%**, DIN 대비 **26.7%** WD error 추가 감소.

#### Exp#6: ECC 결합

ECC-0/1/2/4/8과 결합 시 **18.4%~54.1% VnR 연산 감소**.

#### Ablation Studies (Exp#7-#12)

- **k (클러스터 수):** k↑ → WD error↓, training latency↑. k=16 권장 (WD error 18.0% 감소 vs. RandSel, training 35s).
- **MinHash 함수 수 (h):** h=16일 때 h=0 대비 19.1% 추가 감소.
- **Retraining 빈도:** 5K writes마다 retraining 시 20K 대비 3.2% 추가 감소에 그침 → 빈번한 retraining 불필요.
- **Block size:** 64B~4KB 모든 크기에서 26.2%~34.7% 감소 유지.
- **클러스터링 알고리즘:** k-means, GMM, BIRCH 모두 효과적. BIRCH가 outlier 처리에 가장 우수 (37.8% 감소).
- **애플리케이션 변화:** 6개 데이터셋 transition 환경(10만 writes마다 데이터셋 변경, 총 50만 writes)에서도 11.8%~31.7% 감소 유지.

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

- **Stale Table DRAM footprint:** 512GB NVM 기준 block size 256B일 때 entry당 ~12.3 bits. 전체 stale table 1MB 이하 (2¹⁷ entries 가정).
- **Model training latency:** k=16 기준 ~35s. Back-end에서 수행 가능.
- **페이지 테이블 통합:** LearnWD는 stale block 선정 후 페이지 테이블만 갱신하며, read path는 변경 없음.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2024HPCA-summarize/mitigating-write-disturbance-in-non-volatile-memory-via-coupling-machine-learning-with-out-of-place-updates.md|전체 요약 보기]]
