---
tags: [paper, 2019, 2019MICRO, topic/cache, topic/compression, topic/pim, topic/virtual-memory]
venue: "52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '19)"
year: 2019
summary_path: "../paper-summaries/2019MICRO-summarize/graphq-scalable-pim-based-graph-processing.md"
---

# GraphQ: Scalable PIM-Based Graph Processing

**Venue:** 52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '19)
**저자:** Youwei Zhuo, Chao Wang, Mingxing Zhang, Rui Wang, Dimin Niu, Yanzhi Wang, Xuehai Qian (University of Southern California, Tsinghua University, Beihang University, Alibaba Inc, Northeastern University)

## 개요

- 그래프 분석은 머신 러닝, 자연어 처리, 이상 탐지, 클러스터링, 추천 시스템, 바이오인포매틱스 등 다양한 응용에서 중요한 역할
- 그래프 처리의 핵심 과제는 **비정형 데이터 이동(irregular data movements)**으로, 인접 행렬 기반의 CSR(Compressed Sparse Row) 표현에서 vertex/edge 배열은 순차 접근이나 compute 배열에 대한 접근은 무작위
- 그래프 알고리즘은 낮은 연산량 대비 높은 메모리 대역폭 필요 (processEdge 함수는 단순)
- 기존 PIM(Process-In-Memory) 기반 그래프 처리 아키텍처(Tesseract, GraphP)는 비정형 데이터 이동 문제를 근본적으로 해결하지 못함
  - Tesseract: 인터 큐브 통신에서 예측 불가능한 도착 시간으로 인한 인터럽트 오버헤드, 로드 불균형, 에너지 소비 증가
  - GraphP: 레플리카 동기화가 여전히 비정형 통신 발생
- 단일 PIM 노드 기반으로 멀티노드 확장 시 인터 큐브(120GB/s)와 인터노드(6GB/s) 간 대역폭 차이가 큰 문제

## 방법론

### 3.1. 예측 가능한 인터 큐브 통신 (Predictable Inter-Cube Communication)

- **배치 통신 (Batched Communication):**
  - 소스 큐브에서 reduce 단계를 로컬로 수행 → 원격 큐브로 함수/파라미터 대신 감소된 값 전송
  - 같은 원격 큐브로 향하는 모든 메시지를 동시에 생성하여 자연스러운 배치 형성
  - 행렬 블록 분할을 통해 큐브 간 배치 메시지 생성
  - Figure 4: 인접 행렬 뷰에서 배치 메시지 구조 설명

- **라운드 실행 (Rounded Execution):**
  - 각 반복을 M개 라운드로 분할 (M = 큐브 수)
  - 라운드 간 동기화: 모든 큐브가 한 라운드를 완료해야 다음 라운드 진입
  - 핵심 통찰: 각 라운드에서 각 큐브는 하나의 원격 큐브에 하나의 배치 메시지만 생성
  - 라운드 0에서 큐브 0→1, 큐브 1→2 등 순환 방식으로 통신 패턴 구성
  - 이전 라운드의 배치 메시지가 현재 라운드의 계산과 오버랩 가능 → 논블로킹 전송
  - 각 큐브는 한 라운드에 하나의 배치 메시지만 수신 → 수신 버퍼 하나만 필요
  - Figure 5: 계산-통신 오버랩 시각화

- **전처리 오버헤드:**
  - 그래프 분할 시 원격 큐브별 엣지 리스트 유지 → 엣지 블록 그룹핑
  - R-MAT-Scale27의 경우 추가 약 10초 전처리 (전체의 10% 미만)
  - Table 2: Twitter-2010 (36.7→39.7초), Friendster (53.5→58.2초), R-MAT-Scale27 (130.2→140.2초)

### 3.2. 디스플레이시드 인트라 큐브 데이터 이동 (Decoupled Intra-Cube Data Movements)

- **핵심 설계:** 인터 큐브와 인트라 큐브 데이터 이동을 별도로 처리
  - 인터 큐브: 배치 메시지 버퍼를 메모리에서 라우터가 전송
  - 인트라 큐브: 메시지 큐브와 로컬 라우터로 처리

- **이기종 코어 그룹:**
  - **Process Unit (PU):** vertex/edge 배열의 순차 읽기 및 processEdge 함수 실행
    - 스트라이드 프리페처 사용으로 메모리 대역폭 활용 및 지연 시간 숨김
    - 출력: AUs로 전송할 업데이트 메시지
  - **Apply Unit (AU):** PU로부터 메시지 수신, reduce/apply 함수 실행, compute 배열에 대한 무작위 접근
    - L1 캐시 대신 **스克拉치패드 메모리(SPM)** 사용
    - SPM: L1 캐시보다 빠르고, 소프트웨어가 명시적 공간 할당 가능
    - 라운드 끝에서 배치 메시지를 SPM에서 메모리의 send 버퍼로 순차 기록
  - PU와 AU가 하나의 데이터 이동 파이프라인 형성

