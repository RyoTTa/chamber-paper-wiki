---
tags: [paper, 2021, 2021ISCA, topic/cache, topic/dram, topic/nvm, topic/storage, topic/virtual-memory]
venue: "48th Annual International Symposium on Computer Architecture (ISCA 2021)"
year: 2021
summary_path: "../paper-summaries/2021ISCA-summarize/revamping-storage-class-memory-with-hardware-automated-memory-over-storage-solution.md"
---

# Revamping Storage Class Memory With Hardware Automated Memory-Over-Storage Solution

**Venue:** 48th Annual International Symposium on Computer Architecture (ISCA 2021)
**저자:** Jie Zhang, Miryeong Kwon, Donghyun Gouk, Sungjoon Koh, Nam Sung Kim, Mahmut Taylan Kandemir, Myoungsoo Jung (KAIST, UIUC, Penn State)

## 개요

- NVDIMM-N은 byte-addressable persistency와 DRAM-lik performance를 제공하지만, 용량이 4GB~64GB로 제한됨 (배터리 스케일링 한계).
- NVDIMM-N + SSD를 memory-mapped file (MMF/mmap)로 확장하면 OS overhead (context switch, page fault handling, file system, block layer)로 인해 **평균 48% 성능 저하** 발생 (Figure 7a).
- mmap 기반 시스템에서 software overhead (mmap + I/O stack)가 전체 실행 시간의 **69%**를 차지하며, ULL-Flash 자체는 13%에 불과.
- ULL-Flash (Z-NAND 기반)는 기존 NVMe SSD 대비 낮은 latency (4KB read 8μs vs. NVMe SSD의 수십 μs)와 높은 bandwidth (115%~137% 향상)를 제공하지만, 기존 software stack이 이를 충분히 활용하지 못함.
- Optane DC PMM (NVDIMM-P)은 DRAM 대비 6× 낮은 성능, 512GB/DIMM으로 HAMS 대비 낮은 밀도 (2.3TB/DIMM).

## 방법론

### 3.1. Baseline HAMS

- **Address Manager:** 64-bit byte-addressable 주소 공간을 MMU에 노출. NVDIMM을 ULL-Flash의 inclusive cache로 관리.
- **MoS Tag-Array:** NVDIMM에 direct-mapped cache 타입으로 태그 정보 + ECC 비트를 각 cache line에 통합 (Intel Knights Landing MCDRAM 구성 유사).
  - 각 entry: tag, busy bit (B), valid bit (V), dirty bit (D).
  - Cache miss 시: NVMe 명령 2개 생성 (read: ULL→NVDIMM fill, write: NVDIMM→ULL eviction).
- **Power Failure 관리:**
  - ULL-Flash에 supercapacitor 통합 → DRAM buffer를 flash media로 flush.
  - NVDIMM의 pinned memory 영역 (상위 ~512MB)에 NVMe data structure (SQ, CQ, PRP pool, MSI table) 저장 → MMU에서 접근 불가능하도록 보호.
  - Journal tag를 SQ entry에 추가 → power failure 시 미완료 I/O 요청 복구.
- **Hazard Management:**
  - Eviction hazard: NVMe controller와 cache logic이 동일 NVDIMM 위치에 접근하는 문제 → PRP pool로 page 복제 + busy bit로 격리.
  - Redundant eviction: 동일 데이터에 대한 중복 eviction 방지 → wait queue + busy bit 메커니즘.

### 3.2. Advanced HAMS (Aggressive Integration)

- **Register-based Interface:** DDR4 interface 상에서 HAMS controller ↔ NVMe controller 통신.
  - CS# strobe high로 NVDIMM deselection → WE#/CAS#/RAS#로 write command 설정 → 64B NVMe command를 8-cycle burst로 전송.
  - Lock register로 NVDIMM 동시 접근 방지.
- **ULL-Flash 직접 연결:** NVMe controller가 DDR4 bus를 통해 NVDIMM에 직접 접근 → PCIe bottleneck 제거.
  - 기존: NVDIMM ←DDR4→ MCH ←PCIe→ NVMe controller ← flash
  - Advanced: NVDIMM ←DDR4 bus→ NVMe controller (lock register로 arbitration)
- **SSD 내부 DRAM 제거:** HAMS가 NVDIMM으로 모든 I/O 요청을 buffering하므로 SSD 내부 DRAM 불필요 → 17% energy 절감 + 복잡도 감소.

### 3.3. Persistency Control

- Extend mode: 여러 I/O 요청 병렬 처리 가능.
- Persist mode: 단일 I/O 요청만 허용 → 데이터 일관성 보장.
- Journal tag 기반 power failure 복구 절차:
  1. Power failure 감지 → SQ/CQ tail pointer 차이로 미완료 명령 식별.
  2. Journal tag=1인 명령 검색 → SQ 복원 + tail pointer 증가 + doorbell 재호출.

## 핵심 기여

- HAMS는 NVDIMM + ULL-Flash를 **hardware-automated** 방식으로 통합한 최초의 Memory-over-Storage 솔루션.
- **OS-transparent:** 기존 파일 시스템이나 사용자 애플리케이션 수정 없이 TB scale persistent memory 제공.
- HAMS: **97%** 성능 향상, Advanced HAMS: **119%** 성능 향상 (software-based NVDIMM+SSD 대비).
- Energy: HAMS **41%** 절감, Advanced HAMS **45%** 절감.
- Optane DC PMM 대비 높은 밀도 (2.3TB/DIMM vs. 512GB/DIMM)와 높은 throughput (4.5×).
- Memory expansion의 근본적 한계(OS overhead)를 하드웨어 자동화로 해결한 아키텍처적 기여.

## 주요 결과

- **시뮬레이터:** Gem5 full-system simulator + Amber SSD simulator (ULL-Flash detailed modeling).
- **검증:** 실제 800GB Z-SSD prototype과 검증 완료.
- **시스템 구성:** quad-core ARM v8, 2GHz; 64KB L1I/L1D, 2MB L2; NVDIMM 8GB DDR4, 128KB page; ULL-Flash 800GB (3μs read, 100μs write).
- **워크로드:** mmap-benchmark (seqRd/seqWr/rndRd/rndWr), SQLite benchmark (seqSel/rndSel/seqIns/rndIns/update), Rodinia (BFS/KMN/NN).

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2021ISCA-summarize/revamping-storage-class-memory-with-hardware-automated-memory-over-storage-solution.md|전체 요약 보기]]
