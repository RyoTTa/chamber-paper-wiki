---
tags: [paper, 2022, 2022HPCA, topic/cache, topic/dram, topic/nvm]
venue: "IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2022"
year: 2022
summary_path: "../paper-summaries/2022HPCA-summarize/multi-clock-dynamic-tiering-for-hybrid-memory-systems.md"
---

# MULTI-CLOCK: Dynamic Tiering for Hybrid Memory Systems

**Venue:** IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2022
**저자:** Adnan Maruf (Florida International University), Ashilree Ghosh (Florida International University), Janki Bhimani (Florida International University), Daniel Campello (Google), Andy Rudoff (Intel Corporation), Raju Rangaswami (Florida International University)

## 개요

- 메모리 컴퓨팅의 급속한 성장으로 서버에서 DRAM 수요가 폭발적으로 증가하고 있으나, DRAM 기반 시스템은 용량, 비용, 전력 소비 측면에서 현대 워크로드의 요구를 충족하지 못함
- 지속적 메모리(Persistent Memory, PM) 기술이 DRAM 대비 **4~29배 낮은 전력 소비**와 DRAM에 필적하는 레이턴시/대역폭을 제공하며, 하이브리드 메모리 시스템의 핵심 요소로 부상
- 정적 계층화(Static Tiering)는 페이지를 한 번 할당된 티어에 고정시켜, 시간이 지나며 중요도가 변하는 페이지를 적절히 재배치하지 못하는 근본적 한계 보유
- 하이브리드 메모리 시스템의 핵심 과제: **적절한 페이지를 적절한 티어에 적절한 시점에 배치**하면서 오버헤드를 최소화하는 것
- 기존 기법(Nimble, AutoTiering, Memory-mode)은 페이지 선택 메커니즘의 비효율성으로 인해 정적 계층화 대비 향상이 제한적이었음

## 방법론

### 3.1. 페이지 선택 메커니즘

- 기존 CLOCK 알고리즘은 접근 비트(refrence bit)만 활용하여 페이지의 최근성을 추정하지만, 접근 빈도를 고려하지 않음
- MULTI-CLOCK은 두 개의 독립적인 카운터/비트를 유지:
  - **최근성 비트(Recency Bit)**: 최근 접근 여부를 추적
  - **빈도 카운터(Frequency Counter)**: 접근 빈도를 누적하여 기록
- 페이지가 접근될 때마다 최근성 비트가 설정되고, 빈도 카운터가 증가
- 티어 결정 시 두 특성을 종합적으로 평가하여 DRAM 또는 PM에 배치

### 3.2. 동적 티어 배치

- **DRAM → PM 마이그레이션**: 빈도가 낮고 오래전에 접근된 페이지를 PM으로 이동하여 고성능 DRAM 공간을 확보
- **PM → DRAM 마이그레이션**: 높은 빈도로 접근되는 페이지를 DRAM으로 승격하여 성능 향상
- 마이그레이션 결정은 온라인 방식으로 워크로드에 적응적으로 수행
- NUMA 인식 구현: 멀티소켓 시스템에서 각 NUMA 노드의 메모리 티어를 독립적으로 관리

### 3.3. Linux 커널 구현

- Linux 버전 5.3.1 기반 구현
- 커널의 페이지 리클레임 알고리즘(kswapd)을 확장하여 동적 페이지 마이그레이션 로직 추가
- NUMA 인식: `mbind()`, `set_mempolicy()` 등 NUMA 정책과 호환
- 기존 애플리케이션과 완전히 호환되는 투명한 인터페이스 제공
- 사용자 공간 수정 불필요 — 시스템 수준에서 자동으로 최적 티어 배치 수행

## 핵심 기여

- **핵심 기여**: 접근의 최근성과 빈도를 동시에 고려하는 MULTI-CLOCK 페이지 선택 기법으로 하이브리드 메모리 시스템의 동적 계층화 문제를 효과적으로 해결
- **성능 향상**: 기존 최신 기법 대비 최대 352%, 정적 계층화 대비 132%의 처리량 향상
- **실용성**: Linux 커널 기반 투명한 구현으로 기존 애플리케이션과 완전 호환
- **의의**: 하이브리드 메모리 시스템에서 페이지 선택 메커니즘의 중요성을 강조하고, 간단하면서도 효과적인 해결책을 제시하여 실용적인 시스템 설계에 기여

## 주요 결과

- **구현 언어**: C (Linux 커널 모듈)
- **커널 버전**: Linux 5.3.1
- **시스템 구성요소**:
  - 페이지 접근 비트 모니터링 모듈
  - 빈도 카운터 관리 모듈
  - 티어 간 페이지 마이그레이션 엔진
  - NUMA-aware 정책 관리자
- **하드웨어 요구사항**: Intel Optane DC Persistent Memory (또는 유사 PM 장치) + DRAM으로 구성된 하이브리드 메모리 시스템

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]


## 전체 요약

[[../paper-summaries/2022HPCA-summarize/multi-clock-dynamic-tiering-for-hybrid-memory-systems.md|전체 요약 보기]]
