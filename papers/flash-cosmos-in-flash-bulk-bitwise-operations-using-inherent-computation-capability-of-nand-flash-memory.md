---
tags: [paper, 2022, 2022MICRO, topic/gpu, topic/near-data-processing, topic/storage]
venue: "MICRO 2022 (55th IEEE/ACM International Symposium on Microarchitecture)"
year: 2022
summary_path: "../paper-summaries/2022MICRO-summarize/flash-cosmos-in-flash-bulk-bitwise-operations-using-inherent-computation-capability-of-nand-flash-memory.md"
---

# Flash-Cosmos: In-Flash Bulk Bitwise Operations Using Inherent Computation Capability of NAND Flash Memory

**Venue:** MICRO 2022 (55th IEEE/ACM International Symposium on Microarchitecture)
**저자:** Jie Zhang, Mithuna Thottethodi (Purdue University)

## 개요

- NAND 플래시 메모리 기반 SSD의 **외부 대역폭(8 GB/s, PCIe Gen4)**이 대량 비트 연산(bulk bitwise operations)의 병목 → CPU/GPU 등 주변장치로 데이터를 전송해야 하므로 I/O 대역폭에 의존
- 기존 **In-Storage Processing (ISP):** SSD 내부에 하드웨어 가속기(단순 비트 논리 + 256KB SRAM 버퍼)를 두어 연산 수행 → 그러나 **NAND 플래시 칩에서 SSD 컨트롤러로의 내부 I/O 링크(9.6 GB/s)**가 새로운 병목
- **ParaBit (PB):** NAND 플래시 칩 내부에서 multi-wordline activation으로 비트 연산 수행 (NDP) → 그러나 **단일 sensing으로 처리 가능한 피연산자 수가 2개로 제한**되어 병렬성이 제한됨 (serial sensing 필요)
- 기존 in-flash processing 제안 중 일부는 **아날로그 전류 축적 방식**을 사용하나, 정밀 ADC(아날로그-디지털 컨버터)가 필요 → 칩 면적 31%, 전력 58% 차지 (128 컬럼 공유 기준) → 상용 칩 적용 어려움
- NAND 플래시의 **raw bit error rate (RBER)**가 높아 데이터 randomization 없이는 오류가 빈번 → 대량 비트 연산 시 단일 비트 오류만으로도 결과가 완전히 잘못됨 (BMI: m=36일 때 정확 확률 0.42)

## 방법론

### 3.1. Multi-Wordline Sensing (MWS)

**Intra-block MWS:**
- 단일 블록 내 **모든 wordline을 동시에 활성화**하여 하나의 NAND string에서 연산 수행
- V_REF를 대상 wordline에 적용하고, 비대상 wordline에는 V_PASS 적용
- BL(비트라인)은 '1'로 precharge → NAND string이 전도되면 BL이 '0'으로 드롭
- **bitwise AND:** 모든 WL이 '1'일 때만 BL이 유지됨 (NAND string의 직렬 연결)
- **bitwise OR:** inverse read 모드 + De Morgan's 법칙 활용
  - 데이터를 반전시켜 저장하면, intra-block MWS로 OR 연산 가능
  - 식: `(A1+...+AN) ≡ (NOT A1 • ... • NOT AN)`
- **48개 wordline 동시 활성화 시 tMWS = 1.033 × tR** (3.3% 지연 증가)
- 8개 WL 이하에서는 **tMWS < 1.01 × tR** (< 1% 지연)

**Inter-block MWS:**
- 여러 블록의 wordline을 동시에 활성화
- **비트 AND/OR:** 블록 l과 블록 n의 WL을 동시에 활성화하면 BL_j가 '1'인 조건:
  - `(A1,j • ... • AN,j) + (B1,j • ... • BN,j)` (식 1)
- 32개 블록 동시 활성화 시 **tMWS = 1.363 × tR** (36.3% 지연)
- 4개 블록 이하에서는 **tMWS ≈ 1.033 × tR** (3.3% 지연)
- **전력:** 2 블록 활성화 시 평균 전력 34% 증가, 4 블록 이하에서 erase 동작보다 낮음
- 에너지 효율: 4 블록 inter-block MWS가 개별 4회 read보다 **53% 에너지 절감**

### 3.2. Enhanced SLC-Mode Programming (ESP)

- **기존 SLC-mode programming의 ISPP(Incremental Step Pulse Programming) 파라미터를 조정:**
  - V_TGT 증가 (programmed V_TH 상태를 더 높은 전압으로 이동)
  - ΔVISPP 감소 (V_TH 분포 너비를 좁힘)
  - 추가 ISPP 스텝 수행 → **RBER를 effectively zero로 달성**
