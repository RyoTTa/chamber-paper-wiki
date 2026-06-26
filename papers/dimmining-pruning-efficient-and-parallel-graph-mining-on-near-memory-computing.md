---
tags: [paper, 2022, 2022ISCA, topic/dram, topic/near-data-processing]
venue: "ISCA 2022 (The 49th Annual International Symposium on Computer Architecture)"
year: 2022
summary_path: "../paper-summaries/2022ISCA-summarize/dimmining-pruning-efficient-and-parallel-graph-mining-on-near-memory-computing.md"
---

# DIMMining: Pruning-Efficient and Parallel Graph Mining on Near-Memory-Computing

**Venue:** ISCA 2022 (The 49th Annual International Symposium on Computer Architecture)
**저자:** Guohao Dai, Zhenhua Zhu, Tianyu Fu, Chiyue Wei, Bangyan Wang, Xiangyu Li, Yuan Xie, Huazhong Yang, Yu Wang (Tsinghua University / BNRist / University of California, Santa Barbara)

## 개요

- 그래프 마이닝(Graph Mining)은 소셜 네트워크 분석, 머신러닝, 추천 시스템 등 다양한 도메인에서 점점 더 중요해지고 있는 그래프 내 특정 패턴 탐색 문제
- 그래프 마이닝 가속화의 세 가지 핵심 과제:
  1. **프루닝(Pruning)을 위한 무거운 비교 연산:** 그래프 마이닝에서 대칭性和同型성 제약을 걸어 탐색 공간을 줄이기 위해 프루닝이 널리 사용됨. Table 1에 따르면 비교 연산이 전체 실행 시간의 **6%~53%**를 차지 (5-CF의 경우 53%)
  2. **집합 연산의 낮은 병렬성:** 그래프 마이닝은 정점의 이웃 간 집합 연산(교차, 차집합)으로 표현됨. CSR 포맷은 메모리 효율적이지만 병렬성이 낮고, 비트맵 포맷은 병렬성이 높지만 그래프의 희소성으로 인해 메모리 공간 비효율적
  3. **무거운 데이터 전달:** 그래프 마이닝은 원본 그래프보다 **26배~451배** 큰 중간 데이터를 CPU-메모리 간 반복 전달해야 함 (Table 2: LiveJournal의 경우 그래프 크기 대비 323배)

## 방법론

### 3.1. Index Pre-comparison (Section 3)

#### 3.1.1. Self Anchor (패턴에서 연결된 정점)
- 각 정점의 이웃을 두 개의 불相交 집합으로 사전 분할: $N_{left}(u)$ (자신보다 작은 인덱스의 이웃)과 $N_{right}(u)$ (자신보다 큰 인덱스의 이웃)
- 제약 조건 $u_0 < u_1$이 있을 때, $u_1$은 전체 $N(u_0)$ 대신 $N_{right}(u_0)$만 순회 → 비교 연산 완전 제거
- 메모리 오버헤드: $O(|V|)$ (자기 앵커 포인터 배열 추가)
- 평균 그래프 크기 대비 **15%** 저장 오버헤드

#### 3.1.2. Neighbor Partitions (패턴에서 비연결된 정점)
- Self Anchor가 적용 불가능한 경우(비연결 정점 간 비교)를 위한 구간(Interval) 기반 분할
- 이웃 집합을 $P$개 구간으로 분할하여, 집합 연산을 전체 집합이 아닌 특정 구간에 대해 수행
- 수식: $N(u_0) \cap N(u_1) - N(u_2) = \bigcup_{i<P} [N_{I_i}(u_0) \cap N_{I_i}(u_1) - N_{I_i}(u_2)]$
- 비교 연산이 전체 이웃 집합 크기가 아닌 구간 크기에 의해 제한됨
- 상위 10% 고차수 정점에만 적용 → 평균 **12%** 추가 메모리 오버헤드

### 3.2. Flexible BCSR 포맷 (Section 4.1, Figure 4)

- **구조:** 인접 정점들을 그룹으로 묶고, 각 그룹을 <Key, Value> 쌍(KVP)으로 표현
  - Key: 그룹 인덱스 (CSR의 column array와 유사)
  - Value: 해당 그룹 내 이웃을 나타내는 비트맵
- **유연성:** $a$비트(Key) + $b$비트(Value) = 32비트 (DRAM 정렬)
  - $a=0, b=|V|$ → 비트맵 포맷
  - $a=\lceil \log_2(|V|) \rceil, b=1$ → CSR 포맷
