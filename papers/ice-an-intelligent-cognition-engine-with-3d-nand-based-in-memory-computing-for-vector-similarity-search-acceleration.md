---
tags: [paper, 2022, 2022MICRO, topic/dram, topic/nvm, topic/pim, topic/storage]
venue: "55th IEEE/ACM International Symposium on Microarchitecture (MICRO 2022)"
year: 2022
summary_path: "../paper-summaries/2022MICRO-summarize/ice-an-intelligent-cognition-engine-with-3d-nand-based-in-memory-computing-for-vector-similarity-search-acceleration.md"
---

# ICE: An Intelligent Cognition Engine with 3D NAND-based In-Memory Computing for Vector Similarity Search Acceleration

**Venue:** 55th IEEE/ACM International Symposium on Microarchitecture (MICRO 2022)
**저자:** Han-Wen Hu (Macronix / National Tsing Hua University), Wei-Chen Wang (MIT / National Tsing Hua University), Yuan-Hao Chang (Academia Sinica), Yung-Chun Lee (National Tsing Hua University), Bo-Rong Lin (Macronix), Huai-Mu Wang (Macronix), Yen-Po Lin (National Tsing Hua University), Yu-Ming Huang (Macronix), Chong-Ying Lee (Macronix), Tzu-Hsiang Su (Macronix), Chih-Chang Hsieh (Macronix), Chia-Ming Hu (Macronix), Yi-Ting Lai (Macronix), Chung-Kuang Chen (Macronix), Han-Sung Chen (Macronix), Hsiang-Pang Li (Macronix), Tei-Wei Kuo (National Taiwan University), Meng-Fan Chang (National Taiwan University), Keh-Chung Wang (Macronix), Chun-Hsiung Hung (Macronix), Chih-Yuan Lu (Macronix)

## 개요

- 벡터 유사도 검색(VSS, Vector Similarity Search)은 얼굴 검색, 이미지 검색 등 비정형 데이터 검색의 핵심 기술로, Siamese 네트워크로 추출한 특징 벡터 간의 코사인 유사도/유클리드 거리를 비교하여 top-k 패턴을 찾는다.
- 엣지 디바이스에서 VSS를 수행할 때, 특징 벡터 데이터셋이 DRAM 용량을 초과하면 **스토리지↔DRAM 간 데이터 스왑**이 반복 발생하여, 검색 시간(t_SR)과 에너지 소비(E_SR)가 전체 실행 시간의 **90~99%**를 차지한다(Figure 2).
- 기존 엣지 디바이스(Raspberry Pi 3/4, Jetson Nano)에서 500K 얼굴 데이터셋(CASIA-WebFace)을 대상으로 실험하면, **데이터 이동 시간이 유사도 검색 시간을 압도**하며, 고성능 엣지 디바이스일수록 DRAM 용량 부족으로 상대적 스왑 비율이 더 높아진다.
- 기존 3D NAND 기반 nvIMC(non-volatile In-Memory Computing) 연구들은 ADC/DAC가 필요한 아날로그 방식이었고, 비트 오류 영향을 정확히 고려하지 않았으며, 상용화 가능성이 낮았다(Table III).
- 3D NAND 셀의 비트 오류(reliability issue)를 해결하기 위한 ECC 디코딩은 인코딩/디코딩 과정에서 높은 지연과 에너지를 유발한다.

## 방법론

### 3.1. Cognitive 3D NAND 칩 설계

- **96-Stacked-WL 3D NAND CuA (Circuit-under-Array) 기술:** 512Gb TLC 3D NAND 기반, 4 Plane, 16KB 페이지 크기(Table II).
- **디지털 nvIMC 방식:** 
  - 기존 Type-a (CSL 분리 + ADC 필요) 및 Type-b (CSL VDD 고정) 방식과 달리, ADC/DAC 없이 디지털 어큐뮬레이터만 추가.
  - 수정된 page buffer와 wordline driver로 VVM 연산 지원.
  - **면적 오버헤드 1.6%** (TC 디지털 어큐뮬레이터) — 기존 IEDM 2019 [65]의 137%, IEDM 2018 [63]의 546% 대비 크게 절감(Figure 12(d)).
