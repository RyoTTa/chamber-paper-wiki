---
tags: [paper, 2018, 2018MICRO, topic/dram, topic/gpu]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/architectural-support-for-efficient-large-scale-automata-processing.md"
---

# Architectural Support for Efficient Large-Scale Automata Processing

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Hongyuan Liu, Mohamed Ibrahim, Onur Kayiran, Sreepathi Pai, Adwait Jog (College of William & Mary, Advanced Micro Devices Inc., University of Rochester)

## 개요

- **오토마타 프로세서(AP):** 제노믹스, 악성코드 탐지, 머신 런닝, 데이터 분석 등 다양한 도메인의 애플리케이션을 가속화하는 공간적 아키텍처(spatial architecture)
- AP는 NFA(Non-deterministic Finite Automata)를 네이티브로 실행하여, CPU/GPU 대비 비규칙적 메모리 접근(NFA 전이 테이블 조회)로 인한 데이터 이동 문제를 극복
  - AP의 DRAM 배열에 NFA 상태가 열(column)로 매핑되어, 주어진 사이클에서 독립적이고 동시에 활성화 가능
  - 인메모리 처리 능력으로 프로세서-메모리 간 데이터 이동 없이 NFA 전이 처리
- **확장성 문제:** 미래 애플리케이션은 NFA 기반 애플리케이션의 규모가 크게 확장될 것으로 예상
  - **빅데이터 시대:** ClamAV와 같은 안티바이러스 애플리케이션이不断扩大되는 데이터베이스에서 정규 표현식 기반 바이러스 서명을 사용 → NFA 상태 수가 AP 칩 용량을 초과
  - **처리량 향상 기법들:**
    - NFA 중복화: 다중 입력 심볼 스트림 병렬 처리
    - Parallel Automata Processor: 병렬 열거를 위한 NFA 중복화
    - Multi-stride NFAs: 다중 심볼을 한 단계에서 처리하기 위한 전이 수 증가
  - 현재 AP 칩은 이러한 대규모 NFA를 배치별로 독립 실행 후 재구성(reconfiguration) 필요 → **반복적 재구성과 재실행의 성능 페널티**
- AP 하프코어(half-core)는 최대 **24K 상태**를 보유 가능하지만, 대규모 애플리케이션은 이를 초과
- 기존 공간적 아키텍처의 멀티태스킹 문제: GPU도 대규모 프로그램 상태로 인해 효율적 멀티태스킹 지원이 어려움

## 방법론

### 3.1. 프로파일링 기반 핫/콜드 상태 예측

- **프로파일링 절차:**
  - 컴파일 시, 소량의 프로파일링 입력을 사용하여 모든 NFA를 기능적으로 시뮬레이션
  - 각 NFA의 모든 상태가 실행 중에 활성화되는지 여부를 기록
  - 핫 상태: 프로파일링 중 최소 한 번 활성화된 상태
  - 콜드 상태: 프로파일링 중 한 번도 활성화되지 않은 상태
- **파티셔닝 레이어 선택:**
  - 각 NFA U에 대해 `kU = max{topoorder(s)}` (s는 핫 상태)
  - **예측 핫 집합:** `topoorder(s) ≤ kU`인 상태들
  - **예측 콜드 집합:** `topoorder(s) > kU`인 상태들
  - 핫 상태를 AP 용량에 맞는 배치(batch)로 분할하여 순차적으로 구현
- **최적화:** 각 배치를 AP로 완전히 채우기 위해 핫 집합에 추가 상태를 콜드 집합에서 보충 (kU 점진적 증가)

### 3.2. NFA 파티셔닝 메커니즘

- **기본 원칙:** 특정 위상 순서(topological order)에서 NFA를 분할
  - 매칭은 항상 낮은 위상 순서에서 높은 위상 순서로 진행
  - 파티션을 교차하는 에지(edge)는 한 방향으로만 이동 → 양방향 전이 방지
- **파티셔닝 절차 (Fig. 7):**
  1. 파티셔닝 레이어 `k=3`에서 NFA를 두 부분으로 분할
  2. `k≤3`인 상태(핫 세트)와 `k>3`인 상태(콜드 세트)를 분리
  3. 분할된 엣지를 잘라냄