- **메모리 절약:** CSR 대비 **4.3%~40.6%** 메모리 절약 (Table 3)
- **병렬성 향상:** CSR 대비 **1.01×~2.30×** 병렬성 향상 → CPU에서 평균 **1.25×** speedup
- 집합 연산: 먼저 Key를 비교하여 공통 그룹을 찾고, 해당 Value에 비트 연산(AND/OR) 수행

### 3.3. Systolic Merge Array (Section 4.2, Figure 5)

- **목적:** BCSR의 Key 배열(비연속 이웃)에 대한 병렬 집합 연산 수행
- **세 가지 구성요소:**
  1. **Processing Matrix (PM):** 두 입력 벡터의 모든 KVP 쌍에 대해 키 비교 및 비트 연산을 병렬 수행
  2. **Filter Array (FA):** 부분 결과를 결합 (교차: $\cup$, 차집합: $\cap$)
  3. **Compaction Triangle (CT):** 무효 KVP를 제거하고 유효 결과를 압축
- **동작 원리:** "space-time-offset" 방식으로 입력 벡터 요소가 PM을 흐르며 모든 요소와 연산
- Ordered Queue 대비 **7.00×**, Crossbar 대비 **7.37×** 높은 처리량 (Table 4)
- 완전 파이프라인 구조로 확장성 용이

### 3.4. DIMM 기반 NMC 아키텍처 (Section 5, Figure 6)

- **구조:**
  - LRDIMM 기반, DRAM 디바이스 변경 없이 rank 수준 NMC 프로세서 추가
  - 각 rank에 2개의 DIMMining NMC 모듈 배치
  - 메모리 모드(일반 DRAM)와 NMC 모드 지원
- **DRAM 칩 구성:** 각 칩을 3개 영역으로 분할
  - KVP 데이터 영역, 시작 주소 영역, 중간 데이터 영역
- **수정된 RCD:** NMC 명령 버퍼 & 디코더, 주소 생성자 추가
- **NMC 모듈 구성:**
  - Data Forwarding Unit: BCSR 데이터 전달 + 128KB SRAM 캐시
  - Mining Processor: SMA 기반 집합 연산 수행
  - NMC Controller: 연산 큐 관리, 다음 정점 데이터 접근

## 핵심 기여

1. **Index Pre-comparison로 프루닝 비교 연산을 효과적으로 감소:** Self Anchor와 Neighbor Partition을 통해 비교 연산이 전체 시간의 6%~53%를 차지하는 문제를 해결
2. **BCSR 포맷으로 희소 그래프에서도 비트맵 수준의 병렬성 달성:** CSR 대비 메모리 16.57% 절약하면서 병렬성 2.30× 향상
3. **SMA로 비연속 인덱스의 집합 연산을 효과적으로 병렬화:** Ordered Queue 대비 7.37× 처리량 향상
4. **DIMM 기반 NMC로 대용량 데이터 전달 병목 제거:** FPGA 대비 222.23×, CPU 대비 139.51× speedup
5. **상용 DDR 기반으로 실용성 확보:** HMC 기반 SISA 대비 5.78×~12.32× 성능 while DRAM 내부 회로 변경 없음

**Broader significance:** DIMMining은 그래프 마이닝의 세 가지 핵심 과제(비교 오버헤드, 낮은 병렬성, 대용량 데이터 전달)를 알고리즘부터 아키텍처까지 풀스택으로 해결하며, DIMM 기반 NMC의 실용성을 입증. 향후 다양한 그래프 마이닝 문제에 적용 가능한 범용 가속화 프레임워크를 제시

## 주요 결과

- **프로세서:** CPU (Baseline), FPGA, DIMMining NMC 모듈
- **시스템 구성:**
  - DIMMining NMC: 32nm 공정 기준 모듈당 **0.38mm²**, **105mW**
  - 15nm 스케일링 시 유효 면적 **0.14mm²** (FlexMiner과 유사)
  - 캐시: 128KB SRAM (최적 설계점)
- **그래프 데이터셋:** P2P(11K 정점), Astro(18K), Mico(0.1M), Patents(2.7M), Youtube(7.1M), LiveJournal(4.8M)
- **마이닝 패턴:** 3-CF, 4-CF, 5-CF (Clique Finding), 3-MC (Motif Counting), Diamond, House

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]


## 전체 요약

[[../paper-summaries/2022ISCA-summarize/dimmining-pruning-efficient-and-parallel-graph-mining-on-near-memory-computing.md|전체 요약 보기]]
