---
tags: [paper, 2023, 2023ATC, topic/cache, topic/dram, topic/memory-tiering, topic/nvm, topic/storage]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023ATC-summarize/atc23-lin.md"
---

# p2Cache: Exploring Tiered Memory for In-Kernel File Systems Caching

**Venue:** 
**저자:** 

## 개요

### Fast Storage와 Kernel File System의 괴리

- **Byte-addressable persistent memory (PM)** 상용화: Intel Optane DC PM — DIMM 패키지, memory bus 연결, load/store로 직접 접근. 쓰기 latency ~80 ns, 읽기 latency ~170 ns (DRAM보다 2-3× 느림). 용량은 DRAM의 ~8×.
- **기존 kernel file system (Ext4, XFS, Btrfs)의 한계:**
  - **In-kernel storage stack overhead:** layered 설계(VFS → file system → block layer → journaling → driver)가 느린 HDD/SSD에는 적합하나, PM 같은 fast storage에서는 software가 bottleneck. NVMe SSD(3 μs)에서도 software가 read latency의 50% 차지.
  - **관찰 1:** Ext4는 SSD→PM→DRAM으로 storage 속도가 빨라져도 marginal performance 향상만 보임 (Figure 1a,b,d). Storage stack이 dominant bottleneck.
  - **관찰 2:** VFS는 전체 overhead의 10% 미만. tmpfs(DRAM 위 경량 FS)는 최고 성능 달성 → VFS 아래 thin layer로 fast storage 활용 가능.
  - **관찰 3:** **Journaling이 심각한 bottleneck.** Data journal mode: write 성능이 no journal의 ~10%(SSD), ~30%(PM). 원인: (1) metadata/data를 journal + file system 위치에 double write, (2) block-level journaling으로 partial write도 4KB block 단위로 기록 → write amplification, (3) single kernel thread로 journaling → scalability 제한, (4) 즉시 fsync() 없이 instant durability 불가.

### 기존 접근법의 문제

- **PM-specialized file systems (NOVA, SplitFS, Strata, BPFS, PMFS):**
  - PM에 최적화되어 높은 성능 + strong consistency 제공.
  - **관찰 4:** Production-ready까지 성숙하려면 수년 소요. 또한 DRAM을 bypass → PM의 읽기 latency(DRAM의 2-3×)에 bound. CoW로 인한 write amplification(특히 small writes에서).
  - NOVA: per-inode log-structured FS → synchronous persistence. Small write(1KB)에서 CoW overhead 발생.
- **PM-enhanced file systems (Ext4-DAX, XFS-DAX):**
  - Page cache bypass, PM에 block-level 직접 접근.
  - Block level 운영으로 byte-addressability 활용 불가. Data journal mode 미지원, 강한 crash consistency 불가. NOVA의 50% 미만 성능.
- **PM cache 접근법 (UnionFS, First Responder):**
  - DRAM bypass, block-level에 국한, metadata는 slow path에 방치. **관찰 5:** data+metadata 모두, PM+DRAM 특성 차이를 인식하는 caching이 필요.

## 방법론

### 1. 핵심 아이디어: Read/Write-Distinguishable Memory Hierarchy

PM/DRAM tiered memory system에서 **read와 write를 분리**:
- **모든 write → PM:** instant data durability + strong crash consistency
- **대부분 read → DRAM:** 높은 I/O 성능 (DRAM read가 PM 대비 2-3× 빠름)

### 2. 아키텍처 (Figure 2)

VFS 바로 아래에 두 개의 cache layer:
- **Persistent cache (PM):** 모든 file system update(metadata + data)를 capture → PM에 synchronous persist → asynchronous writeback to underlying FS
- **Page cache (DRAM):** native page cache와 별도 구현. Read를 DRAM에서 서비스.

### 3. Write-centric Persistent Cache (§3.2)

#### 3.1 PM 공간 레이아웃 (Figure 3)

- PM 공간을 `n`개 group으로 분할 (n = CPU core 수)
- 각 group = metadata log area + file data log area
- Per-core **두 개의 WAL** (원형 버퍼):
  - **dWAL (Directory WAL):** directory operation용 (create, link, unlink, mkdir, rmdir, rename, mknod, symlink, setattr, update_time)
  - **fWAL (File WAL):** file operation용 (write, write_iter)
- Multiple PM DIMM → interleaved mode 사용. Per-core WAL로 high concurrency (core 간 독립적 logging).
- 각 log entry에 timestamp → underlying FS 적용 시 순서 보장. VFS의 per-inode rw lock으로 동일 file 동시 업데이트 방지.

#### 3.2 Instant Durability + Strong Crash Consistency (Algorithm 1)

```
function PERSISTENCE(operation):
    log_entry := create_a_log_entry(operation)
    if is_directory_op:
        write_to_dWAL(log_entry)       // 64-byte fixed-size entry
    else:
        write_to_fWAL(log_entry)
        data_persistence(log_entry)     // §3.2.3
    update_in_DRAM_indexes()           // §3.3.2
    sfence()                            // write ordering barrier
    update_log_tail()                   // atomically commit via 8-byte tail update
    sfence()
```

