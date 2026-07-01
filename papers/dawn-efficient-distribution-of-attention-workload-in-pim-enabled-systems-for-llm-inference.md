---
tags: [paper, 2026, 2026IEEECAL, topic/pim, topic/llm, topic/workload-allocation]
venue: IEEE Computer Architecture Letters
year: 2026
summary_path: paper-summaries/2026IEEECAL-summarize/dawn-efficient-distribution-of-attention-workload-in-pim-enabled-systems-for-llm-inference.md
---

# DAWN: Efficient Distribution of Attention Workload in PIM-Enabled Systems for LLM Inference

## 개요

PIM 기반 LLM 추론 시스템에서 행렬을 청크(chunk)로 분할하여 워크로드를 할당하는 방법을 제안. 새로운 V 벡터를 NPU에 할당하여 데이터 재구성 오버헤드를 제거하고, 나머지 청크를 PIM에 균등 분배하여 부하 불균형을 해결.

## 방법론

- **청크 기반 워크로드 할당**: K^T/V 행렬을 N개 벡터의 청크로 분할, 청크를 할당 단위로 사용
- **NPU 활용**: 마지막 청크(새로운 V 요소 포함)를 NPU에 할당 → 재구성 오버헤드 제거
- **PIM 부하 균형**: Greedy approach로 청크를 가장 적게 로드된 PIM 채널에 순차 할당
- **부분 결과 수집**: NPU와 PIM이 각각 계산한 부분 결과를 NPU에서 수집하여 최종 결과 생성

## 핵심 기여

- 행렬 기반 할당의 두 가지 근본적 문제(재구성 오버헤드, 부하 불균형)를 동시에 해결
- NPU-PIM 이기종 시스템에서 실용적인 워크로드 할당 방법론 제시
- 청크 크기 N에 대한 최적화 방법론 및 민감도 분석 제공

## 주요 결과

- Throughput: matrix-based 할당 대비 최대 **44.2%** (평균 34.8%) 향상
- V 벡터당 쓰기 횟수 **97%** 감소
- 가장 많이 로드된 PIM 채널의 계산 시간 **62%** 감소
- NPU 계산 시간 증가 미미 (평균 2.3%)
- DAWN PIM-only도 평균 10.1% throughput 향상
- 64개 채널에서 평균 22.5% throughput 향상

## 한계점

- 청크 크기 N>32 시 NPU 계산 오버헤드 증가로 이점 감소
- N<32 시 빈번한 새 청크 생성으로 재구성 오버헤드 증가
- d=4K 기준 임계값 N=78 초과 시 matrix-based 할당 대비 이점 상실

## 관련 Concepts

- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]

## 관련 논문

- [paper-summaries/2026IEEECAL-summarize/dawn-efficient-distribution-of-attention-workload-in-pim-enabled-systems-for-llm-inference.md]
