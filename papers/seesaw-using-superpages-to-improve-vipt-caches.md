---
tags: [cache, virtual-memory, superpage, vipt, l1-cache]
venue: ISCA
year: 2018
summary_path: paper-summaries/2018ISCA-summarize/seesaw-using-superpages-to-improve-vipt-caches.md
---

# SEESAW: Using Superpages to Improve VIPT Caches

## 개요

SEESAW는 superpage의 넓은 page offset을 활용하여 VIPT L1 캐시의 associativity 제약을 극복하는 기법입니다. 기존 VIPT 캐시는 4KB base page에서 최대 64 set만 사용 가능하여 높은 associativity에 의존하는데, SEESAW는 superpage 접근 시 더 많은 set index 비트를 활용하여 way 수를 동적으로 감소시킵니다.

## 방법론

- **Superpage-Enhanced Set Indexing**: 2MB/1GB superpage의 넓은 page offset을 캐시 set index로 활용
- **동적 Way 감소**: superpage 데이터 조회 시 적은 way만 활성화 → clock gating으로 나머지 way 비활성화
- **Coherence Lookup 최적화**: coherence 메시지도 superpage 여부에 따라 적은 way로 조회 가능
- **OS/앱 변경 불필요**: 기존 superpage 지원만 있으면 동작

## 핵심 기여

1. Superpage의 page offset을 VIPT 캐시 set index에 활용하는 최초의 접근법
2. superpage/base page/coherence 조회의 3가지 유형별 최적화
3. 상용 22nm SRAM 컴파일러로 latency, energy, area 실측 검증

## 주요 결과

- SRAM 측정: 2-way→8-way 시 latency 8.3% 증가, 에너지 3.76× 증가
- SPEC CPU2006: 2MB superpage 평균 MPKI 4.49 (2.04% 향상), 1GB는 4.35 (5.18% 향상)
- 구글 클라우드 워크로드: hit rate 평균 1.53~1.83% 향상
- Coherence energy 대폭 절감

## 한계점

- Superpage 할당이 필요한데, OS의 superpage 할당 정책에 의존
- 1GB superpage는 메모리 할당 문제로 실용성 제한
- Workload의 superpage 사용 비율에 따라 효과 편차 존재

## 관련 concept

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]
