---
tags: [paper, 2020, 2020MICRO, topic/dram, topic/gpu, topic/nvm, topic/pim]
venue: "53rd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '20)"
year: 2020
summary_path: "../paper-summaries/2020MICRO-summarize/dual-acceleration-of-clustering-algorithms-using-digital-based-processing-in-memory.md"
---

# DUAL: Acceleration of Clustering Algorithms using Digital-based Processing In-Memory

**Venue:** 53rd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '20)
**저자:** Mohsen Imani, Saikishan Pampana, Saransh Gupta, Minxuan Zhou, Yeseong Kim, Tajana Rosing (UC Irvine, UC San Diego, DGIST)

## 개요

- IoT 디바이스에서 생성되는 대용량 데이터의 대부분은 레이블이 없는 비지도 학습(Unsupervised Learning) 데이터이며, 클러스터링 알고리즘이 가장 널리 사용됨
- 클러스터링 알고리즘은 모든 데이터 쌍 간의 거리 계산(pairwise distance computation)을 요구하여 연산량이 O(n³)으로 매우 큼
- 기존 프로세서에서 대규모 데이터셋의 클러스터링을 수행하면 프로세서-메모리 간 데이터 이동 비용으로 인해 높은 에너지 소비와 느린 처리 속도에 시달림
- 기존 PIM(Processing In-Memory) 아키텍처의 한계:
  - 클러스터링에 필요한 주요 연산(유사도 검색, 최근접 탐색)을 완전히 지원하지 못함
  - 대부분의 기존 PIM이 아날로그 기반으로 DAC/ADC 블록이 칩 면적/파워의 98%를 차지하여 throughput/area 효율이 낮음
  - 별도의 저장 메모리와 연산 메모리가 필요하여 내부 데이터 이동 오버헤드 발생
- NVIDIA GTX 1080 GPU 대비 58.8배 속도 향상과 251.2배 에너지 효율 개선이 달성됨

## 방법론

### 3.1. HD-Mapper (인코딩 모듈)

- 원본 특성 벡터 F = {f₁, f₂, ..., fₘ}를 D차원 이진 하이퍼벡터 H = {h₁, h₂, ..., h_D}로 변환
- 인코딩 과정:
  - 각 하이퍼벡터 차원을 임의 벡터 Bᵢ와의 내적으로 계산: hᵢ = cos(Bᵢ · F)
  - 임의 벡터 {B₁, B₂, ..., B_D}는 가우시안 분포에서 오프라인으로 사전 생성
  - sign 함수로 이진화: H' = sign(H) → 모든 양수 차원을 '1', 0/음수를 '0'
- RBF 커널 근사: K(x,y) = e^(-||x-y||²/2σ²) ≈ z(x) · z(y)
- 인코딩은 메모리에서 행 병렬 곱셈과 덧셈으로 가속 (Figure 5)
  - 블록 1: 입력 데이터와 기본 벡터의 내적 계산
  - 블록 2: 코사인 함수를 Taylor 전개 3개 항으로 근사하여 적용
- 확장 가능: 기본 벡터가 메모리 행 수를 초과하면 추가 메모리 블록에 분산 저장

### 3.2. 디지털 PIM 가속기

- **데이터 블록 (Data Block):** 인코딩된 데이터 포인트 저장, 행 병렬 하밍 거리 계산 수행
- **거리 블록 (Distance Block):** 페어와이즈 거리 행렬 저장, 클러스터링 연산 수행
- 두 블록은 인터커넥트로 연결되어 비트 직렬/행 병렬 데이터 전송 지원
- 지원 연산:
  1. **검색 기반 연산:** 행 병렬 하밍 거리 계산, 최근접 탐색
  2. **산술 연산:** 행 병렬 덧셈, 곱셈, 나눗셈 (NOR 게이트 기반)

### 3.3. 하밍 거리 계산 (Figure 4)

