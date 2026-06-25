---
tags: [concept, dnn-accelerator, dataflow, neural-network, hardware]
source_count: 1
last_updated: 2026-06-25
---

# DNN Accelerator

## Summary

DNN (Deep Neural Network) 가속기는 딥 뉴럴 네트워크의 연산을 가속화하는 전용 하드웨어입니다. 공간적(spatial) 구조를 채택하여 수백 개의 처리 요소(PE)가 병렬로 작동하며, 데이터플로(dataflow) 패턴에 따라 데이터 흐름이 결정됩니다.

## Key Ideas

### 데이터플로 매핑
- **Weight Stationary**: 가중치를 고정시키고 데이터를 순환시키는 매핑
- **Output Stationary**: 출력을 고정시키고 가중치와 입력을 순환시키는 매핑
- **Row Stationary**: 행 단위로 데이터를 재사용하는 매핑
- **MAERI**: 모듈형이고 구성 가능한 기본 블록을 사용하여 유연한 데이터플로 매핑을 지원 — 기존 고정 데이터플로 가속기 대비 8-459% 높은 활용도 달성 ([paper-summaries/2018ASPLOS-summarize/maeri-enabling-flexible-dataflow-mapping-over-dnn-accelerators.md])

### 아키텍처 설계
- Processing Element (PE): 곱셈-누적(MAC) 연산을 수행하는 기본 연산 단위
- Network-on-Chip (NoC): PE 간 데이터 흐름을 제어하는 인터커넥트
- 글로벌 버퍼: 가중치 및 특성 맵 저장
- 메모리 인터페이스: 외부 메모리와의 데이터 교환

### 프로그래밍 가능성
- 고정된 데이터플로 대신 유연한 데이터플로 매핑 지원
- 다양한 DNN 토폴로지(합성곱, 순환, 풀링 등) 지원
- 재구성 가능한 인터커넥트를 통해 동적 데이터 흐름 제어

## Related Papers

- [maeri-enabling-flexible-dataflow-mapping-over-dnn-accelerators.md]

## Cross-references

- [[paper-wiki/concepts/gpu|GPU]] - DNN 가속기와 GPU의 관계
- [[paper-wiki/concepts/dataflow|Dataflow]] - 데이터플로 매핑 개념