---
tags: [nvm, java, persistence, crash-consistency, jvm]
venue: ASPLOS 2018
year: 2018
summary_path: paper-summaries/2018ASPLOS-summarize/espresso-java-non-volatile-memory.md
---

# Espresso: Brewing Java For More Non-Volatility with Non-volatile Memory

## 개요

Espresso는 Java와 JVM(Java Virtual Machine)을 위한 최초의 전체적(holistic) NVM 지원 시스템입니다. 이 시스템은 프로그래머가 NVM을 활용하여 영속성을 관리할 수 있도록 고성능을 제공하면서 기존 Java 프로그램과의 호환성을 유지합니다.

## 방법론

### Persistent Java Heap (PJH)
- 영속 데이터를 일반 Java 객체로 관리하는 영속 힙 설계
- NVM의 바이트 주소 가능 특성을 활용한 효율적인 메모리 관리
- 힙 메타데이터에 대한 충돌 일관성(crash consistency) 보장

### Persistent Java Object (PJO)
- 프로그래머가 쉽게 사용할 수 있는 영속화 API 제공
- 기존 Java 타입 시스템과의 호환성 유지
- 안전한 영속성 프로그래밍 모델 제공

### 복구 메커니즘
- 충돌 발생 시 힙 메타데이터의 일관성 보장
- 로깅 기반 복구 메커니즘 활용
- 원자적 업데이트를 위한 하드웨어 특성 활용

## 핵심 기여

1. **최초의 전체적 NVM 지원 시스템**: Java 및 JVM을 위한 최초의 전체적 NVM 지원 시스템 제안
2. **높은 성능**: 기존 NVM 지원(JPA 및 PCJ)보다 크게 우수한 성능 발휘
3. **호환성 유지**: 기존 Java 프로그램의 데이터 구조와 호환성 유지
4. **안전한 프로그래밍 모델**: 쉬우면서도 안전한 영속성 프로그래밍 모델 제공

## 주요 결과

- Espresso는 기존 NVM 지원(JPA 및 PCJ)보다 크게 우수한 성능 발휘
- 기존 Java 프로그램의 데이터 구조와 호환성 유지
- 충돌 복구 시 일관성 보장하면서 높은 성능 달성
- 벤치마크 결과에서 JPA 대비 2-5배, PCJ 대비 1.5-3배 성능 향상

## 한계점

- NVM 시뮬레이션 환경에서의 평가로 실제 NVM 하드웨어에서의 성능 검증 필요
- Java 프로그램에 특화되어 있어 다른 관리형 런타임(예: Python)으로의 확장 어려움
- 복구 메커니즘의 오버헤드가 일부 워크로드에서 발생할 수 있음

## 관련 개념

- [[paper-wiki/concepts/nvm.md|NVM (Non-Volatile Memory)]]
- [[paper-wiki/concepts/java.md|Java]]
- [[paper-wiki/concepts/crash-consistency.md|Crash Consistency]]

## 관련 논문

- [paper-summaries/2018ASPLOS-summarize/espresso-java-non-volatile-memory.md]