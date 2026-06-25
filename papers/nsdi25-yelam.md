---
tags: [paper, 2025, 2025NSDI, topic/cache, topic/disaggregation, topic/dram, topic/memory-tiering, topic/virtual-memory]
venue: "22nd USENIX Symposium on Networked Systems Design and Implementation (NSDI '25)"
year: 2025
summary_path: "../paper-summaries/2025NSDI-summarize/nsdi25-yelam.md"
---

# Eden: Practical Far-Memory Disaggregation with Hinted Page Faults

**Venue:** 22nd USENIX Symposium on Networked Systems Design and Implementation (NSDI '25)
**저자:** Zhenyuan Ruan (University of Chicago), Malte Schwarzkopf (Brown University), Marcos K. Aguilera, Adam Belay (UC Berkeley)

## 개요

- 데이터센터 애플리케이션의 메모리 수요가 지속적으로 증가하나 DRAM 비용은 크게 감소하지 않아 메모리 스트랜딩(memory stranding) 문제가 심각
- 호스트 인터커넥트의 대역폭과 지연 시간이 개선되면서 far-memory 시스템에 대한 관심이 재점화, 그러나 기존 접근법은 성능, 개발자 노력, 유연성 중 하나 이상의 차원에서 희생을 강요
- **Paging 기반 시스템** (Infiniswap, Fastswap): 하드웨어 가드(페이지 폴트)를 사용하여 원격 메모리 접근을 차단. 페이지 폴트는 커널 레이턴시(약 **17,000 cycles**)를 초래하여 성능 저하 발생
- **App-통합 시스템** (AIFM): 소프트웨어 가드를 사용하여 객체 기반 인터페이스로 far-memory 접근. 높은 프로그래밍 노력 요구, 가드 자체의 오버헤드(최대 **489 cycles**, 90th percentile) 존재
- **컴파일러 기반 시스템** (TrackFM, Mira): 소프트웨어 가드 자동 삽입 시도. TrackFM의 경우 가드가 **14개 명령어**로 구성되고, 최대 **40%** 성능 저하 발생. 외부 라이브러리의 소스 코드 필요, 바이너리 크기 **2.4×** 증가, 컴파일 시간 **6×** 증가
- 기존 시스템들은 애플리케이션별 맞춤 최적화(프리페치, 캐시 분리 등)를 수행하기 어렵거나 개발자 부담이 과도

## 방법론

### 3.1. 힌트 API (Hint API)

- **기본 힌트 (Basic Hints):** 다가올 메모리 주소(또는 영역)와 읽기/쓰기 가능 여부를 런타임에 알림. 페이지 폴트를 방지하는 데 필수적
- **확장 힌트 (Extended Hints):** 애플리케이션별 추가 정보 전달 가능
  - `rdahead`: 힌트 주소 전후로 배치된 페이지 수 지정하여 읽기 선처리(read-ahead) 수행
  - `ev_prio`: 페이지의 eviction 우선순위 지정으로 캐시 분리(cache separation) 지원
  - `seq`: 순차적 접근 패턴 표시로 힌트 오버헤드 감소
- 힌트는 페이지 정렬 불필요, 코드 한 줄당 하나의 힌트 배치

### 3.2. 페이지 관리

- **힌트 경로 (Hinted Path):**
  1. 힌트가 컨트롤을 Eden의 유저스페이스 런타임으로 전환
  2. 런타임이 페이지 존재 여부 확인 (페이지 테이블 기반)
  3. 페이지가 존재하면 즉시 애플리케이션으로 복귀 (커널 진입 없음)
  4. 페이지가 없으면 RDMA read로 far-memory 서버에서 페치
  5. 페치 중 다른 유저스페이스 스레드로 전환하여 CPU 활용 극대화
  6. 페치 완료 후 `UFFDIO_COPY`로 페이지 매핑 및 원래 스레드 재개
  7. 힌트 기반 폴트는 컨텍스트 스위치 **1회** (기존 페이지 폴트의 2회 대비 절반)

- **비힌트 경로 (Unhinted Path):**
  - 힌트가 모든 폴트를 커버하지 못할 경우 전통적 하드웨어 가드(페이지 폴트) 발생
  - 제어 코어(control core)가 `userfaultfd`를 통해 이벤트 수신 및 처리
  - 제어 코어는 애플리케이션 스레드를 실행하지 않으므로 다른 폴트나 메모리 reclaimed 처리 가능

- **동시 폴트 처리:** 페이지 메타데이터에 잠금(lock)을 포함하여 동일 페이지에 대한 동시 폴트를 정확히 한 번만 처리

### 3.3. 페이지 메타데이터

- 각 페이지당 **64비트** 엔트리: 6개 비트 플래그(R: Registered, P: Present, D: Dirty, L: Locked, E: Evicting, A: Accessed), 관리 코어 ID, 페이지 노드 포인터
- Resident 페이지에 추가 **24바이트** 페이지 노드 할당
- 256GB far-memory 지원 시 64GB 로컬 캐시 기준 **약 750MB (~1%)** 메타데이터 오버헤드 (4KB 표준 페이지)

### 3.4. Vectorized Syscalls

- 기존 Linux의 `UFFDIO_WRITEPROTECT`와 `madvise(MADV_DONTNEED)`의 벡터화 변형 도입
- 비연속(non-contiguous) 여러 페이지를 단일 시스템 콜과 TLB 플러시로 동시에 reclaimed
- 기존 대비 유의미한 확장성 개선 달성

## 핵심 기여

- **핵심 기여:** 소수의 코드 위치가 대부분의 페이지 폴트를 결정한다는 통찰을 기반으로 한 하이브리드 소프트웨어/하드웨어 가드 접근법
- **힌트 API:** 기본 힌트(폴트 예측) + 확장 힌트(프리페치, eviction 우선순위, 순차 접근)로 애플리케이션별 맞춤 최적화 지원
- **경량 유저스페이스 스케줄러:** 페이지 페치 중 다른 스레드 실행으로 CPU 활용 극대화 (Memcached에서 **836 KOPS** vs Fastswap **312 KOPS**)
- **Vectorized syscalls:** 비연속 여러 페이지를 단일 시스템 콜로 처리하여 기존 커널 기반 시스템 대비 확장성 개선
- **개발자 노력:** DataFrame 11개, Memcached 2개 힌트로 대부분의 폴트 커버, 수 시간 내 구현 완료
- **성능:** Fastswap 대비 최대 **178%** (Syn Web Service), **104%** (Memcached), **37%** (DataFrame) 성능 향상
- **의의:** AIFM의 높은 성능을 훨씬 적은 프로그래밍 노력으로 달성하는 practical far-memory 시스템을 제시. 객체 기반 시스템의 성능과 paging 기반 시스템의 투명성을 동시에 추구하는 새로운 패러다임 제시

## 주요 결과

- **베이스:** Shenango (유저스페이스 스케줄러, C/C++)
- **추가 코드:** 6,296줄 (LD_PRELOAD 라이브러리, 폴트 처리, 워크 스틸링, 메모리 reclaimed, 페이지 관리)
- **RDMA 네트워크 스택:** 605줄
- **Far-memory RDMA 서버:** 1,304줄
- **페이지 폴트 위치 추적 도구:** 별도 스탠드얼론 도구
- **커널 패치:** vectorized syscalls 지원을 위한 Linux 커널 패치
- **메모리 할당:** jemalloc 사용으로 페이지 크기 배치 할당 용이성 확보
- **지원 far-memory 세그먼트:** 하나 이상의 메모리 서버에서 매핑 가능

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2025NSDI-summarize/nsdi25-yelam.md|전체 요약 보기]]
