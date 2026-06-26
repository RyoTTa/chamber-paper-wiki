---
tags: [paper, 2024, 2024ATC, topic/disaggregation, topic/dram, topic/memory-tiering, topic/nvm, topic/pim, topic/storage, topic/virtual-memory]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024ATC-summarize/atc24-tabatabai.md"
---

# FBMM: Making Memory Management Extensible With Filesystems

**Venue:** 
**저자:** Bijan Tabatabai, James Sorenson, Michael M. Swift (University of Wisconsin–Madison)

## 개요

CXL, HBM, persistent memory 등 새로운 메모리 하드웨어의 등장으로 tiered memory, far memory, processing-in-memory 등 다양한 MM(Memory Management) 정책이 필요해졌다. 그러나 **Linux의 MM subsystem은 monolithic**하여 확장이 어렵다:

- **Transparent Huge Pages:** 구현이 18개 파일에 분산
- **Meta의 TPP (Transparent Page Placement):** tiered memory 지원을 위해 **22개 kernel 파일** 수정
- **HMSDK:** 9개 파일 수정
- **RMM (Redundant Memory Mappings):** 16개 파일 수정

각 확장마다 core MM code를 수정해야 하고, upstream merge 또는 자체 fork 유지보수 부담이 발생. File system(VFS), driver, networking 등은 extensible한 반면, MM은 예외적으로 확장성이 결여됨.

**4가지 설계 목표:**
1. **Expressiveness:** 다양한 MM 정책 표현 가능
2. **Transparency:** unmodified application 지원
3. **Control:** `madvise`처럼 특정 region에 대한 MM 정책 지정 가능
4. **Non-invasive:** 기존 MM code에 최소한의 변경

---

## 방법론

### 3.1 Architecture Overview

```
 Application
     ↓ ① mmap(MAP_ANON)
 FBMM Shim ───→ ② MFS file tree 검색/생성
     ↓ ③ VFS callback
   MFS ───→ ④ alloc_pages / page table update
     ↓          ⑤ async (kernel thread)
  DRAM / CXL / PMEM / Swap
```

FBMM shim은 per-process **MFS file tree** (maple tree)를 유지. 각 entry는 {MFS file ptr, VA range}.

### 3.2 FBMM Shim: Transparency + VMA Merging

**Key insight:** naive하게 allocation마다 1:1 file mapping은 비효율적:
- File create/open: mmap의 **2~3배** 비용
- VMA 분할 → VMA tree traversal 비용 증가, per-process limit (2¹⁶) 도달 가능

**Solution:** MFS file을 여러 allocation에 **공유**:
1. MFS file의 logical size를 **128GB**로 크게 설정 (metadata만 변경, 비용 무시)
2. File의 VA range와 동일 크기 할당 → allocation VA와 file offset 간 **단순 차감**으로 매핑 (`offset = alloc_start - file_va_range_start`)
3. Top-down allocation → VMA merging 촉진
4. brk → file의 VA range 시작점 = allocation start (상향 성장), mmap → 종료점 = allocation end (하향 성장)

`munmap` 시: overlap되는 모든 file에 `fallocate(FALLOC_FL_PUNCH_HOLE)` → MFS에 메모리 해제 신호

**구현:** kernel 내 ~600 LOC shim + ~50 LOC core MM 변경

### 3.3 MFS Design: VFS Callback 기반

주요 VFS callback:

| Callback | 정의 위치 | 목적 |
|----------|----------|------|
| `get_unmapped_area` | file_operations | VA 할당 |
| `page_fault` | vm_operations_struct | PF 처리, physical page 할당 + PTE 설정 |
| `fallocate` | file_operations | MAP_POPULATE 시 preallocation / munmap 시 해제 |
| `free_inode` | super_operations | file delete → 전체 physical memory 해제 |
| `mmap` (callback) | file_operations | 최초 mapping 시 설정 |

**Physical memory 관리:**
- **Static reservation** (boot time): contiguous 보장, custom allocator 사용 가능 (free list, segment tree 등)
- **Dynamic allocation** (`alloc_pages`): overprovisioning 방지, kernel shrinker callback으로 memory pressure 대응
- MFS가 직접 page table walk/modify

**Translation:** `page_fault` callback에서 `mk_pte`로 PTE 생성. 대체 page table 디자인(RMM, Mitosis 등)도 구현 가능.

### 3.4 한계

