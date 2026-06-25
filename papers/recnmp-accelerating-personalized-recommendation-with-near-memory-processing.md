---
tags: [paper, 2020, 2020ISCA, topic/cache, topic/dram, topic/llm-inference, topic/near-data-processing]
venue: "2020 ACM/IEEE 47th Annual International Symposium on Computer Architecture (ISCA 2020)"
year: 2020
summary_path: "../paper-summaries/2020ISCA-summarize/recnmp-accelerating-personalized-recommendation-with-near-memory-processing.md"
---

# RecNMP: Accelerating Personalized Recommendation with Near-Memory Processing

**Venue:** 2020 ACM/IEEE 47th Annual International Symposium on Computer Architecture (ISCA 2020)
**저자:** Liu Ke, Udit Gupta, Benjamin Youngjae Cho, David Brooks, Vikas Chandra, Utku Diril, Amin Firoozshahian, Kim Hazelwood, Bill Jia, Hsien-Hsin S. Lee, Meng Li, Bert Maher, Dheevatsa Mudigere, Maxim Naumov, Martin Schatz, Mikhail Smelyanskiy, Xiaodong Wang, Brandon Reagen, Carole-Jean Wu, Mark Hempstead, Xuan Zhang (Facebook, Inc.)

## 개요

- 퍼소나라이제이션 추천 시스템(personalized recommendation system)은 딥러닝 모델을 활용하여 데이터센터 AI 연산의 대부분을 차지함. Facebook production 환경에서 추론(inference) 연산의 79% 이상이 추천 모델에 의해 소비됨.
- 기존 아키텍처 연구는 CNN, RNN 등 연산 집약적(compute-intensive)이고 규칙적인(regular) 연산에 집중. 반면 추천 모델은 낮은 연산 강도(compute intensity)와 비규칙적(irregular) 메모리 접근 패턴을 보여 기존 가속화 기법이 효과적이지 않음.
- 추천 모델의 핵심 병목은 희소 임베딩(sparse embedding) 연산인 SparseLengthsSum (SLS)��作. SLS는 대규모 임베딩 테이블에서 비규칙적인 인덱스 기반 lookup과 pooled reduction을 수행하며, 메모리 대역폭 포화(memory bandwidth saturation)를 초래함.
- 임베딩 테이블은 수십 GB에서 수백 GB 규모로, 온칩 메모리(on-chip memory)로는 수용 불가. Roofline 분석 결과 추천 모델은 메모리 대역폭 제한 영역(memory-bound region)에 위치하며, 이론적 성능 한계까지 35.1% 수준의 성능만 달성 중.
- 기존 NMP 솔루션(Chameleon, TensorDIMM)은 DIMM 레벨 병렬성을 활용하지 못하거나, CGRA 코어를 사용하여 면적/전력 오버헤드가 크며, C/A(command/address) 대역폭 제한을 해결하지 못함.

## 방법론

### 3.1. 하드웨어 아키텍처

- RecNMP는 DIMM의 buffer chip에 위치. 각 buffer chip에 DIMM-NMP 모듈과 다수의 rank-NMP 모듈을 포함.
- DIMM-NMP 모듈: host-side memory controller로부터 커스텀 압축 NMP 명령어(NMP-Inst)를 수신하고, 해당 rank로 디스패치. 부분 합(partial sum, PSum) 벡터를 집계하여 최종 결과를 adder tree로 합산 후 host로 반환.
- rank-NMP 모듈: NMP-Inst를 디코딩하여 표준 DDR C/A 명령(ACT, RD, PRE)으로 변환하고, rank 내에서 병렬 임베딩 lookup 및 pooling을 로컬에서 수행.
- NMP 명령어 포맷(Figure 8(d)): DDR cmd (3-bit: ACT/RD/PRE 존재 유무), vector size (vsize), DRAM 주소 (Daddr) 필드로 표준 84-pin C/A 및 DQ 인터페이스에 맞춤.
- Rank-level parallelism: 4 DIMM × 2 ranks/DIMM 구성 시 8× 내부 대역폭 달성 가능. 비례적(parallel) 성능 확장.

