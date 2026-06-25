---
tags: [paper, 2022, 2022ASPLOS, topic/cache, topic/dram, topic/virtual-memory]
venue: ""
year: 2022
summary_path: "../paper-summaries/2022ASPLOS-summarize/parallel-virtualized-memory-translation-with-nested-elastic-cuckoo-page-tables.md"
---

# Parallel Virtualized Memory Translation with Nested Elastic Cuckoo Page Tables

**Venue:** 
**저자:** Jovan Stojkovic (UIUC), Dimitrios Skarlatos (CMU), Apostolos Kokolis (UIUC), Tianyin Xu (UIUC), Josep Torrellas (UIUC)

## 개요

### 1.1 가상화 환경에서의 Nested Address Translation 오버헤드

클라우드 컴퓨팅에서는 서버 통합과 격리를 위해 가상 머신(VM)이 널리 사용됨 (Amazon EC2, Microsoft Azure, Google Compute Engine 등). 그러나 가상화 환경에서의 주소 변환(address translation)은 여전히 막대한 성능 오버헤드를 유발.

**기존 Radix Page Tables의 문제:**
- 네이티브 환경에서 x86-64의 4-level radix page table은 최대 4번의 순차적 메모리 접근 필요
- Nested(가상화) 환경에서는 guest page table의 각 level에서 host page table을 통해 gPA→hPA 변환 필요
- 최악의 경우 **24번의 순차적 메모리 접근** 발생 (Steps 1-24 in Figure 2)
- 향후 Intel Sunny Cove 등에서 5-level tree 도입 시 최대 **35번**으로 증가 예정

**기존 완화 기법의 한계:**
- Huge pages (2MB/1GB): 메타데이터 양을 줄이지만根本的인 순차성 문제 미해결
- 더 큰 multi-level TLB, Page Walk Caches (PWC), Nested TLBs: 비용이 증가하는 반면 성능 향상은 제한적
- L2 cache 시간을 초과하는 TLB 접근 시간 (upcoming TB 주 메모리 용량의 상용화와 함께 주소 변환 메커니즘의 재설계 불가피)
- TLB miss 후에도 nested address translation이 애플리케이션 실행 시간의 **50% 이상**을 차지할 수 있음 (References [6,18,38,52])

### 1.2 Hashed Page Tables (HPTs)의 잠재력과 한계

HPTs는 가상 페이지 번호를 hashing하여 테이블 엔트리에 직접 접근하는 방식으로, 이론적으로 **단계 1번**만으로 주소 변환 가능. IBM PowerPC, HP PA-RISC, Intel Itanium에서 구현된 바 있음.

**그러나 HPTs의 전통적 단점:**
- Hash collision 해결 시 메모리 접근 비용 증가 (collision chain walk, OS 호출 등)
- 모든 프로세스가 하나의 HPT를 공유 → multiple page sizes 및 page sharing 지원 불가
- 추가적인 변환 단계 필요 (PowerPC의 two-level translation)

**Elastic Cuckoo Page Tables (ECPTs) [79]:**
- Cuckoo hashing으로 collision 해결 → worst-case constant time lookup
- Process-private HPTs → multiple page sizes 및 page sharing 지원
- Dynamic hash table resizing 지원
- Native 환경에서 경쟁력 있는 설계로 검증됨

## 방법론

### 3.1 Plain Nested ECPT Design

**3단계 nested translation (Figure 4):**

**Step 1: gVA → hPTE**
- gVA의 VPN을 사용하여 gECPTs (PUD/PMD/PTE)의 각 way를 병렬 조회
- 각 gECPT way에서 생성된 gPA를 hECPTs로 변환
- 최악의 경우: `n² × d²` 병렬 접근 (n=3 page sizes, d=3 ways)
- 평균: CWC 사용 시 **2.8번**의 병렬 접근

**Step 2: hPTE → gPA of data page**
- Step 1에서 일치하는 hPTE들의 포인터로 gECPT 엔트리 조회
- gVA VPN과 tag 비교로 목적지 gECPT 엔트리 확인
- 평균: **2.8번**의 병렬 접근

**Step 3: gPA → hPA of data page**
- gPA를 hashing하여 hECPTs에서 최종 hPA 획득
- 평균: **1.6번**의 병렬 접근

**Cuckoo Walk Cache (CWC)의 역할:**
- TLB miss 후 하드웨어가 먼저 CWC를 조회
- Hit 시 ECPT의 어느 ECPT와 어느 way를 접근해야 하는지 사전에 파악
- 최선의 경우: 각 단계에서 단일 메모리 접근만 필요 → **3번의 메모리 접근**으로 nested translation 완료 (Figure 6)

