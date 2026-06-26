---
tags: [paper, 2018, 2018ASPLOS, topic/disaggregation, topic/dram, topic/storage]
venue: "23rd International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '18)"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/maeri-enabling-flexible-dataflow-mapping-over-dnn-accelerators.md"
---

# MAERI: Enabling Flexible Dataflow Mapping over DNN Accelerators via Reconfigurable Interconnects

**Venue:** 23rd International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '18)
**저자:** Hyoukjun Kwon, Ananda Samajdar, Tushar Krishna (Georgia Institute of Technology)

## 개요

- 딥 뉴럴 네트워크(DNN)는 컴퓨터 비전과 음성 인식에서 높은 성능을 보여주고 있으며, AI의 기반 기술로 자리잡고 있음
- DNN의 높은 연산 복잡성과 에너지 효율성 요구로 인해 하드웨어 가속기에 대한 연구가 급증
- DRAM 접근 비용을 줄이기 위해 대부분의 DNN 가속기는 공간적(spatial) 구조를 채택하여 수백 개의 처리 요소(PE)가 병렬로 작동
- DNN은 빠르게 진화하고 있어 합성곱, 순환, 풀링, 완전 연결 층 등 다양한 층과 다양한 입출력 크기가 최신 토폴로지에 존재
- 기존 DNN 가속기는 고정된 데이터플로 패턴만 지원하므로 임의의 데이터플로를 효율적으로 매핑하기 어려움
- 고정된 데이터플로로 인해 사용 가능한 연산 자원의 활용도가 낮아지는 문제 발생

## 방법론

### 3.1. 기본 블록 설계

- **Processing Element (PE)**: 곱셈-누적(MAC) 연산을 수행하는 기본 연산 단위
- **Register File**: PE의 입출력 데이터를 저장하는 레지스터 파일
- **Switch Module**: PE 간 데이터 흐름을 제어하는 스위치 모듈
- **Global Buffer**: 글로벌 데이터 버퍼로 가중치 및 특성 맵 저장

### 3.2. 재구성 가능한 인터커넥트

- **Network-on-Chip (NoC) 구조**: 2D 메시 구조 기반의 인터커넥트
- **동적 라우팅**: 데이터 흐름에 따라 동적으로 라우팅 경로 변경
- **다중icast**: 하나의 데이터를 여러 PE로 동시에 전달 가능
- ** Reduction Tree**: 감소 연산을 위한 트리 구조 지원

### 3.3. 데이터플로 매핑 전략

- **Weight Stationary**: 가중치를 고정시키고 데이터를 순환시키는 매핑
- **Output Stationary**: 출력을 고정시키고 가중치와 입력을 순환시키는 매핑
- **Row Stationary**: 행 단위로 데이터를 재사용하는 매핑
- **Layer Fusion**: 여러 DNN 층을 융합하여 데이터 재사용 극대화

## 핵심 기여

- **핵심 기여**: 모듈형이고 구성 가능한 기본 블록을 사용하여 유연한 데이터플로 매핑을 지원하는 DNN 가속기 MAERI 제시
- **성능 향상**: 기존 고정 데이터플로 가속기 대비 8-459% 높은 활용도 달성
- **의의**: DNN 가속기의 프로그래밍 가능성 중요성을 강조, 향후 DNN 진화에 적응할 수 있는 유연한 가속기 설계 기반 마련

---

## 참고 자료

- 원본 논문: paper-source/2018ASPLOS/MAERI_Flexible_Dataflow_DNN_Accelerators.pdf
- 요약 파일: paper-summaries/2018ASPLOS-summarize/maeri-enabling-flexible-dataflow-mapping-over-dnn-accelerators.md

## 주요 결과

- 구현 언어: Verilog (하드웨어 설계)
- 코드 라인 수: 약 10,000줄
- 프레임워크: Custom DNN accelerator simulator
- 시스템 구성 요소:
  - PE 배열 (8x8 배열)
  - 재구성 가능한 NoC
  - 글로벌 버퍼
  - 제어 유닛
  - 메모리 인터페이스

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2018ASPLOS-summarize/maeri-enabling-flexible-dataflow-mapping-over-dnn-accelerators.md|전체 요약 보기]]
