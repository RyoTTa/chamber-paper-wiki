---
tags: [paper, 2025, 2025HPCA, topic/cache, topic/disaggregation, topic/dram, topic/memory-tiering, topic/storage, topic/virtual-memory]
venue: "HPCA 2025 (IEEE International Symposium on High Performance Computer Architecture)"
year: 2025
summary_path: "../paper-summaries/2025HPCA-summarize/skybyte-architecting-an-efficient-memory-semantic-cxl-based-ssd-with-os-and-hardware-co-design.md"
---

# SkyByte: Architecting an Efficient Memory-Semantic CXL-based SSD with OS and Hardware Co-design

**Venue:** HPCA 2025 (IEEE International Symposium on High Performance Computer Architecture)
**저자:** Haoyang Zhang, Yuqi Xue, Yirui Eric Zhou, Shaobo Li, Jian Huang (University of Illinois Urbana-Champaign)

## 개요

CXL 기반 SSD(CXL-SSD)는 load/store instruction을 통해 SSD를 메인 메모리처럼 접근할 수 있게 하여 저비용으로 메모리 용량을 확장하는 유망한 접근법임. Flash 기반 SSD의 단가는 $0.27/GB로 DDR5 DRAM($4.28/GB) 대비 약 15.9배 저렴함. 그러나 naive하게 CXL-SSD를 host DRAM처럼 사용할 경우 1.5–31.4×의 성능 저하가 발생함(Figure 2). 그 원인은 다음 세 가지임:

1. **긴 Flash Access Latency.** Flash read latency는 state-of-the-art Z-NAND 기준 3 µs로, DRAM latency보다 수천 배 높음. SSD 내부 DRAM cache(수 GB)가 있으나 miss 시 tail latency는 수백 µs에 달하며, garbage collection(GC) 발생 시 수 ms까지 지연됨(Figure 3). 실제 측정 결과 CXL-SSD 메모리 요청의 90% 이상이 SSD DRAM cache hit으로 200 ns 이내에 처리되지만, tail latency는 최대 수백 µs까지 치솟음.

2. **Excessive Processor Pipeline Stalls.** 현대 CPU의 out-of-order 실행과 multi-level cache로는 수 µs 이상의 flash latency를 감추기에 부족함. CXL-SSD 사용 시 memory-bounded cycle 비율이 77%–99.8%에 달함(DRAM 사용 시 62.9%–98.7%, Figure 4). PCIe 5.0 x4(16 GB/s) 대역폭을 포화시키려면 최소 750개의 concurrent memory request가 필요하나, 이는 현재 프로세서로 실현 불가능함. 결과적으로 CPU core와 CXL-SSD 대역폭 모두 심각하게 underutilization됨.

3. **Access Granularity Mismatch.** CXL.mem은 64B cacheline 단위 접근을 지원하나, flash chip은 물리적 한계로 4KB page 단위 접근만 가능함. 기존 SSD DRAM cache는 block device 용도로 설계되어 page-granular로 동작하므로, 대부분의 workload에서 75% 이상의 page에 대해 40% 미만의 cacheline만 접근하는 locality 패턴(Figure 5, 6)으로 인해 DRAM 공간이 낭비되고, dirty cacheline이 소수여도 전체 page를 flash에 write하여 write amplification이 발생함.

## 방법론

SkyByte는 host OS와 SSD controller의 **co-design**을 통해 위 세 문제를 해결하며, 세 가지 핵심 컴포넌트로 구성됨.

### 1. Coordinated Context Switch Mechanism (§III-A)

**핵심 아이디어:** SSD DRAM cache miss로 인한 long flash access를 감지하면 host CPU에서 context switch를 트리거하여 다른 thread가 CPU core를 사용하게 함으로써 flash latency를 숨김.

