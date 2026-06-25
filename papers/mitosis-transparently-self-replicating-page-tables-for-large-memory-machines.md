---
tags: [paper, 2020, 2020ASPLOS, topic/cache, topic/virtual-memory]
venue: "25th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '20)"
year: 2020
summary_path: "../paper-summaries/2020ASPLOS-summarize/mitosis-transparently-self-replicating-page-tables-for-large-memory-machines.md"
---

# Mitosis: Transparently Self-Replicating Page-Tables for Large-Memory Machines

**Venue:** 25th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '20)
**저자:** Reto Achermann (ETH Zurich), Ashish Panwar (IISc Bangalore), Abhishek Bhattacharjee (Yale University), Timothy Roscoe (ETH Zurich), Jayneel Gandhi (VMware Research)

## 개요

- 대규모 메모리(1~100TB)를 가진 멀티소켓 머신이 보편화되면서, NUMA 환경에서의 비균일 메모리 접근이 핵심 성능 병목으로 부각
- 기존 연구는 데이터 할당 및 배치 정책에 집중했으나, 페이지 테이블(page-table)의 소켓 간 배치 문제는 거의 연구되지 않음
- TLB(Trend Lookaside Buffer) 커버리지가 메모리 증가 속도를 따라가지 못해 TLB miss가 빈번해지며, x86-64에서 TLB miss 시 최대 4번의 메모리 접근이 필요 (Intel 5-level page-table에서는 5번으로 증가)
- 멀티소켓 시나리오에서 페이지 테이블이 소켓 간 분산되어 있어 최대 86%의 leaf PTE가 원격 소켓에 위치하는 경우 발생 (Figure 1)
- 워크로드 마이그레이션 시 OS는 데이터 페이지를 마이그레이션하지만 페이지 테이블은 마이그레이션하지 않아 100% TLB miss가 원격 메모리 접근으로 이어짐

## 방법론

### 3.1. 메커니즘 - 메모리 할당

- 페이지 테이블 복제본을 각 소켓에 엄격한(strict) 할당으로 배치
- 기존 Linux의 페이지 할당 기능을 활용하여 페이지 폴트 시 복제본 할당
- 소켓별 메모리 가용성 부족 시 OS가 페이지 캐시에서 페이지를 확보하거나 demand paging으로 해결
- 복제본은 원형 연결 리스트(circular linked list)로 관리하여 효율적인 위치 추적 (Figure 8)

### 3.2. 메커니즘 - 복제본 일관성 유지

- 페이지 테이블 업데이트 시 모든 복제본에 전파(propagation)
- 페이지 테이블 접근 시 일관된 값 반환 보장
- Accessed bit와 dirty bit 처리를 위한 특수 메커니즘:
  - Accessed bit: 소켓 간 복제본에서 가장 최근 accessed bit 값을 유지
  - Dirty bit: 어느 복제본에서든 dirty로 표시되면 모든 복제본에서 dirty로 간주

### 3.3. 메커니즘 - 스케줄링 시 복제본 사용

- 프로세스가 특정 소켓의 코어에 스케줄링될 때 해당 소켓의 로컬 페이지 테이블 복제본 로드
- CR3 레지스터에 로컬 복제본의 물리 주소 설정
- 프로세스가 다른 소켓으로 마이그레이션될 때 CR3가 자동으로 업데이트됨

### 3.4. 정책 (Policy)

- **복제 정책:** 프로세스가 실행되는 모든 소켓에 페이지 테이블 복제
- **마이그레이션 정책:** OS의 NUMA 스케줄러가 프로세스를 마이그레이션할 때 페이지 테이블도 함께 마이그레이션
- libnuma 사용자 라이브러리 확장을 통해 사용자가 프로세스별로 Mitosis 활성화 제어 가능
- 기본값은 비활성화; 사용자가 명시적으로 선택한 프로세스에만 적용

## 핵심 기여

- **핵심 기여:** 페이지 테이블 배치가 대규모 메모리 NUMA 시스템의 중요한 성능 인자임을 최초로 입증
- **성능 향상:** 멀티소켓 시 최대 1.34x, 마이그레이션 시 최대 3.24x 성능 개선
- **실용성:** 기존 OS 메커니즘(page fault, system call) 위에 구현되어 상용 OS에 적용 가능
- **의의:** 데이터 배치뿐만 아니라 메타데이터(페이지 테이블) 배치의 중요성을 강조하며, 향후 NUMA 시스템 설계에 대한 새로운 관점 제시

## 주요 결과

- Linux 커널 v4.17 기반 x86-64 구현
- Linux PV-Ops 인터페이스를 페이지 테이블로 확장
- 사용자 수준 제어 라이브러리(libnuma 확장) 제공
- 소스 코드: https://github.com/mitosis-project/asplos20-ae
- 하드웨어: 4소켓 Intel Xeon E7-4850v3 (소켓당 14코어, 128GB, 총 512GB) 권장
- 평가 환경: Ubuntu 18.04 LTS, Linux Kernel v4.17

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2020ASPLOS-summarize/mitosis-transparently-self-replicating-page-tables-for-large-memory-machines.md|전체 요약 보기]]
