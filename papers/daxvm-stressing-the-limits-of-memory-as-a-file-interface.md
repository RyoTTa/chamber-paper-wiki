---
tags: [paper, 2022, 2022MICRO, topic/cache, topic/dram, topic/nvm, topic/storage, topic/virtual-memory]
venue: "MICRO 2022 (55th IEEE/ACM International Symposium on Microarchitecture)"
year: 2022
summary_path: "../paper-summaries/2022MICRO-summarize/daxvm-stressing-the-limits-of-memory-as-a-file-interface.md"
---

# DaxVM: Stressing the Limits of Memory as a File Interface

**Venue:** MICRO 2022 (55th IEEE/ACM International Symposium on Microarchitecture)
**저자:** Chloe Alverti, Vasileios Karakostas, Nikhita Kunati, Georgios Goumas, Michael Swift (National Technical University of Athens / University of Athens / NVIDIA / University of Wisconsin-Madison)

## 개요

- Persistent Memory(PMem)은 프로세서 메모리 버스에 연결된 저지연 바이트 주소 가능 스토리지이나, DAX-mmap 인터페이스의 성능이 **가상 메모리 작업(paging)으로 인해 크게 제한**됨
- Linux는 모든 파일 매핑을 DRAM 가정 하에 **게으른(lazy) 방식**으로 페이지 폴트 기반으로 PTE 생성 → PMem에서는 불필요한 오버헤드
- small 파일 접근 시 mmap이 read system call보다 **최대 30% 느림** (Fig. 1a): paging 비용이 데이터 복사 제거 이점을 상쇄
- 멀티 코어 확장성 부족: 32KB 파일에 대한 mmap 처리량이 **4코어 이후 확장 불가** (Fig. 1b)
- 가상 주소 공간 관리의 **mmap semaphore 직렬화** 문제: 동시 m(un)map 요청 시 심각한 락 경쟁
- 동기화 munmap에서 TLB shootdown이 **수천 사이클** 소요, IPI 기반으로 비확장적
- MM append 시 보안상 블록 0-initialization 필요 → **쓰기 비용 2배** (30-40% 지연 시간 증가)
- 커널 space dirty page tracking이 사용자 공간에서 내구성을 관리하는 애플리케이션에도 **불필요한 오버헤드** 강제

## 방법론

### 3.1. O(1) mmap - File Tables (Fig. 2)

**사전 구성된 File Tables:**
- 파일 시스템이 파일 오프셋→PMem 물리 주소 변환을 담당하는 x86-64 페이지 테이블 조각을 유지
- 하위(bottom-up) 방식으로 4KB 페이지 단위 PTE를 구성 → 작은 파일의 경우 단일 4KB PTE 페이지로 충분
- 큰 파일의 경우 huge PMD 엔트리 지원 (2MB/1GB 정렬)

**동작 방식:**
1. mmap 호출 시 file table의 관련 조각을 프로세스의 비공개 페이지 테이블에 첨부
2. PMD 레벨에서 내부 포인터 갱신 → **O(1) 상수 시간** 동작
3. 매핑 크기는 2MB(PMD) 또는 1GB(PUD) 단위로 자동 라운딩

**동적 관리:**
- 작은 파일(<32KB): volatile file tables (VFS inode 캐시 기반)
- 큰 파일(≥32KB): persistent file tables (PMem에 저장, 전원 유지)
- MMU 성능 모니터링: 평균 page walk 레이턴시 > 200cycles且 MMU 오버헤드 > 5%일 때 PMem→DRAM 마이그레이션

**PTE 상태 비트 최적화:**
- access bit, dirty bit 유지 불필요 (PMem은 page cache 관리 불필요)
- 권한 비트는 attachment 레벨(PMD)에서 관리 → 프로세스별 접근 제어 가능

### 3.2. Ephemeral Mapping 관리 (Fig. 3)

**Ephemeral Heap:**
- 프로세스 주소 공간에 사전 할당된 가상 주소 영역 (1GB 단위 동적 확장)
- linear 할당 방식 (스택 유사), 재사용 시점: 해당 1GB 영역의 모든 매핑이 파괴될 때
- 오직 munmap만 허용, mprotect/mremap 등 복잡한 연산 지원하지 않음

**경량 잠금:**
- ephemeral VMA는 VMA red-black tree에 기록되지 않고 전용 리스트(또는 트리)로 관리
- mmap semaphore를 reader로만 획득 + 전용 spinlock 사용 → 멀티 코어 확장성 확보
- volatile 메모리 관리 관련 코드 경로(set A), 페이지 폴트(set B), 메모리 연산(set C) 모두 불필요

### 3.3. 비동기 munmap 최적화

