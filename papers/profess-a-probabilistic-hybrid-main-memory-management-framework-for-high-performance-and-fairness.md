---
tags: [hybrid-memory, nvm, dram, fairness, performance, memory-management]
venue: HPCA
year: 2018
summary_path: paper-summaries/2018HPCA-summarize/profess-a-probabilistic-hybrid-main-memory-management-framework-for-high-performance-and-fairness.md
---

# ProFess: A Probabilistic Hybrid Main Memory Management Framework for High Performance and Fairness

## 개요

ProFess는 고성능과 공정성을 위한 확률론적 하이브리드 메인 메모리 관리 프레임워크입니다. NVM 기반 하이브리드 메모리 시스템에서 공정 프로그램들이 제한된 DRAM 자원을 두고 경쟁하는 문제를 해결하기 위한 새로운 접근법을 제안합니다.

## 방법론

- **Relative-Slowdown Monitor (RSM)**: M1에 대한 경쟁으로 인해 가장 크게 손해를 보는 프로그램을 지시하여 공정한 관리 가능
- **확률론적 Migration-Decision Mechanism (MDM)**: 각 데이터 블록 쌍에 대해 개별적인 비용-편익 분석을 실현하여 고성능 달성
- **통합 관리 프레임워크**: RSM와 MDM의 통합을 통한 시너지 효과

## 핵심 기여

1. 하이브리드 메인 메모리 관리를 위한 새로운 확률론적 프레임워크 제안
2. 공정성과 성능을 동시에 향상시키는 효과적인 관리 방식
3. NVM 기반 하이브리드 메모리 시스템의 실용화에 기여

## 주요 결과

- 기존 최첨단 기법 대비 공정성을 15% 평균(최대 29%) 향상
- 기존 최첨단 기법 대비 성능을 12% 평균(최대 29%) 향상
- 다중 프로그램 워크로드 환경에서 효과적인 성능 발휘

## 한계점

- 하드웨어 기반 구현에 의존하며, 소프트웨어만으로는 구현하기 어려움
- 특정 워크로드 패턴에 최적화되어 있을 수 있음
- 추가적인 하드웨어 오버헤드에 대한 분석 부족

---

**Related Concepts:**
- [[paper-wiki/concepts/hybrid-memory|Hybrid Memory]]
- [[paper-wiki/concepts/nvm|NVM (Non-Volatile Memory)]]
- [[paper-wiki/concepts/memory-management|Memory Management]]

**Related Papers:**
- [paper-summaries/2018HPCA-summarize/profess-a-probabilistic-hybrid-main-memory-management-framework-for-high-performance-and-fairness.md]