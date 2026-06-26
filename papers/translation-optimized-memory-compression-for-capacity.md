---
tags: [paper, 2022, 2022MICRO, topic/cache, topic/compression, topic/dram, topic/virtual-memory]
venue: "55th IEEE/ACM International Symposium on Microarchitecture (MICRO 2022)"
year: 2022
summary_path: "../paper-summaries/2022MICRO-summarize/translation-optimized-memory-compression-for-capacity.md"
---

# Translation-optimized Memory Compression for Capacity

**Venue:** 55th IEEE/ACM International Symposium on Microarchitecture (MICRO 2022)
**저자:** Gagandeep Panwar, Muhammad Laghari, David Bears, Yuqing Liu, Chandler Jearls, Esha Choukse, Kirk W. Cameron, Ali R. Butt, Xun Jian (Virginia Tech / Apple / Microsoft Research)

## 개요

- 메모리는 컴퓨팅 비용의 상당 부분을 차지: AWS VM에서 메모리 2배 → 총 비용 2배 (예: 0.5GB→1GB VM)
- 하드웨어 메모리 압축은 실제 DRAM 비용 없이 effective memory capacity를 증가시키는 기술
- 기존 하드웨어 메모리 압축 기법들은 **memory block level** (256B~512B chunk)에서 압축 및 데이터 마이그레이션 수행 → **block-level address translation** 추가 필요
- Block-level translation은 page-level virtual address translation 위에 serial로 발생 → **address translation 문제 악화**
- 대용량/불규칙 워크로드는 TLB miss rate가 높고, CTE (Compression Translation Entry) miss rate도 유사하게 높음
- Compresso (SOTA): 4KB 범위의 물리 주소 변환에 64B CTE 필요 → CTE는 PTE 대비 **8배 더 큰 공간** 요구
- CTE cache는 64KB → 1K pages만 도달 가능 → 불규칙 워크로드에서 높은 miss rate

**CTE miss의 two key challenges:**
- **Challenge A:** Cold page가 다시 hot이 되어 마이그레이션될 때 page-level translation 오버헤드 발생
- **Challenge B:** Cold page만 압축하면 aggressive 압축 필요 → 해제 시 **>800ns latency** (IBM state-of-the-art ASIC Deflate 기준)

## 방법론

### 3.1. ML1 Optimization: PTB Compression + CTE Embedding

- **PTB 압축 관찰:** 인접 PTE의 status bits가 동일하고, PPN의 상위 비트가 동일 (Figure 6, 7)
- **압축된 PTB 형식:** Status bits 1회 저장 + PPN 상위 비트 truncate → 자유 공간에 CTE embedding
  - 4TB 물리 메모리 시스템: 상위 10 bits truncate 가능
  - 각 compressed PTB에 최대 8개 CTE (4KB 범위 식별 가능, log₂(1TB/4KB) = 28 bits per CTE)
- **CTE Buffer:** 64 entries (~1KB), PPN를 key로 사용하여 lookup
- **Page walk 흐름 (Figure 11):**
  1. TLB miss 시 page walker가 L2에서 PTB 접근
  2. L2가 PTB 내 CTE를 CTE Buffer에 저장
  3. 다음 page walker 접근 또는 data access 시 CTE Buffer에서 CTE 조회
  4. CTE cache miss 시 embedded CTE로 DRAM 접근을 병렬로 수행 (speculative)
  5. 실제 CTE와 비교하여 correct/incorrect 판단
- **평균 22%의 LLC miss가 병렬 data access로 만족** (correct embedded CTE)
- **Uncommon case (<3%):** Embedded CTE 불일치 → CTE from DRAM으로 재접근
- **Overhead:** PTB decompression ≤1 cycle (wiring concatenation), Recency List가 DRAM의 0.4% 사용

### 3.2. ML2 Optimization: Memory-Specialized ASIC Deflate

- **목표:** IBM ASIC Deflate (1100ns/4KB page) 대비 4× faster decompression
- **Huffman 최적화:**
  - **Reduced Huffman tree:** 286 codes → **16 codes**로 축소 (15 hottest characters + 1 escape code)
  - Tree를 **uncompressed format**으로 저장 → tree decompression overhead 제거
  - Compression ratio 감소: 평균 1% ( negligible)
  - Dynamic Huffman skip으로 추가 5% compression ratio 개선 가능
- **LZ 최적화:**
  - CAM size: 32KB → **1KB**로 축소 → compressor 0.060mm², decompressor 0.022mm² (7nm)
  - RFC 1951의 286-symbol alphabet → **256-symbol alphabet** 사용 (9-bit → 8-bit 출력)
  - Compression ratio 감소: 1.6% (non-zero memory pages)
- **Cross-Deflate 최적화:** LZ와 Huffman을 **독립 페이지에 병렬 처리** → throughput 향상
- **구현:** Chisel HDL → Synopsys Design Compiler (7nm ASAP, 0.7V, 2.5GHz)

### 3.3. ASIC Deflate 성능

| 모듈 | 면적 | 지연시간 | Throughput |
|------|------|---------|-----------|
| Decompressor | 0.022 mm² | 277 ns | 14.8 GB/s |
| Compressor | 0.060 mm² | 662 ns | 17.2 GB/s |
| **IBM Decompressor** | - | **1100 ns** | 3.7 GB/s |
| **IBM Compressor** | - | 1050 ns | 3.9 GB/s |

- **Half-page decompression latency:** IBM 대비 **6× faster** (140ns vs 878ns)
- **Total throughput:** 32.0 GB/s (DDR4-3200 channel bandwidth 25.6 GB/s 초과)
- **Total area:** 0.13 mm² (완전한 unit)
- **Compression ratio:** Geomean **3.4×** (GZIP 대비 12% 낮음)

## 핵심 기여

- **핵심 contribution:** Hardware memory compression에서 large/irregular workloads의 address translation 문제를 최초로 해결
- **성능:** Compresso 대비 동일 DRAM 절약 시 **14% 성능 향상**, 동일 성능 시 **2.2× effective capacity** 제공
- **ML1 최적화:** PTB 압축 + CTE embedding으로 page walk 중 병렬 CTE prefetch → CTE cache miss 시 latent 숨김
- **ML2 최적화:** Memory-specialized ASIC Deflate로 IBM 대비 **4× faster decompression** (277ns vs 1100ns)
- **의의:** 데이터센터/클라우드 환경에서 메모리 비용 절감과 성능 향상을 동시에 달성하는 실용적 하드웨어 메모리 압축 솔루션 제시

## 주요 결과

- **구현 언어:** Chisel (HDL), Verilog
- **공정:** 7nm ASAP technology node
- **설계 도구:** Synopsys Design Compiler (합성), Verilator (RTL 시뮬레이션)
- **시뮬레이터:** Gem5 (CPU), Ramulator (DRAM)
- **DRAM:** DDR4-3200, 1-channel, 8-ranks
- **캐시:** 64KB L1d$/L1i$, 256KB L2$ (inclusive), 8MB L3$ (exclusive)
- **CPU:** 4 cores, 2.8GHz, 4-wide OoO, 2048 TLB entries
- **CTE cache:** TMCC 64KB (32KB reach per 64B CTE block), Compresso 128KB (4KB reach)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2022MICRO-summarize/translation-optimized-memory-compression-for-capacity.md|전체 요약 보기]]
