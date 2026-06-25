---
tags: [paper, 2024, 2024HPCA, topic/dram, topic/gpu, topic/nvm, topic/pim]
venue: "IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2024"
year: 2024
summary_path: "../paper-summaries/2024HPCA-summarize/pathfinding-future-pim-architectures-by-demystifying-a-commercial-pim-technology.md"
---

# Pathfinding Future PIM Architectures by Demystifying a Commercial PIM Technology

**Venue:** IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2024
**저자:** Bongjoon Hyun (KAIST), Taehun Kim (KAIST), Dongjae Lee (KAIST), Minsoo Rhu (KAIST)

## 개요

- 과학연산, 그래프 처리, 머신러닝 등에서 메모리 대역폭 병목이 핵심 성능 제약 요건으로 부상 (von-Neumann 아키텍처의 프로세서-메모리 성능 격차)
- PIM(Processing-in-Memory)은 수십 년간 탐구되어 왔으나, 높은 설계 오버헤드(예: DRAM 밀도 저하 [68])와 소프트웨어 스택의 침투성(프로그래밍 모델 [34], [52], 주소 공간 관리 [5], [19])으로 인해 상용화되지 못함
- 최근 Samsung [62], [67], [78], SK Hynix [50], [77]의 도메인 특화 PIM과 UPMEM [126]의 범용 PIM이 시장에 등장
- Facebook(2021): "PIM의 가장 큰 도전은 프로그래밍 가능성(programmability). 모델 압축 방법을 예측하기 어렵고, 유연한 병렬화 지원이 필요"
- 기존 PIM 시뮬레이터들(PIMSim [131], Ramulator-PIM [2], MultiPIM [134], MPU-Sim [128])은 범용 PIM ISA를 지원하지 않음 → 상용 PIM에 대한 정밀한 특성 분석 및 구조적 탐구 불가

## 방법론

### 3.1. UPMEM-PIM 하드웨어 아키텍처 (Fig. 1)

- **시스템 구성**: 호스트 CPU + 표준 DDR4 DIMM + UPMEM-PIM DIMM
- UPMEM-PIM DIMM: DDR4-2400 폼팩터, rank당 8개 UPMEM-PIM DRAM 칩
- 각 DRAM 칩: **8개 DPU**(DRAM Processing Unit), bank당 1개 DPU
- **DPU 메모리 구조**:
  - Main RAM (MRAM): bank당 64MB DRAM
  - Working RAM (WRAM): 64KB SRAM scratchpad
  - Instruction RAM (IRAM): 24KB 명령어 메모리
- **DPU 마이크로아키텍처**:
  - In-order 14-stage 파이프라인, RISC 기반 ISA
  - Fine-grained multi-threading: DPU당 최대 24개 tasklet 동시 실행
  - **Revolver Pipeline**: 같은 스레드의 연속 명령어 dispatched 간 11사이클 제약 → 데이터 포워딩 및 파이프라인 인터록 회피
  - **Register File 구조적 해저드**: RF가 even/odd로 분리, 같은 사이클에 r0과 r2 동시 접근 불가

### 3.2. uPIMulator 시뮬레이션 프레임워크

- **소프트웨어 파이프라인**: C 소스 → UPMEM LLVM 컴파일러 → 어셈블리 → 커스텀 링커 → 기계어 바이너리 → 사이클 레벨 시뮬레이터
- **검증**: 실제 UPMEM-PIM 시스템과 교차 검증 (Fig. 4: 387개 데이터 포인트, 상대 오차 26.9% 이하)
- **시뮬레이션 속도**: 평균 3KIPS (GPGPU-Sim과 동등 수준)
- **기존 PIM 시뮬레이터 비교 (Table III)**:

| 시뮬레이터 | ISA | 프론트엔드 | 실물 검증 | 멀티스레드 | LoC |
|-----------|-----|-----------|----------|-----------|-----|
| PIMSim [131] | x86/ARM/SPARC | Trace | X | X | 30K |
| Ramulator-PIM [2] | x86 | Trace+Execution | X | O | 35K |
| MultiPIM [134] | x86 | Trace+Execution | X | O | 92K |
| MPU-Sim [128] | PTX | Execution | X | X | 12K |
| **uPIMulator** | **UPMEM** | **Execution** | **O** | **X** | **52K** |

### 3.3. 워크로드 특성 분석 (Section IV)

#### 3.3.1. 연산/메모리 대역폭 활용도 (Fig. 5)

- PrIM 벤치마크 16개(BFS, BS, GEMV, HST-L, HST-S, MLP, NW, RED, SCAN-RSS, SCAN-SSA, SEL, SpMV, TRNS, TS, UNI, VA) 평가
- BS와 SpMV를 제외하면 대부분 **compute-bound** 경향 → PIM의 핵심 가치: 메모리 병목이 연산 병목으로 전환
- DPU 최대 DRAM 대역폭: 이론 700 MB/sec, 실제 ~600 MB/sec

#### 3.3.2. 병목 분석 (Fig. 6, 7, 8, 9)

