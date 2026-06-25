---
tags: [paper, 2021, 2021ISCA, topic/cache, topic/dram, topic/llm-inference, topic/near-data-processing]
venue: "ISCA 2021 (48th Annual IEEE/ACM International Symposium on Computer Architecture)"
year: 2021
summary_path: "../paper-summaries/2021ISCA-summarize/reduct-near-cache-compute-for-dnn-inference-on-multi-core-cpus.md"
---

# REDUCT: Keep it Close, Keep it Cool! Efficient Scaling of DNN Inference on Multi-core CPUs with Near-Cache Compute

**Venue:** ISCA 2021 (48th Annual IEEE/ACM International Symposium on Computer Architecture)
**저자:** Anant V. Nori (Intel Labs, Bangalore), Rahul Bera (ETH Zurich), Shankar Balachandran (Intel Labs, Bangalore), Joydeep Rakshit (Intel Labs, Bangalore), Om J. Omer (Intel Labs, Bangalore), Avishaii Abuhatzera (Intel Corporation), Belliappa Kuttanna (Intel Corporation), Sreenivas Subramoney (Intel Labs, Bangalore)

## 개요

- DNN 추론은 데이터센터와 엣지 모두에서 광범위하게 사용되며, 최적의 하드웨어를 구축하기 위한 경쟁이 계속됨
- 범용 멀티코어 CPU는 DNN 추론에 고유한 장점을 제공하나, 기존 CPU 파이프라인 설계는 단일 스레드 성능 최적화에 초점 → 데이터 병렬 DNN 워크로드에 비효율
- Wide Out-of-Order(OoO) CPU 파이프라인의 Front-End(Fetch, Decode, RAT, Dispatch) 단계가 전체 전력의 **59%** 이상 소비
- 기존 CPU의 모놀리식한 코어 중심 구조로 인해 다양한 Ops/Byte(DNN 프리미티브) 요구사항에 비효율적
- **Convolution(행렬-행렬)**: 높은 Ops/Byte, L1 캐시에서 높은 hit-rate(86%) → L2/L3 대역폭 미활용
- **Inner-product(행렬-벡터)**: 낮은 Ops/Byte, L1 캐시에서 낮은 hit-rate(23%) → L1 병목으로 인한 성능 제한
- 데이터 이동 오버헤드: Convolution 22%, Inner-product **156%** (L1→L2, L2→L3 포함)

## 방법론

### 3.1. REDUCT Support Extensions (rSX)

- 루프 메타데이터 인코딩 명령어:
  - `TFULoopStart`: TFU 코드 레지스터 플러시
  - `TFULoopCount`: 총 루프 수 설정 (최대 4개 루프)
  - `TFULoopIteration`: 각 루프의 반복 횟수 설정
  - `TFUBaseAddress`: 로드/스토어의 기본 주소 설정
  - `TFUStride`: 각 루프의 주소 스트라이드 설정
  - `TFURegStride`: 목적지 레지스터 ID 스트라이드 설정
- rSX 비트로 마킹된 명령어는 캐시 근처의 TFU에서 실행
- 32개의 TFU Code Register로 모든 DNN 커널 충분히 지원 가능
- 전체 오프로드: 32사이클 (8B 오프로드 버스), 수백 사이클의 언롤링 실행으로 상쇄

### 3.2. Tensor Functional Unit (TFU)

- 32개의 TFU Code Register를 가진 경량 유닛
- 두 개의 8-entry 인오더 이슈 큐: 하나는 연산 명령어, 다른 하나는 로드/스토어용
- 로드/스토어가 캐시에 직접 접근 → 내부 캐시 레벨 우회
- 48-entry "딥" TFU Data Register File (레지스터 리네이밍 불필요)
- Translation Cache로 메모리 관리 보조
- 각 TFU당 TSMC 28nm 기준 면적: **0.38mm²** (레지스터 0.15, MAC 0.17, 제어 0.06)

### 3.3. 캐시 레벨별 분산 배치

- **L1 근처 TFU**: Convolution(행렬-행렬) 프리미티브용 → 높은 L1 hit-rate 활용
- **L2 근처 TFU**: Inner-product(행렬-벡터) 프리미티브용 → L2의 더 높은 hit-rate와 대역폭 활용
- **L3 근처 TFU**: Pooling/Concat 등 데이터 이동이 많은 프리미티브용
- 각 레벨에서 독립적으로 작동하며, SMT 하드웨어 컨텍스트를 활용한 워크 분배

## 핵심 기여

- **핵심 기여**: Near-cache 분산 텐서 연산 + rSX ISA 확장으로 기존 CPU에서 DNN 추론 효율 대폭 향상
- **성능**: Convolution 2.3x perf/Watt, 2x~3.94x raw 성능; Inner-product 1.8x perf/Watt, 2.8x 성능
- **의의**: 기존 CPU 프로그래밍/메모리 모델 유지하면서 DNNDSA 수준 성능 달성, 데이터센터 TCO 절감 가능
- 캐시 용량/대역폭 증가 없이 **2.63%** 면적으로 최적의 성능/전력 효율 제공

## 주요 결과

| 항목 | 내용 |
|------|------|
| **시뮬레이터** | 수정된 Sniper (사이클 정확 멀티코어 시뮬레이션) |
| **프로세서** | Intel 28코어 데이터센터 프로세서, 4-way SMT, 2.6GHz |
| **기본 연산 능력** | 128(2×64) MACs/cycle/core (Intel DL-Boost 유사) |
| **캐시 구조** | L1: 32KB 프라이빗, L2: 1MB 프라이빗, L3: 1.375MB/slice (분산, 비포함) |
| **NoC** | 4×7 메시, XY 라우팅, 최대 22사이클 지연 |
| **소프트웨어 스택** | oneDNN v1.0, Intel C++ Compiler 19.0, OpenMP 멀티스레딩 |
| **DNN 모델** | ResNet-50, DenseNet-169, MobileNet, ResNeXt-101, Transformer, TwoStream |
| **면적 오버헤드** | 단일 Xeon 코어 대비 **2.63%** (AVX-512 유닛 대비 35% 작음) |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]


## 전체 요약

[[../paper-summaries/2021ISCA-summarize/reduct-near-cache-compute-for-dnn-inference-on-multi-core-cpus.md|전체 요약 보기]]