**왜 기존 방식으로는 안 되는가?** CPU는 어떤 memory access가 SSD DRAM에서 hit/miss인지 알 수 없고, SSD는 host CPU의 microarchitectural 상태(core ID, speculative load 여부)를 알 수 없음. 어느 한쪽만으로는 context switch 여부를 결정할 수 없으므로 양측 협력이 필요함.

**Context Switch 절차 (Figure 7):**

- **C1 — CXL.mem MemRd 전송.** Host CPU가 CXL.mem MemRd 요청을 SSD controller로 전송. CPU는 LLC의 MSHR(Miss Status Handling Register)에 어떤 core의 어떤 instruction이 이 요청을 기다리는지 tracking.
- **C2 — SkyByte-Delay NDR 응답.** SSD controller가 DRAM cache miss를 감지하고, flash 접근이 필요하다고 판단하면 **context switch trigger policy**에 따라 결정. context switch를 트리거하기로 하면 CXL.mem NDR(No Data Response) message의 reserved opcode(111b)를 **SkyByte-Delay**로 정의하여 host로 전송(Figure 8). NDR은 데이터 없이 CXL memory transaction 완료만 알리는 S2M message임.
- **C3 — SkyByte Long Delay Exception.** Host CXL controller가 SkyByte-Delay NDR을 수신하면, 해당 메모리 요청의 LLC MSHR entry를 조회하여 상위 cache 계층(L1, L2)까지 traverse, 해당 응답을 기다리는 모든 미완료(uncommitted) memory instruction을 찾음. 해당 instruction이 **retire stage**에 진입할 때 **SkyByte Long Delay Exception**을 발생시킴(기존의 Page Fault Exception 메커니즘과 유사). Exception handler는 x86 IDT에 등록된 SkyByte handler를 호출하여 OS scheduler가 context switch를 수행.
  - Speculative load/store나 hardware prefetch는 retire stage까지 도달하지 않고 squashed되므로 false-positive context switch가 발생하지 않음 — **추가 하드웨어 비용 없이** 달성됨.
- **C4 — Thread 재개.** Context switch된 thread가 다시 schedule되면, 이전에 exception을 trigger한 memory instruction부터 재실행. 해당 instruction은 CXL-SSD에 다시 memory access를 issue하고, 이때 SSD DRAM에 data가 cache되어 있으면 정상적으로 CXL.mem MemData response 수신.

**MSHR 관리.** Context switch 시 squashed instruction의 MSHR entry를 즉시 해제하여, 다른 thread가 MSHR을 점유할 수 있도록 함. 이 방식은 host DRAM 접근에도 이점이 있어 SkyByte에서 default로 활성화됨.

**Context Switch Trigger Policy (Algorithm 1).** SSD controller는 flash channel queue의 pending request 수(num_read, num_write, num_erase)와 각 operation의 latency를 기반으로 예상 대기 시간을 계산:

```
est_lat = read_lat × (num_read + 1) + write_lat × num_write + erase_lat × num_erase
```

예상 latency가 threshold(기본값 2 µs)를 초과하면 context switch trigger. GC가 진행 중이면 즉시 trigger. Threshold는 host CPU의 context switch overhead(측정치 2 µs)에 맞춰 설정되며 OS가 설정 가능.

**Scheduling Policy.** Round-Robin, Random, CFS(Completely Fair Scheduler) 세 가지 policy 평가 결과 성능 차이는 미미(Figure 10). 모든 thread가 memory I/O bounded이므로 유사한 기회로 memory request 발행 가능. SkyByte는 Linux 표준인 CFS를 기본 사용.

### 2. CXL-Aware SSD DRAM Management (§III-B)

**핵심 아이디어:** SSD 내부 DRAM을 **cacheline-granular write log**와 **page-granular data cache**로 재구성하여 CXL interface(64B)와 flash memory(4KB) 간 granularity mismatch를 해소.

**구조 (Figure 11, 12):**

