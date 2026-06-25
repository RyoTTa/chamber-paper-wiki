---
tags: [paper, 2019, 2019MICRO, topic/dram, topic/gpu, topic/near-data-processing]
venue: "52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '19)"
year: 2019
summary_path: "../paper-summaries/2019MICRO-summarize/medal_scalable_dimm_based_ndp_accelerator_for_dna_seeding_algorithm.md"
---

# MEDAL: Scalable DIMM-based Near Data Processing Accelerator for DNA Seeding Algorithm

**Venue:** 52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '19)
**저자:** Wenqin Huangfu, Xueqi Li, Shuangchen Li, Xing Hu, Peng Gu, Yuan Xie (University of California Santa Barbara, DAMO Academy/Alibaba Group, Institute of Computing Technology/Chinese Academy of Sciences)

## 개요

- 차세대 시퀀싱(NGS) 기술의 확산으로 계산 유전체학이 정밀 의료를 지원하는 핵심 분야로 부상
  - 생물학 데이터가 **지수적으로 성장**: WGS 프로젝트의 바이오 데이터가 **Moore's Law를 능가하는 속도로 증가**, 현재 3.44조 바이스 이상 보유
  - 시퀀싱 비용 감소 속도도 Moore's Law보다 빠름 → 더 많은 종의 대규모 데이터베이스가 현실적
- **DNA 정렬(Alignment)**은 유전체학 분석의 핵심 단계 중 하나로, 두 가지 주요 단계로 구성:
  - **DNA Seeding:** 쇼트 리드를 레퍼런스 게놈에 매핑하여 시드 생성 (가장 시간 소요)
  - **Seed Extension:** 시드를 더 긴 매칭으로 확장
  - BWA-MEM에서 DNA Seeding이 전체 실행 시간의 **29.35%**, 메타제노믹스 시나리오에서는 **48%** 차지
- DNA Seeding은 **메모리 바운드** 작업: 기존 하드웨어 가속 approaches(GPU, FPGA)는 계산에만 초점 → 제한된 개선 공간
  - 프로파일링 결과: DRAM 접근이 CPI 스택의 **60%**, 에너지 소비의 **49.4%** 차지
  - Load/Store 명령이 전체 명령의 **43.4%**
- **기존 NDP 가속기의 한계:**
  - **Chameleon:** 범용 SIMD NDP 가속기 → 세부 랜덤 메모리 접근 패턴에 비효율, 대역폭 활용률 **~10%**
  - **AIM:** FPGA + 전용 버스 → 랭크 수준 병렬성 미활용, 코어스 그레인 접근 (64B)
  - 공통 과제: 세부 랜덤 메모리 접근 문제와 대규모 데이터 확장성

## 방법론

### 3.1. 전체 구조

- **LRDIMM 기반 구조:** 상용 LRDIMM의 PCB 설계 수정으로 구현
  - **DB-Side Accelerator:** 각 DB(Data Buffer)에 4개의 DNA Seeding 전용 하드웨어 가속기 탑재
    - 쿼리 시퀀스 저장 레지스터, CR[4] 저장 레지스터 파일, OR 계산 엔진, 주소 변환 엔진
  - **DB-Side Multiplexer:** DB 출력에 멀티플렉서 추가 → DDR 버스 또는 칩 간 계층 버스로 데이터 전송 가능
  - **RCD-Side Memory Controller (MC):** 호스트와 가속기의 메모리 요청을 병합/스케줄링
    - 호스트 우선 스케줄링 적용 (호스트 사이드 MC가 가속기 요청을 인식하지 못하므로)
  - **Inter-Chip Hierarchical Bus:** 칩 간 통신을 위한 ID/주소 버스 + 데이터 버스
    - 단일 채널 버스, 추가 배선: (4·n+75)와이어 (n = DIMM당 DB 수)
  - **RCD-Side Bus Arbitrator:** 버스 마스터 할당, 데이터 전송 타이밍 관리

### 3.2. Intra-Rank 워크플로우 및 최적화

- **알고리즘 특화 주소 매핑 (Algorithm-Specific Address Mapping):**
  - **Optimization-1:** 컨벤셔널 인터리빙 대신 하위 비트를 컬럼/로우에 매핑 → 랭크 내 로컬 데이터 집계
  - **Optimization-2:** 칩 인덱스를 상위 비트에 매핑 → 인접 데이터가 동일 DB에 연결된 칩에 저장
    - 칩 간 통신 최소화, 칩 수준 병렬성 잠재력 제공
    - 기존: 64B 버스트로 4B 데이터만 유용 → 세부 접근 지원으로 대역폭 활용도 대폭 향상