**배치 처리:**
- "zombie" VMA를 기록하고 비동기적으로 배치 해제
- 임계값(기본 33페이지) 도달 시 전체 TLB flush 1회 수행 → 개별 shootdown 대체
- 가상 메모리 락 보유 시간 단축

**파일 시스템 레이스 대응:**
- 매핑 해제 지연 중 파일 truncate/delete 시 storage block 회수 전제 조건으로 동기적 해제 강제

### 3.4. 내구성 관리 (Durability Management)

**커널 공간 dirty-page tracking 우회:**
- 기본 DAX-mmap: permission fault 기반으로 더티 페이지 추적 (2MB granularities)
- DaxVM nosync 모드: 모든 커널 수준 더티 추적 비활성화, msync no-op 처리
- 사용자 공간에서 non-temporal store/clwb+sfence로 직접 내구성 관리 지원

**동기화 성능:**
- 커널 공간 sync: DAX write syscall 대비 최대 68% 느림 (non-temporal store의 대역폭 이점 활용 불가)
- DaxVM + nosync: 기본 MM 대비 최대 80% 성능 향상

### 3.5. 비동기 블록 Pre-zeroing

- 파일 truncate 시 해제 블록을 즉시 할당 해제하지 않고 **per-core 리스트에 보관**
- 전용 커널 스레드가 non-temporal store로 블록을 비동기 0-초기화
- 대역폭 제한(rate-limited)으로 동시 작업과의 경쟁 방지
- 성능 효과: MM append 지연 시간의 **30-40% 절감**

### 3.6. DaxVM 인터페이스

**새로운 시스템 콜:**
- `daxvm_mmap`: O(1) file table 첨부, 공유 매핑 지원
- `daxvm_munmap`: 매핑 해제

**새로운 플래그:**
| 플래그 | 설명 |
|--------|------|
| MAP_EPHEMERAL | 짧은 수명 매핑, ephemeral heap 활성화 |
| MAP_UNMAP_ASYNC | 비동기 munmap 활성화 |
| MAP_NO_MSYNC | dirty-page tracking 완전 차단, msync no-op |

**POSIX 제한 해제:**
- 부분 mprotect/mremap 실패 (전체 매핑 단위만 지원)
- madvise 미지원 (volatile 메모리 관리용)
- 매핑 크기는 요청보다 클 수 있음 (정렬 요구사항)

## 핵심 기여

1. **O(1) mmap으로 paging 비용 완전 제거:** 파일 시스템 사전 구성 file table을 프로세스 주소 공간에 첨부하는 방식으로, 파일 크기에 무관한 상수 시간 매핑 달성
2. **PMem 특성을 활용한 가상 주소 공간 확장성:** ephemeral heap과 경량 잠금으로 동시 m(un)map 요청을 16코어까지 확장 가능하게 함
3. **POSIX 엄격성 완화를 통한 성능:** 비동기 unmapping, dirty-page tracking 우회, 블록 pre-zeroing으로 PMem의 고유한 특성을 최대한 활용
4. **현실 워크로드에서 검증된 효과:** Apache **4×**, text search **70%**, RocksDB **2.95×** 성능 향상
5. **시스템 가용성 향상:** O(1) mmap으로 PMem 데이터베이스의 **즉시 시작(just boot)** 가능
6. **다른 고성능 스토리지에도 적용 가능:** CXL 기반 바이트 주소 가능 스토리지, 마이크로초급 PCIe SSD 등에도 DaxVM의 기법 적용 가능

**Broader significance:** DaxVM은 PMem의 물리적 특성(바이트 주소 가능성, 높은 대역폭, 비휘발성)을 OS 가상 메모리 스택에 완전히 통합하여, "메모리를 파일 인터페이스로 사용하는 것"의 한계를 시험하고 극복하는 실용적인 접근법을 제시한다. 특히 기존 POSIX mmap의 DRAM 중심 설계 가정이 고성능 스토리지 시대에 어떻게 재고되어야 하는지를 보여준다.

## 주요 결과

- **커널:** Linux 5.1.0, ext4-DAX 및 NOVA 파일 시스템 통합
- **아키텍처:** x86-64
- **테스트베드:** Intel Xeon Gold 5812T Cascade Lake, 2×16코어 @ 2.7GHz, 94GB DRAM + 384GB Intel Optane DCPMM (AppDirect 모드)
- **파일 시스템 aging:** Geriatrix 도구 사용, Agrawal 프로파일, 100TB 쓰기 (70% 사용률)
- **공개 저장소:** github.com/cslab-ntua/DaxVM-micro2022
- **스토리지 오버헤드:** 파일당 최소 4KB (≥32KB 파일), 2MB당 4KB 추가 (0.2%)
- 891MB Linux git 트리(68K 파일): 25MB PMem 사용

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2022MICRO-summarize/daxvm-stressing-the-limits-of-memory-as-a-file-interface.md|전체 요약 보기]]
