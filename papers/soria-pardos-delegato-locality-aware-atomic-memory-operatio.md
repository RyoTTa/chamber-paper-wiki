---
tags: [paper, 2025, 2025MICRO, topic/cache, topic/disaggregation]
venue: "MICRO 2025 (58th IEEE/ACM International Symposium on Microarchitecture)"
year: 2025
summary_path: "../paper-summaries/2025MICRO-summarize/delegato-locality-aware-atomic-memory-operations-on-chiplets.md"
---

# Delegato: Locality-Aware Atomic Memory Operations on Chiplets

**Venue:** MICRO 2025 (58th IEEE/ACM International Symposium on Microarchitecture)
**저자:** Víctor Soria-Pardos, Adrià Armejach, Tiago Mück, Darío Suárez Gracia, Jose Joao, Miquel Moretó (Barcelona Supercomputing Center, UPC, Arm)

## 개요

Chiplet 기반 아키텍처는 monolithic 대비 die size 증가 없이 core count 확장이 가능하지만, interposer를 통한 inter-chiplet 통신 지연이 NUMA 효과를 유발하여 latency-sensitive Atomic Memory Operations(AMO) 성능을 크게 저하시킨다.

**정량적 동기:** NVIDIA Grace CPU Superchip(dual-chiplet)에서 6개 병렬 application 평가 결과(Figure 1), near AMO(near) 대비 centralized AMO(centralized) 성능이 workload에 따라 3가지 category로 분화:
- **Category A:** HIST, RSOR, BC — dual-chiplet에서 centralized가 single-chiplet보다 더 느려짐 (HIST: 0.5× down)
- **Category B:** SPMV, BFS — centralized가 향상되나 near가 더 우수
- **Category C:** LULESH — centralized가 가장 우수

6개 중 4개 application에서 dual-chiplet 전환 시 centralized AMO의 적합성이 감소 → 더 효율적인 AMO execution strategy 필요.

기존 솔루션 한계:
- **Near AMO:** L1D에서 RMW 수행 → cache line ping-pong 발생, inter-chiplet link 대역폭 소모
- **Centralized AMO:** directory로 모든 update 전송 → invalidate로 coherence miss 유발, 모든 update가 fixed per-line location으로 전송되어 interconnect traffic 증가
- **DynAMO [102]:** L1D predictor 기반 near/centralized hybrid → (i) 대부분 near로 보수적 선택, (ii) local L1D 정보만 사용, (iii) coherence miss 감소 불가

## 방법론

### 1. Delegate 및 Migrate Transaction 정의

기존 AMBA CHI protocol에서 지원하는 Near(ReadUnique 기반)와 Centralized(AtomicLoad 기반, directory ALU 필요) 외에 두 가지 새로운 far-AMO transaction 제안:

**Migrate Transaction (Figure 4):**
- Near AMO와 동일한 message flow이나 AtomicLoad request 사용 → directory가 AMO primitives를 구분 가능
- Cache line ownership을 requester의 L2로 이전 → L1D pollution 방지
- 큰 memory footprint에 낮은 reuse를 가진 AMO workload에서 유리 (L1D trashing 방지)
- **실행 예시:** Core 6(C6)이 Core 9(C9) 소유의 cache line에 AtomicLoad 발행 → D14(directory)가 SnpUniq 전송 → C9가 SnpResp로 data 전송 → C6의 L2에서 RMW 수행

**Delegate Transaction (Figure 2c, Figure 4):**
- Directory가 owner에게 SnpAMO 메시지로 RMW operation 전달 → owner가 local에서 RMW 실행 후 ReqAck/Resp를 requester에게 전송
- **핵심 이점:** invalidation 및 cache line transfer 없이 원격 AMO 수행 → coherence miss 완전 제거
- **실행 예시:** C6이 C9 소유 cache line에 AtomicLoad → D14가 SnpAMO to C9 → C9가 local RMW 후 ReqAck+Resp to C6 → SnpResp로 D14에 완료 통지. 3-hop으로 완료 (centralized는 4-hop, Figure 3 Case A).

**Directory ALU 요구사항:**
- Centralized AMO는 directory에 ALU 필요. Floating-point(min, max, add) 지원 ALU를 7nm TSMC, 2GHz 기준 Cadence Genus/Innovus 합성 → **2,894 μm²** (85.4% 부동소수점 RMW, 14.5% bit-wise/simple arithmetic)
- Arm Neoverse V1 core tile(2.52 mm², 7nm) 대비 **0.11%** 증가. Migrate/Delegate는 directory ALU 불필요.

### 2. Static Directory AMO Policies

Directory cache block state에 기반한 5개 static policy 설계 (Table 1). Directory state: UC(Unique Clean), UD(Unique Dirty), RSC(Remote Shared Clean), RSD(Remote Shared Dirty), RU(Remote Unique), I(Invalid).

| Policy | UC/UD | RSC/RSD | RU | I | Directory ALU? |
|--------|-------|---------|----|---|-----------------|
| All-Central | C | C | C | C | 필요 |
| All-Migrate | M | M | M | M | 불필요 |
| Present Central | C | C | C | M | 필요 |
| Pinned Owner | M | M | D | M | 불필요 |
| Unowned Central | C | C | D | M | 일부 불필요 |

