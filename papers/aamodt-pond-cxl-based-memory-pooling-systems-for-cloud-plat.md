---
tags: [paper, 2023, 2023ASPLOS, topic/cache, topic/disaggregation, topic/dram, topic/memory-tiering, topic/virtual-memory]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023ASPLOS-summarize/pond-cxl-based-memory-pooling-systems-for-cloud-platforms.md"
---

# Pond: CXL-Based Memory Pooling Systems for Cloud Platforms

**Venue:** 
**저자:** 

## 개요

Public cloud에서 VM 기반 workload를 서빙할 때, **same-NUMA-node memory 성능**(수십 ns latency)이 gold standard이다. 이를 위해 hypervisor는 VM의 전체 주소 공간을 static preallocation + pinning하며, 이는 SR-IOV 등 virtualization accelerator 호환을 위해 필수적이다.

그러나 DRAM은 서버 비용의 40-50%를 차지하고, **memory stranding**(CPU core는 모두 rented되었으나 unallocated DRAM이 남아 renting 불가능)이 심각한 비용 낭비 요인이다. Azure 100개 production cluster 분석 결과[Fig.2]:

- CPU core 75% scheduled 시 median **6%** DRAM stranded
- CPU core ~85% 시 median **10%+**, **95th percentile 25%** stranded
- Outlier는 최대 **36%** 까지

또한 VM 메모리 사용 패턴 분석 결과, **median VM이 rented memory의 50%를 untouched**(접근하지 않음)[§3.2]. 이 untouched memory를 pool에서 할당하면 latency-sensitive VM도 성능 영향 없음.

기존 memory pooling 솔루션(InfiniSwap, LegoOS 등)은 page fault 기반으로 µs 단위 latency, virtualization accelerator 비호환, guest OS 수정 필요 등의 한계를 가진다.

---

## 방법론

### 3.1 Pond Design Goals

| Goal | 설명 |
|------|------|
| G1 | NUMA-local DRAM과 comparable한 성능 |
| G2 | Virtualization accelerator(SR-IOV, DDA) 호환 |
| G3 | Opaque VM 및 guest OS/application 호환 |
| G4 | 낮은 host resource overhead |

G1을 정량화하기 위해 PDM(Performance Degradation Margin, 허용 가능 slowdown)과 TP(Tail Percentage, PDM 충족 목표 VM 비율)를 정의.

### 3.2 Hardware Layer — External Memory Controller (EMC)

Pond의 핵심 하드웨어는 multi-headed **EMC ASIC**[Fig.6]. 각 host는 CXL port를 통해 EMC에 연결되며, EMC는 자체 DDR5 채널로 pool DRAM을 관리한다.

- **16-socket Pond EMC**: 128 PCIe 5.0 lanes, 12 DDR5 channels → AMD Genoa IOD와 유사한 규모
- **8-socket Pond**: Genoa IOD의 절반 규모
- CXL 3.0의 MHD(Multi-Headed Device)로 표준화됨

**메모리 관리:** EMC는 1GB slice 단위로 메모리를 host에 동적 할당. Host는 CXL device discovery로 pool capacity를 발견, 초기에는 offline 상태. 최대 1024 slice(1TB) × 64 hosts → 768B EMC state. EMC는 per-access permission check로 소유권 강제.

**Failure isolation:** Host는 EMC 간 memory interleaving 하지 않음 → EMC failure 시 해당 EMC의 VM만 영향. CPU/host failure 시 pool memory는 다른 host로 재할당.

### 3.3 System Software Layer — zNUMA

Pool memory는 VM에 **zNUMA (zero-core virtual NUMA) node**로 노출[Fig.10]. zNUMA는 memory는 있으나 core가 없는 NUMA node로, guest OS의 memory allocator가 local vNUMA node를 우선 사용하고, zNUMA는 untouched memory 만큼만 sizing되므로 실제 접근이 거의 발생하지 않음.

**구현:**
- Hypervisor가 SLIT/SRAT 테이블에 `node_memblk`만 추가하고 `node_cpuid`는 생략
- SLIT에 실제 CXL latency 반영하여 guest OS의 NUMA-aware 최적화 활용 가능
- Pool memory는 hypervisor-only专用 partition으로 관리 → 단편화 방지
- 1GB slice offlining: 10-100ms/GB, onlining: µs/GB → 비동기 release로 critical path 회피

