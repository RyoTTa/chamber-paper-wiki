---
tags: [paper, 2018, 2018MICRO, topic/cache, topic/dram]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/mdacache-caching-for-multi-dimensional-access-memories.md"
---

# MDACache: Caching for Multi-Dimensional-Access Memories

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Sumitha George, Minli Julie Liao, Huaipan Jiang, Jagadish B. Kotra, Mahmut T. Kandemir, Jack Sampson, Vijaykrishnan Narayanan (Pennsylvania State University, AMD Research)

## 개요

- 기존 DRAM/SRAM은 행 중심(row-oriented) 접근 방식을 사용하여 1차원 선형화된 메모리 모델을 기반으로 함
- 그러나 많은 알고리즘(행렬 곱셈, 비전 처리, 데이터베이스 쿼리 등)은 본질적으로 다차원 데이터 구조와 접근 패턴을 가짐
- 신흥 메모리 기술(ReRAM, PCRAM 등)의 cross-point 배열은 행과 열 양방향에서 거의 대칭적인 접근 비용을 제공하는 MDA(Multi-Dimensional-Access) 메모리 가능
- 기존 프로세서는 메모리의 행이나 열에 직접 접근하지 않고 캐시 계층을 통해 접근하므로, MDA 메모리의 이점을 완전히 활용하지 못함
- 소프트웨어 메모리 레이아웃, 물리적/논리적 메모리 조직 간 매핑, 캐시 계층 간 co-design이 필요

## 방법론

### 3.1. MDA 메모리 기반 Taxonomy

- **응용 수준 선호도:**
  - 행 선호(row preference): 행 기반 데이터 접근 선호
  - 열 선호(column preference): 열 기반 데이터 접근 선호
  - 혼합 선호(mixed preference): 행과 열 모두 사용
- **캐시 계층 연결 방식:**
  - 1D 캐시 + MDA 메모리: 기존 1D 캐시를 MDA 메모리와 연결
  - 논리적 2D 캐시: 물리적 1D SRAM을 사용하여 논리적으로 2D 캐싱 구현
  - 물리적 2D 캐시: 온칩에 물리적으로 2D 캐시 구조 구현

### 3.2. 컴파일러 수준 벡터화 지원

- 컴파일러가 행/열 선호도를 추출하여 캐시에 전달
- 메모리 레이아웃을 MDA 메모리에 호환하도록 변환
- 벡터화된 접근 패턴을 통해 다차원 접근 효율성 향상
- 기존 벡터화 기술을 확장하여 MDA 메모리 지원

### 3.3. 캐시 설계 옵션

#### 3.3.1. 논리적 2D 캐싱 (물리적 1D SRAM 사용)
- 물리적으로는 기존 1D SRAM 캐시를 사용
- 논리적으로 2D 캐싱 메커니즘 구현
- 행과 열 양방향 접근 지원
- 실행 시간 **72%** 감소 달성

#### 3.3.2. 물리적 2D 캐시
- 온칩에 물리적으로 2D 캐시 구조 구현
- 행과 열에 대한 물리적 접근 경로 제공
- 더 높은 접근 병렬성 및 낮은 레이턴시
- 실행 시간 **65%** 감소 달성

## 핵심 기여

- **핵심 기여:** MDA 메모리를 위한 캐시 계층 설계 taxonomies 및 구체적 구현 제시
- **성능 향상:** 전통적 캐시 시스템 대비 최대 **72%** 실행 시간 감소
- **의의:** 신흥 메모리 기술의 다차원 접근 특성을 활용하기 위한 캐시 설계 지침 제공
- **향후 과제:** 다양한 MDA 메모리 기술 및 실제 응용에서의 확장성 검증 필요

## 주요 결과

- 구현 언어: 컴파일러 확장 및 시뮬레이션
- 프레임워크: LLVM 컴파일러 프레임워크 기반 확장
- 시스템 구성 요소:
  - MDA 메모리 배열 (cross-point 구조)
  - 캐시 계층 (논리적 2D 또는 물리적 2D)
  - 컴파일러 벡터화 모듈
  - 메모리 레이아웃 변환 로직

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/mdacache-caching-for-multi-dimensional-access-memories.md|전체 요약 보기]]
