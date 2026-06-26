---
tags: [paper, 2020, 2020MICRO, topic/dram, topic/gpu, topic/near-data-processing, topic/pim]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO) 2020"
year: 2020
summary_path: "../paper-summaries/2020MICRO-summarize/newton-a-dram-makers-accelerator-in-memory-aim-architecture-for-machine-learning.md"
---

# Newton: A DRAM-maker's Accelerator-in-Memory (AiM) Architecture for Machine Learning

**Venue:** IEEE/ACM International Symposium on Microarchitecture (MICRO) 2020
**저자:** Mingxuan He, Choungki Song, Ilkon Kim, Chunseok Jeong, Seho Kim, Il Park, Mithuna Thottethodi, T. N. Vijaykumar (Purdue University, SK Hynix)

## 개요

- 머신러닝 추론에서 메모리 바운드 모델(LSTM, RNN, MLP, CNN의 fully-connected 레이어)이 중요하며, 이들의 핵심 연산은 행렬-벡터 곱셈임
- 기존 PIM(Processing-in-Memory) 접근 방식은 풀 프로세서 코어를 사용하여 면적 및 전력 제약을 초과하며, 이는 DRAM 밀도 손실과 열 문제를 야기
- 아날로그 PIM은 노이즈, 확장성, 공정 변동 문제로 인해 정확도 저하 발생
- PNM(Processing-Near-Memory)은 낮은 대역폭을 제공하며, 기존 DRAM은 오프 칩 연결의 좁은 채널 폭으로 인해 직렬 데이터 검색에 제약
- 클라우드 엣지에서의 소규모 배치 추론은 필터의 큰 재사용이 없어 깊은 메모리 바운드 상태 유지
- 기존 PIM 방식은 offloading 오버헤드, PIM/non-PIM 모드 전환, 커널 지연 시간等问题가 있음

## 방법론

### 3.1. 필터 행렬 인터리브 레이아웃

- 행렬은 DRAM에 상주하고, 입력 벡터는 브로드캐스트됨
- 각 출력 벡터 요소는 행렬 행과 입력 벡터의 곱셈으로 계산됨
- 입력 벡터는 모든 행렬 행에 곱해지므로 높은 재사용을 가짐
- 청크 인터리브 방식: 첫 번째 행렬 행의 첫 번째 청크 → 두 번째 행렬 행의 첫 번째 청크 순서로 배치
- DRAM 행 크기(예: 1KB = 512개 bfloat16 요소)만큼의 넓은 청크를 사용하여 출력 버퍼링 최소화
- 같은 입력 요소가 다시 페치되지 않도록 완전한 입력 재사용 보장

### 3.2. Newton 조직 구조

- 각 뱅크마다 k개의 곱셈기를 배치하여 열 접근 대역폭과 속도 일치 (예: k=16)
- 곱셈기는 DRAM 공정 트랜지스터로 구현
- 파이프라인 애더 트리를 통해 곱셈 결과를 축적
- 글로벌 입력 벡터 버퍼는 채널 내 모든 뱅크에서 공유되어 면적 비용 절감
- 결과 래치(Result Latch)는 청크당 단일 출력 벡터 요소를 보관

### 3.3. Newton 동작 과정

- 알고리즘 1: 타일화된 행렬-벡터 곱셈(MV) 연산
  - 입력 벡터를 청크로 분할하고 글로벌 버퍼에 로드
  - 각 청크에 대해 모든 뱅크에서 병렬로 타일 연산 수행
  - 각 타일의 결과를 호스트로 전송하여 부분 결과 축적
  - 호스트가 최종 출력 벡터 요소를 계산

### 3.4. 인터페이스 최적화

- **명령 묶기(Command Ganging):** 단일 연산 명령이 �뱅크 내 및 여러 뱅크에 걸친 다중 연산을 수행
- **복합 명령(Complex Commands):** 단일 명령이 (a) 글로벌 버퍼에서 입력 벡터 브로드캐스트, (b) 필터 행렬의 열 읽기, (c) 곱셈-누적을 순차적으로 트리거
- **tFAW 오버헤드 감소:** 명령 대역폭 병목을 완화하기 위한 타이밍 최적화
- 호스트에게는 일반 DRAM 명령과 동일한 결정론적 지연 시간 제공

## 핵심 기여

- Newton은 최소한의 연산 하드웨어만 배치하여 PIM의 면적/전력 제약을 충족하면서도 높은 대역폭 달성
- DRAM과 동일한 인터페이스를 통해 호스트에게 투명한 통합 제공
- 세 가지 최적화를 통해 명령 대역폭 병목을 효과적으로 완화
- 비정상적으로 넓은 인터리브 레이아웃으로 출력 벡터 재사용을 포착
- 실제 신경망 평가에서 GPU 대비 54x, 비-PIM 무한 연산 시스템 대비 10x 속도up 달성
- AiM 기술의 상용화 가능성을 제시하며, DRAM 제조사의 제품 아키텍처로 실용성 인정

## 주요 결과

- 구현 언어: Not specified (하드웨어 설계)
- HBM2E 기반 DRAM 위에 구현된 AiM 아키텍처
- DRAM 공정 트랜지스터를 사용한 곱셈기 구현
- 채널당 16개 뱅크, 각 뱅크에 16개 곱셈기 배치
- 16비트 부동소수점(bfloat16) 데이터 지원
- 호스트 프로세서가 신경망 활성화 함수(ReLU, sigmoid, tanh) 적용

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2020MICRO-summarize/newton-a-dram-makers-accelerator-in-memory-aim-architecture-for-machine-learning.md|전체 요약 보기]]
