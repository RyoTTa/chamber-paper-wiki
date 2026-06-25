---
tags: [paper, 2024, 2024MICRO, topic/dram, topic/near-data-processing, topic/pim, topic/storage]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024MICRO-summarize/ares-flash-efficient-parallel-integer-arithmetic-operations-using-nand-flash-memory.md"
---

# Ares-Flash: Efficient Parallel Integer Arithmetic Operations Using NAND Flash Memory

**Venue:** 
**저자:** 

## 개요

### 1.1 Near Data Processing과 In-Flash Processing

데이터 집약적 응용(ML 추론, 그래프 처리, 빅데이터 분석)에서 memory/storage와 computing unit 간 데이터 이동이 주요 병목. Near Data Processing(NDP)는 연산을 데이터 근처로 offload하여 이 문제를 해결.

- **PIM(Processing-in-Memory):** DRAM 근처 연산. 여전히 storage→memory 데이터 이동 필요.
- **ISP(In-Storage Processing):** SSD controller에서 연산. flash→controller 내부 데이터 이동 발생.
- **IFP(In-Flash Processing):** flash chip 내부에서 직접 연산. 데이터 이동을 최소화하는 가장 효율적인 접근.

Flash 기반 SSD는 대용량·고속 저장 매체로 가장 널리 사용됨. IFP는 데이터가 flash에 저장된 위치에서 직접 연산을 수행하여 데이터 이동을 근본적으로 제거.

### 1.2 기존 IFP 접근의 한계

기존 IFP 연구들은 대부분 **bulk bitwise 연산**(AND, OR, NOT 등)에 초점:

- Flash memory의 multi-level cell sensing 특성을 활용한 bitwise 연산 [9, 14, 35].
- 그러나 integer arithmetic(덧셈, 곱셈, 나눗셈)은 bitwise 연산만으로는 비효율적 — carry propagation, multi-step dependency로 인해 수백~수천 cycle 필요.
- 기존 접근은 bitwise primitive를 외부 controller와의 반복적 통신으로 조합 → 내부 버스 트래픽과 제어 오버헤드가 여전히 큼.

### 1.3 Flash Memory 아키텍처 기초

NAND flash의 내부 구조:

- **Plane:** 독립적으로 동작하는 최상위 단위. 여러 block으로 구성.
- **Block:** 수백 개의 WL(Wordline) 포함. erase 단위.
- **WL(Wordline):** 동일 WL에 연결된 수만 개의 셀. 각 셀은 BL(Bitline)에 연결.
- **Page buffer (latch circuit):** 각 BL 끝에 위치한 latch. read/write 시 데이터를 임시 저장.

핵심 관찰: 모든 BL의 latch circuit이 병렬로 동작 가능. 이 병렬성을 arithmetic 연산에 활용하는 것이 Ares의 아이디어.

## 방법론

### 3.1 방법론

| 항목 | 구성 |
|------|------|
| **Flash Model** | NAND flash chip 시뮬레이션, 실제 flash timing parameter 사용 |
| **Baselines** | OSP(OpenSSD Platform 기반 host-side 연산), ISP(In-Storage Processing, SSD controller 연산) |
| **Operations** | Addition, Subtraction, Multiplication, Division |
| **Operand Sizes** | 8-bit ~ 64-bit integer |
| **Benchmarks** | 합성 마이크로벤치마크 + Vector Similarity Search (VSS) 사례 연구 |
| **Metrics** | Throughput (ops/s), Latency, Energy efficiency |

### 3.2 Arithmetic 연산 성능

**Addition:**
- Ares: OSP 대비 평균 **12.47×** throughput 향상, ISP 대비 **6.82×** 향상.
- ISP도 OSP 대비 향상되나, SSD 내부 데이터 이동(flash→controller)이 여전히 bottleneck.
- Ares는 데이터 이동을 시작부터 제거하여 ISP의 내부 이동 한계를 극복.

**Subtraction:**
- Addition과 유사한 비율의 성능 향상 (2's complement 기반으로 동일 로직 사용).

**Multiplication:**
- Shift-and-add 방식으로 operand bit-width에 비례하는 latency.
- 32-bit multiplication: OSP 대비 ~8×, ISP 대비 ~4× throughput.

**Division:**
- Restoring 방식으로 operand bit-width에 quadratic한 latency.
- Subtraction 반복으로 인해 다른 연산 대비 상대적 이점이 적으나 여전히 OSP/ISP 능가.

### 3.3 Ares-V Vectorized 성능

Multiple plane 활용 시:
- 4-plane Ares-V가 Ares(1-plane) 대비 추가 **~3.5×** throughput.
- 8-plane Ares-V: **~6.8×** throughput.
- Plane 간 독립적 연산으로 near-linear scaling.

### 3.4 Vector Similarity Search (VSS) Case Study

Quantized vector similarity search를 multiplication 집약적 워크로드로 평가:

- **데이터셋:** MS-celeb (10M vectors), ImageNet (14M), Celeb-500k (50M). Vector size: 512 elements, int4~int16 양자화.
- Ares: VVM(Vector-Vector Multiplication)을 연속적 multiplication으로 실행.
- ISP 대비 **6.4×** throughput, OSP 대비 **11.66×** throughput.
- Edge device 시나리오에서 energy efficiency 탁월 — data movement가 거의 없기 때문.

### 3.5 Energy 분석

Flash memory의 read/write energy는 이미 낮으나, data movement energy가 dominant:

- PCIe 전송: pJ/bit 단위로 높은 에너지 소비.
- Ares는 결과(수~수십 바이트)만 전송 → data movement energy 90%+ 절감.

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

- **Flash modification:** Latch circuit 수정 (full adder logic), intra-plane transmission peripheral 추가.
- **추가 transistor:** BL당 수십 개 수준. 전체 flash die 면적 대비 negligible (<0.5%).
- **Controller modification:** Ares 연산 command 추가. 표준 NAND interface 확장.
- **Software interface:** Ares 연산을 추상화하는 host-side library 제공.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2024MICRO-summarize/ares-flash-efficient-parallel-integer-arithmetic-operations-using-nand-flash-memory.md|전체 요약 보기]]