- **4-Plane 병렬 VVM:** 4개 plane에서 동시 비트 곱셈(72μs) + 4회 순차 누적(140μs) → 평균 VVM당 53μs, 26.9mW, 5.74μJ(Table II).

### 3.2. BET 데이터 인코딩

- **목적:** ECC 디코딩 오버헤드를 제거하면서 비트 오류에 대한 내성을 확보.
- **방식:** FP32 특징 벡터를 INT8로 양자화한 후, 2의 보수(two's complement) 형식으로 인코딩.
- **효과:** VGGFace2 기준 INT8 데이터셋 680MB, CelebA 80MB, CASIA-WebFace 2GB 필요.
- **정확도 영향:** HTNS 적용 시 CelebA FP32 기준 95.1% → INT8 95.1%, UINT8 94.4%, INT4 94.8%, INT2 93.6%로 큰 하락 없음(Table IV).

### 3.3. TC 디지털 어큐뮬레이터

- **기능:** VVM 연산의 부호 비트(sign bit) 계산을 처리하여 INT8/INT4 곱셈累積을 지원.
- **구조:** 표준 3D NAND page buffer 주변에 FSM, wordline driver와 함께 배치(Figure 12(c)).
- **성능:** 4-plane 병렬 시 평균 VVM당 에너지 1.4μJ, 전력 26.9mW.

### 3.4. HTNS (Hierarchical Two-layer Navigation Search) 알고리즘

- **1단계:** 전체 특징 벡터 데이터셋을 범주별로 분류한 index를 이용해, 1차 검색으로 상위 N₁개 후보 범주를 선별.
- **2단계:** 선별된 범주의 가중 벡터(weight vectors)만을 대상으로 2차 검색을 수행하여 최종 top-k 결과를 도출.
- **효과:** 전체 데이터셋을 순회하는 대비 탐색 범위를 대폭 축소하여 검색 시간 절감.
- **정확도 개선:** HTNS 적용 시 FP32 기준 CelebA 94.7%→95.1%, VGGFace2 93.2%→93.7%, CASIA-WebFace 82.6%→85.7% 향상(Table IV).

## 핵심 기여

- **핵심 기여:** 3D NAND 기반 디지털 nvIMC를 활용한 최초의 실제 실리콘 데이터를 갖는 VSS 가속기 ICE 제안.
- **성능:** 기존 엣지 시스템 대비 실행 시간 **17×~95×**, 에너지 효율 **11×~140×** 향상.
- **비용 효율:** 면적 오버헤드 **1.6%**로 상용 3D NAND 칩에 쉽게 통합 가능.
- **정확도 보장:** BET 인코딩과 HTNS 알고리즘으로 ECC 없이도 정확도를 유지하거나 향상.
- **범용성:** 얼굴 검색뿐 아니라 이미지 분류, 객체 인식, 음성 인식 등 다양한 VSS 애플리케이션에 확장 가능.
- **의의:** 엣지 디바이스에서 VSS의 핵심 병목인 데이터 이동 문제를 메모리 내 연산으로 근본적으로 해결하고, 상용 3D NAND 기반의 실용적解决方案을 제시.

## 주요 결과

- **테스트 칩:** 96-layer 3D NAND CuA 기술로 제작된 cognitive 3D NAND 테스트 칩(Figure 12(a)).
- **소자 크기:** TC 디지털 어큐뮬레이터 면적 4μm × 1.6μm, 8b ADC 면적 4μm × 0.26μm.
- **시스템 구성:** 2× 컨트롤러(158mW), 128KB SRAM 버퍼(105mW), 3D NAND 인터페이스(80mW), 4× cognitive 3D NAND 칩(884mW) → 전체 검색 시 전력 1227mW(Table II).
- **구현 언어/도구:** HSPICE (회로 시뮬레이션), SiFive HiFive unmatched 보드 + Arduino Due + Raspberry Pi4 (임베디드 시스템 구현).
- **대상 애플리케이션:** 얼굴 검색(Face Search) — MobileFaceNet, FaceNet 모델, CelebA/VGGFace2/CASIA-WebFace 데이터셋.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2022MICRO-summarize/ice-an-intelligent-cognition-engine-with-3d-nand-based-in-memory-computing-for-vector-similarity-search-acceleration.md|전체 요약 보기]]