- MFS composability 불가 (tiered + huge page stacking 등)
- MFS 간 coordination 메커니즘 부재
- Kernel process, page cache, stack/BSS segment에는 적용 불가

---

## 핵심 기여

1. **VFS는 이미 충분한 MM 기능을 제공** — 이를 활용한 MFS가 monolithic MM의 확장성 문제를 해결
2. **FBMM shim 덕분에 application 투명성 확보** — mmap→file operation 변환, VMA merging으로 오버헤드 최소화
3. 실제 application 수준 오버헤드는 **0.1% 미만** (multi-page allocation), MAP_POPULATE 시 **오히려 더 빠름**
4. **3가지 case study에서 검증:** Tiered memory, bandwidth expansion, contiguous allocation 모두 standalone kernel module로 구현, SOTA와 동등 이상 성능
5. MFS는 kernel fork 불필요, 독립 compile/load → adoption barrier 최소화. 향후 DAMON 등 kernel abstraction과 결합 시 구현 크기 추가 감소 가능

## 주요 결과

### 4.1 TieredMFS (Tiered Memory, ~1,500 LOC)

TPP 설계 기반. **Local pool + Remote pool**로 분리, 각 pool에 hot/cold list 유지.

- Kernel thread가 주기적으로 PTE access bit 샘플링 → hot/cold list 갱신
- `page_fault` callback: local pool free가 allocation threshold 이상이면 local, 아니면 remote
- Reclamation threshold 이하 시: local cold list 하위 페이지 → remote pool로 migration
- Allocation threshold 이상 시: remote hot list 페이지 → local pool로 migration

**평가 (GUPS, 32GB data, 8GB hot region):**

| System | Relative Throughput | Remote Access % |
|--------|--------------------|-----------------|
| Linux Split | **70%** | 20% |
| TieredMFS | **88%** | **6.5%** |

**Memcached + YCSB (read-only zipfian, 50 runs median):**

| System | Throughput (kOps/s) | Remote Read % |
|--------|--------------------|---------------|
| Base Linux | 17.5 | 0% |
| Linux Split | 16.5 (**94%**) | 57% |
| TieredMFS | 17.2 (**98%**) | **<0.5%** |

### 4.2 BWMFS (Bandwidth Utilization, ~579 LOC)

HMSDK의 interleaving 기능을 MFS로 구현. `sysfs`로 node별 allocation weight 설정 (e.g., local:remote = 3:2 → 60% local).

- `page_fault`/`fallocate` callback에서 `alloc_pages_node`로 weight 기반 round-robin 할당
- **단일 오후에 프로토타입 완성**

**평가 (STREAM benchmark, 8 threads):**

| Config | Bandwidth (Copy) |
|--------|-------------------|
| Linux (local only) | ~20,000 MB/s |
| BWMFS 1:1 | ~35,000 MB/s |
| BWMFS 2:1 | ~31,000 MB/s |

BWMFS 결과는 HMSDK와 **±3% 이내**. Multi-node bandwidth 활용으로 local-only 대비 최대 **75%** 향상.

### 4.3 ContigMFS (Contiguous Allocation, ~479 LOC)

RMM의 range TLB를 위한 contiguous allocation MFS.

- `get_unmapped_area` callback에서 `folio_alloc`으로 contiguous physical page eager allocation
- 동일 callback에서 PTE + range page table entry 동시 설정
- BadgerTrap 기반 TLB miss simulation으로 효과 검증

**평가 (32-entry range TLB):**

| Application | % TLB Misses Prevented |
|-------------|------------------------|
| mcf | **99.78%** |
| cactuBSSN | **99.92%** |
| GUPS | **99.91%** |

### 4.4 MFS vs Monolithic Implementation 비교

| System | Files Changed | Lines Changed |
|--------|--------------|---------------|
| TPP | 22 | 471 |
| **TieredMFS** | **3** | **1,567** (1/3 debugging + boilerplate) |
| HMSDK | 9 | 920 |
| **BWMFS** | **2** | **579** |
| RMM | 16 | 546 |
| **ContigMFS** | **2** | **479** |

MFS 구현이 monolithic보다 더 많은 LOC를 가질 수 있으나 (TieredMFS > TPP), 이는 core MM code에 의존하지 않고 **자체 구현**했기 때문이며, standalone module로서의 이점(독립 빌드, 간단한 유지보수)이 더 큼.

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2024ATC-summarize/atc24-tabatabai.md|전체 요약 보기]]