- **온칩 인터커넥트:**
  - Send/Recv/Sync 프리미티브 제공
  - 로컬 라우터, 메시지 큐브, 코어 간 인터커넥트
  - 메시지 크기: 64비트 vertex ID + 값 = 128비트 → 한 사이클에 전송 가능

### 3.3. 인터노드 지연 시간 관리 (Hybrid Execution Model)

- **핵심 문제:** 인터 큐브(120GB/s)와 인터노드(6GB/s) 간 대역폭 차이 → 인터노드 통신이 전체 실행 시간의 82-91% 차지
- **하이브리드 실행 모델:**
  - 각 노드가 반복 실행 후 원격 배치 메시지 대기 시간에 로컬 서브그래프 기반 추가 반복 실행
  - **글로벌 반복:** 로컬 반복들의 집합, 원격 업데이트 수신 후 첫 로컬 반복 실행
  - 나머지 로컬 반복은 로컬 서브그래프만 사용
  - 글로벌 동기화는 하이브리드 실행의 지연 시간 상한 보장
- **적용 가능 알고리즘:** ASPIRE에서 정의된 유한 레이턴시 내성 비동기 반복 알고리즘
  - BFS, WCC, PageRank, SSSP 모두 올바른 결과 생성 확인
  - Figure 9(b): SSSP Bellman-Ford 예시에서 하이브리드 실행이 3글로벌 반복, 통합 반복은 4글로벌 반복

### 3.4. 아키텍처 프리미티브

- **인터 큐브 배치 통신 프리미티브:**
  - initBatch: 송수신 버퍼 등록, 섀도우 버퍼 할당 및 상태 플래그 초기화
  - sendBatch: 논블로킹 비동기 전송, 라우터에 오프로드
  - recvBatch: 블로킹 동기 수신, 소스 큐브 ID를 라운드 ID로 추론 가능

- **인터 큐브 링크 전원 관리:**
  - 유휴 링크를 Power-Down 모드로 설정 (HMC 사양 2.1)
  - 링크 상태 전환 시간 150µs 고려

- **인트라 큐브 메시지 패싱 프리미티브:**
  - Send: PU의 레지스터에서 send 큐브로 데이터 이동 (논블로킹)
  - Recv: receive 큐브에서 레지스터로 메시지 로드
  - Sync: PU에서 모든 AU에 라운드 종료 알림

## 핵심 기여

- **핵심 기여:**
  1. 비정형 데이터 이동을 근본적으로 해결하는 최초의 멀티노드 PIM 그래프 처리 아키텍처
  2. 분산 그래프 처리의 아이디어를 PIM 컨텍스트에 성공적으로 적용
  3. 정적이고 구조화된 통신 패턴이 PIM 기반 아키텍처에서 높은 처리량과 성능을 달성하는 데 핵심적

- **성능 향상:**
  - Tesseract 대비 평균 3.3× 스피드업, 81% 에너지 절감
  - 멀티노드에서 메모리 용량 비례적 확장성 입증

- **의의:**
  - PIM 기반 그래프 처리의 실용성을 크게 향상
  - 코드 수정 없이 기존 vertex 프로그래밍 모델과 호환
  - 그래프 크기 확장 시 메모리 대역폭이 선형적으로 증가하는 메모리 용량 비례적 확장성 달성

## 주요 결과

- **구현 언어:** zSim 기반 시뮬레이터
- **그래프 표현:** CSR (Compressed Sparse Row) 형식
- **소프트웨어-하드웨어 공동 설계:**
  - 아키텍처: 통신/동기화 프리미티브 제공
  - 런타임 시스템: vertex 프로그래밍 모델 인터페이스로 그래프 응용 지정
  - 프로그래머 수정 불필요 (런타임 시스템에서 투명하게 구현)

- **파라미터:**
  - PU/AU 수: 각각 8개
  - 큐 크기: 16
  - SPM 크기: AU당 64KB (총 8*64KB = 512KB per cube)
  - SPM 수용량: 128K vertex values (4바이트 기준)
  - 2M 미만 vertex 그래프는 전체 SPM에 완전 적재 가능

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2019MICRO-summarize/graphq-scalable-pim-based-graph-processing.md|전체 요약 보기]]
