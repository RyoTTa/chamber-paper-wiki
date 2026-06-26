---
tags: [paper, 2022, 2022ISCA, topic/cache, topic/dram, topic/gpu, topic/near-data-processing, topic/nvm, topic/storage]
venue: "ISCA 2022 (The 49th Annual International Symposium on Computer Architecture)"
year: 2022
summary_path: "../paper-summaries/2022ISCA-summarize/smartsage-training-large-scale-gnns-using-in-storage-processing-architectures.md"
---

# SmartSAGE: Training Large-scale Graph Neural Networks using In-Storage Processing Architectures

**Venue:** ISCA 2022 (The 49th Annual International Symposium on Computer Architecture)
**저자:** Yunjae Lee, Jinha Chung, Minsoo Rhu (KAIST)

## 개요

- 그래프 신경망(GNN)은 e-commerce(Pinterest PinSAGE, Alibaba AliGraph) 등에서 수십억~수백억 규모의 그래프 노드/엣지를 다루지만, 현대 ML 프레임워크(DGL, PyG)는 **in-memory processing 모델**을 채택하여 전체 그래프 데이터가 DRAM에 적재되어야 함
- 대규모 그래프 데이터셋은 인접 엣지 리스트 배열(neighbor edge list array)이 수백 GB~수천 GB에 달하므로, DRAM 용량 제한으로 인해 그래프 구조 및 특성 벡터 크기의 확장이 불가능
- 기존 SSD 기반 접근법(mmap)의 한계:
  - Neighbor sampling은 fine-grained irregular parallelism을 보이며, LLC miss rate이 평균 **62%**, DRAM 대역폭 활용률은 **21%**에 불과 (Figure 5)
  - mmap 기반 SSD 시스템은 DRAM 대비 평균 **9.8×** (최대 19.6×) 성능 저하 발생 (Figure 6)
  - GPU 유휴 시간이 크게 발생하여 producer-consumer throughput mismatch가 심각 (Figure 7)

## 방법론

### 3.1. Firmware 기반 CSD 아키텍처

- SmartSAGE는 SSD 펌웨어 내부에 ISP 유닛을 구현하여 기존 하드웨어(SSD) 및 소프트웨어(OS, NVMe 프로토콜)와 완전 호환
- **Firmware 기반 CSD 선택 이유:**
  - Neighbor sampling은 무작위 데이터 조회 중심으로 연산 강도가 낮아 엔베드 코어에 적합
  - FPGA 기반 CSD(SmartSSD 등)는 SSD→FPGA 및 FPGA→CPU 2단계 P2P 전송이 발생하여 지연 시간 오버헤드가 큼 (Figure 9)
  - Firmware 기반은 단일 SSD→CPU 전송으로 효율적

### 3.2. ISP Neighbor Sampling 연산

- **ISP 제어 유닛:** CPU→SSD 오프로딩된 서브그래프 생성 요청을 처리
- **서브그래프 생성기:** 대규모 입력 그래프에서 서브그래프를 추출하고, low-level flash 디바이스에 flash page read 요청 전송
- **동작 흐름 (Figure 11):**
  1. SmartSAGE 드라이버가 neighbor sampling 설정 데이터(NS_config)와 함께 서브그래프 생성 요청을 NVMe write command로 전송
  2. SSD 펌웨어가 DMA 접근으로 CPU 메모리에서 NS_config를 SSD로 복사
  3. 주소 변환 후 flash page read 요청을 low-level flash controller에 전달
  4. flash page가 SSD DRAM page buffer에 캐시되면, embedded core가 fine-grained neighbor sampling 수행
  5. 완성된 서브그래프를 DMA write로 CPU DRAM으로 전송

### 3.3. 지연 최적화 소프트웨어 런타임

- **Direct I/O:** Linux direct I/O(O_DIRECT 플래그)를 활용하여 OS page cache를 우회하고 사용자 공간 스크래치패드 버퍼에서 high locality 데이터 이동을 수동으로 관리
  - mmap 기반 대비 neighbor sampling 지연 시간 **2.9×** 감소 (섹션 6.2)
- **I/O command coalescing:** 모든 대상 노드의 neighbor sampling을 단일 NVMe command로 통합하여 command/control 오버헤드 대폭 감소
  - mini-batch 레벨에서 모든 target node의 sampling을 하나의 NS_config로 캡슐화 (Figure 12)

## 핵심 기여

1. **대규모 GNN 학습의 메모리 용량 병목 해결:** NVMe SSD를 활용하여 in-memory processing의 DRAM 용량 제한을 극복
2. **ISP 기반 하드웨어 가속:** SSD 내부에서 neighbor sampling을 수행하여 SSD→DRAM 데이터 전송량을 20× 감소
3. **지연 최적화 소프트웨어:** Direct I/O와 I/O command coalescing으로 OS page cache 오버헤드 제거
4. **하드웨어/소프트웨어 공동 설계:** mmap 기반 SSD 대비 3.5×~10.1× 성능 향상
5. **범용 CSD 호환성:** NVMe 프로토콜 완전 호환으로 기존 CSD 아키텍처에 즉시 적용 가능

**Broader Significance:** SmartSAGE는 GNN 학습의 메모리 용량 병목을 해결하기 위해 ISP 기반 SSD를 활용하는 최초의 시스템으로, 하드웨어-소프트웨어 공동 최적화를 통해 DRAM 수준의 성능을 달성하면서도 대규모 그래프 학습을 가능하게 함

## 주요 결과

- **구현 언어:** Verilog(하드웨어), C++(소프트웨어)
- **CSD 플랫폼:** Cosmos+ OpenSSD (2TB NVMe flash SSD, dual-core ARMv7 Cortex-A9)
- **호스트 시스템:** Intel Xeon Gold 6242 CPU (192GB DRAM) + NVIDIA Tesla T4 GPU
- **소프트웨어 프레임워크:** PyTorch Geometric 기반 GraphSAGE 구현
- **그래프 데이터셋:** Kronecker fractal expansion으로 합성된 대규모 그래프 (Reddit, Movielens, Amazon, OGBN-100M, Protein-PI)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2022ISCA-summarize/smartsage-training-large-scale-gnns-using-in-storage-processing-architectures.md|전체 요약 보기]]
