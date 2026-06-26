---
tags: [paper, 2024, 2024ASPLOS, topic/cache, topic/gpu, topic/llm-inference]
venue: "29th ACM International Conference on Architectural Support for Programming Languages and Operating Systems, Volume 2 (ASPLOS '24), April 27-May 1, 2024"
year: 2024
summary_path: "../paper-summaries/2024ASPLOS-summarize/exegpt-constraint-aware-resource-scheduling-for-llm-inference.md"
---

# ExeGPT: Constraint-Aware Resource Scheduling for LLM Inference

**Venue:** 29th ACM International Conference on Architectural Support for Programming Languages and Operating Systems, Volume 2 (ASPLOS '24), April 27-May 1, 2024
**저자:** Hyungjun Oh, Kihong Kim, Jaemin Kim, Sungkyun Kim, Junyeol Lee, Du-seong Chang, Jiwon Seo (Hanyang University, KT Corporation)

## 개요

- LLM 추론은 자연어 처리 분야를 크게 발전시켰으나, 높은 연산 비용으로 인해 효율적 실행이 과제
  - 단일 토큰 생성에 수백억 FLOP 소요
- 기존 LLM 추론 시스템의 한계:
  - **FasterTransformer (FT) / DeepSpeed Inference (DSI):** 디코딩 배치 크기가 점진적으로 감소 (diminishing decoding batches) → 하드웨어 리소스 활용도 저하 및 추론 스루프루트 하락
  - **ORCA:** 반복 수준 스케줄링으로 배치 크기 유지하나, 인코딩과 디코딩 워크로드 차이로 인해 파이프라인 버블(pipeline bubbles) 발생
  - **지연 시간/스루프루트 트레이드오프 비효율:** 기존 시스템은 배치 크기 축소로 지연 시간을 줄이지만 이는 스루프루트를 크게 저해
- LLM 추론의 고유한 과제:
  - 수백억 개 파라미터로 인해 여러 GPU에서 모델 병렬 실행 필요
  - 오토레그레시브 특성으로 각 모델 실행이 단일 토큰만 생성, 여러 반복 필요
  - 배치 내 입력들의 출력 길이가 달라 디코딩 후반부 배치 크기 급감

## 방법론

### 3.1. 시스템 구성 요소

- **XProfiler:** 단일 인코딩/디코딩 레이어의 실행 시간을 모든 가능한 텐서 병렬 도수(degree)에서 측정
  - 어텐션 커널: 배치 크기 × 시퀀스 길이 스위프
  - 나머지 레이어: 입력 크기(배치 크기 × 입력 길이) 스위프
  - 텐서/파이프라인 병렬 실행의 동기화 오버헤드 측정
- **XSimulator:** 프로파일링 결과와 시퀀스 길이 확률 분포를 사용하여 실행 타임라인 구성
  - 배치 크기의 기대값 계산, 파이프라인 단계별 인코딩/디코딩 시간 추정
- **XScheduler:** 분기 한정(branch-and-bound) 검색으로 지연 시간 제약 하 스루프루트 최대화
  - 제어 변수의 단조로운 특성을 활용한 효율적 탐색
- **XRunner:** FasterTransformer를 확장하여 스케줄 실행
  - 완료된 쿼리의 조기 종료(early-termination) 및 KV-cache 엔트리 컴팩션(compact)
  - WAA 스케줄을 위한 인코딩 GPU→디코딩 GPU 간 KV-cache 전송

### 3.2. 스케줄링 전략

#### 3.2.1. RRA (Round-Robin Allocation) 스케줄링

- GPU를 인코더/디코더에 라운드로빈 방식으로 할당
- 인코딩 1회 실행 후 디코딩을 $N_D$회 반복 실행 → 인코딩/디코딩 배치 크기 일관성 유지
- 제어 변수: 인코딩 배치 크기 $B_E$, 디코딩 배치 크기 $B_D$, 디코딩 반복 횟수 $N_D$
- $B_E$는 이전 $N_D$회 디코딩에서 완료된 쿼리 수와 일치하도록 설정
- 디코딩 배치 축소 문제를 완화하나, 인코딩/디코딩 간 파이프라인 버블 발생 가능

#### 3.2.2. WAA (Workload-Aware Allocation) 스케줄링

- 워크로드 크기에 비례하여 GPU를 인코딩/디코딩에 할당
- **WAA-C:** 연산 시간 기반 할당 — $N \cdot C_E / (C_E + C_D)$ GPU를 인코딩에, 나머지를 디코딩에
- **WAA-M:** 메모리 소비 기반 할당 — 모든 GPU의 메모리 사용량 균등화
- 인코딩/디코딩 단계를 비동기적으로 실행하여 인코딩 지연으로 인한 디코딩 지연 방지
- 디코더 모델의 경우 두 모델 복사본 저장 필요 (오버헤드: OPT 18%, GPT-3 29%)

#### 3.2.3. 두 전략의 비교

- **RRA:** 디코딩 배치 크기 유지에 중점 → 출력 시퀀스 길이가 긴 경우에 유리
- **WAA:** 파이프라인 버블 최소화에 중점 → 출력 시퀀스 길이가 짧은 경우에 유리
- 두 전략 모두 기존 시스템의 핵심 문제(diminishing decoding batches, pipeline bubbles)를 동시에 해결

### 3.3. 지연 시간/스루프루트 트레이드오프 제어 변수

- **배치 크기:** 증가 시 병렬성 향상 → 스루프루트 증가, 지연 시간 증가
- **디코더 마이크로 배치 (WAA):** 디코딩 배치를 여러 마이크로 배치로 분할 → 지연 시간 감소, 스루프루트 감소
- **부분 텐서 병렬성:** 레이어를 여러 GPU에서 텐서 병렬로 실행 → 파이프라인 깊이 감소, 지연 시간 감소
- **인코딩 빈도 (RRA):** 인코딩을 더 자주 실행 → 디코딩 배치 증가 → 스루프루트 증가, 지연 시간 증가

## 핵심 기여

- **핵심 기여:** 지연 시간 제약 하에서 LLM 추론 스루프루트를 최대화하는 제약 인식 스케줄링 시스템 ExeGPT 제시
- **성능:** FT 대비 평균 2.9× 스루프루트 향상 (20개 평가 시나리오 전체), 최대 15.2× 스루프루트, 최대 6× 지연 시간 개선
- **혁신성:** (1) 인코딩/디코딩 해耦합을 통한 리소스 유연한 할당, (2) 4개 제어 변수의 단조로운 특성을 활용한 효율적 최적화, (3) 시퀀스 길이 분포 기반 사전 스케줄링
- **실용성:** FasterTransformer 기반 구현, 프로파일링 2시간 미만, 스케줄링 수 분 이내, 모델 배포 수 초~수십 초
- **적응성:** 시퀀스 분포 변화 시 스케줄 재조정 비용이 합리적이며, RRA는 인코딩 빈도 조정만으로 적응 가능
- **의의:** 다양한 NLP 태스크와 LLM 크기에서 일관되게 우수한 성능을 보이며, LLM 추론 서빙의 효율적 리소스 관리에 기여

## 주요 결과

### 4.1. 단조로운 최적화 (Monotonic Optimization)

- 제어 변수들이 스루프루트와 지연 시간에 대해 단조로운 특성 보유
  - 5% 허용 오차 내에서 전체 제어 변수의 97%가 스루프루트에, 96%가 지연 시간에 대해 단조로움
- **분기 한정(Branch-and-Bound) 알고리즘:**
  - 초기 블록(제어 변수 범위)에서 시작
  - 레이턴시 제약 충족 여부에 따라 블록 분할 및 가지치기(pruning)
  - 휴리스틱 분할: 상단 좌측/하단 우측 점의 스루프루트 비교 후 수직/수평 분할
  - 알고리즘 복잡도: RRA 3초~2분, WAA 1~5분 (기존 탐색 대비 수천 배 빠름)

### 4.2. 동적 스케줄링

- 시퀀스 길이 변동에 따른 인코딩/디코딩 워크로드 불균형 보정
- 런타임에서 인코딩 배치 크기를 동적 조정하여 워크로드가 기대값의 임계값 내 유지
- 디코딩 배치 크기가 평균 대비 임계값 이하/이상으로 변동 시 인코딩 배치 크기 조정

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]


## 전체 요약

[[../paper-summaries/2024ASPLOS-summarize/exegpt-constraint-aware-resource-scheduling-for-llm-inference.md|전체 요약 보기]]
