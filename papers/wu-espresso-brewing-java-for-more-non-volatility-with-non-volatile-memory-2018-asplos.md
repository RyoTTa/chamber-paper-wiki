---
tags: [paper, 2018, 2018ASPLOS, topic/nvm, topic/storage, java, persistent-memory, crash-consistency]
venue: "ASPLOS '18"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/espresso-brewing-java-for-more-non-volatility-with-non-volatile-memory.md"
---

# Espresso: Brewing Java For More Non-Volatility with Non-volatile Memory

**Venue:** 23rd International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '18)
**저자:** Mingyu Wu, Ziming Zhao, Haoyu Li, Heting Li, Haibo Chen, Binyu Zang, Haibing Guan

## 개요

Espresso는 Java에서 NVM(Non-Volatile Memory)을 활용한 **통합 지속성 프레임워크**입니다. Persistent Java Heap(PJH)과 Persistent Java Object(PJO)를 통해 기존 Java 프로그램과 호환되면서도 NVM의 성능 이점을 실현합니다.

**핵심 문제:** Managed runtime(Java)에서 NVM 활용 시 기존 접근의 한계:
- JPA: Java 객체→SQL 변환에서 41.9% 오버헤드
- PCJ: 별도 타입 시스템, 오프 힙 디자인 → 기존 프로그램과 호환성 없음, GC/메타데이터 오버헤드 50% 이상

## 방법론

### Persistent Java Heap (PJH)
- NVM 기반 힙으로 영속 객체를 일반 Java 객체로 관리
- pnew 키워드로 NVM에 객체 할당 (new와 유사한 구문)
- 기존 클래스 선언 변경 불필요 → 높은 호환성

### Crash-consistent GC
- PS old GC 기반 region 기반 3단계 알고리즘
- Consistent snapshot + timestamp 기반 크래시 복구
- 객체 헤더 비트 재사용으로 크래시 상태 추론

### Persistent Java Object (PJO)
- JPA API 재사용 (em.persist(), 트랜잭션 관리)
- SQL 변환 단계 제거 → 직접 NVM에 영속화
- Data deduplication으로 DRAM 메모리 절약

## 핵심 기여

1. **통합 지속성 프레임워크**: 파인 그레인(PJH)과 코어스 그레인(PJO) 지속성 모두 지원
2. **높은 호환성**: 기존 Java 데이터 구조 변경 불필요
3. **Crash-consistent heap**: 할당과 GC에서 크래시까지 일관성 보장
4. **Alias Klass**: DRAM/NVM 혼합 환경에서의 타입 안전성 해결

## 주요 결과

- **PJH vs PCJ**: 최대 **256.3x speedup** (Tuple set)
- **PJO vs JPA**: 최대 **3.24x speedup** (BasicTest)
- **히프 로딩**: Klass 수에 비례 (객체 수와 무관) → 0.2-200만 객체에서 상수 시간
- **복구 가능 GC**: 50회 크래시 삽입 실험에서 100% 복구 성공, 평균 복구 시간 2.574초

## 한계점

- Eager paging으로 인한 메모리 단편화 위험
- CoW/fork 시 identity mapping 깨질 수 있음
- NVM은 DRAM보다 느려 성능이 제한적 (장기 수명 데이터에 최적화)
- 멀티스레드 환경에서의 상세 성능 평가 부족

## 관련 개념

- [[paper-wiki/concepts/nvm.md|NVM]] — 비휘발성 메모리 및 지속성
- [[paper-wiki/concepts/storage.md|Storage]] — 데이터베이스 및 영속 스토리지
