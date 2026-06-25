---
tags: [paper, 2024, 2024ISCA, topic/cache, topic/dram, topic/gpu, topic/llm-inference]
venue: "ISCA 2024 (ACM/IEEE 51st Annual International Symposium on Computer Architecture)"
year: 2024
summary_path: "../paper-summaries/2024ISCA-summarize/splitwise-efficient-generative-llm-inference-using-phase-splitting.md"
---

# Splitwise: Efficient Generative LLM Inference Using Phase Splitting

**Venue:** ISCA 2024 (ACM/IEEE 51st Annual International Symposium on Computer Architecture)
**저자:** Pratyush Patel (University of Washington), Esha Choukse (Microsoft), Chaojie Zhang (Microsoft), Aashaka Shah (Microsoft), Íñigo Goiri (Microsoft), Saeed Maleki (Microsoft), Ricardo Bianchini (Microsoft)

## 개요

- 생성형 LLM 추론(inference)의 급속한 성장으로 고가·고전력 GPU의 대규모 배포가 요구되며, GPU 용량 부족(Chip Shortage)과 데이터센터 전력 벽(Power Wall)이 핵심 문제로 부상
- 기존 GPU 세대 간 메모리 대비 연산 스케일링 비율 불균형: NVIDIA H100은 A100 대비 **3.43×** 더 많은 TFLOPs, **1.75×** 더 높은 전력이지만, HBM 대역폭은 **1.64×** 증가에 그치고 메모리 용량은 동일(80GB) 유지 (Table I)
- LLM 추론은 두 개의 뚜렷한 특성을 가진 단계로 구성:
  - **Prompt Computation Phase**: 모든 입력 토큰이 병렬로 처리되어 첫 번째 출력 토큰 생성 → **compute-intensive** (높은 GPU util, 높은 전력)
  - **Token Generation Phase**: 출력 토큰이 순차적으로 생성 → **memory-intensive** (낮은 GPU util, 낮은 전력, 메모리 대역폭/용량 제약)
- 동일 머신에서 두 단계를 혼합 배치(mixed batching)하면 prompt가 token 실행을 방해하여 TBT(Time Between Tokens) 및 E2E 지연시간 불확실성 증가 → SLO 충족을 위해 비싼 GPU 과적재(over-provisioning) 필요
- **Insight III:** 대부분의 요청에서 E2E 시간의 대부분이 token generation phase에서 소요 (BLOOM-176B 기준, 1500 prompt token의 prompt phase와 6 token의 token phase가 동일 시간)
- **Insight VI:** Token phase는 GPU 전력의 50%를 캡핑해도 지연시간 거의 영향 없음 (700W→350W에서 TBT 거의 변화 없음)

## 방법론

### 3.1 시스템 아키텍처 (Fig. 10)

- **3개 머신 풀**: Prompt Pool, Token Pool, Mixed Pool
  - Mixed Pool: 부하 분산 시 prompt 또는 token 머신으로 동적 전환, 작업 완료 후 원래 풀로 복귀
- **CLS (Cluster-Level Scheduler)**: 머신 풀 관리 + 요청 라우팅. JSQ(Join the Shortest Queue) 스케줄링으로 요청별 prompt/token 머신 쌍 동시 할당
  - 큐 길이 기반 동적 머신 재할당: Mixed Pool 가득 차면 반대 풀 머신을 Mixed로 전환
- **MLS (Machine-Level Scheduler)**: 각 머신의 GPU 메모리 util 관리, 배치 결정, CLS에 상태 보고
  - Prompt 머신: FCFS 스케줄링, **총 2048 token 이하**로 제한 (Fig. 6a: 2048 이후 throughput 감소)
  - Token 머신: 메모리 가용량 추적, 최대한 많은 배치 → 메모리 소진 시 큐잉
  - Mixed 머신: prompt 우선 스케줄링, token phase preemption 가능 (starvation 방지를 위해 age 기반 우선순위)

### 3.2 KV-cache Transfer 최적화 (Fig. 11)

- **문제**: KV-cache가 prompt phase 완료 후 한 번에 전송(serialized)되면 TBT에 직접 영향 → large prompt에서 significant overhead
- **해결: Layer-wise Asynchronous Transfer**
  - 각 layer 계산 완료 시 해당 layer의 KV-cache를 비동기 전송, 동시에 다음 layer 계산 진행
  - MSCCL++ 라이브러리의 zero-copy one-sided put primitive 사용 → InfiniBand로 즉시 전송, token 머신의 수신 명령 불필요
