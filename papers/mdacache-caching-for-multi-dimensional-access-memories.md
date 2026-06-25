---
tags: [paper, 2018, 2018MICRO, topic/cache, topic/memory, topic/compiler]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO), 2018"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/mdacache-caching-for-multi-dimensional-access-memories.md"
---

# MDACache: Caching for Multi-Dimensional-Access Memories

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Sumitha George, Minli Julie Liao, Huaipan Jiang, Jagadish B. Kotra, Mahmut T. Kandemir, Jack Sampson, Vijaykrishnan Narayanan (Pennsylvania State University, AMD Research)

## 개요

- 기존 DRAM/SRAM은 행 중심 접근 방식을 사용하여 1차원 선형화된 메모리 모델을 기반으로 함
- 신흥 메모리 기술(ReRAM, PCRAM 등)의 cross-point 배열은 행과 열 양방향에서 거의 대칭적인 접근 비용을 제공하는 MDA(Multi-Dimensional-Access) 메모리 가능
- MDACache는 MDA 메모리를 위한 캐시 계층 설계 및 최적화를 제안

## 방법론

### 3.1. MDA 메모리 기반 Taxonomy

- 응용 수준 선호도: 행 선호, 열 선호, 혼합 선호
- 캐시 계층 연결 방식: 1D 캐시 + MDA 메모리, 논리적 2D 캐시, 물리적 2D 캐시

### 3.2. 컴파일러 수준 벡터화 지원

- 컴파일러가 행/열 선호도를 추출하여 캐시에 전달
- 메모리 레이아웃을 MDA 메모리에 호환하도록 변환

### 3.3. 캐시 설계 옵션

- **논리적 2D 캐싱:** 물리적 1D SRAM을 사용하여 논리적으로 2D 캐싱 구현 (실행 시간 **72%** 감소)
- **물리적 2D 캐시:** 온칩에 물리적으로 2D 캐시 구조 구현 (실행 시간 **65%** 감소)

## 핵심 기여

- **핵심 기여:** MDA 메모리를 위한 캐시 계층 설계 taxonomies 및 구체적 구현 제시
- **성능 향상:** 전통적 캐시 시스템 대비 최대 **72%** 실행 시간 감소

## 주요 결과

- 논리적 2D 캐싱: 전통적 캐시 시스템 대비 실행 시간 **72%** 감소
- 물리적 2D 캐시: 전통적 캐시 시스템 대비 실행 시간 **65%** 감소
- 워킹 세트/캐시 용량 비율에 따른 민감도 분석 수행
- MDA 기술 가정에 따른 성능 변화 확인

## 한계점

- 물리적 2D 캐시의 면적/전력 오버헤드 존재
- 다양한 MDA 메모리 기술 및 실제 응용에서의 확장성 검증 필요
- 컴파일러 수준 벡터화 지원의 일반화 필요

## 관련 개념

- [[paper-wiki/concepts/caching|Caching]]
- [[paper-wiki/concepts/multi-dimensional-memory|Multi-Dimensional Memory]]
- [[paper-wiki/concepts/compiler-optimization|Compiler Optimization]]

## 관련 논문

- [mdacache-caching-for-multi-dimensional-access-memories.md](../paper-summaries/2018MICRO-summarize/mdacache-caching-for-multi-dimensional-access-memories.md)
