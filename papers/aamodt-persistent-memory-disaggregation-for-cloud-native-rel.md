---
tags: [paper, 2023, 2023ASPLOS, topic/cache, topic/disaggregation, topic/dram, topic/memory-tiering, topic/nvm, topic/storage]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023ASPLOS-summarize/persistent-memory-disaggregation-for-cloud-native-relational-databases.md"
---

# Persistent Memory Disaggregation for Cloud-Native Relational Databases

**Venue:** 
**저자:** 

## 개요

Cloud-native relational DB(Aurora, PolarDB, Socrates)는 compute-storage disaggregation을 통해 resource elasticity를 제공하지만, 여전히 두 가지 근본적 한계가 존재한다:

1. **DRAM disaggregation의 한계:** DRAM density 한계(per-DIMM 128GB), 높고 변동성 큰 가격, volatility로 인한 긴 recovery time
2. **Write latency:** Transaction commit 시 storage layer로의 느린 persistence가 bottleneck

**Persistent Memory(PM, Optane DC 등)의 기회:**
- DRAM 대비 4× density (512GB per DIMM)
- Byte-addressability + persistence 동시 제공
- RDMA를 통한 ultra-low-latency remote access (~8µs for 16KB page via one-sided RDMA)
- Cost: DRAM과 SSD 사이

그러나 기존 PM disaggregation 연구는 native data structures(AsymNVM)나 KV stores(pDPM)만 target. Relational DB는 훨씬 복잡한 software stack과 transaction semantics를 가지며, 다음 두 bottleneck이 발생:

- **PM bandwidth contention:** PM write bandwidth는 DRAM보다 현저히 낮음. 특히 dirty page flush + WAL write가 동시 발생 시 bottleneck
- **PMN CPU bottleneck:** Onload 설계(pDPM)는 PM bandwidth bottleneck, offload 설계(AsymNVM)는 PMN CPU bottleneck — 대규모 multi-tenant 환경에서 치명적

---

## 방법론

### 3.1 3-Level Architecture Overview [Fig.2]

- **Compute Node (CN):** SQL/TXN engine + 소규모 Local Buffer Pool(LBP, DRAM). DB size의 ~5% 수준
- **Persistent Memory Node (PMN):** Remote Buffer Pool(RBP, PM, DB size의 ~50%) + CDLog Store(WAL persistence). Light-weight daemon만 실행
- **Storage Node (SN):** SSD/HDD 기반 공유 저장소. 완전한 DB 복제본 및 checkpoint 보관

**Inclusive hierarchy:** LBP에 cached된 모든 page는 RBP에도 copy 존재 → CN crash recovery 시 PMN의 copy로 즉시 복구 가능

### 3.2 CDLog — Compute-node-Driven Logging [Fig.3,4]

핵심 아이디어: page를 16KB → **256B mini-page**(Optane 3D XPoint의 physical access granularity)로 split하여 fine-grained logging.

**Data structures (CN-side):**
- **Page Metadata Table(PMT):** open-addressing hash table. Page ID → metadata (LBP address, RBP address, dirty-bit vector, local LSN vector). Space overhead: 32B per 16KB page = 2GB for 1TB DB
- **Dirty-bit vector:** per mini-page modified 여부 tracking
- **Local LSN vector:** per mini-page highest LSN 기록

**CDLog entry 구조:**
- **Log metadata:** `<laddr, paddr, lsn>` — PM-applied LSN vector의 주소, target mini-page PM 주소, 이 log entry의 LSN
- **Log data:** mini-page의 새 content

**Log write workflow:**
1. Transaction commit 시 dirty-bit vector 검사 → dirty mini-page list 구성
2. Per dirty mini-page: metadata entry + data entry 생성
3. **Two one-sided RDMA writes**로 PMN의 ring buffer에 직접 기록 (metadata → metadata buffer, data → data buffer)
4. RDMA batching으로 network overhead 감소

### 3.3 Light-Weight PMN Processing [Fig.4]

**PM-side data structures:**
- **RBP:** page server 역할. 각 page마다 PM-applied LSN(aLSN) vector + PM LSN(pLSN) vector 유지
- **CDLog store:** dual ring buffer (metadata + data). CN이 producer, PMN이 consumer
- **Global applied LSN(GaLSN):** LM(Log Merger)가 적용 완료한 마지막 LSN. CN이 주기적 polling

