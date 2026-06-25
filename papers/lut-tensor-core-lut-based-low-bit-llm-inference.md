---
tags: [paper, 2025, 2025ISCA, topic/cache, topic/gpu, topic/llm-inference]
venue: "International Symposium on Computer Architecture (ISCA) 2025"
year: 2025
summary_path: "../paper-summaries/2025ISCA-summarize/lut-tensor-core-a-software-hardware-co-design-for-lut-based-low-bit-llm-inference.md"
---

# LUT Tensor Core: A Software-Hardware Co-Design for LUT-Based Low-Bit LLM Inference

**Venue:** International Symposium on Computer Architecture (ISCA) 2025
**저자:** Zhiwen Mo*, Lei Wang*, Jianyu Wei*, Zhichen Zeng*, Shijie Cao†, Lingxiao Ma, Naifeng Jing, Ting Cao, Jilong Xue, Fan Yang, Mao Yang (Imperial College London, Peking University, USTC, University of Washington, Microsoft Research, Shanghai Jiao Tong University) (* equal contribution, † corresponding author)

## 개요

- LLM 추론은 막대한 하드웨어 리소스를 필요로 하며, LLAMA-2-70B의 경우 FP16 기준 모델 가중치만 140GB 소요
- 저비트 양자화(low-bit quantization)로 추론 비용 절감 시도: 4-bit 가중치 양자화가 보편화되고, 2-bit/1-bit까지 탐구 진행 중
- 가중치 양자화는 고정밀 활성화(activation)와 결합되어 mixed-precision GEMM(mpGEMM) 연산이 핵심 계산 패턴으로 부상
  - 가중치: INT4/2/1 (낮은 정밀도), 활성화: FP16/8, INT8 (높은 정밀도)
- 기존 하드웨어(GPU, TPU)는 mpGEMM을 네이티브로 지원하지 않음 → 비효율적인 디קו얼리제이션 기반 구현에 의존
  - 디코얼리제이션: 저비트 표현을 하드웨어 지원 GEMM에 맞게 업스케일링 → 추가 연산 오버헤드 발생
- Lookup Table(LUT) 기반 mpGEMM은 유망하지만, 소프트웨어 구현에서 제한적인 명령어 지원과 비효율적 메모리 접근으로 인해 성능 격차 존재
  - 기존 LUT 기반 커널이 cuBLAS 대비 GEMM에서 최대 0.02× 수준으로 현저히 저조한 성능 (Fig. 4)

## 방법론

### 3.1. 소프트웨어 최적화
- **테이블 사전 계산 융합(Fusion)**: 기존 설계에서 여러 유닛이 중복으로 사전 계산하는 문제를 해결
  - 사전 계산을 독립 연산자로 분리하고, 이전 연산자와 융합하여 메모리 접근 최소화
  - Welder 컴파일러의 연산자 융합 검색 공간에 사전 계산을 추가하여 오버헤드를 16.47%→2.62%(prefill), 24.41%→2.52%(decode)로 감소 (Table 4)
- **테이블 대칭성 활용**: {0,1}을 {-1,1}로 재해석하여 테이블 크기 50% 절감
- **테이블 양자화**: 활성화 비트 폭에 따라 테이블 폭을 줄여 저장 공간 추가 절감
  - INT8 테이블 양자화 적용 시 모델 정확도 손실 무시할 수준 (WikiText-2 PPL 7.68→7.69, Table 5)

### 3.2. 하드웨어 최적화
- **늘어진 타일링 형태(Elongated Tiling Shape)**: 활성화가 고비트, 가중치가 저비트인 특성을 활용한 MNK 설계 탐색
  - 최적 MNK: M=2, N=64, K=4 (활성화 비트 총합 32bits ≈ 가중치 비트 총합 64bits → 정사각 배열 근사)
- **비트 직렬 설계(Bit-serial Design)**: 다양한 정밀도 조합(WINT1~4 × AFP8/16, AINT8/16)을 하드웨어 리디자인 없이 지원
- **PPA(Power, Performance, Area) 비교**:
  - MAC 기반 Tensor Core 대비 전력 4×~6× 절감, 면적 4×~6× 축소 (WINT1 기준)
  - 기존 LUT 구현 대비 면적 및 전력优势: 기존 LUT는 가중치 2비트 이상에서 면적 이점 없음 → 소프트웨어-하드웨어 공동 설계로 해결
  - LUT-based DP4 유닛: 61.55 TFLOPs/mm² (@WINT1AFP16) 달성, MAC(3.39 TFLOPs/mm²) 대비 18× 높은 연산 밀도

### 3.3. 명령어 집정 및 컴파일 지원
- **LMMA(LUT-based Matrix Multiply-Accumulate) 명령어**: 기존 MMA 명령어를 확장하여 연산자 유형 및 형태 메타데이터 포함
  - 형태 정보를 활용한 타일 기반 딥러닝 컴파일러(TVM 등) 재컴파일로 효율적 커널 자동 생성
- **커널 설계**: CUTLASS 스타일 output-stationary 데이터플로우, 스레드 블록 스위즐링으로 L2 캐시 히트율 향상
- **DSE(Design Space Exploration)**: 다양한 MNK 구성을 탐색하여 연산 밀도-전력-면적 최적점 도출

## 핵심 기여

- LUT 기반 mpGEMM을 위한 소프트웨어-하드웨어 공동 설계로 저비트 LLM 추론 효율 대폭 향상
- 소프트웨어(테이블 융합, 대칭성 활용, 양자화)와 하드웨어(늘어진 타일링, 비트 직렬 설계)의 공동 최적화로 기존 LUT 설계의 한계 극복
- A100 통합 시 BitNet b1.58 3B에서 5.51× 추론 가속, 연산 밀도 20.9×, 에너지 효율 11.2× 향상
- 다양한 가중치(INT1~4) 및 활성화(FP8/16, INT8/16) 정밀도 조합을 유연하게 지원
- 기존 GPU 추론 스택과의 호환성을 위한 LMMA 명령어 및 컴파일 최적화 제공
- 향후 저비트 학습, KV 캐시 양자화, FP 가중치 지원 등 확장 가능성 제시

## 주요 결과

- 하드웨어: Verilog 기반 설계, Synopsys Design Compiler로 TSMC 28nm 공정 합성 (1GHz 타겟팅)
- 시뮬레이터: Accel-Sim(GPU 시뮬레이터) 활용, LUT Tensor Core 통합 A100 시뮬레이션
- 엔드투엔드 시뮬레이터: 타일 기반 GPU 시뮬레이터 개발 (Mean Absolute Percentage Error 5.21%)
  - Accel-Sim 대비 약 500만 배 빠른 시뮬레이션 속도
- 소프트웨어 스택: Welder 컴파일러(TVM 기반) 통합, LMMA 명령어 지원
- 오픈소스: https://github.com/microsoft/T-MAC/tree/LUTTensorCore_ISCA25

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]


## 전체 요약

[[../paper-summaries/2025ISCA-summarize/lut-tensor-core-a-software-hardware-co-design-for-lut-based-low-bit-llm-inference.md|전체 요약 보기]]
