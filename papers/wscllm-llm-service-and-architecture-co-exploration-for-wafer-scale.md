---
tags: [paper, 2025, 2025ISCA, topic/cache, topic/disaggregation, topic/dram, topic/gpu, topic/llm-inference]
venue: "Proceedings of the 52nd Annual International Symposium on Computer Architecture (ISCA '25), 2025"
year: 2025
summary_path: "../paper-summaries/2025ISCA-summarize/wscllm-llm-service-and-architecture-co-exploration-for-wafer-scale.md"
---

# WSC-LLM: Efficient LLM Service and Architecture Co-exploration for Wafer-scale Chips

**Venue:** Proceedings of the 52nd Annual International Symposium on Computer Architecture (ISCA '25), 2025
**저자:** Zheng Xu, Dehao Kong, Jiaxin Liu, Jinxi Li, Jingxiang Hou, Xu Dai, Chao Li, Shaojun Wei, Yang Hu, Shouyi Yin (Tsinghua University, Shanghai AI Laboratory, Shanghai Jiao Tong University)

## 개요

- LLM의 파라미터 수가 급격히 증가함에 따라 단일 GPU/NPU로는 충분한 트랜지스터 규모와 메모리 용량을 확보하기 어려움. Moore's Law 종료와 포토마스크 크기 제약으로 인해 단일 칩에서의 LLM 지원이 한계에 직면.
- 분산 컴퓨팅 아키텍처를 통한 LLM 추론 시, 모델 가중치와 KV 캐시의 대규모 전송이 필요하며, 기존 인터커넥트 통신 대역폭이 LLM 서빙 시스템 성능의 주요 병목으로 작용 (기존 GPU 간 NVLink 대역폭의 한계).
- Wafer-scale 칩 기술은 NPU와 DRAM 칩렛을 통합하여 기존 최첨단 GPU 대비 약 50배의 트랜지스터 수와 6배의 칩 간 대역폭을 제공하지만, 제한된 웨이퍼 면적에서 연산/저장/통신 자원 간 트레이드오프가 발생.
- 기존 LLM 서빙 시스템 (Splitwise 등)은 고정된 텐서 병렬화(TP) 크기를 사용하여 자원 활용도가 낮고, wafer-scale 칩의 2D-mesh 토폴리지 특성을 고려하지 않아 통신 오버헤드가 큼.
- LLM 추론의 prefill과 decoding 단계의 자원 수요가 크게 다르지만 (prefill은 연산 집약적, decoding은 메모리 대역폭 집약적), 동일한 디바이스로 처리하면 비효율 발생.

## 방법론

### 3.1. Central Scheduler (자원 분할 및 배치)

- **Algorithm 1 (Optimal Resource Partition):** 모델 M, die 수 제한 D, die당 메모리 용량 c, 워크로드 W, TP 전략 S, 전체 die 수 N을 입력으로 받아 최적의 prefill/decoding 인스턴스 설정 결정.
  - 모든 가능한 인스턴스 크기를 순회하며 (die 수 제한 및 전체 메모리 용량으로 제약)
  - 각 인스턴스 크기에서 가능한 모든 TP 분할 전략을 열거
  - prefill/decoding 각 단계의 goodput(단일 인스턴스 상한 성능)을 시뮬레이션으로 측정
  - 최적 설정의 인스턴스 수를 throughput 비율에 따라 결정 (N_P, N_D)
  - 복잡도: O(D·S), 탐색 공간이 관리 가능하여 수 분 내 해결
- **Algorithm 2 (Optimal KV Cache Placement):** wafer-scale 칩의 모든 DRAM을 활용하여 KV 캐시를 최적 위치에 배치
  - prefill/decoding 인스턴스 간 최단 경로에 속하는 DRAM 세트를 식별
  - 위치 우선순위와 잔여 용량을 기반으로 우선순위 큐 구성
  - 요청별로 KV 캐시 저장 요구사항을 충족할 때까지 DRAM 자원 할당
  - 메모리 스케줄러가 central scheduler에 요청 실행 중단을 알릴 수 있는 메커니즘 포함

### 3.2. Resource Placement 전략

- **Decoding-centered 배치 전략:** decoding 인스턴스를 웨이퍼 중앙에 배치하고, prefill 인스턴스를 주변에 배치.
- 전송 비용(TransferCost)을 최소화하는 목적 함수: `TransferCost = Σ min Distance(P_i, D_j)`
  - P_i: prefill 인스턴스 중심 위치, D_j: decoding 인스턴스 중심 위치
  - 동일한 최단 경로가 여러 개인 경우 비중복 경로 선택
- 통신 링크 공유 시 하이퍼파라미터 α≥1 추가 (D2D 대역폭이 DRAM 대역폭의 2배를 초과하면 α=1)
- Figure 7: 무작위 배치 vs decoding 중심 배치 비교 — 48-die 칩에서 NP=8, ND=4일 때, 무작위 배치의 전송 비용은 (8α+16) hops, decoding 중심 배치는 16 hops

### 3.3. Execution Scheduler (Prefill/Decoding Pool)

- **Prefill Pool:**
  - 각 prefill 인스턴스는 FCFS 큐(Q_Pi)로 요청 관리
  - Chunked prefill 기법 적용: 긴 프롬프트를 균일한 크기의 청크로 분할하여 반복 처리
  - 배칭과 결합하여 다양한 입력 프롬프트 길이의 하드웨어 활용도 극대화
  - Figure 8: 3개 큐(8-die)의 매핑 스케줄링 예시
- **Decoding Pool:**
  - 각 decoding 인스턴스는 FCFS 큐(Q_Di)로 요청 관리
  - Continuous batching 기법 적용: 비어텐션 연산은 병렬, 어텐션 연산은 순차 처리
  - 디코딩의 낮은 연산 요구사항을 활용하여 가능한 많은 토큰을 배칭

### 3.4. Memory Scheduler

- wafer-scale 칩의 높은 D2D 대역폭(일반적으로 DRAM 대역폭 초과)을 활용하여 cross-die DRAM 읽기/쓰기를 DRAM 대역폭에 의해 제약
- KV 캐시의 cross-die 전송을 DRAM 접근과 오버랩하여 처리
- Algorithm 2 기반 최적 KV 캐시 배치로 추가 D2D 전송 오버헤드 최소화
- 웨이퍼 전체 DRAM을 KV 캐시 저장에 활용하여 높은 LLM 서버 성능 달성

### 3.5. Operator Execution Engine

- **Die-level (TP Engine):** GEMM 연산자(B, S, H, K 4차원)를 기본/하이브리드 TP 분할 전략으로 분할
  - 기본 TP: 단일 차원 분할 (B, S, H, K 각각)
  - 하이브리드 TP: 다중 차원 분할 (LLaMA3-70B의 GQA: K/V 헤드를 H 차원으로 추가 분할)
  - Bidirectional Ring 알고리즘으로 All-gather/All-reduce 통신 구현 (2D-mesh에 적합)
- **Core-level (Intra-Die Engine):** 서브연산 작업을 아톰 연산으로 추가 분할
  - SRAM 제약을 준수하는 아톰 연산을 단일 코어에 매핑
  - Weight Stationary(WS) 접근 기반 매핑 + 휴리스틱 알고리즘으로 최적 인라인-레이어 파이프라이닝 탐색

## 핵심 기여

- **핵심 Contribution:** wafer-scale 칩에서의 LLM 서비스와 아키텍처 공동 탐색을 위한 최초의 통합 프레임워크 제안
- **성능 향상:** SOTA LLM 서빙 시스템(GPU 클러스터 기반 Splitwise) 대비 E2E latency 평균 3.12×, TPS 36.47% 향상
- **설계 인사이트:**
  - wafer-scale 칩의 연산/저장/통신 자원 간 균형이 최적 성능의 핵심
  - DRAM 대역폭과 용량이 LLM 서비스 품질의 가장 중요한 결정 요인
  - 메모리와 통신 자원의 균형 잡힌 자원 할당이 최적 성능에 필수
- **의의:** wafer-scale 기술이 LLM 추론에 적용될 때 아키텍처와 스케줄링을 공동 최적화하면 상당한 성능 향상을 달성할 수 있음을 입증

## 주요 결과

- **구현 언어:** Python (시뮬레이터 프레임워크), C++ (오퍼레이터 실행 엔진)
- **평가 프레임워크:** ASTRA-sim (오픈소스 분산 훈련 시뮬레이터) 확장
  - LLM 추론의 동적 반복 특성 지원 (훈련의 정적 특성과 구별)
  - 오프라인 매핑 조회 테이블 사전 구축 (DNN 기반 피팅)
- **하드웨어 구성:**
  - Compute die: 21.92mm × 22.81mm, 16×16 Dojo-style 코어 배열
  - TSMC 7nm 공정, 1GHz 동작 주파수
  - 코어당 1.02 TFLOPS (Tensor FP16), 1.25MB SRAM
  - 인터커넥트 대역폭: 4방향 총 6 TB/s

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]


## 전체 요약

[[../paper-summaries/2025ISCA-summarize/wscllm-llm-service-and-architecture-co-exploration-for-wafer-scale.md|전체 요약 보기]]
