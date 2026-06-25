---
tags: [paper, 2019, 2019HPCA, topic/gpu, topic/pim]
venue: "25th IEEE International Symposium on High Performance Computer Architecture (HPCA '19)"
year: 2019
summary_path: "../paper-summaries/2019HPCA-summarize/pim-vr-customized-memory-cube-for-virtual-reality.md"
---

# PIM-VR: Erasing Motion Anomalies In Highly-Interactive Virtual Reality World With Customized Memory Cube

**Venue:** 25th IEEE International Symposium on High Performance Computer Architecture (HPCA '19)
**저자:** Chenhao Xie, Xingyao Zhang, Ang Li, Xin Fu, Shuaiwen Leon Song (University of Houston, Pacific Northwest National Lab)

## 개요

- VR(Virtual Reality)은 엔터테인먼트, 의료 시뮬레이션, 교육 등에서 빠르게 성장하고 있으나, 사용자 몰입도를 결정짓는 핵심 요소인 Motion-to-Photon Delay(MPD)를 충분히 줄이지 못함
- MPD가 길면 사용자는 judder, lagging, motion sickness 등 불쾌한 시각적 이상을 경험하며, 이상적인 MPD는 **7ms 미만**이어야 함
- 현대 VR 디스플레이(90~120Hz)는 화면 갱신 주기가 10ms 이내이나, 애플리케이션 지연으로 인해 업데이트된 프레임이 갱신 데드라인 전에 준비되지 못하는 문제가 빈번
- 현재 GPU 기반 ATW(Asynchronous Time Warp)는 두 가지 핵심 문제로 인해 이상적인 MPD를 달성하지 못함:
  1. **비효율적 VR 실행 모델:** GPU가 렌더링을 수행하는 동안 ATW를 삽입하면 리소스 경쟁과 불가피한 긴 프리emption 오버헤드 발생
  2. **집약적 오프칩 메모리 액세스:** 프레임 크기가 GPU 온칩 스토리지를 크게 초과하여频繁한 오프칩 메모리 로드로 성능·에너지 비용 발생

## 방법론

### 3.1. VR 워크플로우 분석

- VR 시스템: HMD 센서 → 애플리케이션 → GPU 렌더링 → 타임 워프 → 디스플레이 파이프라인
- ATW는 이전에 렌더링된 프레임을 최신 HMD 위치 정보로 재투영(re-projection)하여 렌더링 지연을 보상
- 이상적 ATW: 렌더링과 비동기적으로 동작하여 렌더링이 지연되어도 화면 갱신 데드라인 전에 warping 수행 가능
- GPU 기반 ATW: 현재 렌더링 작업을 중단(preemption)하고 ATW를 실행해야 하므로 길고 예측 불가능한 지연 발생

### 3.2. PIM 기반 ATW 아키텍처

- **메모리 해빙(Memory Binning):** 프레임 버퍼의 픽셀 데이터를 HMC 로직 레이너로 직접 전달하여 오프칩 메모리 액세스 제거
- **워핑 엔진(Warping Engine):** 렌즈 왜곡 보정과 투영 변환을 HMC 로직 레이어에서 처리
- **디스플레이 인터페이스:** Warping된 이미지를 디스플레이 버퍼로 전송

### 3.3. 중복성 감소 메커니즘

- VR의 양안 스테레오스코픽 프레임은 좌·우 눈 프레임 간 높은 공간적 중존재
- 좌안 프레임의 중복 픽셀 데이터를 제거하여 메모리 대역폭 요구 사항 대폭 감소
- ATW 연산 자체를 단순화하여 처리 효율성 향상

## 핵심 기여

- PIM-VR은 3D 적층 메모리의 로직 레이어에서 ATW를 비동기적으로 실행하여 VR의 핵심 문제인 MPD를 이상적인 수준으로 해결
- GPU와 리소스 경쟁 없이 PIM에서 ATW를 수행함으로써 preemption 오버헤드 완전 제거
- 양안 중복성 감소로 메모리 대역폭 요구 대폭 축소
- 미래 고해상도 VR 시나리오에서도 열 제약 내에서 잘 확장되는 실용적 설계

## 주요 결과

- HMC 시뮬레이터 프레임워크 기반 물리적 플랫폼 설계
- 실제 VR 애플리케이션 세트로 평가
- PIM 로직 레이어: 인오더(in-order) CPU 코어 기반 설계
- GPU SM 및 텍스처/래스터화 유닛을 HMC 로직 레이어에 통합하지 않음 (전력 밀도 제약 충족)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2019HPCA-summarize/pim-vr-customized-memory-cube-for-virtual-reality.md|전체 요약 보기]]
