---
tags: [paper, 2019, 2019HPCA, topic/cache, topic/dram, topic/nvm, topic/virtual-memory]
venue: "2019 IEEE International Symposium on High-Performance Computer Architecture (HPCA '19)"
year: 2019
summary_path: "../paper-summaries/2019HPCA-summarize/pageseer-using-page-walks-to-trigger-page-swaps-in-hybrid-memory-systems.md"
---

# PageSeer: Using Page Walks to Trigger Page Swaps in Hybrid Memory Systems

**Venue:** 2019 IEEE International Symposium on High-Performance Computer Architecture (HPCA '19)
**저자:** Apostolos Kokolis (University of Illinois at Urbana-Champaign), Dimitrios Skarlatos (University of Illinois at Urbana-Champaign), Josep Torrellas (University of Illinois at Urbana-Champaign)

## 개요

- 데이터 집약적 애플리케이션이 대용량 메모리, 고대역폭, 저전력을 요구하며, DRAM은 공정 스케일링 문제로 인해 확장성에 한계
- NVM(Non-Volatile Memory) 기술(PCM, STT-RAM 등)은 높은 용량과 저렴한 비용을 제공하지만, DRAM 대비 읽기/쓰기 지연 시간이 높고 에너지 소비가 큼
- 하이브리드 메모리 시스템(DRAM + NVM)이 유망한 해결책이나, **데이터 세그먼트를 두 메모리 간에 동적으로 교환(swap)하는 최적 시점과 대상을 결정하는 것이 핵심 과제**
- 기존 하드웨어 관리 swap 기술의 문제:
  - **지나치게 공격적인 접근**: 첫 접근 시 즉시 DRAM으로 이동하면 불필요한 트래픽 발생
  - **지나치게 보수적인 접근**: 많은 접근 이력 축적 후 이동하면 너무 늦게 반응하여 성능 향상 미미
- 최적의 swap을 위해서는 **정확성(accuracy)**과 **충분한 리드 타임(lead time)**이 동시에 필요

## 방법론

### 3.1. MMU-Triggered Prefetch Swaps

- **동작 원리**: TLB miss가 발생하여 page walk가 수행될 때, MMU가 메모리 컨트롤러에 해당 페이지의 물리 주소 생성을 알림
- 메모리 컨트롤러는 두 가지 정보를 기반으로 swap 결정:
  - **대상 페이지(page P)**: 현재 page walk가 생성하는 물리 주소의 페이지
  - **후속 참조 페이지(follower page F)**: 페이지 P 후에 참조될 가능성이 높은 페이지
- **판단 기준**: 페이지 P와 F의 과거 접근 이력(access history)을 분석하여 swap 유무 결정
- 페이지 P가 NVM에 있고 자주 접근되면 DRAM으로 prefetch swap 수행
- follower page F도 동일한 로직으로 사전 swap하여未来的 접근 시 DRAM에서 서비스

### 3.2. 추가 Swap 유형

- **Demand Swaps**: 실제 접근 시 발생하는 swap (기존 메커니즘과 유사)
- **Speculative Swaps**: 접근 패턴 분석에 기반한 예측적 swap
- PageSeer는 MMU-Triggered Prefetch Swaps 외에도 다양한 swap 유형을 통합하여 완전한 솔루션 구현

### 3.3. 접근 이력 관리

- 페이지 단위의 접근 이력 히스토리를 메모리 컨트롤러에 저장
- 각 페이지에 대해 최근 접근 빈도, 접근 간격 패턴 등을 추적
- 후속 참조 페이지(follower) 관계를 학습하여 연관성 높은 페이지 쌍을 식별

## 핵심 기여

- **핵심 Contribution**: page walk에서의 힌트를 활용한 MMU-Triggered Prefetch Swaps를 통해 하이브리드 메모리의 segment swap을 효과적으로 관리하는 최초의 하드웨어 메커니즘 제안
- **성능 향상**: 기존 최첨단 하드웨어 전용 방식 대비 평균 19% 성능 향상, 29% AMAT 감소
- **실용성**: 소프트웨어에 완전히 투명하며, 기존 하드웨어 아키텍처에 통합 가능한 구조
- **의의**: 하이브리드 메모리 시스템에서 DRAM과 NVM의 장점을 효과적으로 결합하는 실용적인 하드웨어 관리 방식을 제시

## 주요 결과

- **평가 방법**: 26개 워크로드에 대한 시뮬레이션 기반 평가
- **하드웨어 구성 요소**: MMU 내 페이지 walk 알림 메커니즘, 메모리 컨트롤러 내 접근 이력 관리 구조, swap 제어 로직
- **소프트웨어 투명성**: 운영체제나 애플리케이션 수정 없이 하드웨어만으로 구현
- 기존 최첨단 하드웨어 전용 방식(hardware-only scheme)과 비교 평가

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2019HPCA-summarize/pageseer-using-page-walks-to-trigger-page-swaps-in-hybrid-memory-systems.md|전체 요약 보기]]
