---
tags: [paper, 2021, 2021ASPLOS, topic/cache, topic/dram, topic/nvm]
venue: "Proceedings of the 26th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '21)"
year: 2021
summary_path: "../paper-summaries/2021ASPLOS-summarize/klocs-kernel-level-object-contexts-for-heterogeneous-memory-systems.md"
---

# KLOCs: Kernel-Level Object Contexts for Heterogeneous Memory Systems

**Venue:** Proceedings of the 26th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '21)
**저자:** Sudarsun Kannan (Rutgers University), Yujie Ren (Rutgers University), Abhishek Bhattacharjee (Yale University)

## 개요

- 이종 메모리 시스템 (Heterogeneous Memory Systems)은 DRAM, die-stacked DRAM, HBM, NVM(Intel Optane) 등 다양한 특성의 메모리 디바이스를 통합하여 성능, 에너지 효율, 비용 트레이드오프를 제공
- 그러나 효율적인 OS 메커니즘과 정책이 부족하여 데이터 계층화(data tiering) 및 마이그레이션에 한계 존재
- 기존 연구는 애플리케이션 데이터의 계층화에 초점, **커널 객체** (인ode, dentry 캐시, 저널 블록, 소켓 버퍼 등)의 관리는 완전히 무시
- 커널 객체는 소수이고 메모리 영향이 적다고 가정했으나, 네트워크/스토리지 속도 향상으로 **커널 객체의 메모리 관리가 성능에 핵심적**
- I/O 집약적 워크로드에서 커널 객체를 무시하면 **최대 4배** 성능 손실 발생
- 기존 OS LRU 메커니즘은 애플리케이션 페이지용으로 설계되어, 커널 객체의 짧은 수명(슬럽: 36ms, 페이지 캐시: 160ms)과 빈번한 할당/해제에 적합하지 않음

## 방법론

### 3.1. 커널 객체 유형 (Table 1)

- 파일 시스템 관련: inode, block I/O, 저널, 페이지 캐시, dentry, extent, blk_mq
- 네트워크 관련: 소켓(sock), 패킷 버퍼(skbuff), 데이터 버퍼(skbuff->data), 수신 드라이버 버퍼(rx_buf)
- 각 활성 파일/소켓마다 하나의 KLOC 존재 (Unix "모든 것은 파일" 원칙 활용)

### 3.2. KLOC 데이터 구조 (Figure 1, 3)

- **knode**: 각 inode에 연결된 메타데이터 구조, 레드-블랙 트리로 관련 커널 객체 추적
  - rbtree-cache: vmalloc/page_alloc으로 할당된 큰 커널 객체 추적
  - rbtree-slab: slab 할당자로 할당된 작은 커널 객체 추적
- **kmap**: 모든 시스템 KLOC의 글로벌 레드-블랙 트리, 모든 knode에 대한 포인터 유지
- **per-CPU 연결 리스트**: 각 CPU가 접근한 knode의 포인터 목록, hot/cold 식용에 활용
  - age 변수: knode 접근 시 0으로 리셋, LRU 스캔 시 증가 → cold 판단 기준
- 메모리 오버헤드: 전체 빠른 메모리 용량의 **<1%**

### 3.3. KLOC 할당 및 관리

- **KLOC 시작**: `begin_kloc()` 시스템 호출로 대상 애플리케이션 지정, 사용자 수준 라이브러리 링크
- **knode 할당**: VFS 레이어에서 slab 할당자 사용 (속도 우선), non-migratable이지만 knode 수가 적어 영향 최소
- **커널 객체 연결**: 파일/소켓 시스템 호출 경로에서 knode의 레드-블랙 트리에 커널 객체 포인터 삽입/삭제
- **네트워크 패킷 처리 과제**: 수신 경로에서 패킷 도착 시 소켓 정보 미확인
  - skbuff 구조체에 8바이트 소켓 필드 추가, 디바이스 드라이버에서 소켓 정보 추출하여 상위 TCP 계층 중복 제거

### 3.4. 동시성 관리

- **RCU(Read-Copy-Update)**: 레드-블랙 트리의 다중 읽기/단일 쓰기 동시성 지원
- **per-CPU 연결 리스트**: 글로벌 kmap의 빠른 경로 캐시로 동기화 오버헤드 감소
  - rbtree-cache/slab 접근 **54%** 감소
- knode의 레드-블랙 트리를 rbtree-cache와 rbtree-slab로 분리하여 잠금 경쟁 감소

## 핵심 기여

- KLOCs는 커널 객체를 체계적으로 관리하는 새로운 OS 추상화로, 이종 메모리 시스템에서 **최대 2.7x** 스루풋 향상
- 기존 Nimble 대비 **1.4-2.7x** 성능 향상, AutoNUMA 대비 **1.5x** 향상
- 커널 객체는 더 이상 무시할 수 없는 성능 요소임을 입증
- 커널 객체의 짧은 수명과 빈번한 할당/해제에 특화된 관리 메커니즘 필요
- **의의**: 파일 시스템 및 네트워크 커널 객체의 계층화를 체계적으로 다룬 최초의 연구, 향후 이종 메모리 관리 연구의 기반 제공

## 주요 결과

### 4.1. LRU/AutoNUMA 정책 확장

- Linux 기존 LRU: 활성/비활성 페이지를 별도 리스트로 추적
- KLOC 확장: knode가 비활성화되면 관련 커널 객체를 즉시 느린 메모리로 마이그레이션 (기존 LRU 스캔 대기 없음)
- 8비트 per-페이지 카운터로 마이그레이션 추적, 반복 마이그레이션 방지 (<1% 페이지가 해당)
- AutoNUMA 확장: 활성 KLOC의 커널 객체가 로컬 메모리에 배치되어 있는지 확인, 원격이면 마이그레이션

### 4.2. I/O 프리페칭 지원

- Linux 적응형 리드어헤드 메커니즘과 통합
- KLOC을 통해 inode와 연결된 커널 객체를 I/O 프리페처에 노출
- 올바른 커널 객체 프리페칭 시 성능 향상, 차가운 객체는 빠르게 느린 메모리로 마이그레이션

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]


## 전체 요약

[[../paper-summaries/2021ASPLOS-summarize/klocs-kernel-level-object-contexts-for-heterogeneous-memory-systems.md|전체 요약 보기]]
