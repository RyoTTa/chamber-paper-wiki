---
tags: [paper, 2025, 2025ASPLOS, topic/cache]
venue: ""
year: 2025
summary_path: "../paper-summaries/2025ASPLOS-summarize/necro-reaper-pruning-away-dead-memory-traffic-in-warehouse-scale-computers.md"
---

# Necro-reaper: Pruning away Dead Memory Traffic in Warehouse-Scale Computers

**Venue:** 
**저자:** 

## 개요

Memory bandwidth는 warehouse-scale computing(WSC)의 critical bottleneck으로 부상했다. 일부 최신 서버 플랫폼에서는 50% CPU utilization만으로도 memory bandwidth가 saturation된다[38]. Per-core memory bandwidth는 지난 10년간 정체된 반면, WSC workload의 memory bandwidth 사용량은 지속적으로 증가하고 있다.

**핵심 발견:** WSC 시스템의 memory traffic 중 상당 부분(geomean **41%**)이 **semantically unnecessary**하다. 이 "dead memory traffic"은 두 가지 유형으로 구성된다:

1. **Dead writebacks:** Deallocated(해제된) 데이터가 LLC에서 eviction될 때 memory로 writeback되는 트래픽. 데이터가 이미 free되었으므로 의미 없는 write.
2. **Dead fetch-on-miss:** Freshly-allocated(새로 할당된) 데이터에 대한 initialization write miss 시 memory에서 dead data를 fetch하는 트래픽. Write-allocate cache 정책에서 발생.

**WSC-specific exacerbation:** C++ WSC workload의 allocation rate는 steady-state 기준 평균 **0.62 APKI**(allocations per kilo instructions)로, SPEC CPU 2017의 0.04 APKI보다 **한 자릿수 높다**. 또한 short-lived이면서 cache line(64B)보다 큰 heap object가 geomean **32%**를 차지한다(Fig. 8). 이러한 short-lived large object는 cache hierarchy 내에서 lifetime을 완주할 가능성이 높아, initialization miss → dead writeback 패턴이 집중적으로 발생.

**Fundamental challenge:** Hardware는 heap allocation/deallocation을 알 수 없고, software는 cache eviction/miss를 알 수 없다 → SW/HW co-design 필요.

## 방법론

### 1. Necro-reaper Overview (§3)

**Approach:** WSC의 vertical integration 생태계(profile-guided compiler + customized memory allocator)를 활용한 pragmatic SW/HW co-design. Hardware tracking table 없이 software가 strategic하게 new ISA instruction을 배치하여 hardware가 dead traffic을 회피하도록 유도.

**Target state transitions (Fig. 2):**
- `dead-cached → uncached`: Dead writeback — **save target**
- `uninit-alloced-uncached → cached`: Fetch-on-miss of dead data — **save target**
- `live-cached ↔ live-uncached`: Useful live traffic — not targeted

**Two-pronged approach:**
- **Cache line installation** on allocation → dead fetch-on-miss 회피
- **Cache line invalidation** on deallocation → dead writeback 회피

### 2. Profile-guided Compilation Flow (§3.1, Fig. 3)

**Profiling 단계:**
1. Compiler가 target workload를 instrumentation
2. Profiling input으로 instrumented code 실행
3. 두 가지 profile 수집:
   - **Per-callsite access offset:** 각 allocation site별 평균 initialized portion (allocation size 대비 비율)
   - **Per-size-class reuse distance:** Power-of-two size class별 deallocation→reuse 간 allocated bytes (90th percentile 기준)

**Optimization 단계:**
1. Compiler가 profile 기반으로 (de)allocation call을 custom call로 대체
2. Profile coverage 없는 allocation site는 static heuristic 사용
3. Memory allocator가 custom call에서 new ISA instruction 삽입

### 3. Cache Line Installation (§4.1)

**Static heuristic (profile 미사용 시):**
- Allocation 크기의 initial **75%**를 설치, **최대 128KB** 상한
- 근거 (Fig. 4): (a) Large allocation이 LLC initialization miss의 상당 부분 기여 (≥16KB objects: 35%) (b) Large/small object 모두 유사한 pace로 initialization (c) 대부분의 object가 완전히 initialize되지는 않으나 large object는 상당 부분 initialize됨
- Sequential initialization 경향[11, 45] 활용하여 object 앞부분 설치

**Profile-guided heuristic:**
- 각 allocation callsite별 평균 initialized portion을 profile → 해당 비율만큼만 설치
- Per-allocation max accessed offset을 cache-line granularity로 반올림
- Geomean profile coverage: **85%** (allocation sites 기준)
- 예: 128B object에서 6%만 initialized → 1개 cache line만 설치 (2개 중)

**Memory allocator interface 확장:** `aligned_alloc_install(size, install_portion)` — allocator가 지정된 portion까지 cache line 단위로 `asm_cacheline_install()` 호출

**On-demand installation (Oracle, impractical):** Initialization miss 발생 시 just-in-time 설치 → run-time hardware tracking 필요[36, 45]. Headroom 측정용으로만 사용.

## 핵심 기여

1. **Dead memory traffic의 심각성 최초 정량화:** WSC workload의 geomean **41%** memory traffic이 semantically unnecessary. 특히 C++ WSC workload의 높은 APKI(0.62)와 short-lived large object 비중(32%)이 주요 원인.
2. **Pragmatic WSC-tailored approach:** Vertical integration(PGO compiler + custom allocator)을 활용, hardware tracking table 없이 dead traffic 회피. Profile-guided installation + invalidation으로 oracle headroom의 63% 달성.
3. **실질적 성능 향상:** 10종 WSC workload에서 geomean **26% memory traffic 감소**, **5.9% IPC 향상**, p99 load latency **10.8% 감소**.
4. **Security-aware design:** Userspace invalidation의 보안 위협을 식별하고 OS-based 및 HW-based(invalidatable bit) hardening 제안.
5. **Broader applicability:** Heap 할당을 넘어 file-backed data 등 다른 memory 유형으로 일반화 가능성. WSC의 상당한 untapped 성능 여유 공간을 시사.

## 주요 결과

**Mechanism:** Free 시 deallocated object에 완전히 포함된 모든 cache line에 대해 invalidation instruction 실행. Size-class-based allocator(TCMalloc)가 object size를 알고 있으므로 boundary 계산 가능.

**Profile-guided invalidation skip:** Address space가 빠르게 reuse되는 경우 invalidation이 오히려 해로움 — invalidated line이 새 allocation에서 re-install되지 않으면 bandwidth penalty 발생.

- **Reuse distance** 정의: deallocation 후 해당 virtual address space가 새 allocation에 reuse되기까지의 총 allocated bytes
- Power-of-two size class별 90th percentile reuse distance 측정
- Threshold: **1MB** 미만이면 invalidation skip (L2 cache 크기 수준 — line이 deallocation부터 reuse까지 cache에 생존 가능)
- **Workload-specific:** Search workload는 small size class((64,128])에서 reuse distance 7.2KB로 매우 짧지만, flume은 4.0MB로 길다 → 정적 heuristic으로는 불가능, profile-guided 필수

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]


## 전체 요약

[[../paper-summaries/2025ASPLOS-summarize/necro-reaper-pruning-away-dead-memory-traffic-in-warehouse-scale-computers.md|전체 요약 보기]]