- **실시간 특성화 (160개 3D TLC NAND 플래시 칩):**
  - tESP를 tPROG 대비 90% 이상 증가시키면 **RBER < 2.07 × 10⁻¹2** (zero bit errors 관찰)
  - 중간 블록: tESP 60% 증가로 **한 자리 수 RBER 감소**
- **상용 칩 호환성:**
  - 현대 MLC NAND는 SLC-mode programming을 지원 (신뢰도 민감한 데이터 저장, SLC write buffer 등)
  - SET FEATURE 명령으로 ISPP 파라미터를 post-fabrication 조정 가능
- **오버헤드:** tESP = 2 × tPROG (400μs), SLC 모드로 인해 **2배 저장 용량 필요** (선택적 사용으로 최소화)

### 3.3. 기타 비트 연산 지원

| 연산 | 메커니즘 |
|------|---------|
| **AND** | Intra-block MWS |
| **OR** | Inverse data 저장 + Intra-block MWS + De Morgan |
| **NOT** | Inverse read |
| **NAND** | Inverse read + Intra-block MWS |
| **NOR** | Inverse read + Inter-block MWS |
| **XOR** | 기존 칩 내부 XOR 레이치 + Inverse read |
| **XNOR** | A XNOR B ≡ A XOR (NOT B) |

### 3.4. 명령어 집합 (Command Set)

- **MWS 명령어:** regular read를 확장
  - ISCM 슬롯: inverse-read, S-latch 초기화, C-latch 초기화, S→C 전송 플래그
  - 주소 슬롯: 페이지 인덱스 대신 **PBM(Page Bitmap)** 사용으로 대상 WL 효율적 지정
  - 최대 4개 주소 슬롯 (CONT 슬롯으로 추가 블록 주소 전송)
- **ESP 명령어:** regular program과 동일 인터페이스
- **XOR 명령어:** sensing latch와 cache latch 간 bitwise XOR, 결과를 C-latch에 저장
- **연산 예시 (Figure 16):** `{A1+(B1•B2•B3•B4)}•(C1+C3)•(D2+D4)` → 두 번의 MWS 명령어로 수행

### 3.5. 시스템 지원

- **Flash-Cosmos 라이브러리:**
  - `fc_write`: 데이터 쓰기 (programming 모드, 위치 정보 포함)
  - `fc_read`: 연산 수행 (피연산자 위치, 크기, 연산 타입 지정)
- **SSD 펌웨어 변경:** MWS/ESP/XOR 명령어 생성, programming 모드별 메타데이터 관리
- **애플리케이션 변경:** 연산 대상 데이터 결정, inverse data 저장 여부, 같은 블록에 배치할 피연산자 선택

## 핵심 기여

1. **NAND 플래시의 고유 연산 능력을 최초로 활용한 대량 비트 연산 가속:** MWS를 통해 단일 sensing으로 48개 피연산자 병렬 처리 가능
2. **ESP로 상용 칩에서 effectively zero bit error 달성:** 160개 실시간 칩으로 검증, RBER < 2.07 × 10⁻¹²
3. **OSP 대비 평균 32배 speedup, 95배 에너지 효율 향상** (실세계 워크로드 기준)
4. **ParaBit 대비 3.5배 성능, 3.3배 에너지 효율** → serial sensing bottleneck 극복
5. **상용 NAND 플래시 칩에서의 높은 구현 가능성:** 기존 테스트 모드 명령어 활용, SET FEATURE로 ISPP 파라미터 조정 가능
6. **In-storage/in-memory NDP와 보완적 관계:** 대용량 데이터의 최종 연산 결과만 외부로 전송 → 대역폭 병목 극복

**Broader significance:** Flash-Cosmos는 NAND 플래시 메모리의 물리적 특성을 소프트웨어 수준의 변경 없이 활용하는 하드웨어 메커니즘으로, storage-class 메모리와 NDP(Near-Data Processing)의 실용화에 기여. 특히 데이터 randomization의 필요성을 제거하여 in-flash processing의 적용 범위를 대폭 확대한 점이 핵심 공헌.

## 주요 결과

- **실시간 특성화 플랫폼:** FPGA 기반 NAND 플래시 컨트롤러 + 온도 컨트롤러 (±1°C)
- **테스트 칩:** 160개 48-Layer 3D TLC NAND 플래시 (16 KiB/page, 48 WL/string)
- **시뮬레이터:**
  - DRAM: Ramulator (DDR4 인터페이스)
  - SSD: MQSim 확장 (ISP, ParaBit, Flash-Cosmos 모델링)
- **호스트 시스템:** Intel i7-11700K, 64GB DDR4-3600
- **SSD 구성:** 2TB, 8채널 × 8다이 × 2플레인, 8GB/s 외부 대역폭

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2022MICRO-summarize/flash-cosmos-in-flash-bulk-bitwise-operations-using-inherent-computation-capability-of-nand-flash-memory.md|전체 요약 보기]]
