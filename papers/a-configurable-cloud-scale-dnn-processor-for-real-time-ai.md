---
tags: [paper, 2018, 2018ISCA, topic/gpu]
venue: "45th Annual International Symposium on Computer Architecture (ISCA '18)"
year: 2018
summary_path: "../paper-summaries/2018ISCA-summarize/a-configurable-cloud-scale-dnn-processor-for-real-time-ai.md"
---

# A Configurable Cloud-Scale DNN Processor for Real-Time AI

**Venue:** 45th Annual International Symposium on Computer Architecture (ISCA '18)
**저자:** Jeremy Fowers, Kalin Ovtcharov, Michael Papamichael, Todd Massengill, Ming Liu, Daniel Lo, Shlomi Alkalay, Michael Haselman, Logan Adams, Mahdi Ghandi, Stephen Heil, Prerak Patel, Adam Sapek, Gabriel Weisz, Lisa Woods, Sitaram Lanka, Steven K. Reinhardt, Adrian M. Caulfield, Eric S. Chung, Doug Burger (Microsoft)

## 개요

- 인터랙티브 AI 서비스(웹 검색, 광고, 음성 인식, 자율주행 등)는 DNN 모델의 저지연 평가를 요구 → "Real-Time AI"
- 기존 GPU 기반 가속기는 배치 처리(throughput)에 최적화되어 있어, 단일 요청의 지연 시간(latency)을 줄이기 어렵다
  - GPU는 요청 간 병렬성(inter-request parallelism)을 활용하여 throughput을 높이지만, 단일 요청에 할당 가능한 리소스가 제한
  - 배치 크기=1에서 GPU의 리소스 활용률이 크게 떨어짐
- 기존 NPU(Neural Processing Unit) 아키텍처:
  - 다중 스레드 기반 (GPU 스타일) 또는 미세한 MIMD (Graphcore 스타일)
  - 소프트웨어/컴파일러가 병렬성을 추출해야 하는 부담 존재
- 핵심 문제: **배치 없이(no batching)** 단일 요청의 지연 시간을 최소화하면서도 높은 처리량을 달성하는 아키텍처 부재

## 방법론

### 3.1. 전체 시스템 구조

- **데이터센터 아키텍처**: FPGA/ASIC 가속 카드가 데이터센터 네트워크에 직접 연결
  - 서버 NIC와 TOR 스위치 사이에 bump-in-the-wire로 배치
  - RDMA 유사 프로토콜로 데이터센터 내 수십만 서버와 저지연 직접 통신
  - 가속기를 논리적으로 분리하고 하드웨어 마이크로서비스로 풀링
- **DNN 가속 플랫폼 구성**:
  1. **툴플로**: 사전 학습된 DNN 모델 → BW NPU ISA 바이너리로 변환
  2. **연합 런타임**: CPU와 분산 하드웨어 마이크로서비스 간 모델 실행 오케스트레이션
  3. **BW NPU**: FPGA에 인스턴스화된 프로그래밍 가능 프로세서

### 3.2. 매트릭스-벡터 곱셈기 (MVM)

- **최대 100,000개 독립 곱셈기+축적기**로 구성된 네트워크
- **타일 엔진**: 각각 고유 크기의 MVM을 구현하는 시리즈로 구성
  - 각 타일 엔진 = 여러개의 곱셈기 유닛(Dot Product Engine, DPE)
  - DPE = 병렬 곱셈기 레인 + 축적 트리
- **4차원 병렬성 활용**:
  1. MVM 간 병렬성 (inter-MVM)
  2. 타일링 병렬성 (MVM tiling)
  3. 타일 내 행 간 병렬성
  4. 행 내 열 간 병렬성
- **MRF(Matrix Register File)**: 각 곱셈기에 전용 메모리 포트 제공 → 초당 수 Terabyte 대역폭
  - 타일별 뱅킹, 행별 서브뱅킹으로 읽기 포트 확장

### 3.3. 벡터 다기능 유닛 (MFU)

- MVM 출력을 처리하는 벡터 다기능 유닛 시리즈
- **지원 연산**:
  - 벡터-벡터 곱셈/덧셈/뺄셈/최대값
  - 단항 활성화 함수: ReLU, sigmoid, tanh
- **내부 구조**: 3개의 벡터 함수 유닛 + 논블로킹 크로스바
  - 크로스바를 현재 명령어 체인에 맞게 구성하여 함수 유닛 간 라우팅
  - 벡터 시퀀스를 파이프라인으로 처리
  - 2개 MFU 체인으로 대부분의 명령어 체인 지원

### 3.4. 계층적 디코딩 및 디스패치 (HDD)

- **Nios II/f 소프트 프로세서**가 BW NPU 명령어를 비동기적으로 발행
- **3단계 계층적 디코딩**:
  1. Nios → Top-Level Scheduler (T×N 동적 명령어)
  2. Top-Level Scheduler → 6개 디코더 + 4개 세컨드 레벨 스케줄러
  3. 세컨드 레벨 스케줄러 → 41개 디코더 → 수천 개의 곱셈기
- **평균 4클래시마다 1개 복합 명령어**를 Nios에서 디스패치 → 전체 파이프라인 가동 유지

### 3.5. 합성 전문화 (Synthesis Specialization)

- 4개 합성 시점 파라미터:
  1. **데이터 타입 (정밀도)**: Float16, BFP 등
  2. **네이티브 벡터 크기**: 모델별 최적 벡터 길이
  3. **데이터 레인 수**: 병렬 곱셈기 수
  4. **매트릭스-벡터 타일 엔진 크기**: MVM 자원 할당
- 하드웨어 구현 유연성: FPGA ↔ ASIC 모두 가능
- 모델 클래스별 경량 마이크로아키텍처 구성 가능

## 핵심 기여

- **핵심 기여**: 배치 없는 real-time DNN 추론을 위한 최초의 프로덕션 규모 NPU 아키텍처
- **성능**: Stratix 10 FPGA에서 35 TeraFLOPS 달성 (배치 없음), GPU 대비 10배 이상 지연 시간 개선
- **아키텍처 혁신**: 단일 스레드 SIMD + HDD + VLP의 조합으로 소프트웨어 부담 최소화 while 대규모 병렬성 활용
- **실용성**: Azure 데이터센터에 실제 프로덕션 배포, 수백만 서버에 걸친 하드웨어 마이크로서비스 인프라
- **의의**: "Real-Time AI" 개념 정립 → 배치 없이도 throughput과 latency를 동시에 달성 가능함을 입증

## 주요 결과

- **플랫폼**: Intel Stratix 10 280 FPGA
- ** ISA**: 단일 스레드 SIMD, 매트릭스-벡터/벡터-벡터 연산
- **제어 프로세서**: Nios II/f 소프트 프로세서
- **네트워크**: 데이터센터 네트워크에 직접 연결, RDMA 유사 프로토콜
- **프로그래밍 모델**: LSTM 기준 ~100줄의 코드로 완전 파라미터화 및 성능 튜닝 가능

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/gpu.md|GPU]]


## 전체 요약

[[../paper-summaries/2018ISCA-summarize/a-configurable-cloud-scale-dnn-processor-for-real-time-ai.md|전체 요약 보기]]
