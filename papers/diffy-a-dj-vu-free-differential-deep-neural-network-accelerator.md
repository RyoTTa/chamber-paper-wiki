---
tags: [paper, 2018, 2018MICRO, topic/accelerator, topic/dnn, topic/computational-imaging]
venue: "MICRO 2018"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/diffy-a-dj-vu-free-differential-deep-neural-network-accelerator.md"
---

# Diffy: a Déjà vu-Free Differential Deep Neural Network Accelerator

**Venue:** MICRO 2018
**저자:** Mostafa Mahmoud, Kevin Siu, Andreas Moshovos (University of Toronto)

## 개요

연산 이미징(Computational Imaging) DNN은 공간적 상관관계가 높아 활성화 값의 델타(delta)를 활용하면 연산, 통신, 저장을 크게 줄일 수 있다. Diffy는 이를 활용한 차분 합성곱(Differential Convolution) 가속기로, 기존 가속기(VAA) 대비 7.1×, PRA 대비 1.41× 성능 향상을 달성한다.

## 방법론

### 차분 합성곱 (Differential Convolution)
- 인접 활성화 값의 차이(델타)를 사용하여 합성곱 연산 수행
- 수학적 근거: a'×w = (a×w) + (Δa×w) — 분배법칙 활용
- 공간적 상관관계가 높으면 Δa가 작아져 효과적 연산 항 대폭 감소

### Diffy 아키텍처
- PRA(Bit-Pragmatic) 가속기를 기반으로 확장
- **Differential Reconstruction Engine (DR)**: 차분 결과를 원래 출력으로 재구성
- **Delta Out 엔진**: 출력을 델타 형식으로 저장하여 다음 레이어로 전달
- AM 크기 축소: 256KB → 128KB (Delta D16 적용 시)

### 데이터 플로우
- 각 행의 첫 번째 출력은 원래 값으로 직접 계산, 나머지는 차분으로 계산
- 출력 재구성은 계단식(cascaded) 방식으로 수행
- 델타 인코딩으로 온칩/오프칩 저장 공간 및 트래픽 절감

## 핵심 기여

1. 연산 이미징 CI-DNN의 공간적 상관관계를 활용한 차분 합성곱 개념 제시
2. 실용적인 차분 합성곱 하드웨어 가속기(Diffy) 설계 및 구현
3. 온칩 저장 55% 절감, 오프칩 대역폭 2.5× 절감
4. 범용 CNN 가속기로도 활용 가능 (이미지 분류에서 6.1× 성능 향상)

## 주요 결과

- **성능**: VAA 대비 7.1×, PRA 대비 1.41× 스피드업
- **절대 성능**: HD 1920×1080에서 3.9~28.5 FPS
- **에너지 효율**: VAA 대비 1.83×, PRA 대비 1.36× 향상
- **저장 공간**: Delta D16으로 AM 348KB (NoCompression 964KB 대비 55% 감소)
- **오프칩 트래픽**: Delta D16으로 비압축 대비 22% 수준으로 감소
- **SCNN 대비**: 50% 희소성 가정 시 4.5× 성능

## 한계점

- 최대 30 FPS를 달성하려면 타일 수 확장 필요 (DnCNN: 32타일 + HBM2)
- VDSR은 높은 활성화 희소성으로 낮은 utilization (38~63%)
- 첫 번째/마지막 레이어에서 채널/필터 수 제한으로 활용률 저하

## 관련 개념

- [[paper-wiki/concepts/accelerator.md|DNN Accelerator]]: 값 인식 가속기 설계 공간 확장
- [[paper-wiki/concepts/computational-imaging.md|Computational Imaging]]: 연산 이미징 DNN의 공간적 상관관계 활용

## 관련 논문 요약

- [paper-summaries/2018MICRO-summarize/diffy-a-dj-vu-free-differential-deep-neural-network-accelerator.md]
