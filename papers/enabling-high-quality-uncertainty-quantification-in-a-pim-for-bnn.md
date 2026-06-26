---
tags: [paper, 2022, 2022HPCA, topic/pim]
venue: "IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2022"
year: 2022
summary_path: "../paper-summaries/2022HPCA-summarize/enabling-high-quality-uncertainty-quantification-in-a-pim-designed-for-bayesian-neural-network.md"
---

# Enabling High-Quality Uncertainty Quantification in a PIM Designed for Bayesian Neural Network

**Venue:** IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2022
**저자:** Xingchen Li (Peking University), Bingzhe Wu (Peking University), Guangyu Sun (Peking University), Zhe Zhang (Peking University), Zhihang Yuan (Peking University), Runsheng Wang (Peking University), Ru Huang (Peking University), Dimin Niu (Alibaba Group), Hongzhong Zheng (Alibaba Group), Zhichao Lu (Hefei Reliance Memory Ltd.), Liang Zhao (Hefei Reliance Memory Ltd.), Meng-Fan (Marvin) Chang (National Tsing Hua University), Tianchan Guan (Alibaba Group), Xin Si (Southeast University)

## 개요

- 현대 딥러닝 모델은 대규모 고품질 데이터셋으로 높은 정확도를 달성하지만, 학습 분포가 아닌 입력이나 적대적 노이즈에 대해 불안정한 예측을 보임
- **불확실성 정량화(Uncertainty Quantification)**는 의료 진단, 자율주행과 같은 고위험 애플리케이션에서 필수적 — Figure 1에서 쓰레기통이 버스로 오분류되는 예시를 통해 불확실성 정량화의 중요성을 설명
- **베이지안 신경망(BNN)**은 추론 시 가중치에 특정 노이즈를 도입하여 불확실성의 자연스러운 확률적 특성을 제공하지만, 기존 가속기는 이에 대한 하드웨어 지원이 부족
- 기존 BNN 가속 접근법(VIBNN 등)은 외부 가우시안 랜덤 넘버 생성기(GRNG)를 사용하여 노이즈를 생성하고 PE로 전달 → **추가 곱셈기/덧셈기 오버헤드**가 기존 PE와 비슷한 수준으로 발생
- 가중치의 평균값과 편차를 모두 로드해야 하므로 **대역폭 및 온칩 메모리 요구사항이 2배**로 증가
- ReRAM PIM 아키텍처는 높은 효율적 연산 능력과 **인시추(in-situ) 노이즈 생성**을 동시에 제공할 수 있는 유망한 후보이나, 하드웨어에서 생성하는 노이즈와 BNN 모델이 요구하는 노이즈 간에 **크나큰 격차(gap)**가 존재
- 이 노이즈 격차로 인해 불확실성 정량화 품질이 현저히 저하됨

## 방법론

### 3.1. ReRAM PIM 기반 노이즈 생성

- ReRAM 배열에는 **다중 노이즈 소스**가 존재 — 각 ReRAM 셀 주변의 물리적 특성에서 기원
- 기존 ReRAM PIM 설계에서 these 노이즈는 추론 정확도의 주요 단점으로 간주되었으나, 본 논문에서는 이를 BNN의 이점으로 전환
- 각 가중치에 **인시추 노이즈 생성** 가능 — 외부 노이즈 소스나 추가 대역폭 불필요
- ReRAM 셀의 물리적 특성을 활용한 자연적 노이즈 생성으로 기존 GRNG 기반 접근법 대비 하드웨어 오버헤드 대폭 절감

### 3.2. 노이즈 격차 해소

- 하드웨어에서 생성된 노이즈와 BNN 모델이 요구하는 노이즈 사이의 **정량적 격차**를 체계적으로 분석
- 노이즈 격차의 원인: ReRAM 셀의 불완전한 노이즈 모델, 제조 공정 변동, 온도 변화 등
- **보정 유닛**을 통해 노이즈 격차를 보정 — 실시간으로 노이즈 특성을 측정하고 조정
- 보정 유닛은 PIM 아키텍처에 통합되어 추가적인 외부 하드웨어 없이 동작

### 3.3. 불확실성 품질 평가

- W2W-PIM이 BNN 추론과 동시에 불확실성 품질을 평가할 수 있는 하드웨어 지원 제공
- 아웃-오브-트레이닝-분포(OOD) 샘플 및 적대적 샘플에 대한 높은 품질의 불확실성 정량화 달성
- 기존 DNN 대비 BNN의 불확실성 정량화 품질 차이를 Figure 1에서 시각적으로 비교

## 핵심 기여

- **핵심 기여**: ReRAM PIM 하드웨어의 노이즈를 BNN의 불확실성 정량화에 효과적으로 활용하는 최초의 종합적 프레임워크
- **혁신점**: 기존의 "노이즈=단점"이라는 고정관념을 "노이즈=자원"으로 전환 — ReRAM PIM의 물리적 특성을 BNN의 이점으로 활용
- **성능**: 높은 불확실성 정량화 품질과 높은 에너지 효율을 동시에 달성
- **실용성**: 의료 진단, 자율주행 등 고위험 분야에서의 BNN 배포를 위한 하드웨어 지원 제시
- **의의**: PIM 아키텍처와 Bayesian 딥러닝의 융합을 통해 새로운 연구 방향 제시 — 하드웨어의 제약을 소프트웨어적 기회로 전환하는 사례

## 주요 결과

- **ReRAM PIM 아키텍처 기반**: 기존 ReRAM PIM 가속기 설계를 확장하여 W2W-PIM 프레임워크 구현
- **보정 유닛 하드웨어**: PIM 칩 내부에 통합된 저오버헤드 보정 회로
- **소프트웨어 지원**: BNN 모델과의 호환성을 위한 프레임워크 수준의 지원
- **평가 환경**: 다양한 BNN 모델과 데이터셋에서의 포괄적 평가

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2022HPCA-summarize/enabling-high-quality-uncertainty-quantification-in-a-pim-designed-for-bayesian-neural-network.md|전체 요약 보기]]
