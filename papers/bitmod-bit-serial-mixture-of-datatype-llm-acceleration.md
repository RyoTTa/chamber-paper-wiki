---
tags: [paper, 2025, 2025HPCA, topic/gpu, topic/llm-inference]
venue: "2025 IEEE International Symposium on High Performance Computer Architecture (HPCA 2025)"
year: 2025
summary_path: "../paper-summaries/2025HPCA-summarize/bitmod-bit-serial-mixture-of-datatype-llm-acceleration.md"
---

# BitMoD: Bit-serial Mixture-of-Datatype LLM Acceleration

**Venue:** 2025 IEEE International Symposium on High Performance Computer Architecture (HPCA 2025)
**저자:** Yuzong Chen, Ahmed F. AbouElhamayed, Xilai Dai, Yang Wang, Marta Andronic, George A. Constantinides, Mohamed S. Abdelfattah (Cornell University, Microsoft Research, Imperial College London)

## 개요

- 대규모 언어 모델(LLM)의 크기가 급격히 성장하면서 배포에 필요한 메모리 용량이 부적절해지고 있음: GPT-1(2018)의 117M 파라미터에서 GPT-3는 175B로 2년 만에 1000배 이상 증가
- 예를 들어, Llama-3(8B+)는 FP16 기준 16GB 이상의 메모리가 필요하며, Jetson-TX2(8GB)와 같은 엣지 GPU에는 적재 불가능
- 기존 가중치 양자화(quantization) 방법들의 한계:
  - 양자 인식 학습(QAT)은 재학습 비용이 너무 높아 LLM에 비실용적
  - 학습 후 양자화(PTQ)는 재학습 불필요하나, GPU는 정수 가중치와 부동소수점 활성화 간의 곱셈 전용 하드웨어가 없어 FP16으로 디양자화 후 연산해야 함
  - 기존 커스텀 데이터 타입(ANT, OliVe, MX 등)은 per-channel 또는 per-tensor 정밀도로는 정량화 오차가 크고, per-group 정밀도에서의 최적 데이터 타입이 미탐구됨
- Per-group 양자화(grain size=128)가 per-tensor 및 per-channel 대비 낮은 최대값과 범위를 가져 정량화 오차를 줄이나, 그룹별 스케일링 팩터의 디양자화 오버헤드가 하드웨어 효율을 저하시킴 (Table I, Fig. 2)

## 방법론

### 3.1. 커스텀 데이터 타입 설계 (알고리즘)

- 기본 FP4 데이터 타입의 잔여 영-zero 값을 특수 값(special value)으로 대체하여 그룹 내 값 분포에 적응
- 특수 값 후보: ±2x, ±0.5x, ±x 등으로, 각 그룹에서 최소 평균 제곱 오차(MSE)를 제공하는 값을 자동 선택 (Algo. 1)
- FP4-EA: 1 sign + 2 exponent + 1 mantissa 비트, 특수 값 ±8까지 확장 가능
- FP3: FP4의 부분집합으로, 동일 하드웨어로 디코딩 가능
- 그룹별 8비트 스케일링 팩터 + 2비트 인코딩 메타데이터만 필요 (그룹 크기 128에서 오버헤드 미미)
- 기존 비대칭 정수 양자화(INT4-Asym)는 16비트 스케일링 팩터 + 8비트 zero-point가 필요하므로 BitMoD가 메모리 오버헤드 면에서 우위 (Section III-D)

### 3.2. 통합 비트 직렬 표현

- 모든 지원 데이터 타입(INT8, INT6, FP4, FP3)을 통합된 비트 직렬 항(bit-serial term)으로 변환:
  ```
  v_term = (-1)^sign · 2^exp · man · 2^bsig
  ```
- **INT8/INT6:** Booth 인코딩으로 이진 문자열을 3비트 Booth 문자열로 분해 (각 항은 sign, exponent, mantissa, bit-significance 포함)
- **FP4:** 고정점 변환 → 선도 비트 감지기(LOD)로 최대 2개의 비트 직렬 항 생성
- **FP3:** FP4의 부분집합이므로 동일 디코더로 처리
- 특수 값 레지스터 파일(SV_reg)에 그룹별 특수 값 저장, LLM 배포 전 1회 프로그래밍

