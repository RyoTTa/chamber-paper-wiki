---
tags: [paper, 2022, 2022HPCA, topic/cache, topic/dram, topic/llm-inference, topic/nvm, topic/storage]
venue: "IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2022"
year: 2022
summary_path: "../paper-summaries/2022HPCA-summarize/rm-ssd-in-storage-computing-for-large-scale-recommendation-inference.md"
---

# RM-SSD: In-Storage Computing for Large-Scale Recommendation Inference

**Venue:** IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2022
**저자:** Xuan Sun, Hu Wan, Qiao Li (City University of Hong Kong); Chia-Lin Yang (National Taiwan University); Tei-Wei Kuo (National Taiwan University, NTU High Performance and Scientific Computing Center); Chun Jason Xue (City University of Hong Kong)

## 개요

- 생산 규모의 추천 시스템(recommendation system)에서 embedding 테이블 크기가 수백 GB에 달하며, 향후 TB 수준으로 성장할 전망 → DRAM 용량 한계에 도달
- DRAM cost-per-GB가 높아 무한 확장은 현실적이지 않으며, SSD로의 이전이 경제적 대안이나 naive SSD 배포 시 심각한 성능 저하 발생
- Read amplification: embedding vector 크기(64B~256B)와 flash page 크기(4KB~32KB) 불일치로 인해 최대 수십 배의 read amplification 발생 (Fig. 3)
- 불규칙한 embedding access pattern:|unique indices가 전체의 84.74%를 차지하며, 상위 10,000개 hot index가 전체 lookups의 59.2%를 차지 → page cache 효율 극히 낮음 (Fig. 4)
- 기존 RecSSD는 embedding lookup만 offload하고 MLP layer는 host에서 처리 → MLP-dominated 모델에 대한 성능 개선 미흡
- Naive SSD 배포 시 embedding-dominated 모델(RMC1, RMC2)에서 DRAM 대비 수십 배 성능 저하, MLP-dominated 모델(RMC3)에서도 상당한 성능 격차

## 방법론

### 3.1. 시스템 개요

- RM-SSD 컨트롤러는 기존 NVMe SSD 구성요소(NVMe Controller, FTL, FMC) + Embedding Lookup Engine(orange) + MLP Acceleration Engine(green)으로 구성 (Fig. 5)
- NVMe Controller: host-SSD 간 NVMe 프로토콜 통신 처리
- FTL: LBA → PBA 변환, block I/O와 inference 요청을 MUX(round-robin)로 분기
- MMIO Manager: host-side memory interface(RM Reg. 통한 low-latency control parameter 교환)와 DMA transmission(lookup indices, bottom MLP input 대량 전송) 지원
- Inference 시 두 엔진이 동시 활성화: Embedding Lookup Engine이 lookup 결과를 Top MLP에 전달, Bottom MLP가 Dense input 처리 → 결과 concatenate → Top MLP 최종 연산

### 3.2. Embedding Lookup Engine

- **EV Translator (Embedding Vector Translator)**: embedding table metadata(extent별 index range + start LBA)를 FPGA 내부 DRAM에 저장
  - Lookup arrive 시: (1) metadata scan → (2) Index Buffer에서 index 추출 → (3) parallel extent ID 검색 → (4) start LBA 결정 → (5) offset × EV_dim으로 최종 LBA 계산
  - Read request 크기 = EV_size = EV_dim × sizeof(float)으로 vector-grained access 구현
- **EV-FMC (Vector-Grained Flash Memory Controller)**:
  - LBA를 FTL을 통해 PBA로 변환 후, request 크기를 EV_size로 설정
  - Flash channel 간 striping으로 parallelism 활용
  - Flash page buffer에서 offset 위치의 vector data만 전송 → transfer time = EV_size/P × page transfer time으로 감소
  - poor locality 특성을 활용하여 나머지 page data 무시 (throughput 향상)
