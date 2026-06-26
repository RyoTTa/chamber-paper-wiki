---
tags: [paper, 2022, 2022MICRO, topic/cache, topic/disaggregation, topic/dram, topic/gpu, topic/virtual-memory]
venue: "MICRO 2022 (55th IEEE/ACM International Symposium on Microarchitecture)"
year: 2022
summary_path: "../paper-summaries/2022MICRO-summarize/designing-virtual-memory-system-of-mcm-gpus.md"
---

# Designing Virtual Memory System of MCM GPUs

**Venue:** MICRO 2022 (55th IEEE/ACM International Symposium on Microarchitecture)
**저자:** Pratheek B*, Neha Jawalkar*, Arkaprava Basu (Indian Institute of Science, Bangalore, India) (*同等한 기여)

## 개요

- 트랜지스터 스케일링 둔화로 단일 모놀리식 칩에서 더 큰 프로세서를 구축하기 어려워짐 → 산업계가 **Multi-Chip Module (MCM)** 디자인으로 전환 중 (AMD Epyc/Ryzen, NVIDIA Grace, AMD MI200, Intel Ponte Vecchio)
- MCM GPU는 패키지 내 **chiplet 간 in-package interconnect**로 연결된 다수의 칩렛으로 구성되나, 논리적으로는 통합된 모놀리식 GPU로 보임 → 물리적 자원의 비균형性(non-uniformity) 초래
- 원격 메모리 접근: chiplet 간 인터커넥트를 이중으로 횡단해야 하며, one-way로 **~32ns 지연** 추가 (NVIDIA 발표 기준)
- 기존 연구 (LASP 등)는 **스케줄링 및 데이터 배치**를 통해 비균형을 완화했으나, **GPU 가상 메모리 시스템에 미치는 영향은 미탐구** 상태
- 데이터 접근이 로컬이더라도, 주소 변환(address translation) 과정에서 원격 chiplet의 자원(L2 TLB, 페이지 테이블)에 접근해야 할 수 있어 성능 제한

## 방법론

### 3.1. 전체 구조 (Overview)

- **MCM GPU 구성:** 4 chiplets, 각 chiplet에 32 CU, 16 메모리 컨트롤러
- **L2 TLB:** 각 chiplet에 512 엔트리, 8-way set-associative, 10 cycle 조회
- **L1 TLB:** 각 CU에 32 엔트리 fully-associative, 1 cycle 조회
- **페이지 워커:** 각 chiplet에 16개, 32 엔트리 fully-associative page cache (10 cycle)
- **interconnect:** 768 GBps 양방향, ~32ns 지연

### 3.2. dHSL (Dynamic HSL) - LASP 기반 주소 매핑

- LASP의 정적 분석이 kernel의 메모리 접근 패턴을 분류: **NL(Non-Local), RCL(Recently-Changed-Local), ITL(Interleaved), Unclassified**
- 가장 큰 데이터 할당의 **LASPBlockSize**를 기반으로 HSL granularity 결정
- LASPBlockSize가 2MB의 배수이면 동일 granularity 사용, 아니면 **closest multiple of 2MB**로 반올림 (dHSL-coarse)
- 가상 주소 할당 시 가장 큰 할당이 먼저 배치되고, **2MB 정렬** 보장 → 원격 L2 TLB 조회 및 원격 PTE 접근 동시 최소화
- Listing 1의 의사코드: 쿼리LASP → largestAlloc 선택 → HSL granularity 결정 → VA/물리 메모리 할당 → PTE 페이지 배치

### 3.3. dHSL-balance - 런타임 불균형 감지 및 전환

- **불균형 감지 메커니즘 (Listing 2, Figure 6):**
  - 각 RTU(Request Translation Unit)에서 incoming/outgoing 요청 수를 epoch(기본 5000 요청)별로 모니터링
  - 불균형 조건: `IncomingRequests / TotalRemoteRequests > 0.8`
  - L2 TLB hit rate > 0.9且 두 연속 epoch에서 불균형 감지 시 CP(Command Processor)가 전환 명령 발송
