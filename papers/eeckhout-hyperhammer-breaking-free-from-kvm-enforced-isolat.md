---
tags: [paper, 2025, 2025ASPLOS, topic/compression, topic/dram, topic/rowhammer, topic/security, topic/virtual-memory]
venue: "ASPLOS 2025 (ACM International Conference on Architectural Support for Programming Languages and Operating Systems)"
year: 2025
summary_path: "../paper-summaries/2025ASPLOS-summarize/hyperhammer-breaking-free-from-kvm-enforced-isolation.md"
---

# HyperHammer: Breaking Free from KVM-Enforced Isolation

**Venue:** ASPLOS 2025 (ACM International Conference on Architectural Support for Programming Languages and Operating Systems)
**저자:** Wei Chen, Zhi Zhang, Xin Zhang, Qingni Shen (Peking University), Yuval Yarom (Ruhr University Bochum), Daniel Genkin (Georgia Tech), Chen Yan (Peking University), Zhe Wang (ICT, CAS)

## 개요

Hardware-assisted virtualization(KVM, Xen, Hyper-V)은 cloud computing의 핵심 enabler로, VT-x/VT-d 같은 하드웨어 기능을 통해 guest VM 간 memory isolation을 제공함. Extended Page Table(EPT)은 GPA→HPA 변환을 위한 두 번째 수준의 page table로, VM 간 분리를 보장하는 핵심 메커니즘.

그러나 **Rowhammer** 취약점은 DRAM row를 반복적으로 activate하여 인접 row의 bit flip을 유발할 수 있음. Rowhammer가 알려진 지 10년 이상 되었지만, hardware-assisted virtualization(HVM) 환경에서 hypervisor 자체를 compromise한 사례는 없었음. 기존 연구들은:

- **Xiao et al. (Xen PVM):** Para-virtualized 환경에서만 가능, 현대 cloud의 HVM에는 적용 불가.
- **Razavi et al. (Flip Feng Shui):** KVM HVM 대상이지만 memory deduplication에 의존 — 이 기능은 보안상 이유로 이미 disable됨 [54, 56]. 또한 co-resident VM만 compromise하고 hypervisor는 침범하지 못함.

**핵심 질문:** "Are modern virtualization platforms vulnerable to Rowhammer attacks?" — 현대 hypervisor에서도 Rowhammer로 hypervisor 자체를 compromise할 수 있는가?

## 방법론

HyperHammer는 3단계로 구성됨: Memory Profiling → Page Steering (Memory Massaging) → Exploitation.

### 1. Memory Profiling (§4.1)

**목표:** Victim row/vulnerable bit와 aggressor row 식별.

**Challenge 1 — Physical address 비공개.** Hypervisor는 VM으로부터 host physical address를 숨김. 그러나 THP가 활성화되면 VM의 2MB hugepage가 host의 2MB physical hugepage로 backing될 확률이 높음. 이 경우 VA의 하위 21비트가 PA까지 보존됨.

**활용:** 현대 x86 프로세서에서 DRAM bank 함수는 PA의 하위 21비트만 사용 (Intel Core i3-10100: bits (17,21), (16,20), (15,19), (14,18), (6,13) / Xeon E3-2124: bits (17,20), (16,19), (15,18), (7,14), (8,9,12,13,18,19)). 따라서 공격자는 GPA 하위 21비트로 DRAM bank를 결정할 수 있고, 2MB hugepage 경계에서 8개 row 중 aggressor row pair를 식별 가능.

**Challenge 2 — Single-sided Rowhammer로 제한.** virtio-mem은 2MB sub-block 단위로 memory를 관리하므로, victim row가 포함된 2MB chunk를 해제하면 인접한 row 중 하나에 대한 접근권을 상실 → double-sided Rowhammer 불가, single-sided로 제한.

**Profiling 절차:** TRRespass로 hammer pattern 식별 → bank/row 조합별 250,000 round hammering → 다른 2MB region scan으로 bit flip 탐지.

**Exploitable bit 필터링:** EPTE의 PFN 비트(bit 12–47) 중 bits 20–⌈log₂(mem_size)⌉ 범위만 타겟팅. Bits 12–20은 동일 2MB hugepage 내로, bits > log₂(mem_size)는 physical memory 범위 밖으로 매핑됨. 16GB 메모리 기준 bits 20–34만 유효.

**결과 (Table 1):** S1(i3-10100)에서 72시간 profiling → 395개 vulnerable bit 중 96개 exploitable (46개 1→0, 50개 0→1). S2(Xeon E3-2124)에서 48시간 → 650개 중 90개 exploitable (49개 1→0, 41개 0→1).

