---
tags: [paper, 2024, 2024MICRO, topic/cache]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024MICRO-summarize/temporarily-unauthorized-stores-write-first-ask-for-permission-later.md"
---

# Temporarily Unauthorized Stores: Write First, Ask for Permission Later

**Venue:** 
**저자:** 

## 개요

x86 프로세서의 TSO(Total Store Order) 일관성 모델에서는 store 명령어가 프로그램 순서대로 메모리를 갱신해야 한다. Store의 지연시간을 감추기 위해 현대 프로세서는 Store Buffer(SB)를 사용하지만, SB 용량은 유한하여 SB가 가득 차면 파이프라인이 정지(stall)된다.

SB 확대가 산업계의 주된 대응 전략이었으나 큰 CAM 기반 SB는 면적·에너지·탐색 지연 측면에서 부담이 크다. Intel은 Sky Lake의 56개에서 Alder Lake의 114개까지 SB를 확대했지만, 근본적인 문제는 여전히 존재:

- **장지연 store miss:** LLC에서 miss된 store는 수백 사이클 동안 SB 헤드를 점유하여 후속 store들을 정체시킴 (예: 505.mcf에서 9.6% 성능 손실)
- **Store burst:** store들이 backend에 drain되는 속도보다 빠르게 유입될 때 SB가 막힘 (예: 502.gcc에서 26.2% 성능 손실)

기존 연구들도 한계가 뚜렷함:
- **SSB (Scalable Store Buffer):** 1K-entry FIFO 대기열로 SB 확장하나, store coalescing 미지원, L2 직접 기록으로 에너지 오버헤드 큼, invalidation 시 순차 재생(replay) 복잡도 높음
- **CSB (Coalescing Store Buffer):** 비연속 cache line store coalescing 지원하나, store-wait-free 메커니즘 부재로 장지연 miss 시 파이프라인 정지
- **SPB (Store Prefetch Burst):** burst 감지 시 4KB 페이지 전체 prefetch하나, 불규칙 패턴에 취약, 과도한 prefetch로 load에 악영향 (cache pollution)

**핵심 통찰:** store 명령어의 지연시간은 (1) 진행 중인 모든 store 데이터가 필요한 cache line의 write permission을 획득할 때까지 외부에 보이지 않고, (2) 메모리 갱신이 최종적으로 프로그램 순서대로 이루어지기만 하면 감춰질 수 있다.

## 방법론

### 3.1 실험 방법론

| 항목 | 구성 |
|------|------|
| Simulator | gem5, x86 full-system, Ubuntu 16.04, kernel 4.9.4 |
| Core model | Detailed out-of-order, 8-wide fetch/decode/rename, 12-wide dispatch/issue/commit |
| SB | 114-entry (baseline), 64/32-entry variants |
| L1D | 48KB, 12-way, 5-cycle latency, stream prefetcher |
| L2 | 1MB, 16-way, 16-cycle round-trip (private) |
| L3 | 64MB, 16-way, 34-cycle round-trip (shared) |
| DRAM | 160-cycle latency |
| Coherence | MESI, inclusive L1D/L2 |
| Branch pred. | 64KB L-TAGE + ITTAGE |
| Energy | McPAT, 22nm, 0.6V, Xi et al. 개선 적용 |
| Benchmarks | SPEC CPU2017 (ref), BigDataBench TensorFlow, PARSEC-3.0 (16 threads) |
| Baselines | SSB (idealized), CSB, SPB |
| TUS config | 2 WCBs, 64-entry WOQ, max atomic group size=16 |

### 3.2 성능 결과

**114-entry SB 기준 (단일 스레드 SB-bound):**
- TUS 평균 성능 향상: **3.2%** (최대 26.1% — 502.gcc5)
- SSB: 2.2%, CSB: 1.0%, SPB: -2.2%
- SB-induced stalls: baseline 6% → TUS 2% (평균)
- L1D write access 2× 감소 (최대 5.5× — 502.gcc5)
- L1D miss pending stall: 7.2% → 5.8%

**PARSEC 병렬 워크로드 (114-entry SB):**
- TUS 평균 성능 향상: **3.5%**
- TUS EDP 개선: 5.1% (CSB 2.4%)
- Write access 감소: dedup 4.9×, ferret 2.0× (평균 2.1×)

**EDP 결과 (114-entry SB, 단일 스레드):**
- TUS: **6.4%** EDP 개선
- CSB: 6.1%, SSB: +5.9% (악화) — SSB의 L2 직접 write overhead
- 505.mcf(long-latency store 위주): TUS가 10% EDP 개선

### 3.3 SB 축소 시나리오 (32-entry SB)

TUS의 가장 중요한 결과: **32-entry SB + TUS가 114-entry SB baseline보다 2% 더 높은 성능을 달성**.

- 32-entry SB 대비 단일 스레드 성능 향상: 10.1% 평균 (최대 36.6%)
- PARSEC: 5.8% 평균
- EDP 개선: 단일 스레드 15.7%, PARSEC 10.2%
- SB가 114→32 entry로 줄며: search 에너지 2× 감소, 면적 21% 감소, store-to-load forwarding latency 5→3 cycles 단축
- L1D hit rate: baseline 96.36% → TUS 96.33% (거의 변화 없음 — cache pollution 없음)

### 3.4 Ablation 및 비교 분석

**505.mcf:** Long-latency store가 주된 병목. CSB/SPB의 coalescing/prefetching은 도움 안 됨, SSB-like over-provisioning 필요. TUS는 unauthorized write로 해결.

**502.gcc5:**
Store burst가 주 원인. Coalescing(CSB) + unauthorized write(TUS) 모두 효과적. TUS 26.1% 향상.

**streamcluster:** SPB가 state-of-the-art 중 최고이나, TUS가 L1D miss pending stall을 27% 추가 감소 — TUS는 store를 L1D에 유지하며, SPB는 계속 prefetch하여 load/prefetch 간의 replacement 충돌 발생.

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

TUS 변경 사항 요약:

| Component | 변경 |
|-----------|------|
| Store Buffer | 변경 없음 |
| WCB | Mask + CID(Coalesce ID) 비트 추가 (1비트/WCB, 2 WCB) |
| L1D entry | Visible(1bit) + Ready(1bit) 추가 |
| WOQ | 신규 64-entry circular buffer (272 bytes) |
| Authorization Unit | Lex order 비교 회로 (저장 공간 없음) |

Operation flow:
1. Store는 WCB에서 coalesce → L1D로 write 시도
2. L1D miss + 자원 충분 → unauthorized write, WOQ entry 할당
3. L1D hit + visible → L2 갱신 후 unauthorized write
4. L1D hit + not-visible → cycle → atomic group 병합
5. Permission 도착 → WOQ mask로 data combine → Ready 표시
6. WOQ head의 atomic group이 모두 Ready → 일괄 Visible 전환, head 진행
7. Invalidation 도착 시: CanCycle=false → lex order 검사 → permission 포기 또는 지연

추가 고려사항: Self-modifying code의 경우 L1I 우선 → CanCycle=false로 강제 visible 유도. Store-to-load forwarding은 L1D에서 지원 가능하나 SB에서 이미 오랜 기간 forwarding이 이루어져 추가 성능 이득 미미하여 비활성화.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]


## 전체 요약

[[../paper-summaries/2024MICRO-summarize/temporarily-unauthorized-stores-write-first-ask-for-permission-later.md|전체 요약 보기]]
