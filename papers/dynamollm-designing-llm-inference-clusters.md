---
tags: [paper, 2025, 2025HPCA, topic/cache, topic/gpu, topic/llm-inference]
venue: "2025 IEEE International Symposium on High Performance Computer Architecture (HPCA 2025)"
year: 2025
summary_path: "../paper-summaries/2025HPCA-summarize/dynamollm-designing-llm-inference-clusters.md"
---

# DynamoLLM: Designing LLM Inference Clusters for Performance and Energy Efficiency

**Venue:** 2025 IEEE International Symposium on High Performance Computer Architecture (HPCA 2025)
**저자:** Jovan Stojkovic, Chaojie Zhang, Íñigo Goiri, Josep Torrellas, Esha Choukse (University of Illinois at Urbana-Champaign, Microsoft Azure Research)

## 개요

- 생성형 LLM의 급속한 도입으로 추론 클러스터가 매일 수백만 건의 쿼리를 처리하며, 이를 지원하기 위해 전력 소비가 높은 GPU 기반 대규모 인프라 구축이 필요
- LLM 추론 환경의 에너지 소비问题是 largely overlooked: GPU 기반 추론 클러스터는 상당한 에너지 소비와 탄소 배출을 유발
- 기존 데이터센터 에너지 관리 기법(CPU 주파수 스케일링, LLC 크기 조절 등)은 LLM 추론의 고유한 특성을 고려하지 않음
- LLM 추론 워크로드의 핵심 특성:
  - **요청 이질성:** 입력/출력 토큰 길이에 따른 연산 특성 차이 (Table IV: SS, SM, SL, MS, MM, ML, LS, LM, LL의 9가지 카테고리)
  - **동적 변동성:** 시간에 따른 요청 분포 및 부하 변동
  - **모델 특성 차이:** Llama2-13B ~ Falcon-180B까지 다양한 모델 크기와 연산 특성
- 기존 에너지 관리 프레임워크의 한계: GPU 주파수 또는 인스턴스 스케일링 중 하나만 사용, LLM 특화 파라미터(텐서 병렬성 등) 미고려, 워크로드 이질성 미반영
- Table I-III: 동일 요청 유형에서도 텐서 병렬성(TP2/TP4/TP8), GPU 주파수(0.8~2.0GHz), 부하 수준에 따라 에너지 소비가 크게 변동 (예: Llama2-70B MM 요청에서 최소 3.91Wh ~ 최대 13.21Wh)

## 방법론

### 3.1. 에너지-성능 프로파일링

- **요청 길이별 프로파일:** 9가지 카테고리(SS~LL)별로 다른 텐서 병렬성과 GPU 주파수에서 에너지/성능 측정
  - 짧은 입력+짧은 출력(SS): 낮은 병렬성(TP2) + 낮은 주파수(0.8GHz)에서 가장 효율적
  - 긴 입력+긴 출력(LL): 높은 병렬성(TP8) + 높은 주파수 필요
- **모델별 프로파일:** Llama2-13B, Mixtral-8x7B, Llama2-70B, Llama3-70B, Mixtral-8x22B, Falcon-180B의 에너지-성능 특성 측정 (Table III)
- **프로파일 기반 예측:** 로드, 요청 길이, 병렬성, 주파수를 입력으로 받아 에너지/지연시간 예측 → 평균 예측 정확도 **98%** 이상
- **프로파일 재사용:** 동일 모델을 사용하는 여러 서비스 간 프로파일 공유로 프로파일링 오버헤드 최소화

### 3.2. 계층적 제어 구조

- **3단계 계층 구조 (Fig. 5):**
  - **Cluster Manager (최상위):** 풀(pool) 할당, 스케일 인/아웃 결정 (에포크: 30분)
  - **Pool Manager (중간):** 텐서 병렬성 결정, 샤드 업/다운 (에포크: 5분)
  - **Instance Manager (최하위):** GPU 주파수 미세 조정 (에포크: 5초)

- **스케일 인/아웃 (Cluster Manager):**
  - 예측된 피크 부하(PL)와 노드당 최대 수용량(ML) 기반으로 각 풀에 할당할 최소 노드 수 결정: ⌈PL/ML⌉
  - 리소스 단편화 방지: 가장 큰 요청 풀에만 과잉 provisioning 허용, 나머지는 상위 풀로 부하 전달

