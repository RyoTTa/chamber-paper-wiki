---
tags: [paper, 2018, 2018ISCA]
venue: "45th Annual International Symposium on Computer Architecture (ISCA '18)"
year: 2018
summary_path: "../paper-summaries/2018ISCA-summarize/bit-fusion-bit-level-dynamically-composable-architecture-for-accelerating-deep-neural-network.md"
---

# Bit Fusion: Bit-Level Dynamically Composable Architecture for Accelerating Deep Neural Networks

**Venue:** 45th Annual International Symposium on Computer Architecture (ISCA '18)
**저자:** Hardik Sharma, Jongse Park, Naveen Suda, Liangzhen Lai, Benson Chau, Vikas Chandra, Hadi Esmaeilzadeh (Georgia Institute of Technology, Arm Inc., University of California, San Diego)

## 개요

- DNN 가속기 설계에서 연산 비트폭(bitwidth)은 정확도 손실 없이 줄일 수 있음 (Quantization)
- 그러나 **DNN 모델 간, 레이어 간 비트폭이 크게 변동**:
  - AlexNet: 1~8비트 혼합
  - Cifar-10: 1~4비트 혼합
  - LSTM/RNN: 1~8비트 혼합
- **고정 비트폭 가속기의 한계**:
  - 최악의 비트폭 요구사항에 맞추면 이점 제한
  - 낮은 비트폭에 최적화하면 정확도 저하
- 기존 비트 직렬(bit-serial) 가속기 (Stripes, Loom 등):
  - 시간적(temporal) 설계 → 멀티플라이어를 여러 사이클에 걸쳐 반복 사용
  - 시프트+축적 로직이 최대 지원 비트폭에 비례하여 면적/전력 오버헤드 증가
  - 16비트 지원 시 시프트+축적 로직이 전체 면적의 ~90% 차지
- 핵심 문제: **동적 비트 수준 융합/분해(dynamic bit-level fusion/decomposition)**를 지원하는 가속기 아키텍처 부재

## 방법론

### 3.1. BitBrick 마이크로아키텍처

- **기본 연산 유닛**: 2비트 × 2비트 곱셈 지원
- **입력**: 두 개의 2비트 피연산자(x2b, y2b) + 부호 비트(sx, sy)
- **처리 과정**:
  1. 부호 비트에 따라 2비트 → 3비트 부호 확장
  2. 3비트 부호 있는 곱셈기로 6비트 곱셈 결과 생성
- **리소스**: 매우 소규모 → 대규모 어레이 구성 가능

### 3.2. 가변 비트폭 매핑

- **4비트 × 4비트 곱셈**: 4개의 2비트 곱셈으로 분해 → 4개 BitBrick 사용
  - 분해된 곱셈 결과를 시프트(0, 2, 2, 4 비트 왼쪽 시프트) 후 합산
- **4비트 × 2비트 곱셈**: 동일한 4개 BitBrick으로 2개의 곱셈 동시 실행 → 2배 성능
- **2비트 × 2비트 곱셈**: 각 BitBrick이 1개 곱셈 → 4개 곱셈 동시 실행 → 4배 성능
- **최대 16비트 지원**: 재귀적 분해 (16→8→4→2비트)
  - A2n × B2n = 2^(2n) × (A_hi × B_hi) + 2^n × (A_hi × B_lo + A_lo × B_hi) + (A_lo × B_lo)

### 3.3. Fusion Unit 마이크로아키텍처

- **공간적 융합(Spatial Fusion)**: 16개 BitBrick을空间적으로 결합하여 단일 사이클 내 다양한 연산 지원:
  - 1개의 4비트 × 4비트 곱셈, 또는
  - 2개의 4비트 × 2비트 곱셈, 또는
  - 4개의 2비트 × 2비트 곱셈
- **시간적 융합(Temporal Fusion) 대비 장점**:
  - 시프트+축적 로직이 면적의 90%를 차지하는 시간적 설계 대비 대폭 면적 절감
  - 동일 처리량에서 더 적은 SRAM 접근

### 3.4. 시스톨릭 실행 모델

- 2D 시스톨릭 어레이: 입력 벡터 × 가중치 행렬 곱셈
- **Fused-PE**: 여러 BitBrick이 융합된 논리적 곱셈 유닛
  - 입력/가중치 버퍼에서 32비트씩 읽음 → 비트폭에 따라 Fused-PE 수를 동적 조정
- **부분 결과 축적**: 32비트 정밀도로 부분 결과 및 최종 결과 유지 → 정확도 보장
- ** getInput/Weight 버퍼**: 비트폭별로 적재 최적화 → 낮은 비트폭에서 버퍼 접근 횟수 4배 감소

### 3.5. 명령어 세트 아키텍처 (Fusion-ISA)

- **블록 구조 ISA**: 레이어 단위로 명령어 블록 구성, 비트 수준 융합 비용을 블록 전체에서 경감
- **설정 명령어(Setup)**: 블록 시작 시 Fusion Unit의 비트폭 구성 지정
- **루프 명령어(Loop)**: DNN 레이어의 중첩 루프를 간결하게 표현 (30~86개 명령어로 LSTM, CNN, pooling, FC 레이어 표현 가능)
- **메모리 접근 명령어**: ld-mem, st-mem, rd-buf, wr-buf — 융합 구성에 따라 의미가 동적으로 변화
- **코드 최적화**: 루프 순서 변경, 루프 타일링, 레이어 융합

## 핵심 기여

- **핵심 기여**: 비트 수준 동적 융합/분해라는 새로운 가속기 설계 차원 제시
- **성능**: Eyeriss 대비 3.9× 속도, 5.1× 에너지 절감; 16nm GPU 대비 895mW로 동일 성능
- **유연성**: 2~16비트까지 임의 비트폭 지원, CNN/RNN/LSTM 등 다양한 DNN 모델 호환
- **의의**: DNN 가속기에서 비트 수준 유연성을 공간적으로 구현한 최초의 아키텍처 → 정밀도-성능-에너지 트레이드오프를 최적화하는 새로운 패러다임 제시

## 주요 결과

- **구현 언어**: Verilog RTL
- **합성 기술**: 45nm 공정, Synopsys Design Compiler
- **시뮬레이터**: Fusion-ISA 기반 정확한 사이클 시뮬레이터 개발
- **온칩 메모리**: IBUF, OBUF, WBUF (입력/출력/가중치 버퍼)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- 개념 매칭 없음

## 전체 요약

[[../paper-summaries/2018ISCA-summarize/bit-fusion-bit-level-dynamically-composable-architecture-for-accelerating-deep-neural-network.md|전체 요약 보기]]
