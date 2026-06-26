---
tags: [paper, 2025, 2025ISCA, topic/cache, topic/compression]
venue: "ISCA 2025 | **Authors:** Zhewen Pan, Joshua San Miguel (University of Wisconsin-Madison)"
year: 2025
summary_path: "../paper-summaries/2025ISCA-summarize/xor-cache-a-catalyst-for-compression.md"
---

# The XOR Cache: A Catalyst for Compression

**Venue:** ISCA 2025 | **Authors:** Zhewen Pan, Joshua San Miguel (University of Wisconsin-Madison)
**저자:** Zhewen Pan, Joshua San Miguel (University of Wisconsin-Madison)

## 개요

현대 컴퓨팅 시스템은 막대한 SRAM 자원을 캐시에 투자함. AMD Zen3의 32MB L3 캐시는 die area의 약 **40%를 차지** [38]. 데이터셋 크기 증가와 memory wall 문제로 캐시 수요는 계속 증가하지만, 대형 캐시는 반드시 성능 향상으로 이어지지 않으며 높은 access latency(tens of cycles)를 초래함.

기존 cache compression 연구 [3, 8-10, 16, 24, 41, 42, 45-47, 49, 51, 54]는 단일 cache level 내 value redundancy만 활용. 그러나 **inclusive/non-inclusive cache hierarchy에서 LLC와 private cache 간 데이터 중복(inclusion redundancy)은 거의 활용되지 않음**. Strictly inclusive cache의 effective capacity 감소 문제는 잘 알려져 있으나 [15, 26, 37, 40, 48, 55], 단순히 exclusive로 전환하는 것 외에는 해결책이 없었음.

XOR Cache는 이 inclusion redundancy를 압축 기회로 전환. 또한 private cache 간 forwarding으로 decompression을 지원하여 두 가지 redundancy(inclusion + private caching)를 동시에 활용.

## 방법론

### 1. XOR Compression 원리 (Section 3.1)

XOR Cache는 두 cache line의 **bitwise XOR 결과를 단일 slot에 저장**하여 2:1 inter-line compression 달성. XOR의 self-inverse 성질(`A⊕B ⊕ A = B`)로 compression/decompression이 완전히 대칭적이고 극히 단순:

- Compressor: 512개 XOR gate array (64B line 기준)
- Decompressor: 동일 hardware, read 시 한 번의 XOR 연산
- Synthesized delay: 0.12ns → 동일 cycle 내 완료

압축된 line pair는 **minimum sharer invariant** 충족 필요: 두 line 중 최소 하나가 private cache에 shared 상태여야 decompression 가능.

### 2. XOR Policy — Candidate Selection (Section 3.2, 5.1.3)

**기본 XOR (opportunistic):** 임의의 standalone line과 XOR → inter-line 2:1 compression 달성.

**Synergistic XOR (catalyst):** 유사한 값의 line들을 XOR하면 `A⊕B`의 entropy가 감소 → BΔI, BPC 등 intra-line compression scheme의 compression ratio를 추가로 boost.

**Profiling 결과 (Figure 2):**
- idealBank (bank 전체 exhaustive search) + BΔI: compression ratio **2.08×** boost (평균), 최대 **4.7×**
- idealBank + BPC: **2.09×** boost, 최대 **3.0×**
- idealBank + Thesaurus: **2.02×** boost, 최대 **4.6×**

**실용적 구현: Map Table 기반 XOR Policy (Section 5.1.3)**
- Direct-mapped map table (128 entries), map function으로 line value의 signature 생성
- 4가지 map function 평가 (Figure 12):
  - LSH-RP (random projection), LSH-BS (bit sampling)
  - BL (byte labeling), **SBL (sparse byte labeling)** — 하위 byte의 높은 entropy를 제거
- **7-bit SBL**이 coverage-accuracy tradeoff 최적점 → 평균 compression ratio ~2.5

**Map table 동작:**
1. Insertion 시 map value 계산 → map table lookup
2. Hit: valid XOR candidate 존재 → XOR compression 수행, map table entry clear
3. Miss: uncompressed로 insert, map table에 tag pointer 등록

### 3. Cache Coherence Protocol (Section 4)

XOR Cache는 mixed inclusive hierarchy 가정: clean line은 inclusion 유지, dirty line은 exclusion 적용.

