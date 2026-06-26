---
tags: [paper, 2025, 2025MICRO, topic/dram, topic/rowhammer, topic/security, topic/virtual-memory]
venue: ""
year: 2025
summary_path: "../paper-summaries/2025MICRO-summarize/citadel-rethinking-memory-allocation-to-safeguard-against-inter-domain-rowhammer-exploits.md"
---

# Citadel: Rethinking Memory Allocation to Safeguard Against Inter-Domain Rowhammer Exploits

**Venue:** 
**저자:** Anish Saxena, Walter Wang, Alexandros Daglis (Georgia Tech)

## 개요

### 1.1 Rowhammer: 지속되는 Hardware Security Threat

Rowhammer는 DRAM row를 반복적으로 activate하면 인접한 row에서 bit flip이 발생하는 하드웨어 취약점이다. 2014년 발견 이후 10년이 지났지만:
- 2022년 연구 기준 **모든 tested DDR4 chip이 취약** [30]
- **TRR 등 commercial mitigation**이 있으나 Half-Double[40] 같은 우회 공격으로 무력화
- JEDEC의 PRAC(Per-Row Activation Counters)는 DRAM area 9% 증가 + 매 activation을 read-modify-write로 만들어 심각한 성능 저하
- Principled hardware solution(MINT[55], PrIDE[28] 등)은 아직 상용 배포되지 않음

Rowhammer는 VM 간 공격[72], unprivileged software[67], remote network code[44], malicious website[25] 등 다양한 공격 벡터로 악용되며, page table bit flip을 통한 privilege escalation[61], DRAM data leakage(RAMbleed)[42], 암호체계 파괴[57] 등 심각한 피해를 일으킨다.

### 1.2 기존 Software-based Isolation의 한계

Software-based domain isolation은 가장 유망한 방어 전략이지만, 기존 솔루션들은 **security와 memory efficiency 사이의 tradeoff**에 실패했다:

**ZebRAM[41]**: 모든 DRAM row를 data row와 guard row로 교차 배치. **50% DRAM capacity loss** (Half-Double 대비로는 67%+). Guard row를 swap space로 사용하는 optimization도 있으나, (1) 현재 RH threshold에서는 수천 번 activation만으로 guard row에 bit flip 발생 가능 → guard row를 swap으로 사용 불가, (2) 70% memory usage에서 3× slowdown.

**Siloz[45]**: DRAM subarray(512~2K rows) 단위로 domain을 격리. Subarray 간에는 RH 간섭이 없으므로 guard row 불필요. 그러나:
- 128개 subarray group → **최대 128개 domain만 지원** (coarse granularity)
- Subarray 크기(GB 단위)로 인한 **memory stranding** 심각 (평균 31% of 128GB stranded)
- 11개 workload mix 중 6개만 지원 가능

### 1.3 핵심 요구사항

현대 서버(예: AMD Bergamo 512 hyperthreads)에서는 수천 개의 security domain이 필요하며, domain 크기는 KB(per-page-table)부터 GB(VM)까지 다양하다 (Figure 1b: 대부분의 프로세스는 수 MB 이하, 대부분의 메모리는 소수 대형 프로세스가 점유).

**Citadel의 목표**: 임의의 개수와 크기의 security domain을 지원하면서, memory capacity loss + stranding을 최소화하고, 성능 저하 없이 기존/현재/미래 시스템에 배포 가능한 memory allocator.

---

## 방법론

### 3.1 방법론 개요

| 항목 | 내용 |
|------|------|
| **System** | 2-socket server, 48 logical cores (2.2GHz), 128GB DDR4-2400MT/s |
| **DRAM** | 128K rows × 128 banks, 8KB/row, 512 rows/subarray, 1MB/global row |
| **OS** | Ubuntu 20.04.6 LTS, Linux 5.15.86 |
| **Baselines** | Buddy (no protection), ZebRAM (guard rows), Siloz (subarray isolation) |
| **Workloads** | SPEC2017 (intrate/fprate, ref dataset), GAP (USA-road + Kronecker graph), CloudSuite (data caching, data analytics, in-memory analytics, media streaming) |
| **Background** | 각 서버 평균 75개 background process (μ=4.9MB, exponential 분포) |
| **PT domains** | 각 process의 page table page마다 별도 domain (K MB당 K/2개 4KB domain) |
| **Workload mixes** | 11개 mix (24~57K domains, 31~112GB memory), 각 2시간 실행 |
| **Metrics** | Memory overhead (capacity loss + stranding), Performance (execution time) |

