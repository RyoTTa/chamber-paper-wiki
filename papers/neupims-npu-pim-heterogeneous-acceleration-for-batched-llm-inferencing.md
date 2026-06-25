---
tags: [paper, 2024, 2024ASPLOS, topic/dram, topic/gpu, topic/llm-inference, topic/pim, topic/rowhammer]
venue: "ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS) 2024"
year: 2024
summary_path: "../paper-summaries/2024ASPLOS-summarize/neupims-npu-pim-heterogeneous-acceleration-for-batched-llm-inferencing.md"
---

# NeuPIMs: NPU-PIM Heterogeneous Acceleration for Batched LLM Inferencing

**Venue:** ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS) 2024
**저자:** Guseul Heo, Sangyeop Lee, Jaehong Cho, Hyunmin Choi, Sanghyeon Lee (KAIST), Hyungkyu Ham†, Gwangsun Kim† (POSTECH), Divya Mahajan§ (Georgia Institute of Technology), Jongse Park (KAIST)

## 개요

- modern transformer 기반 Large Language Models (LLMs)은 decoder block들로 구성되며, 각 블록은 QKV 생성, Multi-Head Attention (MHA), Feed-Forward Networks (FFN)의 세 가지 핵심 컴포넌트를 포함
- **GEMM vs GEMV 연산 특성**: batched processing 시 QKV 생성과 FFN은 compute-intensive한 GEMM (GEneral Matrix Multiplication) 연산, MHA는 bandwidth-heavy한 GEMV (GEneral Matrix-Vector Multiplication) 연산 필요
- **NPU의 한계**: GPU/TPU와 같은 ML 가속기(NPU)는 GEMM에 최적화되어 있으나, GEMV의 낮은 arithmetic intensity로 인해 NPU의 컴퓨팅 리소스가 충분히 활용되지 못함 (utilization < 40%)
- **PIM의 한계**: Processing-in-Memory (PIM) 기술은 GEMV에 효율적이지만, GEMM을 처리할 만큼의 컴퓨팅 능력이 부족
- **기존 NPU+PIM 통합의 문제**: 현재 PIM은 "blocked" 모드로 동작하여 NPU와 PIM이 동시에 활성화될 수 없음 (serial execution → 리소스 under-utilization)
- **LLM 특성상 필수적**: GPT4, LLaMA와 같은 SOTA LLM들의 핵심은 decoder block 스택이며, summarization phase(compile-bound)와 generation phase(memory-bound)가 번갈아 실행되어 homogeneous 플랫폼에서는 높은 리소스 utilization 달성 어려움
- **GPU 리소스 utilization 분석**: RTX 3090, A100에서 GPT-NeoX, LLaMa2, OPT, MPT 모델 테스트 시 compute utilization consistently < 40%, bandwidth utilization更是低效적

## 방법론

### 3.1. PIM 마이크로아키텍처: Dual Row Buffer

- **기존 PIM의 한계**: 단일 row buffer가 메모리 읽기/쓰기와 PIM 가속기용으로 이중 사용되어 동시에 실행 불가
- **NeuPIMs 뱅크 아키텍처**: 
  - MEM row buffer: 일반 메모리 읽기/쓰기 전용
  - PIM row buffer: GEMV 연산 전용
  - 두 row buffer는 독립적인 데이터 경로를 가지며 DRAM의 다중 row activation 속성을 활용
- **커맨드 인터페이스 확장**:
  - PIM_HEADER: 가변 차원 GEMV 연산 지원을 위한 차원 정보 전달
  - PIM_GEMV: 여러 dot-product를 동시에 제어하는 복합 커맨드 (커맨드 트래픽 감소)
  - PIM_PRECHARGE: PIM row buffer 전용 precharge 커맨드

### 3.2. 메모리 컨트롤러: Interleaved Scheduling

