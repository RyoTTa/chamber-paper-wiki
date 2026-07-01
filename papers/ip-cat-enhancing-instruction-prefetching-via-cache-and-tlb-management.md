---
tags: [paper, 2026, 2026ARXIV, topic/cache, topic/tlb, topic/prefetching]
venue: arXiv
year: 2026
summary_path: paper-summaries/2026ARXIV-summarize/enhancing-instruction-prefetching-via-cache-and-tlb-management.md
---

# IP-CaT: Enhancing Instruction Prefetching via Cache and TLB Management

## 개요

L1I 프리페칭의 이점을 최대화하기 위해 TLB와 캐시 관리를 공동 조율하는 마이크로아키텍처 스킴. tPB(Translation Prefetch Buffer)로 주소 변환 지연을 줄이고, TIPRP(Trimodal Instruction Prefetch Replacement Policy)로 L2 캐시 내 프리페치된 코드 라인을 효율적으로 관리.

## 방법론

- **tPB (Translation Prefetch Buffer)**: sTLB 옆에 위치하는 64 엔트리 완전 연관 버퍼
  - L1I 페이지 교차 프리페치가 가져온 PTE를 저장
  - demand sTLB 미스를 서비스하여 페이지ウォー크 수 대폭 감소
  - sTLB 폴루션 없이 주소 변환 비용 절감
- **TIPRP (Trimodal Instruction Prefetch Replacement Policy)**:决策 트리 기반 L2 캐시 교체 정책
  - NPIP, BIP, PIP 세 가지 보완적 정책을 동적 선택
  - 프로그램 단계에 따라 가장 적합한 정책 자동 선택
  - 캐시 히트와 evictions 모두에서 카운터 업데이트로 빠른 적응

## 핵심 기여

- L1I 프리페칭의 두 가지 핵심 제약(주소 변환 지연, 가변적 재사용 행동)을 동시 해결
- 0.79KB의 매우 작은 저장 오버헤드로 유의미한 성능 향상
- 소프트웨어 변경 불필요한 마이크로아키텍처 솔루션

## 주요 결과

- **단일 코어**: EPI+IP-CaT **6.1%**, Barça+IP-CaT **8.3%**, FNL+MMA+IP-CaT **7.9%** geomean 스피드업
- **sTLB MPKI 감소**: EPI 31.6%, FNL+MMA 18.2%, Barça 32.3%
- **다중 코어**: 160개 워크로드 믹스에서 모든 경쟁 정책 능가 (Mockingjay 대비 14.2% 스피드업)
- **SMT**: 단일 코어보다 더 큰 절대 스피드업
- 모든 L1I 프리페처 유형과 105개 서버 워크로드에서 일관된 성능 향상

## 한계점

- LLC 크기가 4MB로 증가하면 스피드업 2.6%로 감소 (그러나 여전히 유의미)
- 2MB 페이지 비중이 100%일 때 tPB 효과 미미 (페이지 교차 프리페치 자체가 감소)
- TIPRP를 demand 접근에 적용하면 성능 10.1% 감소 (프리페치/demand 분리 관리 필요)

## 관련 Concepts

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]

## 관련 논문

- [paper-summaries/2026ARXIV-summarize/enhancing-instruction-prefetching-via-cache-and-tlb-management.md]
