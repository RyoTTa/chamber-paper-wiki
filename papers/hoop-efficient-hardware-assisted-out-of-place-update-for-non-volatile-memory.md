---
tags: [paper, 2020, 2020ISCA, topic/cache, topic/dram, topic/nvm, topic/virtual-memory]
venue: "2020 ACM/IEEE 47th Annual International Symposium on Computer Architecture (ISCA '20)"
year: 2020
summary_path: "../paper-summaries/2020ISCA-summarize/hoop-efficient-hardware-assisted-out-of-place-update-for-non-volatile-memory.md"
---

# HOOP: Efficient Hardware-Assisted Out-of-Place Update for Non-Volatile Memory

**Venue:** 2020 ACM/IEEE 47th Annual International Symposium on Computer Architecture (ISCA '20)
**저자:** Miao Cai (Nanjing University), Chance C. Coats (University of Illinois at Urbana-Champaign), Jian Huang (University of Illinois at Urbana-Champaign)

## 개요

- NVM (Non-Volatile Memory, 비휘발성 메모리)은 DRAM에 근접하는 성능과 확장 가능한 메모리 용량을 제공하는 차세대 메모리 기술이나, 시스템 장애 시 데이터의 원자적 지속성(atomic durability)이 필요
- 기존 크래시 컨시스턴시(crash-consistency) 기법의 핵심 문제:
  - **로깅(logging):** undo/redo 로깅 모두 데이터 업데이트 전 사본을 유지해야 하므로 NVM에 쓰기 증폭(write amplification) 발생 → NVM 수명 단축 및 성능 저하
  - **섀도우 페이징(shadow paging):** 페이지 단위 복사로 인한 높은 쓰기 증폭, TLB 수정 필요
  - **로그 구조화 NVM (LSNVMM):** 소프트웨어 기반 인덱스 트리로 인한 O(logN) 메모리 접근으로 읽기 지연 시간 증가
- 크래시 컨시스턴시 기법은 NVM의 추가 쓰기 트래픽(최대 2.1×)을 유발하거나, 프로그램 실행의 크리티컬 패스(critical path)에서 상당한 성능 오버헤드를 초래하거나, 또는 그 둘 다를 동시에 발생
- 특히 커머셜 비순차(out-of-order) 프로세서와 하드웨어 제어 캐시 계층에서 메모리 지속성을 보장하는 것은 예측 불가능한 캐시 퇴출(eviction)로 인해 어렵고 비용이 높음

## 방법론

### 3.1. 메모리 컨트롤러 내 간접 계층 (Indirection Layer)

- **OOP 데이터 버퍼:** 각 코어당 1KB 전용 버퍼, 동시 트랜잭션 실행 시 접근 경합 방지
  - 워드(word) 단위로 데이터 업데이트를 추적 (캐시 라인 granularity 아님)
  - 데이터 패킹(data packing) 적용: 여러 독립 캐시 라인의 데이터를 하나의 메모리 슬라이스에 압축
  - 최대 8개의 8바이트 워드 데이터 + 64바이트 메타데이터를 하나의 128바이트 메모리 슬라이스에 패킹
- **해시 기반 주소 매핑 테이블:**
  - 물리 주소 → 물리 주소 매핑 (physical-to-physical address mapping)
  - 기본 256KB/코어 (총 2MB), 해시 테이블로 O(1) 주소 변환
  - 캐시 라인이 OOP 영역에 기록되면 매핑 테이블에 엔트리 추가
  - GC 또는 LLC miss 시 엔트리 제거
- **퇴출 버퍼 (Eviction Buffer):** 128KB, GC 중 NVM으로 퇴출된 캐시 라인과 홈 영역 주소 저장
- **지속성 순서 Persistence Ordering:**
  - 메모리 컨트롤러 내에서 지속성 순서를 관리 → 프로그래머가 명시적으로 cache-line flush나 memory barrier 명령어를 실행할 필요 없음
  - 트랜잭션 종료(Txend) 시 OOP 데이터 버퍼에서 남은 메모리 슬라이스를 OOP 영역에 flush

### 3.2. OOP 영역 구성 (OOP Region Organization)

- OOP 영역은 로그 구조(log-structured) 방식으로 구성되어 단편화 최소화 및 순차 쓰기를 통한 높은 처리량 달성
- **OOP 블록:** 2MB 크기, 128바이트 고정 크기 메모리 슬라이스로 구성
- **블록 인덱스 테이블:** 각 OOP 블록의 인덱스 번호와 시작 주소 저장, 메모리 컨트롤러에 캐싱
- **메모리 슬라이스 유형:**
  - **데이터 메모리 슬라이스:** 8개 8바이트 워드 데이터 + 64바이트 메타데이터 (홈 영역 주소, 트랜잭션 ID, 다음 슬라이스 주소 오프셋 등)
  - **주소 메모리 슬라이스:** 커밋된 트랜잭션의 시작 주소 저장, GC가 OOP 블록에서 커밋된 트랜잭션을 빠르게 식별

### 3.3. 가비지 컬렉션 및 데이터 병합 (GC & Data Coalescing)

- **GC 알고리즘 (Algorithm 1):**
  1. OOP 블록 내 주소 메모리 슬라이스를 역순으로 스캔 (최신 커밋된 트랜잭션 우선)
  2. 동일한 홈 영역 주소의 업데이트를 데이터 병합(data coalescing)으로 통합 → 동일 위치에 여러 번 쓰는 것 방지
  3. 해시 맵 H에 최신 업데이트만 유지
  4. 홈 영역으로 데이터 마이그레이션, 매핑 테이블에서 해당 엔트리 제거
- **데이터 병합 효과 (Table IV):**
  - 트랜잭션 수 10^4개 시 85% 이상의 데이터를 홈 영역에 다시 쓸 필요 없음
  - 데이터 로컬리티 활용으로 쓰기 트래픽 대폭 감소
- **크래시 안전성:** GC 중 시스템 크래시 발생 시 OOP 영역의 커밋된 트랜잭션을 통해 데이터 복구 가능

### 3.4. 데이터 복구 (Data Recovery)

- 시스템 크래시 후 OS가 여러 복구 스레드를 생성
- 각 복구 스레드가 OOP 블록을 주소 공간에 매핑(kmap)
- 커밋된 주소 메모리 슬라이스를 읽어 커밋 순서대로 정렬
- 복구 스레드에 round-robin 방식으로 분배 → 병렬 처리로 빠른 복구
- 마스터 스레드가 로컬 해시 집합을 글로벌 해시로 통합, 최신 버전만 유지
- NVM 대역폭 25GB/s 시 1GB OOP 영역 복구에 47ms 소요 (2.3× 가속)

## 핵심 기여

- **핵심 기여:** NVM 크래시 컨시스턴시를 위한 최초의 메모리 컨트롤러 기반 하드웨어 오프플레이스 업데이트 기법
- **성능 향상:** 기존 최신 기법 대비 최대 1.7× 높은 처리량, 2.1× 낮은 쓰기 증폭
- **실용성:** 메모리 컨트롤러 내 경량 하드웨어 수정 (면적 오버헤드 4.25%)으로 소프트웨어에 투명
- **연구 방향:** 다중 메모리 컨트롤러 지원(2-Phase Commit), 매핑 테이블 압축을 통한 추가 최적화 가능성
- **의의:** 로깅과 섀도우 페이징의 본질적 한계를 극복하는 새로운 패러다임으로, NVM 기반 시스템의 실용화에 기여

## 주요 결과

- **구현 환경:** McSimA+ (Pin 기반 다중코어 시뮬레이터) + NVM 시뮬레이터
- **시스템 구성:**
  - 프로세서: 2.5GHz 순수외부(x86) 16코어
  - L1 I/D 캐시: 32KB, 4-way; L2: 256KB, 8-way; LLC: 2MB, 16-way
  - NVM: 읽기/쓰기 50ns/150ns, 512GB 용량
- **하드웨어 오버헤드:**
  - 매핑 테이블 2MB + OOP 데이터 버퍼 1KB/코어 + 퇴출 버퍼 128KB
  - 캐시 라인당 1 persistent bit 추가
  - CACTI 6.5 기반 면적 오버헤드: 4.25%
- **소프트웨어 인터페이스:** Txbegin/Txend 트랜잭션 인터페이스 제공, 동시성 제어는 프로그래머에게 유연하게 위임

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2020ISCA-summarize/hoop-efficient-hardware-assisted-out-of-place-update-for-non-volatile-memory.md|전체 요약 보기]]
