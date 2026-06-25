---
tags: [paper, 2018, 2018ISCA, topic/storage, topic/near-data-processing]
venue: "ISCA 2018"
year: 2018
summary_path: "../paper-summaries/2018ISCA-summarize/grafboost-using-accelerated-flash-storage-for-external-graph-analytics.md"
---

# GraFBoost: Using Accelerated Flash Storage for External Graph Analytics

**Venue:** ISCA 2018
**저자:** Sang-Woo Jun, Andy Wright, Sizhuo Zhang, Shuotao Xu, Arvind (MIT)

## 개요

대규모 그래프(최대 40억 정점, 1280억 엣지)를 1GB DRAM의 단일 노드에서 처리하는 FPGA 기반 플래시 스토리지 시스템이다. Sort-Reduce 알고리즘으로 랜덤 접근을 순차 SSD 접근으로 변환한다.

## 방법론

### Sort-Reduce 알고리즘
- 정점 업데이트를 로그한 후 외부 정렬 + 리듀스 함수 교차 적용
- 랜덤 그래프 접근 → 순차 SSD 블록 접근으로 변환

### 하드웨어 가속기 (FPGA)
- VC707 FPGA + 1GB DRAM + 1TB Flash
- 소프트웨어 대비 2~4× 성능 향상
- SSD 컨트롤러 내 탑재 가능한 자원 사용

### 지연 업데이트
- 새/이전 정점 값을 함께 저장하여 중복 I/O 제거

## 핵심 기여

1. Sort-Reduce 알고리즘으로 DRAM 독립적 그래프 분석 달성
2. FPGA 가속기로 SSD 대역폭까지 포화시키는 성능
3. 단일 노드에서 테라바이트급 그래프 처리 가능

## 주요 결과

- **DRAM 독립성**: 1GB DRAM으로 40억 정점/1280억 엣지 처리
- **모든 벤치마크 성공**: 5개 그래프 모두 30분 이내 완료
- **기존 시스템 대비**: GraphLab/FlashGraph/X-Stream/GraphChi 중 유일하게 전체 벤치마크 처리
- **하드웨어 가속 효과**: 2~4× 성능 향상

## 한계점

- 현재 FPGA 기반 프로토타입, ASIC 구현 필요
- 정렬 비용이 그래프 크기에 비례

## 관련 개념

- [[paper-wiki/concepts/storage.md|Storage]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
