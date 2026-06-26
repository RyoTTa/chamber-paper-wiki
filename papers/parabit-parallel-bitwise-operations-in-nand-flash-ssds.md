---
tags: [paper, 2024, 2024ISCA, topic/cache, topic/dram, topic/nvm, topic/pim, topic/security, topic/storage]
venue: "MICRO 2021 (54th Annual IEEE/ACM International Symposium on Microarchitecture)"
year: 2024
summary_path: "../paper-summaries/2024ISCA-summarize/parabit-parallel-bitwise-operations-in-nand-flash-memory-based-ssds.md"
---

# ParaBit: Processing Parallel Bitwise Operations in NAND Flash Memory based SSDs

**Venue:** MICRO 2021 (54th Annual IEEE/ACM International Symposium on Microarchitecture)
**저자:** Congming Gao (Tsinghua University), Xin Xin (University of Pittsburgh), Youyou Lu (Tsinghua University), Youtao Zhang (University of Pittsburgh), Jun Yang (University of Pittsburgh), Jiwu Shu (Tsinghua University)

## 개요

- 데이터 집약적 애플리케이션에서 저장장치(storage)와 메인 메모리 간 데이터 이동 오버헤드가 주요 성능 병목(Memory wall)으로 작용하며, PIM(Processing-in-Memory) 및 ISC(In-Storage Computing) 아키텍처가 이를 완화하기 위해 제안되었으나, 처리할 데이터량이 클 때 저장장치-메모리 간 대역폭 제한으로 여전히 큰 데이터 이동 비용이 발생
- 기존 PIM 및 ISC는 데이터가 이미 메모리에 로드된 후 처리된다는 비현실적 가정을 기반으로 하며, 실제 데이터 볼륨이 메모리 용량을 초과하면 SSD→DRAM 데이터 이동 비용이 연산 비용의 **30배(PIM)** 및 **60배(ISC)**에 달함 (Section 3의 preliminary study)
- 예시: 200,000장의 800×600 이미지(YUV 256레벨)는 140GB 저장 공간 필요 → PIM 시스템의 64GB DRAM을 초과하여 SSD↔DRAM 데이터 스와핑 발생
- PIM(Ambit) 및 ISC(Cosmos OpenSSD)의 실제 평가에서 데이터 이동 시간이 전체 실행 시간의 **90% 이상**을 차지하며, 비트 연산 시간은 2~6%에 불과

## 방법론

### 3.1 NAND Flash의 Latching Circuit 기반 비트 연산

- MLC(Multi-Level Cell) 셀의 LSB/MSB 읽기 과정에서 sensing voltage(VREAD0~VREAD3)와 트랜지스터 제어(M1~M5)를 조정하여 논리 연산 수행
- **AND 연산** (Fig. 5a): VREAD1으로 cell 상태 E(11)를 판별 → L(A) = L(A)_old ∧ L(SO) = 1000 → 출력에 1 (E 상태일 때만)
- **OR 연산** (Fig. 5b): VREAD2, VREAD3 순차 sensing으로 3단계 제어 → L(OUT) = 1101
- **XNOR 연산** (Fig. 6): 6단계 제어로 E 또는 S2 상태 판별 → L(OUT) = 1010
- NAND, NOR, XOR, NOT는 초기값 설정 후 유사한 sensing/transistor 제어로 구현 가능 (Table 2~5)
- **Truth Table (Table 1):** E(1/1)→AND:1, OR:1, XNOR:1; S1(1/0)→AND:0, OR:1, XNOR:0 등 7개 연산 지원

### 3.2 Location-free ParaBit

- 기본 ParaBit은 두 오퍼랜드 비트가 동일한 MLC 셀에 저장되어야 작동 → 다른 셀에 있을 경우 재할당 필요 (오버헤드 큼)
- **CACHE READ RANDOM 명령 활용**: 서로 다른 워드라인의 정렬된 셀(aligned cells, 동일 bitline)이 동일 latch circuit을 공유하므로, 2단계 sensing 전략으로 서로 다른 워드라인의 셀 읽기 가능
- AND, OR 연산은 기본적으로 지원 (MSB 셀의 두 번째 operand도 처리 가능하도록 L1 독립성 활용)
- XOR 연산: 추가 inverter(M6, M7)와 2개 제어 트랜지스터를 SO와 MSO 사이에 통합하여 원래 LSB 값 직접 취득 → M⊕N = M̄N + MN̄ 계산 (Fig. 8)
- 하드웨어 오버헤드: latch circuit과 column decoder의 die area 대비 약 **1.2%**

### 3.3 SSD 컨트롤러 구현 구조

- **CMD Parse 모듈**: 호스트의 NVMe read command 예약 바이트(DWord 2, 3, 13)에 비트 연산 시맨틱 저장 (intra-bitwise type, operand tag, pointer, extra bitwise type, batch order)
- **Operands ReAllocation 모듈**: 오퍼랜드가 동일 MLC에 정렬되지 않은 경우 재할당 수행. scramble/encryption 함수 일시 비활성화
- **Parallel Read 모듈**: 배치 구조 기반 병렬 비트 연산 실행. 배치 내 2개 오퍼랜드 → 결과 → 다음 배치의 오퍼랜드로 재사용
- 연산 결과는 SSD 내부 버퍼에 임시 저장 후 재로드하여 다중 연산 체이닝 지원

### 3.4 TLC/QLC 확장 및 신뢰성

- TLC의 8상태(E, S1~S7) 인코딩(111~011)으로 동일 원리 적용 가능
- 신뢰성 문제: 기존 ECC가 비트 연산과 호환되지 않음 (XOR/XNOR 제외). 에러 내성 낮은 앱의 경우 오퍼랜드 페이지를 새 MLC로 이동 후 연산 수행
- SSD 내부 버퍼 공간 오버헤드: 최대 병렬성 활용 시 약 5MB

## 핵심 기여

1. **In-flash computing의 최초 실증**: NAND flash의 latch circuit 특성을 활용하여 기존 상용 SSD에서 7개 비트 논리 연산을 하드웨어 수정 없이 구현
2. **데이터 이동 오버헤드 대폭 절감**: PIM 대비 최대 **84.1%**, ISC 대비 **83.0%** 의 전체 실행 시간 단축 (비트맵 인덱스 기준)
3. **대규모 데이터 처리에 적합**: SSD의 수백 개 칩 병렬성을 활용하여, 오퍼랜드 206.4MB 이상에서 PIM 아키텍처 대비 성능 우위 달성
4. **확장성**: NAND flash 외에도 PCM, STT-MRAM, ReRAM 등 NVM 기술에도 적용 가능하며, all-flash storage 시스템에서 수백~수천 개 SSD의 병렬성으로 높은 컴퓨팅 효율 달성 가능

## 주요 결과

| 항목 | 세부사항 |
|------|---------|
| **구현 언어** | C/C++ (SSD 시뮬레이터), H-spice (회로 시뮬레이션) |
| **SSD 하드웨어** | 128 chip, 4 plane/chip, 8KB page, 512GB MLC SSD |
| **플래시 레이턴시** | 쓰기 640µs, sensing 25µs |
| **병렬성** | 최대 2개 8MB 오퍼랜드 동시 처리 |
| **하드웨어 수정** | Location-free ParaBit: inverter + 2 트랜지스터 (die area ~1.2%) |
| **호스트-디바이스 통신** | NVMe command 예약 바이트 활용 |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/security.md|Security]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2024ISCA-summarize/parabit-parallel-bitwise-operations-in-nand-flash-memory-based-ssds.md|전체 요약 보기]]
