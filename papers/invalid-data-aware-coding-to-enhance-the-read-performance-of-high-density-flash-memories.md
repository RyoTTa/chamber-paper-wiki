---
tags: [paper, 2018, 2018MICRO, topic/dram, topic/storage]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/invalid-data-aware-coding-to-enhance-the-read-performance-of-high-density-flash-memories.md"
---

# Invalid Data-Aware Coding to Enhance the Read Performance of High-Density Flash Memories

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Wonil Choi, Myoungsoo Jung, Mahmut Kandemir (Pennsylvania State University, Yonsei University)

## 개요

- NAND 플래시 기술의 성숙으로 SSD가 다양한 컴퓨팅 영역에서 광범위하게 사용
- 저장 용량 증가 전략: (1) 피처 사이즈 축소, (2) 3D 아키텍처 스택, (3) 셀당 비트 밀도 증가
- 고비트 밀도 플래시(MLC, TLC, QLC)가 주류:
  - MLC: 셀당 2비트
  - TLC: 셀당 3비트 (LSB, CSB, MSB)
  - QLC: 셀당 4비트
- **읽기 성능 변동 문제(Read Performance Variation):**
  - TLC 셀의 3종류 비트(LSB, CSB, MSB)가 서로 다른 읽기 지연 시간 보유
  - CSB 읽기가 LSB보다 오래 걸리고, MSB 읽기가 가장 오래 걸림
  - MSB 읽기 지연 시간은 LSB의 2배 이상
- **원인:** 기존 코딩에서 각 비트 읽기에 다른 수의 메모리 액세스 필요
  - LSB: 1회 액세스
  - CSB: 2회 액세스
  - MSB: 4회 액세스
- **기존 코딩의 문제점:**
  - LSB 값이 무효화(invalidated)된 후에도 CSB/MSB 읽기 지연 시간이 줄어들지 않음
  - 메모리 액세스 횟수가 동일하게 유지되어 성능 비효율 초래
- 읽기 중심 워크로드에서 읽기 지연 시간 최적화가 SSD 성능에 필수적

## 방법론

### 3.1. TLC 플래시 읽기 메커니즘

- **전압 상태:** 8개의 전압 범위(S1-S8)로 3비트 조합 표현
- **읽기 과정:**
  - LSB 읽기: 1개의 읽기 전압(Vread)으로 1회 셀 감지
  - CSB 읽기: 2개의 읽기 전압으로 2회 셀 감지
  - MSB 읽기: 4개의 읽기 전압으로 4회 셀 감지
- **기존 코딩의 비효율:**
  - LSB가 무효화되어도 CSB/MSB 읽기는 동일한 액세스 횟수 유지
  - 예: LSB 페이지가 삭제된 후에도 MSB 읽기는 4회 액세스 필요

### 3.2. IDA 코딩 원리

- **전압 조정(Voltage Adjustment):**
  - LSB/CSB 무효화 시 중복 전압 상태를 병합
  - 병합된 전압 상태는 더 적은 수의 감지 전압으로 구분 가능
  - 예: LSB 무효화 시 MSB 읽기를 4회 → 2회로, CSB 읽기를 2회 → 1회로 감소
- **변환 과정:**
  1. 전통적 코딩으로 새 블록에 데이터 기록
  2. 블록 내 다수 페이지가 무효화되면 IDA 코딩 적용
  3. 재프로그래밍(reprogramming)으로 전압 레벨 조정
  4. 조정된 블록은 향상된 읽기 지연 시간 제공
- **효과:**
  - MSB 읽기: 4회 → 1-2회 액세스로 감소
  - CSB 읽기: 2회 → 1회 액세스로 감소
  - 읽기 지연 시간이 LSB 수준으로 근접

### 3.3. 데이터 리프레시와의 통합

- **데이터 리프레시(data refresh)란:**
  - 데이터 무결성 유지를 위해 정기적으로 수행되는 플래시 기본 연산
  - 절차: (1) 대상 블록에서 데이터 읽기 → (2) ECC로 오류 정정 → (3) 새 블록에 기록
- **통합 방식:**
  - IDA 코딩의 전압 조정 시간을 리프레시 과정의 단계(3)에 대체
  - 리프레시 시 이미 오류 정정된 데이터를 확보하므로 전압 조정으로 인한 데이터 손실 위험 제거
  - 전압 조정이 스토리지 내부 대역폭을 사용하는 오버헤드를 리프레시와 공유하여 은폐
- **이점:**
  - 성능 오버헤드 은폐: 전압 조정 시간이 리프레시 시간에 포함
  - 신뢰성 보장: 오류 정정 후 데이터를 사용하므로 전압 조정으로 인한 인접 셀 간섭으로부터 보호
  - 기존 SSD 동작과의 호환성: 데이터 리프레시는 현대 SSD의 기본 기능

### 3.4. MLC 및 QLC로의 일반화

- **MLC (2비트/셀):**
  - LSB 무효화 시 MSB 읽기 지연 시간 감소
  - 2개 전압 상태 병합으로 감지 전압 수 감소
- **QLC (4비트/셀):**
  - 더 많은 비트 조합에 대한 전압 조정 가능
  - 다수 비트 무효화 시 더 큰 읽기 성능 향상 기대
- **범용성:** IDA 코딩은 고비트 밀도 플래시의 일반적인 문제를 해결하는 접근법

## 핵심 기여

- **핵심 기여:** 고비트 밀도 플래시의 읽기 성능 변동 문제를 해결하는 IDA 코딩 제시
  - 비트 무효화 시 전압 조정으로 읽기 지연 시간 감소
  - 데이터 리프레시와의 통합으로 성능/신뢰성 오버헤드 은폐
- **성능 향상:**
  - TLC에서 읽기 응답 시간 평균 28% 향상
  - MLC에서도 14.5% 성능 향상
- **실용성:**
  - 기존 SSD 데이터 리프레시 기능과의 완전한 호환성
  - 별도의 하드웨어 추가 없이 소프트웨어 수준 구현 가능
- **의의:**
  - 고비트 밀도 플래시의 읽기 성능 최적화에 새로운 방향성 제시
  - 읽기 중심 워크로드에서의 SSD 성능 향상에 기여
  - 차세대 플래시 기술(QLC 등)에서의 활용 가능성 제시
- **한계점:**
  - 쓰기 중심 워크로드에서는 효과 제한적
  - 전압 조정의 정밀도와 신뢰성에 대한 추가 연구 필요
  - 실제 상용 SSD에서의 검증 필요

## 주요 결과

- **대상 디바이스:** TLC 기반 SSD
- **구현 위치:** FTL(Flash Translation Layer) 내 데이터 리프레시 모듈
- **전압 조정 메커니즘:**
  - ISPP(Incremental Step Pulse Programming) 기반 전압 레벨 조정
  - 인접 셀 간섭(NI) 고려한 정밀 전압 제어
- **오류 관리:**
  - ECC 엔진과 통합된 오류 정정
  - 전압 조정 전후 데이터 무결성 검증
- **호환성:** 현대 SSD의 기본 데이터 리프레시 기능과의 완전한 호환성

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/invalid-data-aware-coding-to-enhance-the-read-performance-of-high-density-flash-memories.md|전체 요약 보기]]
