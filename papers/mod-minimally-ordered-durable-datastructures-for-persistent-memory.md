---
tags: [paper, 2020, 2020ASPLOS, topic/cache, topic/nvm]
venue: "25th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '20)"
year: 2020
summary_path: "../paper-summaries/2020ASPLOS-summarize/mod-minimally-ordered-durable-datastructures-for-persistent-memory.md"
---

# MOD: Minimally Ordered Durable Datastructures for Persistent Memory

**Venue:** 25th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '20)
**저자:** Swapnil Haria (University of Wisconsin-Madison, now at Google), Mark D. Hill (University of Wisconsin-Madison), Michael M. Swift (University of Wisconsin-Madison)

## 개요

- Persistent Memory (PM)은 Intel Optane DCPMM과 같이 2019년부터 출시된 빠르고 바이트 주소 가능한 비휘발성 메모리로, 시스템 재부팅 및 전원 장애 시 애플리케이션 진행 상태를 보존 가능한 복구 가능한(recoverable) 애플리케이션을 가능하게 함
- 현재 PM 복구 가능 애플리케이션 개발의 두 가지 극단적 접근법: (1) 전문 프로그래머가 만든 단일 커스텀 내구성 데이터 구조 (빠르지만 개발 난이도 높음, 합성 불가), (2) 소프트웨어 트랜잭션 메모리 (STM) 기반 범용 접근 (간단하지만 높은 성능 오버헤드)
- PM-STM 기반 애플리케이션의 평균 실행 시간의 64%가 flush 활동에, 9%가 로깅에 소요됨 (Intel PMDK v1.5 기준)
- 주요 성능 병목: 과도한 ordering 제약. 각 트랜잭션에 5-11개의 sfence (x86-64)가 필요하여 flush 지연 시간이 겹치지 못하고 직렬화됨
- Optane DCPMM에서 단일 clwb+sfence 지연 시간은 353ns이나, 16개 flush를 겹치면 평균 flush 지연 시간이 75% 감소 (단, 16개 이상은 거의 추가 개선 없음)

## 방법론

### 3.1. Functional Shadowing 메커니즘

- 모든 MOD 데이터 구조 업데이트는 non-destructive 및 out-of-place로 구현
- 업데이트 시 원본을 수정하지 않고 새 shadow 버전을 생성. shadow 생성에는 ordering 제약이 없음
- 모든 dirty cacheline을 순서 없는 clwb로 flush 가능 (flush 겹침으로 오버헤드 최소화)
- 단일 ordering point로 모든 미완료 flush 완료 및 shadow 영속성 보장
- 이후 애플리케이션이 원본 데이터 구조를 새 shadow로 원자적으로 교체

### 3.2. 구조적 공유 (Structural Sharing)

- 함수형 데이터 구조의 핵심 최적화: tree 기반 구현으로 업데이트 시 상위 레벨의 새 노드만 생성, 하위 서브트리는 기존 데이터 공유
- 1백만 개 요소 데이터 구조의 업데이트 shadow에 필요한 추가 메모리는 원본 데이터 구조의 0.01% 미만
- 넓고 얕은 트리 구현으로 "bubbling-up of writes" 문제 회피 (내부 노드 업데이트 시 부모까지 전파되는 문제)

### 3.3. MOD 데이터 구조 레시피

1. 기존 함수형 데이터 구조 (CHAMPR-tree, RRB-tree 등)를 사용
2. nvm_malloc으로 PM 할당 관리
3. 데이터 구조 내부 상태를 persistent heap에 할당
4. 모든 업데이트 작업에서 수정된 PM cacheline을 unordered clwb로 flush
5. Ordering은 후속 Commit 단계에서 수행

### 3.4. 프로그래밍 인터페이스

- **Basic Interface:** 단일 데이터 구조에 대한 간단한 실패 원자적 업데이트. 내부 버전 관리를 숨기고 STL과 유사한 인터페이스 제공 (push_back, insert, push, pop, enqueue, dequeue)
- **Composition Interface:** 여러 데이터 구조의 여러 업데이트를 원자적으로 수행. Update 단계에서 non-destructive 업데이트로 새 버전 생성 후, Commit에서 원자적 교체
- **Commit 구현:**
  - CommitSingle: 단일 데이터 구조의 다중 업데이트. 8B 원자적 포인터 쓰기로 하나의 ordering point
  - CommitSiblings: 공통 부모 객체가 가리키는 여러 데이터 구조 업데이트. 부모의 새 인스턴스 생성 후 단일 포인터 교체
  - CommitUnrelated: 서로 무관한 여러 데이터 구조 업데이트. 짧은 STM으로 여러 포인터 원자적 업데이트

## 핵심 기여

- **핵심 기여:** PM 복구 가능 애플리케이션 개발을 위한 중간 지대(modular middle ground) 제공. 전문 커스텀 데이터 구조의 높은 성능과 STM의 단순함을 동시에 달성
- **성능:** Intel Optane DCPMM에서 포인터 기반 데이터 구조(map, set, queue, stack) 평균 43% 성능 향상, 애플리케이션 벤치마크 평균 36% 향상 (PMDK v1.5 대비)
- **프로그래밍 용이성:** C++ STL과 유사한 익숙한 인터페이스로 프로그래머가 crash-consistency, ordering, durability 세부 사항 없이 복구 가능 애플리케이션 개발 가능
- **확장성:** 함수형 데이터 구조를 MOD로 변환하는 레시피를 제공하여, Python, JavaScript, Rust 등 다른 언어로의 확장 가능성 제시
- **의의:** PM 생태계에서 복구 가능 애플리케이션 개발의 접근성을 높이고, 효율적인 flush 관리를 위한 새로운 프로그래밍 모델 제시
- **한계 및 향후 연구:** vector 성능 개선, non-temporal writes 통합, 동시성 처리 추가

## 주요 결과

- **언어:** C++14
- **데이터 구조:** map (CHAMPR-tree), set (CHAMPR-tree), stack (linked list), queue (linked list), vector (RRB-tree)
- **PM 할당자:** nvm_malloc (오픈 소스)
- **메모리 재clamation:** 참조 카운팅 기반. PM에 영속적으로 저장하지 않음 (복구 시 스캔으로 해결)
- **자동 테스트:** PM 할당/쓰기/flush/commit/fence 트레이스 생성 후 두 가지 불변식 검증으로 정확성 테스트

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]


## 전체 요약

[[../paper-summaries/2020ASPLOS-summarize/mod-minimally-ordered-durable-datastructures-for-persistent-memory.md|전체 요약 보기]]