- CAM(Content Addressable Memory) 셀을 수정하여 하밍 거리 계산 지원
  - 각 CAM 셀은 2개의 NVM 디바이스로 구성 (0T-2R, 보수 값 저장)
  - 매칭된 경우 ML(Match-Line)이 충전 유지, 불일치 시 ML 방전
- ML 방전 시간 특성을 활용한 하밍 거리 검출:
  - 불일치 비트가 많을수록 ML이 더 빠르게 방전
  - 비선형 샘플링 시간으로 최대 7비트까지 병렬 검색 가능
  - 3비트 카운터로 7비트 윈도우의 결과를 1 사이클에 거리 메모리에 기록
- 처리 시간: 200ps/100ps 샘플링, 에너지: 1632fJ (7비트)

### 3.4. 최근접 값 탐색 (Figure 4d)

- 서로 다른 비트 위치에 가중치 부여 (MSB에 높은 전압 할당)
  - V₁=0.8V, V₂=0.4V, V₃=0.2V, V₄=0.1V
- 4비트 병렬 검색으로 정확한 최근접 값 탐색
- 5000회 몬테카를로 시뮬레이션으로 10% 기술/메모리스트 변동에서도 정확성 검증

### 3.5. 메모리 기반 산술 연산 (Figure 4e)

- memristor 스위칭 특성을 활용한 NOR 게이트 구현
  - NOR는 만능 로직 게이트로 덧셈과 곱셈 구현 가능
  - 나눗셈은 분모의 역수를 곱하는 것으로 근사
- 행 병렬로 모든 활성화된 메모리 행에서 동시 연산
- 단일 연산은 CMOS보다 약 60배 느리지만, 대규모 병렬성으로 전체 효율 우위

## 핵심 기여

- **핵심 기여:** 최초의 디지털 기반 PIM 아키텍처로 비지도 학습(클러스터링)을 가속하는 DUAL 제시
- ** 알고리즘-하드웨어 공동 설계:** HD-Mapper의 비선형 인코딩과 디지털 PIM의 하밍 거리 계산이 결합되어 유클리드 거리 기반 클러스터링을 메모리 친화적으로 변환
- **실용적 성과:** GPU 대비 58.8배 속도, 251.2배 에너지 효율, 품질 손실 없음
- **기술적 의의:** ADC/DAC 불필요로 높은 throughput/area 달성, 행 병렬 검색/산술 연산으로 대규모 병렬성 확보
- **범용성:** 계층적 클러스터링, K-means, DBSCAN 등 다양한 알고리즘 지원
- **향후 과제:** 더 큰 데이터셋에서의 확장성, 다양한 NVM 기술과의 통합

## 주요 결과

- **하드웨어 구성:**
  - 64개 타일, 각 타일에 256개 크로스바 메모리 블록
  - 각 메모리 블록: 1K × 1K 크기
  - 타일당 면적: 0.84 mm², 전력: 1.76W
  - 전체 DUAL 면적: 53.57 mm², 전체 전력: 113.51W
  - 총 메모리 용량: 2GB
- **연산 특성 (Table III, 28nm 기술):**
  - 하밍 거리 계산: 1632fJ, 200/100ps
  - 최근접 탐색: 1214fJ, 200ps
  - 8비트 덧셈: 2.3pJ, 98.4ns
  - 8비트 곱셈: 67.7pJ, 448.3ns
  - 8비트 나눗셈: 72.5pJ, 561.4ns
- **소프트웨어 스택:**
  - VLCA(Variable-Length Column Array) 데이터 구조로 모든 연산 값을 표현
  - PIM 명령어 세트: hamm_7, add/sub/mul/div, near_search, row_mv 등
  - 런타임 라이브러리가 함수 호출을 PIM 명령어로 변환

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2020MICRO-summarize/dual-acceleration-of-clustering-algorithms-using-digital-based-processing-in-memory.md|전체 요약 보기]]