### 2. Page Steering — Memory Massaging (§4.2)

Page Steering은 VM이 hypervisor의 memory 재사용 메커니즘을 조작하여 vulnerable bit 위치에 EPT page가 할당되도록 하는 novel memory massaging 기법. 3단계로 구성됨 (Figure 1).

#### 2.1 Exhausting Free Lists (§4.2.1)

**문제:** EPT page는 4KB(order-0) 크기. virtio-mem으로 해제된 memory는 order-9(2MB) block으로 buddy system에 반환. Kernel은 small-order block을 우선 할당하므로, VM이 해제한 2MB block의 특정 4KB page가 EPT로 재사용되려면 모든 small-order block을 소진해야 함.

**해결 — vIOMMU exploit:** 공격자는 VM 내에서 1개 page를 할당하고, vIOMMU를 통해 해당 page에 대한 I/O virtual address mapping을 60,000개 생성. 각 mapping은 IOPT page(order-0, MIGRATE_UNMOVABLE) 하나를 소비 (각 IOPT page는 512개 entry 포함, 2MB 간격으로 mapping 배치). EPT page도 MIGRATE_UNMOVABLE로 할당되므로, 동일 free list에서 경쟁.

**한계:** vIOMMU는 IOMMU group당 최대 65,535개 mapping만 허용. 다행히 정상 상황에서 MIGRATE_UNMOVABLE small-order block은 50,000개를 넘지 않음 (Figure 3).

#### 2.2 Releasing Vulnerable Pages (§4.2.2)

**문제:** VM은 생성 시점에 address space가 pre-allocated되어 runtime에 memory release가 제한적.

**해결 — Voluntary Page Release via virtio-mem:** virtio-mem에서 hypervisor가 VM에 memory 해제를 요청하지만, **VM이 이를 따르지 않아도 강제하지 않음**을 악용. 공격자는 virtio-mem driver를 수정하여:
- Vulnerable bit가 포함된 page의 GPA를 virtio-mem block/sub-block number로 변환 후 `virtio_mem_sbm_unplug_sb_online()` 호출 → hypervisor가 madvise로 해당 physical page를 kernel free list에 반환.
- 자동 memory 재할당 방지: VM이 voluntary release 시 target allocation과 actual allocation 간 불일치가 발생하는데, 일반 driver는 이를 감지하고 즉시 재할당 요청. 공격자는 이 동작을 disable.

#### 2.3 Creating EPTEs (§4.2.3)

**문제:** VFIO로 PCI passthrough 사용 시 hypervisor는 VM의 모든 address space를 pre-allocate → runtime에 새 EPT page를 생성할 방법이 없어 보임.

**해결 — iTLB Multihit Countermeasure Exploit:**

**iTLB Multihit Bug:** 일부 Intel 프로세서(Comet Lake까지, 2020년 출시)에서 4KB iTLB와 2MB iTLB가 concurrently query될 때, hugepage→4KB page로 mapping 변경 중 stale iTLB entry가 남아 machine check error 발생.

**KVM Countermeasure:** 기본 활성화. 모든 hugepage backed EPTE의 NX bit(bit 2) clear → hugepage 내 code 실행 시 page fault 발생 → hypervisor가 hugepage를 512개의 4KB page로 split → **split 과정에서 새 EPT page 할당.**

**Exploit:** 공격자가 hugepage에 code를 배치하고 실행 → countermeasure trigger → hypervisor가 512개 4KB page로 split하며 1개 EPT page 생성. 이를 spraying 방식으로 확장:

공격자가 \(N\)개의 hugepage(각 2MB, vulnerable bit 포함)를 해제한 후, \(512 \times (N + 2)\)개의 EPT page를 할당하기 위해 \(N + 1\) GB의 memory buffer를 code로 채우고 실행. 이 buffer는 THP에 의해 2MB hugepage로 backing되며, 각 hugepage가 split될 때 1개 EPT page가 생성됨.

**할당 순서:** Header page cache → PCP → small-order free blocks → 해제된 hugepage의 4KB page들. 따라서 \(512 \times (N + 2)\)개 EPT page를 생성하면 해제된 모든 hugepage의 page들이 EPT page로 재사용됨을 보장 (Table 2).

### 3. Exploitation (§4.3)

Page Steering 후 시스템은 vulnerable bit 위치에 EPTE가 배치된 상태. 공격자는 profiling 시 사용한 pattern으로 Rowhammer를 수행하여 bit flip 유발.

**Mapping Change 감지:** VM page에 magic value 기록 → bit flip 후 page scan → magic value 불일치 시 mapping 변경 감지.

