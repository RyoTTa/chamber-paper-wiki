---
tags: [paper, 2019, 2019MICRO, topic/compression, topic/storage]
venue: "52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '19)"
year: 2019
summary_path: "../paper-summaries/2019MICRO-summarize/smash-co-designing-software-compression-and-hw-indexing.md"
---

# SMASH: Co-designing Software Compression and Hardware-Accelerated Indexing for Efficient Sparse Matrix Operations

**Venue:** 52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '19)
**저자:** Konstantinos Kanellopoulos, Nandita Vijaykumar, Christina Giannoula, Roknoddin Azizi, Skanda Koppula, Nika Mansouri Ghiasi, Taha Shahroodi, Juan Gomez Luna, Onur Mutlu (ETH Zürich, Carnegie Mellon University, National Technical University of Athens)

## 개요

- 희소 선형 대수 연산은 추천 시스템, 신경망, 그래프 분석, 고성능 컴퓨팅 등 다양한 응용에서 광범위하게 사용
- 희소 행렬의 핵심 문제: **극단적인 희소성**으로 인한 비효율
  - Facebook 소셜 네트워크 연결 행렬: 0.0003% 비영소수
  - YouTube 소셜 네트워크 연결 행렬: 2.31% 비영소수
  - 영소수 저장 및 연산에 불필요한 메모리와 연산 낭비

- **기존 압축 포맷의 한계 (CSR 등):**
  - CSR: row_ptr, col_ind, values 세 배열로 구성
  - 비영소수 위치 발견(indexing)에 **포인터 체이싱 연산** 필요
  - col_ind[row_ptr[i]]에서 col_ind[row_ptr[i+1]]까지 순회하며 열 인덱스 탐색
  - 현대 프로세서/메모리 계층에서 매우 비효율적

- **SpMV (Sparse Matrix Vector Multiplication) 인덱싱 오버헤드:**
  - y[i] += values[j] * x[col_ind[j]] 연산 시 col_ind 로드 후 x 벡터 인덱싱 필요
  - 이 복잡한 인덱싱操作 후에야 곱셈 수행 가능

- **SpMM (Sparse Matrix Matrix Multiplication) 인덱스 매칭 문제:**
  - 행 A의 각 행과 열 B의 각 열 간 내적 연산 시 인덱스 매칭 필요
  - col_ind 검색 + row_ind 검색으로 인덱스 일치 여부 확인
  - 모든 내적 연산에 대해 위치 찾기操作 필요

- **이상적 CSR과의 성능 격차 (Figure 3):**
  - 이상적 인덱싱: SpMV에서 **2.13× 스피드업**, SpMM에서 **2.81× 스피드업**
  - 실행 명령어 수: SpMV 42% 감소, SpMM 65% 감소
  - 인덱싱 오버헤드가 희소 행렬 연산의 핵심 병목

- **특수화된 압축 포맷의 한계:**
  - DIA, ELL, JAD 등 특정 행렬 구조에 특화된 포맷
  - 일반적인 응용(CNN, 그래프 처리)에는 적용 불가
  - 희소성 구조/정도가 사전에 알려져야 함

## 방법론

### 3.1. 소프트웨어 압축 (계층적 비트맵 압축)

- **계층적 비트맵 구조:**
  - 각 비트가 행렬 영역의 비영소수 존재/부재를 표현
  - 계층 레벨별 압축 비율 조정 가능
  - Figure 4 예시: 3레벨 비트맵 계층
    - Bitmap-2: 2개 연속 영역을 하나의 비트로 인코딩 (압축 비율 2:1)
    - Bitmap-1: 4개 연속 영역을 하나의 비트로 인코딩 (압축 비율 4:1)
    - Bitmap-0: NZA(Non-Zero Values Array)의 블록을 인코딩

- **압축 비율 트레이드오프:**
  - 높은 압축 비율: 비트맵 크기 감소 → 스캔 효율↑, 불필요한 연산↑
  - 낮은 압축 비율: 비영소수만 정확히 연산, 저장 오버헤드↑
  - Figure 5: 8:1 vs 4:1 압축 비율 비교
    - 8:1: 2비트로 전체 행렬 인코딩, 8요소 블록 저장
    - 4:1: 4비트로 전체 행렬 인코딩, 4요소 블록 저장

- **NZA (Non-Zero Values Array):**
  - 실제 희소 행렬 값을 저장하는 데이터 구조
  - Bitmap-0의 압축 비율에 따라 메모리에서의 세분화 결정

- **변환 과정 (CSR → SMASH):**
  1. 기존 포맷의 인덱싱 메커니즘으로 모든 비영소수 블록 식별
  2. 비영소수 블록을 메모리에 연속적으로 배치하여 NZA 생성
  3. Bitmap-0부터 시작하여 계층적 비트맵 생성
  - 자동화 가능, 하드웨어 가속도 가능

