---
tags: [paper, 2022, 2022ISCA, topic/cache, topic/dram, topic/near-data-processing]
venue: "ISCA 2022 (The 49th Annual International Symposium on Computer Architecture)"
year: 2022
summary_path: "../paper-summaries/2022ISCA-summarize/menda-a-near-memory-multi-way-merge-solution-for-sparse-transposition-and-dataflows.md"
---

# MeNDA: A Near-Memory Multi-way Merge Solution for Sparse Transposition and Dataflows

**Venue:** ISCA 2022 (The 49th Annual International Symposium on Computer Architecture)
**저자:** Siying Feng (University of Michigan), Xin He (University of Michigan), Kuan-Yu Chen (University of Michigan), Liu Ke (Washington University in St. Louis), Xuan Zhang (Washington University in St. Louis), David Blaauw (University of Michigan), Trevor Mudge (University of Michigan), Ronald Dreslinski (University of Michigan)

## 개요

- 희소 선형 대수(Sparse BLAS)는 그래프 분석, 머신러닝, 과학 계산 등에서 필수적인 프리미티브이나, 불규칙한 메모리 접근 패턴으로 인해 메모리 집약적
- **희소 행렬 전치(transposition)의 중요성:** CSR↔CSC 변환은 이축 공유 Gradient, Quasi-Minimal Residual, 대수적 다중 그리드 방법 등에서 필수 Building Block
  - 그래프 분석 프레임워크에서 데이터플로우 표현을 동적으로 전환할 때 빈번한 전치가 필요 (Beamer et al. BFS 혼합 접근법 기반)
  - 최근 알고리즘/아키텍처 발전으로 그래프 처리 성능이 향상되면서, 런타임 전치 오버헤드가 실행 시간의 126%에 달할 수 있음 (CoSPARSE 기준)
- **기존 최적화의 한계:** SpMM/SpMV 등 다른 희소 커널은 크게 최적화되었으나, 희소 행렬 전치는 상대적으로 주목받지 못함
  - OuterSPACE(2018)에서 SpMM 실행 시간이 전치와 유사 → SpArch(2020)에서 SpMM이 전치보다 훨씬 빨라지면서 전치가 병목으로 부상
- **메모리 대역폭 병목:** 희소 행렬 전치는 정수 비교만 수행하며 연산 강도가 낮아, 성능이 달성 가능한 메모리 대역폭에 크게 의존
  - Roofline 모델 분석: 희소 행렬 전치는 완전히 memory-bound
  - 스케일러빌리티 분석: CPU 스레드 확장 시 메모리 인터페이스에서의 요청 경쟁으로 인해 성능 확장 한계

## 방법론

### 3.1. 도전 과제 및 해결 (Section 3)
- **도전 1: 양방향 고대역폭 필요**
  - 희소 행렬 전치는 감소(reduction)가 없으므로 입력-fetch와 출력-streaming 모두 고대역폭 필요
  - 기존 sparse gathering 제안처럼 출력을 호스트로 직접 전송하는 방식은 불가능
- **도전 2: 제한된 온칩 저장소**
  - CPU 구현(mergeTrans)은 중간 데이터를 호스트-메모리 간 왕복 전송 → 큰 메모리 트래픽 발생
  - NMP 가속기는 더 제한된 SRAM으로 중간 데이터 전송량을 줄여야 함
- **도전 3: 멀티 PU 간 통신**
  - DIMM 내 여러 rank에 PU 배치 시, DIMM 간 통신은 off-chip 인터페이스를 거쳐야 함 → 병목
- **도전 4: 데이터 레이아웃 제약**
  - 전치 후에도 압축 형식(CSR/CSC) 유지 필요
  - PU 간 통신을 피하는 데이터 레이아웃 필요

### 3.2. 하드웨어 머지 트리 (Section 3.3)
- **넓은 머지 트리:** 머지 정렬 반복 횟수를 줄여 중간 데이터 전송량 최소화
  - 리프 수 = 1024 (1024-way 머지)
- **Seamless Back-to-Back Merge Sort:** 여러 라운드의 머지 정렬을 stall 없이 연속 실행
  - 각 PU는 FIFO 엔트리 2개를 사용하여 입력/출력 버퍼 교체 시 지연 최소화
- **Stall Reducing Prefetching:**
  - prefetch 버퍼(32 엔트리)를 활용하여 DRAM read 지연을 숨김
  - 메모리 대역폭 활용률 극대화
- **Request Coalescing:**
  - 인접 메모리 접근을 하나의 요청으로 병합하여 메모리 컨트롤러 요청 큐 사용량 감소

### 3.3. 데이터 레이아웃 (Section 3.5)
- **NNZ 기반 수평 분할:** 희소 행렬을 각 rank에 동일한 NNZ 수만큼 수평으로 분할
  - 각 rank가 독립적으로 전치 수행 가능 → PU 간 통신 불필요
  - 행 인덱스가 rank 간 겹치지 않도록 설계
- **압축 형식 유지:** 입력 CSR과 출력 CSC 모두 동일한 수평 분할 형식 유지
  - 호스트 코드 변경 최소화

### 3.4. SpMV 확장 (Section 3.6)
- MeNDA의 머지 트리는 outer-product SpMV의 partial column 병합에 활용 가능
- CoSPARSE 프레임워크와 통합하여 검증
- SpMV를 위한 부가 하드웨어: 16개 FP 곱셈기 + 3개 FP 덧셈기 (누적용)

## 핵심 기여

- **희소 행렬 전치의 중요성 재조명:** SpMM/SpMV 최적화로 인해 전치가 새로운 병목으로 부상 (최대 126% 오버헤드)
- **NMP 기반 해결책:** DIMM 내부 대역폭을 활용하여 off-chip 인터페이스 병목 제거
- **범용성:** Merge Sort 기반으로 SpMV 등 다른 희소 프리미티브로 확장 가능
- **실용적 통합:** DIMM 버퍼 칩에 통합 가능한 저전력(78.6mW)/소면적(7.1mm²) 가속기
- **성능:** CPU scanTrans 대비 19.1배, cuSPARSE GPU 대비 7.7배 속도 향상
- **의의:** 희소 선형 대수 애플리케이션의 메모리 병목을 NMP로 해결하는 효율적이고 확장 가능한 아키텍처 제안

## 주요 결과

- **구현 언어:** Cycle-accurate 시뮬레이터 + Ramulator 메모리 인터페이스 연결
- **RTL:** PU의 RTL 모델을 40nm에서 Synopsys Design Compiler로 합성
- **PU 파라미터:**
  - 주파수: 800MHz
  - 면적: 7.1mm² (40nm)
  - 소비 전력: 78.6mW (SpMV 지원 시 추가 13.8mW)
  - 리프 수: 1024
  - FIFO 엔트리: 2개, 프리페치 버퍼: 32 엔트리, 읽기/쓰기 큐: 32 엔트리
- **통합 가능성:** DIMM의 버퍼 칩에 통합 가능 (일반 버퍼 칩 면적 ~100mm² 대비 7.1mm²로 작은 오버헤드)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]


## 전체 요약

[[../paper-summaries/2022ISCA-summarize/menda-a-near-memory-multi-way-merge-solution-for-sparse-transposition-and-dataflows.md|전체 요약 보기]]
