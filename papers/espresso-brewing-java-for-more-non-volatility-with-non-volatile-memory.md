---
tags: [paper, 2018, 2018ASPLOS, topic/nvm, topic/pim]
venue: "ASPLOS 2018"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/espresso-brewing-java-for-more-non-volatility-with-non-volatile-memory.md"
---

# Espresso: Brewing Java For More Non-Volatility with Non-volatile Memory

**Venue:** ASPLOS 2018 (Architectural Support for Programming Languages and Operating Systems)
**저자:** Mingyu Wu, Ziming Zhao, Haoyu Li, Heting Li, Haibo Chen, Binyu Zang, Haibing Guan (Shanghai Jiao Tong University)

## 개요

비휘발성 메모리(NVM)는 DRAM에 근접하는 레이턴시와 디스크와 같은 지속성을 동시에 제공하지만, 관리형 런타임(예: JVM)과의 결합 방법은 충분히 이해되지 않음. 기존 영속성 프로그래밍 모델(JPA, PCJ)은 성능 오버헤드가 크거나 기존 Java 프로그램과 호환되지 않는 문제점이 있음.

Espresso는 Java와 런타임을 위한 전체적 확장 시스템으로, Persistent Java Heap (PJH)과 Persistent Java Object (PJO)를 통해 고성능 영속성 관리를 제공. PCJ 대비 최대 256.3배, JPA 대비 최대 3.24배 성능 향상을 달성.

## 방법론

### Persistent Java Heap (PJH)
- 기존 Java 힙에 NVM 기반 영속 힙을 추가하는 확장 설계
- 영속 데이터를 일반 Java 객체로 관리하여 기존 프로그램과의 호환성 유지
- `pnew` 키워드로 NVM에 객체 할당
- Non-generational 힙 설계 (NVM은 오래 지속되는 데이터 저장에 적합)

### 복구 가능한 가비지 컬렉터
- 충돌 일관성을 보장하는 가비지 컬렉터 설계
- Timestamp 기반 알고리즘으로 충돌 상태 추론 및 복구
- 일관된 스냅샷(Consistent Snapshot)을 NVM에 저장하여 복구 보장
- 복구 시간: 평균 2.574초, 최대 4.161초

### Persistent Java Object (PJO)
- JPA와 호환되는 영속 프로그래밍 추상화
- SQL 변환 단계를 제거하여 성능 향상
- DBPersistable 인터페이스로 네이티브 객체 직접 영속화
- 데이터 중복 제거(Data Deduplication) 최적화

## 핵심 기여

1. Persistent Java Heap (PJH) 설계: 기존 Java 프로그램의 대규모 재설계 없이 NVM 활용 가능
2. 새로운 영속 프로그래밍 추상화 (PJO): 단순하고 안전한 영속 데이터 조작
3. OpenJDK 기반 구현 및 체계적 평가로 효과 입증

## 주요 결과

- **PCJ 대비 성능**: Tuple Set 작업에서 256.3배, Primitive Create에서 60.4배 향상
- **JPA 대비 성능**: JPAB 벤치마크에서 최대 3.24배 향상 (H2 데이터베이스)
- **히프 로딩 시간**: User-guaranteed 안전 모드에서 객체 수에 관계없이 일정 (Klass 수에 비례)
- **복구 시간**: 평균 2.574초, 최대 4.161초 (일반 Old GC 단계와 유사)
- **구현 규모**: OpenJDK 8 기반 PJH 7,000줄 C++ + 300줄 Java, PJO 1,500줄 Java

## 한계점

- JVM 수정이 필요하여 기존 Java 애플리케이션의 즉시 적용이 어려움
- NVM의 읽기 성능이 DRAM보다 낮아 읽기 중심 워크로드에서는 제한적
- 충돌 복구 시 전체 힙 스캔이 필요할 수 있음 (Zeroing Safety 모드)

## 관련 개념

- [[paper-wiki/concepts/nvm.md|NVM]]
- [[paper-wiki/concepts/pim.md|PIM]]
- [[paper-wiki/concepts/storage.md|Storage]]

## 참고

- [요약 파일](../paper-summaries/2018ASPLOS-summarize/espresso-brewing-java-for-more-non-volatility-with-non-volatile-memory.md)
