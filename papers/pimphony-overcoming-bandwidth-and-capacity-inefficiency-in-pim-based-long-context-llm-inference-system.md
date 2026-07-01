---
tags: [paper, 2025, 2025HPCA, topic/pim, topic/llm, topic/long-context]
venue: IEEE International Symposium on High-Performance Computer Architecture
year: 2025
summary_path: paper-summaries/2025HPCA-summarize/pimphony-overcoming-bandwidth-and-capacity-inefficiency-in-pim-based-long-context-llm-inference-system.md
---

# PIMphony: Overcoming Bandwidth and Capacity Inefficiency in PIM-based Long-Context LLM Inference System

## 개요

긴 컨텍스트(최대 1M 토큰) LLM 추론에서 PIM의 세 가지 근본적 비효율성(채널 활용도 저하, I/O 병목, 정적 메모리 관리)을 해결하는 PIM 오케스트레이터. TCP, DCS, DPA의 세 가지 공동 설계 기술을 통해 PIM 활용도를 크게 향상.

## 방법론

- **Token-Centric PIM Partitioning (TCP)**: 배치 차원이 아닌 토큰 축을 따라 병렬성 재배치
  - 기존 HFP(Head-First Partitioning)의 긴 컨텍스트 비효율성 해결
  - 배치 크기와 관계없이 모든 채널에서 동시 활성화 보장
- **Dynamic PIM Command Scheduling (DCS)**: 실시간 데이터 의존성 기반 비순차 명령 발행
  - I/O 지연 시간을 숨기기 위해 데이터 이동과 계산 중첩
  - 정적 스케줄러의 고정된 WR-INP→MAC→RD-OUT 파이프라인 한계 극복
- **Dynamic PIM Access (DPA)**: 경량 의사-MMU를 통한 동적 KV 캐시 할당
  - 런타임 가상-물리 주소 변환으로 정적 메모리 낭비 제거
  - 평균 용량 활용률 36.2%에서 크게 개선

## 핵심 기여

- 긴 컨텍스트 LLM에서 PIM의 채널 활용도, I/O 효율, 메모리 관리를 동시에 최적화
- MLIR 기반 컴파일러로 소프트웨어 스택 통합, 실용적 구현 가능성 입증
- 기존 PIM 연구의 짧은 컨텍스트(4K) 한계를 극복하고 긴 컨텍스트(최대 1M) 지원

## 주요 결과

- **PIM 전용 시스템**: CENT 대비 최대 **11.3배** 성능 향상
- **xPU+PIM 시스템**: NeuPIMs 대비 최대 **8.4배** 성능 향상
- **채널 활용도**: TCP 적용으로 배치 크기와 관계없이 높은 활용도 유지
- **MAC 활용도**: 32K 컨텍스트에서 48% 활용도 감소 문제 해결
- **메모리 활용률**: 정적 메모리 낭비 대폭 감소

## 한계점

- LongBench/LV-Eval의 다양한 컨텍스트 길이 분산에 대한 추가 검증 필요
- MLIR 기반 컴파일러 구현의 복잡성
- PIM 하드웨어의 상용화 수준에 따른 구현 가능성 의존

## 관련 Concepts

- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]

## 관련 논문

- [paper-summaries/2025HPCA-summarize/pimphony-overcoming-bandwidth-and-capacity-inefficiency-in-pim-based-long-context-llm-inference-system.md]
