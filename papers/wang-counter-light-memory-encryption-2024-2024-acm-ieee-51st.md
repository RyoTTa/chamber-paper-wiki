---
tags: [paper, 2024, 2024ISCA, topic/cache, topic/dram, topic/security]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024ISCA-summarize/counter-light-memory-encryption.md"
---

# Counter-light Memory Encryption

**Venue:** 
**저자:** 

## 개요

### 1.1 Counter-less Encryption의 한계

Counter-less encryption(AES-XTS 기반)은 data block과 address를 AES 입력으로 사용하여(Fig. 2a), LLC read miss 시 data가 도착한 후에야 data-dependent AES 계산을 시작 가능. 이로 인해 LLC miss latency가 data access latency + AES calculation latency의 합이 됨.

- **실측 결과** (Intel Silver 4314, TME, AES-128): per-access memory latency가 encryption off 대비 **10ns 증가** (AES-128 10-round latency와 일치).
- **Irregular workload 성능**: TME on 시 no encryption 대비 평균 **91%** (9% slowdown). AES-256(14-round, 14ns) 시뮬레이션에서는 평균 **87%** (13% slowdown) — Fig. 5.

### 1.2 Counter Mode Encryption의 Trade-off

Counter mode(AES-CTR)는 counter와 address로 OTP를 생성하여 data와 XOR. Cipher 계산이 data-independent이므로 data 도착 전에 미리 계산 가능. RMCC [74]는 counter value의 AES 결과를 memoization table(4KB)에 캐싱하여, counter 도착 시 재계산 없이 OTP를 빠르게 획득 → 한 counter가 수백만 data block에 의해 공유되어 irregular workload에서도 ≥90% hit rate 달성.

그러나 counter block의 DRAM access가 LLC read miss와 writeback 모두에서 발생하며, irregular workload는 counter cache miss rate가 높아 bandwidth overhead가 큼. Memoization은 latency 문제를 해결하지만 bandwidth overhead는 해결하지 못함.

### 1.3 기존 솔루션의 실패 (Strawman)

- **Lightweight cipher 대체**: PRESENT, PRINCE 등은 AES보다 빠르지만 보안성이 약함. PRINCE는 structural linear relation을 이용한 key recovery attack에 취약 [39].
- **단순 counter mode + memoization만 사용**: counter access 자체가 data보다 늦게 도착하는 경우가 22%의 LLC miss에서 발생(Fig. 8), counter access latency만으로도 평균 7% 성능 저하(Fig. 9) — counter-less의 9%에 근접.

---

## 방법론

### 3.1 방법론

| 항목 | 상세 |
|------|------|
| **Simulator** | Gem5 [11] + Ramulator [49] + DRAMPower [16] |
| **CPU** | 4 OoO cores, 3.2 GHz |
| **Cache** | L1d$/L1i$ 32KB/32KB, L2$ 1MB, L3$ 8MB |
| **Counter cache** | 64KB 32-way |
| **Memoization table** | 128-entry |
| **AES latency** | AES-128: 10ns, AES-256: 14ns (simulated) |
| **Memory** | 128GB DDR5, 25.6 GB/s (baseline), 6.4 GB/s (stress) |
| **Timing** | tCL/tRCD/tRP = 13.75ns |
| **Workloads** | graphBIG (4-thread, Facebook dataset), SPEC2017 (mcf, omnetpp), PARSEC (canneal, streamcluster) — 4-instance multiprogrammed |
| **Warmup** | KVM fast-forward → 25B instr atomic warmup → 20ms atomic + 20ms detailed |

### 3.2 성능 (Fig. 16)

| Metric | Counter-light | Counter-less |
|--------|:---:|:---:|
| No encryption 대비 성능 (AES-128) | **98%** | 91% |
| No encryption 대비 성능 (AES-256) | **98%** | 87% |
| Counter-less 대비 개선 (AES-128) | **+8.6%** | — |
| Counter-less 대비 개선 (AES-256) | **+13.0%** | — |

- **LLC miss latency**: Counter-light는 counter-less 대비 AES-128에서 7.2ns, AES-256에서 11.2ns 평균 절감 (Fig. 17).

### 3.3 대역폭 (Fig. 18)

- 25.6 GB/s DRAM: no encryption 시 평균 utilization 22%, Counter-light 36% — spare bandwidth 충분.
- 6.4 GB/s stress test: utilization 73%까지 증가. Counter-light는 counter-less 대비 최악 **1.4%** 성능 저하 (Fig. 20) — 동적 mode switching으로 counter-less로 fallback.

### 3.4 Ablation Studies

**Dynamic mode switching 제거 시** (항상 counter mode):
- 평균 성능 저하 **20%** (counter-less 대비).
- omnetpp: **51%** 저하 (bandwidth overhead 96%).
- Streamcluster: LLC writeback이 LLC miss의 1% 미만으로 거의 영향 없음.

**Bandwidth threshold 변화** (Fig. 21, 22):
- Threshold 10% → 80% 증가 시, 6.4 GB/s에서 counter-less writeback 비율 100% → 70%.
- Default 60% threshold, 25.6 GB/s 기준: **3%**만 counter-less writeback.

**Regular workload** (Fig. 23): Counter-light 99.5% vs counter-less 96.6% (no encryption 대비) — regular workload에서도 우수.

### 3.5 에너지 (Fig. 19)

Counter-light는 counter-less 대비 **5.1% DRAM energy per instruction 절감** (성능 향상으로 idle DRAM energy 감소). omnetpp만 소폭 증가 (성능 benefit 적음).

---

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

- **Simulation 기반**: Gem5 + Ramulator + DRAMPower. 실제 silicon 구현은 없음.
- **Hardware 변경점**:
  - MC 내 parity 계산 logic에 `EncryptionMetadata` XOR 추가 (4 XOR gate).
  - Memoization table (4KB, 128-entry, 32B/entry).
  - 64KB counter cache (writeback 전용, LLC miss 시 미사용).
  - Barrel shifter + S-Box combining logic (RMCC의 carry-less multiplication 대체).
- **ECC 호환성**: Synergy [63] 기반 — chipkill-correct 유지, 기존 error correction 절차와 호환.
- **기존 시스템 통합**: TME/SME/SEV 등의 counter-less 시스템에 counter mode engine이 이미 존재하는 경우 활용 가능.

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/security.md|Security]]


## 전체 요약

[[../paper-summaries/2024ISCA-summarize/counter-light-memory-encryption.md|전체 요약 보기]]
