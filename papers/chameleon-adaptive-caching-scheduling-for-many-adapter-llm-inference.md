---
tags: [paper, 2025, 2025MICRO, topic/cache, topic/gpu, topic/llm-inference]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO 2025)"
year: 2025
summary_path: "../paper-summaries/2025MICRO-summarize/chameleon-adaptive-caching-scheduling-for-many-adapter-llm-inference.md"
---

# Chameleon: Adaptive Caching and Scheduling for Many-Adapter LLM Inference Environments

**Venue:** IEEE/ACM International Symposium on Microarchitecture (MICRO 2025)
**저자:** Nikoleta Iliakopoulou, Jovan Stojkovic, Chloe Alverti, Tianyin Xu, Hubertus Franke, Josep Torrellas (University of Illinois Urbana-Champaign; IBM Research)

## 개요

- LLM 추론 클러스터는 다양한 다운스 트리밍 태스크(챗봇, 코드 생성, 요약 등)의 동시 쿼리를 처리해야 하며, 각 태스크는 다른 fine-tuned LLM이 필요 → 하드웨어 및 에너지 비용 급증
- Low-Rank Adaptation (LoRA)은 기본 모델의 소수 파라미터만 미세 조정하여 메모리 요구사항을 줄이지만, 기존 시스템(S-LoRA, Punica)은 두 가지 핵심 비효율성 존재
- **과제 1 — Adapter 로딩 오버헤드:** 기존 시스템은 GPU 메모리에서 adapter를 폐기하고 필요 시 CPU-GPU PCIe 링크를 통해 재로딩 → 높은 부하 시 PCIe 대역폭 포화(Figure 4: LoRA-500에서 8 RPS 시 P99 TTFT가 LoRA-1 대비 2.60× 증가)
- **과제 2 — 워크로드 이질성으로 인한 꼬리 지연:** adapter rank(크기), 입력/출력 크기, adapter 인기도에 따라 요청 실행 시간이 크게 변하며(Figure 7: heavy-tail 분포), 기존 FIFO 스케줄링은 head-of-line blocking 유발, SJF는 긴 요청 starve
- 실제 Azure 프로DUCTION trace 분석: 대부분의 요청은 짧은 시간에 완료되지만, 소수의 긴 요청이 전체 지연時間を 지배 → adapter 랭크가 꼬리 지연에 추가적인 주요 원인으로 작용

## 방법론

### 3.1. Adapter Cache

**캐시 구조:**
- 각 LLM 인스턴스당 로컬 캐시 1개 유지, 어댑터 가중치(읽기 전용)와 메타데이터(Adapter ID, Rank, Last Used Timestamp, Usage Frequency, Reference Counter) 저장
- Reference Counter가 0인 adapter만 교체 대상 → 현재 실행 중인 요청이 사용하는 adapter는 절대 교체 불가
- 스케줄러가 배치의 메모리 요구사항을 캐시 매니저에 전달 → 매니저가 필요 시 교체 및 로딩 수행

**동적 캐시 크기 조정 (Dynamic Cache Sizing):**
- 하드웨어 캐시와 달리 용량이 실시간으로 변동
- 입력 활성화, KV 엔트리, 누락 adapter가 유휴 GPU 메모리에 맞지 않을 때 캐시 축소 → 어댑터 폐기
- 요청 완료 후 유휴 메모리가 생기면 캐시 확대 → 해당 요청의 adapter 저장
- Figure 6: Llama-7B에서 대부분 시간 풍부한 유휴 메모리 존재,_but 부하 급증 시 급격히 감소 → 동적 조정 필수

**Cost-Aware Eviction Policy:**
- 점수 = F × Frequency + R × Recency + S × Size (F=0.45, R=0.10, S=0.55)
- 기존 LRU 대비 세 가지 요소를 복합 고려 → 인기 있는 adapter 보존 + 큰 adapter 우선 폐기(재로딩 비용 높음)
- Figure 17: rank 128 요청에서 Chameleon이 Ch-FairShare 대비 P99 TTFT 12% 추가 감소
- GDSF(Greedy Dual Size Frequency)와 비교: GDSF는 인기 있는 adapter만 캐싱하고 나머지를 폭넓게 폐기하는 경향 → Chameleon보다 열위

