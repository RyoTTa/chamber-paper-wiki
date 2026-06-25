---
tags: [pim, stochastic-computing, dram, in-situ-accelerator, energy-efficiency]
venue: MICRO
year: 2018
summary_path: paper-summaries/2018MICRO-summarize/scope-a-stochastic-computing-engine-for-dram-based-in-situ-accelerator.md
---

# SCOPE: A Stochastic Computing Engine for DRAM-Based In-Situ Accelerator

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** NOTA 논문 정보에서 확인 필요 (DRIMM 연구 그룹)

---

## 개요

DRAM 기반 인시itu 가속기를 위한 확률적 컴퓨팅 엔진 SCOPE를 제안. 기존 DRAM 아키텍처를 최소한으로 수정하여 확률적 컴퓨팅 연산을 수행하며, 데이터 이동 오버헤드를 크게 줄임. Hierarchical bitstream 및 Hybrid-SC 기법을 통해 정밀도-속도 트레이드오프를 개선.

## 방법론

- **DRAM 기반 확률적 컴퓨팅:** Computational SA에서 확률적 비트 스트림 기반 연산 수행
- **AND 연산 (곱셈 for SC):** 3사이클 연산으로 확률적 곱셈 구현
- **CSA (Carry Save Adder):** 4사이클 연산으로 확률적 덧셈 구현
- **Hierarchical Bitstream:** MSBs/LSBs 분할을 통한 정밀도 유지 및 비트 수 감소
- **Hybrid-SC:** 그룹 내부 BIN + 그룹 외부 SC로 정밀도-속도 균형

## 핵심 기여

- DRAM 기반 확률적 컴퓨팅 엔진 최초 제안
- 기존 DRAM에 최소한의 수정으로 인시tu 컴퓨팅 지원
- 확률적 컴퓨팅의 정밀도 제한을 하드웨어 기법으로 완화

## 주요 결과

- 기존 DRAM 대비 높은 에너지 효율 달성
- 확률적 컴퓨팅을 통한 낮은 면적/전력 오버헤드
- DRAM 기반 인시tu 컴퓨팅의 실현 가능성 입증

## 한계점

- 확률적 컴퓨팅의 고유한 정밀도 제한
- 특정 워크로드(신경망 추론, 이미지 처리)에만 최적화 가능
- 기존 프로그래밍 모델과의 호환성 문제

## 관련 개념

- [[paper-wiki/concepts/processing-in-memory.md|Processing-in-Memory]]
- [[paper-wiki/concepts/dram.md|DRAM]]

## 전체 요약

[paper-summaries/2018MICRO-summarize/scope-a-stochastic-computing-engine-for-dram-based-in-situ-accelerator.md](paper-summaries/2018MICRO-summarize/scope-a-stochastic-computing-engine-for-dram-based-in-situ-accelerator.md)