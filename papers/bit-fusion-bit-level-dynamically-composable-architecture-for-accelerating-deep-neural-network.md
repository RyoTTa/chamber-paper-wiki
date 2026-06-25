---
tags: [paper, 2018, 2018ISCA, topic/gpu, topic/pim]
venue: "ISCA 2018"
year: 2018
summary_path: "../paper-summaries/2018ISCA-summarize/bit-fusion-bit-level-dynamically-composable-architecture-for-accelerating-deep-neural-network.md"
---

# Bit Fusion: Bit-Level Dynamically Composable Architecture for Accelerating Deep Neural Networks

**Venue:** ISCA 2018
**저자:** Hardik Sharma, Jongse Park, Naveen Suda, Liangzhen Lai, Benson Chau, Vikas Chandra, Hadi Esmaeilzadeh (Georgia Tech, Arm, UC San Diego)

## 개요

DNN 가속기에서 비트폭은 정확도 손실 없이 줄일 수 있으나, 모델/레이어 간 비트폭이 크게 변동한다. 고정 비트폭 가속기는 최악의 비트폭에 맞추면 이점이 제한되고, 비트 직렬 가속기는 시프트+축적 로직의 면적 오버헤드가 크다.

Bit Fusion은 2비트 곱셈을 기본으로 하는 BitBrick을 공간적으로 결합하여 동적으로 비트 수준 융합/분해를 지원하는 가속기이다. Eyeriss 대비 3.9× 속도, 5.1× 에너지 절감을 달성하며, 16nm 스케일링 시 895mW로 GPU와 동일 성능을 보인다.

## 방법론

### BitBrick 마이크로아키텍처
- 2비트 × 2비트 곱셈 지원 기본 연산 유닛
- 부호 확장 후 3비트 곱셈기로 6비트 결과 생성

### 공간적 융합 (Spatial Fusion)
- 16개 BitBrick을 공간적으로 결합하여 단일 사이클 내 다양한 연산 지원:
  - 1개 4비트×4비트, 또는 2개 4비트×2비트, 또는 4개 2비트×2비트
- 시간적 설계 대비 면적/전력 대폭 절감

### 가변 비트폭 매핑
- 4비트 곱셈 = 4개의 2비트 곱셈으로 분해 → shift-add로 복원
- 최대 16비트 지원: 재귀적 분해 (16→8→4→2비트)

### 시스톨릭 실행 모델
- 2D 시스톨릭 어레이에서 입력 벡터 × 가중치 행렬 곱셈
- Fused-PE 수를 비트폭에 따라 동적 조정 → 낮은 비트폭에서 버퍼 접근 4배 감소

### Fusion-ISA
- 블록 구조 ISA로 레이어 단위 비트 수준 융합 비용 경감
- 루프 명령어로 DNN 레이어의 중첩 루프를 30~86개 명령어로 표현

## 핵심 기여

1. 비트 수준 동적 융합/분해라는 새로운 가속기 설계 차원 제시
2. 공간적 융합으로 시간적 설계 대비 대폭 면적/전력 절감
3. 2~16비트까지 임의 비트폭 지원으로 다양한 DNN 모델 호환

## 주요 결과

- **Eyeriss 대비**: 3.9× 속도, 5.1× 에너지 절감 (동일 45nm, 1.1mm²)
- **Stripes 대비**: 2.6× 속도, 3.9× 에너지 절감
- **GPU 대비**: 16nm에서 895mW로 동일 성능 (279배 낮은 전력)
- **Cifar-10**: 최대 13× 속도 향상 (1비트 입력/가중치)

## 한계점

- 고정된 레이어 내 비트폭 변동은 미지원 (레이어 간 변동만 지원)
- 16비트 초과 비트폭은 지원하지 않음

## 관련 개념

- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/pim.md|PIM]]
