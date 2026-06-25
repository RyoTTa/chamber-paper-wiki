---
tags: [paper, 2025, 2025HPCA, topic/dram, topic/gpu, topic/llm-inference, topic/pim, topic/storage]
venue: "2025 IEEE International Symposium on High Performance Computer Architecture (HPCA 2025)"
year: 2025
summary_path: "../paper-summaries/2025HPCA-summarize/paise-pim-accelerated-inference-scheduling-engine-for-transformer-based-llm.md"
---

# PAISE: PIM-Accelerated Inference Scheduling Engine for Transformer-based LLM

**Venue:** 2025 IEEE International Symposium on High Performance Computer Architecture (HPCA 2025)
**저자:** Hyojung Lee, Daehyeon Baek, Jimyoung Son, Jieun Choi, Kihyo Moon, Minsung Jang (Cloud Research Team, Samsung SDS)

## 개요

- 트랜스포머 기반 LLM은 오토레그레시브 토큰 생성으로 인해 상당한 연산 및 메모리 리소스 필요
- 디코더 블록의 어텐션 레이어는 산술 집적도(arithmetic intensity)가 낮고 메모리 트래픽이 높음
  - 쿼리 벡터와 독립적인 Key-Value(KV) 캐시 행렬 간의 행렬-벡터 곱셈 필요
  - 각 디코더 반복마다 KV 캐시 행렬 업데이트 필요
- LLM 추론이 메모리 병목 현상으로 인해 레이턴시 증가
- Processing-In-Memory(PIM)는 메모리 은행(bank) 근처에 처리 유닛(PU)을 통합하여 연산 처리량과 데이터 대역폭을 은행 수에 비례하여 확장 가능
-然而, GPU-PIM 이기종 컴퓨팅 활용 시 여러 가지 도전 과제 발생:
  1. PIM과 GPU의 메모리 읽기 순서 차이 → GPU가 PIM 읽기 프로토콜에 따라 메모리 영역 업데이트 필요
  2. PIM의 효과적인 처리 영역 최적 크기 결정 → 하드웨어 사양(은행, 뱅크 그룹, 채널)에 의존
  3. 호스트 프로세서 개입으로 인한 DRAM 커맨드 시퀀스 위반 가능성 → PIM 계산 정확성 훼손

## 방법론

### 3.1. 데이터 레이아웃 조정(DLA) 모듈

- **표준 PIM-GEMV의 한계:**
  - 순차적 DLA로 PIM 메모리 대역폭의 25%만 활용
  - 벌크 메모리 복사 API로 기존 대비 **21.4%** 실행 시간 절감
  -그러나 GPU 대비 성능 열세 지속
- **인터리브 DLA 방법:**
  - 가중치 행렬을 트랜잭션 크기(32B)의 약수로 열 방향 분해
  - 분해된 행렬 조각을 트랜잭션 크기 주기 내에서 인터리브
  - Figure 7 예시: 4개 가중치 행렬이 단일 PIM 영역에 인터리브
  - 인터리브 DLA + IB-GEMV 조합으로 표준 GEMV 대비显著하게 높은 데이터 처리량 달성

### 3.2. 인터리브 배치(IB) PIM-GEMV 연산

- **표준 GEMV와의 차이:**
  - 32B 폭의 트랜잭션별 합(sum) 수행
  - 출력 행렬을 인터리브 배치 출력 벡터로 구성
  - 출력 행렬에서 서로 다른 GEMV(여러 색상)의 결과를 명확하게 구분 가능
  - 별도의 감소(reduction)를 통해 최종 GEMV 출력 벡터 도출
- **감소 방식 차이:**
  - 기존: 모든 16개 요소를 부분 결과 트랜잭션에서 누적
  - 개선: 동일한 가중치 행렬의 부분 결과만 최종 배치 출력 벡터에 대해 누적

### 3.3. 스케줄링 알고리즘 (Algorithm 1)

- **입력 파라미터:**
  - 모델 구성: 히든 임베딩 차원, 헤드 차원, 멀티 헤드 수, 디코더 수, 시퀀스 길이 등
  - PIM 하드웨어 특성: 가중치 행렬 최적 크기, PIM 효과성(α), 유휴 은행 비효율성(β), DLA 오버헤드(γ)
