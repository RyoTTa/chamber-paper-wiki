---
tags: [paper, 2018, 2018MICRO, topic/storage]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/genesys-enabling-continuous-learning-through-neural-network-evolution-in-hardware.md"
---

# GeneSys: Enabling Continuous Learning through Neural Network Evolution in Hardware

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Ananda Samajdar, Parth Mannan, Kartikay Garg, Tushar Krishna (Georgia Tech)

## 개요

- 현대 딥러닝 시스템은 (1) 수작업으로 조정된 신경망 토폴로지, (2) 대규모 레이블링된 데이터, (3) 대규모 컴퓨팅 리소스를 기반으로 구축
- 그러나 적응형 범용 지능 시스템은 미지의 환경에서 자율적으로 학습해야 하며, 위 3요소 중 일부 또는 전부에 접근할 수 없을 수 있음
- 강화학습(RL) 및 진화 알고리즘(EA) 기반 방법이 이 문제를 해결할 수 있지만, 엣지 디바이스(로봇/드론)에서의 배포에는 다음과 같은 문제 존재:
  - **제한된 전력/에너지 예산:** 엣지 디바이스의 리소스 제약
  - **지속적인 환경 상호작용:** 생애 학습(life-long learning) 필요
  - **클라우드 연결 불가:** 무거운 처리를 오프로딩할 수 없음
- RL 알고리즘은 보상 수신 시마다 역전파(backpropagation)를 통해 NN을 학습해야 하며, 이는 계산 및 메모리 측면에서 매우 비용이 높음
- 지도학습의 한계:
  - 구조화된 레이블 데이터에 대한 의존성
  - NN 토폴로지에 대한 높은 의존성
  - 극도로 높은 계산 및 메모리 요구사항 (주 단위 학습 시간)

## 방법론

### 3.1. NEAT 알고리즘 특성

- **개체군(Population):** 매 세대에서 환경을 실행하여 적합도 점수를 얻는 NN 토폴로지 집합
- **유전자(Gene):**
  - **노드 유전자:** NN 노드(뉴런)를 나타냄 - ID, 활성화 함수(ReLU 등), 바이어스 포함
  - **연결 유전자:** 시냅스를 나타냄 - 시작/종료 노드, 가중치, 활성화 여부 포함
- **유전체(Genome):** 하나의 NN을 고유하게 설명하는 유전자 집합
- **초기화:** 입력/출력 레이어만 포함하는 매우 단순한 토폴로지로 시작
- **돌연변이(Mutation):**
  - 가중치 변경: 부모 유전자의 가중치를 소폭 변경
  - 유전자 추가: 새 유전자를 기본 속성으로 추가
  - 유전자 삭제: 노드 또는 연결 제거
- **교차(Crossover):** 부모 유전자의 속성을 상대 적합도에 따라 선택하여 자식 유전자 생성

### 3.2. EvE (Evolution Engine) 가속기

- **역할:** EA 기반 학습의 하드웨어 가속
- **기능:**
  - NN의 토폴로지와 가중치를 하드웨어에서 완전히 진화
  - 역전파(backpropagation) 없이 적합도 기반 학습
  - GLP(유전자 수준 병렬성) 활용: 각 유전자의 독립적인 연산 병렬화
  - PLP(개체군 수준 병렬성) 활용: 여러 NN 개체의 병렬 평가
- **설계 고려사항:**
  - 유전 연산(돌연변이, 교차)의 병렬 실행
  - 적합도 평가를 위한 환경 상호작용 효율적 처리
  - 메모리 접근 패턴 최적화

### 3.3. ADAM (Accelerator for Dense Addition & Multiplication)

- **역할:** EvE가 생성한 비정형 NN의 효율적 추론
- **특징:**
  - 비정형(irregular) NN 구조에 최적화
  - 밀도 높은 덧셈과 곱셈 연산 가속
  - EvE가 진화시킨 다양한 토폴로지의 NN을 효율적으로 실행
- **설계:**
  - Sparsity 인식 설계: 불균일한 NN 연결 구조 활용
  - 에너지 효율적 연산: 엣지 디바이스의 제한된 전력 예산 충족

### 3.4. GENESYS SoC 통합

- **15nm 기술 노드로 구현**
- **EvE + ADAM 통합:** 학습(진화)과 추론의 원활한 통합
- **메모리 시스템:** NN 개체군 및 유전체 데이터 효율적 관리
- **환경 인터페이스:** OpenAI Gym 환경과의 상호작용 지원

## 핵심 기여

- **핵심 기여:** EA 기반 학습 시스템을 위한 최초의 HW-SW 프로토타입 제시
  - EvE(학습 가속기)와 ADAM(추론 가속기)의 통합 시스템
- **성능 향상:** CPU/GPU 대비 2-5 orders of magnitude 높은 에너지 효율성
- **실용성:** 엣지 디바이스에서의 자율 학습 가능성 입증
  - 제한된 전력/에너지 예산에서도 지속적인 학습 가능
- **의의:** 
  - 일반적 지능 시스템 구현을 위한 새로운 방향성 제시
  - RL 대비 계산 비용이 낮은 EA 기반 학습의 하드웨어 가속화
  - 자율 에이전트(로봇/드론)의 상용화 촉진
- **한계점:**
  - NE 알고리즘의 수렴 속도 및 최적해 도달 능력에 대한 추가 연구 필요
  - 복잡한 실제 환경에서의 성능 검증 필요
  - 상용화를 위한 추가 최적화 및 검증 필요

## 주요 결과

- **기술 노드:** 15nm
- **구성 요소:**
  - EvE (Evolution Engine): EA 기반 학습 가속기
  - ADAM: 추론 가속기
  - 메모리 시스템: 개체군 및 유전체 데이터 저장
- **소프트웨어 스택:**
  - NEAT 알고리즘 구현
  - OpenAI Gym 환경 인터페이스
  - 적합도 함수 관리
- ** benchmark 환경:** OpenAI Gym의 다양한 환경 suite 사용

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/genesys-enabling-continuous-learning-through-neural-network-evolution-in-hardware.md|전체 요약 보기]]
