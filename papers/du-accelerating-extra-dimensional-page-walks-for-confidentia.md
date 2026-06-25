---
tags: [paper, 2023, 2023MICRO, topic/dram, topic/security, topic/virtual-memory]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023MICRO-summarize/accelerating-extra-dimensional-page-walks-for-confidential-computing.md"
---

# Accelerating Extra Dimensional Page Walks for Confidential Computing

**Venue:** 
**저자:** Dong Du, Bicheng Yang, Yubin Xia, Haibo Chen (Shanghai Jiao Tong University)

## 개요

- **Cloud computing 트렌드:** (1) Confidential computing(Intel TDX, ARM CCA, AMD SEV-SNP)으로 클라우드 제공자를 신뢰하지 않고 보안 민감 애플리케이션 호스팅, (2) Microservices/serverless computing이 기본 computation unit으로 부상 → 노드당 100+ 인스턴스.
- **기존 segment-based isolation 한계:** Intel SGX(PRM), RISC-V PMP(<16 domains) 등 register-based segment isolation은 확장성(scalability)과 granularity에 한계가 있음.
- **Permission table로의 전환:** ARM CCA(GPT), Intel TDX(PAMT), AMD SEV-SNP(RMP)는 permission table을 도입하여 page-level fine-grained isolation 실현. 그러나 이는 page table walk에 **extra dimension**을 추가하여 메모리 참조 횟수를 크게 증가시킴.
  - RISC-V Sv39(3-level page table) 기준: PMP 사용 시 4회 메모리 참조(PT pages 3 + data 1) → 2-level permission table 추가 시 **12회**(PT validation 6 + data validation 2 + data 1 + PT pages 3 = 총 12).
  - Sv48, Sv57 등 deeper page table에서는 더 심각.

## Motivation 분석 (Fig. 3)

- **ld instruction latency (Fig. 3a):** Table-based isolation 시 PMP 대비 평균 **63.4% 증가**, worst-case **91.1% 증가**.
- **Computation-intensive workloads (GAP benchmark, Fig. 3b):** TLB inlining optimization으로 완화 가능 → 평균 5.2%, 최대 9.6% overhead.
- **Real-world cloud applications (Fig. 3c-d):** Serverless(FunctionBench) 최대 **20.3%**, Redis 최대 **31.8%** 성능 저하 → TLB inlining만으로 충분하지 않음.

**핵심 관찰:** Permission table이 유발하는 extra memory reference의 **약 75%**(RISC-V Sv39 기준 8회 중 6회)가 **PT page validation**에 사용됨. 데이터 페이지 validation 비용은 상대적으로 작음.

## 방법론

**핵심 아이디어:** PT pages는 segment(register)로 보호하고, data pages는 permission table로 보호 → segment의 효율성 + table의 확장성 결합.

### 1. PMP Table Hardware Extension (Fig. 5, Fig. 6)

- **기반:** RISC-V PMP (최대 16 entries, 각 entry = addr + config register)
- **T bit (Table mode bit):** 기존 PMP config register의 reserved bit-5에 추가. `T=0` → segment mode (register에 저장된 permission 사용), `T=1` → table mode (PMP Table에서 permission fetch).
- **PMP Table 구조:**
  - 2-level radix tree permission table (mode=0, 다른 값은 reserved)
  - i번째 entry가 table mode면 i+1번째 entry의 addr register가 PMP Table base address를 저장
  - **Root pmpte (Fig. 6c):** V(valid), R/W/X permissions. 모두 0이면 next-level pointer (huge page 개념 차용). RV64에서 1개 root pmpte = 32MB 관리.
  - **Leaf pmpte (Fig. 6d):** 64-bit entry가 16개 4KB page의 permission을 4-bit씩 저장 (R/W/X + reserved 1bit). RV64.
  - **Address indexing (Fig. 6e):** Physical address offset = OFF[1] (root index) + OFF[0] (leaf index) + PageIndex (leaf pmpte 내 index) + PageOffset.
- **Zero new registers/instructions:** 기존 PMP register의 reserved bit만 활용. Prototype은 16 entries → 8개의 PMP Table (128GB), ePMP(64 entries) → 512GB.
- **Switch 유연성:** Runtime에 segment↔table mode 전환 가능. Secure monitor(M-mode)만 HPMP entries 관리.

### 2. Penglai-HPMP Software System (Fig. 7)

**General Memory Segment (GMS) abstraction:**
- 연속된 물리 메모리 영역 + 동일 permission → 하나의 GMS.
- OS가 GMS에 "fast" 또는 "slow" label 부여 (hint).
- Penglai-HPMP secure monitor가 label을 보고 "fast" GMS는 segment mode로, 나머지는 table mode로 isolation.
- N개 fast GMS + unlimited slow GMS. 예: 32GB system, 16 HPMP entries → 1개 monitor용, 4개(2 tables) slow용, 11개 fast.

