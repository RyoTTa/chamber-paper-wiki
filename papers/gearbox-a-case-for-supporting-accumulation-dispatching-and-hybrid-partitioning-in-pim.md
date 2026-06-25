---
tags: [paper, 2022, 2022ISCA, topic/dram, topic/gpu, topic/pim]
venue: "ISCA 2022 (The 49th Annual International Symposium on Computer Architecture)"
year: 2022
summary_path: "../paper-summaries/2022ISCA-summarize/gearbox-a-case-for-supporting-accumulation-dispatching-and-hybrid-partitioning-in-pim.md"
---

# Gearbox: A Case for Supporting Accumulation Dispatching and Hybrid Partitioning in PIM-based Accelerators

**Venue:** ISCA 2022 (The 49th Annual International Symposium on Computer Architecture)
**저자:** Marzieh Lenjani, Alif Ahmed, Mircea Stan, Kevin Skadron (University of Virginia)

## 개요

- Processing-in-Memory (PIM)은 메모리 세그먼트 근처에 처리 유닛을 배치하여 데이터 이동 오버헤드를 최소화하지만, 기존 PIM 아키텍처는 SIMD 아키텍처를 사용하여 SpMV(Sparse-Matrix-Dense-Vector) 및 SpMSpV(Sparse-Matrix-Sparse-Vector)와 같은 랜덤 접근 기반 커널을 효율적으로 지원하지 못함
- SIMD 기반 ALU는 모든 피연산자가 로컬 또는 원격 메모리 세그먼트에서 수집될 때까지 유휴 상태로 대기해야 하므로, 랜덤 접근 패턴에서는 병렬성을 활용하기 어려움
- SpMV/SpMSpV에서 적절한 행렬/벡터 분할은 처리 부하 분배와 통신량에 직접 영향: 기존 PIM 가속기(SpaceA 등)는 row-oriented 처리만 지원하여 column-oriented 처리의 잠재력을 활용하지 못함
- 기존 PIM 가속기는 메모리 레이어 간 데이터 이동 오버헤드가 크며, 논문에서 제시한 GPU(NVIDIA P100, 3개 HBM2 스택) 대비 Gearbox는 단 1개 메모리 스택으로 평균 15.73×(최대 52×) speedup을 달성

## 방법론

### 3.1. Walkers와 Indirect Accesses (Section 4.1)

- 각 SPU(Service Processing Unit)에 3개의 Walker가 존재하며, 각각 하나의 큰 배열(A, B, C)에 대해 읽기/쓰기 수행
- **Indirect Access 지원:** 간접 접근이 필요한 경우(예: C[A[i]] += B[i]), 인덱스 필드를 통해 간접 접근의 소스 레지스터와 대상 Walker를 지정
- 컨트롤러는 인덱스를 사용하여 행 주소와 열 주소를 파생: one-hot-encoder 값을 shift하여 접근된 단어를 선택
- **서브클럭(sub-clock) 활용:** 새 행 로딩과 one-hot-encoder 값 shift를 겹쳐 처리하여 오버헤드 은폐

### 3.2. Dispatcher와 Bank-level Switch (Section 4.3)

- Dispatcher SPU는 링 인터커넥트에 가장 가까운 서브어레이에 위치
- **라우팅 역할:** 원격 누적 패킷의 라우팅, 자기 bank의 인덱스 범위를 latch에 유지
- 인덱스가 자기 bank에 속하면 Walker에 로드, 같은 메모리 레이어에 속하면 링 인터커넥트에 배치, 다른 레이어에 속하면 TSV를 통해 전달
-乘법과 로컬 누적을 원격 누적 전송과 동시에 오버랩 수행

### 3.3. Hybrid Partitioning (Section 5)

- **Step 1 (FrontierDistribution):** 입력 벡터의 희소 포맷(frontier)을 서브어레이 간에 분할 및 분배
- **Step 2 (OffsetPacking):** 열 오프셋, 열 길이, 프론티어 값을 새로운 배열로 패킹 (Figure 10의 의사 코드)
- **Step 3 (LocalAccumulations):** 프론티어의 각 값을 해당 열과 곱셈 수행, 깨끗한 값(clean value)이 갱신되면 Dispatcher에 전송
- **Step 4 (Dispatching):** Dispatcher가 저장된 모든 인덱스-값 쌍을 대상 서브어레이로 전송
- **Step 5 (RemoteAccumulations):** 수신된 인덱스-값 쌍을 순차적으로 처리하여 최종 누적 수행
- **Step 6 (Applying):** 다음 반복을 위한 프론티어 생성, 출력 벡터의 희소 포맷 생성

### 3.4. 명령어 형식 (Table 1)

- 총 3비트 NextPC, 4비트 OpCode, 3비트 Src1/Src2, 1비트 ReadWrite 등 다양한 필드 보유
- **IndirectAccSrc/Dst:** 간접 접근 지원을 위한 레지스터 지정
- **LongEntryTreat:** Hybrid Partitioning 지원을 위한 긴 활성화 인덱스 처리 방식 결정
- **CheckCleanVal/CleanIndexSrc/CleanPairDst:** 출력 벡터의 희소 포맷 생성 지원

## 핵심 기여

- Gearbox는 PIM 기반 가속기에서 SpMV/SpMSpV를 효율적으로 지원하기 위해 **Accumulation Dispatching**, **Hybrid Partitioning**, **Subarray-level Random Accesses**의 세 가지 핵심 기술을 제안
- 단일 메모리 스택으로 서버급 GPU(NVIDIA P100, 3 HBM2 스택) 대비 평균 15.73× speedup, 에너지는 97% 절감
- 일반 SIMD 커널에서도 기존 bank-level SIMD 대비 4.4× 향상으로 범용성 입증
- future work: 다른 irregular 커널 확장, SRAM/E-DRAM 설정 적용, 높은 오류율 메모리 기술에 대한 안정성 메커니즘 추가

## 주요 결과

- **구현 언어/기술:** RTL 모델을 14nm 기술로 설계, 22nm DRAM에서의 3.08× 페널티 적용하여 평가
- **시스템 구성 요소:**
  - Gearbox: 22nm, 32 vault, 32 서브어레이 (open-bitline 구조), 행당 256 bytes, 레이어당 64 bank
  - 8개 메모리 레이어, 행 주기: 50ns, 주파수: 164MHz
  - Logic layer 내 ARM Cortex-A35, 1.2GHz, 64 레인 링 인터커넥트
  - 각 vault에 4~32KB SRAM
- **소프트웨어 스택:** CUDA 유사 API(cudaMemcpy()) 기반 데이터 오프로딩, 라이브러리 기반 프로그래밍 모델
- **전처리:** 긴 열 분할 및 파티션별 열 오프셋 복제, 로드 밸런싱을 위한 열 순서 무작위화

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2022ISCA-summarize/gearbox-a-case-for-supporting-accumulation-dispatching-and-hybrid-partitioning-in-pim.md|전체 요약 보기]]
