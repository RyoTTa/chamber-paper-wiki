---
tags: [concept, dnn-accelerator, dataflow, neural-network, hardware]
source_count: 4
last_updated: 2026-06-26
---

# DNN Accelerator

## Summary

DNN (Deep Neural Network) 가속기는 딥 뉴럴 네트워크의 연산을 가속화하는 전용 하드웨어입니다. 공간적(spatial) 구조를 채택하여 수백 개의 처리 요소(PE)가 병렬로 작동하며, 데이터플로(dataflow) 패턴에 따라 데이터 흐름이 결정됩니다.

## Key Ideas

### 데이터플로 매핑
- **Weight Stationary**: 가중치를 고정시키고 데이터를 순환시키는 매핑
- **Output Stationary**: 출력을 고정시키고 가중치와 입력을 순환시키는 매핑
- **Row Stationary**: 행 단위로 데이터를 재사용하는 매핑
- **MAERI**: 모듈형이고 구성 가능한 기본 블록을 사용하여 유연한 데이터플로 매핑을 지원 — 기존 고정 데이터플로 가속기 대비 8-459% 높은 활용도 달성 ([paper-summaries/2018ASPLOS-summarize/maeri-enabling-flexible-dataflow-mapping-over-dnn-accelerators.md])

### 아키텍처 설계
- Processing Element (PE): 곱셈-누적(MAC) 연산을 수행하는 기본 연산 단위
- Network-on-Chip (NoC): PE 간 데이터 흐름을 제어하는 인터커넥트
- 글로벌 버퍼: 가중치 및 특성 맵 저장
- 메모리 인터페이스: 외부 메모리와의 데이터 교환

### 프로그래밍 가능성
- 고정된 데이터플로 대신 유연한 데이터플로 매핑 지원
- 다양한 DNN 토폴로지(합성곱, 순환, 풀링 등) 지원
- 재구성 가능한 인터커넥트를 통해 동적 데이터 흐름 제어

### 저정밀/아웃라이어 인식 가속화
- **OLAccel**: 아웃라이어 인식 양자화 기반 4비트 신경망 가속기 — 데이터를 저정밀(4비트, 97%)과 고정밀(16비트, 3%) 영역으로 분할, 기존 16비트 가속기 대비 최대 62.2% 에너지 절감 ([paper-summaries/2018ISCA-summarize/energy-efficient-neural-network-accelerator-based-on-outlier-aware-low-precision-computation.md])

### DNN 학습 메모리 최적화
- **Gist**: 레이어별 인코딩으로 feature maps 메모리 최대 4.1× 절감 — Binarize(32× 압축), SSDC(희소성 활용), DPR(정밀도 축소)로 DNN 학습 메모리 병목 완화 ([paper-summaries/2018ISCA-summarize/gist-efficient-data-encoding-for-deep-neural-network-training.md])
- **cDMA**: activation sparsity 활용 압축 DMA 엔진으로 GPU-CPU 데이터 전송 병목 해결 — 평균 2.6×(최대 13.8×) 압축률, 평균 53%(최대 79%) 성능 향상 ([paper-summaries/2018HPCA-summarize/compressing-dma-engine-leveraging-activation-sparsity-for-training-deep-neural-networks.md])

### In-Cache DNN 가속
- **Neural Cache**: LLC 캐시 구조를 대규모 병렬 연산 유닛으로 재활용 — 비트 직렬 연산으로 SRAM 배열에서 제자리(in-situ) 합성곱, 완전 연결, 풀링, 양자화 연산 지원. CPU 대비 18.3×, GPU 대비 7.7× 지연 시간 향상, 전력 50% 절감, 면적 오버헤드 2% 미만 ([paper-summaries/2018ISCA-summarize/neural-cache-bit-serial-in-cache-acceleration-of-deep-neural-networks.md])

## Related Papers

- [maeri-enabling-flexible-dataflow-mapping-over-dnn-accelerators.md]
- [energy-efficient-neural-network-accelerator-based-on-outlier-aware-low-precision-computation.md]

## Cross-references

- [[paper-wiki/concepts/gpu|GPU]] - DNN 가속기와 GPU의 관계
- [[paper-wiki/concepts/dataflow|Dataflow]] - 데이터플로 매핑 개념