**Cache-based management:**
- Lower-numbered entries가 higher priority → fast GMS를 낮은 번호 entry에 배정.
- 모든 GMS는 table에도 포함, segment entries는 table의 cache처럼 동작.
- Label 업데이트 시 table 수정 없이 register만 변경.

**OS kernel modification:**
- 모든 PT pages를 단일 GMS에 할당 → "fast" label 부여 → segment mode로 보호.
- 수정량: Linux v5.10 기준 약 700줄 C 코드 추가.
- 기존 연구(Penglai의 PT page trap, ASAP의 contiguous PT prefetching)와 호환.

### 3. Virtualized Environment 확장 (Fig. 8)

- Guest PT(3-level) + Nested PT(4-level) + Permission table(2-level) → **3D page walk** → 최대 16회 메모리 참조.
- **HPMP 적용:** NPT pages를 contiguous region에 할당 → segment mode → 24회 절감.
- **HPMP-GPT:** Guest kernel이 GPT pages도 contiguous하게 배치하고 hypervisor에 "fast" GMS 통보 → 추가 6회 절감 → 최종 **2회 extra reference**만 남음.

## 핵심 기여

1. **Extra-dimensional page walk 비용의 75%가 PT page validation** — segment로 PT page를 보호하고 data page만 table로 관리하는 hybrid 접근이 효과적.
2. **HPMP는 zero new register/instruction**으로 기존 RISC-V PMP의 reserved bit만 활용하여 구현 가능.
3. **Serverless computing에서 14.1% → 3.5%, Redis에서 16.0% → 4.5%** 로 overhead 감소 (BOOM 기준).
4. **Virtualization에서 HPMP-GPT는 16.3%-26.8% overhead**로 감소 — 3D page walk의 실용적 해결책.
5. **PMPTW-Cache와 결합 시 최적** — segment(PT page 제거) + cache(data page 가속) 시너지.
6. ARM CCA, Intel TDX 등 다른 ISA에도 적용 가능한 일반적 설계.

## 주요 결과

### 실험 환경 (Table 1)

| 항목 | Rocket (in-order) | BOOM (out-of-order) |
|------|-------------------|---------------------|
| Frequency | 1 GHz | 3.2 GHz |
| Pipeline | 5-stage scalar | 4-way superscalar, 128-ROB |
| L1 I/D cache | 16KB each | 32KB each (8-way) |
| L2 cache | 512KB (8-way) | 512KB (8-way) |
| LLC | 4MB | 4MB (8-way) |
| L1 I/D TLB | 32 entries, fully-assoc | 32 entries, fully-assoc |
| L2 TLB | 1024 entries, direct-mapped | 1024 entries, direct-mapped |
| PTECache | 8 entries | 8 entries |
| Memory | 16GB DDR3, 25.6 GB/s | 16GB DDR3, 25.6 GB/s |
| Simulator | FireSim (FPGA-accelerated) | FireSim |

### 1. Memory Access Latency (Fig. 10, Table 2)

**Test cases:** TC1(cold), TC2(TLB flushed, cache hit), TC3(warm, neighbor page), TC4(best, TLB hit).

- BOOM ld instruction: PMP Table → PMP 대비 38.9%-91.1% more cycles. **HPMP → 23.1%-73.1% cost reduction.**
- Rocket: HPMP → 47.7%-72.4% cost reduction.
- TLB hit case(TC4): TLB inlining으로 모든 방식 동일 latency.

### 2. OS Operations — LMBench (Table 3, BOOM)

- PMP Table → PMP 대비 평균 **39.03%** latency 증가 (최대: stat 60.33%).
- HPMP → PMP 대비 overhead 거의 제거 (평균 PMPT/HPMP ratio: 128.43%).

### 3. Computation-Intensive — RV8 + GAP (Fig. 11)

- **GAP on BOOM:** PMP Table → 1.8%-9.6% overhead. HPMP → **0.6%-2.4%** overhead.
- **RV8 on Rocket:** PMP Table → 0.0%-1.7%. HPMP → 0.0%-0.5%.

### 4. Serverless Computing — FunctionBench (Fig. 12a-b)

- **BOOM:** PMP Table → 평균 **14.1%** latency 증가 (최대 20.3%). HPMP → 평균 **3.5%** (최대 6.4%).
- **Rocket:** PMP Table → 평균 5.1%. HPMP → 평균 2.0%.
- **Image processing chain (Fig. 12c):** PMP Table → 1.6%-29.7% overhead (이미지 크기 커질수록 감소, computation dominate). HPMP → 0.3%-6.7%.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/security.md|Security]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2023MICRO-summarize/accelerating-extra-dimensional-page-walks-for-confidential-computing.md|전체 요약 보기]]
