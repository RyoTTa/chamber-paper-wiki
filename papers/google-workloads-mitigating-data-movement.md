---
tags: [pim, data-movement, energy-efficiency, consumer-devices, google]
venue: ASPLOS
year: 2018
summary_path: paper-summaries/2018ASPLOS-summarize/google-workloads-for-consumer-devices-mitigating-data-movement-bottlenecks.md
---

# Google Workloads for Consumer Devices: Mitigating Data Movement Bottlenecks

## 개요

Google 소비자 워크로드(Chrome, TensorFlow Mobile, 비디오 재생/캡처)에서의 데이터 이동 병목 현상을 종합적으로 분석하고, PIM(Processing-in-Memory)을 통해 에너지 효율성과 성능을 크게 향상시키는 방안을 제시합니다.

## 방법론

- **데이터 이동 패턴 분석:** 각 워크로드에서의 메모리 접근 패턴과 병목 현상 식별
- **PIM 아키텍처 설계:** 소비자 디바이스의 제한된 면적 및 전력 제약을 고려한 PIM 로직 설계
- **워크로드별 최적화:** 각 워크로드의 특성에 맞는 PIM 적용 방안 제시

## 핵심 기여

1. Google 소비자 워크로드에서의 데이터 이동 병목 현상에 대한 종합적 분석
2. PIM이 다양한 소비자 워크로드에서 효과적인 해결책임을 입증
3. 소비자 디바이스의 에너지 효율성 향상을 위한 실용적인 설계 지침 제공

## 주요 결과

- PIM 적용 시 전체 워크로드 평균 55.4% 시스템 에너지 절감
- PIM 적용 시 전체 워크로드 평균 54.2% 실행 시간 단축
- Chrome 웹 브라우저: 에너지 48% 절감, 실행 시간 45% 단축
- TensorFlow Mobile: 에너지 62% 절감, 실행 시간 60% 단축
- 비디오 재생: 에너지 51% 절감, 실행 시간 50% 단축
- 비디오 캡처: 에너지 60% 절감, 실행 시간 58% 단축

## 한계점

- PIM 시뮬레이터 기반 분석으로 실제 하드웨어 구현과의 차이 존재
- 특정 Google 워크로드에 최적화된 분석
- 범용 소비자 디바이스에서의 검증 필요

## 관련 concept 페이지

- [[paper-wiki/concepts/pim|Processing-in-Memory]]
- [[paper-wiki/concepts/data-movement|Data Movement]]
- [[paper-wiki/concepts/energy-efficiency|Energy Efficiency]]

## 관련 논문 요약

- [google-workloads-for-consumer-devices-mitigating-data-movement-bottlenecks.md](paper-summaries/2018ASPLOS-summarize/google-workloads-for-consumer-devices-mitigating-data-movement-bottlenecks.md)