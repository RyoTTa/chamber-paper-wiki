---
tags: [java, nvm, persistence, crash-consistency, managed-runtime]
venue: ASPLOS
year: 2018
summary_path: paper-summaries/2018ASPLOS-summarize/espresso-brewing-java-for-more-non-volatility-with-non-volatile-memory.md
---

# Espresso: Brewing Java For More Non-Volatility with Non-volatile Memory

## 개요

Espresso는 Java와 그 런타임을 위한 전체적인 확장 패키지로, 프로그래머가 NVM을 활용하여 고성능으로 지속성 관리를 가능하게 합니다. 이 논문은 Java 환경에서 NVM을 효과적으로 활용하기 위한 새로운 프로그래밍 모델과 시스템 설계를 제안합니다.

## 방법론

- **Persistent Java Heap (PJH)**: 지속성 데이터를 일반 Java 객체로 관리하는 일반적인 힙 디자인
- **Persistent Java Object (PJO)**: 쉽고 안전한 지속성 프로그래밍 모델을 위한 새로운 추상화
- **크래시 일관성 보장**: 힙 메타데이터의 복구 메커니즘을 통한 데이터 무결성 보장

## 핵심 기여

1. Java 환경에서 NVM을 효과적으로 활용하는 최초의 전체적인 프레임워크 제안
2. 기존 Java 프로그램과의 완전한 호환성을 유지하면서도 성능 향상
3. 프로그래머에게 쉽고 안전한 지속성 프로그래밍 모델 제공

## 주요 결과

- 기존 Java NVM 지원 방식(JPA 및 PCJ)보다 상당한 성능 향상 달성
- 기존 Java 프로그램의 데이터 구조와 완전한 호환성 유지
- 프로그래머가 쉽게 사용할 수 있으면서도 안전한 지속성 프로그래밍 모델 제공

## 한계점

- Java 런타임에 특화된 솔루션으로 다른 언어나 환경에는 직접 적용하기 어려움
- NVM 하드웨어의 특성에 의존적이며, 향후 NVM 기술 변화에 따른 адап테이션 필요
- 대규모 시스템에서의 확장성에 대한 충분한 평가 부족

---

**Related Concepts:**
- [[paper-wiki/concepts/nvm|NVM (Non-Volatile Memory)]]
- [[paper-wiki/concepts/persistence|Persistence Management]]
- [[paper-wiki/concepts/crash-consistency|Crash Consistency]]

**Related Papers:**
- [paper-summaries/2018ASPLOS-summarize/espresso-brewing-java-for-more-non-volatility-with-non-volatile-memory.md]