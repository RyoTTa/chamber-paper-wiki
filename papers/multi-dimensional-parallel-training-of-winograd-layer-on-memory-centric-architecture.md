---
tags: [paper, ndp, winograd, cnn-training, memory-centric, 2018]
venue: MICRO 2018
year: 2018
summary_path: paper-summaries/2018MICRO-summarize/multi-dimensional-parallel-training-of-winograd-layer-on-memory-centric-architecture.md
---

# Multi-dimensional Parallel Training of Winograd Layer on Memory-Centric Architecture

## 개요

- Winograd 변환의 intra-tile 병렬성을 데이터 병렬성과 결합한 다차원 병렬 학습(MPT) 제안
- 메모리 중심 NDP 아키텍처와 하이브리드 네트워크 토폴로지로 CNN 학습 가속
- 최대 2.7배 학습 가속 달성 (기존 데이터 병렬 NDP 대비)

## 방법론

- 2차원 워커 조직: 그룹(데이터 병렬) × 클러스터(intra-tile 병렬)
- 타일 전송(Tile Transfer): Winograd 도메인 피처 맵의 gather/scatter 통신
- 동적 클러스터링: 레이어별 최적 토폴로지 재구성
- NDP 아키텍처: 3D 적층 메모리 고대역폭 활용

## 핵심 기여

- Winograd 변환의 새로운 병렬화 차원 (intra-tile parallelism)
- 메모리 중심 네트워크 + NDP 결합 아키텍처
- 예측 기반 비활성화로 타일 전송 대역폭 절감

## 주요 결과

- 데이터 병렬 NDP 대비 최대 2.7배 학습 가속
- 다중 GPU 시스템 대비 최대 2.1배 성능 향상
- Winograd 변환: 연산 2.8배 절감, 데이터 접근 4.4배 증가

## 한계점

- 타일 크기에 따른 수치적 불안정성 (large weight/tile size)
- 메모리 중심 네트워크의 물리적 구현 복잡성
- 고정된 배치 크기 가정 (128-256)

## 관련 concept 페이지

- [[paper-wiki/concepts/near-data-processing|Near-Data Processing]]
- [[paper-wiki/concepts/pim|Processing-in-Memory]]
