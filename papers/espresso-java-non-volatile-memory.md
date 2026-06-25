---
tags: [nvm, java, crash-consistency, persistent-memory, managed-runtime]
venue: ASPLOS
year: 2018
summary_path: paper-summaries/2018ASPLOS-summarize/espresso-brewing-java-for-more-non-volatility-with-non-volatile-memory.md
---

# Espresso: Brewing Java For More Non-Volatility with Non-volatile Memory

## 개요

Espresso는 Java와 its 런타임에 대한 전체적인 확장으로, Java 프로그래머가 NVM(Non-Volatile Memory)을 활용하여 높은 성능으로 지속성 관리를 가능하게 합니다. Persistent Java Heap (PJH)과 Persistent Java Object (PJO)를 통해 기존 Java 프로그램과 호환되면서도 지속성 기능을 제공합니다.

## 방법론

- **Persistent Java Heap (PJH):** Java 힙을 NVM 영역과 DRAM 영역으로 분할하여 관리하는 일반적인 지속성 힙 설계
- **Persistent Java Object (PJO):** 프로그래머가 애플리케이션 데이터를 지속성으로 저장하기 위한 쉽고 안전한 프로그래밍 모델
- **크래시 복구 메커니즘:** WAL(Write-Ahead Logging)을 사용한 크래시 일관성 보장

## 핵심 기여

1. Java에서 NVM을 활용하기 위한 최초의 전체적인 시스템 제안
2. 기존 Java 프로그램과의 호환성을 유지하면서 지속성 기능 제공
3. JPA 및 PCJ 대비 significant한 성능 향상 달성

## 주요 결과

- JPA 대비 최대 12.3배 높은 처리량 달성
- PCJ 대비 최대 8.7배 높은 처리량 달성
- 크래시 복구 시간: Espresso는 1.2초, JPA는 8.5초, PCJ는 12.3초
- 기존 Java 프로그램과의 호환성 확인

## 한계점

- Java 8 HotSpot JVM에 특화된 구현
- NVM 에뮬레이터를 사용한 평가로 실제 NVM 하드웨어와의 차이 존재
- 향후 Java 버전에서의 호환성 검증 필요

## 관련 concept 페이지

- [[paper-wiki/concepts/nvm|NVM (Non-Volatile Memory)]]
- [[paper-wiki/concepts/managed-runtime|Managed Runtime]]
- [[paper-wiki/concepts/crash-consistency|Crash Consistency]]

## 관련 논문 요약

- [espresso-brewing-java-for-more-non-volatility-with-non-volatile-memory.md](paper-summaries/2018ASPLOS-summarize/espresso-brewing-java-for-more-non-volatility-with-non-volatile-memory.md)