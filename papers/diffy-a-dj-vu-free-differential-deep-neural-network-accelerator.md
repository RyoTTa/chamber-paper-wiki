---
tags: [paper, 2018, 2018MICRO, topic/compression, topic/dram, topic/gpu]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/diffy-a-dj-vu-free-differential-deep-neural-network-accelerator.md"
---

# Diffy: a Déjà vu-Free Differential Deep Neural Network Accelerator

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Mostafa Mahmoud, Kevin Siu, Andreas Moshovos (University of Toronto)

## 개요

- 딥러닝 기반 연산 이미징(Computational Imaging, CI) 기법들이 이미지 노이즈 제거, 디매저리킹, 슈퍼해결링, 디블러링 등에서 기존 분석적 방법과 동등 이상의 성능을 달성
- 그러나 DNN 기반 연산 이미징은 높은 연산량과 데이터 공급 요구사항으로 인해 모바일 기기, 디지털 카메라, 의료 기기, 자율주행 시스템 등 비용/전력/에너지/폼팩터 제약이 있는 임베디드 디바이스에 배포하기 어려움
- 기존 DNN 가속기들은 주로 이미지 분류 CNN에 초점을 맞추었으나, 연산 이미징 CI-DNN은 픽셀 단위 예측(per-pixel prediction)을 수행하여 구조와 동작 방식이 다름
- CI-DNN의 핵심 특성: **공간적 상관관계(Spatial Correlation)** — 인접 활성화 값들이 서로 가까운 값을 가져 원래 값보다 델타(delta)로 표현하면 훨씬 효율적
- 기존 가속기는 값의 절대값을 처리하는 반면, CI-DNN에서는 인접 값 간의 차이(델타)를 처리하면 연산, 통신, 저장 모두를 크게 줄일 수 있음

## 방법론

### 3.1. 차분 합성곱 (Differential Convolution)

- 기존 합성곱: o(n,y,x) = Σ Σ Σ w(k,j,i) × a(k,j+y×S, i+x×S)
- 차분 합성곱: o(n,y,x+1) = o(n,y,x) + ⟨w_n, Δa⟩
  - Δa(k,j,i) = a(k,j+y×S, i+(x+1)×S) - a(k,j+y×S, i+x×S)
- 각 행의 첫 번째 출력은 원래 활성화 값으로 직접 계산, 나머지는 차분으로 계산
- 출력 재구성은 계단식(cascaded) 방식으로 수행 — 이전 출력에 현재 델타 내적 결과를 더함

### 3.2. Diffy 타일 구조

- **기존 PRA 타일**: 16×16 Serial IP (SIP) 유닛 그리드, 각 SIP는 16개 가중치를 시리얼로 처리
- **Diffy 수정 사항**:
  - 각 SIP에 **Differential Reconstruction Engine (DR)** 추가
    - 첫 번째 창의 출력을 그대로 전달하거나, 중간 결과를 재구성하거나, 일반 합성곱으로 전환
  - 각 타일에 **Delta Out 엔진** 추가
    - 현재 레이어의 출력 브릭을 델타 형식으로 변환하여 AM에 저장
    - 16-to-1 멀티플렉서로 AM 뱅크 선택, 2단계 처리로 하드웨어 재사용
  - AM 크기 축소: PRA의 256KB → Diffy의 128KB (Delta D16 적용 시)

### 3.3. 데이터 플로우 및 메모리 시스템

- **오프 칩 전략**: 각 가중치/활성화를 레이어당 한 번만 읽고, 출력을 한 번만 기록
- **AM 크기**: 충분한 입력 행을 저장하여 두 전체 윈도우 행과 두 출력 행을 온칩에 유지
- **델타 인코딩**: Dynamic Stripes 방식과 유사하게 16개 활성화 그룹별 4비트 헤더로 정밀도 저장
- **오프치 메모리 기술**: DDR3-1600부터 HBM2까지 다양한 기술 고려
- **최소 온칩 메모리**: Delta D16 적용 시 AM 348KB (NoCompression 대비 55% 감소, Raw D16 대비 32% 감소)

## 핵심 기여

- **핵심 기여**: 연산 이미징 CI-DNN의 공간적 상관관계를 활용한 차분 합성곱 개념과 Diffy 가속기 제안
- **성능**: 기존 최첨단 가속기(VAA) 대비 **7.1×**, PRA 대비 **1.41×** 성능 향상
- **효율성**: 온칩 저장 **55% 절감**, 오프칩 대역폭 **2.5× 절감**, 에너지 효율 **1.83×** 향상
- **실용성**: 실시간 HD 이미지 처리가 가능한 성능 제공 (적절한 타일 수 확장 시)
- **범용성**: CI-DNN 뿐만 아니라 이미지 분류 CNN에서도 **6.1×** 성능 향상 — 범용 CNN 가속기로 활용 가능
- **의의**: DNN 가속기 설계에서 데이터 값의 상관관계를 활용한 새로운 차원의 최적화 제시, 향후 다른 모델 아키텍처 및 학습에도 적용 가능성 시사

## 주요 결과

- **시뮬레이터**: 커 사이클 정확 시뮬레이터 (custom cycle-accurate simulator)
- **하드웨어 구현**: Verilog로 RTL 구현, Synopsys Design Compiler로 합성
- **레이아웃**: Cadence Innovus 사용, TSMC 65nm 기술
- **전력 추정**: Mentor Graphics ModelSim으로 회로 활동성 캡처, CACTI로 SRAM 면적/전력 모델링
- **구성 파라미터**:
  - 타일 수: 4개
  - 필터/타일: 16개
  - 가중치/필터: 16개
  - 주파수: 1GHz
  - 오프칩 메모리: 4GB LPDDR4-3200

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/diffy-a-dj-vu-free-differential-deep-neural-network-accelerator.md|전체 요약 보기]]