**Log application:** LM daemon이 ring buffer scan → metadata entry로부터 target mini-page 주소 획득 → **DMA/RDMA memory copy**로 data entry를 target mini-page로 복사 → aLSN 갱신. CPU는 거의 개입하지 않음 (RDMA doorbell batching으로 polling overhead 감소).

**Lock-free design:** CN(producer)과 PMN(consumer)이 strictly incrementing LSN으로 동작 → accidental overwrite는 GaLSN coarse-grained monitoring으로 방지. 분산 락 불필요.

### 3.4 Optimistic Remote Read + Log-Pull [Table 2,3]

RBP hit → LBP miss 시 CN이 one-sided RDMA read로 page fetch:

1. CN이 PMT로 target RBP page의 PM 주소 확인
2. One-sided RDMA read로 page + aLSN vector 동시 fetch
3. CN이 로컬 PMT의 local LSN vector와 aLSN 비교 → freshness check
4. **Match (99.75% cases):** read 완료
5. **Stale (0.25% cases):** CN이 PMN에서 relevant log entries를 **log-pull** (one-sided RDMA read) → CN-side에서 log application 수행 (page가 stale이더라도 PMN CPU 개입 없음)

Latency 비교 (Table 2):

| Variant | Median | Avg | P99 |
|---------|--------|-----|-----|
| Log-offload (기존) | 178µs | 227µs | 872µs |
| CDLog | 23µs | 25µs | 48µs |
| PilotDB (log-pull) | **15µs** | **16µs** | **30µs** |

### 3.5 State Recovery

**CN crash:** PMN의 RBP에 page copy 유지 → reboot 후 PMT를 PMN에서 reconstruct(GaLSN 위치의 log entries apply). Recovery 거의 즉시. LBP warm-up: ~35s (MySQL-ideal의 81+87s 대비).

**PMN crash (server 재시작 가능):** PM persistence로 state 보존 → remap PM region → unfinished transaction rollback → 즉시 서비스 재개

**PMN crash (server 교체):** 3-way log replication으로 다른 PMN replica가 primary 승계 → 즉시 failover. RBP warm-up은 background에서 checkpoint + log-pull로 진행.

---

## 핵심 기여

**핵심 Contribution:**
1. **PM disaggregation을 cloud-native relational DB에 최초 적용** — 3-tier DRAM-PM-SSD 구조로 LBP를 DB size의 5%로 축소
2. **CDLog**: mini-page granularity physical logging + CN-driven log organization으로 PM write bandwidth를 최대 55% 감소
3. **CPU-light PMN data plane**: one-sided RDMA로 critical path의 거의 모든 PMN CPU 개입 제거 (log write, optimistic read, log-pull 모두 단일 one-sided RDMA로 처리)
4. **Optimistic read + log-pull**: 99.75% read가 one-sided RDMA로 완료, stale 시에도 CN-side에서 처리
5. **Real Optane PM + RDMA cluster 구현 및 검증** — MySQL-ideal 대비 최대 98% throughput, Aurora 대비 최대 2.72×

**Broader Significance:**
- PM이 DRAM 대체가 아닌 complementary tier로서 cost-effective disaggregation을 가능케 함을 입증
- Optane 단종 이후에도 CXL 기반 storage/memory(KIOXIA XL-FLASH, Samsung CXL SSD 등)로 동일 설계 원리 적용 가능
- CPU-light 설계로 PMN당 수십 개 tenant 지원 가능 → cloud provider의 PM pooling 경제성 검증

## 주요 결과

- **CN:** MySQL kernel 수정 (~5,000 lines C++). Log module: WAL → CDLog 교체 + log-pull 구현. Buffer pool: LRU 관리 유지 + RBP hierarchy 추가
- **PMN:** Light-weight daemon (background log application + recovery). RDMA-based memory copy
- **Platform:** Intel Xeon Platinum 8260 ×2, 256GB DDR4, 4×128GB Optane DC PM (App-Direct mode), 25Gbps network
- **Storage layer:** SPDK + RDMA + NVMe SSD 기반 distributed file system

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2023ASPLOS-summarize/persistent-memory-disaggregation-for-cloud-native-relational-databases.md|전체 요약 보기]]
