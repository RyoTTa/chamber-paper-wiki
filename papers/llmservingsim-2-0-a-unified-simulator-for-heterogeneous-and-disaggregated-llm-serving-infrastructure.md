---
tags: [paper, 2026, 2026TEMP, topic/llm, topic/simulation, topic/heterogeneous]
venue: "IEEE International Symposium on Performance Analysis of Systems and Software (ISPASS) 2026"
year: 2026
summary_path: "../paper-summaries/TEMP-summarize/llmservingsim-2-0-a-unified-simulator-for-heterogeneous-and-disaggregated-llm-serving-infrastructure.md"
---

# LLMServingSim 2.0: A Unified Simulator for Heterogeneous and Disaggregated LLM Serving Infrastructure

**Venue:** IEEE International Symposium on Performance Analysis of Systems and Software (ISPASS) 2026
**저자:** Jaehong Cho, Hyunmin Choi, Guseul Heo, Jongse Park (KAIST)

## 개요

- 최신 LLM 서빙 인프라는 GPU 중심의 동질적 배포에서 이질적 하드웨어와 분산 아키텍처로 빠르게 진화 중
- 현대 서빙 시스템은 prefill-decode 분리, expert parallelism, prefix caching 등의 분산 기법을 활용하여 확장성과 효율성을 향상
- 그러나 기존 시뮬레이터들은 이질적 하드웨어와 분산 서빙 기법 간의 런타임 상호작용을 통합적으로 모델링하지 못함
- LLM 서빙 성능은 하드웨어나 소프트웨어 선택이 단독으로 결정하는 것이 아니라, 런타임에서의 스케줄링, 데이터 이동, 인터커넥트 동작의 상호작용에 의해 결정됨

## 방법론

### 3.1. Interaction-awareness
- 서빙 소프트웨어 결정과 이질적 하드웨어 동작 간의 런타임 상호작용을 명시적으로 모델링
- batching, routing, placement, caching, offloading이 진화하는 시스템 상태에 적응하는 방식 포착
- 소프트웨어 정책과 하드웨어 상태 간의 피드백에서 발생하는 성능 동작 분석 가능

### 3.2. Unified modeling of heterogeneity and disaggregation
- 이질적 가속기, 다계층 메모리 시스템, 분산 서빙 아키텍처의 통합 표현 제공
- 하드웨어 조합이 달라질 때 분산 서빙 기법이 어떻게 동작하는지 연구 가능
- 하드웨어와 소프트웨어 효과를 분리하지 않고 통합적으로 평가

### 3.3. Runtime-driven serving dynamics
- 서빙 결정을 런타임 기반 시뮬레이션 루프에 임베딩
- 동적 요청 흐름, 리소스 경쟁, 인터커넥트 효과에서 시스템 성능이 발현되도록 설계
- 대기열 형성, 경쟁 증폭, 위상별 동작과 같은 시간적 효과 포착

### 3.4. Extensibility to emerging hardware
- 프로파일 기반 연산자 모델링을 통해 새로운 가속기와 메모리 기술의 저 노력 통합
- 서빙 모델 재구성 없이 미래 하드웨어 설계 평가 가능
- LLM 서빙 인프라가 계속 진화함에 따라 새로운 하드웨어-소프트웨어 조합의 빠른 탐색 지원

### 3.5. Power-aware modeling
- 시뮬레이션 프레임워크에 전력 모델링 통합
- 성능과 에너지 관련 트레이드오프의 공동 평가 가능
- 컴퓨팅, 메모리, 데이터 이동 활동을 전력 특성과 연관시켜 분석

## 핵심 기여

- **핵심 기여**: 이질적이고 분산된 LLM 서빙 인프라에서의 하드웨어-소프트웨어 상호작용을 분석할 수 있는 통합 시뮬레이터 제안
- **실용성**: 프로파일 기반 모델링을 통해 새로운 하드웨어 통합 지원, 시뮬레이션 시간 약 10분 유지
- **성능**: 실제 서빙 배포와 비교하여 핵심 성능, 메모리, 전력 지표를 평균 오차 0.95%로 재현
- **확장성**: 다양한 이질적 하드웨어와 분산 서빙 기법을 통합적으로 모델링
- **의의**: 미래 LLM 서빙 인프라의 하드웨어-소프트웨어 공동 설계를 위한 실용적인 도구 제공

## 주요 결과

- **정확도**: 평균 오차 0.95%로 실제 배포와 높은 정확도 달성
- **시뮬레이션 시간**: 복잡한 시스템 구성에서도 약 10분 유지
- **지표**: 처리량, 지연 시간 (TTFT, TPOT), 메모리 사용량, 전력 소비 재현
- **비교**: 기존 시뮬레이터들이 부분적으로만 지원했던 기능들을 통합적으로 지원

## 한계점

- 프로파일 기반 모델링의 정확도가 프로파일 데이터의 품질에 의존
- 새로운 하드웨어 기술의 시뮬레이션을 위해 프로파일 데이터 수집 필요
- 매우 복잡한 시스템 구성에서의 시뮬레이션 정확도 추가 검증 필요

## 관련 개념

- [[paper-wiki/concepts/llm.md|Large Language Model]]
- [[paper-wiki/concepts/simulation.md|Simulation]]
- [[paper-wiki/concepts/heterogeneous.md|Heterogeneous Computing]]

## 전체 요약

[[../paper-summaries/TEMP-summarize/llmservingsim-2-0-a-unified-simulator-for-heterogeneous-and-disaggregated-llm-serving-infrastructure.md|전체 요약 보기]]