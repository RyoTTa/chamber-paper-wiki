---
tags: [paper, 2019, 2019MICRO, topic/cache, topic/nvm]
venue: "52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO-52), 2019"
year: 2019
summary_path: "../paper-summaries/2019MICRO-summarize/distributed-logless-atomic-durability-with-persistent-memory.md"
---

# Distributed Logless Atomic Durability with Persistent Memory

**Venue:** 52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO-52), 2019
**저자:** Siddharth Gupta (EcoCloud, EPFL), Alexandros Daglis (Georgia Institute of Technology), Babak Falsafi (EcoCloud, EPFL)

## 개요

- 데이터센터 운영자들은 퍼시스턴트 메모리(Persistent Memory, PM)를 도입하여 빠른 접근 속도와 영속성을 결합한 성능 이점을 활용하기 시작하였다. Intel 3D XPoint와 같은 비휘발성 메모리 기반 제품들이 PM의 배포를 가속화하고 있다.
- PM을 효과적으로 활용하기 위해 소프트웨어는 **크래시 컨시스턴시(crash consistency)**를 위해 특별히 설계되어야 한다. 특히 트랜잭션 프로그래밍 추상화에서는 **원자적 영속성(atomic durability)**이 요구된다.
- 기존 원자적 영속성의 주요 접근법은 **로그 기반(write-ahead logging)** 방식으로, 이는 상당한 오버헤드를 유발한다: △추가 CPU 사이클 △쓰기 트래픽 증가 △명령 순서 제약(ordering constraints). 특히 **짧은 트랜잭션에서 성능 저하가 두드러진다**.
- 기존 연구들(Kiln 등)은 영속적 스테이징 영역을 활용하는 접근법을 제안했으나, **단일 LLC(Last Level Cache) 중심의 집중화된 구조**에 의존하여 확장 가능한 메모리 계층 구조를 지원하지 못한다.
- 현대 서버 CPU의 메모리 계층 구조는 **분산된 다중 메모리 컨트롤러(MC)**를 특징으로 하며, 단일 트랜잭션의 갱신이 서로 다른 메모리 위치에 분산된 데이터에 영향을 줄 수 있어 **분산된 스펙ulative 상태 관리**가 핵심 도전 과제로 부상한다.

## 방법론

### 3.1. 메모리 컨트롤러의 영속적 버퍼링

- **MC 큐의 활용:** 요청 큐(request queues)를 트랜잭션의 스테이징 영역으로 활용
  - 배터리 백업 요구사항이 적음 (큐의 용량이 작음)
  - 최신 서버 CPU에서 이미 배터리 백업된 MC 사용 가능
- **동작 원리:**
  - 트랜잭션 실행 중 모든 갱신을 MC 큐에 버퍼링
  - 트랜잭션 종료 시 원자적으로 PM에 커밋
  - 전원 장애 시 배터리 백업된 MC가 모든 갱신을 보존

### 3.2. 분산 커밋 프로토콜 (Two-Phase Commit)

- **프로토콜 구조:**
  - 트랜잭션이 여러 MC에 걸쳐 분산된 갱신을 생성할 때 적용
  - 각 MC는 독립적으로 자신의 갱신을 로컬로 버퍼링
  - 커밋 시점에서 모든 MC가 동시에 커밋 수행
- **원자적 커밋 보장:**
  - 단일 트랜잭션의 갱신이 여러 MC에 분산되어 있을 때, 모든 MC가 하나로 커밋하거나 아무것도 커밋하지 않음
  - 하드웨어 수준에서 원자적 결정을 보장하는 분산 프로토콜 구현

### 3.3. 복구 메커니즘

- **크래시 시 동작:** 전원 장애 발생 시 MC의 영속적 큐에서 버퍼링된 갱신을 검색
- **일관성 보장:** 항상 모든 갱신이 PM에 반영되거나, 아무것도 반영되지 않는 원자성 보장
- **기존 기술과의 차별점:** 
  - Kiln과 달리 LLC 수정 불필요
  - 분산된 메모리 계층 구조 지원

## 핵심 기여

- **핵심 기여:** 로깅 없이 원자적 영속성을 달성하는 최초의 하드웨어 메커니즘 LAD 제시
- **성능 향상:** 이상적 성능의 80%를 달성하면서 로그 기반 오버헤드 완전 제거
- **실용성:** 기존 현대 CPU의 배터리 백업된 MC를 활용하는 실용적인 설계로, 데이터센터에서의 PM 활용에 큰 기여
- **기술적 의의:** 분산된 메모리 계층 구조에서의 원자적 영속성 관리 문제를 해결하여, 향후 확장 가능한 PM 시스템 설계의 기반 마련

## 주요 결과

- **하드웨어 변경 범위:** L1D 캐시와 메모리 컨트롤러(MC)에 대한 제한된 하드웨어 수정
- **영속성 요구사항:** MC만 영속성이 요구되며, 온칩 캐시는 영속성 불필요
- **시스템 구성:** 현대 서버 CPU의 기존 배터리 백업된 MC 활용
- **소프트웨어 오버헤드:** 로그 생성 오버헤드를 제거하여 기존 로그 기반 접근법 대비 상당한 성능 향상

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]


## 전체 요약

[[../paper-summaries/2019MICRO-summarize/distributed-logless-atomic-durability-with-persistent-memory.md|전체 요약 보기]]
