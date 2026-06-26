---
tags: [paper, 2025, 2025MICRO, topic/cache, topic/disaggregation, topic/dram, topic/memory-tiering, topic/security]
venue: "MICRO 2025"
year: 2025
summary_path: "../paper-summaries/2025MICRO-summarize/efficient-security-support-for-cxl-memory-through-adaptive-incremental-offloaded-re-encryption.md"
---

# Efficient Security Support for CXL Memory through Adaptive Incremental Offloaded (Re-)Encryption

**Venue:** MICRO 2025
**저자:** Chuanhan Li (UC Santa Cruz), Jishen Zhao (UCSD), Yuanchao Xu (UC Santa Cruz)

## 개요

CXL memory는 DRAM scaling 한계를 극복할 유망한 기술이나, public cloud 도입을 위해서는 TEE(Trusted Execution Environment)와 CXL IDE(Integrity and Data Encryption)의 통합 보안이 필수적이다. 현재 SOTA baseline인 XTS TEE + CXL IDE는 XTS encryption이 memory read의 critical path에 있기 때문에 memory-intensive workload에서 **최대 14.9% overhead**가 발생한다.

**정량적 동기:**
- DRAM scaling 한계 → CXL로 memory bandwidth/capacity 확장 필요
- CXL 2.0 IDE: 68-byte Flit 단위로 AES-256-GCM encryption + MAC authentication (confidentiality, integrity, replay protection, uniqueness 보장)
- Counterless TEE(AMD SEV, Intel TDX): AES-XTS encryption 사용 — counter metadata 불필요하나, 두 번째 AES 연산이 ciphertext 도착을 기다려야 함 (critical path)
- CTR mode encryption: counter cache hit 시 OTP precomputation으로 latency 대부분 숨김 가능 → **counter cache miss** 시 XTS와 유사하거나 더 큰 overhead

## Motivation Analysis (§3)

### Potential Solutions 분석 (Figure 6, Table 1)

| Design | LLC miss latency | BW | Security metadata | Overflow overhead | Uniqueness |
|--------|-----------------|-----|-------------------|-------------------|------------|
| XTS TEE + CXL IDE (baseline) | High | Medium | 0 update/write | Zero | Yes |
| CTR TEE + CXL IDE | Low~Medium | Low~Medium | 1 update/write | Low | Yes |
| Split CTR TEE + CXL IDE | Low | High | 1 update/write | High | Yes |
| CTR + Integrity Tree | Medium | Low | Multiple updates/write | High | Yes |
| **AIORE (this work)** | **Low** | **Low** | **0 or 1 update/write** | **Nearly Zero** | **Yes** |

### Split Counter Analysis (Figure 7)

4가지 counter scheme 평가 (3b-Split, 7b-Split, 64b-Mono, 3b-Morph):
- 3b-Split: counter cache hit rate 최고, other security overhead 5.8%뿐이나 **overflow overhead 4.3%** + overflow traffic이 data access 대비 45%
- **Observation 1:** Counter overflow overhead와 추가 memory traffic이 CTR TEE의 핵심 bottleneck
- Morphable counter [63]도 2.4% overflow overhead + 20.3% overflow traffic → integrity tree가 없는 SOTA TEE에서는 가정이 맞지 않음

### Counter Light 분석 (Figure 9-10)

Counter Light [82]: BW utilization threshold로 CTR↔XTS mode 전환 (ECC bus로 16B metadata 동시 전송)

- **Figure 9:** BW saturation threshold(0%~100%) 변화에도 성능 거의 불변 → BW-based selection은 strategic하지 않음
- **Figure 10:** Hottest page 비율별 정적 CTR encryption → 최적 configuration에서 **28.2% security overhead 감소**
- **Observation 2:** Access hotness 기반의 CTR/XTS 선택이 hybrid encryption의 혜택을 최대로 활용

---

## AIORE 설계 (§4)

### 1. Design Intuition

**두 가지 핵심 원칙:**
1. **Hotness-aware adaptive encryption:** Hot pages는 CTR-encrypted(낮은 latency + 높은 counter cache hit), cold pages는 XTS-encrypted(counter 유지 불필요 → counter cache pollution 방지)
2. **Incremental + Offloaded re-encryption:** Encryption mode 전환 또는 counter overflow로 인한 page re-encryption을 프로그램 고유의 memory access와 encryption/decryption 과정에 통합 → 추가 overhead 없음. 미완료 page는 CXL memory module로 offload.

