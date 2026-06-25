---
tags: [paper, 2018, 2018ISCA, topic/gpu, topic/llm-inference]
venue: "ISCA 2018"
year: 2018
summary_path: "../paper-summaries/2018ISCA-summarize/a-configurable-cloud-scale-dnn-processor-for-real-time-ai.md"
---

# A Configurable Cloud-Scale DNN Processor for Real-Time AI

**Venue:** ISCA 2018
**저자:** Jeremy Fowers, Kalin Ovtcharov, Michael Papamichael, Todd Massengill, Ming Liu, Daniel Lo, Shlomi Alkalay, Michael Haselman, Logan Adams, Mahdi Ghandi, Stephen Heil, Prerak Patel, Adam Sapek, Gabriel Weisz, Lisa Woods, Sitaram Lanka, Steven K. Reinhardt, Adrian M. Caulfield, Eric S. Chung, Doug Burger (Microsoft)

## 개요

인터랙티브 AI 서비스는 배치 없는 DNN 추론에서 저지연과 높은 처리량을 동시에 요구한다. 기존 GPU는 배치 처리에 최적화되어 단일 요청의 지연 시간을 줄이기 어렵다.

Brainwave NPU는 단일 스레드 SIMD ISA와 계층적 디코딩/디스패치(HDD)를 통해 단일 명령어가 7M 이상의 기본 연산으로 확장되는 아키텍처이다. Intel Stratix 10 FPGA에서 배치 없이 35 TeraFLOPS를 달성하며, GPU 대비 10배 이상 낮은 지연 시간을 보인다.

## 방법론

### 시스템 아키텍처
- FPGA/ASIC 가속 카드가 데이터센터 네트워크에 직접 연결 (bump-in-the-wire)
- RDMA 유사 프로토콜로 수십만 서버와 저지연 통신
- 가속기를 하드웨어 마이크로서비스로 풀링

### 매트릭스-벡터 곱셈기 (MVM)
- 최대 100,000개 독립 곱셈기+축적기로 구성
- 4차원 병렬성: inter-MVM, 타일링, 행 간, 열 간
- MRF(Matrix Register File)로 초당 수 Terabyte 대역폭

### 계층적 디코딩 및 디스패치 (HDD)
- Nios II/f 소프트 프로세서에서 BW NPU 명령어 비동기 발행
- 3단계 계층적 디코딩으로 수천 개의 곱셈기에 분산 디스패치
- 평균 4클래시마다 1개 복합 명령어 디스패치

### 합성 전문화
- FPGA 합성 시점에 데이터 타입, 벡터 크기, 데이터 레인 수, 타일 엔진 크기 조정
- 모델 클래스별 경량 마이크로아키텍처 구성

## 핵심 기여

1. 배치 없는 real-time DNN 추론을 위한 최초의 프로덕션 규모 NPU
2. 단일 스레드 SIMD + HDD + VLP로 소프트웨어 부담 최소화 while 대규모 병렬성 활용
3. Azure 데이터센터 실제 프로덕션 배포

## 주요 결과

- **처리량**: 11~35.9 TeraFLOPS (배치 없음)
- **지연 시간**: 4ms 미만 (대규모 RNN 기준)
- **GPU 대비**: watt-for-watt 10배 이상 지연 시간/처리량 개선
- **정밀도**: Float16/BFP로 모델 스코어링 정확도 동일

## 한계점

- FPGA 클럭 속도 및 면적 오버헤드로 하드 NPU 대비 열등할 수 있음
- 단일 노드 평가 중심, 멀티 FPGA 모델 분할은 간략히 언급

## 관련 개념

- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
