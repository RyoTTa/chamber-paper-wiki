---
tags: [paper, compression, dnn, model-compression, permuted-diagonal, 2018]
venue: MICRO 2018
year: 2018
summary_path: paper-summaries/2018MICRO-summarize/permdnn-efficient-compressed-dnn-architecture-with-permuted-diagonal-matrices.md
---

# PERM DNN: Efficient Compressed DNN Architecture with Permuted Diagonal Matrices

## 개요

- 순열 대각 행렬(Permuted Diagonal Matrix) 기반 DNN 압축 및 추론 가속 아키텍처 제안
- 기존 EIE 대비 3.3~4.8배 처리량, CIRCNN 대비 11.51배 처리량 향상
- 프루닝 없는 구조화된 희소 모델 생성으로 재훈련 비용 제거

## 방법론

- 블록-순열 대각 행렬: 가중치 행렬을 k×k 블록으로 분할 후 대각선에 비영 항목 배치
- 단순 실수 연산 (FFT 불필요), 임의 크기의 압축률 지원
- 입력 희소성 완전 활용 (시간 영역 직접 처리)
- 다중 PE 구조의 FC 레이어 전용 추론 엔진

## 핵심 기여

- 순열 대각 행렬이라는 새로운 구조화된 희소 표현
- CIRCNN의 세 가지 한계점(복잡한 산술, 유연성 부족, 입력 희소성 미활용) 해결
- 재훈련 불필요한 엔드투엔드 학습 방식

## 주요 결과

- EIE 대비: 처리량 3.3~4.8배, 면적 효율 5.9~8.5배, 에너지 효율 2.8~4.0배
- CIRCNN 대비: 처리량 11.51배, 에너지 효율 3.89배
- 28nm CMOS 32-PE 설계: 703.4mW, 8.85mm², 614.4 GOPS

## 한계점

- FC 레이어에 특화 (CONV 레이어 미가속)
- 구조화된 희소성의 정확도 영향 (k 크기에 따라 변동)
- 동적 희소성 활용의 제한적 범위

## 관련 concept 페이지

- [[paper-wiki/concepts/compression|Compression]]
