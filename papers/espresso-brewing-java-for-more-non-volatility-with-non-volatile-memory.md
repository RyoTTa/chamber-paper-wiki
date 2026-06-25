---
tags: [paper, 2018, 2018ASPLOS, topic/nvm, topic/java]
venue: "ASPLOS 2018"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/espresso-brewing-java-for-more-non-volatility-with-non-volatile-memory.md"
---

# Espresso: Brewing Java For More Non-Volatility with Non-volatile Memory

**Venue:** ASPLOS 2018
**저자:** Mingyu Wu, Ziming Zhao, Haoyu Li, Heting Li, Haibo Chen, Binyu Zang, Haibing Guan (Shanghai Jiao Tong University)

## 개요

NVM(Non-Volatile Memory)은 DRAM에 가까운 지연 시간과 디스크 수준의 지속성을 제공하지만, 관리형 런타임(Java JVM)에서의 활용은 충분히 연구되지 않음. 기존 Java 지속성 모델(JPA, PCJ)은 성능이 좋지 않거나 기존 Java 프로그램과 호환되지 않음.

Espresso는 Java와 NVM을 통합하는 최초의 완전한 솔루션으로, Persistent Java Heap (PJH)과 Persistent Java Object (PJO)를 제공하여 기존 Java 프로그램과 호환되면서도 높은 성능을 달성.

## 방법론

### Persistent Java Heap (PJH)
- Java 힙을 NVM 영역과 DRAM 영역으로 분리하여 관리
- 지속성 데이터는 NVM에, 비지속성 데이터는 DRAM에 배치
- 힙 메타데이터에 대한 충돌 일관성(crash consistency) 보장

### Persistent Java Object (PJO)
- Java 객체에 지속성 속성을 추가하는 새로운 추상화
- 세 가지 지속성 모드: Eager, Lazy, Volatility
- 프로그래머가 객체별로 지속성 모드를 선택할 수 있는 유연성 제공

### 충돌 일관성 메커니즘
- Write-Ahead Logging (WAL) 기반 복구 메커니즘
- NVM에 로그 영역을 별도로 할당하여 지속성 데이터 변경사항 기록

## 핵심 기여

1. Java와 NVM을 통합하는 최초의 완전한 솔루션 제공
2. 기존 Java NVM 지원(JPA, PCJ) 대비 최대 4.5배 성능 향상
3. 기존 Java 프로그램과의 완전한 호환성 보장

## 주요 결과

- Espresso vs JPA: 최대 4.5배 높은 처리량 달성
- Espresso vs PCJ: 최대 3.2배 높은 처리량 달성
- NVM 접근 오버헤드: 기존 수동 지속성 관리 대비 60% 감소
- 충돌 복구 시간: 100MB 힙 기준 평균 12ms

## 한계점

- JVM 수정이 필요하여 기존 Java 애플리케이션 배포에 추가 작업 필요
- NVM 하드웨어 의존성으로 인해 일반화된 환경에서의 적용에 제한
- GC 일시정지 시간 증가 가능

## 관련 개념

- [[paper-wiki/concepts/nvm|NVM]]
- [[paper-wiki/concepts/java-virtual-machine|Java Virtual Machine]]
- [[paper-wiki/concepts/crash-consistency|Crash Consistency]]

## 관련 논문

- [Espresso 논문 요약](../paper-summaries/2018ASPLOS-summarize/espresso-brewing-java-for-more-non-volatility-with-non-volatile-memory.md)