**Stable states (Table 1):**
| State | Directory | LLC Data |
|-------|-----------|----------|
| Invalid | ✗ | ✗ |
| Shared | ✓ | ✓ |
| Modified | ✓ | ✗ |
| Shared₀ | ✗ | ✓ |

**Decompression — 3가지 Forwarding Case (Table 2, Figure 7):**

A와 B가 XOR되어 있고, B에 대한 `getS(B)` 요청이 LLC에 도달한 경우:

1. **Local recovery:** B의 requestor가 A의 sharer인 경우. LLC가 `A⊕B`를 requestor에게 전송 → requestor가 local A와 XOR하여 B 복원. (A: Shared 상태)

2. **Direct forwarding:** B의 requestor가 A를 share하지 않지만 B가 sharer 보유. LLC가 B의 sharer에게 요청 forward → B의 sharer가 data 직접 제공. (B: Shared 상태, XOR 불필요)

3. **Remote recovery:** B의 requestor가 A를 share하지 않고 B도 sharer 없음. LLC가 `A⊕B` + fwd-getS(B)를 A의 sharer에게 전송 → A의 sharer가 `A⊕B ⊕ A = B` 계산 후 B's requestor에게 반환.

**UnXORing (Section 4.4):** 3가지 경우에 unXORing 필요
- `getM` (line upgrade to Modified): writer가 값 변경 → LLC copy stale
- 마지막 `putS` (S→S₀ 전환): minimum sharer invariant 위반 방지
- Eviction from S/S₀: tag/data 공간 부족 시

**Deadlock Freedom (Section 4.5):**
- Murphi model checking으로 single-address deadlock freedom 검증
- Multi-address: cyclic dependence 없음 (write-back response가 LLC-bound request와 다른 virtual network)
- 추가 virtual network 불필요

Protocol overhead: transient states **+18.8%**, message types **+18.2%**.

## 핵심 기여

1. **핵심 기여:** Inclusion redundancy를 압축 자원으로 전환한 최초의 cache compression scheme. XOR의 단순성(single-cycle, self-inverse)으로 overhead 최소화.

2. **Catalyst 효과:** XOR compression이 BΔI 등 기존 intra-line scheme과 결합 시 compression ratio를 최대 4.7×까지 boost. SBL map function으로 7-bit만으로도 효과적인 candidate matching.

3. **실용성:** LLC area **1.93×**, power **1.92×** 감소, 성능 overhead **2.06%**에 불과. EDP **26.3%** 개선. Protocol deadlock-free, 추가 virtual network 불필요.

4. **Limitation/Future:** 현재는 2-way XOR만 지원. N-way XOR, 다른 reversible function 적용 가능성 열려 있음.

## 주요 결과

**Organization (Figure 8):**
- Decoupled tag-data array
- Tag entry: `XORed` (1b), `XORPtr` (log₂T bits, partner tag), `DataPtr` (log₂D bits)
- Data entry: `tagptr` (reverse pointer), 64B data
- 8B-segmented data array (Thesaurus 방식, variable size 지원)
- Map table: direct-mapped, 128 entries × tagptr width

**Read flow (Figure 10):**
1. Directory + tag parallel lookup
2. Directory hit (M state) → owner로 forward (normal)
3. Directory hit (S state, standalone) → data array read (normal)
4. Directory hit (S state, XORed) → XORPtr로 partner 찾음 → directory 2nd lookup → forwarding case 결정
5. Directory miss + tag hit (S₀, XORed) → local recovery 또는 remote recovery
6. LLC miss → memory fetch → insertion flow

**Insertion flow (Figure 11, off critical path):**
1. Map function 적용 → map table lookup
2. Hit: tag pointer read → data read → bitwise XOR → XORed data write
3. Miss: tag pointer insert to map table, data insert, tag update

**Write/Upgrade:** XORed line에 write → unXORing → writeback hop → dirty line은 exclusion 적용으로 LLC에서 제거

**Co-eviction:** unXORing → dirty writeback to memory → tag pair eviction (data expansion은 transaction buffer space만 사용 → 추가 eviction 유발하지 않음)

## 평가

### 방법론

