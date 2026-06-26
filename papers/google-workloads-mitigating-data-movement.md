---
tags: [paper, 2018, 2018ASPLOS, topic/pim]
venue: "ASPLOS 2018 (Architectural Support for Programming Languages and Operating Systems)"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/google-workloads-for-consumer-devices-mitigating-data-movement-bottlenecks.md"
---

# Google Workloads for Consumer Devices: Mitigating Data Movement Bottlenecks

**Venue:** ASPLOS 2018 (Architectural Support for Programming Languages and Operating Systems)
**저자:** Amirali Boroumand (Carnegie Mellon University), Saugata Ghose (Carnegie Mellon University), Youngsok Kim (Seoul National University), Rachata Ausavarungnirun (Carnegie Mellon University), Eric Shiu (Google), Rahul Thakur (Google), Daehyun Kim (Samsung Research/Google), Aki Kuusela (Google), Allan Knies (Google), Parthasarathy Ranganathan (Google), Onur Mutlu (ETH Zürich/Carnegie Mellon University)

## 개요

- 소비자 디바이스(스마트폰, 태블릿, Chromebook, 웨어러블 디바이스)의 폭발적 성장
- 2017년 전 세계 스마트폰 사용자 23억 명, 태블릿 사용자 12억 명
- 제한된 배터리 용량과 열 전력 예산으로 인해 에너지 효율성이 최우선 관심사
- 데이터 이동이 소비자 디바이스의 전체 시스템 에너지와 실행 시간의 주요 기여자
- 메모리 시스템과 컴퓨팅 유닛 간 데이터 이동 비용이 계산 비용보다 significantly 높음
- 리튬이온 배터리 용량은 지난 20년간 2배 증가하는 데 그침
- 소비자 디바이스의 열 전력 방산이 심각한 성능 제약 요건으로 부상

## 방법론

### 3.1. Chrome 웹 브라우저
- 웹 페이지 렌더링 과정에서의 데이터 이동 패턴 분석
- HTML 파싱, CSS 처리, JavaScript 실행에서의 메모리 접근 특성
- PIM 적용 가능 프리미티브: 문자열 처리, 이미지 디코딩, 데이터 압축/해제

### 3.2. TensorFlow Mobile
- 모바일 기기에서의 머신러닝 추론 워크로드 분석
- 텐서 연산에서의 데이터 이동 병목 현상 식별
- PIM 적용 가능 프리미티브: 행렬 곱셈, 합산 연산, 활성화 함수

### 3.3. 비디오 재생 및 캡처
- YouTube, Google Hangouts 등의 비디오 서비스에서의 워크로드 분석
- 비디오 디코딩 및 인코딩 과정에서의 데이터 이동 패턴
- PIM 적용 가능 프리미티브: 비디오 디코딩, 이미지 처리, 오디오 처리

### 3.4. PIM 아키텍처 설계 고려사항
- 소비자 디바이스의 제한된 면적 및 전력 제약 고려
- 간단한 코어 또는 특화 가속기로 구성된 PIM 로직
- 기존 메모리 아키텍처와의 통합 방안

## 핵심 기여

- 데이터 이동이 소비자 디바이스의 주요 에너지 및 성능 병목임을 종합적으로 분석
- PIM이 다양한 Google 소비자 워크로드에서 효과적인 해결책임을 입증
- 소비자 디바이스의 에너지 효율성 향상을 위한 실용적인 설계 지침 제공
- 향후 소비자 디바이스 아키텍처 설계에서 데이터 이동 최소화의 중요성 강조

## 주요 결과

- PIM 시뮬레이터 기반 분석
- 실제 Google 소비자 워크로드의 프로파일링
- 에너지 소모 모델링 및 성능 분석
- 기존 메모리 시스템과의 비교 평가

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2018ASPLOS-summarize/google-workloads-for-consumer-devices-mitigating-data-movement-bottlenecks.md|전체 요약 보기]]
