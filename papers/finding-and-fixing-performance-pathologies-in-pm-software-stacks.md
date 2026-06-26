---
tags: [paper, 2019, 2019ASPLOS, topic/nvm]
venue: "24th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '19)"
year: 2019
summary_path: "../paper-summaries/2019ASPLOS-summarize/finding-and-fixing-performance-pathologies-in-persistent-memory-software-stacks.md"
---

# Finding and Fixing Performance Pathologies in Persistent Memory Software Stacks

**Venue:** 24th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '19)
**저자:** Jian Xu, Juno Kim, Amirsaman Memaripour, Steven Swanson (Google, University of California San Diego)

## 개요

- NVMM (Non-Volatile Main Memory)은 CPU 메모리 버스에 직접 연결되는 고속 비휘발성 메모리로, IO 집약적 애플리케이션에 상당한 성능 향상을 약속하지만, 기존 스토리지 소프트웨어 스택의 설계 원칙과 근본적으로 상충
- 기존 NVMM 파일 시스템 연구(NOVA, PMFS, Strata 등)는 상당한 성능 향상을 보여주었으나, 레거시 애플리케이션이 NVMM을 효과적으로 활용하는 방법과 파일 시스템이 이를 어떻게 지원해야 하는지에 대한 중요한 질문이 남아 있음
- 기존 블록 기반 파일 시스템(ext4-DAX, xfs-DAX)은 NVMM에 적응시키기 위해 DAX를 추가했으나, 메타데이터 업데이트는 여전히 레거시 블록 기반 저널링 메커니즘을 사용하여 성능 병목을 유발
- 현대 시스템의 다중 소켓, 다중 코어 구조에서 NUMA 효과가 NVMM 파일 시스템 성능에 심각한 영향을 미침
- 핵심 질문: (1) 레거시 애플리케이션을 NVMM으로 전환하는 데 얼마나 많은 노력이 필요한가? (2) 정교한 NVMM 기반 데이터 구조가 반드시 필요한가? (3) 기존 파일 시스템이 NVMM을 얼마나 효율적으로 지원하는가? (4) 확장성은?

## 방법론

### 3.1. FLEX 메커니즘

- 애플리케이션에서 파일을 DAX-mmap으로 주소 공간에 매핑한 후, `write()`/`read()` 시스템 콜 대신 사용자 공간 연산으로 대체
- **FLEX 쓰기 과정:**
  - 파일 확장이 필요한 경우 `fallocate()`로 사전 할당 후 `mmap()`/`mremap()`으로 매핑 확장
  - non-temporal store와 `clwb` 명령어로 데이터를 NVMM에 안정적으로 기록
  - 동기적 쓰기 필요 시 `sfence` 명령어로 저장 완료 보장
- **FLEX 읽기:** `memcpy()`로 단순 변환
- FLEX는 엄격한 POSIX 원자성을 보장하지 않으나, 연구 대상 애플리케이션(SQLite, RocksDB, Kyoto Cabinet)은write 원자성을 가정하지 않음

### 3.2. FLEX 성능 분석 (Figure 5)

| 접근 패턴 | FLEX vs POSIX 성능 향상 |
|-----------|----------------------|
| **Append and extend** | 최대 61× |
| **Circular append** | 최대 11× |
| **4KB 페이지 사용 시** | 4KB 미만 전송에서만 성능 향상 |
| **2MB 페이지 사용 시** | 넓은 범위에서 성능 향상 |

- 작은 쓰기에서 성능 이점이 특히 큼 (RocksDB, SQLite, Kyoto Cabinet의 공통 패턴)
- `fallocate()` 크기가 클수록 할당 오버헤드 경감으로 성능 향상

### 3.3. 애플리케이션별 적용 결과

**SQLite (Figure 1):**
- PERSIST 저널링 모드 + FLEX 적용: ext4-DAX 대비 2.5~2.8× 성능 향상
- WAL 모드에서 `fallocate()` 사전 할당으로 파일 시스템 간 성능 격차 해소
- 코드 변경: 266줄

**Kyoto Cabinet (Figure 2a):**
- FLEX write + clwb + falloc + mremap 적용 시 NOVA 대비 7~25× 성능 향상
- `msync()` 대신 사용자 공간 clwb로 NOVA 3.4×, ext4-DAX 7.2×, xfs-DAX 7.7× 향상
- 코드 변경: 181줄

**LMDB (Figure 2b):**
- clwb로 msync 대체 시 11~14× throughput 향상
- ext4-DAX가 2MB 슈퍼페이지 mmap 지원으로 xfs-DAX, NOVA 대비 11% 우수
- 코드 변경: 101줄

**Redis (Figure 3):**
- P-Redis (PMDK 기반 영속 해시테이블): AOF 동기 쓰기 대비 27%~2.6× 향상
- AOF 비활성화 대비 약 9% 성능 하락으로 높은 영속성 효율
- 코드 변경: 1,526줄 (가장 큰 노력)

**RocksDB (Figure 4):**
- FLEX 적용: 2.2~18.7× 성능 향상
- 영속 스킵리스트 적용 시 추가 19% 향상 (총 11× vs baseline)
- 코드 변경: 56줄 (FLEX) + 380줄 (영속 스킵리스트)

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1. ext4 저널링 병목 분석

- 기존 JBD2: 4KB 페이지 전체 기록, 개별 메타데이터 변경 시에도 전체 페이지 쓰기 필요
- 트랜잭션당 최대 8개 저널 페이지 기록 (헤더, 커밋 블록, inode, inode 비트맵, 할당자 등)
- JBD2는 저널링된 연산 간 동시성 미지원 → 멀티스레드 확장성 병목

### 4.2. JDD 개선 사항

- 개별 메타데이터 필드 단위 저널링 (전체 페이지 대신)
- pre-allocated per-CPU 저널링 영역으로 병렬 처리 지원
- undo 로깅: 이전 값을 저널에 복사하고 NVMM의 메타데이터 구조에 직접 업데이트
- 커밋 시 저널을 invalid로 표시 (경량 커밋)
- 복구 시 저널된 데이터로 부분 업데이트 롤백

### 4.3. JDD 성능 (Figure 6)

| 벤치마크 | JDD 성능 향상 |
|---------|-------------|
| 마이크로벤치마크 (4KB random write + fsync) | 3.7× |
| Filebench Varmail | 40% |
| SQLite WAL | 11% |
| Redis | 11%~2.6× |
| RocksDB | 18.7× |

- 지연 시간 분석 (Figure 7): ext4-DAX에서 JBD2 커밋이 전체 지연의 50% 차지 → JDD가 이를 제거

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]


## 전체 요약

[[../paper-summaries/2019ASPLOS-summarize/finding-and-fixing-performance-pathologies-in-persistent-memory-software-stacks.md|전체 요약 보기]]
