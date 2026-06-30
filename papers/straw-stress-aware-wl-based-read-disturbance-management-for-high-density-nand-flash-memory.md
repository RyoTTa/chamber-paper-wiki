---
tags: [paper, nand-flash, read-disturbance, ssd, reliability, storage]
venue: ASPLOS
year: 2026
summary_path: paper-summaries/2026ASPLOS-summarize/straw-stress-aware-wl-based-read-disturbance-management-for-high-density-nand-flash-memory.md
---

# STRAW: Stress-Aware WL-Based Read Disturbance Management for High-Density NAND Flash Memory

## 개요

STRAW는 고밀도 NAND 플래시 메모리의 읽기 방해(read disturbance) 문제를 해결하는 최초의 WL 기반 관리 기술입니다. 기존 블록 기반 읽기 복구(read reclaim)의 한계를 극복합니다.

## 방법론

- **스트레스 인식 WL 기반 읽기 복구 (WR2)**: 스트레스 받은 WL만 복구하여 조기 RR 최소화
- **스트레스 감소 읽기 (SR2)**: 적응적 Vpass 스케일링으로 읽기 방해 스트레스 사전 완화
- **Space-Saving 알고리즘**: WL별 카운터의 공간 오버헤드 최소화

## 핵심 기여

- 160개 실제 3D NAND 플래시 칩의 특성 분석 기반 읽기 방해 모델
- 이질적인 WL별 읽기 방해 허용치 정량화
- 반응적 접근의 한계 극복을 위한 선제적 완화 기법

## 주요 결과

- 기존 최첨단 기술 대비 평균 88.6% RR-induced page-copy 오버헤드 감소
- 3D QLC NAND에서의 심각한 신뢰도 문제 효과적 완화
- 다양한 읽기 패턴에서 일관된 성능 향상

## 한계점

- 특정 NAND 플래시 아키텍처에 최적화
- 읽기 패턴 분석 오버헤드 존재
- 지속적인 쓰기 작업에서의 성능 영향 미확인

## 관련 개념

- [[paper-wiki/concepts/nand-flash|NAND Flash Memory]]
- [[paper-wiki/concepts/ssd|Solid-State Drives]]
- [[paper-wiki/concepts/reliability|Reliability]]

## 관련 논문

- [Read reclaim techniques](paper-summaries/2023MICRO-summarize/read-reclaim-techniques-for-nand-flash-memory.md)
- [3D NAND flash memory](paper-summaries/2024ISCA-summarize/3d-nand-flash-memory.md)