### 3.2 Advanced Nested ECPTs: 세 가지 최적화

#### 3.2.1 Shortcut Translation Cache (STC) (Section 4.1)

**문제:** gCWC miss 시 hardware는 gCWT 엔트리의 host physical address를 알아야 함 → gPA→hPA 변환 필요 → 추가 메모리 접근 및 잠재적 성능 저하

**해결책:** MMU 내에 매우 작은 캐시(STC)를 두어 gCWT 엔트리의 gPA→hPA 변환을 캐싱

- **Nested TLB와 유사한 역할** (radix page tables의 translation을 캐싱하듯 ECPT 메타데이터의 translation을 캐싱)
- 10-entry STC로 **hit rate 약 99%** 달성 (Section 9.4)
- MMU에서 수행되는 L2 miss를 **17%** 감소

#### 3.2.2 Adaptive PTE hCWT Caching (Section 4.2)

**Step 1에서의 PTE hCWT 캐싱:**
- gECPTs는 상대적으로 작고 넓은 범위를 커버 → 매우 높은 locality
- PTE hCWT를 hCWC에 캐싱하면 Step 1의 두 번째 부분에서 효과적

**Step 3에서의 Adaptive PTE hCWT Caching:**
- 애플리케이션에 따라 locality가 크게 차이
- PTE hCWT hit rate가 **0.5 미만**이면 비활성화
- PMD hCWT hit rate가 **0.85 초과**且 PTE가 비활성화된 경우 다시 활성화
- GUPS/SysBench: random access → PMD hit rate 낮음 → PTE 캐싱 비활성화
- 기타 앱: 높은 PTE hit rate → 캐싱 활성화

#### 3.2.3 4KB Page Table Allocation (Section 4.3)

- 현대 hypervisor (KVM) 및 OS 커널은 page table에 **4KB 페이지만 사용**
- PUD-hECPT와 PMD-hECPT를 건너뛰고 PTE-hECPT만 조회 가능
- 초기 walk 비용 감소 (warm-up 기간 95th percentile tail latency 평균 **9.4%** 향상)

### 3.3 Nested Hybrid Design (Section 6)

실용적 마이그레이션 경로: guest는 기존 radix page tables, host는 ECPTs 사용
- 최대 9번의 순차적 단계로 감소 (vs. 기존 24번)
- NTLB로 추가 최적화 가능
- Nested ECPTs 대비 평균 **7%/11%** 느림 (4KB/THP) but 기존 Nested Radix보다 **12%/13%** 빠름

## 핵심 기여

- **최초의 병렬 nested address translation 페이지 테이블 설계** 제안
- 기존 nested radix의 24번 순차 단계 중 **단 3번만**으로 축소 (병렬 접근 활용)
- 4KB pages에서 평균 **1.19×**, huge pages 사용 시 **1.24×** 속도 향상
- MMU busy cycles **25-31%** 감소, L3 MPKI **10-11%** 감소
- Nested Hybrid design을 통한 점진적 마이그레이션 경로 제공
- 물리적 메모리 연속성(contiguity)에 의존하지 않는 설계로 실용적 배포 가능

## 주요 결과

### 4.1 시뮬레이션 환경

- **시뮬레이터:** Simics full-system simulator + SST framework + DRAMSim2
- **시스템 구성:** 8 cores, 80GB main memory, 4 channels, 8 banks
- **프로세서:** 2GHz, 4-issue OoO, 128-entry ROB
- **캐시:** L1 32KB (2 cyc), L2 512KB (16 cyc), L3 2MB/slice (56 cyc)
- **TLB:** L1 DTLB 64 entries (4KB), 32 entries (2MB), 4 entries (1GB); L2 DTLB 1024 entries
- **MMU 구조체 크기:** Nested Radix 1680B, Nested ECPTs 1488B, Nested Hybrid 1408B (Nested Radix 대비 더 작음)
- **_host/guest OS:** Ubuntu Server 16.04 / Ubuntu Cloud 16.04, Hypervisor: QEMU-KVM

### 4.2 평가 대상 애플리케이션

| Domain | Suite | 애플리케이션 | Memory Footprint |
|--------|-------|-------------|-----------------|
| Graph analytics | GraphBIG | BC, BFS, CC, DC, DFS, PR, SSSP, TC | 9-17.3 GB |
| HPC | HPC Challenge | GUPS | 64 GB |
| Bioinformatics | BioBench | MUMmer | 6.9 GB |
| Systems | SysBench | SysBench | 64 GB |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2022ASPLOS-summarize/parallel-virtualized-memory-translation-with-nested-elastic-cuckoo-page-tables.md|전체 요약 보기]]
