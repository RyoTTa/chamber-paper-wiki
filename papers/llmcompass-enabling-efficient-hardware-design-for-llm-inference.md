---
tags: [paper, 2024, 2024ISCA, topic/dram, topic/gpu, topic/llm-inference]
venue: "51st Annual International Symposium on Computer Architecture (ISCA 2024)"
year: 2024
summary_path: "../paper-summaries/2024ISCA-summarize/llmcompass-enabling-efficient-hardware-design-for-large-language-model-inference.md"
---

# LLMCompass: Enabling Efficient Hardware Design for Large Language Model Inference

**Venue:** 51st Annual International Symposium on Computer Architecture (ISCA 2024)
**저자:** Hengrui Zhang, August Ning, Rohan Baskar Prabhakar, David Wentzlaff (Princeton University)

## 개요

- LLM (GPT-3 175B 등)의 배포에 막대한 하드웨어 비용이 필요: GPT-3 추론을 위한 DGX A100 노드는 $100,000 USD 이상의 비용이 발생하며, 각 A100 GPU는 54B 트랜지스터와 80GB HBM을 탑재
- LLM 하드웨어 설계를 평가할 수 있는 도구가 부족: Roofline 모델은 빠르지만 부정확하고, cycle-level 시뮬레이터는 정확하지만 느림; FPGA 에뮬레이션은 정확하지만 막대한 공학적 노력이 필요
- GPT-3 175B 추론을 위한 최소 하드웨어: 5개 이상의 NVIDIA A100 GPU가 모델 파라미터(half precision)를 저장하기 위해 필요하며, 이러한 높은 비용이 LLM의 대중화를 저해
- 기존 하드웨어 평가 도구들은 빠르고, 아키텍처적으로 설명 가능하고, 성능 최적화되고, 비용 인식적인 요구사항을 모두 충족하지 못함
- LLM 추론의 특성(autoregressive 토큰 생성, 대규모 파라미터)이 하드웨어 설계에 미치는 영향이 아직 충분히 이해되지 않음

## 방법론

### 3.1. 하드웨어 설명 템플릿 (Hardware Description Template)

- **System:** 디바이스 간 디바이스-디바이스 인터커넥트(NVLink 등)로 연결된 여러 디바이스로 구성 (예: DGX 노드)
- **Device:** 여러 코어, 공유 글로벌 버퍼, 오프칩 메인 메모리를 가짐 (예: GPU). 글로벌 버퍼는 코어, 디바이스 간 인터커넥트, 메인 메모리에 연결
- **Core:** 여러 레인이 로컬 버퍼를 공유 (예: SM). 로컬 버퍼는 온칩 인터커넥트를 통해 글로벌 버퍼에 연결
- **Lane:** 벡터 유닛, systolic array, 레지스터, 제어 로직을 독립적으로 보유
- NVIDIA A100, AMD MI210, Google TPUv3 세 가지 상용 하드웨어로 검증

### 3.2. 성능 모델 (Performance Model)

- LLM 계산 그래프와 하드웨어 설명을 입력으로 받아 throughput/latency 보고서 생성
- Tile-by-tile 시뮬레이션: dense 연산자의 구조적이고 예측 가능한 compute/memory access 패턴을 활용
- Mapper가 parameter search를 통해 최적의 mapping 및 scheduling scheme을 자동 탐색
- 실제 하드웨어 대비 평균 10.9% latency 오류율(다양한 연산자/입력 크기), LLM 추론 기준 평균 4.1% 오류율 달성
- 4-A100 GPU 노드에서 GPT-3 175B 추론 시뮬레이션이 상용 하드웨어에서 16분 이내 완료 (26,400회 mapper parameter search 포함)

### 3.3. 면적 및 비용 모델 (Area and Cost Model)

- 트랜지스터 수 및 다이 면적을 오픈소스 디자인, tape-out, 생성기에서 추정
- 로컬/글로벌 버퍼는 SRAM 캐시로 모델링하고 CACTI로 면적 도출 후 7nm 공정으로 스케일링
- 메모리 및 디바이스 간 인터커넥트는 A100/MI210 다이 사진에서 추정한 PHY/컨트롤러 면적 기반
- GA100 다이 면적 오류율 5.1%, Aldebaran 다이 면적 오류율 8.1% 달성
- wafer 비용 모델링을 통한 다이당 비용 추정, DDR/HBM2e 메모리 비용 포함

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1. 컴퓨팅 시스템 설계

- **Prefill vs Decoding 차이:** Prefill은 compute-bound, Decoding은 IO-bound (메모리 대역폭에 민감)
- 소수의 큰 코어 vs 다수의 작은 코어 비교: 큰 systolic array/벡터 유닛은 면적 효율적이지만 utilization이 어려움
- A100 대비 컴퓨팅 능력을 절반으로 줄여도 여전히 95.3% 성능 달성 가능
- Design E(가장 큰 코어): prefill latency 12.4% 증가, decoding latency 1.9% 증가, 다이 면적 7.7% 감소

### 4.2. 메인 메모리

- Decoding은 prefill보다 메모리 대역폭에 훨씬 더 민감
- 대역폭 800→2000 GB/s: prefill 14.3% 개선, decoding 1.88x 속도 향상
- 추가 대역폭(3200 GB/s): prefill 3.5% 추가 개선, decoding 26% 추가 개선

### 4.3. 로컬/글로벌 버퍼

- 로컬 버퍼 64KB→192KB: prefill 18.0% 개선, 면적 5.8% 증가
- 로컬 버퍼 192KB→1024KB: prefill 0.2% 개선만 (diminishing returns), 면적 28.8% 증가
- 192KB는 FP16에서 128×128×128 행렬 곱셈에 충분한 크기 (NVIDIA A100 설계 선택에 대한 시사점)
- Decoding은 버퍼 크기 증가에 거의 영향을 받지 않음 (IO-bound)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]


## 전체 요약

[[../paper-summaries/2024ISCA-summarize/llmcompass-enabling-efficient-hardware-design-for-large-language-model-inference.md|전체 요약 보기]]
