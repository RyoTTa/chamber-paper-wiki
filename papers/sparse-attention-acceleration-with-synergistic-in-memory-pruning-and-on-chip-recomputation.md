---
tags: [paper, 2022, 2022MICRO, topic/llm-inference, topic/pim]
venue: "55th IEEE/ACM International Symposium on Microarchitecture (MICRO 2022)"
year: 2022
summary_path: "../paper-summaries/2022MICRO-summarize/sparse-attention-acceleration-with-synergistic-in-memory-pruning-and-on-chip-recomputation.md"
---

# Sparse Attention Acceleration with Synergistic In-Memory Pruning and On-Chip Recomputation

**Venue:** 55th IEEE/ACM International Symposium on Microarchitecture (MICRO 2022)
**저자:** Amir Yazdanbakhsh, Ashkan Moradifirouzabadi, Zheng Li, Mingu Kang (Google Research, Brain Team / University of California, San Diego)

## 개요

- Self-attention mechanism은 query-key 간 pairwise correlation을 계산하는 핵심 연산으로, **O(N²)** 의 복잡도를 가짐 (N = 입력 시퀀스 길이)
- Transformer 모델의 시퀀스 길이가 지속적으로 증가하는 추세 (>2K): BERT, GPT 등에서의 긴 시퀀스 요구사항 증가
- 기존 runtime pruning 기법 (LEOPARD, SpAtten 등)은 all key/value embeddings를 온칩 메모리로 가져온 후 pruning을 수행하므로, **데이터 통신 오버헤드가 전체 에너지의 60% 이상** 차지 (on-chip 메모리가 20%로 제한될 때, Figure 1)
- ReRAM 기반 in-memory computing은 높은 에너지 효율성과 대규모 병렬성을 제공하지만, **analog circuit 오류** (thermal noise, process variation), **ADC overhead**, **unpruned vector selective read 문제** 등이 존재
- ReRAM MLC (Multi-Level Cell)은 4-bit/cell이 최적 균형점으로, 정밀도에 제한이 있음

## 방법론

### 3.1. In-Memory Thresholding (ReRAM 기반)

- ReRAM crossbar array에 key vector를 column으로, query vector를 wordline에 DAC로 인가하여 vector-matrix multiplication 수행 (Equation 2)
- **1-bit analog comparator**로 threshold와 비교 → pruning vector (binary) 생성 → 5-bit ADC 대비 **20× 낮은 면적, 30× 낮은 소비전력**
- 모델 정확도 영향 최소화: 4-bit precision에서 virtually no accuracy degradation (Figure 5)
- **Transposable ReRAM** 활용: in-situ computation 모드 (vector-matrix multiplication)과 transposed read 모드 (unpruned vector selective read) 지원
- MSB bits는 transposable ReRAM, LSB bits는 standard ReRAM에 분리 저장

### 3.2. SPRINT Memory Controller

- **CopyQ** 커맨드: query vector를 in-memory query buffer로 복사 (tCL 타이밍만 준수)
- **ReadP** 커맨드: binary pruning vector를 on-chip buffer로 읽음 (read command와 동일한 타이밍)
- **tAxTh** 타이밍: in-memory thresholding 수행 시간 (<8 cycle)
- **Spatial Locality Detection (SLD) engine:** 인접 query의 pruning vector 간 bitwise AND 연산으로 중복 fetch 방지
  - Task 1: Memory Request Vector = P_{t-1} ∧ P_t (실제 fetch가 필요한 vector만 요청)
  - Task 2: Spatial Locality Vector = P_{t-1} ∧ P_t (on-chip에 이미 존재하는 vector 활용)
- 평균 시퀀스 길이의 **2.1%만** between adjacent queries에서 fetch 필요

### 3.3. SPRINT On-Chip Accelerator

- **N CORELETs** 구조: 각 CORELET은 QK-PU (dot product) + V-PU (weighted sum) + K/V buffers로 구성
- **Token-interleaving:** 인접 key vector를 서로 다른 CORELET에 분배하여 워크로드 균형 도달 (Figure 8)
- **2D sequence reduction:** Zero-padded 영역의 연산을 수평/수직 두 방향으로 제거 (예: BERT-SQUAD에서 46% padding 영역 제거)
- **Bypassing mechanism:** 데이터 미스 시 rotate pointer로 사용 가능한 key vector부터 처리

### 3.4. 데이터 레이아웃 및 메모리 시스템

- Key vectors는 non-interleaving 방식으로 memory mat의 하나의 column에 저장
- 인접 key vector는 서로 다른 bank/channel에 분산 배치
- 65nm TSMC 공정, 1GHz 목표 주파수
- S-SPRINT (16KB), M-SPRINT (32KB, 2 CORELETs), L-SPRINT (64KB, 4 CORELETs)

## 핵심 기여

- **핵심 contribution:** ReRAM crossbar array의 approximate in-memory computing과 on-chip precise recompute를 결합하여 self-attention의 quadratic complexity를 linear로 변환하는 최초의 시도
- **성능 향상:** 16KB on-chip 메모리에서 평균 7.5× speedup, 19.6× energy reduction 달성
- **정확도 보장:** On-chip recompute를 통해 baseline 대비 0.36% 미만의 정확도 하락으로 동등 수준 보장
- **의의:** Transformer 모델의 점점 증가하는 시퀀스 길이 요구사항과 리소스 제약 환경에서의 efficient attention acceleration를 위한 hardware-software co-design 프레임워크 제시

## 주요 결과

- **구현 언어:** Verilog (RTL), Chisel (Deflate)
- **공정:** 65nm TSMC general-purpose standard cell library
- **설계 도구:** Cadence Genus 19.1 (logic synthesis), Cadence Innovus 19.1 (PnR)
- **SRAM:** ARM Memory Compiler (65nm single-port SRAM)
- **ReRAM:** 65nm 기준 0.10 pJ/MAC (in-memory computing), 3.1 pJ/bit (read), 24.4 pJ/bit (write)
- **면적:** S-SPRINT 1.18×0.8mm² (16KB on-chip SRAM 포함), M-SPRINT 1.9mm²
- ReRAM in-memory 면적 오버헤드: 약 6%

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2022MICRO-summarize/sparse-attention-acceleration-with-synergistic-in-memory-pruning-and-on-chip-recomputation.md|전체 요약 보기]]
