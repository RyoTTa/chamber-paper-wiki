---
tags: [paper, 2025, 2025MICRO, topic/dram, topic/gpu, topic/llm-inference]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO) 2025"
year: 2025
summary_path: "../paper-summaries/2025MICRO-summarize/streamtensor-dataflow-accelerators-for-llms.md"
---

# StreamTensor: Make Tensors Stream in Dataflow Accelerators for LLMs

**Venue:** IEEE/ACM International Symposium on Microarchitecture (MICRO) 2025
**저자:** Hanchen Ye (University of Illinois Urbana-Champaign), Deming Chen (Inspirit IoT, Inc. / University of Illinois Urbana-Champaign)

## 개요

- LLM의 자기회귀(autoregressive) 특성으로 인해 디코딩 단계가 메모리에 과도하게 의존하며, 기존 Von Neumann 아키텍처는 메모리 병목(memory wall) 문제로 성능 제한
- 기존 데이터플로우 가속기 컴파일러들은 커널 간 상호 의존성(inter-kernel correlation), 외부 메모리 접근 관리, 버퍼 최적화 문제를 해결하지 못함
- 스트리밍 방식으로 중간 결과를 전달하면 효율이 크게 향상되지만, 기존 접근법은 다음 4가지 함정(pitfall)에 직면:
  - **Pitfall 1: 커널 간 상호 의존성** - 파이프라인 실행 시 커널 간 레이턴시 균형 및 병렬화 전략 정렬 필요
  - **Pitfall 2: 외부 메모리 접근** - DMA의 레이턴시 오버랩, 데이터 레이아웃, 패킹/벡터화 문제
  - **Pitfall 3: 스트림 기반 커널 퓨전** - 프로듀서/커SUMER 간 호환되지 않는 스트림 레이아웃
  - **Pitfall 4: FIFO 크기 결정** - 오버플로/언더플로우로 인한 데드락 및 성능 저하
- 기존 프레임워크(Allo, DFX, Stream-HLS)는 수동 설계가 필요하거나 제한된 유연성으로 인해 실제 LLM 배포에 어려움

## 방법론

### 3.1. itensor 타입 시스템

- **반복적 텐서(iterative tensor) 타입**: 데이터 타입, 반복 공간(iteration space), 반복 매핑(iteration map)을 인코딩
  - 기존 텐서 타입은 메모리 매핑 접근만 지원하지만, itensor는 스트림 접근 패턴을 명시적으로 표현
  - 프로듀서/컨슈머의 itensor 타입이 일치하면 직접 스트리밍 연결 가능
  - 타입 불일치 시 스트림 레이아웃 변환기(converter) 자동 삽입

- **stream 타입**: 버퍼화(bufferization) 후 하드웨어 FIFO를 나타내는 타입
  - itensor에서 stream으로 변환 시 스트림 레이아웃 정보 제거
  - 데이터플로우 컴포넌트 생성 및 최적화는 itensor 레벨 IR에서 수행

### 3.2. 컴파일 파이프라인

- **Linalg to Dataflow 변환**: MLIR의 Linalg 연산을 커널과 태스크로 변환
  - 반복 루프 네스트를 커널로 변환
  - 텐서 입출력을 커널 경계에서 itensor로 변환하여 DMA 자동 생성

- **데이터플로우 커널 퓨전**: 프로듀서/컨슈머 커널 간 스트림 연결
  - itensor 타입 비교로 호환성 확인
  - 비호환 시 최소 핑퐁 버퍼 크기의 레이아웃 변환기 자동 생성
  - 팩(pack)/언팩(unpack) 및 위دن(widen) 연산으로 외부 메모리 대역폭 최적화

### 3.3. FIFO 크기 결정

- **토큰 행동 모델**: piecewise 함수로 커널의 토큰 생성/소비 패턴 모델링
  - delay 변수를 통해 커널 간 토큰 전달 지연 시간 표현
  - max_token 계산으로 최소 FIFO 크기 결정

- **선형 계획법(LP) 공식화**:
  - 목적 함수: 모든 엣지의 delay 합 최소화
  - 제약 조건: 커널 쌍 간 최대 누적 delay 보장
  - 리소스 제약 불필요 (퓨전 시 칩 온 리소스 제한으로 이미 보장)

## 핵심 기여

- **핵심 기여**: itensor 타입 시스템을 통한 스트림 기반 데이터플로우 가속기 자동 생성 및 최적화 프레임워크 제안
- **성능 향상**: FPGA 기반 LLM 가속기에서 Allo 대비 0.76x 지연 시간, DFX 대비 0.52x 지연 시간 달성
- **에너지 효율**: GPU 대비 최대 1.99x 향상 (Qwen 모델)
- **유연성**: GPT-2, Qwen, Llama, Gemma 등 다양한 LLM에 성공적으로 적용
- **의의**: 데이터플로우 아키텍처의 프로그래밍 생산성과 성능을 동시에 향상시키는 체계적인 컴파일러 프레임워크로, 향후 확장 가능한 데이터플로우 컴파일 연구의 기반 마련

## 주요 결과

- **구현 언어**: C++ (HLS), MLIR 기반 컴파일러
- **프레임워크**: MLIR compilation framework 기반
- **프론트엔드**: Torch-MLIR을 통한 PyTorch 모델 입력
- **하드웨어 타겟**: AMD U55C FPGA (16nm, 250MHz)
- **컴파일 도구**: Vitis 2024.1
- **양자화**: W4A8 (4비트 가중치, 8비트 활성화)
- **온칩 메모리**: 41MB
- **오프칩 메모리**: 16GB HBM (460GB/s)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]


## 전체 요약

[[../paper-summaries/2025MICRO-summarize/streamtensor-dataflow-accelerators-for-llms.md|전체 요약 보기]]
