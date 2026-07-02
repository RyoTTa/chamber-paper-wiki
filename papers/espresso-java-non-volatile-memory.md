---
tags: [paper, 2018, 2018ASPLOS, topic/dram, topic/nvm]
venue: "ASPLOS '18 (Architectural Support for Programming Languages and Operating Systems), 2018"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/espresso-java-non-volatile-memory.md"
---

# Espresso: Brewing Java For More Non-Volatility with Non-volatile Memory

**Venue:** ASPLOS '18 (Architectural Support for Programming Languages and Operating Systems), 2018
**저자:** Mingyu Wu, Ziming Zhao, Haoyu Li, Heting Li, Haibo Chen, Binyu Zang, Haibing Guan (Shanghai Jiao Tong University)

## 개요

- 비휘발성 메모리(NVM)는 DRAM에 근접하는 레이턴시와 디스크와 같은 지속성을 동시에 제공하여 메모리 계층 구조를 혁신할 것으로 기대됨
- 기존 관리형 런타임(예: Java 가상 머신)과 NVM을 결합하는 방법은 충분히 이해되지 않음
- 기존 영속성 프로그래밍 모델(JPA, PCJ)의 한계:
  - JPA(Java Persistence API): 조밀한(granular) 추상화를 사용하여 트랜잭션 API를 제공하지만, NVM의 출현을 고려하지 않음
  - Java 객체와 네이티브 직렬화 데이터 간 불필요한 변환 오버헤드 발생
  - PCJ(Persistent Collections for Java): 객체 수준에서 영속 데이터를 조작할 수 있는 세밀한 프로그래밍 모델을 제공하지만, 기존 Java 프로그램과 호환되지 않는 독립 타입 시스템 사용
  - PCJ는 네이티브 객체로 영속 데이터를 관리하여 성능이 저하됨

## 방법론

### 3.1. Persistent Java Heap (PJH)
- 영속 데이터를 일반 Java 객체로 관리하는 힙 설계
- 기존 Java 프로그램과의 호환성 유지
- NVM의 바이트 주소 가능 특성을 활용한 효율적인 메모리 관리
- 힙 메타데이터에 대한 충돌 일관성 보장

### 3.2. Persistent Java Object (PJO)
- 프로그래머가 쉽게 사용할 수 있는 영속화 API 제공
- 기존 Java 타입 시스템과의 호환성 유지
- 안전한 영속성 프로그래밍 모델 제공
- 기존 Java 데이터 구조와의 호환성 보장

### 3.3. 복구 메커니즘
- 충돌 발생 시 힙 메타데이터의 일관성 보장
- 로깅 기반 복구 메커니즘 활용
- 원자적 업데이트를 위한 하드웨어 특성 활용

## 핵심 기여

- 핵심 기여: Java 및 JVM을 위한 최초의 전체적 NVM 지원 시스템 제안
- 성능 향상: 기존 JPA 및 PCJ보다 크게 우수한 성능
- 기존 Java 프로그램과의 호환성 유지로 실용적 적용 가능성 입증
- NVM과 관리형 런타임의 통합을 위한 중요한 발전 방향 제시

## 주요 결과

- 구현 언어: Java 및 JVM 확장
- 시스템 구성 요소:
  - Espresso 런타임: PJH 및 PJO 관리
  - 수정된 JVM: 영속 힙 지원
  - 네이티브 라이브러리: NVM 접근 관리
- 기존 Java 프로그램과의 호환성 유지

## 한계점

- JVM 수정이 필요하여 기존 Java 애플리케이션의 즉시 적용이 어려움
- NVM의 읽기 성능이 DRAM보다 낮아 읽기 중심 워크로드에서는 제한적
- 충돌 복구 시 전체 힙 스캔이 필요할 수 있음 (Zeroing Safety 모드)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]


## 전체 요약

[[../paper-summaries/2018ASPLOS-summarize/espresso-java-non-volatile-memory.md|전체 요약 보기]]