**Write Log (64MB, double-buffered).** Circular buffer로 모든 cacheline write 요청을 append-only로 기록. Flash 접근 없이 critical path에서 처리됨. Double buffering으로 하나의 log가 가득 차면 background에서 compaction 수행하고 새 log로 전환하여 incoming request를 blocking하지 않음.

**Write Log Index.** 2-level hash table 구조:
- **1st-level hash table:** Logical Page Address(LPA)로 색인. 각 entry는 8B LPA + 8B second-level table pointer(총 16B).
- **2nd-level hash table:** page 내 cacheline의 page offset(6-bit)과 log offset(26-bit)을 저장. 각 entry는 4B.
- Second-level table은 초기 4개 entry(16B)로 시작하여 load factor > 0.75 시 double 크기로 resize. Worst case memory footprint는 32MB(1M개의 16B 1st-level entry + 1M개의 16B 2nd-level table), 평균 5.6MB.
- Lock-free hash table로 동시성 처리.

**Data Cache (448MB, page-granular).** Flash에서 읽은 page를 page 단위로 caching하여 spatial locality 활용. Red-black tree로 indexing.

**Read Operation:**
- `R1`: Data cache → Write log에 **병렬 lookup**. Data cache hit이면 즉시 반환.
- `R2`: Data cache miss, write log hit → write log에서 cacheline 반환.
- `R3`: 둘 다 miss → flash에서 전체 page를 data cache로 fetch, write log에 update된 cacheline이 있으면 merge 후 target cacheline 반환.

**Write Operation:**
- `W1`: Write log의 tail에 cacheline append.
- `W2`: Data cache에 page가 존재하면 병렬 update.
- `W3`: Write log index table update (같은 cacheline 재기록 시 최신 log offset으로 갱신).

**Write Log Compaction (Figure 13).** Background에서 수행:
- `L1`: 1st-level hash table scan → flush 대상 page 식별.
- `L2`: Data cache에 page 있으면 바로 flash write.
- `L3`: Cache에 없으면 flash에서 coalescing buffer로 load.
- `L4`: 2nd-level table 순회하며 dirty cacheline merge.
- `L5`: Merged page를 flash channel에 분산 write (channel parallelism 활용).

**왜 효과적인가?** Page-granular cache는 소수의 dirty cacheline 때문에 전체 page를 flash에 write해야 하지만, cacheline-granular write log는 compaction 시 동일 page의 dirty cacheline들을 **coalescing**하여 flash write 횟수를 대폭 감소. 또한 fine-granular buffering으로 제한된 DRAM 용량을 더 효율적으로 활용. Coalescing window가 page cache보다 훨씬 넓어 write reduction 효과가 큼. Compaction은 평균 146 µs 소요.

### 3. Adaptive Page Migration (§III-C)

**핵심 아이디어:** Host DRAM을 SSD DRAM cache의 확장으로 활용. SSD controller가 per-page access count를 추적하여 threshold를 초과하는 hot page를 host DRAM으로 promotion.

**Migration 절차:**
1. SSD controller가 hot page 선정 후 PCIe MSI-X interrupt로 host OS에 page address 전달.
2. Host OS는 buddy allocator로 host DRAM physical page 할당 후 page content copy.
3. Migration 완료 시 PTE 갱신 → 해당 virtual address가 host DRAM page를 가리키도록 remap, TLB shootdown.

**Data Consistency.** Promotion Look-aside Buffer(PLB, 64 entries × 24B)를 root complex에 구현하여 migration 중인 page에 대한 read/write 일관성 유지 (선행연구 [7]의 접근법). 각 PLB entry는 source/destination page address(8B × 2), migrated cacheline bitmap(8B), valid bit를 포함. Migration 중 read는 SSD DRAM에서, write는 이미 migrated된 cacheline이면 host DRAM으로 forwarding.

**Eviction.** Host DRAM 공간 부족 시 Linux의 active/inactive list 기반 page reclamation policy로 cold page를 SSD로 demotion.