- **Small vs Large Prompt 분기**: 
  - Small prompt (<512 tokens on H100): serialized transfer 사용 (오버헤드 미미)
  - Large prompt: layer-wise transfer로 전송 지연 숨김
- **결과 (Fig. 14, 15)**: Prompt computation 대비 오버헤드 **<7%**. A100 setup에서 serialized: 최대 3% E2E 오버헤드, Splitwise per-layer: **0.8%** E2E 오버헤드. 두 번째 토큰 지연시간: Splitwise **16.5%** vs serialized **64%**

### 3.3 Cluster 설계 변형 (Table V)

| 설계 | Prompt 머신 | Token 머신 | 특징 |
|------|------------|-----------|------|
| Splitwise-AA | DGX-A100 | DGX-A100 | 동일 하드웨어, 저비용 |
| Splitwise-HH | DGX-H100 | DGX-H100 | 동일 하드웨어, 고성능 |
| Splitwise-HA | DGX-H100 | DGX-A100 | 이질적, Prompt 고성능 + Token 저비용 |
| Splitwise-HHcap | DGX-H100 (전력캡핑) | DGX-H100 (50% 전력캡) | 전력 최적화 |

- **Splitwise-HA의 근거 (Insight VII):** Token phase는 compute capability에 덜 민감 → A100이 더 나은 Perf/W 및 Perf/$ 효율
- **Splitwise-HHcap의 근거 (Insight VI):** Token phase는 50% 전력 캡핑해도 지연시간 거의 영향 없음

### 3.4 Provisioning 프레임워크

- 이벤트 기반 클러스터 시뮬레이터로 설계 공간 탐색
- 입력: 클러스터 설계, LLM 성능 모델, 요청 트레이스, SLO(Table VI: P50/P90/P99 TTFT/TBT/E2E 기준), 제약 조건(throughput), 최적화 목표(cost/power/throughput)
- 예시 (Fig. 12): Splitwise-HH의 coding workload에서 70 RPS 달성 시 **27 prompt + 3 token 머신**이 비용 최적점

## 핵심 기여

1. **Phase Splitting으로 LLM 추론 효율 대폭 향상**: Prompt와 Token 단계를 분리하여 각각에 최적화된 리소스 관리로 **1.4×~2.35× throughput 향상**
2. **비용·전력 동시 최적화 가능**: Splitwise-HHcap은 동일 throughput을 **25% 낮은 전력**으로, Splitwise-AA는 **1.4× throughput을 20% 낮은 비용**으로 달성
3. **KV-cache Transfer 오버헤드 최소화**: Layer-wise 비동기 전송으로 E2E 영향 **<1%**, 사용자 인지 불가능한 수준
4. **강건성(robustness)**: 다른 모델, 다른 워크로드 패턴으로 배포된 클러스터에서도 성능 저하 없이 적응 가능 → 실무적 배포 가치 높음
5. **GPU 세대 간 불균형 활용**: H100의 높은 연산을 prompt에, A100의 높은 메모리 대비 연산 비율을 token에 배치하여 하드웨어 특성과 워크로드 특성의 매칭 최적화

## 주요 결과

| 항목 | 세부사항 |
|------|---------|
| **구현 플랫폼** | vLLM 위에 Splitwise 구현 (오픈소스) |
| **하드웨어** | Microsoft Azure: 2× DGX-A100, 2× DGX-H100 VM |
| **통신 라이브러리** | MSCCL++ (GPU-driven communication stack) |
| **인터커넥트** | InfiniBand (A100: 200Gbps, H100: 400Gbps) |
| **시뮬레이터** | 이벤트 기반, 오픈소스 (SplitwiseSim) |
| **성능 모델** | Piece-wise linear, MAPE <3% (80:20 train/test) |
| **모델** | BLOOM-176B (70 layers, 14336 hidden, 112 heads), Llama2-70B (80 layers, 8192 hidden, 32 heads) |
| **트레이스** | Azure 프로덕션 트레이스 (2023.11.11, coding + conversation) |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]


## 전체 요약

[[../paper-summaries/2024ISCA-summarize/splitwise-efficient-generative-llm-inference-using-phase-splitting.md|전체 요약 보기]]
