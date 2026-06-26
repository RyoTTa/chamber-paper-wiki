---
tags: [paper, 2025, 2025ASPLOS, topic/dram, topic/rowhammer]
venue: ""
year: 2025
summary_path: "../paper-summaries/2025ASPLOS-summarize/marionette-a-rowhammer-attack-via-row-coupling.md"
---

# Marionette: A RowHammer Attack via Row Coupling

**Venue:** 
**저자:** 

## 개요

**Coupled row**는 DRAM 칩 내부에서 두 개의 서로 다른 DRAM row index(DRI) row가 하나의 wordline을 공유하는 현상이다[28, 44, 45]. Processor-memory interface 관점에서는 두 개의 별도 row로 보이지만, DRAM 칩 내부에서는 동일한 wordline에 연결되어 있어 한 row를 activate하면 coupled row도 동시에 activate된다.

Coupled row는 DDR4 ×4 칩, LPDDR4 칩, HBM2 스택에서 발견되었으며, 2015~2019년 사이 제조된 3개 주요 DRAM 제조사(Mfr.A, Mfr.B, Mfr.C)의 DIMM에서 확인되었다(Table 3). 특히 Mfr.A의 DIMM lot A0, A1, A2에서 각각 10, 8, 14개 인스턴스, Mfr.B B0에서 4개 인스턴스에서 coupled row가 일관되게 발견됨. 2020년 이후 제조된 DIMM에서는 발견되지 않았다.

**핵심 문제:** Coupled row activation은 기존 RowHammer 방어의 근본 가정(aggressor row를 hammering하면 DRI 상 인접한 victim row만 vulnerable)을 무력화한다. Coupled row pair는 physical address(PA) 공간상 멀리 떨어져 있어(MSB 차이), software-level adjacency 기반 방어를 우회할 수 있다. Tested server에서 coupled-row pair 간 PA gap은 `N_row/2`로, 이는 PA의 MSB 1비트 차이에 해당한다.

## 방법론

### 1. Coupled row의 RowHammer 특성 분석 (§4)

**실험 환경:** FPGA 기반 DRAM testing infrastructure (AMD Xilinx Alveo U200/U280) + 45°C 온도 제어. Server 시스템(Table 2): Haswell, Broadwell, Cascade Lake Intel Xeon.

**Hammering pattern 정의 (Table 4):**
- *conventional:* `{q, q+2, ..., q+2k}^{N/k}` — aggressor row 직접 hammering
- *pure coupled-row:* `{Q, Q+2, ..., Q+2k}^{N/k}` — coupled row만 hammering
- *interleaved coupled-row:* `{q, q+2, ..., Q, Q+2, ..., Q+2k}^{N/2k}` — aggressor + coupled row 교차 hammering

**Bitflip 특성 결과 (Table 5, 6):**

| Metric | DIMM A0 | DIMM A1 | DIMM A2 | DIMM B0 |
|--------|---------|---------|---------|---------|
| Overlap ratio (pure, single) | 95.9% | 96.2% | 95.9% | 95.9% |
| Overlap ratio (pure, double) | 96.2% | 96.2% | 96.4% | 98.1% |
| Relative BER (pure, single) | 0.991 | 0.990 | 0.999 | 0.974 |
| Relative BER (pure, double) | 0.997 | 0.994 | 1.000 | 0.997 |
| Overlap ratio (interleaved, single) | 96.7% | 96.5% | 96.3% | 96.0% |
| Overlap ratio (interleaved, double) | 96.3% | 97.1% | 97.1% | 97.9% |

모든 DIMM에서 bitflip 위치 overlap >95%, relative BER >0.97. RowPress 패턴(7.8μs interval, 5K hammering)에서도 overlap 90.7~91.5%, relative BER 0.982~0.992.

**결론:** Coupled row는 conventional aggressor와 거의 동일한 RowHammer 능력을 가진다.

### 2. In-DRAM TRR의 Coupled row 처리 (§4.2)

U-TRR[17]을 이용해 Mfr.A의 counter-based in-DRAM TRR을 reverse-engineering:
- Bank당 4개 address buffer 보유
- Buffer management: 최초 4개의 ACT address를 capture, 나머지는 discard (counting 없음)
- Capture된 address의 victim row들에 대해 refresh 수행
- 매 몇 번의 REF command마다 mitigation trigger, 이후 모든 buffer flush

**Coupled-row pair는 단일 entry로 관리됨 (Case 1, Fig. 4).** Verification test: ACT sequence `0xq, 0xQ, 0xr, 0xR, 0xs, 0xS, 0xt, 0xT` 수행 후 모든 victim(0xq/Q, 0xr/R, 0xs/S, 0xt/T)이 mitigation 대상이 됨 → Case 2(별도 entry)였으면 0xs/S, 0xt/T가 lost 됨.

