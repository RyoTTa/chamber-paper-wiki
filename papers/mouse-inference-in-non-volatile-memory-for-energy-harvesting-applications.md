---
tags: [paper, 2020, 2020MICRO, topic/llm-inference, topic/nvm, topic/pim, topic/storage]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO) 2020"
year: 2020
summary_path: "../paper-summaries/2020MICRO-summarize/mouse-inference-in-non-volatile-memory-for-energy-harvesting-applications.md"
---

# MOUSE: Inference In Non-volatile Memory for Energy Harvesting Applications

**Venue:** IEEE/ACM International Symposium on Microarchitecture (MICRO) 2020
**저자:** Salonik Resch, S. Karen Khatamifard, Zamshed I. Chowdhury, Masoud Zabihi, Zhengyang Zhao, Husrev Cilasun, Jian-Ping Wang, Sachin S. Sapatnekar, Ulya R. Karpuzcu (University of Minnesota, Twin Cities)

## 개요

- 저전력 엣지 디바이스에서 머신러닝 추론 능력에 대한 수요가 증가하고 있으며, 에너지 하베스팅 기술은 배터리 없이도 이러한 디바이스의 배치를 가능하게 함
- 에너지 하베스팅 애플리케이션은 극도로 높은 에너지 효율성과 전원 차단에 대한 내성 Requirement가 있음
- 기존 에너지 하베스팅 디바이스에서의 간헐적 처리(Intermittent Processing)는 정확성 보장, 효율적인 shut down/restart, 순방향 진행(Forward Progress) 보장이라는 세 가지 핵심 과제를 제기
- 기존 checkpointing 기법은 추가적인 지연시간과 에너지, 그리고 복잡한 소프트웨어 지원이 필요하며, 두 checkpoint 사이의 에너지 요구량이 너무 크면 프로그램이 멈추는 비종료(Non-termination) 문제가 발생
- 저전력 마이크로컨트롤러(예: MSP430FR5994) 자체가 100mm² 이상의 면적을 차지하며, 에너지 하베스팅 시스템에서 상당한 면적 오버헤드를 초래

## 방법론

### 3.1. 스피니트로닉 PIM 기반

- CRAM은 STT-MRAM 배열을 기반으로 하며, 각 셀은 1개의 MTJ와 1개의 접근 트랜지스터로 구성
- 논리 연산은 외부 로직 회로나 감지 증폭기(Sense Amplifier) 없이 배열 내부에서 완전히 수행
- NAND, AND, OR 등 기본 논리 게이트를 MTJ 연결을 통해 구현 가능
- 복잡한 연산(예: full-add)은 기본 논리 게이트 9개의 순차적 수행으로 구성

### 3.2. 배열 아키텍처

- 각 열에 두 개의 비트 라인(BLE: Bit Line Even, BLO: Bit Line Odd)과 로직 라인(LL)이 존재
- 각 행에는 접근 트랜지스터를 제어하는 워드 라인(WL)이 존재
- 메모리 연산: WL을 활성화하고 LL과 비트 라인之间에 전압 차를 적용하여 읽기/쓰기 수행
- 논리 연산: 입력 행(n1, n2)과 출력 행(m)을 활성화하고 BLE와 BLO之间에 전압 차를 적용
- 열 수준 병렬성(Column-level Parallelism)을 통해 다수의 열에서 동시에 연산 수행 가능

### 3.3. SHE(Spin Hall Effect) 채널 대안

- 각 MTJ에 SHE 채널을 추가하여 읽기/쓰기 경로를 분리
- 읽기 경로(tread)와 쓰기 경로(twrite)를 독립적으로 최적화 가능
- 쓰기 전류 밀도가 낮아져 에너지 효율성 향상
- 논리 연산 시 입력 MTJ 저항의 영향이 줄어들어 연산 견고성 증가

## 핵심 기여

- MOUSE는 비휘발성 스피니트로닉 메모리 기반 PIM을 활용하여 에너지 하베스팅 애플리케이션에 최적화된 머신러닝 추론 가속기
- MTJ 논리 연산의 멱등성 특성을 활용하여 전원 차단 상황에서도 정확성 보장
- 모든 연산 후 자동 checkpointing이 발생하여 즉시 재시작 가능
- SVM과 BNN 추론에서 높은 에너지 효율성과 성능 달성
- 에너지 하베스팅 기반 저전력 엣지 디바이스의 실용화에 기여

## 주요 결과

- 구현 언어: Not specified (하드웨어 설계)
- MOUSE는 타일 기반 아키텍처로 구성
- 각 타일은 MTJ 배열, 행 디코더, 열 디코더로 구성
- 구성 요소: 메모리 컨트롤러, 128B 메모리 버퍼, 비휘발성 PC 레지스터, 비휘발성 명령 버퍼, 전압 감지 회로
- 64비트 명령어 형식: 논리 연산, 메모리 연산, 열 활성화 세 가지 타입
- 에너지 버퍼(커패시터)를 활용하여 에너지를 시간에 걸쳐 축적한 후 버스트로 소비

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2020MICRO-summarize/mouse-inference-in-non-volatile-memory-for-energy-harvesting-applications.md|전체 요약 보기]]