- **대역폭 인식 데이터 매핑 (Bandwidth-Aware Data Mapping):**
  - 충분한 여유 칩이 있으면 인덱스 데이터를 복제하여 병렬 접근 지원
  - 여유 칩이 부족하면 모든 칩에 균등 매핑으로 가용 대역폭 최대 활용

- **개별 칩 선택 (ICS - Individual Chip Selection):**
  - 컨벤셔널 DIMM: 모든 칩에 공유 CS 신호 → 잠금 걸린(lock-step) 작업 패턴
    - 세부 랜덤 접근 시 불필요한 데이터 출력으로 **50% 대역폭 낭비**
  - ICS: 각 DRAM 칩에 개별 CS 와이어 설계 → RCD-side MC에서 제어
    - 칩 0 활성화/칩 1 비활성화 → 첫 번째 C/A 전송 → CS 전환 → 칩 1 활성화/칩 0 비활성화
    - **지연 시간 절감:** 파이프라인 명령으로 순차 처리, **에너지 절감:** 불필요한 출력 제거
    - 결과: 세부 메모리 접근 지원 + 칩 수준 병렬성 구현

### 3.3. Inter-Rank 확장 설계

- **폴링 기반 통신 (CPU-Polling):**
  - 호스트 CPU가 모든 DIMM을 주기적 폴링 → 랭크 간 데이터 접근 시 호스트가 전송 조율
  - 하드웨어 수정 불필요, 단순 설계
  - 단점: 데이터 전송 없이도 호스트/메모리 버스 점유

- **인터럽트 기반 통신:**
  - DDR의 RFU(Reserved for Future Use) 핀을 인터럽트 신호로 활용
  - APIC에 연결하여 DB에서 원격 데이터 접근 필요 시 호스트에 알림
  - 폴링 대비 개선: 버스 점유 없음, 호스트 우선 스케줄링의 추가 지연 없음

- **NVDIMM 기반 솔루션:**
  - NVDIMM-P의 높은 밀도 NVM에 대용량 DNA 인덱스 저장
  - 원격 랭크 접근을 온-DIMM NVM 로컬 접근으로 변환 → 랭크 간 통신 완전 제거
  - DRAM + NVM 모두 바이트 접근 가능

- **알고리즘 특화 데이터 압축:**
  - BWA-MEM의 Bucket 구조를 개선: Row Head Bucket + Compressed Bucket
    - 기존: 체크포인트에 32비트 OR 값 저장 → 압축 후 Fine-grained 체크포인트로 정밀도 감소
  - 메모리 공간 **48.9% 절감** (평균)
  - 매 이터레이션당 필요 데이터량 감소 → 통신 오버헤드도 동시에 감소

## 핵심 기여

- **핵심 기여:** 상용 DRAM 컴포넌트를 활용한 **실용적 NDP 가속기 MEDAL** 제시
- 세부 랜덤 메모리 접근 문제를 알고리즘 특화 기술(주소 매핑, 데이터 매핑, ICS)로 해결
- 세 가지 인터랭크 설계로 대규모 데이터 확장성 확보
- **CPU 대비 30.50x~69.69x 스피드업**, 에너지 **289.91x~426.27x 절감** (설계별 차이)
- 기존 NDP 가속기(Chameleon, AIM) 대비 **3.43x~8.37x** 성능 향상
- DDR 인터페이스를 활용하여 유연한 시스템 통합 (일반 메모리로도 재구성 가능)
- 향후 그래프 처리, 데이터베이스 검색, 희소 행렬 연산 등 다른 애플리케이션으로의 확장 가능성

## 주요 결과

- **시스템 구성:**
  - CPU: Intel Xeon E5-2680 v3, 2.50GHz
  - 메모리: 400GB, L1 64KB/L2 256KB/L3 32MB
  - MEDAL: 384GB, 4채널, DIMM당 4랭크, 랭크당 16 DRAM 칩
  - DRAM: DDR4 4Gb×4, Bank Group 2, 은행당 2개, 1,200MHz
- **시뮬레이션:** Ramulator 기반 주 정확도 시뮬레이터 수정
- **하드웨어 매개변수:** Design Compiler (28nm 기술)로 사전 레이아웃 추정
  - Addr Trans: 20클록, 4.05mW
  - SMEM: 1클록, 6.00mW
  - Suffix: 5클록, 0.52mW
- **데이터베이스:** NCBI에서 10개 게놈 (15.9억~276억 바이스)
- **쿼리 시퀀스:** 각 게놈에서 추출한 1,000만 개 101길이 시퀀스

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]


## 전체 요약

[[../paper-summaries/2019MICRO-summarize/medal_scalable_dimm_based_ndp_accelerator_for_dna_seeding_algorithm.md|전체 요약 보기]]
