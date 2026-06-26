---
tags: [paper, 2022, 2022MICRO, topic/dram, topic/pim, topic/storage]
venue: "MICRO 2022 (55th IEEE/ACM International Symposium on Microarchitecture)"
year: 2022
summary_path: "../paper-summaries/2022MICRO-summarize/pluto-enabling-massively-parallel-computation-in-dram-via-lookup-tables.md"
---

# pLUTo: Enabling Massively Parallel Computation in DRAM via Lookup Tables

**Venue:** MICRO 2022 (55th IEEE/ACM International Symposium on Microarchitecture)
**저자:** João Dinis Ferreira, Gabriel Falcao, Juan Gómez-Luna, Mohammed Alser, Lois Orosa, Mohammad Sadrosadati, Jeremie S. Kim, Geraldo F. Oliveira, Taha Shahroodi, Anant Nori, Onur Mutlu (ETH Zürich / IT, University of Coimbra / Galicia Supercomputing Center / TU Delft / Intel)

## 개요

- 프로세서와 메인 메모리 간 데이터 이동(Data Movement)은 메모리 집약적 워크로드의 실행 시간과 에너지 소비의 핵심 병목(Bottleneck)
- Processing-in-Memory(PiM)는 이 문제를 완화하기 위한 유망한 패러다임이며, 그 중 Processing-using-Memory(PuM)는 메모리 디바이스의 고유한 물리적 특성을 활용하여 메모리 어레이 내부에서 연산을 수행
- 기존 PuM 아키텍처의 핵심 한계:
  - 비트 단위 비트와이즈 연산(Majority, AND, OR, NOT) 및 간단한 산술 연산(덧셈)만 효율적으로 지원
  - 곱셈, 나눗셈, 지수 함수 등의 복잡한 연산은 높은 레이턴시와 에너지 비용을 유발 (예: SIMDRAM에서 곱셈은 이차적 DRAM 활성화 필요)
  - 지수 함수, 삼각 함수 등은 아예 지원하지 않음
- 기존 PuM의 연산 제한은 실제 응용의 확장을 극심하게 제한하며, 복잡한 연산을 효율적으로 수행할 수 있는 범용적 PuM 아키텍처가 필요

## 방법론

### 3.1. pLUTo LUT Query 메커니즘 (Figure 2, 3)

- **입력 단계:** 소스 서브어레이에 LUT 쿼리 입력 벡터(LUT 인덱스 목록)를 로드
- **Row Sweep:** pLUTo-enabled 서브어레이의 모든 행을 순차적으로 활성화 (단일 DRAM 명령)
- **Match Logic 동작:** 각 행 활성화 시, 해당 행의 인덱스와 입력 벡터의 각 요소를 비교하여 일치 여부 확인
- **Flip-Flop(FF) Buffer:** 일치하는 LUT 요소를 FF 버퍼에 복사 (Match Logic이 제어하는 스위치를 통해)
- **결과 전달:** LISA-RBM 연산으로 FF 버퍼의 내용을 목적지 서브어레이로 복사
- 비트 병렬 방식: LUT 요소의 비트는 인접 비트라인에 수평 저장, 전체 복사본은 하나의 행을 차지

### 3.2. 세 가지 pLUTo 디자인 (Figure 4)

#### 3.2.1. pLUTo-BSA (Buffered Sense Amplifier)
- 기존 센스 앰플리파이어 위에 matchline 제어 스위치와 FF 버퍼를 추가
- Row Sweep 동작: 각 행 활성화 후 matchline에 의해 선택된 요소만 FF 버퍼로 복사
- 에너지 효율: 행 활성화당 추가 에너지 비용 존재

#### 3.2.2. pLUTo-GSA (Gated Sense Amplifier)
- 센스 앰플리파이어에 matchline 제어 게이트를 추가 (스위치가 센스 앰플리파이어 내부에 위치)
- 가장 낮은 면적 오버헤드: 10.2%
- 활성화 간 precharge 불필요 → row sweep 시간 단축
- 단점: 비트라인 노이즈가 가장 큼 (SPICE 시뮬레이션에서 확인됨)

