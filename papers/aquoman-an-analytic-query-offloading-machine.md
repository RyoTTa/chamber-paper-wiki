---
tags: [paper, 2020, 2020MICRO, topic/dram, topic/llm-inference, topic/storage]
venue: "53rd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '20)"
year: 2020
summary_path: "../paper-summaries/2020MICRO-summarize/aquoman-an-analytic-query-offloading-machine.md"
---

# AQUOMAN: An Analytic-Query Offloading Machine

**Venue:** 53rd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '20)
**저자:** Shuotao Xu, Thomas Bourgeat, Tianhao Huang, Hojun Kim, Sungjin Lee, Arvind (MIT CSAIL, DGIST)

## 개요

- 클라우드 환경에서 테라바이트 단위 분석 워크로드는 애플리케이션 서버와 스토리지 서버가 네트워크를 통해 분리된 구조에서 실행됨
- 스토리지 대역폭을 포화시키고 레이턴시를 숨기기 위해 충분한 하드웨어 스레드와 DRAM이 요구됨 — 비용 효율적이지 않은 대규모 서버 클러스터 필요
- 2020년 기준 Amazon EC2 i3.metal 서버는 8개 1.9TB SSD, 72 vCPU, 512GB DRAM을 탑재해야 SSD 대역폭을 활용 가능
- 플래시 기술 발전으로 스토리지 대역폭이 10년간 13배 향상되어 CPU의 인메모리 처리 능력을 크게 초과함 (Figure 1)
- 기존 In-Storage Processing (ISP) 접근법은 필터링, Aggregate Group-By 등 단순 연산만 오프로드 가능하며, TPC-H 벤치마크의 핵심 연산인 multi-way join을 처리하지 못함 (Table I)
- 클라우드 데이터 웨어하우징에서 약 70%의 CPU 사이클과 60%의 DRAM 사용량이 불필요하게 소모됨

## 방법론

### 3.1. 전체 구조 (Figure 2)

- AQUOMAN은 플래시 드라이브 내부에 위치하며 NAND 플래시 어레이에 직접 접근
- 3개의 핵심 가속기로 구성:
  1. **Row Selector:** 비트벡터 마스크를 사용하여 입력 테이블 데이터를 효율적으로 선택
  2. **Row Transformer:** PE 배열로 구성된 심스틱 아키텍처에서 각 행에 무상태 함수를 적용하여 중간 테이블 생성
  3. **SQL Swissknife:** 표준 SQL 연산(accumulate, sort, merge, aggregate, topK 등)을 수행하는 가속기 배열
- 40GB DDR4 DRAM 탑재 (1TB SSD당 16GB 목표)
- 3개 가속기가 파이프라인 방식으로 동시에 동작

### 3.2. Row Selector (Figure 6)

- 벡터 단위로 단일 열 술어(prredicate)를 평가하는 벡터 유닛
- `Pr = F(CP₀, ..., CPₙ₋₁)` 형태의 술어 지원 (CPᵢ: 열 비교/상수 equality)
- 4~6개의 Column Predicate Evaluator로 TPC-H의 대부분의 필터 술어 처리 가능
- 멀티열 술어나 정규식 필터링은 Row Transformer로 전달

### 3.3. Row Transformer (Figure 7, 8)

- **Table Reader:** Row-Vector ID를 받으면 플래시 읽기 시작, 비트벡터 마스크가 0인 플래시 페이지는 건너뜀
- **Row Transformation Systolic Array:** 데이터플로우 그래프를 PE 배열에 매핑
  - 각 PE는 4단계 정수 아리스메틱 벡터 프로세서 (브랜치 명령어 없음)
  - 7개 범용 레지스터(rf[1]~rf[7]) + operand FIFO + 특수 FIFO(rf[0])
  - 간단한 32비트 명령 세트: Pass, Copy, Store, ALU(Add/Sub/Mul/Div/EQ/LT/GT)
- **정규식 가속기:** 가변 크기 문자열 열을 미리 처리 (1MB 캐시로 country name 같은 작은 도메인 처리)
- 데이터플로우 그래프의 노드가 동일 수평 슬라이스의 PE에 매핑될 수 있음 (노드 간 남쪽/동쪽 데이터 전송만 허용, 순환 없음)

### 3.4. SQL Swissknife (Figure 11)

