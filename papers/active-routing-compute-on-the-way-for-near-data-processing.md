---
tags: [paper, 2019, 2019HPCA, topic/dram, topic/near-data-processing, topic/pim]
venue: "25th IEEE International Symposium on High Performance Computer Architecture (HPCA '19)"
year: 2019
summary_path: "../paper-summaries/2019HPCA-summarize/active-routing-compute-on-the-way-for-near-data-processing.md"
---

# Active-Routing: Compute on the Way for Near-Data Processing

**Venue:** 25th IEEE International Symposium on High Performance Computer Architecture (HPCA '19)
**저자:** Jiayi Huang, Ramprakash Reddy Puli, Pritam Majumder, Sungkeun Kim, Rahul Boyapati, Ki Hwan Yum, Eun Jung Kim (Texas A&M University, NVIDIA, Intel Corporation)

## 개요

- 데이터 폭증 시대에 데이터 분석 애플리케이션(신경망, 그래프 처리 등)은 **large memory footprint + low data reuse rate** 특성을 보임.
- CPU 연산 밀도와 메모리 대역폭 간의 격차가 심화 → 연산 능력을 충분히 활용하지 못함.
- 기존 처리 방식의 한계:
  - **PIM (Processing-in-Memory):** 메모리에 연산 요소를 배치하여 데이터 이동 감소. 그러나 데이터가 동일 모듈에 없으면 메모리 네트워크를 통해 데이터를 가져와야 하여 통신/에너지 오버헤드 발생.
  - **기존 네트워크 내 연산 (NYU Ultracomputer 등):** 순수 감소(reduction) 연산만 지원. `dot product` 같은 중간 결과 산술 연산 가속 불가.
  - **MAERI (DNN 가속기):** 리프 노드에서만 곱셈 수행, 네트워크 토폴로지에 정적으로 고정되어 적응력 부족.
- 핵심 문제: **데이터 위치 근처에서 연산을 수행하면서, 중간 결과를 네트워크 경로 상에서 효율적으로 집약(aggregate)하는 방법 부재.**

## 방법론

### 3.1. 시스템 구성 (Figure 2)

- 호스트 CPU가 HMC 기반 메모리 네트워크에 연결 (Dragonfly 토폴로지, 16 큐브).
- 각 HMC의 로직 레이어에 **Active-Routing Engine (ARE)** 탑재.
- `Update` 패킷: 오퍼랜드를 가져와 NDP(Near-Data Processing)로 부분 합(partial sum) 계산.
- `Gather` 패킷: ARTree를 따라 부분 결과를 루트로 집약(reduction).

### 3.2. Three-Phase Packet Processing

#### 3.2.1. ARTree Construction (트리 구축)

- Update 패킷이 메모리 네트워크를 통과하며 동적으로 ARTree 구축.
- 각 큐브는 flow ID를 등록하고, 패킷이 해당 큐브에 스케줄되지 않았으면 자식 큐브로 포워딩.
- 부모-자식 관계를 기록하여 트리 브랜치 형성 (Figure 3a).

#### 3.2.2. Update Phase (데이터 처리)

- 오퍼랜드 요청을 데이터가 위치한 메모리 큐브로 전송.
- 응답 도착 시 산술 연산(곱셈-누적 등)을 스케줄된 큐브에서 수행.
- 오퍼랜드가 서로 다른 큐브에 분산된 경우, 최소 경로의 마지막 공통 큐브에서 요청을 복제하여 처리 (Figure 3b).
- 같은 큐브의 모든 중간 결과를 부분 합으로 축소.

#### 3.2.3. Gather Phase (집약)

- 모든 Update 패킷 전송 후 Gather 패킷을 루트에서 리프로 전파.
- 리프 노드에서 부분 합을 네트워크에서 순차적으로 집약(reduction)하며 루트로 전달.
- 자식의 Update Phase 완료 시 parent에게 Gather response 전송 → flow record 해제 (Figure 3c).

### 3.3. Memory Access Patterns and Enhancements

- **Regular-Regular:** 캐시 블록 granularity로 벡터 처리. 데이터 locality 최대 활용.
- **Regular-Irregular:** irregular 데이터를 regular 데이터 위치로 전송하여 처리.
- **Irregular-Irregular:** 단일 오퍼랜드 쌍을 스케줄된 큐브로 전달 (스칼라 연산).
- 오프로딩 granularity를 패턴별로 조정하여 offloading overhead를 경감.

### 3.4. Hardware Implementation

- **ISA Extension:** `UpdateRR`, `UpdateRI`, `UpdateII`, `Gather` API를 확장 명령어로 변환.
- **Network Interface (NI):** 전용 레지스터에 opcode/operand 정보 기록 → 패킷 조립.
- **Active-Routing Engine (ARE):** HMC 로직 레이어에 통합.
  - Packet Processing Unit: 패킷 디코딩 및 연산 스케줄링.
  - Flow Table: 트리 구조 및 상태 정보 관리 (flow ID, opcode, 부모/자식, 부분 결과, req/rep counter).
  - Operand Buffers: 오퍼랜드 임시 저장. 여러 flow가 공유하여 처리량 향상.
  - ALU: 가벼운 산술 로직. 1250MHz, 멀티플라이 9사이클, 버퍼 접근 1사이클. 정수/부동소수점 곱셈-누적, sum/xor/min/max 등 감소 연산 지원.
- **Integrity Considerations:**
  - 가상 메모리: 오프로드 명령어를 확장 로드/스토어로 처리하여 동일한 VA→PA 변환.
  - 캐시 일관성: 오프로드 패킷을 먼저 directory로 전송하여 back-invalidation 수행.

### 3.5. Enhancements

- **ART-tid:** 스레드 ID로 네트워크 포트를 인터리빙하여 균형 잡힌 트리 구축.
- **ART-addr:** 오퍼랜드 주소 기반으로 가장 가까운 포트를 통해 Update 패킷 전송 → 더 얕은 트리 생성.
- **Dynamic Offloading:** 런타임에 데이터 접근 locality를 판단하여 Active-Routing과 호스트 처리를 적응적으로 전환 (lud 사례: 2x speedup).

## 핵심 기여

- **핵심 Contribution:** 네트워크 내에서 데이터 흐름 스타일로 연산을 수행하는 인네트워크 컴퓨팅 아키텍처 최초 제안.
- **성능:** PIM(PEI) 대비 최대 7x speedup, 지오메인 60% 성능 향상.
- **에너지 효율:** EDP 80% 감소.
- **의의:** 데이터 집약적 애플리케이션에서 데이터 이동 병목을 근본적으로 해결하며, HMC/HBM 기반 차세대 메모리 네트워크 시스템 설계의 새로운 패러다임을 제시.

## 주요 결과

- **구현 언어:** Verilog (ARE 하드웨어), C/C++ (시뮬레이터)
- **시뮬레이터:** McSimA+ (코어/캐시 계층) + CasHMC (HMC 메모리 모델링)
- ** ISA Extension:** Pin 기반 프론트엔드에서 확장 명령어 구현.
- **ARE 합성:** TSMC 45nm 라이브러리. 멀티플라이 6.61ns, 버퍼 접근 0.59ns.
- **면적/전력:** ALU 0.02mm²/17.8mW, Operand Buffer 0.026mm²/16.9mW, Flow Table 0.05mm²/33.2mW.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2019HPCA-summarize/active-routing-compute-on-the-way-for-near-data-processing.md|전체 요약 보기]]
