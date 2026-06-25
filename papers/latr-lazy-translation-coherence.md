---
tags: [paper, 2018, 2018ASPLOS, topic/virtual-memory, topic/tlb]
venue: "ASPLOS 2018"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/latr-lazy-translation-coherence.md"
---

# LATR: Lazy Translation Coherence

**Venue:** ASPLOS 2018
**저자:** Mohan Kumar*, Steffen Maass*†, Sanidhya Kashyap†, Ján Veselý‡, Zi Yan‡, Taesoo Kim†, Abhishek Bhattacharjee‡, Tushar Krishna† (*Joint first authors, †Georgia Institute of Technology, ‡Rutgers University)

## 개요

TLB shootdown은 멀티코어 시스템에서 비용이 비싸며, 기존 동기적 메커니즘은 IPI를 사용하여 원격 코어에 shootdown 신호를 전달. Apache 웹 서버와 같은 메모리 관리 작업이 빈번한 애플리케이션의 성능 병목 현상 발생.

LATR은 TLB shootdown을 lazy하게 처리하는 새로운 메커니즘을 제시하여 IPI 없이 비동기적으로 TLB 무효화를 처리. Apache에서 59.9% 성능 향상, munmap()에서 70.8% 지연 시간 감소.

## 방법론

### Lazy TLB Coherence 메커니즘
- Shootdown 큐: 각 코어에 shootdown 요청을 저장하는 로컬 큐 관리
- 비동기 처리: shootdown 요청을 즉시 처리하지 않고 다음에 적절한 시점에 처리
- Software-managed TLB: OS가 TLB 상태를 소프트웨어적으로 관리

### 구현 상세
- Shootdown 큐 구조: 고정 크기 큐로 shootdown 요청 저장
- 배치 처리: 여러 shootdown 요청을 배치 처리하여 오버헤드 감소
- 동기화 메커니즘: 배리어(barrier) 연산을 사용하여 필수적 동기화 지점에서 shootdown 처리 보장

## 핵심 기여

1. TLB shootdown을 lazy하게 처리하는 새로운 메커니즘 제시
2. IPI 없는 비동기적 TLB coherence 달성
3. 애플리케이션 레벨 변경 없이 시스템 전반의 성능 개선

## 주요 결과

- Apache 성능 향상: Linux 대비 59.9% 향상, ABIS 대비 37.9% 향상
- munmap() 지연 시간: 70.8% 감소 (2-소켓 머신)
- TLB shootdown 처리량: 46.3% 증가
- Memcached 성능: Linux 대비 32.4% 향상

## 한계점

- 소프트웨어 관리 오버헤드로 인한 추가 CPU 사용
- 복잡한 동기화 시나리오에서의 잠재적 일관성 문제
- 특정 워크로드에서의 성능 저하 가능성

## 관련 개념

- [[paper-wiki/concepts/tlb|TLB]]
- [[paper-wiki/concepts/virtual-memory|Virtual Memory]]
- [[paper-wiki/concepts/multicore|Multicore]]

## 관련 논문

- [LATR 논문 요약](../paper-summaries/2018ASPLOS-summarize/latr-lazy-translation-coherence.md)