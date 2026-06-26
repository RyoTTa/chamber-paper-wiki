---
tags: [paper, 2019, 2019ASPLOS, topic/dram, topic/nvm, topic/security]
venue: "24th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '19)"
year: 2019
summary_path: "../paper-summaries/2019ASPLOS-summarize/pmtest-fast-testing-framework-for-persistent-memory-programs.md"
---

# PMTest: A Fast and Flexible Testing Framework for Persistent Memory Programs

**Venue:** 24th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '19)
**저자:** Sihang Liu (University of Virginia), Yizhou Wei (University of Virginia), Jishen Zhao (UC San Diego), Aasheesh Kolli (Penn State University / VMware Research), Samira Khan (University of Virginia)

## 개요

- 3D XPoint, NVDIMMs와 같은 비휘발성 메모리(PM, Persistent Memory) 기술의 발전으로 메모리에서 직접 영속 데이터를 조작하는 PM 시스템이 등장
- PM 기반 크래시 일관성 소프트웨어(CCS, Crash-Consistent Software)는 커널 모듈, 사용자 공간 라이브러리, 커스텀 애플리케이션까지 다양하게 개발되고 있으나, 크래시 일관성 보장은 어렵고 버그가 발생하기 쉬움
- 두 가지 기본 보장이 필요: (1) **지속성 보장(Durability Guarantee)** - 데이터가 신뢰성 있게 영속화됨을 보장, (2) **순서 보장(Ordering Guarantee)** - 쓰기 연산의 순서를 명시적으로 강제
- 하드웨어는 런타임에 명령어를 재순서화할 수 있어, 프로그래머가 올바른 순서와 지속성 보장을 구현했는지 테스트하기 어려움
- 기존 테스트 도구의 한계:
  - **Yat**: Intel PMFS 전용, 100k PM 연산에서 5년 이상 소요 (완전 탐색 방식)
  - **Pmemcheck**: PMDK 전용, 약 20× 성능 오버헤드
  - **Persistence Inspector**: PMDK 전용, x86 지속성 모델만 지원
  - 모든 기존 도구는 특정 CCS나 메모리 지속성 모델에만 국한되거나 상당한 성능 오버헤드 발생

## 방법론

### 3.1. 시스템 아키텍처

- PMTest는 두 가지 주요 구성요소로 구성: (1) **트래킹 엔진** - 대상 프로그램에서 PM 연산을 추적, (2) **체킹 엔진** - 추적된 트레이스를 검증
- 사용자 공간 CCS: PMTest 체킹 엔진과 동일 프로세스에서 실행, 스레드 안전 큐로 트레이스 전달
- 커널 모듈: 커널 FIFO(/proc/PMTest)를 통해 사용자 공간 체커로 트레이스 전달 (1024 트레이스 엔트리)
- 다중 스레드 프로그램 지원: 스레드별 독립적 트레이스 유지, `PMTest_THREAD_INIT()`으로 초기화

### 3.2. 트래킹 엔진

- x86 아키텍처에서 세 가지 기본 PM 연산 추적:
  - `write(addr, size)` - 주소 범위에 대한 쓰기 연산
  - `clwb(addr, size)` - 캐시 라인을 PM으로 쓰기백 (지속 강제)
  - `sfence` - 이전 write/clwb의 순서 강제 (지속성 배리어)
- PMTest 함수 요약 (Table 2):
  - **초기화/종료**: `PMTest_INIT()`, `PMTest_EXIT()`, `PMTest_THREAD_INIT()`
  - **제어**: `PMTest_START()`, `PMTest_END()`
  - **범위 관리**: `PMTest_EXCLUDE()`, `PMTest_INCLUDE()`
  - **변수 등록**: `PMTest_REG_VAR()`, `PMTest_UNREG_VAR()`, `PMTest_GET_VAR()`
  - **통신**: `PMTest_SEND_TRACE()`, `PMTest_GET_RESULT()`
  - **체커**: `isPersist()`, `isOrderedBefore()`, `TX_CHECKER_START/END()`

### 3.3. 체킹 엔진 (Checking Engine)

- **영속 상태(Persistency Status) 관리:**
  - 그림자 메모리(Shadow Memory)를 인터벌 트리(Interval Tree)로 구현하여 주소를 구간, 영속 상태를 값으로 관리
  - O(log n) 복잡도의 업데이트/조회 연산 (n = 트레이스 길이)
  - 두 가지 상태 구조:
    - `global_timestamp`: sfence встреч时 증가하는 글로벌 에포크 카운터
    - `persist_interval`: 특정 메모리 위치가 영속화될 수 있는 시간 구간
    - `flush_interval`: 특정 메모리 위치가 명시적으로 쓰기백될 수 있는 시간 구간

- **상태 업데이트 규칙:**
  - `write(addr, size)`: persist_interval을 `(global_timestamp, ∞)`로 설정
  - `clwb(addr, size)`: flush_interval을 `(global_timestamp, ∞)`로 설정
  - `sfence`: global_timestamp 증가 → 이전 clwb의 flush_interval과 persist_interval을 현재 에포크로 종료

- **검증 규칙:**
  - `isPersist(addr, size)`: persist_interval이 현재 global_timestamp 이전에 종료되는지 확인
  - `isOrderedBefore(addrA, sizeA, addrB, sizeB)`: addrA의 persist_interval과 addrB의 persist_interval이 겹치지 않는지 확인

- **다중 스레드 체킹:**
  - 마스터 스레드 + 워커 스레드 풀 구조 (Figure 8)
  - 라운드로빈 스케줄링으로 트레이스를 워커에 배포
  - 독립적인 테스트로 병렬 처리 가능

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1. 라이브러리별 체커 (PMDK 트랜잭션용)

- **불완전 트랜잭션 검사:**
  - `TX_CHECKER_START()`와 `TX_CHECKER_END()`로 트랜잭션 범위 표시
  - 트레이스 끝에서 모든 수정된 영속 객체에 `isPersist()` 자동 주입
  - `PMTest_EXCLUDE()`로 일관성 보호가 필요 없는 업데이트 제외 가능

- **백업 로그 누락 검사:**
  - `TX_ADD()`로 로깅된 객체를 추적하는 추가 인터벌 트리(log tree) 유지
  - 수정 전에 해당 객체가 log tree에 존재하는지 확인
  - 로깅 누락 시 자동 감지

### 4.2. 성능 체커

- **불필요한 쓰기백 검사:**
  - 아직 수정되지 않은 데이터의 `clwb` 감지 (WARN 보고)
  - 동일 객체의 중복 `clwb` 감지

- **중복 로깅 검사:**
  - PMDK 트랜잭션에서 동일 영속 객체를 여러 번 로깅하는 경우 감지 (WARN 보고)

### 4.3. 다른 지속성 모델 적응

- HOPS(Hands-Off Persistence System) 모델 지원:
  - `ofence`: 순서만 보장 (쓰기백 안 함) → global_timestamp 증가
  - `dfence`: 순서 + 지속성 보장 → global_timestamp 증가 + persist_interval 종료
  - `isPersist()`와 `isOrderedBefore()` 규칙은 동일한 원리로 적용

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/security.md|Security]]


## 전체 요약

[[../paper-summaries/2019ASPLOS-summarize/pmtest-fast-testing-framework-for-persistent-memory-programs.md|전체 요약 보기]]
