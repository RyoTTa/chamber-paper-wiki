---
tags: [paper, 2018, 2018MICRO, topic/cache, topic/dram, topic/rowhammer, topic/storage]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/duplicon-cache-mitigating-off-chip-memory-bank-and-bank-group-conflicts-via-data-duplication.md"
---

# Duplicon Cache: Mitigating Off-Chip Memory Bank and Bank Group Conflicts via Data Duplication

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Ben (Ching-Pei) Lin (University of Texas at Austin), Michael B. Healy (IBM T.J. Watson Research Center), Rustam Miftakhutdinov (Intel Corporation), Philip G. Emma (IBM T.J. Watson Research Center), Yale Patt (University of Texas at Austin)

## 개요

- DDR4 DRAM은 **뱅크 그룹(Bank Group)** 구조를 도입하여 뱅크 수를 효과적으로 늘리고 비용을 절감
- 그러나 뱅크 그룹 내 다른 뱅크에 대한 연속 활성화(Activate) 및 읽기(Read) 명령 시 추가 지연(tRRD_L, tCCD_L) 발생 → **뱅크 그룹 충돌(Bank Group Conflict)**
- 동일 뱅크의 다른 행에 대한 요청은 Precharge/Activate/Read가 직렬로 처리되어 **뱅크 충돌(Bank Conflict)** 발생
- 이상적 실험 결과:
  - 뱅크 충돌만 제거: **14.8%** 평균 성능 향상
  - 뱅크 그룹 충돌만 제거: **11.6%** 평균 성능 향상
  - 둘 다 제거: **22.5%** 평균 성능 향상 (최대 37.5%)
- 기존 해결책들의 한계:
  - OS 기반 뱅크 파티셔닝: 충분한 뱅크/스레드 비율 필요 (8-16개/스레드)이나 현대 시스템은 ~6.86개/스레드
  - 주소 매핑 개선: 뱅크 수가 부족하면 충돌 불가피
  - DRAM 변경 기반 (SALP, Tiered-Latency): 상용 DRAM 변경 필요
  - 완전 복제(Full Duplication): 저장공간 및 일관성 비용이 부담

## 방법론

### 3.1. 데이터 저장소 (Reserved Storage)

- 물리 메모리 주소 공간의 끝에 128MB 영역 예약 (전체 16GB의 1/128)
- OS에는 16GB - 128MB = 15.872GB로 알려짐 → 메모리 할당에서 제외
- 복제된 데이터는 홈 뱅크 그룹과 다른 뱅크 그룹의 Reserved Storage에 저장

### 3.2. 라인 크기 (64B)

- DDR4 DRAM의 최소 접근 단위: 8 컬럼 × 8바이트 = 64바이트
- DDR4 버스트 길이 8에 맞춤

### 3.3. 세트 연관 구조 (4-way Set-Associative)

- 각 홈 뱅크 그룹(m)의 데이터는 대체 뱅크 그룹(m+1 mod 4)의 4개 뱅크 중 하나에 복제 가능
- 전통적 캐시와 유사한 세트/웨이 구조:
  - 인덱스 비트: 홈 주소의 비채널, 비컬럼 인덱스 비트 사용
  - 태그 비트: Address Tag로 섹터 식별
- 4-way가 단일 웨이보다 우수 (실험으로 확인)

### 3.4. 태그 저장소 (Tag Store)

- 메모리 컨트롤러의 전용 SRAM 테이블 (채널별 142KB, 총 284KB)
- 각 엔트리 구성:
  1. **Address Tag (9비트)**: 섹터 식별 (물리 주소의 행 비트 15~9 + 뱅크 비트 1~0)
  2. **Valid Columns Mask (128비트)**: 유효 컬럼 추적 (1K 컬럼 / 8 컬럼 per 라인)
  3. **Demand Activates Counter (DAC, 4비트)**: 포화 카운터, 삽입 정책에 사용
  4. **Useful Bit (1비트)**: 교체 정책에 사용

### 3.5. Demand Activates Filtering

- 복제는 비용(스토리지, 쓰기 트래픽)이 발생하므로, 성능에 영향을 줄 데이터만 복제
- **Demand Activate** = demand 읽기 요청에 대한 행 활성화 (행 버퍼 미스 발생 시)
- DAC로 행별 demand activate 횟수 추적, **Threshold (Thrsh=15)** 초과 시 복제 시작
- 세 가지 기준:
  1. demand 읽기 요청이 프로그램 임계 경로에 있을 가능성 높음
  2. 행 버퍼 미스/충돌 시 더 긴 지연 발생
  3. demand activate 횟수로 위 두 기준을 동시에 측정 가능

### 3.6. 유틸리티 추적 및 확률적 교체

- **Usefulness Tracking**: 복제된 컬럼이 실제로 읽기 요청으로 소스되었는지 추적
  - 유틸리티가 있는 섹터는 교체 불가
  - 주기적으로 (100만 메모리 요청마다) 유틸리티 비트 리셋
- **Probabilistic Replacement**: Monitoring 및 Duplicating-not useful 상태의 섹터는 확률 ε=1/256로 교체 가능
  - 유용한 섹터가 될 시간을 부여하면서, 불필요한 섹터는Eventually 교체

### 3.7. 캐시 섹터 상태 머신

1. **Invalid** (DAC=0): 행이 아직 할당되지 않음
2. **Monitoring** (1≤DAC<Thrsh): 행 할당됨, DAC 증가 중, 복제 시작 전
3. **Duplicating-not useful** (DAC≥Thrsh, Useful=0): 모든 접근 시 복제, 아직 사용되지 않음
4. **Duplicating-useful** (DAC≥Thrsh, Useful=1): 복제 데이터가 사용됨, 교체 보호

## 핵심 기여

- **핵심 기여**: 메모리 컨트롤러에 구현되는 Duplicon Cache로 DRAM 뱅크 및 �뱅크 그룹 충돌 완화
- **성능**: 평균 **8.3%** 성능 향상, 최대 **~17%**
- **에너지**: 평균 **5.6%** 에너지 절감
- **실용성**: 상용 DRAM 변경 불필요, 메모리 컨트롤러 수정만으로 구현
- **저장소 효율**: 128MB Reserved Storage (전체 16GB의 0.78%) + 284KB 태그 저장소로 충분한 이득 달성
- **의의**: 뱅크/뱅크 그룹 충돌이라는 DRAM 아키텍처의 근본적 문제를 소프트웨어 투명하게 해결하는 새로운 접근법 제시

## 주요 결과

- **시뮬레이터**: Multi2Sim 기반 실행驱动 정확 시뮬레이터 (4코어 x86)
- **프론트엔드**: Multi2Sim 기반
- **메모리 컨트롤러**: 128 엔트리 메모리 큐, FR-FCFS 스케줄링, Open-Page 정책
- **프리페처**: Stream Prefetcher (스트림 64, 거리 64, 큐 128, 디그리 4) + FDP
- **DRAM**: 2채널, 랭크당 1뱅크 그룹, 랭크당 16뱅크, 8Gb DDR4-3200 x8
- **태그 저장소 면적**: 채널별 142KB, 총 284KB (SRAM)
- **DRAM 저장 오버헤드**: 코어당 32MB (128MB total)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/duplicon-cache-mitigating-off-chip-memory-bank-and-bank-group-conflicts-via-data-duplication.md|전체 요약 보기]]