## 방법론

**IREBC (Incremental Re-Encryption Bitmap Cache):**
- LRU cache, compute node root complex에 위치
- Entry: 36-bit PFN + 3-bit re-encryption state + 64-bit incremental bitmap (re-encrypting page 전용)
- Backed by in-memory IREBT
- CXL memory PTE의 unused 2-bit로 encryption state 표시 → regular page의 LLC miss 시 IREBC search skip

**Re-encryption state encoding:**
| State | Meaning |
|-------|---------|
| 000 | XTS-encrypted |
| 001 | CTR-encrypted |
| 100 | Re-encrypting: XTS → CTR |
| 101 | Re-encrypting: CTR → XTS |
| 110 | Re-encrypting: Counter overflow |

**Workflow (Figure 13):**
- LLC miss → TLB에서 page encryption state 획득 (PTE의 2-bit)
- Cache writeback → IREBC에서 PFN으로 entry 검색. Miss 시 IREBT read
- **XTS/CTR encrypted page 읽기:** 지정된 mode로 decrypt
- **Re-encrypting page 읽기:** bitmap 확인 → 완료 cacheline은 new mode로 decrypt, 미완료는 old mode로 decrypt
- **Re-encrypting page 쓰기:** 항상 new mode로 encrypt + bitmap 완료 표시
- **Silent eviction:** new mode로 encrypt + bitmap 완료

**Counter overflow handling:** Major counter increment + 모든 minor counter reset을 incremental하게 수행. Write 시 minor counter 0으로 reset + new major counter value로 encrypt.

**Counter cache design:** 3-bit minor counter 채택, cacheline당 2개 major counter (각 64개 minor counter) → 두 page가 독립적으로 re-encrypt 가능.

**초기 상태:** AIORE는 모든 page를 XTS-encrypted로 시작.

## 핵심 기여

1. **AIORE는 CXL memory 보안을 위한 최초의 adaptive hybrid encryption framework**로, page access frequency에 따라 CTR과 XTS encryption을 동적으로 선택하여 평균 **3.7% overhead**(baseline 대비 **62.8% 감소**) 달성.

2. **세 가지 핵심 설계:**
   - **Page hotness tracker:** LLC miss/writeback monitoring으로 CTR/XTS mode 동적 전환 → counter cache pollution 방지
   - **Incremental re-encryption:** 프로그램 고유 memory access에 re-encryption 통합 → 추가 latency zero
   - **Offloaded re-encryption:** 미완료 page를 CXL memory module에서 처리 → critical path overhead 제거

3. **Split counter의 overflow overhead가 CTR TEE의 핵심 bottleneck**임을 정량적으로 입증하고, incremental+offloaded re-encryption으로 24.1% 추가 overhead 감소.

4. **68 KB/CXL module의 적은 면적 오버헤드**로 CXL/PCIe root complex에 통합 가능, Intel Xeon 6th gen 8-module 기준 최대 528 KB.

5. **Broader significance:** CXL memory의 public cloud 도입을 가로막는 보안-성능 tradeoff를 실용적 수준으로 해소. Tiered memory, CXL 3.0 switch 기반 multi-host 환경으로의 확장성 논의.

## 주요 결과

**IREBB (Incremental Re-Encryption Bitmap Buffer):**
- CXL memory module root complex에 FIFO buffer
- Entry: IREBC entry + 256-bit split counter
- IREBC eviction 시 해당 entry + counter cacheline을 IREBB로 전송
- XTS/CTR MEEs가 idle 시 IREBB entry를 순차 처리 → 미완료 cacheline re-encrypt
- 완료 후 PFN response → compute node PTE update
- **Offloaded page 접근 시:** IREBB 첫 entry면 완료까지 block (infrequently used page이므로 성능 영향 미미)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/security.md|Security]]


## 전체 요약

[[../paper-summaries/2025MICRO-summarize/efficient-security-support-for-cxl-memory-through-adaptive-incremental-offloaded-re-encryption.md|전체 요약 보기]]
