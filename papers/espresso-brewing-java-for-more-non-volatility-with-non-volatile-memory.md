---
tags: [nvm, java, crash-consistency, persistence, managed-runtime]
venue: ASPLOS
year: 2018
summary_path: paper-summaries/2018ASPLOS-summarize/espresso-brewing-java-for-more-non-volatility-with-non-volatile-memory.md
---

# Espresso: Brewing Java For More Non-Volatility with Non-volatile Memory

## 개요

Espresso는 Java와 그 런타임을 위한 통합 지속성 프레임워크로, 프로그래머가 NVM(Non-Volatile Memory)을 활용하여 지속성 데이터를 효율적으로 관리할 수 있게 합니다. Persistent Java Heap(PJH)과 Persistent Java Object(PJO)를 통해 기존 Java 프로그램과 호환되면서 성능을 크게 향상시킵니다.

## 방법론

- **Persistent Java Heap (PJH)**: NVM 기반 힙으로 일반 Java 힙처럼 지속성 Java 객체를 관리
- **Persistent Java Object (PJO)**: PJH 위에 구축된 새로운 지속성 프로그래밍 추상화
- **크래시 일관성 보장**: NVM 할당기에서 크래시 일관성을 보장하기 위한 복구 메커니즘

## 핵심 기여

- NVM과 Java를 통합하는 최초의 통합 프레임워크 제시
- 세밀한 지속성과 거친 지속성 모두 지원하는 통합 인터페이스
- 기존 Java 프로그램의 데이터 구조와 대부분 호환
- JPA 및 PCJ 대비 크게 향상된 성능

## 주요 결과

- 기존 NVM 지원 Java(JPA, PCJ)보다 크게 성능 향상
- 기존 Java 프로그램의 데이터 구조 변경 없이 지속성 객체 조작 가능
- `pnew` 키워드를 통한 간편한 NVM 할당

## 한계점

- OpenJDK 8 기반 구현으로 최신 Java 버전과의 호환성 미확인
- 특정 NVM 하드웨어(3D-Xpoint 등)에 최적화되었을 가능성

## 관련 개념

- [[paper-wiki/concepts/nvm|NVM]]
- [[paper-wiki/concepts/java|Java]]
- [[paper-wiki/concepts/crash-consistency|Crash Consistency]]
- [[paper-wiki/concepts/persistence|Persistence]]