### 3.2. 메모리 사이드 캐싱 (RankCache)

- 각 rank-NMP 모듈에 RankCache(128KB 권장)를 통합하여 임베딩 벡터의 시간적 재사용(temporal reuse) 활용.
- LocalityBit: 소프트웨어에서 NMP-Inst에 포함된 캐시 가능 비트. 임베딩 인덱스가 배치 내에서 t회 이상 접근되면 캐시에 저장하고, 미만이면 캐시 bypass.
- 임베딩 테이블은 추론 시 읽기 전용(read-only)이므로 캐시 정확성에 영향 없음.
- 캐시 크기 스위프 결과: 128KB에서 최적 설계점 도달. 8KB 시 hit rate 24.9%로 성능 저하, 128KB 이상은 필수적 캐시 도달 후 수율 개선 미미.

### 3.3. Table-Aware Packet Scheduling

- 기존 메모리 컨트롤러의 FR-FCFS 스케줄링: 여러 임베딩 테이블의 NMP 패킷이 동일 우선순위로 스케줄되어 시간적 locality 파괴.
- Table-aware 스케줄링: 배치(batch) 내 동일 임베딩 테이블에 대한 NMP 패킷을 우선 스케줄링하여 테이블 내 시간적 locality 보존.
- 멀티스레드 메모리 스케줄러[thread-level memory scheduler] 메커니즘에서 착안하여 구현.

### 3.4. Hot Entry Proﬁling

- 프로덕션 임베딩 트레이스 분석: 랜덤 접근(random) 대비 20-60%의 시간적 locality 존재 (8-64MB 캐시 용량 스위프에서 확인).
- 추론 전 NMP 커널의 인덱스 벡터를 프로파일링하여 고주문율(high-frequency) 임베딩 엔트리를 탐지하고 LocalityBit을 설정.
- 프로파일링 오버헤드: 전체 엔드-투-엔드 실행 시간의 <2%.
- 최적화 조합 시 ideal 캐시 성능에 근접하는 hit rate 달성 (Figure 12).

## 핵심 기여

- RecNMP는 상용 DDR4 DRAM 기반의 경량형 near-memory processing으로 프로덕션 추천 모델의 핵심 병목인 희소 임베딩 연산을 가속화.
- Rank-level 병렬성 활용과 하드웨어/소프트웨어 공동 최적화를 통해 **9.8× memory latency speedup** 및 **4.2× end-to-end throughput** 향상.
- 메모리 에너지 45.8% 절감과 co-located FC 연산의 간접 가속 효과까지 제공.
- 기존 Chameleon(TensorDIMM 대비 DIMM 수가 아닌 rank 수에 비례한 확장성) 및 경량 설계(Chameleon 대비 4-6% 면적/전력)로 프로덕션 배포에 적합.
- 추천 모델의 비규칙적 메모리 접근 패턴을 효과적으로 활용하는 locality-aware 하드웨어/소프트웨어 공동 설계의 중요성을 입증.

## 주요 결과

- **구현 언어**: RTL (Verilog/VHDL) 기반 하드웨어 설계 + C++ 소프트웨어 스택
- **설계 기술**: 40nm CMOS 기술 노드 기반 Synopsys Design Compiler 사용
- **시뮬레이션**: Ramulator 기반 DDR4 cycle-level 시뮬레이터 + 커스텀 LRU 캐시 시뮬레이터 + Cacti 기반 에너지/면적 추정
- **시스템 구성 요소**:
  - DIMM-NMP 모듈: DDR PHY 및 프로토콜 엔진, adder tree
  - rank-NMP 모듈: 명령 디코더, RankCache(SRAM), 파이프라인 연산 유닛 (4-stage pipeline)
  - 호스트 확장: 메모리 컨트롤러의 NMP 패킷 스케줄링 로직
- **실제 시스템 평가**: 18코어 Intel Skylake, DDR4-2400MHz 4채널 64GB

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]


## 전체 요약

[[../paper-summaries/2020ISCA-summarize/recnmp-accelerating-personalized-recommendation-with-near-memory-processing.md|전체 요약 보기]]
