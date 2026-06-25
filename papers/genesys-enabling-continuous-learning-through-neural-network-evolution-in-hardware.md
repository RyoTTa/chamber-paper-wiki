---
tags: [paper, 2018, 2018MICRO, topic/llm, topic/ai, topic/accelerator]
venue: "MICRO 2018"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/genesys-enabling-continuous-learning-through-neural-network-evolution-in-hardware.md"
---

# GeneSys: Enabling Continuous Learning through Neural Network Evolution in Hardware

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Ananda Samajdar, Parth Mannan, Kartikay Garg, Tushar Krishna (Georgia Tech)

## 개요

현대 딥러닝 시스템은 수작업으로 조정된 NN 토폴로지, 대규모 레이블링 데이터, 대규모 컴퓨팅 리소스에 의존. 그러나 엣지 디바이스(로봇/드론)에서의 자율 학습을 위해서는 제한된 전력/에너지 예산, 지속적인 환경 상호작용, 클라우드 연결 불가 등의 문제를 해결해야 함. 이 논문은 EA(Evolutionary Algorithm) 기반 학습 시스템의 HW-SW 프로토타입인 GENESYS를 제시.

## 방법론

### NEAT 알고리즘
- **개체군(Population):** 매 세대에서 환경을 실행하여 적합도 점수를 얻는 NN 토폴로지 집합
- **유전자(Gene):** 노드 유전자(뉴런)와 연결 유전자(시냅스)로 구성
- **돌연변이/교차:** 유전 연산을 통해 더 나은 NN 구조 탐색
- **역전파 불필요:** 적합도 기반 학습으로 계산 비용 대폭 절감

### GENESYS 시스템
- **EvE (Evolution Engine):** NN의 토폴로지와 가중치를 하드웨어에서 완전히 진화
- **ADAM:** EvE가 생성한 비정형 NN의 효율적 추론 가속
- **병렬성 활용:** GLP(유전자 수준), PLP(개체군 수준) 병렬성 활용

## 핵심 기여

- EA 기반 학습 시스템을 위한 최초의 HW-SW 프로토타입 제시
- 역전파 없이 NN 토폴로지 진화를 하드웨어에서 가속화
- 15nm 기술 노드로 구현된 GENESYS SoC
- 엣지 디바이스에서의 자율 학습 가능성 입증

## 주요 결과

- CPU/GPU 대비 **2-5 orders of magnitude** 높은 에너지 효율성
- OpenAI Gym 환경에서 효과적 학습 입증
- 실시간 학습 가능성 확인
- 수작업 최적화나 역전파 없이 NN 토폴로지 진화 성공

## 한계점

- NE 알고리즘의 수렴 속도 및 최적해 도달 능력에 대한 추가 연구 필요
- 복잡한 실제 환경에서의 성능 검증 필요
- 상용화를 위한 추가 최적화 및 검증 필요

## 관련 개념

- [[paper-wiki/concepts/llm.md|LLM/AI]]
- [[paper-wiki/concepts/accelerator.md|Accelerator]]

## 전체 요약

[[../paper-summaries/2018MICRO-summarize/genesys-enabling-continuous-learning-through-neural-network-evolution-in-hardware.md|전체 요약 보기]]