- **지연 시간 분해 (Fig. 6)**: 스케줄러 유휴 상태를 세 가지로 분류:
  - Memory idle: 메모리 연산 대기 (BS, SpMV에서 높음)
  - Revolver idle: 파이프라인 스케줄링 제약 (GEMV, HST-S, MLP, RED, TRNS, TS에서 높음)
  - RF idle: odd/even 레지스터 파일 구조적 해저드 (BFS, NW, SCAN-RSS/SSA, SEL, UNI에서 높음)
- **스레드 수준 병렬성 (TLP) (Fig. 7)**: 스케줄러가 파이프라인에 발급 가능한 스레드 수 분석. 낮은 TLP를 보이는 워크로드가 낮은 연산 활용도
- **시간에 따른 TLP 변화 (Fig. 8)**: BS는 일관되게 낮은 TLP, GEMV는 일관되게 높은 TLP, SCAN-SSA는 고-저 혼합
- **명령어 혼합 (Fig. 9)**: load/store(scratchpad) > DMA(DRAM) → scratchpad 중심 프로그래밍 모델의 특성. HST-L과 TRNS은 동기화 명령어 비중 높음 (busy waiting)

#### 3.3.3. 강한 스케일링 (Fig. 10)

- 1/16/64 DPU로 병렬화 시 대부분 잘 스케일링
- 예외: BFS, BS, NW는 서브선형 스케일링 (DPU 증가 시 통신 크기 증가)
- SCAN-RSS, SCAN-SSA, SEL, UNI, VA: CPU↔DPU 데이터 전송이 전체 실행 시간의 대부분 차지

## 핵심 기여

- **uPIMulator**: 최초의 상용 범용 PIM ISA 호환 시뮬레이터 (52K LoC, 3KIPS)
- **핵심 기여**: UPMEM-PIM의 내부 동작 세밀히 특성화 → 범용 PIM의 가능성과 한계 입증
- **미래 PIM에 필요한 아키텍처 특성**: 벡터 처리, ILP 향상 마이크로아키텍처, 멀티테넌시 보안/투명성 지원, 온디맨드 캐싱
- **프로그래밍 모델의 중요성**: scratchpad 중심 모델은 유연성과 멀티테넌시에 한계 →未来的 PIM은 캐시와 scratchpad의 혼합 또는 캐시 중심 모델 고려
- 이 연구는 PIM이 "진정한 범용 컴퓨팅 장치"로 진화하기 위한 아키텍처 연구 방향을 제시

## 주요 결과

### 4.1. Case Study #1: 벡터 처리 지원

- 현재 UPMEM DPU: 스칼라 연산만 지원 → 벡터 연산 필수
- 벡터화 실험: SIMD 유닛 추가 시 **최대 4.7×(BS), 6.8×(GEMV)** 성능 향상 (Fig. 15의 cache-centric와 유사한 수준)
- 미래 PIM에 벡터 처리 지원이 중요한 방향

### 4.2. Case Study #2: ILP 향상 마이크로아키텍처

- Revolver pipeline와 odd/even RF 구조적 해저드가 주요 병목
- 다중 파이프라인 또는 더 넓은 issue 폭으로 ILP 향상 가능

### 4.3. Case Study #3: 멀티테넌시

- **MMU 지원**: uPIMulator에 하드웨어 MMU 추가 (단일 페이지 테이블 워커, 4KB 페이지, 16-entry fully-associative TLB)
- **성능 영향**: 평균 0.8% (최대 14.1%) 지연 증가 → 실용적
- 높은 TLB 히트율: scratchpad 중심 모델에서 DMA가 코어스 그레인 단위로 데이터 전송 → 높은 공간적 locality
- DPU 350MHz → 메모리 접근 지연이 수십 사이클 (CPU/GPU의 수백 사이클 대비 낮은 TLB 미스 페널티)
- **투명성 문제**: scratchpad 기반 프로그래밍 모델은 멀티테넌시에 부적합 (mem_alloc()으로 WRAM heap 초과 → 프로그램 수정 필요)

### 4.4. Case Study #4: 온디맨드 캐시 vs. Scratchpad (Fig. 14, 15, 16)

- uPIMulator의 커스텀 링커를 활용한 캐시 vs. scratchpad 비교 연구
- **캐시 기반 구성**: instruction cache(8-way, 24KB) + data cache(8-way, 64KB), LRU 교체
- **scratchpad 기반**: 메모리 할당 API로 WRAM heap 명시적 관리

**결과 (Fig. 15)**:
- BS: 캐시 기반에서 4.7× 성능 향상
- GEMV: 캐시 기반에서 6.8× 성능 향상
- UNI: scratchpad 기반에서 우월 (DRAMA→scratchpad DMA가 효과적)
- 워크로드 특성에 따라 캐시가 유리할 수도, scratchpad가 유리할 수도 있음

**메모리 접근 분석 (Fig. 16)**:
- BS: scratchpad 기반은 DRAM에서 더 많은 바이트 읽음 (DMA 오버헤드)
- UNI: 캐시 기반은 더 적은 바이트 읽지만, 캐시 미스 지연이 크다

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2024HPCA-summarize/pathfinding-future-pim-architectures-by-demystifying-a-commercial-pim-technology.md|전체 요약 보기]]
