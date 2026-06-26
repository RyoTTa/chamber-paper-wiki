---
tags: [paper, 2020, 2020HPCA, topic/gpu, topic/pim]
venue: "2020 IEEE International Symposium on High Performance Computer Architecture (HPCA '20)"
year: 2020
summary_path: "../paper-summaries/2020HPCA-summarize/enabling-highly-efficient-capsule-networks-processing-through-a-pim-based-architecture-design.md"
---

# Enabling Highly Efficient Capsule Networks Processing Through A PIM-Based Architecture Design

**Venue:** 2020 IEEE International Symposium on High Performance Computer Architecture (HPCA '20)
**저자:** Xingyao Zhang (ECOMS Lab, ECE Department, University of Houston; Future System Architecture Lab, University of Sydney), Shuaiwen Leon Song (Future System Architecture Lab, University of Sydney), Chenhao Xie (Pacific Northwest National Lab), Jing Wang (Capital Normal University), Weigong Zhang (Beijing Advanced Innovation Center for Imaging Theory and Technology), Xin Fu (ECOMS Lab, ECE Department, University of Houston)

## 개요

- CNN은 이미지 처리에서 큰 성공을 거두었으나, 풀링(pooling) 연산으로 인해 위치 및 자세(pose) 정보를 정확하게 보존하지 못하는 한계 존재
- Capsule Network(CapsNet)는 capsule 개념을 도입하여 등변성(equivariance)을 실현하고, CNN 대비 의료 영상 처리에서 평균 19.6%, 자율주행에서 42.06% 높은 검출 정확도 달성
- 그러나 CapsNet의 라우팅 절차(routing procedure)는 다음과 같은 실행 비효율성에 직면:
  - 중간 변수(intermediate variables)가 온칩 스토리지보다 42x~420x 크게 초과하여 대규모 오프칩 메모리 접근 필요 (Figure 6a)
  - 동기화(synchronization)가 빈번하게 발생하여 write-after-read, write-after-write hazard 회피 필요
  - GPU의 온칩 메모리 용량 증가로는 성능 향상이 제한적 (V100 기준 최대 14% 향상, Figure 6b)
  - 메모리 대역폭 증가도 전체 RP 성능을 평균 26%만 향상 (Figure 7)

## 방법론

### 3.1. 인터-볼트 레벨 설계 (Inter-Vault Level Design)

- 라우팅 절차의 5개 방정식이 B(batch), L(low-level capsule), H(high-level capsule) 차원 중 적어도 하나에서 병렬화 가능 (Table II)
- 단일 차원에서만 워크로드를 분배하여 인터-볼트 통신 최소화
- 실행 점수(execution score) S = 1/(αE + βM)을 제안하여 최적의 워크로드 분배 유도
  - E: 가장 큰 워크로드가 있는 볼트의 실행 시간
  - M: 인터-볼트 통신 오버헤드
- 사전 집계(pre-aggregation)를 통해 인터-볼트 통신량 추가 절감

### 3.2. 인트라-볼트 레벨 설계 (Intra-Vault Level Design)

- HMC의 로직 레이어에 다수의 처리 요소(PE)를 통합
- 각 PE는 덧셈, 곱셈, 비트 시프팅 연산을 지원하는 유니크한 구조
- 지수 함수(exponential) 근사: ExpResult ≈ BS(log₂(e) × x + Avg + b - 1)로 단순화
- 정확도 복원(accuracy recovery) 기법: 평균 차이 비율을 곱하여 정확도 손실 최소화 (Table V)

### 3.3. 메모리 주소 매핑 및 리소스 관리

- 기존 HMC의 순차 인터리빙 매핑을 수정하여 연속 블록이 하나의 볼트에 할당되도록 변경 (Figure 13)
- 동적 서브페이지 크기 결정: PE의 데이터 요청 크기에 따라 16B~256B로 유연하게 조정
- 런타임 메모리 접근 스케줄러(RMAS)를 통해 GPU와 PE 간 메모리 접근 우선순위 동적 결정
  - 성능 영향 함수 κ = γv × nh × Q + γh × nmax / nh를 최소화하는 nh 선택

### 3.4. 정확도 검증

- 근사 연산으로 인한 평균 정확도 손실: 0.35%
- 정확도 복원 후: 대부분의 경우 정확도 손실 0%, 전체 평균 0.04% 미만
- Caps-SV2, Caps-SV3에서는 RP 반복 횟수 증가 시 근사 노이즈가 특징 매핑의 강건성을 향상

## 핵심 기여

- **핵심 기여:** CapsNet의 라우팅 절차 비효율성을 해결하기 위한 최초의 PIM 기반 하이브리드 아키텍처 제안
- **성능 향상:** GPU 대비 2.44x 성능, 64.91% 에너지 절감
- **실용성:** 면적 오버헤드 0.32%, 전력 오버헤드 2.24W로 HMC의 열 제약 내 구현 가능
- **의의:** 라우팅 절차의 다차원 병렬화 특성을 활용한 워크로드 분배 기법과 특수 함수 근사 기법을 통해 메모리 기반 가속기의 실용성을 입증

## 주요 결과

- **구현 언어:** PyTorch 기반 시뮬레이션 + gate-level 시뮬레이션
- **평가 인프라:** NVprofiler, nvidia-smi, HMC-sim, Gate-Level Simulation (Figure 14)
- **HMC 구성:** 32 vault, 각 vault당 16 PE + operation controller
- **면적 오버헤드:** 32 vault + RMAS = 3.11mm² (22nm 공정), HMC 로직 면적의 0.32%
- **전력 오버헤드:** 평균 2.24W (HMC의 최대 허용 TDP 10W 이내)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2020HPCA-summarize/enabling-highly-efficient-capsule-networks-processing-through-a-pim-based-architecture-design.md|전체 요약 보기]]