- **샤드 업/다운 (Pool Manager):**
  - MILP 솔버로 최적 병렬성 결정: 최소 에너지为目标 while SLO 만족
  - 수식:
    ```
    min Σ(N_TP_i × Energy_TP_i,f_i(L_TP_i))
    s.t. Σ(i × N_TP_i) ≤ N (GPU 수 제약)
         Σ(N_TP_i × L_TP_i) ≥ L (부하 수요 충족)
         Performance_TP_i,f_i(L_TP_i) ≤ SLO
    ```

- **주파수 스케일링 (Instance Manager):**
  - 프로파일에서 SLO 위반 주파수 필터링 → 에너지 최소 주파수 선택
  - 5초 단위로 빈번한 조정 가능

### 3.3. 재구성 오버헤드 최소화

- **인스턴스 스케일 인/아웃:**
  - 모델 가중치를 클러스터 로컬 스토리지에 캐싱 → 글로벌 저장소에서 가져오지 않음
  - VM 스냅샷에서 시작: GPU 드라이버, 추론 엔진 등 이미 초기화된 상태로 부팅 시간 단축
  - 피크 부하 예측 기반 사전 VM 생성: 에포크 시작 전 백그라운드에서 새 VM 준비

- **샤드 재구성:**
  - 그래프 매칭 알고리즘: 현재/목표 가중치 분포 간 최대 가중치 이완 매칭으로 데이터 전송량 최소화
  - NVLink를 통한 GPU 간 직접 전송: 호스트 개입 없이 병렬 가중치 전송 (Llama2-70B 기준 ~50ms)
  - 교차 병렬성 전환 예시: TP4→TP8 시 4개 GPU가 나머지 4개로 가중치의 절반만 전송

- **단계적 재구성(Staggered Reconfiguration):**
  - 모든 인스턴스가 동시에 재구성되지 않도록, 에너지 절약 잠재력이 높은 인스턴스부터 순차 재구성
  - 서비스 중단 시간 최소화

## 핵심 기여

- **핵심 기여:** LLM 추론 환경을 위한 최초의 종합 에너지 관리 프레임워크 DynamoLLM 제시
- **성능:** 52% 에너지 절약, 38% 탄소 배출 감소, 61% 비용 절감 — 모두 SLO 충족 하에서 달성
- **혁신성:** (1) 워크로드 이질성을 반영한 풀 기반 리소스 관리, (2) 3단계 계층적 제어로 복잡도 처리, (3) 다중 노브(인스턴스 수, 병렬성, 주파수) 동시 최적화
- **실용성:** Microsoft Azure 프로덕션 트레이스로 검증, vLLM 추론 엔진과 원활하게 통합 가능
- **재구성 효율:** 그래프 매칭 기반 가중치 전송 최소화 + NVLink 직접 전송 + 사전 VM 생성으로 빈번한 재구성 가능
- **의의:** LLM 추론의 에너지 문제를 체계적으로 해결하는 최초의 프레임워크로, 대규모 GPU 클러스터에서의 실질적인 에너지/비용/탄소 배출 절감 방안 제시

## 주요 결과

- **플랫폼:** NVIDIA DGX H100 서버 기반
- **추론 엔진:** vLLM
- **평가 환경:** Microsoft Azure 프로덕션 트레이스 (Coding, Conversation 서비스의 1주일간 호출 트레이스)
- **오픈소스:** Azure 프로덕션 트레이스 일부 공개 (https://github.com/Azure/AzurePublicDataset)
- **평가 대상 모델:** Llama2-13B, Mixtral-8x7B, Llama2-70B, Llama3-70B, Mixtral-8x22B, Falcon-180B
- **SLO 기준:** TTFT(첫 토큰까지 시간) 및 TBT(토큰 간 시간) 기반, 요청 유형별 차등 SLO (Table IV)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]


## 전체 요약

[[../paper-summaries/2025HPCA-summarize/dynamollm-designing-llm-inference-clusters.md|전체 요약 보기]]
