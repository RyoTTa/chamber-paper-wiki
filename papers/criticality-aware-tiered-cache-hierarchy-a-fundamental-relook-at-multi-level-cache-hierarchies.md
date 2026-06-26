---
tags: [paper, 2018, 2018ISCA, topic/cache]
venue: "45th Annual International Symposium on Computer Architecture (ISCA '18)"
year: 2018
summary_path: "../paper-summaries/2018ISCA-summarize/criticality-aware-tiered-cache-hierarchy-a-fundamental-relook-at-multi-level-cache-hierarchies.md"
---

# Criticality Aware Tiered Cache Hierarchy: A Fundamental Relook at Multi-level Cache Hierarchies

**Venue:** 45th Annual International Symposium on Computer Architecture (ISCA '18)
**저자:** Anant Vithal Nori, Jayesh Gaur, Siddharth Rai, Sreenivas Subramoney, Hong Wang (Intel Microarchitecture Research Lab, IIT Kanpur)

## 개요

- 온다이 캐시는 메인 메모리 지연 시간을 숨기는 인기 있는 방법이지만, 큰 캐시를 빠르게 구축하기 어려움
- 현대 마이크로프로세서의 일반적인 3레벨 캐시 계층 구조:
  - L1 (작고 빠름, 코어 프라이빗) → L2 (큰 프라이빗) → LLC (큰 공유)
  - 대부분의 요청이 빠른 내부 레벨(L1, L2)에서 서비스되어 평균 히트 지연 시간이 낮음
- **최근 트렌드**: 평균 히트 지연 시간을 줄이기 위해 **L2 캐시를 점점 크게** 설계 (1MB 이상)
- **근본적 비효율**: 현재 캐시 계층은 **모든 로드 접근의 평균 히트 지연 시간**을 최적화하지만, **프로그램 성능에 영향을 미치는 것은 critical load만** 존재
  - Critical path 위의 load만이 성능에 영향 → 비critical load는 높은 지연 시간으로도 무방
- 핵심 문제: 큰 L2 캐시가 대부분의 애플리케이션에서 면적 대비 성능 향상 효과가 미미하며, 면적을 더 효율적으로 활용할 수 있는 방안 부재

## 방법론

### 3.1. Criticality 감지 메커니즘

- **데이터 의존성 그래프(Data Dependency Graph)**: Fields et al.의 초기 연구를 기반으로 최적화된 하드웨어 표현
  - **3KB 면적**으로 critical path 학습
  - 점진적(incremental) 학습 방법 → 런타임에 동적으로 critical path 감지
- **Critical load 지시자**: 하드웨어에서 정확하게 critical load 명령어를 식별
  -Critical load PC(Program Counter) 목록을 유지
  - Critical path 위의 load만을 프리패칭 대상으로 선정

### 3.2. TACT 프리패처 (Timeliness Aware and Criticality Triggered)

- **Critical load에 대한 인터-캐시 프리패처**:
  - LLC 또는 L2에서 L1로 데이터를 프리패칭
  - Critical load가 실제로 발행되기 직전에 데이터를 L1에 준비
- **프리패칭 기반**:
  - 대상 critical load 근처의 load 명령어 주소 또는 데이터의 연관성(association) 활용
  - 주소 기반 프리패칭: 이전 프리패치된 주소 패턴 기반
  - 데이터 기반 프리패칭: 데이터 값의 연관성 활용
- **코드 런어헤드 프리패처**: 코드 L1 미스로 인한 코드 스타그네이션 제거
  - 코드 접근도 critical path 위에 있을 수 있으므로 프리패칭

### 3.3. CATCH 기반 캐시 계층 구성

- **L2 제거 option**: CATCH가 critical load를 L1으로 서비스하므로 L2가 불필요
  - 면적 절감 → LLC 용량 증가 또는 코어 수 증가에 활용
- **유연한 구성 탐색 프레임워크**:
  - 칩 전체 면적, 성능, 전력 간 트레이드오프 탐색 가능
  - 급진적 방향 (L2 완전 제거) 부터 점진적 최적화까지

## 핵심 기여

- **핵심 기여**: 프로그램 criticality를 활용한 캐시 계층 설계의 근본적 재검토
- **발견**: 기존의 L2 캐시 확대 트렌드가 실제로는 비효율적인 설계 선택
- **성능**: CATCH로 8.4~10.3% IPC 향상, L2 제거 시 30% 면적 절감 + 4.5% 성능 향상
- **의의**: Criticality-aware 설계가 캐시 계층의 면적-성능-전력 트레이드오프를 근본적으로 개선할 수 있음을 입증 → 향후 프로세서 설계에서 criticality가 핵심 고려 사항이 되어야 함

## 주요 결과

- **하드웨어 오버헤드**: Critical path 학습에 3KB 면적만 필요
- **프리패처**: TACT 프리패처가 기존 캐시 하드웨어에 추가되는 구조
- **적용 대상**: Skylake 유사 프로세서의 3레벨 캐시 계층

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]


## 전체 요약

[[../paper-summaries/2018ISCA-summarize/criticality-aware-tiered-cache-hierarchy-a-fundamental-relook-at-multi-level-cache-hierarchies.md|전체 요약 보기]]
