---
tags: [paper, 2021, 2021HPCA, topic/dram, topic/near-data-processing, topic/pim]
venue: "2021 IEEE International Symposium on High-Performance Computer Architecture (HPCA '21)"
year: 2021
summary_path: "../paper-summaries/2021HPCA-summarize/fafnir-accelerating-sparse-gathering-by-using-efficient-near-memory-intelligent-reduction.md"
---

# FAFNIR: Accelerating Sparse Gathering by Using Efficient Near-Memory Intelligent Reduction

**Venue:** 2021 IEEE International Symposium on High-Performance Computer Architecture (HPCA '21)
**저자:** Bahar Asgari (Georgia Institute of Technology), Ramyad Hadidi (Georgia Institute of Technology), Jiashen Cao (Georgia Institute of Technology), Da Eun Shim (Georgia Institute of Technology), Sung-Kyu Lim (Georgia Institute of Technology), Hyesoon Kim (Georgia Institute of Technology)

## 개요

- 추천 시스템(recommendation systems)은 Facebook, Netflix, YouTube 등 산업 전반에서 사용되며, Facebook의 프로덕션 데이터센터에서 AI 추론 사이클의 **65%** 를 소모
- 추천 시스템의 핵심 병목: **임베딩 조회(embedding lookup)** — 대용량 임베딩 테이블에서 불규칙한 랜덤 메모리 액세스를 통해 벡터를 수집(sparse gathering)하는 과정
- 임베딩 테이블은 수 GB 크기로 여러 메모리 디바이스(DIMM)에 분산 필수 → 랜덤 액세스로 인해 **메모리 대역폭 병목** 발생
- 기존 NDP(Near-Data Processing) 솔루션의 한계:
  - **TensorDIMM [9]**: 임베딩 벡터를 DIMM 간 분할하고 열 주요 순서(column-major)로 액세스 → 행 버퍼 로컬리티(row-buffer locality) 파괴, 병렬성 제한 (rank-level parallelism만 활용)
  - **RecNMP [8]**: 벡터를 rank에 분산하여 rank-level parallelism 활용 → **공간적 국소성(spatial locality)에 의존**, 임베딩 벡터가 동일 DIMM에 없으면 NDP에서 감소 연산 불가 → 핵심 데이터 이동 문제 미해결
- RecNMP는 NDP에서 캐싱 메커니즘(128KB)을 사용하지만, 최대 **50% 히트율** 로 비효율적이고 하드웨어 오버헤드 38%
- 둘 다 연결(connection) 오버헤드 문제 미해결: 메모리 디바이스와 컴퓨팅 디바이스 간 **c×m all-to-all 연결** 필요 → 확장성 한계

## 방법론

### 3.1. 트리 구조

- **32개 rank** → 31개 PE(Processing Element)로 구성된 이진 트리
- DIMM/rank 노드: 7개 PE, 8개 rank 연결 (1PE:2R 비율)
- 채널 노드: 3개 PE, 4개 채널 연결
- 데이터 흐름: 리프(leaf) → 루트(root) 방향으로 점진적 감소
- **헤더 구조**: indices(방문한 인덱스 목록) + queries(미방문 인덱스 목록)
  - 리프에서 시작 시 queries에 모든 인덱스 포함
  - 각 PE를 지나면서 indices로 이동, 루트에서 queries가 비어있으면 완료

### 3.2. PE (Processing Element) 마이크로아키텍처

- 두 개의 입력(A, B)과 한 개의 출력을 가진 처리 장치
- **입력 FIFO 버퍼**: 각 엔트리에 512B 값 + 10B 헤더 (16비트 인덱스/쿼리 필드)
- **비교 유닛**: B[x]의 queries 필드와 A[i의 indices 필드를 비교
  - B[x].queries[j]에 A[i].indices의 모든 요소 포함 시 → **감소(reduce)**: out.values = A[i].values + B[x].values
  - 불일치 시 → **포워딩(forward)**: B[x]를 그대로 전달
- **병합 유닛(merge unit)**: 동일한 출력을 병합하거나 중복 출력 제거
- 배치 크기 B에 따라 버퍼 크기 결정: min(nm+n+m, B)

### 3.3. 동시 배치 처리 및 중복 메모리 액세스 제거

- 호스트가 배치 내 **고유 인덱스(unique indices)** 만 추출하여 메모리에서 한 번만 읽음
- 고유 인덱스의 헤더에 queries 필드를 포함시켜, 감소 연산에 필요할 때마다 트리 내에서 반복 사용
- 예시: 4개 쿼리에서 14개 총 액세스 → **7개 고유 인덱스** 만 실제 메모리 액세스
- 캐싱 메커니즘 불필요 → RecNMP의 128KB 캐시(50% 히트율) 대비 효율적

### 3.4. SpMV 적응

- SpMV와 임베딩 조회의 차이: SpMV는 벡터 요소를 하나의 스칼라로 감소, 임베딩 조회는 벡터를 벡터로 감소
- **벡터화 기법**: 각 PE가 독립적인 요소 벡터를 처리하여 병렬 감소 수행
- LIL(List-of-List) 압축 포맷 사용으로 대규모 희소 행렬의 스트리밍 지원
- 대규모 행렬(500만+ 열): 2번 이하의 병합 단계만 필요

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

- **하드웨어 언어**: C++로 마이크로아키텍처 기술 → HLS(Vivado HLS)로 RTL(Verilog) 생성
- **FPGA 구현**: XCVU9P Xilinx FPGA (VCU1525 키트), 4개 16GB DDR4 DIMM
- **ASIC 설계**: ASAP 7nm PDK, Innovus 배치, Tempus 타이밍 분석
- **DIMM/rank 노드 면적**: 0.282mm² (7PE 포함)
- **채널 노드 면적**: 0.121mm²
- **PE 면적**: 0.077mm²
- **FPGA 리소스 사용량**: LUT 5%, LUTRAM 0.15%, FF 1%, BRAM 13%

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2021HPCA-summarize/fafnir-accelerating-sparse-gathering-by-using-efficient-near-memory-intelligent-reduction.md|전체 요약 보기]]