### 3.2 Memory Overhead (§8.1)

**Overall** (Figure 9):
- Citadel: **평균 7.2%** memory overhead (1.5% capacity loss + 5.7% stranding), 최대 16%
- Siloz: 평균 31% overhead (대부분 stranding)
- ZebRAM: 평균 50% loss
- **Citadel만 11개 mix 모두 지원** (ZebRAM 4/11, Siloz 6/11)
- 공통 지원 mix 기준: Citadel은 ZebRAM 대비 **9.8×**, Siloz 대비 **4.5×** 낮은 overhead

**Workload mix별**:
- mix3 (256 SPEC, 65GB): Citadel 5%, Siloz 23%, ZebRAM ❌
- mix9 (48 apps + 512 bg + 56K PT domains, 112GB): Citadel 6%, Siloz ❌, ZebRAM ❌
- mix10 (256 SPEC + 52K PT domains, 105GB): Citadel 7% — 85% memory usage에서도 5% overhead만으로 보안 제공

**85% memory usage 시**: Citadel의 total overhead는 5% — 고부하 환경에서도 실용적.

### 3.3 Performance (§8.2)

- Citadel과 Buddy allocator 모두 memory allocation에 **<1% runtime** 소비
- 40개 workload에서 **평균 4.1% speedup** (최대 +15%/-13%)
- Fine-grained per-domain lock으로 contention 없음
- 모든 mix에서 end-to-end 성능 차이 negligible

### 3.4 Temporal Behavior (§8.3)

Mix10의 2시간 실행 분석 (Figure 11):
- Memory overhead는 6% (128GB 대비), workload 요구량 대비 9%로 안정적 유지
- Ramp-up/down 시에만 상대 overhead 60%까지 spike하나 절대량은 negligible
- 평균 allocation/deallocation rate: **70K pages/sec**, peak 980K alloc + 1.7M dealloc pages/sec
- → High memory churn 환경에서도 Citadel 견고함

### 3.5 Ablation Studies (§8.4)

**Optimization breakdown** (Figure 12a):
| Configuration | Capacity Loss | Stranding | Total |
|--------------|---------------|-----------|-------|
| Chunks only (16-row, no opts) | 7.6% | 7.1% | 14.7% |
| + Zonelets | ↓ | ↓ | 13.7% |
| + Zone expansion/shrinking/splitting | **1.5%** | **5.7%** | **7.2%** |

**Chunk size sensitivity** (Figure 12b):
- Chunk=8: loss 7%+ (worst-case 25%지만 zone expansion이 amortize), stranding low
- Chunk=16: loss <2%, stranding 5.7% → **optimal balance**
- Chunk=64: loss <1%, stranding 증가

**Guard row count** (N_G=2 vs 4, Figure 12c):
- N_G=4: 평균 9% overhead — 미래 더 악화되는 RH 환경에도 gracefully scale

**Complex DRAM mappings** (§8.5):
- Mirroring/inversion/scrambling 시 chunk당 neighbor 수 2~4개 → zone expansion 확률 감소
- Capacity loss 25%까지 증가 가능
- 단, simple mapping을 사용하는 실제 DRAM device 존재 [3, 49]

**Memory sharing impact** (§8.6):
- SPEC+GAP mix에서 refcount>1인 page는 <0.1% — sharing disable overhead negligible
- 공유가 많은 workload에서는 §6.3의 RH-safe sharing mechanism 확장 가능

---

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

| Component | 규모 및 기술 |
|-----------|------------|
| **Citadel core** | ~1,600 LOC C (Linux kernel 5.15 patch) |
| **Override points** | 6개 buddy allocator 함수 (mm/page_alloc.c, mm/memblock.c) |
| **Data structures** | Global chunk bitvector, per-chunk 512B occupancy bitvector, 256KB GRT, per-domain/zone metadata |
| **Domain mapping** | Per-cgroup domain (POC), per-PT domain (emulated) |
| **Bootstrapping** | Kernel boot 시 Citadel 초기화 → metadata zonelet relocation → user process fork 전 security 확보 |
| **Artifact** | Apache 2.0 licensed, Zenodo DOI, VM image 제공 |

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]
- [[paper-wiki/concepts/security.md|Security]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2025MICRO-summarize/citadel-rethinking-memory-allocation-to-safeguard-against-inter-domain-rowhammer-exploits.md|전체 요약 보기]]