- **Aggregate GroupBy (Figure 12):**
  - Column Zipper로 동일 Row-Vector ID의 여러 Row Vector를 결합
  - Group Number Assign: 1024 버킷 해시 테이블로 그룹 식별자에 그룹 번호 할당
  - 최대 16B 그룹 식별자, 해시 충돌 시 spillover → x86 호스트 처리
  - Reduce By Group Number: 그룹별로 sum, min, max, cnt 연산 수행
  - SRAM 32 파티션 분할로 bank 기반 대역폭 향상

- **TopK (Figure 13):**
  - Vector Compare-And-Swap (VCAS) 체인으로 최대 k개 요소 유지
  - Algorithm 1: 정렬된 입력 벡터와 Top-n 벡터를 요소별 비교-스왑
  - K/n개 VCAS를 데이지 체인으로 연결
  - 파이프라인 가능한 비트onic 벡터 정렬기로 사전 정렬

- **Merger (Figure 14):**
  - 2-to-1 Merger로 두 정렬된 리스트를 병합 → Intersection Engine에서 교차하지 않는 부분 제거
  - 중복 값 처리: 두 입력 소스를 번갈아 가며 처리하여 look-ahead 1로 결정

- **1GB-Block Streaming Sorter (Figure 15):**
  - Pipelined Bitonic Sorter로 64B 입력 벡터 정렬
  - 3계층 256-to-1 Merger로 2²⁴ × 64B → 1GB 정렬 블록 생성
  - 첫 번째/두 번째 계층: SRAM에 중간 결과 저장 (16KB, 4MB 블록)
  - 세 번째 계층: 1GB 블록 병합에 DRAM 사용
  - 충분한 DRAM 시 256GB까지 정렬 가능 (스트리밍 속도의 절반으로 fold)
  - 입력 길이에 따라 최대 12.0 GB/s 처리량 달성 (Table V)

## 핵심 기여

- **핵심 기여:** 테라바이트 데이터셋에 대한 엔드투엔드 인스토리지 분석 SQL 쿼리 가속 시스템 AQUOMAN 제시
- **Table Task 프로그래밍 모델:** 정적 데이터플로우 그래프 기반 스트리밍 아키텍처로 중간 테이블 DRAM 수요 대폭 절감
- **실용적 성과:** 1TB TPC-H에서 4코어/16GB 호스트 + AQUOMAN SSD가 32코어/128GB 호스트와 동일 성능
- **CPU 70% 절약, DRAM 60% 절약:** 클라우드 환경에서 상당한 비용 절감 가능
- **기존 대비 우수성:** Q100 등 기존 ISP 아키텍처의 10X-100X 성능 저하 문제 해결, 1TB 데이터셋에서의 첫 번째 검증
- **FCAccel 대비 2.5X 처리량 향상:** 심스틱 기반 행 변환의 파이프라인 효율성 입증
- **향후 과제:** (1) 병렬 쿼리 실행 평가, (2) 다중 AQUOMAN SSD에 걸친 분산 쿼리 실행

## 주요 결과

- **FPGA 프로토타입:** BlueDBM에서 Xilinx VCU108 FPGA 보드 사용
  - Row Selector: 42,023 LUTs, 36,725 FFs
  - Row Transformer: 47,859 LUTs, 29,660 FFs, 256 DSP48
  - SQL Swissknife (sorter 제외): 95,077 LUTs, 76,823 FFs, 140 RAMB36
  - 총 302,398 LUTs (56%), 273,245 FFs (24%), 448 RAMB36 (26%), 256 DSP48 (33%) 사용 (Table III)
  - 125MHz 타이밍 요구사항 충족, 4GB/s 처리 속도

- **1GB-Block 하드웨어 Sorter:** VCU118에서 200MHz, 512비트 데이터 패스로 합성
  - uint32: 855,867 LUTs (72%), kv<uint64,uint64>: 900,087 LUTs (76%) (Table IV)
  - AQUOMAN + Sorter 합산 시 VCU118 용량 초과 2% → 최적화 필요

- **AQUOMAN 시뮬레이터:** MonetDB 11.27.9에 통합된 트레이스 기반 시뮬레이터
  - MAL (Monet Assembly Language) 확장으로 AQUOMAN Table Task 트레이싱 자동 삽입
  - 8KB 페이지 접근 granularity, 2.4GB/s 플래시 읽기 대역폭 가정

- **시스템 스택 (Figure 3):** AQUOMAN Compiler → AQUOMAN Executor → Flash Controller → NAND Flash

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2020MICRO-summarize/aquoman-an-analytic-query-offloading-machine.md|전체 요약 보기]]
