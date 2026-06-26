---
tags: [paper, 2018, 2018HPCA, topic/dram, topic/nvm]
venue: "HPCA '18 (IEEE International Symposium on High Performance Computer Architecture), 2018"
year: 2018
summary_path: "../paper-summaries/2018HPCA-summarize/profess-a-probabilistic-hybrid-main-memory-management-framework-for-high-performance-and-fairness.md"
---

# ProFess: A Probabilistic Hybrid Main Memory Management Framework for High Performance and Fairness

**Venue:** HPCA '18 (IEEE International Symposium on High Performance Computer Architecture), 2018
**저자:** Dmitry Knyaginin (Chalmers University of Technology), Vassilis Papaefstathiou (FORTH-ICS), Per Stenstrom (Chalmers University of Technology)

## 개요

- NVM(Non-Volatile Memory) 기술은 DRAM보다 높은 비트 밀도와 낮은 비트당 비용을 제공하여 비용 효율적인 하이브리드 메인 메모리 구현 가능
- 하이브리드 메모리의 두 파티션: M1(DRAM)과 M2(NVM) - M2는 더 느리지만 더 큰 용량
- 플랫 마이그레이팅(topology) 구조에서 프로세서가 M1과 M2에 직접 접근 가능
- 공정 프로그램들이 제한된 공유 자원인 M1을 두고 경쟁하는 문제
- 프로그램이 M1에 대한 경쟁으로 인해 상대적으로 느려지는 정도를 측정하는 공정한 관리의 필요성
- 고성능과 공정성을 동시에 달성하기 위한 메모리 관리 프레임워크의 부재

## 방법론

### 3.1. Relative-Slowdown Monitor (RSM)
- 각 프로그램의 상대적 느려짐 정도를 모니터링
- M1에 대한 경쟁으로 인해 가장 크게 손해를 보는 프로그램을 식별
- 공정한 메모리 할당 결정을 위한 지표 제공

### 3.2. 확률론적 Migration-Decision Mechanism (MDM)
- 데이터 블록의 마이그레이션에 대한 비용-편익 분석을 개별적으로 수행
- 확률론적 접근을 통한 의사결정 최적화
- 고성능 달성을 위한 효과적인 마이그레이션 전략 수립

### 3.3. 통합 관리 프레임워크
- RSM와 MDM의 통합을 통한 시너지 효과
- 고성능과 공정성의 동시 달성
- 다중 프로그램 워크로드 환경에서의 효과적인 메모리 관리

## 핵심 기여

- ProFess는 하이브리드 메인 메모리 관리를 위한 새로운 프레임워크 제안
- 공정성과 성능을 동시에 향상시키는 효과적인 관리 방식 제공
- NVM 기반 하이브리드 메모리 시스템의 실용화에 기여

---

**References:** [paper-summaries/2018HPCA-summarize/profess-a-probabilistic-hybrid-main-memory-management-framework-for-high-performance-and-fairness.md]

## 주요 결과

- 하드웨어 기반 구현
- 플랫 마이그레이팅 하이브리드 메모리 구조 지원
- 기존 프로세서 아키텍처와의 호환성

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]


## 전체 요약

[[../paper-summaries/2018HPCA-summarize/profess-a-probabilistic-hybrid-main-memory-management-framework-for-high-performance-and-fairness.md|전체 요약 보기]]