- **All-Central:** Default. NVIDIA Grace, AWS Graviton 3/4의 CHI 기반 시스템 기본 정책. Low temporal locality workload에 적합.
- **All-Migrate:** 항상 requester L2로 ownership 이전. L1D 대신 L2에서 RMW 수행 → L1D pollution 방지. Directory ALU 불필요. KME에서 1.44× speedup.
- **Pinned Owner:** CAS-affine. Owner 존재 시 delegate(무효화 방지), 미존재 시 migrate → CAS 실패율 감소. LFQ에서 최고 성능. Figure 8: CAS Counter microbenchmark에서 1.7× speedup, L2 AMO miss ratio 최저.
- **Unowned Central:** RU state에서 delegate, 그 외 centralized/migrate. 위 두 policy의 장점 결합.

**평균 성능 (Figure 7, Near 대비 geomean):**
- All-Migrate: 1.02×, Pinned Owner: 1.26×, All-Central: 1.68×, Unowned Central: 1.69×, Present Central: 1.70×
- Best Static(oracle): **1.85×** → workload별 최적 policy 선택의 중요성 입증

### 3. Chiplet-Aware AMO Policy

Unowned Central 확장. Requester/Owner의 chiplet 위치를 고려 (Table 2):

- **LLC miss → requester 위치 확인:** 동일 chiplet이면 requester로 allocate(Migrate), 원격이면 directory에서 수행(Centralized)
- **Owner 존재 → owner 위치 확인:** Owner가 directory chiplet이면 Delegate, 원격이면 ownership 해제 후 Centralize

**핵심 발견 (Case A/B/C 분석, Figure 5):** Cache line owner가 directory와 다른 chiplet에 있으면 cache line transfer가 inter-chiplet link를 통과해야 함. Chiplet-Aware는 directory chiplet에 owner를 강제하여 cross-chiplet transfer 최소화.

## 핵심 기여

1. **두 가지 새로운 far-AMO transaction(Delegate, Migrate)을 정의하고 구현**하여 chiplet 기반 시스템에서 AMO placement의 선택지를 centralize-only에서 3-way(centralize/delegate/migrate)로 확장.

2. **6개 static policy 중 Pinned Owner policy는 directory ALU 없이 1.26× speedup** 달성 → CAS contention 환경에서 invalidation 제거의 효과 입증.

3. **Delegato trace mechanism**은 private cache의 reuse 정보를 directory에 heartbeat 형태로 전달 → directory가 informed AMO placement 결정을 가능하게 함.

4. **Delegate-based predictor**는 0.17%의 면적 비용으로 DynAMO(state-of-the-art) 대비 1.13×, centralized AMO 대비 1.07× speedup 달성. UCIe 2ns 환경에서도 견고.

5. **Broader significance:** Chiplet 시대의 coherence protocol 설계에서 far-AMO 다양화가 핵심 요소임을 입증. 향후 Armv9.6의 LSFE(floating-point AMO) 등 복잡한 AMO primitive 확산에 대비한 설계 방향 제시.

## 주요 결과

**문제:** Directory는 L2 miss/eviction 정보만 수신 → actual reuse 정보 부재. 최신 core는 L2 cache가 2MB/core로 커져서 LLC가 original access pattern 재구성 불가.

**Delegato Trace Mechanism (Figure 6a):**
- Private cache(L2)에 **Reuse Table**(128-entry, entry당 50-bit: 49-bit TAG + 1-bit reuse field) 배치
- Delegate transaction의 SnpResp 메시지에 **reuse_bit**(1-bit) 추가 → directory가 heartbeat처럼 owner의 cache line 사용 여부 확인
- Reuse Table은 AMO 간 Delegate transaction 사이에 local AMO 발생 시 reuse=1로 설정, transaction 종료 시 reset
- 기존 CHI protocol의 DataPull field 재활용 → 추가 wire 비용 없음

**Predictor Table (Figure 6b):**
- Directory에 128-entry predictor(entry당 56-bit: 49-bit TAG + 5-bit Requester ID + 2-bit policy field)
- 3-state state machine: Chiplet-Aware(CA, default), Present Central(PC), Pinned Owner(PO)
- **상태 전이:**
  - SnpResp[reuse_bit==0] 수신 → PO → PC로 전환 (ownership 회수)
  - 동일 requester가 2회 연속 AMO → PC → PO로 전환 (Migrate로 ownership 이전)
  - New line 또는 requester 변경 → PC → CA 전환

**면적 오버헤드:** Reuse Table 800B + Predictor Table 896B + L2 FP-capable ALU 2,894μm² × 32 cores → 총 0.142 mm². Neoverse V1 32-core system(80.64 mm²) 대비 **0.17%**.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]


## 전체 요약

[[../paper-summaries/2025MICRO-summarize/delegato-locality-aware-atomic-memory-operations-on-chiplets.md|전체 요약 보기]]
