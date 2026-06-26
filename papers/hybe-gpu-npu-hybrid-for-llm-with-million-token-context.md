---
tags: [paper, 2025, 2025ISCA, topic/cache, topic/dram, topic/gpu, topic/llm-inference]
venue: "International Symposium on Computer Architecture (ISCA) 2025"
year: 2025
summary_path: "../paper-summaries/2025ISCA-summarize/hybe-gpu-npu-hybrid-system-for-efficient-llm-inference-with-million-token-context-window.md"
---

# Hybe: GPU-NPU Hybrid System for Efficient LLM Inference with Million-Token Context Window

**Venue:** International Symposium on Computer Architecture (ISCA) 2025
**저자:** Seungjae Moon*, Junseo Cha*, Hyunjun Park, Joo-Young Kim (HyperAccel) (* equal contribution)

## 개요

- LLM 추론의 두 가지 단계인 prefill stage(GEMM 연산, compute-intensive)와 decode stage(GEMV 연산, memory-intensive) 간의 계산 불균형이 하드웨어 활용도를 심각하게 저하시킴
- GPU는 풍부한 병렬 코어를 보유하여 prefill stage에서 높은 성능을 발휘하지만, decode stage에서 코어 활용도가 크게 떨어져 전력 소비 비효율이 발생
- 컨텍스트 윈도우 크기의 급격한 증가로 KV 캐시 크기가 모델 파라미터를 초과하는 상황 발생: Llama-3 8B의 경우 모델 파라미터 16GB 대비 KV 캐시가 최대 128GB(1M 토큰)에 달함
- KV 캐시 크기 공식: KVcache = 2 × l × N × nlayer × nhead × dhead × b (컨텍스트 윈도우 l, 배치 크기 N에 비례)
- 배치 추론이 KV 캐시 용량 제한으로 인해 사실상 불가능해지며, prefill-decode 간 계산 불균형이 더욱 악화
- 기존 GPU-GPU 하이브리드 시스템(Splitwise)은 A100 GPU를 decode stage에 활용하지만, GPU 아키텍처 자체의 비효율로 인해 15% 효율 개선에 그침

## 방법론

### 3.1. 전체 구조
- Hybe GPU(NVIDIA H100)가 prefill stage를 담당하고, Hybe NPU(5개)가 decode stage를 담당
- GPU와 NPU는 PCIe Gen 5를 통해 연결되고, 다중 스레딩을 통해 독립적이면서 병렬적으로 실행
- 모델 병렬성(model parallelism) 지원: 어텐션은 head-wise, FFN은 column-wise로 모델 파라미터를 분할
- NPU 간 통신은 부분 결과를 전송하면서 다음 부분 결과를 계산하는 방식으로 통신 대역폭 숨김

### 3.2. Hybe NPU 아키텍처
- Samsung 4nm 공정, 1.0GHz 작동, 칩 면적 0.84mm² (HBM3 PHY 포함 시 83.2mm²)
- 핵심 구성요소:
  - **Controller (CTRL)**: RISC 프로세서 기반, 명령어 파싱 및 Out-of-Order 실행 지원
  - **DMA**: HBM에서 가중치 및 KV를 버스트 모드로 읽기, reshape 지원
  - **Matrix Processing Unit (MPU)**: 32개 MAC 트리로 구성, GEMV 연산 최적화, HBM 대역폭과 정확히 일치하는 연산 용량(3.35 TFLOPS FP16)
  - **Vector Processing Unit (VPU)**: softmax, 정규화 등 비-GEMV 연산 처리, FP32 정밀도 유지
  - **Sampling Unit (SMP)**: Bitonic sorter와 top-kp 모듈로 토큰 샘플링
  - **Network Unit (NET)**: NPU 간 AllGather 동기화 지원

### 3.3. Fine-grained KV Transmission (FGKVT)
- 기존 방식: 레이어 단위로 전체 KV를 GPU→NPU로 전송 → GPU에 큰 메모리 footprint 유지
- FGKVT 방식: 어텐션 연산을 균일한 헤드 수의 그룹으로 분할, 부분 QKV를 온더플라이로 NPU에 전송
- GPU에서 QKV 생성과 동시에 KV 전송을 시작하여 통신 지연 시간을 어텐션 연산으로 숨김
- 컨텍스트 윈도우가 증가할수록 KV 전송 크기는 선형적으로 증가하지만, 어텐션의 계산 복잡도는 지수적으로 증가 → 전송 지연이 완전히 숨겨짐
- 데이터 리셰이핑: GPU-NPU 간 다른 메모리 매핑을 런타임에서 리셰이핑하여 최소 통신 지연 달성

### 3.4. Stage-wise Pipelining
- Naive pipelining: GPU와 NPU의 prefill/decode 지연이 같을 때만 유효, 입출력 비율 편차 시 idle 발생
- Prefill overloading: 입출력 비율이 감소할 때 GPU가 유휴 상태가 되는 것을 방지 - 다음 요청의 prefill을 조기 시작
- Prefill offloading: 출력 비율 감소 시 NPU가 유휴 상태가 되는 것을 방지 - NPU가 다음 요청의 prefill stage를 일부 처리
- Hybe scheduler가 입출력 비율을 동적으로 판단하여 overloading과 offloading을 결합 → 모든 idle 시간 제거

## 핵심 기여

- million 토큰 컨텍스트 윈도우를 가진 LLM 추론의 핵심 문제인 prefill-decode 계산 불균형을 하이브리드 GPU-NPU 아키텍처로 해결
- 경량 NPU를 디코딩 전용으로 설계하여 GPU 대비 55.7% 높은 메모리 대역폭 활용도, 69.0% 높은 코어 활용도 달성
- Fine-grained KV transmission과 stage-wise pipelining을 통해 KV 캐시 메모리 요구량 대폭 절감 및 하드웨어 활용도 극대화
- Phi-3(100K 토큰)에서 2.1× 속도 향상, Llama-3(1M 토큰)에서 3.9× 에너지 효율 향상 달성
- 기존 GPU 전용 시스템의 한계를 극복하고, 대규모 컨텍스트 LLM 추론의 실용적 솔루션 제시

## 주요 결과

- GPU: NVIDIA H100 SXM (80GB HBM3, 3.35 TB/s 대역폭, 1,979 TFLOPS FP16)
- GPU 소프트웨어: vLLM 라이브러리의 CUDA 커널 수정, cudaMemcpyAsync()를 활용한 KV 전송
- NPU: SystemVerilog 기반 RTL 구현, Synopsys VCS로 시뮬레이션
- NPU 기술: Samsung 4nm 공정, HBM3 5스택 (80GB, 3.35 TB/s), 면적 0.84mm², 소비전력 0.29W
- MPU 면적: 0.22mm², MPU 전력: 0.12W (칩 전력의 41.4%)
- NPU 런타임: OpenCL 기반, 이벤트 기반 스케줄링으로 Hybe scheduler 지원
- GPU-NPU 통신: PCIe DMA 트랜스퍼 시뮬레이션, pinned memory 활용 zero-copy 동작

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]


## 전체 요약

[[../paper-summaries/2025ISCA-summarize/hybe-gpu-npu-hybrid-system-for-efficient-llm-inference-with-million-token-context-window.md|전체 요약 보기]]
