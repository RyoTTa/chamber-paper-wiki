---
tags: [paper, 2019, 2019MICRO, topic/cache, topic/dram, topic/nvm, topic/storage, topic/virtual-memory]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO) 2019"
year: 2019
summary_path: "../paper-summaries/2019MICRO-summarize/ssp-eliminating-redundant-writes-in-failure-atomic-nvrams-via-shadow-sub-paging.md"
---

# SSP: Eliminating Redundant Writes in Failure-Atomic NVRAMs via Shadow Sub-Paging

**Venue:** IEEE/ACM International Symposium on Microarchitecture (MICRO) 2019
**저자:** Yuanjiang Ni (UC Santa Cruz), Jishen Zhao (UC San Diego), Heiner Litz (UC Santa Cruz), Daniel Bittman (UC Santa Cruz), Ethan L. Miller (UC Santa Cruz, Pure Storage)

## 개요

- NVRAM(Phase-Change Memory, memristor, Intel Optane DC)은 DRAM 수준의 성능과 디스크 수준의 지속성을 제공하여 새로운 storage tier로 부상하고 있으나, 비정상 종료 후 일관성(consistency) 유지가 주요 과제
- 기존 failure-atomicity 기법들의 핵심 문제: **"write twice" 문제** — 데이터 무결성을 보장하기 위해 동일 데이터를 NVRAM에 두 번 작성해야 함
  - Write-ahead logging: 로그 영역에 먼저 쓰고, 실제 데이터 영역에 다시 씀 → NVRAM write 트래픽 최대 2배 증가
  - Log-structuring (LSNVMM): 매핑 테이블 오버헤드가 크고, large block mapping으로 인한 fragmentaion 및 garbage collection 비용 발생
  - Shadow paging (SCSP/BPFS): entire page 단위 CoW → byte-granularity 접근에 비효율적 (작은 업데이트 시에도 전체 페이지 복사 필요)
- NVRAM의 제한된 write endurance(내구성) 관점에서, redundant writes는 수명을 크게 저하시킴
- 기존 하드웨어 지원 기법(ATOM, Proteus, DHTM)도 log update 또는 redundant write를 critical path에서 제거하지 못함

**Table 1 비교 (논문 내):**
| 기법 | 낮은 Extra Writes | 낮은 Persistence Overhead | 낮은 Instruction Overhead |
|------|-------------------|--------------------------|--------------------------|
| Software redo/undo logging | ✕ | ✕ | ✕ |
| ATOM, Proteus | ✕ | ✕ | ✔ |
| DHTM | ✕ | ✔ | ✔ |
| LSNVMM | ✔ | ✔ | ✕ |
| SSP | ✔ | ✔ | ✔ |

## 방법론

### 3.1. Shadow Sub-Paging 기본 개념

- 각 active virtual page에 대해 두 개의 물리 페이지(P0, P1)를 연결
- 3개 bitmap (각 cache line당 1비트):
  - **Current bit:** 최신 버전이 P0인지 P1인지 정의
  - **Updated bit:** 해당 캐시 라인이 현재 트랜잭션에서 기록되었는지 추적 (write set)
  - **Committed bit:** 커밋된(안전한) 버전이 P0인지 P1인지 정의 (NVRAM에 영구 저장)
- **Atomic update 과정 (Figure 4):**
  1. Current bit를 확인하여 기록 대상 페이지 결정
  2. 데이터를 캐시로 로드 (없으면 로드)
  3. 캐시 라인 태그를 변경하여 "다른" 페이지에 매핑
  4. 새 데이터로 캐시 업데이트
  5. Current bit 뒤집기
  - 기록된 캐시 라인은 언제든 캐시에서 제거해도 커밋된 데이터를 덮어쓰지 않음 (safe eviction)

### 3.2. Metadata Journaling

- multi-page 트랜잭션 커밋 시 여러 committed bitmap을 원자적으로 업데이트해야 함
- **메타데이터 저널링** (data가 아닌 SSP 메타데이터만 대상으로 하는 redo logging):
  - 각 메타데이터 업데이트 시 NVRAM에 log entry 추가 (page ID + committed bitmap, 128 bits/page)
  - 메타 로그를 먼저 NVRAM에 영속화한 후 실제 committed bitmap 업데이트
  - 기존 data journaling(64 Byte/block) 대비 훨씬 가벼움

### 3.3. Page Consolidation

- 각 virtual page가 두 물리 페이지를 가지므로 2× 용량 오버헤드 발생 → 이를 해결하기 위한 메커니즘
- **비활성 페이지 감지:** TLB에서 해당 virtual page가 evicted되면 inactive로 판단
- **consolidation 과정:**
  - 두 물리 페이지 중 valid cache line이 적은 쪽을 다른 쪽으로 복사 (최소 데이터 이동)
  - committed bitmap에서 '0' 또는 '1' 개수로 각 페이지의 valid cache line 수 계산 가능
  - Virtual-to-physical 매핑 테이블 업데이트
- Eagerness: 현재 즉시(eagerly) consolidation 수행, 향후 lazy consolidation 연구 예정
- **Page consolidation이 유일한 redundant write 발생 지점** → 트랜잭션 수 대비 TLB eviction 수가 적어 전체 write 트래픽 대폭 감소

### 3.4. 하드웨어 아키텍처 확장

- **TLB 확장:** 두 번째 물리 페이지 번호(PPN1), current bitmap, updated bitmap을 TLB entry에 추가
  - Thread별 private updated bitmap (write set 격리)
  - 모든 thread가 공유하는 current bitmap (shared memory 일관성)
  - Per-page committed bitmap은 NVRAM에 영구 저장
- **CPU Core 확장:** cache line 태그에 1비트 TX 비트 추가 → 트랜잭션에서 수정된 라인 식별
- **Memory Controller 확장:** SSP cache 관리, metadata journaling, page consolidation 수행
- TLB shootdown 대신 page-overlays 방식 활용 (cache coherence protocol 기반)

### 3.5. 제약 사항 및 Fall-back

- 트랜잭션이 사용 가능한 TLB entry보다 많은 페이지를 갱신해야 하는 경우: transaction abort → software fall-back (unbounded redo/undo logging)
- 현재 4KB base page만 지원 (superpage는 auto-demote/promote로 향후 확장 가능)
- Virtually-indexed cache와도 호환 가능

## 핵심 기여

- SSP는 NVRAM에서 failure-atomicity를 보장하면서 **redundant writes를 거의 완전히 제거**하는 최초의 기법
- cache-line granularity remapping + metadata journaling + page consolidation의 조합으로 logging 기반 기법 대비 최대 1.8× write 감소, 1.6× throughput 향상
- NVRAM의 write endurance 문제를 완화하고, byte-addressable persistent memory의 실용성을 높이는 중요한 기여
- 향후 work: superpage 지원, lazy consolidation, hardware transactional memory와의 통합

## 주요 결과

- 구현 언어: Not specified (하드웨어 아키텍처 제안)
- 프로토타입: FPGA 기반 구현 또는 시뮬레이터 사용 (Section 5에서 평가)
- 프로그래밍 모델: Mnemosyne의 `atomic{...}` 구문 사용, ISA 확장 (`ATOMIC_BEGIN`, `ATOMIC_END`, `ATOMIC_STORE` 명령어 추가)
- 하드웨어 변경 범위: TLB, Memory Controller, CPU Core 태그 확장

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2019MICRO-summarize/ssp-eliminating-redundant-writes-in-failure-atomic-nvrams-via-shadow-sub-paging.md|전체 요약 보기]]
