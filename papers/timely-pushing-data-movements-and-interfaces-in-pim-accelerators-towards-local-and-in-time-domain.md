---
tags: [paper, 2020, 2020ISCA, topic/pim]
venue: "2020 ACM/IEEE 47th Annual International Symposium on Computer Architecture (ISCA 2020)"
year: 2020
summary_path: "../paper-summaries/2020ISCA-summarize/timely-pushing-data-movements-and-interfaces-in-pim-accelerators-towards-local-and-in-time-domain.md"
---

# TIMELY: Pushing Data Movements and Interfaces in PIM Accelerators Towards Local and in Time Domain

**Venue:** 2020 ACM/IEEE 47th Annual International Symposium on Computer Architecture (ISCA 2020)
**저자:** Weitao Li, Pengfei Xu, Yang Zhao, Haitong Li, Yuan Xie, Yingyan Lin (Rice University, Stanford University, University of California Santa Barbara)

## 개요

- IoT 디바이스(스마트폰, 센서, 드론 등)는 배터리 구동과 소형 폼 팩으로 인해 에너지/연산 자원이 제한적이며, CNN/DNN 기반 애플리케이션의 에너지 소비는 IoT 배터리를 빠르게 소모함 (DianNao에서 메모리 접근이 에너지의 95% 차지).
- ReRAM 기반 PIM(R2PIM) 가속기는 가중치를 메모리에 고정시켜 데이터 이동 비용을 줄이나, PRIME에서 확인된 바와 같이 입력/부분합(Psum) 이동 비용이 전체 에너지의 83%를 차지하는瓶颈이 존재.
- ISAAC에서는 ADC/DAC 인터페이스 회로의 에너지가 전체의 61%를 차지하며, 기존 R2PIM 가속기(PRIME, ISAAC, PipeLayer)의 에너지 효율성을 심각하게 제한.
- 기존 R2PIM 가속기의 compute density도 메모리 벽(memory wall)과 인터페이스 오버헤드로 인해 충분히 활용되지 못함.

## 방법론

### 3.1. Analog Local Buffers (ALBs)

- ReRAM 크로스바 내부에 작은 크기의 아날로그 버퍼를 배치하여 동일 크로스바에서의 반복적인 입력/Psum 접근을 로컬에서 처리
- ALB는 아날로그 도메인에서 동작하므로 D/A, A/D 변환 불필요 → 변환 에너지 완전 제거
- Figure 4에서 크로스바당 ALB 배치 구조 설명: 각 크로스바의 행/열 끝에 위치
- 입력 특성 맵(input feature map)의 지역적 재사용(local reuse)과 출력 채널 간 가중치 공유를 ALB에서 활용
- ALB 크기가 작아 면적 오버헤드 최소화하면서 에너지 절감 효과 극대화

### 3.2. Time-Domain Interfaces (TDIs)

- 전통적 DAC/ADC는 아날로그 전압 신호를 사용하는 반면, TDI는 시간 신호(time signal)를 사용
- DTC(Digital-to-Time Converter)와 TDC(Time-to-Digital Converter)는 디지털 회로로 구현 가능하여:
  - DAC/ADC 대비 에너지 소비 대폭 절감
  - PVT(Process, Voltage, Temperature) 변동에 강건
  - 공정 스케일링(technology scaling) 시 에너지 효율성 향상
- 디지털 신호 Dx를 시간 지연 Tx로 표현 (고전압/저전압 = 1/0)
- TIMELY에서 ALB와 결합하면 변환 횟수 자체를 대폭 줄여 추가 에너지 절감

### 3.3. Only-Once Input Read (O2IR) 매핑

- 기존 R2PIM 가속기는 CNN 컨볼루션 연산에서 입력 픽셀을 여러 번 읽음 (D×Z×G/S²회 재사용)
- O2IR은 입력을 한 번만 읽고 ALB에 저장한 뒤, 이후 모든 재사용은 로컬에서 처리
- 매핑 알고리즘:
  1. 입력 특성 맵을 크로스바에 할당
  2. 출력 채널 필터를 크로스바에 매핑
  3. O2IR 제약 조건 하에서 입력/Psum의 접근 패턴 최적화
- D/A 변환 횟수: 기존 대비 최대 수십 배 절감 (입력 재사용 횟수에 비례)
- 매핑의 정확성과 일반화를 위해 수학적 모델로 검증

## 핵심 기여

- TIMELY는 ReRAM 기반 PIM 가속기의 두 가지 핵심 bottleneck(입력/Psum 이동 + ADC/DAC 인터페이스)을 동시에 해결하는 세 가지 혁신적 기법 제안.
- ALB(아날로그 데이터 국소성), TDI(시간 영역 인터페이스), O2IR(한 번만 읽는 매핑)의 조합으로 **PRIME 대비 18.2× 에너지 효율성, PipeLayer 대비 31.2× compute density, PRIME 대비 736.6× 처리량** 달성.
- 10개 이상 CNN/DNN 모델에서의 포괄적 평가와 ablation study를 통해 각 기법의 기여도를 정량적으로 검증.
- ReRAM 기반 PIM 가속기의 에너지 효율성을 한 세대 높이는 수준의 연구로, IoT/엣지 디바이스에서의 DNN 추론 가속화에 중요한 기여.

## 주요 결과

- **설계 언어**: RTL 기반 하드웨어 설계
- **평가 도구**: gem5 시뮬레이터 기반 R2PIM 아키텍처 모델링 + 커스텀 에너지 모델
- **시스템 구성 요소**:
  - ReRAM 크로스바 배열 (B×B 크기, 기본값 B=16)
  - ALB (Analog Local Buffer): 크로스바 내부에 위치
  - TDI (Time-Domain Interface): DTC/TDC 기반
  - 메모리 컨트롤러 및 인터커넥트
- **지원 모델**: CNN(ResNet, VGG, MobileNet 등) + DNN(MLP 등) 10개 이상 모델
- **다양한 칩 구성**: 다양한 크로스바 크기, 서브칩 수, 메모리 용량으로 실험

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2020ISCA-summarize/timely-pushing-data-movements-and-interfaces-in-pim-accelerators-towards-local-and-in-time-domain.md|전체 요약 보기]]
