---
tags: [paper, 2023, 2023MICRO, topic/compression, topic/disaggregation, topic/dram, topic/memory-tiering, topic/near-data-processing, topic/nvm]
venue: "56th Annual IEEE/ACM International Symposium on Microarchitecture (MICRO 2023)"
year: 2023
summary_path: "../paper-summaries/2023MICRO-summarize/xfm-accelerated-software-defined-far-memory.md"
---

# XFM: Accelerated Software-Defined Far Memory

**Venue:** 56th Annual IEEE/ACM International Symposium on Microarchitecture (MICRO 2023)
**저자:** Neel Patel, Amin Mamandipoor, Derrick Quinn, Mohammad Alian (University of Kansas)

## 개요

- DRAM은 서버 비용의 **50% 이상**, 탄소 발자국의 **75%**를 차지하며, DRAM 용량 확장은 CMOS 기술 축소 어려움으로 인해 정체 상태
- 데이터센터에서 메모리 요구사항은 급격히 증가하는 반면, DRAM 제조 비용과 탄소 배출은 다른 구성 요소를 크게 상회
- Far memory 아키텍처가 비용 절감 대안으로 부상: **SFM** (Software-Defined Far Memory)과 **DFM** (Disaggregated Far Memory)의 두 가지 범주
  - DFM: PCIe, CXL, 네트워크 등 느린 인터커넥트로 추가 DRAM 모듈 연결
  - SFM: 로컬 DRAM의 일부를 압축된 냉 데이터 저장용으로 동적 할당 (Google, Meta 도입)
- SFM 구현의 핵심 문제: **CPU 기반 압축/해제**가 메모리 대역폭을 과도하게 소모
  - 512GB SFM에서 메모리 대역폭 사용량이 최대 **34GBps**에 달할 수 있음
  - co-running 애플리케이션의 메모리/캐시 계층 간섭으로 성능 저하 유발

## 방법론

### 3.1 DFM vs SFM 비용 분석 (Section 3)

- **1차원 비용 모델**로 512GB far memory 구현 시 SFM과 DFM 비교
- DFM 비용 모델:
  ```
  DFM_Cost = ExtraGB × MemoryCostPerGB + (PCIeEnergy + IdleDIMMEnergy) × ElectricityCost × TIME
  ```
- SFM 비용 모델:
  ```
  SFM_Cost = EnergyPerGB × GBSwappedPerMin × ElectricityCost × TIME + CPUCost
  ```
- **핵심 결과**: 100% promotion rate에서도 SFM이 DRAM 기반 DFM보다 비용 효율적
  - DFM DRAM 대비 SFM 손익분기점: **8.5년**
  - 20% promotion rate에서는 PMem 기반 DFM보다도 SFM이 더 경제적
- **탄소 배출**: DRAM 제조는 로직 제조 대비 **10배** 높은 탄소 배출 → SFM이 DFM보다 수명 기간 동안 낮은 배출 유지

### 3.2 Near-Memory Processing 활용 기회

- SFM 가속화로 비용 절감 가능: CPU 사이클 절약 + 메모리 대역폭 절감
- **네 가지 오버헤드**: (O1) 동기 해제 작업으로 인한 메모리 접근 지연, (O2) CPU 사이클 에너지 소비, (O3) 메모리 대역폭 소모, (O4) 캐시 계층 오염
- 온칩 가속기(Intel QAT 등)는 O1, O2만 해결 가능하며 O3, O4 미해결
- NMA는 O3와 O4 모두 해결 가능: 메모리 측에서 압축/해제 수행 시 대역폭 및 캐시 오염 제거

### 3.3 DRAM 리프레시 기반 메커니즘 (Section 5-6)

- **tRFC 인터벌 활용**: DRAM 리프레시 동안 여러 행이 병렬로 리프레시됨 → 이 대기 시간 동안 NMA가 DRAM에 조건부/랜덤 접근 수행
- 리프레시 명령은 ACT + PRE 시퀀스와 동일한 의미를 가짐
- **Compress_Request_Queue**: CPU에서 NMA로 압축 요청 전송 (MMIO 쓰기)
- **ScratchPad Memory (SPM)**: NMA 내부 2MB 스테이징 버퍼, 압축 결과를 DRAM에 쓰기 전 일시 저장
- **조건부 접근**: 리프레시 간 NMA가 DRAM에 접근 가능한지 사전 확인 → 에너지 10.1% 절감

### 3.4 소프트웨어 스택

- **XFM_Backend**: Linux zswap의 SFM_Backend를 수정한 백엔드
  - `xfm_swap_out()`: NMA에 압축 요청 전송, SPM 용량 확인 후 MMIO로 Compress_Request_Queue에 추가
  - `xfm_swap_in()`: 압축된 페이지를 Red-Black Tree에서 조회 후 NMA에 해제 요청
- **CPU_Fallback**: SPM 공간 부족 시 CPU가 직접 (de)compression 수행
- **Multi-Channel 모드**: 4개 DIMM에서 채널 인터리빙 호환, 각 DIMM의 SFM 영역에 동일 위치에 데이터 배치
  - 2-DIMM/4-DIMM에서 압축비 각각 **5%**, **14%** 감소 (허용 범위)

## 핵심 기여

- **핵심 기여**: 최초로 NMA를 활용하여 SFM을 가속화하는 아키텍처 제안
- **비교 분석**: SFM은 DRAM 기반 DFM 대비 8.5년 내 손익분기, 탄소 배출도 server 수명 내 DFM을 결코 추월하지 않음
- **성능**: co-running 애플리케이션 **5~27% 성능 향상**, 메모리 대역폭 사용 완전 제거 (최대 1TB)
- **의의**: 기존 DRAM 표준(리프레시 메커니즘)을 활용하여 투명한 NMA-CPU 동시 접근 구현, 하드웨어 비용 7W, 면적 0.15%로 실용적
- **향후 과제**: 더 정교한 냉 페이지 예측 휴리스틱으로 higher promotion rate에서의 이익 극대화

## 주요 결과

- **프로토타입**: Samsung AxDIMM (Xilinx UltraScale+ FPGA) 기반
  - 오픈소스 Deflate 압축/해제 가속기 통합 (14.8GBps 압축, 17.2GBps 해제)
  - 2MB ScratchPad Memory + 컨트롤러 로직
- **에뮬레이터**: gem5 DDR4-2400 타이밍 모델 기반, AIFM 사용자 공간 far memory 프레임워크 통합
- **압축 알고리즘**: zstd (CPU 백엔드 및 XFM 에뮬레이터 공통)
- **하드웨어 비용**:
  - FPGA: LUT 435,467개 (83.3%), FF 94,135개 (9.0%), BRAM 51개 (5.18%)
  - 전력: 동적 5.7W + 정적 1.3W = **총 7.024W**
  - CACTI 시뮬레이션: DRAM 뱅크 수정 시 ~0.15% 면적, ~0.002% 전력 오버헤드

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]


## 전체 요약

[[../paper-summaries/2023MICRO-summarize/xfm-accelerated-software-defined-far-memory.md|전체 요약 보기]]