| Component | Specification |
|-----------|--------------|
| Simulator | gem5 (Ruby model), full-system |
| Core | 4 OoO cores, 3GHz x86-64 |
| L1I/L1D | 32KB, 4-way, 4 cycles, private |
| L2 | 256KB, 8-way, 9 cycles, private |
| L3 (LLC) | 1MB/bank, 16-way, 40 cycles, shared, 4 banks |
| Memory | DualChannel DDR4-2400 |
| Area/Power | CACTI 7.0 (32nm) |
| Compressor | Synopsys Design Compiler (32nm) |
| Baselines | Uncompressed MSI, BΔI, BPC, Thesaurus, Exclusive, Exclusive+BΔI |
| Benchmarks | PERFECT (image processing), PARSEC 3.0 (simlarge), SPEC CPU 2017 (multi-programmed, 4-core mixes) |
| Simulation | 100B fast-forward + 1B detailed instructions/core |

**LLC Configuration (Table 4):**
- Uncompressed: 1MB data array
- BΔI: 1.3× smaller data array
- Thesaurus/BPC: 1.5× smaller
- **XOR Cache+BΔI: 2.5× smaller data array**
- XOR Cache map table: 128 entries, 14b/entry = 0.22KB

### Compression Ratio (Figure 13, Section 6.3)

XOR Cache+BΔI의 compression ratio:
- Multi-threaded (PERFECT, PARSEC): BΔI 대비 **+23.1%**, Thesaurus 대비 **+23.4%**, BPC 대비 **+4.5%**
- Multi-programmed (SPEC): BΔI 대비 **+34.9%**, Thesaurus 대비 **+18.4%**, BPC 대비 **+28.5%**
- Exclusive+BΔI 대비: multi-threaded **+16.2%**, multi-programmed **+27.8%**

Inter-line compression ratio가 이론적 상한 2.0보다 낮은 이유:
1. Private cache line이 LLC의 최대 1/4만 차지 (LLC:MLC = 4:1)
2. Modified line 존재 → private cache 공간 경쟁 → S line 감소
3. Multi-threaded workload의 data sharing → S non-unique line 비중 높음 → S unique가 적음

### Area & Power (Figure 14, Section 6.4)

**Area:** XOR Cache의 추가 hardware: 0.01mm². 총 LLC area:
- Uncompressed 대비 **1.93× 감소**
- BΔI 대비 **1.56× 감소**, Thesaurus 대비 **1.41× 감소**, BPC 대비 **1.35× 감소**
- Exclusive+BΔI 대비 **1.30× 감소**

**Power:** XOR Cache의 추가 private cache access: 전체의 1.99%에 불과. Network traffic +23.4% (Exclusive LLC의 +24.6%보다 낮음). 총 cache hierarchy power:
- Uncompressed 대비 **1.46× 감소**
- LLC power만: **1.92× 감소**

### Performance Overhead (Figure 15, Section 6.5)

Uncompressed MSI baseline 대비:
- Multi-threaded: **1.45%** slowdown
- Multi-programmed: **2.95%** slowdown (compressibility 낮고 remote recovery path 비중 높음)
- Overall geomean: **2.06%** overhead

### Iso-Storage Performance (Figure 16, Section 6.6)

LLC 크기 민감 workload 대상: XOR Cache는 uncompressed iso-storage LLC 대비 avg **1.78%** (최대 **5.22%**) speedup. BΔI (-2.89%), Thesaurus (1.75%), BPC (1.28%)보다 우수.

### Sensitivity Studies (Section 6.7)

- **8-core:** network traffic +18.7%, performance overhead 1.55% (4-core의 1.45%와 유사)
- **LLC-to-private ratio:** 2:1에서 inter-line compression ratio 증가 (redundancy 증가로 XOR 기회 확대)

### Energy-Delay Product (Figure 18, Section 6.8)

XOR Cache의 EDP: uncompressed 대비 **26.3% 감소** — 모든 scheme 중 최저.

## 구현

- gem5 Ruby memory model에 coherence protocol 구현
- Compressor: Synopsys Design Compiler (32nm), 512 XOR gate array, 0.12ns delay
- Map table: direct-mapped 128 entries, LSH/SBL 기반 map function
- Mixed inclusive coherence (clean=inclusive, dirty=exclusive)
- Explicit eviction/upgrade notification (full bit-vector directory)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/compression.md|Compression]]


## 전체 요약

[[../paper-summaries/2025ISCA-summarize/xor-cache-a-catalyst-for-compression.md|전체 요약 보기]]
