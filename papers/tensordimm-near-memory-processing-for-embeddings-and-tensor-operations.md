---
tags: [paper, 2019, 2019MICRO, topic/dram, topic/gpu, topic/near-data-processing]
venue: "52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '19)"
year: 2019
summary_path: "../paper-summaries/2019MICRO-summarize/tensordimm-near-memory-processing-for-embeddings-and-tensor-operations.md"
---

# TensorDIMM: A Practical Near-Memory Processing Architecture for Embeddings and Tensor Operations in Deep Learning

**Venue:** 52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '19)
**저자:** Youngeun Kwon, Yunjae Lee, Minsoo Rhu (KAIST)

## 개요

- 딥러닝 애플리케이션의 복잡성이 급증하면서, GPU/NPU 등 고성능 가속기를 활용한 확장형 시스템 설계가 증가 추세
- **임베딩 레이어의 메모리 병목 문제:**
  - 하이퍼스케일러们的 연구에 따르면 임베딩 룩업과 텐서 조작은 오늘날 데이터센터에서 배포되는 가장 메모리 집약적인 딥러닝 알고리즘
  - Facebook 데이터센터 기준: 임베딩 레이어가 전체 DL 워크로드 실행 시간의 **34%** 차지
  - 임베딩 모델 크기: 수백 GB 규모 → GPU의 물리적 메모리 용량(수십 GB) 초과
- **기존 해결책의 한계:**
  - CPU 전용 구현: 저대역폭 CPU 메모리에서 임베딩 벡터를 읽음 → **7.3-20.9× slowdown** (GPU 전용 대비)
  - 하이브리드 CPU-GPU: CPU에서 임베딩 룩업 후 GPU로 복사 → PCIe 채널(16GB/sec)의 대역폭 병목
  - CPU-GPU 간 데이터 복사 지연으로 인한 성능 저하
- **핵심 문제:** 임베딩 레이어의 높은 메모리 용량 및 대역폭 요구사항을 충족시키는 아키텍처적 솔루션 부재

## 방법론

### 3.1. 하드웨어 아키텍처: TensorDIMM

- **DIMM 구조:**
  - 상용 버퍼링 DIMM(예: Registered DIMM, Load-Reduced DIMM) 기반
  - 버퍼 디바이스에 NMP 유닛 통합
  - 64개 데이터 I/O(DQ) 핀 가진 표준 DIMM 폼팩터
- **근메모리 프로세싱(NMP) 유닛:**
  - 임베딩 gather 연산 수행: 여러 임베딩 벡터를 동시에 읽기
  - 리듀스(reduction) 연산: 읽어온 임베딩 벡터들의 합산/평균 계산
  - 메모리 대역폭 증폭 효과: TensorDIMM 수에 비례하여 대역폭 확장
  - 레이턴시 절감: 데이터가 DIMM 내부에서 직접 처리되어 CPU/GPU까지 이동 불필요
- **메모리 기술:** 상용 DRAM 디바이스 그대로 사용 → 비용 효율적

### 3.2. 소프트웨어 스택: TensorISA 및 런타임 시스템

- **TensorISA (텐서 ISA):**
  - DL 텐서 연산에 특화된 커스텀 명령어 세트
  - 메모리 대역폭 효율적 연산 수행
  - gather 및 reduce 명령어 지원
  - TensorDIMM과 공동 설계(co-design)되어 대역폭 확장성 보장
- **주소 매핑 스킴:**
  - 임베딩에 대한 효율적 주소 매핑
  - TensorDIMM 간 분산 저장 최적화
  - 메모리 컨트롤러의 대역폭 제약 극복
- **런타임 시스템:**
  - TensorDIMM을 활용한 텐서 연산 스케줄링
  - 임베딩 룩업 자동화
  - CPU-GPU 간 데이터 복사 최소화

### 3.3. 시스템 아키텍처: TensorNode

- **분산 메모리 노드:**
  - TensorDIMM 모듈 풀로 구성된 메모리 풀
  - NVSwitch 기반 고대역폭 GPU 인터커넥트 내부에 배치
  - NVIDIA DGX-2와 유사한 16-GPU 환경에서 평가
- **메모리 용량 확장:**
  - TensorNode에 임베딩 룩업 테이블 완전 저장
  - GPU 메모리 대비 수 배 큰 용량 제공
- **대역폭 확장:**
  - NVLINK v2: 25GB/sec 풀듀플렉스 양방향 대역폭/링크
  - TensorISA와 결합하여 실제 임베딩 연산 대역폭 대폭 증가

### 3.4. 임베딩 레이어 처리 흐름

- **임베딩 룩업 단계:**
  1.稀疏 특징(sparse features)이 입력으로 주어짐
  2. TensorDIMM에서 임베딩 벡터 수집(gather)
  3. NMP 유닛이 메모리 내에서 직접 리듀스 수행
- **DNN 추론 단계:**
  1. 밀집 특징(dense features)은 기존 GPU/NPU에서 처리
  2. 임베딩 결과는 TensorNode에서 가져옴
  3. 특성 상호작용(feature interaction) 후 상위 MLP 처리

## 핵심 기여

- **핵심 기여:** 희소 임베딩 레이어의 메모리 병목 문제를 해결하는 최초의 아키텍처적 솔루션 제시
- **실용적 설계:** 상용 DRAM을 기반으로 한 TensorDIMM으로 실용성 및 구현 용이성 확보
- **성능 향상:** CPU 전용 대비 6.2-15.0×, 하이브리드 CPU-GPU 대비 8.9-17.6× 추론 시간 단축
- **확장성:** TensorISA와 TensorNode를 통한 메모리 용량 및 대역폭 동시 확장
- **산업적 의의:** 추천 시스템 등 실제 산업 DL 애플리케이션에 즉시 적용 가능한 솔루션
- **학술적 기여:** 임베딩 레이어라는 새로운 메모리 집약적 DL 워크로드에 대한 아키텍처 연구 영역 개척

## 주요 결과

- **하드웨어 프로토타입:**
  - 상용 GPU 시스템 기반 TensorDIMM 프로토타입 구현
  - NVSwitch 인터커넥트 활용한 TensorNode 연결
- **소프트웨어 프로토타입:**
  - 고성능 GPU 시스템에서的概念 검증(proof-of-concept) 구현
  - TensorISA와 런타임 시스템 통합
- **시스템 구성:**
  - GPU: NVIDIA Tesla V100 (16GB HBM2)
  - 메모리: TensorDIMM 기반 DRAM 모듈
  - 인터커넥트: NVLINK v2

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]


## 전체 요약

[[../paper-summaries/2019MICRO-summarize/tensordimm-near-memory-processing-for-embeddings-and-tensor-operations.md|전체 요약 보기]]
