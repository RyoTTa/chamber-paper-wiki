---
tags: [nvm, java, persistence, crash-consistency]
venue: ASPLOS
year: 2018
summary_path: paper-summaries/2018ASPLOS-summarize/espresso-brewing-java-for-more-non-volatility-with-non-volatile-memory.md
---

# Espresso: Brewing Java For More Non-Volatility with Non-volatile Memory

## 개요

Espresso는 Java와 JVM을 위한 최초의 전체적(holistic) NVM 지원 시스템입니다. 이 시스템은 프로그래머가 NVM을 활용하여 영속성을 관리할 수 있도록 고성능을 제공합니다.

## 방법론

- Persistent Java Heap (PJH): 영속 데이터를 일반 Java 객체로 관리하는 힙 설계
- 복구 가능한 메커니즘: 힙 메타데이터에 대한 충돌 일관성 보장
- Persistent Java Object (PJO): 프로그래머가 애플리케이션 데이터를 영속화할 수 있는 쉬우면서도 안전한 프로그래밍 모델

## 핵심 기여

1. Java 및 JVM을 위한 최초의 전체적 NVM 지원 시스템 제안
2. 기존 Java 프로그램과의 호환성 유지
3. JPA 및 PCJ보다 우수한 성능 달성
4. 충돌 복구 시 일관성 보장

## 주요 결과

- Espresso는 기존 NVM 지원(JPA 및 PCJ)보다 크게 우수한 성능 발휘
- 기존 Java 프로그램의 데이터 구조와 호환성 유지
- 벤치마크 결과에서 JPA 대비 2-5배, PCJ 대비 1.5-3배 성능 향상

## 한계점

- 특정 JVM 버전에 대한 의존성
- 모든 Java 프로그램에서의 최적화 보장하지 않음
- 하드웨어 특성에 따른 성능 변동

## 관련 concept 페이지

- [[paper-wiki/concepts/nvm|NVM]]
- [[paper-wiki/concepts/persistence|Persistence]]
- [[paper-wiki/concepts/crash-consistency|Crash Consistency]]

## 관련 논문 요약

- [paper-summaries/2018ASPLOS-summarize/espresso-brewing-java-for-more-non-volatility-with-non-volatile-memory.md]