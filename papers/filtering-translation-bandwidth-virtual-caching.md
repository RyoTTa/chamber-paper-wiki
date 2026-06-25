---
tags: [gpu, virtual-memory, caching, tlb, address-translation]
venue: ASPLOS
year: 2018
summary_path: paper-summaries/2018ASPLOS-summarize/filtering-translation-bandwidth-with-virtual-caching.md
---

# Filtering Translation Bandwidth with Virtual Caching

## 개요

GPU에서의 가상 캐시 계층을 제안하여 주소 번역 대역폭을 효과적으로 필터링합니다. 소프트웨어 수정 없이 기존 GPU 프로그램과 호환되면서도 이상적인 MMU에 근접하는 성능을 달성합니다.

## 방법론

- **GPU 가상 캐시 계층:** 전체 GPU 캐시 계층 (L1 및 L2)을 가상 캐시로 구성
- **주소 번역 대역폭 필터링 메커니즘:** 프라이빗 TLB miss 발생 시 가상 캐시에서 먼저 확인
- **동의어(Synonym) 문제 해결:** GPU의 가속기 특화 속성을 활용한 태그 기반 동의어 검출

## 핵심 기여

1. GPU에서의 가상 캐시 계층을 통한 주소 번역 대역폭 필터링 기법 제안
2. 소프트웨어 수정 없이 기존 GPU 프로그램과의 호환성 확보
3. 이상적인 MMU에 근접하는 성능 달성

## 주요 결과

- 가상 캐시 계층 적용 시 이상적인 MMU 대비 평균 98% 성능 달성
- L1 가상 캐시만 사용한 경우: 이상적인 MMU 대비 평균 85% 성능
- 전체 가상 캐시 계층 사용 시 L1 가상 캐시 대비 평균 1.31배 성능 향상
- 주소 번역 대역폭 사용량 평균 60% 감소

## 한계점

- gem5 시뮬레이터 기반 평가로 실제 GPU 하드웨어와의 차이 존재
- 특정 GPU 워크로드에 최적화된 설계
- 범용 GPU 애플리케이션에서의 성능 검증 필요

## 관련 concept 페이지

- [[paper-wiki/concepts/gpu|GPU Architecture]]
- [[paper-wiki/concepts/virtual-memory|Virtual Memory]]
- [[paper-wiki/concepts/caching|Caching]]

## 관련 논문 요약

- [filtering-translation-bandwidth-with-virtual-caching.md](paper-summaries/2018ASPLOS-summarize/filtering-translation-bandwidth-with-virtual-caching.md)