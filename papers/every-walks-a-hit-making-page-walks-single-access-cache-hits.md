---
tags: [paper, 2022, 2022ASPLOS, topic/cache, topic/virtual-memory]
venue: ""
year: 2022
summary_path: "../paper-summaries/2022ASPLOS-summarize/every-walks-a-hit-making-page-walks-single-access-cache-hits.md"
---

# Every Walk's a Hit: Making Page Walks Single-Access Cache Hits

**Venue:** 
**저자:** Chang Hyun Park (Uppsala University), Ilias Vougioukas (Arm Research), Andreas Sandberg (Arm Research), David Black-Schaffer (Uppsala University)

## 개요

- 메모리 용량이 10년간 100× 성장했으나 TLB 크기는 3배 성장에 그쳐 L2 TLB 엔트리 약 1500개, 2MB large page 기준 3GB 커버리지에 불과
- 대용량 데이터 애플리케이션이 빈번한 TLB miss와 page walk 비용에 시달리며, 가상화 환경에서는 2D page walk로 인해 이론적 최대 24회 메모리 액세스 발생 (실제로 PWC와 large page로 4.4회로 감소)
- 기존 page table은 4KB 노드 기반 4-level 구조로 깊이가 깊어 serialized memory indirection 비용이 큼
- 5-level page table 도입 시 문제는 더욱 심화될 것으로 예측
- Page Walker Cache (PWC)는 이미 평균 접근 횟수를 1.5회로 줄여주지만, 최대 2.5회까지 발생 (가상화: 4.4회)

## 방법론

### 3.1. 메커니즘

- 2MB large page를 사용하여 두 레벨의 page table 노드를 하나로 병합 (L4+L3, L2+L1 각각 병합)
- 8GB 애플리케이션 기준: 기존 4106개의 4KB 페이지 → 9개의 2MB 페이지로 감소 (page table 깊이 4 → 2)
- 약 2MB 오버헤드 (18MB vs 8GB data) 발생하지나 전체 대비 무시 가능
- radix 구조의 page table tree 특성을 활용하여 기존 2MB page 지원을 그대로 활용

### 3.2. 가상화 환경에서의 Flattening

- 가상화 시 guest page table과 host page table 모두 평탄화 가능 (host만, guest만, 또는 둘 다)
- guest만 평탄화: 11MB guest page table의 indirection 감소로 4.4→2.8 접근 (평균)
- host만 평란화: 최종 데이터 주소 변환에만 효과 (Nested TLB + vPWC가 host 변환을 효율적으로 캐싱)
- 둘 다 평탄화: 최대 8회 이론적 접근 → PWC로 2.8회로 감소

### 3.3. 자기 참조 페이지 문제

- Flattened page table은 기존 recursive page table과 호환되지 않음
-高效的 역참조 솔루션을 제공하여 Linux 커널 프로토타입 구현

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1. 메커니즘

- 하드웨어 카운터를 이용하여 TLB miss율이 높은 구간 감지
- 높은 miss율 구간에서 교체 시 99% 확률로 data 대신 page table entry를 우선 유지
- 나머지 1%는 LRU 방식으로 교체 (co-runner에 대한 영향 최소화)
- 컨텍스트별 cache partitioning (MPAM 등)을 활용하여 프로세스 간 간섭 방지

### 4.2. 근거

- 높은 TLB miss율을 보이는 애플리케이션은 높은 data miss율도 동시에 보임 (L2 data miss 95%, L3 data miss 80%)
- 8GB 애플리케이션의 page table은 약 16MB → LLC에 완전히 캐싱 가능
- page table은 data보다 훨씬 작아 cache에서 차지하는 비중이 적으므로 data 대신 캐싱하는 것이 유리

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2022ASPLOS-summarize/every-walks-a-hit-making-page-walks-single-access-cache-hits.md|전체 요약 보기]]