- **메모리/PIM 커맨드 인터리빙**: 메모리 읽기/쓰기 커맨드와 PIM 커맨드를 효율적으로 인터리빙하여 C/A bus 대역폭 병목 방지
- **PIM 커맨드 우선순위**: PIM 커맨드의 발행 지연이 메모리 커맨드보다 크므로 우선순위 부여
- **DRAM timing parameter 준수**: tRP=14, tRCD=14, tRAS=34, tRRD_L=6, tWR=16, tCCD_S=1, tCCD_L=2, tREFI=3900, tRFC=260, tFAW=30

### 3.3. Sub-batch Interleaving 스케줄링

- **MHA 레이어 오버랩**: Multi-head attention은 head 수준 병렬성을 가지며, PIM에서 logit/attend 연산과 NPU에서 softmax 연산을 겹칠 수 있음
- **Sub-batch 분할**: 하나의 배치를 두 개의 독립적인 sub-batch로 분할
  - Sub-batch 1의 GEMM 연산과 Sub-batch 2의 GEMV 연산을 동시 실행
  - 두 sub-batch 간 데이터 의존성 없음으로 병렬 실행 가능
- **실행 타임라인 비교**:
  - Serialized: N × per-decoder-block time
  - Sub-batch Interleaving: (N-1) × per-sub-batch partial time + single decoder-block time

### 3.4. MHA 레이어 지연 시간 추정 (Algorithm 1)

- **입력**: seq_len (요청의 시퀀스 길이)
- **파라미터**: E (모델 임베딩 크기), L_tile (PIM tile당 GEMV 지연), L_GWRITE (global buffer 쓰기 지연), P_DRAM (DRAM 페이지 크기), B_chnl (채널당 PIM 뱅크 수), N_head (헤드 수)
- **출력**: L_MHA (추정 MHA 지연 시간)
- **Key-T×Query GEMV**: N_tiles = (seq_len/B_chnl) × (E/P_DRAM)
- **Logits×Value GEMV**: N_tiles = ((E/N_head)/B_chnl) × ((seq_len/P_DRAM) × N_head)

### 3.5. 채널 로드 밸런싱 (Algorithm 2: Greedy Min-Load Bin Packing)

- 가장 긴 시퀀스 길이의 요청부터 가장 적재량이 적은 PIM 채널에 순차적으로 할당
- 각 채널의 총 부하를 MHA 지연 시간 추정으로 계산
- 채널 간 실행 시간 불균형 최소화

### 3.6. Sub-batch 분할 알고리즘 (Algorithm 3)

- 각 채널의 요청을 두 개의 sub-batch로 균등하게 분할
- 홀수 개 요청 시 round-robin 방식으로 분배하여 균형 유지

## 핵심 기여

- **핵심 Contribution**: NPU와 PIM의 이종 가속을 통해 LLM 추론 처리량을 획기적으로 향상시키는 NeuPIMs 시스템 제안
- **성능 향상**: GPU-only 대비 3×, NPU-only 대비 2.4× throughput improvement 달성
- **리소스 Utilization**: NPU utilization 28%→65%, PIM utilization 17%→26%로 대폭 향상
- **실용적 배포**: Dual row buffer와 sub-batch interleaving을 통해 practical한 PIM의 LLM 추론 시스템 통합 첫 번째 단계
- **향후 전망**: Tensor parallelism 및 pipeline parallelism과의 호환성 확인, 다양한 LLM 모델에 대한 일반화 가능성 입증

## 주요 결과

- **하드웨어 사양 (Table 2)**:
  - NPU: 8개의 systolic array (128×128), 8개의 SIMD vector unit
  - HBM: 32 채널, 채널당 32 뱅크, 1GHz, 1GB 용량
  - Bank group당 4 뱅크, 페이지 크기 1KB
- **시뮬레이터**: ONNXim (오픈소스 NPU 시뮬레이터) + DRAMsim3 (PIM 시뮬레이터) 결합
- **소스코드**: https://github.com/casys-kaist/NeuPIMs
- **프로토타입**: 멀티 칩렛 설계, 8개 systolic array 각각 SIMD vector unit과 통합

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]


## 전체 요약

[[../paper-summaries/2024ASPLOS-summarize/neupims-npu-pim-heterogeneous-acceleration-for-batched-llm-inferencing.md|전체 요약 보기]]
