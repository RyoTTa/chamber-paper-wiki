---
tags: [paper, 2026, 2026NSDI, topic/cache, topic/gpu, topic/llm-inference]
venue: "23rd USENIX Symposium on Networked Systems Design and Implementation (NSDI '26)"
year: 2026
summary_path: "../paper-summaries/2026NSDI-summarize/fastserve-iteration-level-preemptive-scheduling-for-large-language-model-inference.md"
---

# FastServe: Iteration-Level Preemptive Scheduling for Large Language Model Inference

**Venue:** 23rd USENIX Symposium on Networked Systems Design and Implementation (NSDI '26)
**저자:** Bingyang Wu, Yinmin Zhong, Zili Zhang, Shengyu Liu, Fangyue Liu, Yuanhang Sun, Gang Huang, Xuanzhe Liu, Xin Jin (Peking University)

## 개요

- LLM (ChatGPT 등) 기반 대화형 AI 애플리케이션은 낮은 추론 지연 시간(low inference latency)을 요구함.
- 기존 LLM 서빙 시스템 (Orca, vLLM)은 FCFS + run-to-completion 방식으로 작업을 처리.
- LLM 추론의 autoregressive 특성: 입력 + 이전 출력 토큰을 기반으로 한 번에 한 토큰씩 생성. 출력 길이(output length)를 사전에 알 수 없어 작업 실행 시간이 가변적임.
- **Head-of-line blocking 문제:** 긴 작업(long job)이 스케줄되면 짧은 작업(short job)들이 대기해야 함. 실제 워크로드(ShareGPT, Alpaca)에서 queuing delay가 end-to-end 지연 시간의 최대 90%를 차지함 (Figure 1).
- 실행 시간(execution time) 최적화만으로는 부족하며, 핵심 병목은 대기 지연(queuing delay).
- Chunked prefill (Sarathi-Serve)은 긴 입력을 분할하여 부분적으로 완화하지만, 더 빈번한 병목인 긴 출력 문제를 해결하지 못하고, 추가 메모리 접근으로 TTFT 성능을 저하시킴.

## 방법론

### 3.1. Semi Information-Agnostic 설정

- 일반 MLFQ는 작업 크기에 대한 정보가 없는 정보-비의존적(information-agnostic) 환경에서 지연 시간을 최소화하는 고전적 방식.
- LLM 추론은 **semi information-agnostic**: 출력 길이는 알 수 없지만, 입력 길이는 알 수 있음.
- 입력 길이는 첫 출력 토큰 생성 시간(prefill 시간)을 결정하며, 이는 이후 decoding 시간보다 훨씬 큼 (Figure 5). 예: OPT 2.7B, A100 GPU, input length=1024에서 prefill ≈ 0.08s, decoding ≈ 0.005s.

### 3.2. 기존 MLFQ의 한계

- 기존 MLFQ: 모든 새 작업이 최우선 큐(Q₁)로 진입. quantum 소진 시 하위 큐로 강등.
- LLM의 긴 prefill 시간 때문에 작업이 첫 번째 iteration을 완료하기도 전에 quantum을 소진할 수 있음.
  - 이때 선점하면 불필요한 재계산(recomputation) 발생.
  - 선점하지 않으면 head-of-line blocking 재발.
- **Dilemma:** prefill 시간이 긴 작업을 MLFQ의 최상위 큐에 넣는 것은 비효율적.

### 3.3. Skip-Join 동작 방식

1. **초기 큐 진입 (Skip-Join):**
   - 경량 프로파일링으로 prefill 시간(t_init) 예측.
   - `q_i ≥ t_init`를 만족하는 가장 높은 우선순위 큐(Q_i)로 바로 진입.
   - t_init보다 작은 quantum을 가진 상위 큐들을 건너뜀(skip) → 불필요한 강등 방지.

2. **강등 (Demotion):**
   - quantum 소진 시, 현재 우선순위와 다음 iteration 시간 기반으로 η배 낮은 큐로 강등.
   - 하위 큐의 quantum은 상위 큐의 2배로 설정.

3. **기아 방지 (Starvation Prevention):**
   - `α` 파라미터(사용자 정의 SLO 기반, 기본 300ms) 이상 기아 상태인 작업을 최우선 큐(Q₁)로 승격.
   - Tail latency 악화 방지.

4. **알고리즘 (Algorithm 1):**
   - `init_time = P.getNextIterTime(job)` — 프로파일러로 prefill 시간 예측
   - `p_job = min i, s.t. qi ≥ init_time` — 적절한 큐 선택
   - 강등: `Q_p.pop(job), Q_{p+η}.push(job)`
   - 승격: `Q_p.pop(job), Q_1.push(job)`

### 3.4. 실행 예시 (Figure 7)

- 3개 작업(J₁, J₂, J₃) 동시 도착. J₁은 긴 입력+짧은 출력, J₂와 J₃는 짧음.
- FCFS: J₁이 block → 평균 latency 4.23
- 기존 MLFQ: J₁이 Q₁ → prefill 중 quantum 소진 → head-of-line blocking → 평균 latency 5.0
- **Skip-Join MLFQ:** J₁을 낮은 큐에 직접 배치 → J₂, J₃ 먼저 처리 → 평균 latency 3.3 (SRPT oracle 3.0에 근접)

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1. 메모리 압력 문제

- 선점형 스케줄러는 실행 중인 작업 + 선점된 작업들의 KV cache를 모두 유지해야 함.
- OPT-175B: 단일 요청(input 512 tokens)에 KV cache 2.3GB, 토큰당 4.6MB 추가.
- Skip-Join MLFQ의 피크 KV cache 메모리는 FCFS 대비 최대 **7배** 큼 (Figure 8, OPT 2.7B).

### 4.2. Strawman 솔루션의 한계

1. **새 작업 지연 (defer):** GPU 메모리 부족 시 새 작업 실행 지연 → 다시 head-of-line blocking.
2. **Kill & Recompute:** 저우선순위 작업 종료 후 재계산 → 자원 낭비 + live-lock 가능성.

### 4.3. Proactive Swapping

- **핵심 통찰:** KV tensor는 해당 작업이 스케줄될 때만 GPU 메모리에 있으면 됨.
- **동작 방식:**
  - GPU 메모리 압력 ↑ → 저우선순위 작업의 KV cache를 host memory로 오프로드.
  - 해당 작업 스케줄 직전에 GPU로 다시 업로드.
- **Latency hiding:**
  - 비동기 메모리 작업 + pipelining으로 통신과 계산 중첩 (Figure 9).
  - Reactive swapping(작업 종료 후 swap)과 달리, Proactive는 J₁ 실행 중에 J₂의 swap을 미리 수행.

### 4.4. 스와핑 순서 결정: ENST (Estimated Next Scheduled Time)

- **ENST(i) = min(T_promote(i), T_execute(i))**
  - T_promote(i): 기아 방지에 의해 승격될 시간
  - T_execute(i, j) = Σ q_k (i.priority < k ≤ j.priority): 작업 j가 작업 i와 동일 큐로 강등될 때까지 실행 시간
  - T_execute(i) = (1/B) × Σ T_execute(i, j) (j: i보다 높은 우선순위 작업들)
  - B: 최대 배치 크기
- ENST가 가장 큰 작업 → 먼저 swap out
- ENST가 가장 작은 작업 → 먼저 swap in
- 버스트 처리: 새 작업(고우선순위) 유입에 대비해 유휴 KV cache 슬롯 일부 예약.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]


## 전체 요약

[[../paper-summaries/2026NSDI-summarize/fastserve-iteration-level-preemptive-scheduling-for-large-language-model-inference.md|전체 요약 보기]]
