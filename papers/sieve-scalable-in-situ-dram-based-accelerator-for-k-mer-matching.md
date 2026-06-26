---
tags: [paper, 2021, 2021ISCA, topic/cache, topic/dram, topic/pim]
venue: "ACM/IEEE 48th Annual International Symposium on Computer Architecture (ISCA) 2021"
year: 2021
summary_path: "../paper-summaries/2021ISCA-summarize/sieve-scalable-in-situ-dram-based-accelerator-for-k-mer-matching.md"
---

# Sieve: Scalable In-situ DRAM-based Accelerator Designs for Massively Parallel k-mer Matching

**Venue:** ACM/IEEE 48th Annual International Symposium on Computer Architecture (ISCA) 2021
**저자:** Lingxi Wu (University of Virginia), Rasool Shariﬁ (University of Virginia), Marzieh Lenjani (University of Virginia), Kevin Skadron (University of Virginia), Ashish Venkat (University of Virginia)

## 개요

- 바이오informatics 파이프라인의 핵심 단계인 k-mer matching이 modern high-end computing platforms에서 주요 병목으로 작용
- k-mer matching은 random access pattern과 낮은 computational intensity를 특징으로 하며, cache-friendly하지 않음
- 현대 sequencing 기술의 데이터 생성 속도가 Moore's Law를 초과: 2025년 metagenomics 시장 규모 **$1.4 billion** 예상, YouTube 및 Twitter를 초과하는 데이터양 처리 필요
- Precision medicine 환경에서 NovaSeq 기반 시퀀싱으로 **48시간** 내 **10 TB** 데이터 생성 가능하나, 분석 파이프라인(예: Kraken)에는 **약 68일** 소요
- 기존 hash table 기반 k-mer database의 캐시 효율성 극히 낮음: 연속 k-mer 중 단 **8%만 동일 bucket**에 인덱싱되어 새로운 bucket을 반복적으로 memory에서 fetch
- k-mer record는 약 **12 bytes**이나, cache line 단위 fetch로 인해 대부분의 bandwidth와 energy 낭비 발생
- 연산 강도(computational intensity)가 낮아 memory wall 문제를 완화할 수 없음 — CLARK에서 counter 업데이트는 trivial한 반면, DB에서 k-mer retrieval은 수많은 cycle 소모

## 방법론

### 3.1. 데이터 레이아웃 (Column-wise Data Mapping)

- k-mer 패턴을 2비트로 인코딩 (A: 00, C: 01, G: 10, T: 11) 후 DRAM bitline을 따라 column-wise로 전치 배치
- 각 subarray 내 bit cell을 3개 영역으로 분할:
  - **Region-1**: reference와 query k-mer 패턴이 교차 저장 (interleaved)
  - **Region-2**: payload offset (각 reference k-mer의 시작 주소)
  - **Region-3**: 실제 payload (taxon label 등)
- Region-2/3는 기존 row-major 형식으로 저장
- Region-1을 더 작은 pattern group으로 세분화하고, 각 group마다 **64개의 다른 query k-mer**가 복제되어 배치 (wire 전송 지연 방지)
- DDR3 micron 32M 기준 pattern group당 **512 reference + 64 query = 576 k-mer**
- Batch 크기는 chip의 prefetch size에 의해 결정 (8 byte prefetch → 64 bits 쓰기)

### 3.2. Matcher 회로

- 각 sense amplifier를 Matcher로 강화: **XNOR gate + AND gate + 1-bit latch** 구성
- XNOR gate: reference bit와 query bit의 동일 여부 검사
- AND gate: 이전 matching 결과(latch)와 현재 XNOR 출력을 비교하여 latch 업데이트
- latch는 초기값 **1** (match로 가정)으로 시작, 비트 단위 누적 매칭 결과 저장
- Match Enable 토글로 matcher의 bypass/참여 제어 가능

### 3.3. Early Termination Mechanism (ETM)

- 행 전체 latch가 **0**으로 저장되면 ETM이 추가 row activation 중단
- 전체 행을 OR하는 대신 segment 분할 후 파이프라인 방식으로 부분 결과 전파
- **256 latch마다 1개의 Segment Register (SR)** 삽입
- 각 DRAM row cycle마다 segment가 이전 SR 값을 가져와自身的 latch들과 OR 후 다음 SR로 출력
- ETM flush를 위해 최대 **256 DRAM row cycles** 추가 소요 (최악의 경우)