- **불완전 예측 처리:**
  - 프로파일링에서 콜드로 예측된 상태가 실제 실행에서 활성화될 수 있음
  - **중간 보고 상태(Intermediate Reporting State):** AP에서 콜드 상태로의 전이를 위해 추가
  - 기존 AP의 보고 하드웨어(reporting hardware)에 독립적으로 중간 보고를 발생
  - 라우팅 매트릭스의 계층적 구조(블록, 행, STE)를 활용한 상태 활성화

### 3.3. BaseAP/SpAP 실행 모드

- **BaseAP 모드:**
  - AP에 핫 상태만 구현하여 실행
  - 콜드 상태와의 전이가 필요한 경우 중간 보고를 생성
  - 기존 AP 실행과 동일하나 더 적은 상태 사용
- **SpAP 모드:**
  - AP에 콜드 상태만 구현하여 실행
  - BaseAP에서 생성된 중간 보고를 입력으로 받아 콜드 상태 처리
  - **점프(Jump) 연산:** 활성화된 상태가 없을 때, 다음 중간 보고의 입력 위치로 점프 → 불필요한 입력 심볼 처리.skip
  - **활성화(Enable) 연산:** 중간 보고의 상태 ID를 사용하여 해당 STE를 활성화
- **알고리즘 (Algorithm 1):**
  ```
  SpAP 실행:
    각 사이클에서:
      if 활성화된 상태가 없으면:
        다음 중간 보고의 입력 위치로 점프
      if 현재 입력 위치 = 중간 보고의 입력 위치이면:
        해당 상태 활성화
      입력 심볼 처리
  ```
- **장점:** 콜드 상태가 핫 상태로 다시 전이하는 엣지가 없으므로, BaseAP↔SpAP 간 왕복 전환이 불필요

### 3.4. 중간 보고 상태의 오버헤드 관리

- **증가하는 상태 수:** 중간 보고 상태 추가로 총 상태 수 증가 → 재구성/실행 횟수 증가 가능
- **jump 연산 비율(JumpRatio):** SpAP 모드에서 점프로 건너뛰는 입력 심볼의 비율
  - 높은 JumpRatio → 콜드 상태가 실제로 드물게 활성화됨 → 높은 속도 향상
- **enable 연산 병렬성:** SpAP 모드에서 enable 연산은 입력 심볼 처리와 겹칠 수 있음
  - 단, 동시에 여러 중간 보고가 발생하면 병렬 처리 불가 → **enable stall** 발생 가능
- **레이턴시 오버헤드:** 점프 연산과 enable 연산의 구현 오버헤드는 전체 실행 시간 대비 미미

## 핵심 기여

- **핵심 기여:** 대규모 NFA 애플리케이션을 효율적으로 처리하기 위한 최초의 AP 아키텍처 지원 제시
- **핵심 기법:**
  - 프로파일링 기반 핫/콜드 상태 예측으로 AP 리소스 효율적 활용
  - BaseAP/SpAP 이중 실행 모드로 핫/콜드 상태를 분리 처리
  - 중간 보고 상태 + 점프 연산으로 콜드 상태 처리 시 불필요한 연산 최소화
- **성능:** 기하평균 **2.1배**(최대 **47배**) 속도 향상 (26개 벤치마크)
- **리소스 효율성:** 핫 세트만 구현하여 재구성 횟수 대폭 감소 (예: 47회 → 1회)
- **실용성:** 다양한 AP 크기(12K~49K STE)에서 일관된 성능 향상, 프로파일링 오버헤드 낮음
- **의의:** AP의 확장성 문제를 해결하여, 빅데이터 시대의 대규모 패턴 매칭 애플리케이션 지원
- **향후 확장:** Cache Automaton 등 다른 AP 구현에도 적용 가능한 보완적 기법

## 주요 결과

- **시뮬레이션:** 상세 사이클 정확 시뮬레이션
- **AP 모델:** 기존 AP 하프코어 기반 (최대 24K STE)
- **소프트웨어:**
  - 프로파일러: NFA 상태의 핫/콜드 분류
  - NFA 파티셔너: 위상 순서 기반 NFA 분할
  - BaseAP/SpAP 실행 모드 구현
- **하드웨어 추가:**
  - 중간 보고 상태 레지스터
  - 점프 연산을 위한 입력 위치 추적 레지스터
  - 상태 활성화를 위한 계층적 디코더 (7×128 블록 선택, 4×16 행 선택, 4×16 STE 선택)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/architectural-support-for-efficient-large-scale-automata-processing.md|전체 요약 보기]]
