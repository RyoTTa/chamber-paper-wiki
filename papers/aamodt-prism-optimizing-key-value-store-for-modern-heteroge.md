---
tags: [paper, 2023, 2023ASPLOS, topic/cache, topic/dram, topic/nvm, topic/storage]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023ASPLOS-summarize/prism-optimizing-key-value-store-for-modern-heterogeneous-storage-devices.md"
---

# Prism: Optimizing Key-Value Store for Modern Heterogeneous Storage Devices

**Venue:** 
**저자:** 

## 개요

기존 storage system은 **performance device(고성능, 고비용) vs. capacity device(저성능, 저비용)** 라는 명확한 계층(hierarchy)을 가정하고 caching, tiering, layered LSM-tree 등의 설계를 해왔다. 그러나 최신 storage hardware의 발전은 이 dichotomy를 무너뜨렸다:

| Device | Read BW | Read Latency | $/TB |
|--------|---------|-------------|------|
| Intel Optane DCPMM (NVM) | 6.8 GB/s | **0.30 μs** | 4,096 |
| Samsung 980 Pro (Flash SSD, PCIe 4) | **7 GB/s** | 50 μs | **150** |

- Flash SSD가 NVM보다 **27배 저렴**하면서도 더 높은 bandwidth 제공.
- NVM은 flash SSD 대비 **2 orders of magnitude 낮은 latency**, practically unlimited endurance (292 PBW vs. 0.6 PBW).
- PCIe Gen 5 SSD는 bandwidth가 13 GB/s로 추가 확대 예상.
- NVM은 memory channel 제한으로 capacity/bandwidth scaling이 어려움.

→ "Storage hierarchy is not a hierarchy" [88], "storage jungle" [38].

**핵심 질문:** "더 이상 hierarchical이 아닌 storage landscape에서 key-value store를 어떻게 설계해야 하는가?"

## 방법론

- **io_uring** for asynchronous I/O to Value Storage.
- **PACTree [50]** as Persistent Key Index (교체 가능, 의존성 없음).
- XFS filesystem + O_DIRECT.
- 8개 Value Storage(SSD당 1개), 각각 독립적인 io_uring SQ/CQ pair + GC thread (queue depth=64).
- NVM usage: 100M KV pair → 약 5.4GB (Persistent Key Index + HSIT).

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1 평가 방법론

| 항목 | 내용 |
|------|------|
| **Hardware** | Dual-socket Xeon, 40코어, 768GB NVM(6×128GB Optane DIMMs), 96GB DRAM, 8×Samsung 980 Pro 1TB SSD (RAID-0, RAID controller 2개) |
| **Competitors** | MatrixKV [89], RocksDB-NVM [33], SLM-DB [45], KVell [57] |
| **Workloads** | YCSB A~E(100M KV pairs, 1KB/item, Zipf 0.99), Nutanix production trace, 1B KV pairs(1TB) |
| **Cost normalization** | 모든 시스템에 동일 $170 비용 할당. Prism은 KVell 대비 작은 DRAM cache(20GB vs. 32GB) 사용 |
| **Configuration** | Prism: SVC=20GB, PWB=16GB; 40 threads |

### 4.2 성능 결과

**Throughput (Figure 7, Table 3):**

| Workload | vs MatrixKV | vs RocksDB-NVM | vs KVell | vs SLM-DB |
|----------|-------------|----------------|----------|-----------|
| **YCSB-A** (write-intensive) | **13.1×**, 3.2× lower avg latency | 유사 | **1.3×**, 8.7× lower tail latency | **22.7×** |
| **YCSB-B/C/D** (read-intensive) | 4.8~5.5× | — | 1.2~1.7× | up to **14.4×** |
| **YCSB-E** (scan-intensive) | 1.4× | — | **2.3×** | **2.5×** |

**Latency (Table 3):** Prism의 YCSB-A median latency=2μs (KVell=152μs). YCSB-E 99%-ile=808μs (KVell=1,215μs).

**1B KV pairs workload (Figure 10a):** KVell 대비 최대 **2.42× throughput** — SVC와 thread combining 효과.

**Nutanix production workload (Figure 10b):** 57% update, 41% read, 2% scan → KVell 대비 **1.44× throughput**.

### 4.3 Ablation & Sensitivity Studies

**데이터 skew 영향 (Figure 9):** Prism은 skewness 증가(Zipf 0.5→1.5)에 따라 throughput도 증가 — PWB/SVC가 hot data를 효과적으로 관리. KVell은 skew 증가 시 load imbalance로 throughput 감소.

**Thread combining 효과 (Figure 11):** QD=64에서 timeout 방식 대비 throughput 11.7배, latency 1.9배 개선.

**Write amplification (Figure 12):** Prism의 WAF가 가장 낮음. MatrixKV는 Prism 대비 **최대 162배**(compaction), KVell은 **최대 13배**(page-granularity IO).

**SSD 개수 영향 (Figure 13):** 2~8개 SSD에서 Prism이 KVell 대비 일관된 throughput 우위. 단, SSD≤2개 read-intensive에서는 KVell이 약간 앞섬 (KVell의 aggressive injector thread 때문).

**SVC/PWB 크기 (Figure 15):** SVC=4GB(20GB의 20%)만으로도 55% read/scan 성능 유지 — value-granule caching이 page-granule 대비 효율적.

**Multicore scalability (Figure 16):** Prism은 모든 workload에서 near-linear scaling. KVell(QD=64)은 core 증가에 따른 latency 열화 발생.

**GC 영향 (Figure 17):** Prism의 GC는 non-blocking (HSIT 통한 접근) → throughput에 유의미한 영향 없음.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2023ASPLOS-summarize/prism-optimizing-key-value-store-for-modern-heterogeneous-storage-devices.md|전체 요약 보기]]
