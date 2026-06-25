---
tags: [paper, 2020, 2020MICRO, topic/dram, topic/nvm]
venue: "53rd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '20)"
year: 2020
summary_path: "../paper-summaries/2020MICRO-summarize/p-inspect-architectural-support-for-programmable-non-volatile-memory-frameworks.md"
---

# P-INSPECT: Architectural Support for Programmable Non-Volatile Memory Frameworks

**Venue:** 53rd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '20)
**저자:** Apostolos Kokolis, Thomas Shull, Jian Huang, Josep Torrellas (University of Illinois at Urbana-Champaign)

## 개요

- NVM(Non-Volatile Memory) 기술(3D XPoint, PCM, ReRAM 등)이 높은 저장 밀도, 낮은 정적 전력, DRAM에 필적하는 성능 특성을 제공하지만, 성공 여부는 사용자 친화적인 프로그래밍 프레임워크에 달려 있음
- 기존 NVM 프로그래밍 프레임워크의 대부분은 프로그래머에게 NVM에 배치할 모든 객체를 수동으로 표시하도록 요구하며, persistent store를 식별하고 CLWB, sfence 명령어와 로그를 수동으로 삽입해야 함 → 프로그래밍 난이도 증가, 잠재적 버그 발생, 재사용 불가능한 코드 생성
- Persistence by Reachability 프레임워크는 프로그래머가 durable root(진입점)만 지정하면 런타임이 자동으로 전이적 클로저(closure)의 영속성을 보장하여 프로그래밍 부담을 크게 줄이지만, 런타임 오버헤드가 상당함
- Persistence by Reachability 프레임워크의 런타임은 프로그램의 모든 load/store 시점에서 동적 상태 검사 수행, DRAM과 NVM 간 데이터 구조 이동을 런타임에 수행 → 상당한 실행 시간 오버헤드 발생
- 기존 하드웨어 기반 접근법(Intel MPX 등)은 포인터 경계 같은 제한된 정보만 제공 가능하며, 메모리 위치에 태깅하는 접근법은 프로덕션 코드에 사용하기에 오버헤드가 너무 큼

## 방법론

### 3.1. Bloom Filter 기반 상태 검사

- P-INSPECT는 두 개의 하드웨어 블룸 필터를 활용:
  - **FWD (Forwarding) Bloom Filter:** forwarding 객체를 추적. DRAM에 있는 객체가 NVM로 복사되면 Forwarding bit이 설정되며, 해당 객체의 주소가 FWD 블룸 필터에 추가됨
  - **TRANS (Transient) Bloom Filter:** transitive closure 처리가 진행 중인 객체를 추적. Queued bit이 설정된 객체를 추적
- checkStoreBoth 연산 시:
  - 소유자(Ha)의 기반 주소가 NVM에 있고 Xaction이 아닌 경우 → 하드웨어가 즉시 write 수행 (Table IV, row 1)
  - 소유자가 DRAM에 있고 forwarding이 아닌 경우 → 하드웨어가 즉시 write 수행 (Table IV, row 2-3)
  - 그 외의 경우 → 소프트웨어 핸들러(checkHandV, checkV, logStore)를 자동 호출
- checkLoad 연산 시:
  - 객체가 NVM에 있거나 DRAM에서 FWD 블룸 필터에 없는 경우 → 하드웨어가 즉시 read 수행 (Table V)
  - FWD 블룸 필터에 있는 경우 → 소프트웨어 핸들러(loadCheck)를 호출하여 Forwarding bit 확인 후 포인터 따라감

### 3.2. 소프트웨어 핸들러 (Algorithm 1)

- **checkHandV (handler x):** 소유자와 값 객체 모두에서 forwarding을 검사
  - 소유자가 persistent하지 않으면 일반 write 수행 (Line 18)
  - 값 객체가 persistent하지 않으면 makeRecoverable() 호출로 NVM으로 이동 (Line 9)
  - Xaction 내부이면 로그 엔트리 생성 후 persistentWrite 수행 (Line 11-13)
- **checkV (handler y):** 소유자가 NVM에 있는 경우, 값 객체만 검사
- **logStore (handler z):** 두 객체 모두 NVM에 있고 Xaction인 경우, 로그 엔트리 생성 후 persistentWrite
- **loadCheck (handler {):** DRAM에 있는 객체의 Forwarding bit 확인 후 포인터 따라가 read

### 3.3. PersistentWrite 명령어 (Figure 2)

- 기존의 write + CLWB + sfence 세 작업이 최악의 경우 2번의 메모리 왕복을 요구 → P-INSPECT는 이를 단일 왕복으로 결합
- persistentWrite의 세 가지 플레이버:
  1. 단순 write (CLWB/sfence 불필요)
  2. write + CLWB (sfence 불필요)
  3. write + CLWB + sfence (가장 큰 성능 향상)
- 구현 과정 (Figure 2(b)):
  - 기존 코어가 persistentWrite를 발행하면 캐시 계층을 통해 업데이트 전달 (Step 1)
  - 디렉토리가 라인을 recall하고 소유자 캐시 무효화 (Step 2)
  - 업데이트가 dirty 캐시 라인과 결합되어 NVM으로 전송 (Step 3)
  - NVM에서 ACK가 디렉토리를 거쳐 기존 코어로 반환 (Step 4)
- NVM이 캐시 라인보다 미세한 granularity로 쓰기를 지원하는 경우에 최적화 적용 가능

## 핵심 기여

- **핵심 기여:** Persistence by Reachability NVM 프레임워크를 가속화하는 최초의 하드웨어 아키텍처 P-INSPECT 제시
- **프로그래밍 편의성 유지:** 프로그래머의 개입 없이 기존 프레임워크의 persistence by reachability 특성을 그대로 유지
- **실질적 성과:** 실행 명령어 26% 감소, 실행 시간 16% 감소로 이상적 런타임 수준의 성능 달성
- **하드웨어-소프트웨어 공조:** 블룸 필터 기반 투명 검사와 persistentWrite 명령어의 결합으로 NVM 프로그래밍의 실용성 크게 향상
- **의의:** NVM 기술의 광범위한 도입에 필수적인 프로그래밍 난이도 문제를 하드웨어 지원으로 해결하는 방향 제시

## 주요 결과

- **시뮬레이션 기반 평가:** 기존 Persistence by Reachability 프레임워크와 통합된 시뮬레이션 환경 사용
- **하드웨어 블룸 필터:** 캐시 코히어런트 프로토콜과 통합되어 snooping을 통해 투명하게 동작
- **소프트웨어 핸들러:** 기존 프레임워크의 런타임에 통합되며, checkHandV, checkV, logStore, loadCheck 네 가지 핸들러로 구성
- **persistentWrite:** CPU 명령어 세트에 추가되며, 캐시 계층과 디렉토리 프로토콜의 수정으로 구현

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]


## 전체 요약

[[../paper-summaries/2020MICRO-summarize/p-inspect-architectural-support-for-programmable-non-volatile-memory-frameworks.md|전체 요약 보기]]