- **EV Sum (Embedding Vector Sum)**:
  - DEMUX가 block I/O vs embedding vector request 구분
  - Floating-point adders(fadd)로 벡터 요소별 병렬 누적 연산
  - 각 embedding table마다 하나의 result vector 생성 → Top MLP 입력으로 전달

### 3.3. MLP Acceleration Engine

- **Basic FC layer design**: Systolic array 대신 adder tree 적용 → 시간 복잡도 RC/(kr·kc) × II로 감소
  - kernel 크기 kr, kc에 따라 리소스 소비 조절 가능
  - II cycles 동안 kc unit을 pipeline하여 fadd/fmul 재사용 → 리소스 소비进一步 reduced
- **Intra-layer decomposition**: Bottom MLP/Embedding과 Top MLP의 첫 번째 FC layer(L0)를 병렬 처리
  - R×C = Rb×C + Re×C로 분해하여 embedding/bottom MLP 결과를 L0에서 바로 concatenate 가능
  - Long inner concatenation 병목 제거
- **Inter-layer composition**: 인접 레이어의 scan 방향을 교대로 배치(row scan ↔ column scan)
  - Li는 column scan, Li+1는 row scan → 파이프라인 stall 없이 MLP 시간 50% 감소
- **Kernel search algorithm**: 최적 kernel 크기 자동 탐색
  - 제약조건: T_bot' ≤ T_emb', T_top' ≤ T_emb', 리소스 최소화
  - Rule 1: BRAM에 모든 weight 적재 가능 여부 판단
  - Rule 2: DRAM 사용 시 DRAM read bandwidth 활용도 최대화 (IID ≥ IIB)
  - Rule 3: N_batch = 1→2→4→... 증가直到 성능 목표 충족
  - Rule 4: 인접 레이어 간 시간 균형 유지

## 핵심 기여

- **핵심 Contribution**: 추천 시스템 전체를 SSD의 low-end FPGA로 offload하는 첫 번째 완전한 in-storage computing 솔루션 제시
- **성능 향상**: Baseline SSD 대비 20~100× throughput improvement, 기존 SOTA(RecSSD) 대비 1.5~15× improvement
- **Key insight**: Embedding lookup의 read amplification 제거(vector-grained access)와 MLP 가속(FPGA pipelining)을 결합하면 embedding-dominated와 MLP-dominated 모델 모두에서 의미 있는 성능 향상 가능
- **실용성**: Low-end FPGA를 사용하여 SSD 내부 리소스/전력 제약을 만족하면서도 높은 가성비 달성
- **한계점**: Embedding vector의 poor locality로 인해 page cache 효과 제한, quantization 미적용으로 인한 정확도-성능 트레이드오프 미탐구

## 주요 결과

- **구현 플랫폼**: Xilinx Virtex 57 Plus UltraScale XCVU9P (Amazon EC2 F1 instance, PCIe gen3 × 16)
- **보드 구성**: FPGA chip + 64GB DDR4 (16GB × 4, 64-byte data width)
- **에뮬레이션**: 4개 DDR4 bank로 4개 flash channel 에뮬레이션, Insider framework의 NVMe driver 수정
- **FTL**: Linear mapping function 적용
- **Read latency 에뮬레이션**: FPGA clock 200MHz(5ns) 기반, T_page = 20μs (T_flush:T_trans = 7:3), C_EV = ⌈(60 × EV_size/P_size + 140) × T_page⌉ cycles
- **소프트웨어**: C++ runtime library + Cython을 통한 PyTorch/Caffe2 통합
  - RM_create_table, RM_open_table, RM_send_inputs, RM_read四个自信 interfaces
  - System-level pipeline: 현재 batch 결과 읽기 전 다음 batch input 사전 전송 → throughput 향상

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2022HPCA-summarize/rm-ssd-in-storage-computing-for-large-scale-recommendation-inference.md|전체 요약 보기]]
