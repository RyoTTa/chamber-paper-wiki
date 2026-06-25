---
tags: [paper, 2022, 2022MICRO, topic/dram, topic/pim]
venue: "55th IEEE/ACM International Symposium on Microarchitecture (MICRO 2022)"
year: 2022
summary_path: "../paper-summaries/2022MICRO-summarize/genpip-in-memory-acceleration-of-genome-analysis-via-tight-integration-of-basecalling-and-read-mapping.md"
---

# GenPIP: In-Memory Acceleration of Genome Analysis via Tight Integration of Basecalling and Read Mapping

**Venue:** 55th IEEE/ACM International Symposium on Microarchitecture (MICRO 2022)
**저자:** Haiyu Mao (ETH Zürich), Mohammed Alser (ETH Zürich), Mohammad Sadrosadati (ETH Zürich), Can Firtina (ETH Zürich), Akanksha Baranwal (ETH Zürich), Damla Senol Cali (Bionano Genomics), Aditya Manglik (ETH Zürich), Nour Almadhoun Alserr (ETH Zürich), Onur Mutlu (ETH Zürich)

## 개요

- Nanopore 시퀀싱 기술은 장방향 리드(long reads)를 저비용으로 생성할 수 있으나, 두 단계의 비용이 높은 처리 과정이 필요: (1) **베이스콜링(basecalling)** - 원시 전기 신호를 핵산 염기(A, C, G, T)로 변환, (2) **리드 매핑(read mapping)** - 리드의 정확한 위치를 참조 유전체에서 탐색
- 기존 파이프라인에서 베이스콜링과 리드 매핑은 **별도 기기에서 분리 실행**됨: 베이스콜링은 습식 실험실(wet lab), 리드 매핑은 건식 실험실(dry lab)에서 처리
- 분리 실행으로 인해 세 가지 핵심 문제 발생:
  - **데이터 이동 병목:** 베이스콜링 결과(546GB)를 매핑 기기로 전송해야 하며, 원시 신호 데이터(3913GB)와 함께 대용량 중간 데이터 저장 필요
  - **중복 연산:** 저품질 리드(10-20%)와 매핑 불가 리드(30-70%)에 대해 이미 베이스콜링이 완료된 후 필터링되어 불필요한 연산 발생
  - **성능/에너지 손실:** E. coli 데이터셋 기준 전체 리드의 30.5%가 불필요하며, 베이스콜링에만 ~3100 CPU 시간 소요
- 기존 PIM 가속기는 베이스콜링(Helix) 또는 리드 매핑(PARC)을 **개별적으로** 가속하며, 파이프라인 전체를 통합한 가속기는 없음
- 시스템 A(기존实践) 대비 시스템 C(데이터 이동 제거 이상적 시스템)는 **2.23x** 성능 향상, 시스템 D(데이터 이동 + 불필요 리드 제거)는 **3.28x** 성능 향상 달성 가능

## 방법론

### 3.1. 청크 기반 파이프라인 (CP)

- 기존 파이프라인: 베이스콜링은 청크 단위, 리드 품질 관리/매핑은 리드 전체 단위로 처리 → 파이프라인 병목
- **CP 접근법:** 모든 단계를 청크 단위로 세분화하여 중첩 실행
  - 청크 1개가 베이스콜링되면 해당 청크의 품질 점수(SQS)를 즉시 계산
  - 다음 청크 베이스콜링 중 이전 청크의 시딩/체이닝 동시 실행
  - 수식: `AQS_read = (SQS_first + Σq_ci) / 2c` (Equation 3)로 청크별 품질 점수 누적 합산
- **이점:** 중간 데이터 저장 필요성 감소 + 단계 간 중첩 실행을 통한 시간 절약

### 3.2. 조기 거부 기법 (ER)

