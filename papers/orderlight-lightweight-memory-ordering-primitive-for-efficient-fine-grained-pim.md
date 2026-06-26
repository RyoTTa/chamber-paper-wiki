---
tags: [paper, 2021, 2021MICRO, topic/dram, topic/gpu, topic/pim]
venue: "MICRO 2021 (54th Annual IEEE/ACM International Symposium on Microarchitecture)"
year: 2021
summary_path: "../paper-summaries/2021MICRO-summarize/orderlight-lightweight-memory-ordering-primitive-for-efficient-fine-grained-pim-computations.md"
---

# OrderLight: Lightweight Memory-Ordering Primitive for Efficient Fine-Grained PIM Computations

**Venue:** MICRO 2021 (54th Annual IEEE/ACM International Symposium on Microarchitecture)
**저자:** Anirban Nag (Uppsala University), Rajeev Balasubramonian (University of Utah)

## 개요

- 현대 워크로드(Neural Networks, Genomic Analysis, Data Analytics)는 **데이터 집약적 단계**가 전체 실행의 상당 부분을 차지하며, 기존 GPU/TPU로는 메모리 대역폭 병목을 해결할 수 없음
- PIM(Processing-in-Memory)은 메모리 근처에서 연산을 수행하여 메모리 대역폭 이점을 제공하지만, 두 가지 핵심 측면에 대한 연구가 부족함:
  1. PIM에 오프로딩하는 연산의 **세분화된(granularity) 정도**
  2. PIM 연산과 호스트 메모리 접근 간의 **중재(arbitration) 세분화 정도**
- 기존 PIM 연구는 대부분 ** coarse-grained approach**를 사용하며, 이는 다음과 같은 높은 비용을 유발:
  - 호스트 프로세서와 호환되지 않는 메모리 인터페이스 필요
  - 호스트의 동시 메모리 접근 금지로 인한 프로세서 활용도 저하
  - 복잡한 메모리 측 로직 필요
- 기존 메모리 순서 원어인 **fence**는 fine-grained PIM에 적합하지 않음:
  - fence 오버헤드: 165~245 cycles (vector_add 커널 기준)
  - TS 크기에 따라 4.5x~25x 성능 저하 발생
  - Store에 대한 ordering이 글로벌 시리얼라이제이션 포인트까지만 보장되어 PIM에는 불충분

## 방법론

### 3.1. PIM 커널과 순서 요구사항

- 호스트(GPU)가 PIM 메모리 명령어를 발행하여 PIM 연산을 수행하는 **PIM 커널** 개념 도입
- Figure 4: PIM 커널 예시 (Fetch-and-Add, Store 등)
- 기존 fence는 PIM 명령어 사이에 삽입되어야 하며, 이는 극심한 오버헤드를 유발
- OrderLight는 **PIM 커널 내에서 명령어 순서를 보장**하면서도 코어의 대기를 최소화

### 3.2. OrderLight 패킷 구조

- Figure 8에 표시된 OrderLight 패킷 필드:
  - **Packet ID (2b)**: 일반 load/store 요청과 구별
  - **Channel ID (4b)**: ordering을 적용할 메모리 채널 식별
  - **Memory-group ID (4b, 선택적)**: 특정 메모리 그룹에만 ordering 적용 가능
  - **Packet number**: 메모리 컨트롤러의 sanity check 및 통계 수집용
- 패킷은 메모리 파이프를 통해 컨트롤러까지 전달되며, 모든 단계에서 순서가 유지됨

### 3.3. 코어 측 설계 변경

- **Operand Collector 변경**: OrderLight 패킷은 모든 선행 PIM 요청이 operand collector를 떠난 후에만 발행됨
  - PIM 요청 카운터를 사용하여 추적
  - 카운터가 0일 때만 OrderLight 패킷 발행
  - fence 대비 훨씬 짧은 시간 동안만 명령 발행 중단

### 3.4. 메모리 파이프 설계 변경

- **캐시 bypass**: PIM 요청은 캐시를 우회하여 non-temporal load/store로 동작
- **경로 분기(Diverging Paths) 처리**: Copy-and-merge 기법 사용
  - Figure 9: 분기점에서 패킷 복제, 합류점에서 병합
  - FSM으로 분기점/합류점 제어
- **메모리 컨트롤러**: 
  - Request counter와 OrderLight flag로 각 PIM 메모리 그룹별 순서 강제
  - OrderLight flag가 설정된 후에는 해당 메모리 그룹의 요청을 스케줄링하지 않음
  - 선행 요청이 모두 스케줄링된 후 flag 해제

## 핵심 기여

- **핵심 기여**: PIM에서의 효율적인 메모리 순서 강제를 위한 최초의 메모리 중심 순서 프리미티브 제안
- **성능 향상**: fence 대비 5.5x~8.5x 실행 시간 개선
- **의의**: Fine-grained PIM 접근법의 실용화를 위한 핵심 장벽 해결
  - 기존 PIM 연구의 coarse-grained 접근법의 한계를 극복
  - 호스트 프로세서(GPU)와의 동시 동작 지원
  - 현대 워크로드의 데이터 집약적 단계 가속화

## 주요 결과

| 항목 | 내용 |
|------|------|
| **시뮬레이터** | GPGPU-Sim 기반 |
| **호스트 GPU** | Volta Titan V (80 SMs, 1200 MHz) |
| **메모리** | HBM (16 channels, 16 banks/channel, 850 MHz) |
| **프로토콜** | Scoped/relaxed consistency 모델 (GPU 호환) |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2021MICRO-summarize/orderlight-lightweight-memory-ordering-primitive-for-efficient-fine-grained-pim-computations.md|전체 요약 보기]]