- **전환 메커니즘 (Figure 6b):**
  - CP가 모든 L1 TLB, RTU, L2 TLB에 HSL switch 메시지 broadcast
  - 비동기 전환이므로 일시적으로 다른 HSL이 혼재할 수 있으나, TLB는 read-only cache이므로 정확성 문제 없음
  - 전환 메시지는 네트워크 트래픽의 **<0.1%**로 미미
  - **dHSL-balance:** fine-grain(4KB) interleaving으로 전환하여 모든 chiplet에 L2 트래픽 균등 분배
  - 불균형 해소 시 **dHSL-coarse로 복귀** 가능 (기본 0.5 임계값, 두 연속 epoch)

### 3.4. PTE 배치 전략

- dHSL-coarse가 2MB 단위로 VA를 chiplet에 매핑하므로, 해당 2MB 영역의 **leaf-level PTE가 포함된 4KB 페이지를 해당 chiplet의 메모리에 배치**
- 상위 레벨 PTE는 어느 chiplet에든 배치 가능 (PWC가 상위 접근 필터링)
- GPU 드라이버가 커널 시작 시 dHSL-coarse에 따라 PTE 페이지 위치 결정 (Listing 1, lines 17-22)

### 3.5. 하드웨어 오버헤드

- CU당 1 레지스터 (HSL 파라미터), RTU당 5개 32비트 카운터
- L2 TLB 엔트리당 `log(numChiplets)` 비트 추가
- **총 상태 오버헤드: 9,344 비트** (4 chiplet 기준)
- Larger page(64KB) 지원: dHSL-coarse granularity를 32MB로 확장

## 핵심 기여

1. **MCM GPU의 가상 메모리 비균형을 정량적으로 분석:** 원격 L2 TLB 조회와 원격 PTE 접근이 성능을 제한하는 두 가지 주요 원인 식별
2. **MGvm은 세 가지 최적화를 통합:** dHSL (aggregate capacity + 로컬리티), dHSL-coarse (PTE 원격 접근 제한), dHSL-balance (런타임 불균형 대응)
3. **Private TLB 대비 52%, Shared TLB 대비 30% speedup** 달성 (평균)
4. **하드웨어 오버헤드 미미:** 9,344 비트 (4 chiplet 기준), 상용 DRAM 호환
5. **Large pages(64KB), 다양한 TLB 크기, walker 수, 인터커넥트 지연에서도 일관된 성능 향상** 유지
6. **UVM(Unified Virtual Memory)과 호환 가능:** 페이지 폴트 핸들러만 확장하면 됨

**Broader significance:** MCM 기반 프로세서가 산업계에서 범용화되는 상황에서, 가상 메모리 시스템의 MCM-aware 설계의 중요성을 처음으로 제시. 특히 LASP의 정적 분석을 재활용하여 기존 소프트웨어 스택과의 호환성을 유지하면서 하드웨어 수준의 최적화를 달성한 점이 실용적 의의가 큼.

## 주요 결과

- **시뮬레이터:** MGPUSim (Go 언어 기반, cycle-accurate)
- **시스템:** AMD GCN 아키텍처 모델링, 4 chiplets × 32 CUs = 128 CUs
- **커널:** 15개 워크로드 (Polybench, AMD App SDK, Heteromark, SHOC, Pannotia)
- **페이지 테이블:** 4KB 기본 페이지, radix tree 구조
- **LASP 연동:** 정적 분석은 compile-time에 수행, MGvm는 이를 런타임 HSL 설정에 활용
- **공개 코드:** Docker 이미지 제공 (Zenodo: 10.5281/zenodo.6937470)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2022MICRO-summarize/designing-virtual-memory-system-of-mcm-gpus.md|전체 요약 보기]]
