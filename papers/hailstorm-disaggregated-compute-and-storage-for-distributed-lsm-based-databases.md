---
tags: [paper, 2020, 2020ASPLOS, topic/disaggregation, topic/storage]
venue: "25th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '20)"
year: 2020
summary_path: "../paper-summaries/2020ASPLOS-summarize/hailstorm-disaggregated-compute-and-storage-for-distributed-lsm-based-databases.md"
---

# Hailstorm: Disaggregated Compute and Storage for Distributed LSM-based Databases

**Venue:** 25th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '20)
**저자:** Laurent Bindschaedler, Ashvin Goel, Willy Zwaenepoel (EPFL, University of Toronto, University of Sydney)

## 개요

- 분산 LSM 기반 데이터베이스(MongoDB, Cassandra, Couchbase 등)가 클라우드 애플리케이션의 표준 스토리지로 자리잡았지만, 두 가지 핵심 문제로 인해 예측 불가능한 성능과 낮은 활용률에 시달림
- **스큐(Skew) 문제:** 워크로드에서 자연스럽게 발생하는 키 분포 불균형. YCSB Zipfian 분포 실험에서 한 노드가 전체 요청의 약 75%를 처리하며 CPU 및 I/O 과부하 발생. MongoDB의 샤드 리밸런서가 25.4GB 데이터를 마이그레이션했으나 skew를 9×에서 5×로만 완화. 마이그레이션이 오히려 추가 compaction을 유발하여 성능 악화 야기 (Figure 3)
- **백그라운드 작업 간섭:** Compaction이 디스크 용량의 최대 스토리지 대역폭(320 MB/s SSD 기준)을 상시 점유. RocksDB 단독 벤치마크(YCSB A)에서 처리량이 평균 22.4 KOps/s에서 최대 0.6 KOps/s까지 떨어짐 (Figure 2). Compaction 시간이 4배 증가(최대 9초)
- **리샤딩의 한계:** MongoDB 리밸런서가 skew 상황에서 효과적이지 않음. 리샤딩 자체가 flush/compaction 오버헤드를 증가시켜 과부하를 악화. YCSB E(Zipfian)에서 스キュ와 compaction이 결합되어 처리량이 1시간 이상 거의 0에 수렴
- 기존 LSM 최적화(PebblesDB, HyperLevelDB 등)는 단일 노드의 리소스만 고려하며, 다른 노드의 여유 리소스를 활용하지 못함

## 방법론

### 3.1. 아키텍처 개요

- 기존 분산 데이터베이스와 동일하게 작동 (데이터베이스 레이어에 Hailstorm 존재를 투명하게 전달)
- 각 스토리지 엔진은 로컬 파일시스템 대신 Hailstorm 파일시스템에 데이터를 영속화
- **표준 POSIX 파일시스템 인터페이스 노출:** 스토리지 엔진에 드롭인 대체 가능. mmap(), fsync() 등 기존 인터페이스 지원
- 파일 레벨 가시성을 통해 sstable 파일을 인식하고 compaction 오프로딩 수행 가능
- 각 클라이언트는 co-located된 데이터베이스 인스턴스의 파일에만 접근 가능 (메타데이터를 로컬 유지)

### 3.2. 스토리지 아키텍처

- **데이터 분산:** 파일을 1MB 블록으로 분할. 의사 난수 순환 매핑 함수 M_F를 사용하여 서버에 균일 분산
  - 파일 F, 블록 크기 B, 서버 수 N에서 offset I의 바이트는 서버 M_F(⌊I/B⌋ mod N)의 블록 ⌊I/B⌋에 위치
  - 데이터 위치가 결정적이므로 클라이언트 간 조율 불필요 → 지연 시간 감소
- **메타데이터 관리:** 파일은 UUID로 식별. 플랫 네임스페이스로 서버에 분산 저장. 클라이언트는 파일 경로-UUID 매핑을 로컬 유지
- **스토리지 로드 밸런싱:**
  - 의사 난수 분산으로 서버 간 불균형 최소화
  - 배치 샘플링(batch sampling) 전략으로 프리페칭: 1MB 블록에 대해 Φ_K=10개 동시 대기 요청, 64KB 블록에 대해 Φ_K=100개 대기
  - 순차 접근(예: compaction 시 sstable 읽기)에서 자동 프리페칭 수행
- **비동기 I/O:** fsync()를 제외한 대부분의 I/O 연산 비동기 처리. fsync()는 스토리지 엔진의 정확한 의미 보장을 위해 블로킹 구현
- **내결성:** 단일 디스크 장애 시 RAID로 완화. 선택적 블록 레벨 primary-backup 복제 지원. 복제본은 다른 랙에 배치하여 동시 장애 방지

### 3.3. Compaction 오프로딩

- **compaction 메커니즘:** 각 클라이언트와 데이터베이스 인스턴스 옆에 경량 에이전트(Agent) 실행. 리소스 사용량 모니터링
  - 로컬 머신이 과부하라고 판단하면 compaction 스레드를 일시 정지(pause)하고 랙 내 다른 노드로 오프로딩
  - 원격 에이전트는 별도의 LSM 스토리지 엔진 프로세스를 생성하여 수동 compaction 실행
  - Compaction은 파일을 제자리에서 수정하지 않으므로 두 에이전트 간 추가 동기화 불필요
  - 완료 후 원격 에이전트가 새로운 sstable 파일 목록과 메타데이터를 원본 노드에 전달
- **과부하 감지:** CPU 사용률, I/O 큐 깊이, compaction 스택 크기를 종합적으로 판단. 임계값 초과 시 오프로딩 트리거

## 핵심 기여

- **핵심 기여:** 분산 LSM 데이터베이스에서 스토리지와 컴퓨트를 분리하는 Hailstorm 시스템 제안. 스토리지 풀링과 compaction 오프로딩의 시너지로 스큐와 I/O 버스트 문제를 근본적으로 해결
- **성능:** MongoDB YCSB 스큐 워크로드에서 평균 60% 처리량 향상, 테일 지연 4~5× 감소, scan 워크로드에서 22× 향상. TiDB TPC-C/TPE-E에서 47~56% 향상
- **의의:** 기존 데이터베이스 레이어의 리샤딩보다 스토리지 레이어의 리소스 분리가 스큐 완화에 더 효과적이라는 실증적 증거 제시. LSM 스토리지 엔진의 compaction 비용을 분산시키는 새로운 패러다임 제시. 표준 POSIX 인터페이스를 통해 기존 시스템과의 호환성 확보
- 향후 연구: 랙 간 스토리지 풀링, 더 정교한 과부하 감지 알고리즘, 다양한 LSM 변형(PebblesDB 등)에서의 검증

## 주요 결과

- **Hailstorm 파일시스템:** ~2,800줄 코드 (Linux FUSE 기반)
- **RocksDB 수정:** Compaction 오프로딩을 위해 ~70줄 코드 변경 (compaction 인터셉트 및 에이전트 호출)
- **원격 compaction 프로세스:** RocksDB를 수정하여 일부 검사를 비활성화 (6줄 주석 처리)
- **블록 크기:** 1MB (쓰기), 64KB (읽기). 100KB~4MB 범위에서 유사한 성능 확인
- **지원 스토리지 엔진:** RocksDB, LevelDB 기반 변형(PebblesDB, HyperLevelDB)
- **지원 데이터베이스:** MongoDB (MongoRocks), TiDB (TiKV)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2020ASPLOS-summarize/hailstorm-disaggregated-compute-and-storage-for-distributed-lsm-based-databases.md|전체 요약 보기]]
