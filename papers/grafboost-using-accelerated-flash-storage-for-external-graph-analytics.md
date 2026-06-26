---
tags: [paper, 2018, 2018ISCA, topic/dram, topic/nvm, topic/storage]
venue: "45th Annual International Symposium on Computer Architecture (ISCA '18)"
year: 2018
summary_path: "../paper-summaries/2018ISCA-summarize/grafboost-using-accelerated-flash-storage-for-external-graph-analytics.md"
---

# GraFBoost: Using Accelerated Flash Storage for External Graph Analytics

**Venue:** 45th Annual International Symposium on Computer Architecture (ISCA '18)
**저자:** Sang-Woo Jun (MIT), Andy Wright (MIT), Sizhuo Zhang (MIT), Shuotao Xu (MIT), Arvind (MIT)

## 개요

- 대규모 그래프 (수십억 정점, 수천억 엣지)의 분석은 소셜 네트워크, 신경 구조 분석, 전력망 최적화 등에 필수적
- 기존 시스템의 한계:
  - **메모리 기반 (GraphLab)**: 전체 그래프를 DRAM에 저장 → 메모리 부족 시 swap thrashing으로 성능 급락
  - **반외부 (FlashGraph)**: 정점만 DRAM에 저장, 엣지는 플래시 → 정점 데이터가 DRAM에 맞지 않으면 실패
  - **스트리밍 (X-Stream)**: 모든 슈퍼스텝에서 전체 그래프 순회 → 희소 활성 목록 알고리즘에서 비효율
  - **외부 (GraphChi)**: 디스크 기반 → 그래프를 여러 번 읽어야 하여 성능 저하
- 핵심 문제: **DRAM 용량에 독립적으로 대규모 그래프 분석을 지원하는 단일 노드 시스템 부재** — 기존 시스템은 모두 DRAM 크기에 비례하는 비용/자원 필요

## 방법론

### 3.1. Sort-Reduce 알고리즘
- 그래프 분석의 각 슈퍼스텝에서 정점 업데이트를 로그에 기록
- 로그된 업데이트를 외부 정렬(sort) 후 리듀스 함수를 적용하여 중복 제거 및 병합
- 정렬과 리듀스를 **교차(interleave)** 수행 → 메모리 사용량 최적화 + 처리 효율 극대화
- 랜덤 업데이트 → 순차 SSD 블록 접근으로 변환 → 플래시 I/O 효율 극대화

### 3.2. 하드웨어 가속기 (FPGA)
- Xilinx VC707 FPGA 보드 + 1GB DRAM + 1TB 플래시 스토리지
- CPU 대비 **2~4배 성능 향상** (소프트웨어 전용 대비)
- SSD 플래시 컨트롤러 칩 (4~8 ARM 코어, 500MB~1GB DRAM)에 통합 가능한 수준의 자원 사용
- ASIC 구현 시 SSD 컨트롤러 내 탑재 가능

### 3.3. 프로그래밍 모델
- Vertex-centric 프로그래밍 모델 지원
- 각 정점 프로그램: 현재 정점 + 이웃 정점/엣지 정보를 입력으로 받아 정점 값 업데이트 및 메시지 전송
- Push/Pull 방식 모두 지원
- Pregel, Giraph, GraphLab과 유사한 인터페이스

### 3.4. 소프트웨어 구현 (GraFSoft)
- 32코어 Xeon 서버 (최대 128GB DRAM, 2.5TB 플래시)
- 멀티스레드 병렬 처리로 CPU 활용 극대화
- 하드웨어 가속기 없이도 기존 시스템 대비 경쟁력 있는 성능

## 핵심 기여

- **핵심 기여**: Sort-Reduce 알고리즘으로 랜덤 그래프 접근을 순차 SSD 접근으로 변환하는 새로운 외부 그래프 분석 아키텍처
- **DRAM 독립성**: 1GB DRAM으로 40억 정점/1280억 엣지 처리 — 기존 시스템의 DRAM 의존성 탈피
- **실용성**: FPGA 기반 하드웨어 가속기가 SSD 컨트롤러 내 탑재 가능한 수준의 자원 사용
- **의의**: 대규모 그래프 분석을 단일 노드, 제한된 자원으로 처리 가능한 새로운 패러다임 제시 — 클러스터 없이 테라바이트급 그래프 분석 가능

## 주요 결과

- **하드웨어**: Xilinx VC707 FPGA 보드, 1GB DRAM, 1TB NVMe 플래시
- **소프트웨어**: C++ 기반, vertex-centric 프로그래밍 모델
- **시스템 구성**: 단일 노드 — FPGA 가속기 + 호스트 서버 연결
- **프로그래밍 환경**: 유연한 프로그래밍 환경으로 다양한 그래프 알고리즘 지원

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2018ISCA-summarize/grafboost-using-accelerated-flash-storage-for-external-graph-analytics.md|전체 요약 보기]]