### 3.2. 하드웨어 인덱싱 (Bitmap Management Unit)

- **BMU 구조 (Figure 6):**
  - SRAM 버퍼: 비트맵을 한 블록씩 저장 (256바이트)
  - 하드웨어 로직: 버퍼를 스캔하여 비영소수 블록 탐지
  - 프로그래머블 레지스터: 행렬 차원, 압축 비율 등 설정
  - 출력 레지스터: 비영소수 블록의 행/열 인덱스 저장
  - 여러 행렬 동시 인덱싱 지원을 위한 그룹 구조

- **BMU 동작 과정:**
  1. 하드웨어 로직이 비트맵 버퍼를 스캔하여 세트 비트 탐지
  2. 행렬 차원과 압축 비율을 읽어 행/열 인덱스 계산
  3. 출력 레지스터 업데이트
  4. CPU가 RDIND 명령어로 반복적 인덱스 읽기 가능

- **계층적 비트맵 순회 알고리즘:**
  - 깊이 우선 탐색 방식
  - 각 레벨에서 세트 비트의 인덱스 저장
  - Bitmap-0에 도달하면 비영소수 블록 위치 확정
  - **인덱스 계산 공식:**
    ```
    Index = Σ(i=0 to levels-1) (Π(j=0 to i) comp(j)) * index_bit(i)
    ```
    - comp(j): Bitmap-j의 압축 비율
    - index_bit(i): Bitmap-i에서 발견된 세트 비트의 인덱스
  - 행 인덱스 = Index / matrix_columns
  - 열 인덱스 = Index % matrix_columns

### 3.3. SMASH ISA (소프트웨어/하드웨어 인터페이스)

- **5개 새 명령어 (Table 1):**
  1. **MATINFO (row, col, grp):** 행렬 차원을 BMU 레지스터에 로드
  2. **BMAPINFO (comp, lvl, grp):** 각 비트맵의 압축 비율 로드
  3. **RDBMAP [mem], buf, grp:** 메모리에서 비트맵을 BMU 버퍼로 로드
  4. **PBMAP grp:** BMU에게 비트맵 스캔 및 다음 비영소수 블록 인덱스 계산 지시
  5. **RDIND rd1, rd2, grp:** 현재 비영소수 블록의 행/열 인덱스를 CPU 레지스터로 로드

- **일반성:** SpMV, SpMM, 희소 행렬 덧셈, 희소 LU 분해, 희소 고유값 계산 등 다양한 희소 행렬 연산에 적용 가능

### 3.4. 소프트웨어 전용 SMASH

- BMU/ISA 없이 소프트웨어로만 실행 가능한 변형
- 비트맵 블록을 64바이트씩 4개 로드 명령어로 로드
- CLZ (Count Leading Zeros) 명령어로 최상위 세트 비트 탐지
- 세트 비트마다 AND 마스킹으로 다음 세트 비트 탐색
- 하드웨어 가속 대비 추가 연산 오버헤드 발생
-それでも CSR보다 우수한 성능 (전체 명령어 수 감소)

## 핵심 기여

- **핵심 기여:**
  1. 희소 행렬 연산에서 인덱싱이 핵심 병목임을 최초로 입증
  2. 하드웨어가 소프트웨어 압축 인코딩을 인식하고 활용하는 새로운 하드웨어-소프트웨어 공동 설계 제안
  3. 계층적 비트맵 인코딩으로 다양한 희소 행렬에 일반적 적용 가능
  4. 경량 하드웨어 유닛(BMU)으로 효율적 인덱싱 가속

- **성능 향상:**
  - SpMV: 38%, SpMM: 44% 평균 성능 향상
  - 그래프 응용: 20% 평균 성능 향상
  - 하드웨어 오버헤드: 0.076% (매우 미미)

- **의의:**
  - CSR 등 전통적 압축 포맷의 인덱싱 비용 문제를 근본적으로 해결
  - 소프트웨어-하드WARE 공동 설계 패러다임으로 희소 행렬 처리 효율성 크게 향상
  - 머신 러닝, 그래프 분석 등 다양한 응용에서 실용적 적용 가능

## 주요 결과

- **시뮬레이터:** zsim 시뮬레이터 사용
- **시스템 구성 (Table 2):**
  - CPU: 3.6GHz Westmere-유사 OOO, 4-wide issue
  - ROB: 128엔트리, LQ/SQ: 32엔트리
  - L1: 32KB, 8-way, 2사이클
  - L2: 256KB, 8-way, 8사이클
  - L3: 1MB, 16-way, 20사이클
  - DRAM: 1채널, 16뱅크, 4GB DDR4
- **실제 하드웨어 검증:** Intel Xeon Gold 5118 (2.30GHz, 14nm)
- **소프트웨어 구현:** TACO 라이브러리 기반 CSR 베이스라인

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2019MICRO-summarize/smash-co-designing-software-compression-and-hw-indexing.md|전체 요약 보기]]
