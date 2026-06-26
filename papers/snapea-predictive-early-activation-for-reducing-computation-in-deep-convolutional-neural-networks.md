---
tags: [paper, 2018, 2018ISCA]
venue: "45th Annual International Symposium on Computer Architecture (ISCA '18)"
year: 2018
summary_path: "../paper-summaries/2018ISCA-summarize/snapea-predictive-early-activation-for-reducing-computation-in-deep-convolutional-neural-networks.md"
---

# SnaPEA: Predictive Early Activation for Reducing Computation in Deep Convolutional Neural Networks

**Venue:** 45th Annual International Symposium on Computer Architecture (ISCA '18)
**저자:** Vahideh Akhlaghi (UC San Diego / Georgia Tech), Amir Yazdanbakhsh (Georgia Tech), Kambiz Samadi (Qualcomm), Rajesh K. Gupta (UC San Diego), Hadi Esmaeilzadeh (UC San Diego)

## 개요

- Deep CNN은 단일 입력 분류에도 **수십억 번의 곱셈-누적 연산** 필요 (예: 224×224×3 ImageNet 이미지)
- 핵심 관찰: 많은 현대 CNN에서 convolution 후 ReLU 활성화 함수 적용 → **ReLU는 음수 입력에 0 출력**
  - AlexNet: ReLU가 입력의 약 42%를 0으로 만듦
  - GoogLeNet: 약 66%
  - SqueezeNet: 약 68%
  - VGGNet: 약 62%
- 입력 이미지에 따라 zero 값의 공간 분포가 달라짐 (동적 패턴)
- 기존 접근법의 한계:
  - **정적 pruning**: 네트워크 구조를 미리 변경 → 동적 입력 패턴 미반영
  - **Dynamic pruning**: 실행 시 0을 감지하지만 convolution의 모든 연산을 완료 후 필터링 → 불필요한 연산 이미 수행
- 핵심 문제: **convolution 연산 중간에 zero 출력을 조기에 탐지하여 불필요한 연산을 생략하는 메커니즘 부재**

## 방법론

### 3.1. Exact Mode (정확 모드)
- **가중치 재배치**: 가중치를 부호 순서로 정렬 (음수 → 양수 순서)
- **부분 합 모니터링**: convolution 연산 중간에 부호 비트를 1비트씩 확인
- **조기 중단**: 부분 합이 음수가 되면 나머지 multiply-accumulate 연산 중단
- 정확도 손실: **0%** (ReLUs 출력이 정확히 동일)
- 연산 절약: average 28% speedup, 16% energy reduction

### 3.2. Predictive Mode (예측 모드)
- **추론 기반 조기 중단**: exact mode보다 더 일찍 중단
- **다변수 최적화 알고리즘**: 층별 민감도에 따라 예측 임계값 결정
- **정확도-연산 트레이드오프 노브**: 임계값 조절로 정확도 손실 제어
- 평균 3% 정확도 손실로:
  - 67.8%의 convolution 층에서 predictive 모드 적용 가능
  - 적용된 층: 평균 2.02× speedup, 1.89× energy saving
  - 최대: 3.59× speedup, 3.14× energy reduction

### 3.3. 하드웨어 구현
- **Early Termination Unit (ETU)**: convolution 연산 중간에 부호 비트 모니터링 및 중단 제어
- **Weight Pre-processing Unit**: 가중치를 부호 순서로 재배치
- **Threshold Register**: predictive 모드의 임계값 저장
- ETU 오버헤드: 매우 낮음 (1비트 부호 비교 + 카운터)

### 3.4. 소프트웨어-하드웨어 공존 최적화
- **정적 분석**: 네트워크 각 층의 민감도 분석 → predictive 모드 적용 가능 층 식별
- **동적 적용**: 실행 시 ETU가 부호 비트를 모니터링 → 중단 결정
- **互补적 특성**: 기존 정적 pruning 기법과 결합 가능 (pruning 후 남은 연산에 SnaPEA 적용)

## 핵심 기여

- **핵심 기여**: CNN의 algorithmic 구조 (ReLU의 zero 출력 특성)를 활용한 최초의 조기 활성화 기법
- **성능**: Exact mode에서 평균 28% speedup, 16% energy 절약 (정확도 손실 0%)
- **실용성**: 기존 CNN 가속기에 쉽게 통합 가능, 하드웨어 오버헤드 미미
- **互补성**: 정적 pruning 기법과 결합하여 추가 성능 향상 가능
- **의의**: 딥러닝 가속기의 에너지 효율성 향상에 기여

## 주요 결과

- **평가 플랫폼**: 기존 CNN 가속기 기반 모델링
- **구현 언어**: C++ 시뮬레이터 + 하드웨어 RTL (Verilog)
- **시스템 구성**: CNN 가속기에 ETU 통합
- **네트워크**: AlexNet, GoogLeNet, SqueezeNet, VGGNet, ResNet 등 5개 현대 CNN

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- 개념 매칭 없음

## 전체 요약

[[../paper-summaries/2018ISCA-summarize/snapea-predictive-early-activation-for-reducing-computation-in-deep-convolutional-neural-networks.md|전체 요약 보기]]