**Huge Page 지원.** 2MB huge page migration 시 PLB를 2-level 구조로 확장:
- 1st-level: 64B bitmap으로 2MB 내 각 4KB chunk의 migration 상태 추적.
- 2nd-level: 8B bitmap으로 현재 migration 중인 4KB chunk 내 각 cacheline 추적.

## 핵심 기여

1. **CXL-SSD의 근본적 병목을 3가지 축에서 공략:** (a) coordinated context switch로 flash latency hiding, (b) cacheline-granular write log로 access granularity mismatch 해소, (c) adaptive page migration으로 host DRAM을 SSD cache 확장으로 활용.

2. **OS-hardware co-design의 실용적 가치 입증:** 기존 CXL.mem 프로토콜의 reserved opcode와 x86 exception mechanism을 활용하여 **최소한의 하드웨어 변경**으로 실현 가능한 설계. CXL 3.0 표준과 호환됨.

3. **성능-비용 trade-off 최적화:** DRAM-Only의 75% 성능을 15.9× 저렴한 비용으로 달성, cost-effectiveness 11.8× 개선. 느린 commodity flash로도 competitive한 성능 가능.

4. **Write log의 효과:** 64MB의 작은 write log로도 23.08× flash write traffic 감소 — 제한된 SSD DRAM 용량을 가장 효율적으로 활용하는 설계 포인트.

## 주요 결과

### 실험 설정

**Workloads (Table I):** Graph Processing(bc, bfs-dense), Image Processing(srad), HPC(radix), Database(ycsb, tpcc via nstore), Machine Learning(dlrm — DLRM recommendation model). 모든 workload는 최소 8GB memory footprint, write ratio 5%–36%, LLC MPKI 1.0–122.9. Thread별 100M+ instruction trace를 Intel Xeon 서버에서 PIN으로 포착 후 시뮬레이터에서 replay.

**비교 대상 (Ablation study):**
- **Base-CSSD:** 최신 CXL-SSD 설계 [32], [62] (prefetching, optimized cache replacement, SSD-side MSHR 포함)
- **SkyByte-C:** Base-CSSD + coordinated context switch
- **SkyByte-P:** Base-CSSD + adaptive page migration
- **SkyByte-W:** Base-CSSD + CXL-aware SSD DRAM (write log + data cache)
- **SkyByte-CP:** Base-CSSD + context switch + page migration
- **SkyByte-WP:** Base-CSSD + page migration + CXL-aware SSD DRAM
- **SkyByte-Full:** 모든 컴포넌트 활성화 (24 threads on 8 cores)
- **DRAM-Only:** 무한 host DRAM (ideal baseline)

### Overall Performance (Figure 14)

| Variant | vs. Base-CSSD (geo. mean) | 비고 |
|---|---|---|
| SkyByte-P | 1.84× | Page promotion 효과 |
| SkyByte-W | 2.16× | Write log의 write coalescing 효과 |
| SkyByte-CP | 2.79× | Page promotion + context switch |
| SkyByte-WP | 2.95× | Page promotion + write log |
| **SkyByte-Full** | **6.11×** (최대 16.35×) | 모든 컴포넌트 결합 |
| DRAM-Only | — | SkyByte-Full은 DRAM-Only 성능의 75% 달성 |

**비용 효율성:** SkyByte-Full은 DRAM-Only 대비 15.9× 저렴하고 cost-effectiveness는 **11.8×** 개선 ($4.28/GB vs $0.27/GB 기준, 2024년 여름 시장가).

### Context Switch 효과 (Figure 15, Table III)

Thread 수를 8개에서 24개까지 증가시키며 throughput과 SSD bandwidth utilization 측정:
- Thread 수 증가에 따라 throughput이 선형적으로 증가 — context switch가 flash latency를 효과적으로 숨김.
- Flash read 비율이 높고 평균 flash read latency가 긴 workload(srad: 22.5 µs, bfs-dense: 25.7 µs)일수록 multi-threading 효과가 큼.
- 평균 flash read latency가 context switch overhead(2 µs)에 근접한 workload(bc: 3.5 µs, dlrm: 3.4 µs)는 thread 2개로도 충분.
- 일부 workload(dlrm)에서 thread 과다 시 context switch overhead로 throughput 감소.

