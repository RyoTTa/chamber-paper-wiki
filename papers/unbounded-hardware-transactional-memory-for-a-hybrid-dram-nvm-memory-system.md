---
tags: [paper, 2020, 2020MICRO, topic/cache, topic/dram, topic/nvm]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO) 2020"
year: 2020
summary_path: "../paper-summaries/2020MICRO-summarize/unbounded-hardware-transactional-memory-for-a-hybrid-dram-nvm-memory-system.md"
---

# Unbounded Hardware Transactional Memory for a Hybrid DRAM/NVM Memory System

**Venue:** IEEE/ACM International Symposium on Microarchitecture (MICRO) 2020
**저자:** Jungi Jeong, Jaewan Hong, Seungryul Maeng, Changhee Jung, Youngjin Kwon (Purdue University, KAIST)

## 개요

- NVM(Non-Volatile Memory) 기반 영속 메모리 프로그래밍은 failure atomicity를 요구하지만, 기존 하드웨어 트랜잭셔널 메모리(HTM)는 트랜잭션 크기를 온칩 캐시 경계로 제한하여 capcity overflow 문제 발생
- LLC-bounded HTM은 트랜잭션 footprint가 캐시 크기를 초과하면 반복적으로 abort하여 최대 6.2x 성능 저하 발생 (Section III-C)
- 기존 unbounded HTM 제안들(LogTM, LTM, VTM, Bulk, LogTM-SE)은 비현실적 하드웨어 가정 또는 99% 이상의 false positive rate로 인해 실용적이지 않음
- DRAM과 NVM이 혼합된 하이브리드 메모리 시스템에서 HTM이 두 메모리 유형 간 상호작용을 지원한 사례가 없으며, 최신 persistency 모델(AutoPersist, Go-pmem)의 요구사항을 충족하지 못함
- 장시간 실행되는 읽기 전용 트랜잭션(long-running read-only transactions)은 1% 미만의 빈도로 발생하지만, capcity overflow로 인해 전체 처리량을 크게 저하시킴

## 방법론

### 3.1. 단계적 충돌 감지 (Staged Conflict Detection)

- 온칩 캐시: 디렉토리 기반 cache coherence 프로토콜 확장
  - 디렉토리 엔트리에 Tx-bit, Tx-Owner, Tx-Sharer 필드 추가
  - Tx-Owner/Tx-Sharer에 core ID 대신 transaction ID를 저장하여 context switch 지원
  - GetM 요청 시 Tx-Sharer 존재 → read-after-write conflict, Tx-Owner 존재 → write-after-write conflict
- 오프칩 메모리: HW bloom 필터 기반 address signature 사용
  - LLC-missed 요청의 주소만 signature와 대조하여 false positive 대폭 감소 (99% → 26%)
  - 기존 방식(L1-cached coherence traffic 확인) 대비 대폭 개선

### 3.2. 시그니처 격리 최적화

- 충돌 도메인(conflict domain): 서로 충돌할 수 있는 트랜잭션 그룹 정의
- pthread 라이브러리를 수정하여 프로세스 내 스레드에 transaction group ID 부여
- LLC-missed 요청을 동일 충돌 도메인의 시그니처와만 대조하여 false positive 추가 감소 (26% → 9%)
- 서로 다른 프로세스 간 불필요한 abort 방지

### 3.3. 하이브리드 로깅 (Hybrid Logging)

- **DRAM 데이터 (undo logging):**
  - 온칩 캐시에서 eager version management 적용 (overwrite 시 old version을 DRAM에 flush)
  - LLC에서 eviction될 때 memory controller가 old value를 log에 비동기적으로 복사
  - 커밋 시 commit mark만 log에 기록하면 즉시 완료 → 빠른 커밋
  - redo 대비 읽기 지연(read-indirection) 문제 없음
- **NVM 데이터 (redo logging):**
  - 기존 hw-assisted logging 기반 (Jeong et al. 2018)
  - 수정된 cache block을 DRAM cache에 flush하고 NVM log에 new value 저장
  - DRAM cache가 NVM log 검색을 빠른 DRAM 검색으로 대체

### 3.4. 커밋 및 abort 프로토콜

- **커밋:** DRAM과 NVM의 커밋을 병렬로 수행
  - DRAM: commit mark를 log에 기록하여 완료
  - NVM: redo-log가 NVM에 durable된 후 DRAM cache에서 in-place 업데이트
- **Abort:**
  - 온칩 상태: 수정된 cache block invalidate
  - DRAM: undo log에서 old value를 in-place 위치로 복원
  - NVM: DRAM cache에서 uncommitted block invalidate, NVM log 삭제는 background에서 처리
- Transaction Status Structure (TSS)로 모든 실행 중 트랜잭션 상태 추적
- Conflict resolution: on-chip은 requester-wins, off-chip은 requester-loses 정책 적용

### 3.5. 컨텍스트 스위치 처리

- Transaction ID가 core ID 대신 사용되어 컨텍스트 스위치 후에도 정확한 충돌 감지 보장
- 컨텍스트 스위치 시 private cache의 수정된 데이터를 LLC로 flush
- 중단된 스레드의 트랜잭션은 TSS에서 abortion flag 확인 후 재시작

## 핵심 기여

- UHTM은 DRAM/NVM 하이브리드 메모리 시스템을 위한 최초의 unbounded HTM으로, staged conflict detection과 hybrid logging을 통해 실용성 달성
- Address signature의 false positive rate를 99%에서 9%로 대폭 감소시켜 unbounded HTM의 실용성을 입증
- LLC-Bounded HTM 대비 평균 56%, 최대 818% 성능 향상으로 capcity overflow 문제 해결
- DRAM과 NVM 데이터를 동일 트랜잭션에서 처리할 수 있는 최초의 설계로 최신 persistency 모델 지원
- 컨텍스트 스위치, 멀티 프로세스 환경에서도 정확한 충돌 감지 보장

## 주요 결과

- gem5 시뮬레이터의 system-call emulation mode 사용
- 16코어 인오더 프로세서, 2GHz, 2단계 캐시 계층
- L1 I/D: 32KB, 8-way (1.5ns), LLC: 16MB, 16-way (15ns)
- DRAM: 82ns, NVM: 읽기 175ns, 쓰기 94ns (ADR로 쓰기 지속성 보장)
- Intel PMDK 라이브러리의 micro-benchmark (HashMap, B-Tree, RB-Tree, SkipList) 및 자체 개발 hybrid KV-store 사용
- 하드웨어 오버헤드: 디렉토리 엔트리 확장, transaction ID 레지스터, TSS, overflow list, DRAM cache, 주소 signature 배열

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]


## 전체 요약

[[../paper-summaries/2020MICRO-summarize/unbounded-hardware-transactional-memory-for-a-hybrid-dram-nvm-memory-system.md|전체 요약 보기]]