#### 3.2.1. 품질 점수 기반 거부 (QSR)
- 소수의 비연속 샘플 청크(N_qs개)의 평균 품질 점수로 전체 리드 품질 예측
- 핵심 관찰: 고품질 리드의 청크 품질 범위(11-18)가 저품질 리드(4-10)와 명확히 구분됨
- 단일 청크로는 예측 불가(저품질 리드에도 품질 점수 >7인 청크 존재) → 2-5개 비연속 청크 샘플링 필요
- **알고리즘 (Algorithm 1):** N_qs개 청크를 균등 간격으로 샘플링 → 평균 점수 계산 → θ_qs와 비교하여 거부 결정
- E. coli: 2개 청크 샘플링, 인간: 5개 청크 샘플링으로 최적화

#### 3.2.2. 매핑 기반 거부 (CMR)
- N_cm개 연속 청크를 결합하여 더 큰 청크(예: 1500염기) 구성
- 큰 청크의 체이닝 점수가 θ_cm 미만이면 해당 리드를 매핑 불가로 예측
- E. coli: 5개 청크 결합, 인간: 3개 청크 결합으로 최적화
- 거부 비율: E. coli 6.3%, 인간 5.5% (거짓 음성 비율 거의 0)

### 3.3. 메모리 내 시딩 가속기

- **구성 요소:** eDRAM 버퍼, 쿼리 문자열 생성기(QSG), ReRAM 기반 CAM 배열, ReRAM 기반 RAM 배열
- **동작 흐름:**
  1. 베이스콜링된 청크를 eDRAM 버퍼에 저장
  2. QSG가 청크에서 부분 문자열을 추출하여 쿼리 문자열 생성 (1염기씩 시프팅)
  3. ReRAM CAM에서 키(참조 문자열)와 병렬 비교 → 매칭 시 주소 출력
  4. 주소로 ReRAM RAM에서 값(참조 유전체 내 위치) 조회
  5. 가능한 매칭 위치 목록을 리드 매핑 컨트롤러에 전달
- **규모:** 4096개 시딩 유닛, 유닛당 832x128 CAM, 8개 16KB RAM, 1개 4KB eDRAM

### 3.4. GenPIP 컨트롤러

- Read Queue: 원시 전기 신호 저장 (eDRAM, 최대 6MB)
- Chunk Buffer: 베이스콜링된 청크 저장 (eDRAM, 2.3M 염기 수용)
- AQS Calculator: 청크 품질 점수 누적 합산 및 평균 계산
- ER-QSR Controller: 평균 품질 점수와 θ_qs 비교 → 거부 신호 발생
- ER-CMR Controller: 체이닝 점수와 θ_cm 비교 → 거부 신호 발생

## 핵심 기여

- GenPIP는 **최초의 메모리 내 게놈 분석 파이프라인 가속기**로, 베이스콜링과 리드 매핑을 밀접하게 통합
- CP와 ER의 두 가지 핵심 기법으로 **데이터 이동 제거 + 불필요 연산 제거**를 동시에 달성
- CPU 대비 41.6x, GPU 대비 8.4x 성능 향상, 32.8x/20.8x 에너지 절감으로 기존 대비 압도적 성능
- 시퀀싱 기기 내부에 구현되어 전체 파이프라인의 end-to-end 가속을 목표로 함
- 게놈 분석 파이프라인의 holistic한 재설계와 가속에 대한 기여

## 주요 결과

- **하드웨어 구현:** Verilog HDL로 로직 컴포넌트 구현, Synopsys Design Compiler로 32nm 공정 합성
- **메모리 모델링:** NVSim/NVM-CAM(ReRAM), CACTI 6.5(eDRAM)
- **기존 가속기 활용:** PIM Basecaller는 Helix[63] 아키텍처 기반, 체이닝/얼라인먼트는 PARC[88] 기반
- **总面积:** 163.8 mm² (32nm 기준), **총 전력:** 147.2W
  - Basecalling Module: 49.2 mm², 27.4W
  - Read Mapping Module: 93.1 mm², 114.5W (DP 유닛 1024개)
  - GenPIP Controller: 21.5 mm², 5.3W
- **시뮬레이터:** 인하우스 시뮬레이터로 성능/에너지/면적 평가

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2022MICRO-summarize/genpip-in-memory-acceleration-of-genome-analysis-via-tight-integration-of-basecalling-and-read-mapping.md|전체 요약 보기]]