- **오프로딩 결정 기준:**
  - **효과성 αk:** PIM이 GEMM 연산에서 GPU보다 성능 우위를 가지는 정도 (αk > 0이면 PIM 유리)
  - **가중치 행렬 재사용:** DLA 오버헤드(γ)와 유휴 은행 비효율성(β)을 상쇄
  - **오프로딩 인센티브 u:** u > 0이면 PIM으로 오프로딩 결정
- **FC 레이어 오프로딩 전략:**
  - 가중치 행렬 (n, m)이 여러 반복에서 재사용됨
  - 반복 횟수 = 디코더 수 × 출력 길이
  - u = αk·(Lseq−s)·dnm − γnm − β(n⋆m⋆−nm)
- **어텐션 레이어 오프로딩 전략:**
  - K 또는 V 행렬이 PIM 메모리 영역에 할당
  - 한 행씩 업데이트 → 재사용 효율이 평균 절반
  - u = α1·(Lseq−s)·dhnm/2 − γnm/2 − β(n⋆m⋆−nm/2)

### 3.4. 소프트웨어 아키텍처 (Figure 9)

- **구성 요소:**
  - 수정된 C++ PIM 라이브러리 (Samsung SAIT PIMLibrary 기반)
  - Python 래퍼 (KV 캐시 관리)
- **새로운 GPU 커널:**
  - 인터리브 배치 GEMV 커널 (가중치 변환용)
  - GEMM 커널을 3단계로 분해:
    1. 입력 변환 (Input transformation)
    2. PIM GEMM 연산
    3. 출력 변환 (Output transformation)
- **메모리 관리:**
  - PIM 버퍼 관리 코드로 PIM 물리 메모리 영역 내 KV 캐시 영역 할당/해제
  - 4가지 버전의 DLA 커널:
    - 프리필링 단계: 배치 업데이트용 2개
    - 생성 단계: 단일 토큰 업데이트용 2개 (K, V 각각)
  - K와 V 캐시 업데이트가 다름 → 각 단계별 2개 커널 버전 필요
- **입력/출력 버퍼 최적화:**
  - 사전 할당된 입력/출력 벡터 버퍼로 메모리 할당 오버헤드 최소화
  - AS 및 KV 커널이 순차적으로 호출되어 입/출력 벡터 버퍼 공유 가능

## 핵심 기여

- **핵심 기여:** PIM 기반 LLM 추론 가속을 위한 PAISE 프레임워크 제안
- **성능:** 어텐션 레이어 PIM 오프로딩으로 최대 **48.3%** 실행 시간 절감, 에너지 **11.5%** 절감
- **혁신성:**
  1. 인터리브 DLA + IB-GEMV로 PIM 메모리 대역폭 최대 활용
  2. 모델 구성과 PIM 하드웨어 특성을 고려한 최적 오프로딩 결정 알고리즘
  3. KV 캐시의 인터리브 배치 처리로 어텐션 레이어 연산 효율 극대화
  4. 실제 HBM-PIM 디바이스(AMD MI100) 기반 실증 평가
- **한계 및 향후 과제:**
  - 멀티 프로세스 서비스 미지원 (PIM 커널 스케줄링 세밀성 부족)
  - 단일 프로세스 환경 전제 → 가상 주소 변환 문제 가능
  - 멀티 GPU 환경 확장 필요 (원격 메모리 접근, 기존 프레임워크 호환)
- **의의:** PIM 기술이 LLM 추론의 메모리 병목 현상을 효과적으로 해결할 수 있음을 실증, 향후 PIM 기반 LLM 가속의 실용화 가능성 제시

## 주요 결과

- **하드웨어:** AMD Instinct MI100 GPU + HBM-PIM(Aquabolt-XL)
- **PIM 구성 (Table IV):**
  - HBM2 기술, 4 스택, 16 채널, 2 랭크, 4 뱅크 그룹
  - 은행당 행: HBM 16,384 / PIM 8,192
  - 클럭 속도: 1,200 MHz
- **소프트웨어:** HIP, OpenCL, Python
- **대상 모델:** GPT-2, Llama2-7B

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2025HPCA-summarize/paise-pim-accelerated-inference-scheduling-engine-for-transformer-based-llm.md|전체 요약 보기]]