### Average Memory Access Time — AMAT (Figure 17)

AMAT을 host DRAM → SSD DRAM → flash chip의 3-level memory hierarchy로 모델링:
- SkyByte-Full은 SkyByte-WP 대비 AMAT 추가 개선 (flash latency hiding). DRAM-Only 대비 AMAT은 1.39×이나, 더 많은 thread(24 vs 8)로 parallelism을 활용하여 end-to-end 성능은 1.33× 저하에 그침.
- **Latency breakdown:** SkyByte-W는 write buffering으로 flash access를 critical path에서 제거하여 효과적. SkyByte-P는 hot page를 host DRAM으로 옮겨 SSD 접근 횟수 감소.

### Flash Write Traffic (Figure 18)

- SkyByte-W는 SkyByte-P보다 flash write traffic 감소에 더 효과적 — write log의 넓은 coalescing window 덕분.
- **SkyByte-Full 평균 23.08× flash write traffic 감소** (Base-CSSD 대비).
- Context switch가 SSD DRAM contention을 증가시켜 compaction frequency를 높여 write traffic이 **소폭 증가**할 수 있으나, 성능 이점 대비 미미.

### Write Log Size Sensitivity (Figure 19, 20)

Total SSD DRAM(512MB) 내 write log/data cache 비율 변화 실험:
- Write가 많고 temporal locality가 좋은 workload(srad, tpcc)는 log size에 민감.
- **대부분 workload에서 64MB(전체의 1/8)로도 충분한 write coalescing window 확보.**
- Log size 증가 시 flash write traffic 감소 효과는 diminishing returns.

### SSD DRAM Size Sensitivity (Figure 21)

SSD DRAM cache 크기를 0.125–2.0GB로 변화:
- 모든 경우에서 SkyByte-Full이 다른 baseline보다 우수.
- Cacheline-granular write log가 page-granular cache 대비 더 큰 effective cache size 제공 → **SkyByte는 작은 SSD DRAM으로도 Base-CSSD(더 큰 DRAM)와 유사하거나 더 나은 성능 달성** — CXL-SSD 비용 절감 효과.

### Flash Latency Sensitivity (Figure 22, Table IV)

ULL(3 µs), ULL2(4 µs), SLC(25 µs), MLC(50 µs) 네 종류 NAND flash로 실험:
- Flash latency가 높을수록 SkyByte-Full의 개선 효과가 커짐 — write log와 context switch 모두 flash latency hiding이 핵심.
- **SkyByte-Full**은 느리고 저렴한 commodity flash로도 ULL Z-NAND에 근접한 성능 달성 가능 — **병렬화 가능한 application에 대해 cost-effective CXL-SSD 구축 가능성 시사.**

### Alternative Page Migration 비교 (Figure 23)

TPP(Transparent Page Placement [43]) 및 AstriFlash [23]와 비교:
- **SkyByte-CP > SkyByte-CT** (1.09×): TPP의 periodic sampling 기반 page hotness 추정보다 SkyByte의 per-page tracking이 더 정확.
- **SkyByte-CP > AstriFlash-CXL** (1.09×): SkyByte는 hot page만 promotion하여 fully associative cache 효과, AstriFlash는 on-demand paging으로 set-associative cache.
- **SkyByte-WCT > SkyByte-CT** (1.10×): SkyByte의 CXL-aware SSD DRAM 관리가 TPP와 결합 시에도 효과적.

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/storage.md|Storage]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2025HPCA-summarize/skybyte-architecting-an-efficient-memory-semantic-cxl-based-ssd-with-os-and-hardware-co-design.md|전체 요약 보기]]