### 3.3. BitMoD 처리 요소(PE) 마이크로아키텍처

- 매 사이클마다 4방향 도트 곱셈: 4개 비트 직렬 가중치 항(w) × 4개 FP16 활성화(a)
- **Step 1 (지수 정렬):** ae + we 합산 → 델타 지수(δe) 계산, 곱셈 부호(ys) 생성
- **Step 2 (비트 직렬 곱셈):** 1비트 가중치 Mantissa(wm) × 11비트 활성화 Mantissa(am, hidden bit 포함) → 우시프터로 지수 정렬 → 비트 직렬 Mantissa 도트 곱셈 (adder tree)
- **Step 3 (누적):** 도트 곱셈 결과 × 가중치 bit-significance(Wbsig) → 누적기 mantissa(mACC)에 추가 → 정규화로 누적기 지수(eACC) 갱신
- **Step 4 (비트 직렬 디양자화):** 누적기 mantissa를 그룹 스케일링 팩터(∆i)의 비트별로 곱셈 → 시프트-앤-'=>" 합으로 디양자화된 부분 합의 지수(eGRP)와 mantissa(mGRP) 산출
- 디양자화 오버헤드 분석: 그룹 크기 128, PE 곱셈 크기 4, FP3(최저 정밀도)에서 2 사이클 → 128/4 × 2 = 64 사이클 → 8비트 스케일링 팩터의 8사이클 디양자화가 파이프라인을 절대 정지시키지 않음
- FP3 사용 시 FP16 PE 대비 **2×** 처리량 향상, INT6 사용 시 **1.33×** 향상
- BitMoD PE는 FP16 PE 대비 **24%** 적은 면적 사용

### 3.4. 전체 가속기 아키텍처

- 4×4 타일의 PE 어레이, 소스틱(systolic) 방식 연결
- 각 PE 타일: 8행 × 8열, output-stationary 데이터플로우
- 비트 직렬 항 생성기(Bit-serial Term Generator): 가중치 데이터를 비트 직렬 항으로 분해
- 가중치 버퍼, 입력 버퍼(은행 구조), 출력 버퍼로 충분한 대역폭 제공
- 오프칩 DRAM에서 가중치 로드

## 핵심 기여

- **핵심 기여:** 3비트/4비트 가중치 양자화에서도 실용적 정확도를 유지하는 알고리즘-하드웨어 공동 설계 BitMoD 프레임워크 제시
- **정확도:** 4비트에서 평균 ∆PPL 0.48(기존 최선 0.62 대비 23% 개선), 3비트에서 ∆PPL 2.94(기존 최선 23.14 대비 87% 개선)
- **성능:** FP16 대비 2.2× 속도, 2.31× 에너지 효율; ANT 대비 1.69×, OliVe 대비 1.48× 속도 향상
- **유연성:** 비트 직렬 PE로 INT8/INT6/FP4/FP3를 통합 처리, 정밀도-효율성 트레이드오프 자유자재 조절 가능
- **실용성:** 기존 PTQ 기법(AWQ, OmniQuant, SmoothQuant)과 호환되어 추가 정확도 향상 가능
- **의의:** 엣지 디바이스에서의 LLM 배포를 위한 저정밀 양자화와 전용 가속기를 동시에 최적화한 최초의 통합 솔루션

## 주요 결과

- **소프트웨어:** Python/PyTorch 기반 양자화 프레임워크 (bitmod-quant)
- **하드웨어 시뮬레이터:** Custom cycle-level 시뮬레이터 (bitmod-sim)
- **오픈소스:** GitHub (https://github.com/yc2367/BitMoD-HPCA-25)에 전체 코드 공개
- **양자화 속도:** Llama-2-7B 전체 모델을 단일 A6000 GPU에서 ~10초 내 양자화
- **지원 모델:** OPT-1.3B, Phi-2B, Yi-6B, Llama-2-7B, Llama-2-13B, Llama-3-8B (6개 대표 LLM)
- **기존 기법 통합 검증:** AWQ, OmniQuant, SmoothQuant와의 결합 가능성 실험 포함

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]


## 전체 요약

[[../paper-summaries/2025HPCA-summarize/bitmod-bit-serial-mixture-of-datatype-llm-acceleration.md|전체 요약 보기]]
