---
tags: [paper, 2018, 2018HPCA, topic/gpu, topic/pim]
venue: "24th IEEE International Symposium on High Performance Computer Architecture (HPCA '18)"
year: 2018
summary_path: "../paper-summaries/2018HPCA-summarize/graphr-accelerating-graph-processing-using-reram.md"
---

# GraphR: Accelerating Graph Processing Using ReRAM

**Venue:** 24th IEEE International Symposium on High Performance Computer Architecture (HPCA '18)
**저자:** Linghao Song (Duke University), Youwei Zhuo (University of Southern California), Xuehai Qian (University of Southern California), Hai Li (Duke University), Yiran Chen (Duke University)

## 개요

- 그래프 처리: 소셜 네트워크, 사이버 보안, 추천 시스템, 자연어 처리 등 광범위한 응용
- 그래프 처리의 핵심 과제:
  - **불량한 locality**: 인접 정점 순회 시 랜덤 액세스
  - **높은 메모리 대역폭 요구**: 단순 연산 대비 데이터 이동이 많음
  - **캐시 블록 낭비**: 그래프 연산은 캐시 블록의 일부만 사용
- 기존 하드웨어 가속기:
  - **Graphicionado**: SPM에 최적화된 순차 액세스 + 파이프라인
  - **TESSERACT**: 근데이터 처리 (HMC 내부 대역폭 활용)
  - 공통 한계: 연산 유닛에서 단순 연산을 하나씩 수행 → 병렬화 부족
- 핵심 문제: **대규모 병렬 그래프 처리를 위한 에너지 효율적 하드웨어 가속기 부재**

## 방법론

### 3.1. ReRAM 크로스바 기반 SpMV
- **ReRAM 셀**: 전류 합산 (KVL)을 통한 곱셈-누적 연산 (아날로그)
- **희소 행렬 표현**: 인접 행렬을 ReRAM 크로스바에 저장
- **벡터-행렬 곱셈**: 
  - 입력 벡터를 크로스바의 행에 주입
  - 각 열의 전류 합산 → 출력 벡터 생성
  - 디지털-아날로그 변환 후 디지털 처리
- **병렬성**: 크로스바의 모든 행에서 동시에 연산 → O(1) 시간 복잡도

### 3.2. Graph Engine (GE) 설계
- **구성**: ReRAM 크로스바 + ADC (Analog-to-Digital Converter) + 디지털 로직
- **서브그래프 처리**: 큰 그래프를 작은 서브그래프로 분할
  - 각 서브그래프를 하나의 GE에서 처리
  - 여러 GE를 병렬로 활용하여 그래프 전체 처리
- **데이터 흐름**:
  1. 인접 행렬의 서브블록을 ReRAM에 로드
  2. 정점 값을 벡터로 입력
  3. 크로스바에서 SpMV 수행
  4. 출력 벡터를 메모리에 저장
  5. 다음 반복을 위해 새 서브블록 로드

### 3.3. 메모리 관리 및 데이터 배치
- **HMC (Hybrid Memory Cube)**: GE와 연결된 고대역폭 메모리
- **데이터 배치**: 인접 행렬의 서브블록을 GE의 ReRAM에 로드
- **전송 최소화**: GE 내부에서 최대한 많은 연산 수행 → 외부 메모리 트래픽 감소

### 3.4. 정확도 관리
- **오차 분석**: ReRAM의 아날로그 연산 오차가 그래프 알고리즘에 미치는 영향 최소
- **디지털 보정**: ADC 출력 후 디지털 보정 로직으로 오차 보정
- **반복적 알고리즘의 수렴성**: 충분한 반복 횟수로 오차 수렴 보장

## 핵심 기여

- **핵심 기여**: ReRAM의 아날로그 연산을 활용한 최초의 그래프 처리 가속기
- **성능**: CPU 대비 16× speedup, GPU 대비 2× speedup, PIM 대비 4× speedup
- **에너지 효율**: CPU 대비 34×, GPU 대비 9×, PIM 대비 11× 에너지 절약
- **실용성**: ReRAM 기술 성숙도에 따라 실현 가능성 달라지나, 아날로그 연접의 잠재력 입증
- **의의**: 차세대 비휘발성 메모리 기술과 근데이터 처리의 결합으로 그래프 처리의 에너지 효율성 혁신

## 주요 결과

- **평가 플랫폼**: ReRAM 크로스바 기반 시뮬레이터 + HMC 메모리 모델
- **그래프 알고리즘**: PageRank, BFS, SSSP, Collaborative Filtering
- **그래프 데이터셋**: Twitter, Wikipedia, Hollywood, RMAT 합성 그래프
- **기준선**: CPU, GPU, PIM 기반 가속기 (Graphicionado, TESSERACT)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2018HPCA-summarize/graphr-accelerating-graph-processing-using-reram.md|전체 요약 보기]]
