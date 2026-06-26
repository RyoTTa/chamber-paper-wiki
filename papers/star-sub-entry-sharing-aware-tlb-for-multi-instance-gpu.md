---
tags: [paper, 2024, 2024MICRO, topic/cache, topic/dram, topic/gpu, topic/virtual-memory]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO 2024)"
year: 2024
summary_path: "../paper-summaries/2024MICRO-summarize/star-sub-entry-sharing-aware-tlb-for-multi-instance-gpu.md"
---

# STAR: Sub-Entry Sharing-Aware TLB for Multi-Instance GPU

**Venue:** IEEE/ACM International Symposium on Microarchitecture (MICRO 2024)
**저자:** Bingyao Li, Yueqi Wang, Tianyu Wang (University of Pittsburgh); Lieven Eeckhout (Ghent University); Jun Yang (University of Pittsburgh); Aamer Jaleel (NVIDIA); Xulong Tang (University of Pittsburgh)

## 개요

- NVIDIA의 Multi-Instance GPU (MIG)는 단일 GPU를 여러 독립 인스턴스로 분할하여 컴퓨팅 자원과 메모리를 완전히 격리하지만, **마지막 레벨 TLB (L3 TLB)는 모든 인스턴스 간에 공유**됨
- 최신 NVIDIA GPU (A100 등)는 L3 TLB의 각 엔트리에 16개의 **sub-entry**를 배치하여 16개의 64KB 페이지 (총 1MB 정렬 범위)에 대한 주소 변환을 하나의 엔트리에 압축 저장 → 하드웨어 오버헤드 줄이면서 TLB reach 향상
- 단일 워크로드에서는 효과적이지만, **멀티 테넌트 환경에서 L3 TLB 공유 시 sub-entry 활용도가 크게 저하**됨 — co-running 애플리케이션 간의 간섭이 TLB thrashing을 유발하여 sub-entry가 완전히 채워지기 전에 eviction 발생
- NVIDIA A100에서 측정한 결과: MIG 활성화 상태에서 co-running 워크로드의 성능이 단독 실행 대비 **최대 50% 이상 저하** (Figure 1)
- 기존 TLB 최적화 기법들 (range TLB, cluster TLB, large page, TLB speculation 등)은 단일 앱에 최적화되어 MIG 환경에서 효과적이지 않음

## 방법론

### 3.1. Sub-Entry Sharing 메커니즘

**공유 조건 (Algorithm 2: TLB Insertion):**
- 새로운 주소 변환이 도착할 때, 해당 set의 모든 엔트리에서 sub-entry 활용도 확인
- 공유 후보 엔트리 조건: (i) 8개 미만의 sub-entry가 사용 중, (ii) 하나의 base address만 점유
- 동일 프로세스의 엔트리가 있으면 우선 선택 (같은 프로세스는 유사한 액세스 패턴을 보임)
- 해당 없으면 가장 낮은 sub-entry 활용도를 가진 엔트리를 선택
- 어떤 엔트리도 공유 조건을 충족하지 못하면 기존 LRU eviction 수행

**레이아웃 결정:**
- 기존 base address의 sub-entry가 연속적으로 점유된 경우 → **Sequential layout** (layout bit = '01'): 마지막 3비트로 sub-entry 인덱싱
- 빈 슬롯이 있는 경우 → **Stride layout** (layout bit = '10'): 첫 번째 3비트로 sub-entry 인덱싱
- non-shared 상태 (layout bit = '00'): 기존 4비트 sub-entry 인덱스 사용

**동적 상태 전환:**
- 공유 상태에서 하나의 base address가 8개 sub-entry를 모두 사용하면 → 다른 base eviction → non-shared 상태로 복귀
- Layout bit, 두 번째 base 메타데이터 리셋, sub-entry 재구성 (4비트 인덱스로)
- 삽입 과정은 critical path에서 벗어나므로 성능에 직접적 영향 없음

### 3.2. TLB Lookup 절차

- L3 TLB에 변환 요청이 도착하면 해당 set의 모든 엔트리를 병렬로 비교
- **non-shared 엔트리 (layout bit '00'):** 4비트 sub-entry 인덱스로 직접 탐색
- **공유 엔트리 (layout bit '01' 또는 '10'):** 두 base address를 순차적으로 확인
  - base address 매칭 후 layout bit에 따라 마지막/첫 번째 3비트 사용
  - **Address Identify Bit (AIB)** 비교로 해당하는 물리적 페이지 번호 확인
- 단일 base 탐색: 40 사이클 (기존과 동일), 두 번째 base 추가 시: 50 사이클

### 3.3. 하드웨어 오버헤드

- 추가 비트: layout bit (2비트) + AIB (16비트: 서브엔트리당 1비트) + 두 번째 base address (30비트) + v/d (2비트) = **엔트리당 50비트 추가**
- 원래 L3 TLB 엔트리: 864비트 → STAR 엔트리: 914비트
- CACTI 22nm 기준: 면적 오버헤드 **1.4%**, 동적 전력 **0.3%** 증가, 누설 전력 **5.3%** 증가
- TLBs는 전체 시스템 동적 전력의 1% 미만을 차지하므로 전체 전력 영향 미미

## 핵심 기여

- **핵심 기여:** MIG 환경에서 L3 TLB sub-entry 활용도 문제를 최초로 식별하고, 동적 공유 메커니즘을 제안
- **성능 향상:** 평균 **28.7%**, 최대 **51.3%** 멀티테넌트 워크로드 성능 향상
- **하드웨어 효율성:** 면적 1.4%, 동적 전력 0.3%의 미미한 오버헤드
- **실용성:** 기존 L3 TLB 구조를 크게 변경하지 않고 확장 가능하며, 다른 TLB 최적화 기법과 호환
- **의의:** GPU 가상화(MIG) 환경에서 TLB 공유로 인한 성능 병목을 체계적으로 분석하고 해결하는 최초의 연구 → 차세대 GPU의 멀티테넌트 격리 설계에 중요한 시사점 제공

## 주요 결과

- **시뮬레이터:** GPU 기반 시뮬레이터 (GPGPU-Sim 기반) 사용
- **하드웨어:** NVIDIA A100 GPU에서 측정한 파라미터 기반 (SM 108개, DRAM 5GB/slice, L1 D-cache 64KB, L2 cache 4MB)
- **L3 TLB 구성:** 16-way set associative, 1024 엔트리, 64KB 페이지
- **워크로드:** Rodinia Benchmark Suite (MT, ATAX, BICG, ST, CONV, NW, C2D, BFS, PR, FFT, FIR 등)
- **멀티 테넌트 구성:** MIG 인스턴스 분할 (3g:2g:2g 또는 3g:3g)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2024MICRO-summarize/star-sub-entry-sharing-aware-tlb-for-multi-instance-gpu.md|전체 요약 보기]]
