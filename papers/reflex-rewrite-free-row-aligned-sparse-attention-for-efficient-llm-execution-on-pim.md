---
tags: [paper, 2026, 2026DAC, topic/pim, topic/llm, topic/sparse-attention]
venue: Design Automation Conference
year: 2026
summary_path: paper-summaries/2026DAC-summarize/reflex-rewrite-free-row-aligned-sparse-attention-for-efficient-llm-execution-on-pim.md
---

# REFLEX: Rewrite-Free Row-Aligned Sparse Attention for Efficient LLM Execution on PIM

## 개요

DRAM 행 구조와 sparse attention을 정렬하는 재쓰기 없는(rewrite-free) 프레임워크. Modulo 기반 페이지 읽기/쓰기와 행 정렬 명령 스케줄링을 통해 PIM 기반 LLM 디코딩의 행 활성화 오버헤드를 크게 감소.

## 방법론

- **Modulo-M Page Read (디코딩)**: sparse attention을 행 정렬된 페이지 그룹으로 제한
  - Read Modulus m으로 논리적 행을 m개 잔여 그룹으로 분할
  - Score-guided page selection으로 어텐션 적응성 유지
- **Modulo-N Page Write (프리필)**: 재쓰기 없는 행 정렬 KV 레이아웃 생성
  - Write Modulus n으로 페이지를 슬롯에 순환 매핑
  - 의미적으로 관련된 페이지가 동일 행에 자연스럽게 클러스터링
- **행 정렬 명령 스케줄링**: DRAM 연산을 행 단위로 스케줄링, KV 블록 기반 교차 실행

## 핵심 기여

- Sparse attention + PIM의 시너지를 데이터 배치, 희소성, 스케줄링 공동 설계로 실현
- 재쓰기 없이 정확도를 보존하면서 행 활성화 명령 18% 감소
- HBM3 기반 PIM에서 행 활용률 극대화 (K: 50% → 향상, V: 6% → 대폭 향상)

## 주요 결과

- **PIM 처리량**: LServe 대비 **1.64배** 향상
- **에너지 효율**: LServe 대비 **1.36배** 향상
- **시스템 처리량** (A100+PIM): LServe 대비 **1.37배** 향상
- **시스템 지연 시간**: LServe 대비 **1.27배** 감소
- LongBench에서 Dense 기반과 동일하거나 약간 향상된 정확도
- Needle-in-a-Haystack에서 20K+ 토큰 컨텍스트 전반에서 강건한 성능

## 한계점

- Write Modulus와 Read Modulus 선택에 대한 민감도 존재 (n < m 시 정확도 저하)
- 하드웨어 변경 불필요하지만, 기존 PIM 컨트롤러의 스케줄링 지원 필요
- 혼합 희소 Attention 지원 시 정적/동적 헤드 비율 조정 필요

## 관련 Concepts

- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]

## 관련 논문

- [paper-summaries/2026DAC-summarize/reflex-rewrite-free-row-aligned-sparse-attention-for-efficient-llm-execution-on-pim.md]
