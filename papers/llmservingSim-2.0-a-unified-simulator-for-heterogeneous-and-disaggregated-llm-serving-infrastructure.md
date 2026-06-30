---
tags: [paper, 2026, 2026ISPASS, topic/llm, topic/simulator, topic/serving]
venue: "ISPASS 2026"
year: 2026
summary_path: "../paper-summaries/2026ISPASS-summarize/llmservingSim-2.0-a-unified-simulator-for-heterogeneous-and-disaggregated-llm-serving-infrastructure.md"
---

# LLMServingSim 2.0: A Unified Simulator for Heterogeneous and Disaggregated LLM Serving Infrastructure

**Venue:** ISPASS 2026
**저자:** Jaehong Cho, Hyunmin Choi, Guseul Heo, Jongse Park (KAIST)

## 개요

LLM 서빙 인프라가 이종성(heterogeneity)과 분리(disaggregation) 방향으로 진화하고 있다. 현대 배포는 다양한 가속기(TPU, NPU, PIM 등)를 통합하며, 시스템 소프트웨어는 계산, 메모리, 모델 컴포넌트를 분산 리소스로 분리한다. LLMServingSim 2.0은 이러한 이종적이고 분리된 LLM 서빙 인프라에서의 런타임 기반 하드웨어-소프트웨어 상호작용을 분석할 수 있는 통합 시뮬레이터이다.

## 방법론

### 상호작용 인식 (Interaction-awareness)
- 서빙 소프트웨어 결정과 하드웨어 동작의 런타임 상호작용 명시적 모델링
- 배칭, 라우팅, 배치, 캐싱, 오프로딩의 동적 적응 포착

### 이종성 및 분리의 통합 모델링
- 이종 가속기, 다층 메모리 시스템, 분리된 서빙 아키텍처의 통합 표현
- 결합된 상호작용에서 발생하는 시스템 동작의 일관된 평가

### 런타임 기반 서빙 역학
- 동적 요청 흐름, 리소스 경쟁, 인터커넥트 효과에서 성능이 나타나도록 시뮬레이션
- 대기열 형성, 경쟁 증폭, 위상 의존적 동작 포착

### 이머징 하드웨어 확장성
- 프로파일 기반 연산자 모델링을 통한 새로운 가속기 및 메모리 기술 통합
- 서빙 모델 재구성 없이 미래 하드웨어 설계 평가 가능

### 전력 인식 모델링
- 계산, 메모리, 데이터 이동 활동을 전력 특성과 연관
- 성능 및 에너지 관련 트레이드오프 공동 평가

## 핵심 기여

- 이종적이고 분리된 LLM 서빙 인프라를 위한 통합 시뮬레이터 최초 제시
- 런타임 기반 시뮬레이션을 통한 동적 서빙 동작 포착
- 프로파일 기반 모델링으로 이머징 하드웨어의 손쉬운 통합
- 전력 인식 모델링을 통한 성능-에너지 트레이드오프 분석

## 주요 결과

- 실제 서빙 배포 대비 평균 오차 **0.95%**로 주요 지표 재현
- 복잡한 시스템 구성에서도 약 **10분**의 실용적인 시뮬레이션 시간
- Throughput, TTFT, TPOT, 메모리 사용량, 전력 소비 등 주요 지표 포착
- 다양한 워크로드와 하드웨어 플랫폼에서 일관된 정확도 달성

## 한계점

- 프로파일 기반 모델링의 정확도는 프로파일 데이터 품질에 의존
- 복잡한 시스템 동작의 완전한 포kończ를 위한 추가 검증 필요

## 관련 개념

- [[paper-wiki/concepts/llm.md|LLM Inference]]
- [[paper-wiki/concepts/simulator.md|System Simulation]]

## 전체 요약

[[../paper-summaries/2026ISPASS-summarize/llmservingSim-2.0-a-unified-simulator-for-heterogeneous-and-disaggregated-llm-serving-infrastructure.md|전체 요약 보기]]