### 3.2. Adapter-Aware Multi-Queue Scheduler

**Weighted Request Size (WRS) 계산:**
- WRS = (A × InputSize/MaxInputSize + B × OutputSize/MaxOutputSize) × AdapterSize/MaxAdapterSize
- A=0.4, B=0.6 (실험적 프로파일링 기반)
- 입력 크기(prefill 지연), 출력 크기(decode 반복 횟수), adapter 크기(연산 속도 영향)를 종합적으로 고려
- 2차 다항식 적용 시 1차 대비 최대 10% 성능 향상

**큐 할당 및 자원 관리:**
- K-Means 클러스터링으로 최적 큐 수 결정 (Kmax=4), 클러스터 경계 = 인접 센트로이드의 중간값
- 각 큐에 자원 할당량(Tokens) 부여: 큐론 이론 기반 M/M/1 모델링
  - Tok_min ≥ S × D × (1/SLO + λ)
- 두 단계 스케줄링:
  - Phase 1: 각 큐가 할당량 내에서 배치에 요청 추가, 남은 자원은 "Total Spare Resources" 버킷에 수집
  - Phase 2: 잔여 자원을 작은 큐 순서대로 재분배 → 자원 활용도 최대화
- Opportunistic Bypassing: 특정 요청이 GPU 메모리 부족으로 실행 불가 시, 더 작은 요청이 대신 실행 가능 → 단, 반복적 bypass 방지를 위해 예측 기반 제어

**동적 큐 재구성:**
- 부하 패턴 변화에 따라 주기적으로(Trefresh=5분) 큐 수와 컷오프 재계산
- 정적 큐 구성 대비 고부하 시 10% P99 TTFT 향상(Figure 22)

### 3.3. Prefetching (선택적 최적화)

- 대기열의 요청이 필요로 하는 adapter를 사전에 GPU 메모리로 로딩
- 히스토그램 기반 미래 부하 예측 기법 적용
- 기본으로는 비활성화(예측 정확도에 의존), 실험에서 Chameleon 대비 P99 TTFT 8.8% 추가 감소(Figure 18)

## 핵심 기여

- **핵심 기여:** Many-adapter LLM 추론 환경을 위한 최초의 adapter 캐시 설계 + adapter-aware 다중 큐 스케줄러
- **성능 향상:** 고부하에서 P99 TTFT **80.7% 감소**, P50 TTFT **48.1% 감소**, throughput **1.5× 향상** (S-LoRA 대비)
- **멀티 GPU 확장성:** TP4에서 P99 TTFT **95.8% 감소**, GPU 수 증가에 따른 캐싱 이점 확대
- **실용성:** 소프트웨어만으로 구현, 하드웨어/OS/CUDA 커널 변경 불필요, 오픈소스 S-LoRA 기반
- **의의:** Adapter 기반 LLM 서빙의 두 가지 근본적 비효율성(로딩 오버헤드, 워크로드 이질성)을 동시에 해결하는 시스템 설계 제시 → many-adapter 환경에서의 실용적인 LLM 추론 최적화 방향 제시

## 주요 결과

- **기반 플랫폼:** S-LoRA (오픈소스 LLM 추론 서빙 플랫폼)
- **하드웨어/OS 변경 불필요:** CUDA 커널 수정 없음, 소프트웨어만으로 구현
- **하드웨어:** NVIDIA A40 GPU(48GB), AMD EPYC 9454 CPU(48코어, 377GB RAM)
- **확장 실험:** A100 GPU(24GB/48GB/80GB), 멀티 GPU(TP2, TP4)
- **모델:** Llama-7B, Llama-13B, Llama-30B (Falcon, OPT, Mixtral에서도 유사 경향 관찰)
- **트레이스:** Azure production trace(Splitwise), WildChat-1M, LMSYS-Chat-1M
- ** 출력 길이 예측기:** BERT 기반 프록시 모델(오픈소스), 평균 정확도 ~80%

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]


## 전체 요약

[[../paper-summaries/2025MICRO-summarize/chameleon-adaptive-caching-scheduling-for-many-adapter-llm-inference.md|전체 요약 보기]]