### 3.4. Column Finder (CF)

- 매칭된 reference k-mer의 column (bitline) 위치를 탐지하여 payload offset 및 payload 검색
- 2단계 파이프라인 shifter:
  - **1단계**: Backup Segment Register (BSR)를 shift하여 매칭된 segment 탐지
  - **2단계**: 해당 segment를 Reserved Segment (RS)로 복사 후 최종 column index 추출
- ETM 세그먼트를 재활용하여 하드웨어 비용 최소화
- CF는 후속 k-mer 매칭과 겹쳐서(overlap) 수행됨

### 3.5. Sieve Type-1 / Type-2 / Type-3 비교

- **Type-1**: DRAM chip I/O 인터페이스에 로직 배치, bank 레이아웃 변경 없음 → 최소 침입 (area overhead **2.48%**)
  - SRAM Buffer(SB), Matcher Array(MA), Skip Bits Register(SkBR), Start Batch Register(StBR)로 구성
  - 행당 **128 batch**로 나뉘어 처리, column decoder로 batch 선택
  - 가장 낮은 parallelism과 높은 latency이나, DRAM 용량 증가에 따른 성능 확장 가능
- **Type-2**: subarray group에 compute buffer 배치 (여러 subarray가 하나의 k-mer matching unit 공유)
  - LISA 방식으로 subarray 간 빠른 row copy 활용 (hop delay 약 **4ns**, tCCD 대비 **~8배 빠름**)
  - Compute buffer 1~128개/bank까지 변형 가능 → performance-area trade-off 탐색
  - area overhead: 1CB(**1.03%**), 64CB(**6.3%**), 128CB(**10.75%**)
- **Type-3**: 각 subarray의 local row buffer에 직접 로직 통합 (subarray-level parallelism, SALP 활용)
  - 최고 parallelism과 성능 잠재력, 그러나 최고 설계 복잡성
  - area overhead: **10.90%**
  - subarray당 독립적으로 k-mer matching 수행 가능

### 3.6. K-mer to Subarray 매핑 및 시스템 통합

- 색인 테이블: 각 entry가 **8-byte subarray ID** + 해당 subarray의 첫/마지막 k-mer 정수값 보유
- 색인 테이블 크기: 500GB 용량에서도 **2MB 미만**으로 선형 확장
- DIMM 및 PCIe 두 가지 form factor 지원
  - DIMM: **0.37W/GB**, **25 GB/s** 대역폭 → Type-1에 적합
  - Type-2: 최소 PCIe 3.0 x8, Type-3: 최소 PCIe 4.0 x16 필요
- PCIe 패킷 기반 프로토콜: 4KB payload당 **340 요청**, **24 PCIe 패킷**으로 32GB Sieve 포화

## 핵심 기여

- k-mer matching은 bioinformatics 파이프라인의 핵심 병목이며, memory-bound 특성으로 인해 기존 CPU/GPU로는 해결 불가능
- Sieve는 DRAM bitline에 reference k-mer를 수직 배치하고, single-row activation + ETM으로 **326x speedup / 74x energy saving** (CPU 대비) 달성
- 세 가지 디자인(Type-1~3)을 통해 hardware complexity와 성능 간 체계적 trade-off 분석
- Type-3가 최고 성능(404x speedup over CPU)을 보이나, Type-2는 area-efficient한 대안으로 **55x speedup** 달성
- in-situ PIM 가속기가 bioinformatics의 근본적인 memory wall 문제를 효과적으로 해결할 수 있음을 실증

## 주요 결과

- 구현 언어: Verilog (SPICE 시뮬레이션 포함)
- 45nm PTM 트랜지스터 모델 기반 circuit-level SPICE 검증
- matcher 회로의 입력 커패시턴스: **약 0.2pF** (BL 커패시턴스 22pF 대비 미미)
- sense amplifier 활성화 후 matcher 결과 준비 시간: **1ns 미만**
- OpenRAM으로 SRAM Buffer 모델링, FreePDK45로 면적/지연시간/에너지 추정
- Stillmaker et al. 스케일링 팩터로 22nm 기술 노드로 축소 추정

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2021ISCA-summarize/sieve-scalable-in-situ-dram-based-accelerator-for-k-mer-matching.md|전체 요약 보기]]
