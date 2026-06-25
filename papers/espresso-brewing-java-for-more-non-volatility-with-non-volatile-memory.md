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

NVM(Non-Volatile Memory)은 DRAM에 가까운 레이턴시와 디스크와 같은 지속성을 제공하지만, Java와 같은 고급 프로그래밍 언어에서의 활용은 충분히 이해되지 않음. 기존 JPA와 PCJ는 각각 다른 한계를 가지고 있어 통합적으로 사용할 수 없음.

Espresso는 Java에서 NVM을 효과적으로 활용하기 위한 통합 지속성 프레임워크를 제안하며, Persistent Java Heap (PJH)과 Persistent Java Object (PJO)를 통해 기존 Java 프로그램과 호환되면서도 지속성 관리 성능을 크게 향상시킴.

## 방법론

### Persistent Java Heap (PJH)
- NVM 기반 힙으로 기존 Java 객체를 변경 없이 NVM에 저장
- `pnew` 키워드를 통해 NVM에 Java 객체 할당
- 크래시 일관 할당 및 해제를 보장하는 메모리 관리자

### Persistent Java Object (PJO)
- PJH 위에 구축된 새로운 지속성 프로그래밍 추상화
- JPA API를 재사용하여 하위 호환성 유지
- 불필요한 오버헤드를 제거한 성능 최적화

### 크래시 일관성 보장
- NVM 할당기에서 머신 크래시를 견딜 수 있는 안전한 런타임 환경 제공
- 힙 메타데이터의 무결성을 유지하기 위한 복구 메커니즘

## 핵심 기여

1. Java에서 NVM을 활용하기 위한 최초의 통합 지속성 프레임워크 제안
2. 기존 Java 프로그램과 호환되면서도 지속성 관리 성능을 크게 향상하는 새로운 접근법
3. 세밀한 지속성과 거친 지속성 요구사항을 모두 만족하는 통합 인터페이스

## 주요 결과

- 마이크로벤치마크에서 PCJ 대비 최대 256.3배 속도 향상
- H2 데이터베이스의 JPAB 벤치마크에서 JPA 대비 최대 3.24배 속도 향상
- 기존 Java 프로그램과 호환성 유지하면서 지속성 관리 성능 크게 향상

## 한계점

- NVM 하드웨어 지원이 아직 널리 배포되지 않은 상태에서의 연구
- OpenJDK 8 기반 구현으로 최신 Java 버전과의 호환성 미검증
- 다양한 NVM 유형(ReRAM, STT-RAM 등)에서의 성능 차이 미분석

---

**Related Concepts:** [[paper-wiki/concepts/nvm|NVM]], [[paper-wiki/concepts/java-virtual-machine|Java Virtual Machine]], [[paper-wiki/concepts/crash-consistency|Crash Consistency]]