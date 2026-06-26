---
tags: [paper, 2022, 2022HPCA, topic/gpu, topic/pim]
venue: "IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2022"
year: 2022
summary_path: "../paper-summaries/2022HPCA-summarize/accelerating-gcns-using-crossbar-based-processing-in-memory-architectures.md"
---

# REFLIP: Accelerating Graph Convolutional Networks Using Crossbar-based Processing-In-Memory Architectures

**Venue:** IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2022
**저자:** Yu Huang, Long Zheng, Pengcheng Yao, Qinggang Wang, Xiaofei Liao, Hai Jin (Huazhong University of Science and Technology), Jingling Xue (UNSW Sydney)

## 개요

- **GCN 가속의 핵심 도전**: Graph Convolutional Networks(GCNs)는 그래프 기반 머신 러닝에서 promising하지만, 두 가지 상이한 연산 커널을 포함: **combination**(신경망 연산, 규칙적 메모리 접근)과 **aggregation**(그래프 분석, 비규칙적 메모리 접근)
- 기존 GCN 가속기는 **divide-and-conquer** 철학을 채택하여 두 커널을 각각 가속하기 위한 별도 하드웨어를 구축 → **커널 간 상호작용 고려 부족**
- 기존 하이브리드 아키텍처의 한계:
  - combination과 aggregation 간 **동적 워크로드 변동** 대응 미흡 → 하드웨어 리소스 활용도 저하
  - 고정된 스케줄링 순서로 인해 **레이어 간 미세한 소프트웨어 최적화** 기회 상실
- **기존 성능 수치**: 소프트웨어 프레임워크(PyG) 기반 CPU/GPU 대비 수천 배 느린 GCN 추론 속도 → 실시간 대규모 그래프 처리 불가

## 방법론

### 3.1. 통합 아키텍처

- **PE(Processing Element)**: 64개 PE → 각 PE에 8개 CU, 온칩 버퍼(input/crossbar/output), NFU, PFU 포함
- **CU(Computing Unit)**: 64×64 crossbar array × 32개, ADC/DAC, Voltage/Current Buffer, Current Reductor 내장
- **SIMT 실행 모델**: 레이어 간 병렬화 → 레이어당 필요 데이터만 crossbar에 저장하여 면적 효율성 향상
- **Controller**: 오프칩 메모리와 REFLIP 칩 간 데이터 이동 조정, 샘플링 메커니즘 지원
- **칩 구성**: 총 **64 PE**, **47.38K mW** 전력, **43.65 mm²** 면적

### 3.2. Combination: Layer-Wise Weight Mapping

- 가중치 파라미터를 crossbar에 매핑, vertex feature를 입력으로 사용
- **레이어별 반복 로딩**: 모든 레이어의 가중치를 crossbar에 상주시키는 대신 현재 레이어만 로딩 → aggregation에 crossbar 리소스 할당 가능
- **Inter-vertex 병렬성 활용**: 가중치 복제본을 여러 PE에 복제하고, vertex를 균등 분배하여 레이어 내 병렬 combination 처리
- 가중치의 높은 재사용 가능성으로 로딩 오버헤드 상쇄 가능

### 3.3. Aggregation: Flipped Mapping

- **기존 그래프 매핑의 한계**: 희소한 edge 데이터를 crossbar에 매핑하면 zero 값에 대한 비효율적 연산 발생
- **Flipped 매핑**: multi-dimensional vertex feature를 crossbar에 매핑하고, edge 데이터를 입력으로 제공
- GCN의 vertex feature 차원(100~1000)이 일반 그래프 알고리즘 대비 100~1000배 큼 → intra-vertex 병렬성 극대화 가능
- Crossbar sparsity 문제 완전 해결

### 3.4. 하이브리드 실행 모델

- **Row-Major 모델**: source vertex를 한 번만 로딩하지만 invalid edge로 인한 비효율적 crossbar 연산
- **Column-Major 모델**: invalid edge 제거 가능하지만 vertex feature 반복 로딩 → 데이터 로딩 오버헤드 증가
- **하이브리드 모델**: power-law 분포 활용 → high-degree vertex는 row-major, low-degree vertex는 column-major 적용
- **임계값 θ=10%**: high/low degree vertex 분류 기준 → crossbar 효율성과 로딩 오버헤드 간 최적점 달성

### 3.5. 로컬리티 인식 하드웨어

- **Voltage Buffer**: 수평 crossbar 간 DAC 변환 공유 → 디지털-아날로그 변환 **74.98%** 감소
- **Current Buffer**: 수직 crossbar 출력 전류를 아날로그 방식으로 리듀싱 → ADC 변환 **57.31%** 감소
- **Dynamic Reductor Controller**: 다른 목적 vertex를 업데이트하는 수직 crossbar 간 정확한 결과 분리
- 총 에너지 소비 **41.57%** 절감

## 핵심 기여

- **핵심 기여**: GCN의 combination과 aggregation을 PIM 기반 crossbar 아키텍처로 통합 가속하는 최초의 접근법
- **성능 혁신**: CPU 대비 **6,432×**, GPU 대비 **86×**, 기존 GCN 가속기 대비 **5×** speedup
- **에너지 효율**: CPU 대비 **9,817×** 에너지 절감 → 모바일/엣지 디바이스에서의 GCN 가능성 제시
- **설계 원칙**: "하나의 통합 아키텍처로 두 커널 모두 처리" → 하드웨어 리소스 활용도 극대화
- **Flipped mapping의 핵심**: GCN 특유의 multi-dimensional vertex feature를 활용하여 희소 그래프 데이터의 crossbar sparsity 문제 완전 해결
- **실용성**: 소프트웨어 최적화 없이 하드웨어만으로도 기존 가속기 대비 58.86× 성능 향상 가능

## 주요 결과

- **시뮬레이터**: execution-driven cycle-accurate 시뮬레이터 + CACTI(메모리 모델링)
- **하드웨어 구현**: SystemVerilog로 reductor controller RTL 합성, Cadence 시뮬레이션으로 Voltage/Current Buffer 검증
- **Crossbar**: ReRAM 기반 2-bit MLC, 읽기 지연 29.31ns, 쓰기 지연 50.88ns
- **정밀도**: 32-bit 고정소수점 표현 (GCN 추론 정확도 충분)
- **데이터 포맷팅 오버헤드**: 평균 **9.12%** (전체 추론 대비)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2022HPCA-summarize/accelerating-gcns-using-crossbar-based-processing-in-memory-architectures.md|전체 요약 보기]]