#### 3.2.3. pLUTo-GMC (Gated Memory Cell)
- DRAM 셀 자체를 2T1C 셀로 변경하여 matchline 제어 스위치를 셀 내부에 통합
- 가장 높은 면적 오버헤드: 23.1%
- 가장 높은 에너지 효율과 성능

### 3.3. 시스템 통합 스택 (Section 6)

- **pLUTo ISA:** pluto_row_alloc, pluto_subarray_alloc, pluto_op (LUT 쿼리), pluto_{bit,byte}_* (시프팅), pluto_and/pluto_or (비트 연산)
- **pLUTo Library:** C API 라이브러리. api_pluto_lut, api_pluto_mul, api_pluto_add 등 고수준 래퍼 함수 제공
- **pLUTo Compiler:** 데이터 의존성 분석, 피연산자 정렬(시프팅, 마스킹, 행 병합 자동 삽입)
- **pLUTo Controller:** ROM(RAM 명령 시퀀스 매핑) + 레지스터 파일 + FSM으로 구성. CPU 다이에서 <0.08% 면적 오버헤드

### 3.4. LUT 데이터 로딩 (Section 6.5)

- First-Time Generation: LUT 요소를 처음부터 계산
- Loading from Memory: 기존 메모리의 LUT를 LISA-RBM으로 pLUTo 서브어레이로 복사
- Loading from Secondary Storage: SSD 등에서 DMA로 메인 메모리에 로드
- 1.9MB 데이터 처리 시점에서 DDR4 기준 LUT 로딩 시간 = LUT 쿼리 시간으로 상쇄 (Figure 11)

## 핵심 기여

1. **pLUTo는 DRAM 기반 PuM에서 최초로 범용적 LUT 쿼리를 가능케 한다:** 기존 PuM의 제한된 연산 세트를 극복하여 곱셈, 나눗셈, 지수 함수 등을 효율적으로 지원
2. **CPU 대비 평균 713×, GPU 대비 1.2× 성능 향상:** 에너지는 CPU 대비 1855×, GPU 대비 39.5× 절감
3. **세 가지 디자인으로 다양한 트레이드오프 제공:** pLUTo-GSA(10.2% 면적 오버헤드, 가장 낮은 비용) ~ pLUTo-GMC(23.1%, 가장 높은 성능/에너지 효율)
4. **양자화 신경망 추론에 특히 적합:** 1-bit/4-bit 정밀도에서 CPU 대비 10×/30× 성능, 110× 에너지 절감
5. **오픈소스 구현 제공:** github.com/CMU-SAFARI/pLUTo에서 재현 가능한 스크립트 포함

**Broader significance:** pLUTo는 PuM 패러다임의 연산 범위를 근본적으로 확장하여, DRAM의 높은 저장 밀도를 활용한 범용 인메모리 연산의 실용성을 입증.未来的 메모리 기술(예: DDR5, 3D-stacked)과 결합하여 더욱 큰 성능/에너지 이점을 제공할 잠재력

## 주요 결과

- **시뮬레이터:** custom-built cycle-level 시뮬레이터 (오픈소스: github.com/CMU-SAFARI/pLUTo)
- **시스템 구성 (Table 3):**
  - DDR4 2400MHz, 8GB, 1-channel, 1-rank, 4-bank groups, 512 rows/subarray, 8KB/row
  - PnM: HMC 기반, 비트와이즈 연산 지원, on-die 코어 1.25GHz, 10W TDP
  - FPGA: Zynq UltraScale+ ZCU102
  - pLUTo: 16개 서브어레이 병렬 (DDR4), 512개 서브어레이 병렬 (3DS)
- **SPICE 시뮬레이션:** Low-Power 22nm Metal Gate PTM 트랜지스터 기반, Monte Carlo 100회, process variation 5%
- **CACTI 7:** 에너지 소비 및 면적 추정
- **워크로드:** 벡터 덧셈/곱셈, 비트 카운팅, CRC-8/16/32, Salsa20, VMPC, 이미지 이진화, 컬러 그레이딩 (총 11개)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2022MICRO-summarize/pluto-enabling-massively-parallel-computation-in-dram-via-lookup-tables.md|전체 요약 보기]]
