---
tags: [paper, 2024, 2024HPCA, topic/dram, topic/gpu, topic/nvm, topic/storage]
venue: "IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2024"
year: 2024
summary_path: "../paper-summaries/2024HPCA-summarize/beacongnn-large-scale-gnn-acceleration-with-in-storage-computing.md"
---

# BeaconGNN: Large-Scale GNN Acceleration with Out-of-Order Streaming In-Storage Computing

**Venue:** IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2024
**저자:** Yuyue Wang, Xiurui Pan, Yuda An, Jie Zhang, Glenn Reinman (UCLA, Peking University)

## 개요

- GNN(Graph Neural Network)은 소셜 네트워크, 추천 시스템, 팬데믹 예측 등 다양한 도메인에서 광범위하게 활용되고 있으며, 대규모 그래프 구조 데이터에서 복잡한 관계와 의존성을 포착하는 데 탁월한 성능을 보임
- 실제 산업 시나리오에서 그래프와 피처 테이블의 크기는 수백 GB에서 TB 단위로 확장되며, 단일 머신의 메모리 용량을 크게 초과함
- GNN 데이터 준비 단계에서 스토리지와 프로세서(CPU/GPU) 간의 집중적인 데이터 전송이 발생하며, 얇은 PCIe 버스가 I/O 대역폭을 병목으로 만들고 SSD의 I/O 접근 지연이 메모리 대비 현저히 높음
- 기존 In-Storage Computing(ISC) 솔루션(GList, SmartSage)은 세 가지 근본적인 한계를 보유:
  1. **홉바이홉 순차 샘플링**: SmartSage는 호스트와 스토리지 간 인터-hop 통신이 필요하여 SSD 내부 병렬성을 활용하지 못함
  2. **페이지 단위 채널 전송**: GNN의 작고 무작위적인 I/O 패턴이 4KB 플래시 페이지 단위 전송과 불일치하여 읽기 증폭(read amplification) 발생
  3. **펌웨어 기반 처리**: SSD 내장 프로세서의 처리 능력 제한으로 ULL(Ultra-Low Latency) 플래시의 높은 처리량을 따라잡지 못함
- 일반 SSD에서 ULL 플래시로 전환 시, 활성 플래시 다이 수를 1→8로 증가시켜도 처리량은 49%만 향상되고 평균 지연은 7.7배 증가하는 비효율 발생 (Figure 7)

## 방법론

### 3.1. DirectGraph 구조

- 전체 GNN 그래프를 두 가지 유형의 페이지로 구성: **프라이머리 페이지(P-section)**와 **세컨더리 페이지(S-section)**
- 각 페이지는 가변 길이 섹션을 하나 이상 포함하며, 플래시 물리 페이지에 정렬됨
- 프라이머리 섹션: 노드의 피처 벡터와 이웃 리스트를 저장
- 세컨더리 섹션: 고차원 노드의 추가 이웃을 저장
- 저차원 노드의 프라이머리 섹션은 단일 페이지를 차지하지 않으므로, 연결된 배열(linked array)로 구성되어 하나의 프라이머리 페이지에 압축 저장

### 3.2. 주소 매핑

- 각 이웃 인덱스는 4바이트 물리 주소로 매핑: 28비트 플래시 페이지 인덱싱 + 4비트 페이지 내 섹션 인덱싱 (1TB SSD, 4KB 페이지 기준)
- 호스트는 미니배치 시작 시 대상 노드의 프라이머리 섹션 주소만 제공
- 이후 모든 데이터 주소 지정은 주소 변환 없이 SSD 내부에서 수행
- 이웃 리스트 읽기: 프라이머리 섹션 페이지 → 세컨더리 섹션 페이지 순서로 읽기 후 샘플링 수행

### 3.3. 순차 샘플링 지원

- DirectGraph를 통해 호스트-SSD 간 인터-hop 통신 장벽 제거
- 여러 홉의 이웃 샘플링을 순서에 관계없이 병렬로 실행 가능
- SSD 컨트롤러가 플래시에서 GNN 데이터를 직접 위치할 수 있어 호스트 측 파일 시스템과 NVMe 스택이 불필요

## 핵심 기여

- **핵심 기여**: 대규모 GNN 가속을 위한 풀스테이지 ISC 시스템 최초 제안 — 기존 부분적 오프로딩(GList, SmartSage)의 한계를 극복
- **DirectGraph**: 플래시 물리 주소 기반 그래프 형식으로 주소 변환 오버헤드 제거 및 순서 무관 샘플링 가능
- **멀티 레벨 네어-데이터 프로세싱**: 다이, 채널, 컨트롤러 레벨에 걸친 하드웨어 가속으로 I/O 병목 제거
- **성능**: CPU 중심 시스템 대비 27.3배, 기존 ISC 대비 11.6배 처리량 향상 달성
- **의의**: ULL 플래시와 ISC의 잠재력을 실현하여 대규모 GNN 학습/추론의 스토리지 병목을 근본적으로 해결하는 아키텍처 제안

## 주요 결과

### 4.1. 다이 레벨 샘플러 (Die-Level Sampler)

- 2-plane 플래시 다이의 제어 회로에 처리 로직 구현
- 구성 요소: GNN 설정 레지스터, 샘플러, TRNG(True Random Number Generator)
- 기능: 이웃 샘플링, 피처 벡터 검색, 미사용 데이터 필터링
- 샘플링 결과를 기반으로 후속 샘플링을 위한 새로운 플래시 명령 생성
- 채널 전송량을 대폭 줄이면서 유효한 데이터만 반환

### 4.2. 채널 레벨 커맨드 라우터 (Channel-Level Command Router)

- 플래시 인터페이스 컨트롤러에 인터채널 라우터 추가
- 채널 데이터 스트림에서 샘플링 명령어를 추출하여 대상 다이로 포워딩
- SSD 임베디드 프로세서의 개입 없이 하드웨어 기반 I/O 처리 실현
- ULL 플래시의 높은 처리량을 완전히 활용 가능

### 4.3. SSD 컨트롤러 레벨 공간 가속기 (Spatial Accelerator)

- SSD 내부 버스에 연결된 공간 가속기
- 벡터화된 임베딩 집계(embedding aggregation)와 GEMM 기반 임베딩 업데이트 수행
- 서브그래프와 샘플된 피처 벡터는 SSD DRAM에 저장
- GNN 모델 파라미터와 함께高效的 연산 수행

### 4.4. GNN 엔진

- 플래시 펌웨어에서 실행되는 GNN 엔진
- 데이터 준비 및 GNN 계산 단계를 스케줄링
- DirectGraph를 그래프 형식으로 활용하여 다중 레벨 주소 변환 간소화
- 멀티홉 샘플링의 순차적 장벽을 제거하고 순서 무관(out-of-order) 샘플링 지원

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2024HPCA-summarize/beacongnn-large-scale-gnn-acceleration-with-in-storage-computing.md|전체 요약 보기]]
