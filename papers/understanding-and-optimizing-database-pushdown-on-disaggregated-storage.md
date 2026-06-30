---
tags: [paper, database, pushdown, disaggregation, storage, optimization]
venue: ASPLOS
year: 2026
summary_path: paper-summaries/2026ASPLOS-summarize/understanding-and-optimizing-database-pushdown-on-disaggregated-storage.md
---

# Understanding and Optimizing Database Pushdown on Disaggregated Storage

## 개요

TapDB는 스토리지 분리 환경을 위해 설계된 새로운 푸시다운 데이터베이스 시스템입니다. 기존 정책 기반 푸시다운 설계가 하드웨어 트렌드 변화로 인해 비효율적이 된 문제를 해결합니다.

## 방법론

- **테이블 인식 연산자 비용 추정기**: 인시추 메타러닝 및 카디널리티 추정 기반
- **인가 제어 스킴**: 동적 비용 조정으로 간섭 없는 윈도우 유지
- **DRAM-SSD 하이브리드 테이블**: 메모리 블로잉 기반 메모리 용량 확장
- **임계 경로 기반 연산자 스케줄러**: 실행 긴급도에 따른 자원 할당

## 핵심 기여

- 스토리지 분리 환경에서의 푸시다운 비용 균형 변화 식별
- 세 가지 근본 원인 발견: 테이블 구조 간과, 낮은 간섭 허용, 스케줄러 부족
- Lazy evaluation과 network/I/O를 계산과 교환하는 접근법

## 주요 결과

- SSB 및 TPCH 벤치마크에서 기존 솔루션 대비 1.3–2.3배 가속
- 다양한 데이터 스케일에서 일관된 성능 향상
- 4세대 분리 스토리지 노드에서의 일반화 가능성 입증

## 한계점

- 특정 데이터베이스 워크로드에 최적화
- 스토리지 노드의 CPU 자원 제한에 대한 잠재적 병목
- 복잡한 쿼리에서의 오버헤드 가능성

## 관련 개념

- [[paper-wiki/concepts/database-systems|Database Systems]]
- [[paper-wiki/concepts/storage-disaggregation|Storage Disaggregation]]
- [[paper-wiki/concepts/query-optimization|Query Optimization]]

## 관련 논문

- [FPDB](paper-summaries/2024ATC-summarize/fpdb-a-fast-and-programmable-database-system.md)
- [Cloud-native databases](paper-summaries/2024OSDI-summarize/cloud-native-database-systems.md)