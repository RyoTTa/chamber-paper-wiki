---
tags: [paper, 2018, 2018HPCA, topic/dram]
venue: "IEEE International Symposium on High Performance Computer Architecture (HPCA) 2018"
year: 2018
summary_path: "../paper-summaries/2018HPCA-summarize/reliability-aware-data-placement-for-heterogeneous-memory-architecture.md"
---

# Reliability-Aware Data Placement for Heterogeneous Memory Architecture

**Venue:** IEEE International Symposium on High Performance Computer Architecture (HPCA) 2018
**저자:** Manish Gupta (UCSD), Vilas Sridharan (AMD), David Roberts (AMD), Andreas Prodromou (UCSD), Ashish Venkat (UCSD), Dean Tullsen (UCSD), Rajesh Gupta (UCSD)

## 개요

- 기존 단일 유형 메모리 시스템은 비용과 성능 간의 트레이드오프에 직면
- Heterogeneous Memory Architecture (HMA)는 die-stacked 메모리(높은 대역폭, 낮은 용량)와 DDRx 메모리(높은 용량, 낮은 대역폭)를 결합하여 해결
- 메모리 계층 간 데이터 배치가 시스템 신뢰성(reliability)과 성능에 큰 영향
- 기존 데이터 배치 전략은 주로 성능(performance) 또는 에너지(energy)에 초점, 신뢰성 고려 부족
- Architectural Vulnerability Factor (AVF)를 활용한 신뢰성-aware 데이터 배치 필요

## 방법론

### 3.1. Static Placement

- 프로그램 실행 전에 페이지의 hotness와 risk를 사전 분석하여 배치 결정
- 컴파일 타임 또는 프로파일링을 통해 페이지 특성 파악
- **1.6배 신뢰성 향상**, 성능 손실 1% 달성 (Figure 4)

### 3.2. Dynamic Placement

- 실행 시간에 페이지의 hotness와 risk를 동적으로 모니터링하여 마이그레이션
- OS 또는 하드웨어 트래커를 활용한 실시간 접근 패턴 분석
- **1.5배 신뢰성 향상**, 성능 손실 4.9% 달성 (Figure 5)

### 3.3. Program Annotation-Based Placement

- 프로그래머가 프로그램에 신뢰성 관련 어노테이션을 추가하여 배치 힌트 제공
- 컴파일러가 어노테이션을 해석하여 최적 배치 결정
- **1.3배 신뢰성 향상**, 성능 손실 1.1% 달성 (Figure 6)

## 핵심 기여

- HMA에서 신뢰성-aware 데이터 배치가 시스템 전체 신뢰성을 크게 향상시킬 수 있음
- Hotness-risk quadrant 분석을 통한 체계적인 페이지 분류 방법론 제시
- 세 가지 배치 기법各不同的性能-신뢰성 트레이드오프 제공
- 기존 메모리 관리 기법과의 호환성으로 실용적 적용 가능성 확보
- 향후 복합 메모리 시스템에서 신뢰성을 고려한 데이터 관리 연구 기반 마련

## 주요 결과

- HMA 시스템 모델: die-stacked 메모리(예: HBM) + DDRx 메모리 구성
- AVF 분석을 위한 하드웨어 카운터 및 소프트웨어 프로파일링 도구
- OS 레벨 페이지 테이블 관리 및 메모리 배치 로직
- 마이그레이션 오버헤드 최소화를 위한 비용-편익 분석 알고리즘

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2018HPCA-summarize/reliability-aware-data-placement-for-heterogeneous-memory-architecture.md|전체 요약 보기]]