- **Atomicity model:** Optane PM은 8-byte update만 atomic 보장 → log tail 8-byte update로 전체 operation commit.
- **두 개의 sfence:** (1) WAL/data write 후, (2) log tail update 후. CPU store buffer의 write ordering 보장.
- **vs JBD2 비교:**
  - JBD2: 복잡한 transaction (journal header + multiple descriptor blocks + commit block), 모두 4KB block 단위.
  - P2Cache: 가벼운 64-byte log entry. Byte-addressable PM의 이점 활용.
  - Defer writeback: PM 대용량 + persistence → writeback을 최대한 지연 가능, coalescing 최적화.

#### 3.3 Fine-grained, Highly-efficient Data Logging: Decoupled CoW (§3.2.3)

**문제:** Consistency 위해 commit 전 old data overwrite 금지 → 기존 방식은 CoW로 전체 block copy → write amplification.

**해결: "Decoupled CoW"** — copy와 write를 분리, write 크기에 따라 차별화:

1. **Small partial write (< 2KB, block=4KB):**
   - fWAL에 operation log entry append → 바로 뒤에 data content append.
   - Log tail을 data content 끝으로 이동 → commit.
   - **장점:** 추가 block allocation 없음, copy 없음. Byte-addressable PM의 append-only 특성 활용.

2. **Large partial write (≥ 2KB, < 4KB):**
   - File data log area에 free block allocate → partial write 저장.
   - Red-black tree로 free block tracking (NOVA와 유사).

3. **Aligned overwrite (full blocks):**
   - File data log area에 새 data block 할당 → 기존 block replace.

4. **Append:**
   - 기존 data block 끝에 새 data append → 추가 block 필요시 allocate.

**Read 시 assembling:** DRAM indexes로 분산된 data 조립 (Section 3.3.2). Copy는 writeback 시 수행 — fWAL의 small write를 file data log area로 복사, large write의 missing portion을 old data로 채움. 최대 half block(2KB)만 copy 필요. Real-world trace에서 partial update는 30-90%.

## 핵심 기여

1. **Legacy kernel file system도 PM의 이점을 누릴 수 있다.** VFS 아래 경량 persistent cache layer 도입으로, 기존 FS 수정 없이 strong consistency + high performance 달성. Production-ready 검증된 FS의 신뢰성을 그대로 유지.

2. **Read/write-distinguishable memory hierarchy가 핵심 통찰.** PM의 빠른 write + persistence와 DRAM의 빠른 read를 분리 활용. Device-level parallelism으로 double write overhead를 숨기는 inclusive cache model이 단순하면서도 효과적.

3. **Decoupled CoW는 PM의 byte-addressability를 극대화.** Partial write에서 불필요한 data copy를 제거하여 기존 CoW의 write amplification 해결. 특히 small, partial write가 많은 real-world workload에서 높은 성능.

4. **P2Cache는 PM-specialized FS보다도 빠르다.** Metadata ops 3.5×, RocksDB insert 72% 우위 — full-fledged FS보다 caching layer가 더 단순하고 빠를 수 있음을 입증. 향후 CXL 기반 byte-addressable storage로의 자연스러운 확장 가능.

## 주요 결과

#### 4.1 Inclusive Cache Model

- DRAM(최상위)이 항상 최신 버전 보유.
- **Write path:** PM persist + DRAM copy 동시 수행 → commit.
- **Read path:** DRAM → PM → underlying FS 순차 탐색.
- **Device-level parallelism (Figure 4):** PM write와 DRAM copy가 병렬 수행 → double write latency ≈ single PM write latency. 느린 PM이 빠른 DRAM copy를 숨김. DRAM write bandwidth는 PM의 6×.
- LRU eviction, dirty page drop 가능 (PM에 이미 persist됨).

#### 4.2 Fast Read Assembling via In-DRAM Indexes

Linux kernel의 **XArray** (lockless, memory-efficient radix tree)로 4개의 per-inode index (Figure 5):

| Index | 대상 | 저장 위치 |
|-------|------|-----------|
| ① | Full data blocks | DRAM page cache |
| ② | Partial-write slots | DRAM page cache |
| ③ | Log entries | PM fWAL |
| ④ | Data blocks | PM file data log area |

**Read assembling sequence:**
1. offset → index ① query → full cache hit → 직접 반환 (case 1)
2. {offset, length} → index ② query → partial slot 존재 확인 → aggregation (case 4,5)
3. {offset, length} → index ③ query → fWAL의 small partial write 수집 → page cache로 copy (case 5)
4. offset → index ④ query → PM data block에서 large partial write 수집 → page cache로 copy (case 2,4)
5. Uncovered "holes" → underlying FS에서 read (case 3,4, 가장 느림)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2023ATC-summarize/atc23-lin.md|전체 요약 보기]]