**EPT Page 식별:** 변경된 page의 내용을 8-byte 그룹(EPT entry 크기) 512개로 scan:
- 각 그룹이 all-zero이거나 하위 12비트 중 하나라도 non-zero인 large value이면 EPT format match.
- Format match 시 EPT entry를 하나씩 수정하며 magic value 변화 확인 → EPT page임을 검증.

**VM Escape:** 확인된 EPT page의 entry를 수정하여 공격자 VM의 page mapping을 임의의 host physical memory로 redirect → full host memory access.

**성공 확률:** VM memory size / (512 × Host memory size). 공격자 VM에 host memory의 많은 부분이 할당될수록 성공 확률 증가.

## 핵심 기여

1. **최초의 HVM hypervisor compromise Rowhammer 공격.** 기존 연구들은 co-resident VM만 공격했으나, HyperHammer는 hardware-assisted virtualization 환경에서 **hypervisor 자체를 compromise**하는 최초 사례.

2. **Page Steering**이라는 novel memory massaging 기법을 통해 VM이 hypervisor의 page 재사용을 간접 제어 — vIOMMU, virtio-mem, iTLB Multihit countermeasure 등 **정당한 hypervisor feature들의 상호작용을 악용**하는 정교한 공격 체인.

3. **Hypervisor-VM interface의 근본적 취약점 노출:** VM의 memory management request를 hypervisor가 충분히 검증하지 않으면, 공격자가 간접적으로 critical data structure(EPT)의 물리적 배치를 제어할 수 있음.

4. **방어 원칙:** Hypervisor는 VM memory management communication을 quarantine/validate하고, VM action에 의존한 memory allocation을 피해야 함.

## 주요 결과

| System | CPU | DIMM | 비고 |
|---|---|---|---|
| S1 | Intel Core i3-10100 (Ice Lake) | 2×8GB Apacer DDR4-2666 non-ECC | Consumer |
| S2 | Intel Xeon E3-2124 (Coffee Lake) | 2×8GB Apacer DDR4-2666 non-ECC | Server-class |
| S3 | Same HW as S1 | OpenStack DevStack (nova 29.1.0, Libvirt 10.4, QEMU 9.0) | Cloud platform |

**VM 구성:** 4 vCPUs, 13GB memory (12GB for profiling), 1 NIC, Ubuntu 22.04 (modified kernel 6.1.66). Hypervisor: Ubuntu 20.04, kernel 6.1.66, THP enabled.

### Profiling 결과 (Table 1)

| System | Profiling Time | Total Vuln. Bits | Exploitable Bits (1→0 / 0→1) |
|---|---|---|---|
| S1 | 72 hours | 395 | 96 (46 / 50) |
| S2 | 48 hours | 650 | 90 (49 / 41) |

### Page Steering 결과

**Noise page exhaustion (Figure 3):** S1, S2에서 60,000개 vIOMMU mapping으로 noise page(MIGRATE_UNMOVABLE small-order)가 1,024개 threshold 아래로 급감. S3(OpenStack)에서는 초기 noise page가 더 많아 시간이 더 소요됨.

**EPT page 재사용률 (Table 2):** VM이 해제한 page 중 EPT로 재사용된 비율 (\(R_N\))은 memory buffer 크기가 클수록(5GB→10GB), 해제 page 수가 적을수록(100→20) 증가. S2의 경우 \(R_N\)=23.9%, \(R_E\)=51.0% (N=20, S=10GB).

### Exploitation 성공률 (Table 3)

| System | Attack Attempt Time | Time to 1st Success | Attempts to 1st Success |
|---|---|---|---|
| S1 | 4.0 min | 16.7 hours | 250 |
| S2 | 4.7 min | 33.8 hours | 432 |

**End-to-end 예상 시간:** Profiling 포함 시:
- S1: 12개 exploitable bit 발견에 9시간/attempt × 512 attempts ≈ **192일** (13GB VM)
- S2: 6.4시간/attempt × 512 attempts ≈ **137일**
- VM이 host memory의 작은 부분만 할당받으면 attack time은 훨씬 증가.

## 한계점

- 공격에 수개월 소요 (133–188일) — 즉각적 위협은 아님.
- VM에 할당된 host memory 비율이 낮을수록 공격 시간 기하급수적 증가.
- iTLB Multihit bug가 있는 구형 Intel processor(Comet Lake 이하)에서만 가능.
- Non-ECC DIMM 필요 — commodity server는 ECC 채택 중.
- Consumer/Small-server 환경의 proof-of-concept.

## 관련 개념

- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]
- [[paper-wiki/concepts/security.md|Security]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2025ASPLOS-summarize/hyperhammer-breaking-free-from-kvm-enforced-isolation.md|전체 요약 보기]]
