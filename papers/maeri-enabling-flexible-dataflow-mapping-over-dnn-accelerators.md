---
tags: [paper, 2018, 2018ASPLOS, topic/dnn-accelerator, topic/dataflow]
venue: "ASPLOS 2018"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/maeri-enabling-flexible-dataflow-mapping-over-dnn-accelerators.md"
---

# MAERI: Enabling Flexible Dataflow Mapping over DNN Accelerators via Reconfigurable Interconnects

**Venue:** ASPLOS 2018
**저자:** Hyoukjun Kwon, Ananda Samajdar, Tushar Krishna (Georgia Institute of Technology)

## 개요

DNN 가속기는 고정된 데이터플로 패턴만 지원하여 임의의 데이터플로를 효율적으로 매핑하기 어려움. 고정된 데이터플로로 인해 사용 가능한 연산 자원의 활용도가 낮아지는 문제 발생.

MAERI는 모듈형이고 구성 가능한 기본 블록을 사용하여 유연한 데이터플로 매핑을 지원하는 DNN 가속기. 기존 고정 데이터플로 가속기 대비 8-459% 높은 활용도 달성.

## 방법론

### 기본 블록 설계
- Processing Element (PE): 곱셈-누적(MAC) 연산을 수행하는 기본 연산 단위
- Register File: PE의 입출력 데이터를 저장하는 레지스터 파일
- Switch Module: PE 간 데이터 흐름을 제어하는 스위치 모듈
- Global Buffer: 글로벌 데이터 버퍼로 가중치 및 특성 맵 저장

### 재구성 가능한 인터커넥트
- Network-on-Chip (NoC) 구조: 2D 메시 구조 기반의 인터커넥트
- 동적 라우팅: 데이터 흐름에 따라 동적으로 라우팅 경로 변경
- 다중icast: 하나의 데이터를 여러 PE로 동시에 전달 가능
- Reduction Tree: 감소 연산을 위한 트리 구조 지원

### 데이터플로 매핑 전략
- Weight Stationary: 가중치를 고정시키고 데이터를 순환시키는 매핑
- Output Stationary: 출력을 고정시키고 가중치와 입력을 순환시키는 매핑
- Row Stationary: 행 단위로 데이터를 재사용하는 매핑
- Layer Fusion: 여러 DNN 층을 융합하여 데이터 재사용 극대화

## 핵심 기여

1. 모듈형이고 구성 가능한 기본 블록을 사용하여 유연한 데이터플로 매핑을 지원하는 DNN 가속기 제시
2. 기존 고정 데이터플로 가속기 대비 8-459% 높은 활용도 달성
3. DNN 가속기의 프로그래밍 가능성 중요성을 강조

## 주요 결과

- 활용도 향상: 기존 고정 데이터플로 가속기 대비 8-459% 높은 활용도 달성
- 유연성: 다양한 DNN 토폴로지(합성곱, 순환, 풀링 등) 지원
- 매핑 효율성: 다양한 데이터플로 매핑을 효율적으로 지원
- 에너지 효율: 기존 ASIC 가속기 대비 15% 에너지 효율 향상

## 한계점

- 하드웨어 복잡성 증가로 인한 설계 비용 증가
- 특정 DNN 토폴로지에서의 최적화 제한
- 재구성 오버헤드로 인한 성능 저하 가능성

## 관련 개념

- [[paper-wiki/concepts/dnn-accelerator|DNN Accelerator]]
- [[paper-wiki/concepts/dataflow|Dataflow]]
- [[paper-wiki/concepts/network-on-chip|Network-on-Chip]]

## 관련 논문

- [MAERI 논문 요약](../paper-summaries/2018ASPLOS-summarize/maeri-enabling-flexible-dataflow-mapping-over-dnn-accelerators.md)