### 3.4 Distributed Control Plane — ML 기반 Prediction Pipeline [Fig.11,13]

**VM scheduling 시 (A):**
1. VM request 도착 → distributed ML serving system에 query
2. Workload history 있으면 → **latency insensitivity model**로 pool-only 배치 가능 여부 판단
3. History 없거나 latency-sensitive 예측 → **untouched memory model**로 zNUMA 크기 결정
4. Pool Manager가 EMC에 memory onlining 지시 → hypervisor가 zNUMA topology로 VM start

**QoS monitoring (B):**
- PMU telemetry(1초 주기)로 모든 VM의 memory-bound metrics 모니터링
- Latency sensitivity 재평가 → PDM 초과 시 mitigation trigger
- Mitigation: accelerator 일시 해제 → VM memory 전체를 local DRAM으로 복사 → accelerator 재활성화 (~50ms/GB)
- Untouched memory overprediction 시에도 동일 mechanism 적용

### 3.5 ML Models 상세

**Latency Insensitivity Model [Fig.12]:**
- **Algorithm:** RandomForest (Scikit-learn)
- **Features:** 200개 core-PMU hardware counters (TMA pipeline slot metrics: backend-bound, memory-bound, store-bound, DRAM-latency-bound, LLC MPI, memory bandwidth, memory parallelism)
- **Labels:** Pool memory에서의 relative slowdown (offline test run + internal workload A/B test)
- **Hyperparameter:** FP(false positive rate) 제어 → "몇 %의 VM을 latency insensitive로 분류할 것인가"

**Untouched Memory Model [Fig.14]:**
- **Algorithm:** LightGBM GBM (quantile regression)
- **Features:** VM metadata — customer ID, VM type, guest OS, region, previous VM untouched memory percentiles, workload name
- **Labels:** VM lifetime 동안의 minimum untouched memory (hypervisor access bit scan 기반)
- **Hyperparameter:** OP(overprediction rate) 제어 → "몇 %의 untouched memory를 예측할 것인가"

**Combined Optimization (Eq.1):**
```
maximize: LI(PDM) + UM
subject to: FP(PDM) + OP ≤ (100 − TP)
```
Pond가 자동으로 두 model 간 FP/OP budget을 최적 분배.

---

## 핵심 기여

**핵심 Contribution:**
1. **최초의 대규모 public cloud memory stranding/untouched memory 정량화** — 100개 cluster, 75일간 production trace 분석
2. **CXL pool size-latency tradeoff 최초 분석** — 8-16 socket small pool로 충분, multi-headed EMC로 switch-only 대비 latency 1/3 감소
3. **Pond**: CXL load/store + zNUMA + ML prediction의 full-stack memory pooling 시스템
4. **Opaque VM에서도 적용 가능한 ML prediction pipeline** — PMU counters만으로 latency sensitivity 판별, VM metadata로 untouched memory 예측
5. **실제 Azure production 환경 검증** — 7% DRAM 절감, 1-5% PDM 이내 성능

**Broader Significance:**
- Static preallocation 제약 하에서도 memory pooling이 실용적임을 입증
- CXL이 단순 memory expansion을 넘어 cloud resource disaggregation의 게임 체인저가 될 수 있음을 제시
- ML 기반 resource prediction이 cloud efficiency의 핵심 도구임을 재확인

## 주요 결과

- **System software:** Azure production hypervisor 수정 — zNUMA topology instantiation, core-PMU state를 virtual core metadata에 복사(1초 주기 sampling, 1ms 소요), hypervisor page table access bit scan(30분 주기, 10초 소요)
- **Emulation:** 2-socket 서버에서 한 socket의 core만 disable하고 그 socket의 memory를 pool로 emulation (Intel: 78ns local / 142ns remote, AMD: 115ns local / 255ns remote)
- **Control plane:** 일일 telemetry를 중앙 DB에 수집 → nightly retraining → ONNX export → custom inference serving system
- **Production deployment:** Azure의 Protean VM scheduler에 zNUMA 요청을 추가 dimension으로 bin packing

---

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2023ASPLOS-summarize/pond-cxl-based-memory-pooling-systems-for-cloud-platforms.md|전체 요약 보기]]
