---
tags: [paper, 2018, 2018ASPLOS, topic/cache, topic/virtual-memory]
venue: "23rd International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '18)"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/latr-lazy-translation-coherence.md"
---

# LATR: Lazy Translation Coherence

**Venue:** 23rd International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '18)
**저자:** Mohan Kumar*, Steffen Maass*†, Sanidhya Kashyap†, Ján Veselý‡, Zi Yan‡, Taesoo Kim†, Abhishek Bhattacharjee‡, Tushar Krishna† (*Joint first authors, †Georgia Institute of Technology, ‡Rutgers University)

## 개요

- TLB(Translation Lookaside Buffer)는 가상 주소를 물리 주소로 빠르게 변환하는 코어별 캐시로, 애플리케이션 성능에 중요
- TLB 항목은 페이지 테이블 항목과 일관성을 유지해야 하지만, 하드웨어적 지원이 없어 소프트웨어적으로 제공해야 함
- 기존 시스템에서는 동기적 TLB shootdown 메커니즘을 사용하여 원격 코어의 stale TLB 항목을 무효화
- TLB shootdown은 비용이 비쌈: 120코어(8소켓)에서 최대 80µs, 16코어(2소켓)에서 6µs 소요
- IPI(Inter-Processor Interrupt)를 사용하여 shootdown 신호를 전달하는데, IPI 자체가 120코어에서 최대 6.6µs 소요
- Apache 웹 서버와 같은 메모리 관리 작업이 빈번한 애플리케이션의 성능 병목 현상 발생

## 방법론

### 3.1. Lazy TLB Coherence 메커니즘

- **Shootdown 큐**: 각 코어에 shootdown 요청을 저장하는 로컬 큐 관리
- **비동기 처리**: shootdown 요청을 즉시 처리하지 않고 다음에 적절한 시점에 처리
- **Software-managed TLB**: OS가 TLB 상태를 소프트웨어적으로 관리하여 하드웨어 제한 극복
- **Timestamp 기반 무효화**: 각 shootdown에 타임스탬프를 할당하여 최신성 보장

### 3.2. 구현 상세

- **Shootdown 큐 구조**: 고정 크기 큐로 shootdown 요청 저장
- **큐 전이 로직**: 
  1. shootdown 요청 발생 시 큐에 추가
  2. 큐가 가득 차면 현재 배치를 원격 코어로 전송
  3. 원격 코어는 idle 시점에 큐를 비우며 TLB 무효화 처리
- **동기화 메커니즘**: 배리어(barrier) 연산을 사용하여 필수적 동기화 지점에서 shootdown 처리 보장
- **메모리 모델**: TSX(Transactional Synchronization Extensions)와 통합하여 낙관적 실행 지원

### 3.3. 최적화 기법

- **Batching**: 여러 shootdown 요청을 배치 처리하여 오버헤드 감소
- **Selective Invalidation**: 실제로 변경된 페이지에 대해서만 무효화 수행
- **Priority Queue**: 중요도가 높은 shootdown을 우선 처리
- **Adaptive Batching**: 워크로드 특성에 따라 배치 크기 동적 조정

## 핵심 기여

- **핵심 기여**: TLB shootdown을 lazy하게 처리하는 새로운 메커니즘 제시
- **성능 향상**: Apache에서 59.9% 성능 향상, munmap()에서 70.8% 지연 시간 감소
- **의의**: 기존 동기적 TLB coherence의 비용 문제를 해결하여 멀티코어 시스템의 확장성 향상, 애플리케이션 레벨 변경 없이 시스템 전반의 성능 개선

---

## 참고 자료

- 원본 논문: paper-source/2018ASPLOS/LATR_Lazy_Translation_Coherence.pdf
- 요약 파일: paper-summaries/2018ASPLOS-summarize/latr-lazy-translation-coherence.md

## 주요 결과

- 구현 언어: C (커널 모듈)
- 코드 라인 수: 약 3,000줄
- 프레임워크: Linux 커널 4.14 기반
- 시스템 구성 요소:
  - Shootdown 큐 관리자
  - 무효화 처리기
  - 배리어 동기화 모듈
  - 통계 수집 모듈

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2018ASPLOS-summarize/latr-lazy-translation-coherence.md|전체 요약 보기]]
