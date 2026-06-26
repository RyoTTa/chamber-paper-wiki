---
tags: [paper, 2018, 2018MICRO, topic/dram, topic/gpu]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/scope-a-stochastic-computing-engine-for-dram-based-in-situ-accelerator.md"
---

# SCOPE: A Stochastic Computing Engine for DRAM-Based In-Situ Accelerator

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** NOTA 논문 정보에서 확인 필요 (DRIMM 연구 그룹)

## 개요

- 데이터 이동 병목: 현대 컴퓨터 시스템에서 데이터 이동이 에너지와 지연 시간의 주요 병목 현상
- 기존 DRAM: 단순 저장 매체로만 활용되며, 연산은 별도의 프로세서에서 수행
- 인시tu 컴퓨팅(In-situ Computing)의 필요성: 데이터가 저장된 위치에서 직접 연산 수행으로 데이터 이동 최소화
- 확률적 컴퓨팅(Stochastic Computing, SC)의 장점:
  - 낮은 정밀도 비트 스트림을 사용한 간단한 연산 (AND 게이트로 곱셈, 덧셈은 비트 스트림 결합)
  - 낮은 면적, 낮은 전력 소비
  - 연산 오류에 대한 높은 관용성(tolerance)
- 기존 확률적 컴퓨팅의 한계:
  - 비트 스트림 길이에 따른 정밀도-속도 트레이드오프
  - 긴 비트 스트림은 높은 정밀도를 제공하지만 느린 연산 속도

## 방법론

### 3.1. DRAM 기반 확률적 컴퓨팅 아키텍처

- **기존 DRAM 구조 확장:**
  - Bank, Subarray, Computational SA(Sense Amplifier) 구조 유지
  - Simple Shifters: BLs(Bit Lines) 간, 서브어레이 간 데이터 통신 지원
  - Computational SA: 확률적 컴퓨팅 연산을 수행하는 핵심 구성 요소
  - Register, BL logic, Cell로 구성
  - Stochastic Number Generator (SNG): 확률적 비트 스트림 생성 (선택적)
  - Popcount 회로: 결과 비트 스트림에서 1의 비율 계산 (선택적)

### 3.2. 연산 메커니즘

- **AND 연산 (곱셈 for SC):**
  - 3사이클 연산: Read(X) → Read(Y) → Read(R)
  - R = X & Y (AND 게이트)
  - 확률적 곱셈 수행

- **CSA (Carry Save Adder) 연산:**
  - 4사이클 연산: Read(X) → Read(Y) → Read(C) → Read(G)
  - (S, Co) = X + Y + Cin 계산
  - 확률적 덧셈 수행

### 3.3. 정밀도 향상 기법

- **Hierarchical Bitstream:**
  - 원래 비트 스트림 (2n-1 비트)을 MSBs(Most Significant Bits)와 LSBs(Least Significant Bits)로 분할
  - X1s·X2s = (X1b·X2b)/2n 공식 사용
  - 비트 스트림 길이를 줄이면서 정밀도 유지

- **Hybrid-SC (Hybrid Stochastic Computing):**
  - 그룹 내부에서는 이진수(BIN) 사용, 그룹 외부에서는 확률적 컴퓨팅(SC) 사용
  - 2n-1 비트에서 (2n/2+1-2) 비트로 비트 수 감소
  - 정밀도와 속도의 균형 달성

- **ALAP-PCMUL (As Late As Possible - Probabilistic Counting Multiplication):**
  - 행별 합계(Row-wise sum)와 열별 합계(Column-wise sum)를 사용한 곱셈
  - 비트 스트림의 확률적 특성을 활용한 효율적 곱셈

- **ASAP-PC (As Soon As Possible - Probabilistic Counting):**
  - ALAP-PCMUL의 역순으로 빠른 연산 지원

## 핵심 기여

- **핵심 기여:** DRAM 기반 확률적 컴퓨팅 엔진 SCOPE 제안
- **성능 향상:** 기존 DRAM 대비 에너지 효율 및 면적 효율 크게 향상
- **의의:** 
  - 인시tu 컴퓨팅과 확률적 컴퓨팅을 결합한 최초의 시도
  - DRAM을 단순 저장 매체에서 연산 수행 가능한 컴퓨팅 리소스로 변환
  - 신경망 추론, 이미지 처리 등 확률적 컴퓨팅이 유리한 워크로드에 적용 가능
- **한계점:** 
  - 확률적 컴퓨팅의 고유한 정밀도 제한
  - 특정 워크로드에만 최적화 가능
  - 기존 프로그래밍 모델과의 호환성 문제

## 주요 결과

- DRAM 기반 하드웨어 구현
- 기존 DRAM 아키텍처에 최소한의 수정 추가
- Computational SA, SNG, Popcount 회로 등 하드웨어 구성 요소 추가
- 확률적 비트 스트림 생성 및 처리를 위한 제어 로직

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/scope-a-stochastic-computing-engine-for-dram-based-in-situ-accelerator.md|전체 요약 보기]]