→ In-DRAM TRR은 coupled row에 대해 conventional과 동일한 보안 보장을 제공한다. 그러나 in-DRAM TRR 자체가 tailored attack으로 우회 가능하다는 것이 알려져 있음[10, 13, 21, 35].

### 3. System-level Coupled row 특성 (§5)

**Coupled row 식별:** Row buffer conflict timing과 perf counter(ACT/PRE command count)로 coupled-row pair와 SBDR(same-bank-different-row) pair가 구분 불가능함을 확인 → Memory controller는 coupled row를 인지하지 못한다.

**PA space gap:** Tested system(System-a~d)에서 PA의 MSB가 DRI의 MSB에 해당. Coupled-row pair는 PA space에서 큰 gap 존재. 6 DIMM/socket 구성(System-e)에서는 row bit이 PA의 MSB에 위치할 가능성이 더 커져 gap이 더욱 증가.

**Blacksmith[21] 변형 실험:** Coupled-row pair 중 하나만 hammering → 인접 victim row(q±1) 뿐만 아니라 coupled-row victim row(Q±1)에서도 bitflip 발생 확인.

## 핵심 기여

1. **새로운 RowHammer attack vector:** Coupled row는 기존 소프트웨어 방어의 근본 가정(DRI adjacency)을 무력화하며, tracking-based(SoftTRR)와 isolation-based(Siloz) 방어 모두 우회 가능.
2. **End-to-end exploit 입증:** SoftTRR-protected server에서 privilege escalation 성공 — 최초의 coupled-row 기반 end-to-end exploit.
3. **Attack amplification:** Bare metal 시스템에서도 1.66× 성공률 향상.
4. **Low-cost mitigation:** DRAM hardware 수정 없이 SPD 정보 노출 + 기존 소프트웨어 방어 로직의 경미한 수정으로 방어 가능.
5. **Broader impact:** LPDDR4, HBM2 등 다양한 DRAM type에서 coupled row 발견됨 → 향후 DRAM 세대에서도 보안 위협 가능성. 제조사가 coupled row optimization의 보안 위험을 인지하고 사용을 중단할 것을 권고.

## 주요 결과

#### 4.1 Tracking-based 방어 우회 (SoftTRR[74])

SoftTRR은 page fault handler hooking으로 page table adjacent page의 access count를 tracking하고, threshold 도달 시 victim row refresh 수행.

**우회 메커니즘 (Fig. 6):** Attacker가 page table에 인접한 row 대신 그 coupled row를 hammering → SoftTRR은 이 access를 감지하지 못하지만, coupled row activation으로 실제 aggressor가 동시에 activate되어 page table에 RowHammer bitflip 발생.

**End-to-end exploit (System-a, Linux v4.4.220, ECC-disabled):**

4단계 공격 flow:
- **S1 (Preparing aggressor rows):** Buddy allocator massaging으로 PA-contiguous 2MB 영역 확보. DRAMA[50]로 DRAM address mapping 파악 → aggressor row 준비
- **S2 (제외):** Victim row에 대한 write 권한이 없으므로 memory templating 불필요
- **S3 (Page table spraying):** mmap 반복 호출로 PTE를 remote victim row 위치에 배치. Coupled-row aggressor에 PTE-like data pattern이 자동으로 채워져 unwanted bitflip 억제
- **S4 (Hammering):** k-assisted double-sided pattern 사용 (DIMM별 최적 k: A0=12, A1=14, A2=14, B0=2). HC 선택 시 inverted-case HCfirst(FPGA: ~125K, System-a: ~150K)와 identical-case HCfirst(FPGA: ~440K, System-a: ~625K) 사이의 gap 활용 (Fig. 7)

**결과:** SoftTRR-protected System-a에서 privilege escalation 성공 (PTE → 다른 PTE redirect).

#### 4.2 Isolation-based 방어 우회 (Siloz[41])

Siloz는 VM memory를 subarray group 단위로 provisioning하여 cross-VM RowHammer 방지. Sense amplifier가 subarray 간 물리적 barrier 형성.

**우회 메커니즘 (Fig. 5):** Coupled-row pair가 서로 다른 subarray group에 걸쳐 있을 경우, attacker가 자신이 제어하는 row를 hammering → isolated region 내 coupled row를 puppetize하여 remote victim row에 double-sided attack 수행.

**참고:** Multi-DIMM setup에서 DRAM addressing function 식별 복잡성으로 인해 Siloz에 대한 실제 RowHammer 공격은 수행하지 않음 (future work).

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]


## 전체 요약

[[../paper-summaries/2025ASPLOS-summarize/marionette-a-rowhammer-attack-via-row-coupling.md|전체 요약 보기]]
