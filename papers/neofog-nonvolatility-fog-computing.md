---
tags: [paper, 2018, 2018ASPLOS]
venue: "ASPLOS 2018 (Architectural Support for Programming Languages and Operating Systems)"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/neofog-nonvolatility-exploiting-optimizations-for-fog-computing.md"
---

# NEOFog: Nonvolatility-Exploiting Optimizations for Fog Computing

**Venue:** ASPLOS 2018 (Architectural Support for Programming Languages and Operating Systems)
**저자:** Kaisheng Ma, Jinyang Li, Tongda Wu, Zhibo Wang, Xueqing Li, Yongpan Liu, Yuan Xie, Mahmut Taylan Kandemir, Jack Sampson, Vijaykrishnan Narayanan (The Pennsylvania State University, Tsinghua University, University of California at Santa Barbara)

## 개요

- 에너지 하베스팅 시나리오에서 비휘발성 프로세서(NVP)는 유망한 솔루션으로 부상
- 무선 센서 네트워크(WSN)는 에너지 하베스팅의 가장 중요한 애플리케이션 중 하나
- 분산 감지 시스템에서 위치, 에너지 하베스터 각도, 전원 등의 차이로 인해 각 노드가 사용 가능한 에너지 양이 다름
- 기존 접근법은 비휘발성 컴퓨팅 접근법이 제공하는 기능의 맥락에서 이러한 문제를 검토하지 않음
- 에너지 하베스팅 전력의 비신뢰성으로 인해 컴퓨팅과 통신 모두 에너지 비용이 높음
- 센서 노드 수준에서 컴퓨팅과 통신 비용에 대한 기존 가정이 더 이상 유효하지 않게 됨

## 방법론

### 3.1. 비휘발성 프로세서(NVP) 활용

- 통합 비휘발성 리소스의 하드웨어 및 소프트웨어 관리 발전 활용
- 불안정 전원 환경에서의 컴퓨팅 신뢰성 및 효율성 향상
- NVP가 휘발성 프로세서보다 더 나은 전진(progress)을 달성함을 입증

### 3.2. 비휘발성 RF 컨트롤러(NVRF)

- RF 모듈 초기화 가속화를 통한 데이터 전송 시간 및 에너지 비용 절감
- 통신 경로에서의 비휘발성 활용을 통한 플랫폼 최적화
- 무선 통신 초기화 비용을 크게 감소

### 3.3. 로드 밸런싱 알고리즘

- 컴퓨팅 및 통신 요구사항의 균형을 맞추기 위한 새로운 알고리즘
- 에너지 하베스팅 노드들의 에너지 불균형을 고려한 동적 작업 분배
- 분산 시스템에서의 효율적인 리소스 활용

## 핵심 기여

- 비휘발성 프로세서와 RF 컨트롤러의 통합을 통해 에너지 하베스팅 시스템의 컴퓨팅 및 통신 효율성을 크게 향상
- 기존 가정을 재검토하고 새로운 최적화 기회를 탐구하는 연구 필요성 강조
- IoT 및 퍼지 컴퓨팅 환경에서의 실용적인 적용 가능성 입증
-未来的 에너지 하베스팅 시스템 설계에 중요한 시사점 제공

---

## 참고 자료

- 논문 원문: `/home/ryotta205/Chamber_paper/paper-source/2018ASPLOS/NEOFog_Nonvolatility_Fog_Computing.pdf`
- 관련 개념: Nonvolatile Processor, Fog Computing, Energy Harvesting, Wireless Sensor Network

## 주요 결과

- NEOFog 시스템 아키텍처 구현
- 비휘발성 프로세서 기반 하드웨어 플랫폼
- 에너지 하베스팅 및 관리 소프트웨어
- 무선 센서 네트워크 통신 스택

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- 개념 매칭 없음

## 전체 요약

[[../paper-summaries/2018ASPLOS-summarize/neofog-nonvolatility-exploiting-optimizations-for-fog-computing.md|전체 요약 보기]]
