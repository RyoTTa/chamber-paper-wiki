---
tags: [paper, 2020, 2020ISCA, topic/cache, topic/compression, topic/nvm]
venue: "IEEE/ACM International Symposium on Computer Architecture (ISCA), 2020"
year: 2020
summary_path: "../paper-summaries/2020ISCA-summarize/morlog-morphable-hardware-logging-for-atomic-persistence-in-non-volatile-main-memory.md"
---

# MorLog: Morphable Hardware Logging for Atomic Persistence in Non-Volatile Main Memory

**Venue:** IEEE/ACM International Symposium on Computer Architecture (ISCA), 2020
**저자:** Xueliang Wei, Dan Feng, Wei Tong, Jingning Liu, Liuqing Ye (Wuhan National Laboratory for Optoelectronics, Huazhong University of Science and Technology)

## 개요

- 바이트 주소 지정 가능한 비휘발성 메모리(NVM: Phase Change Memory, Resistive RAM, 3D XPoint 등)는 메인 메모리로 사용될 잠재력을 가지고 있음
- NVMM(Non-Volatile Main Memory) 시스템은 시스템 장애(전원 손실, 시스템 크래시) 상황에서 데이터의 **원자적 지속성(Atomic Persistence)**을 보장해야 함
- NVM 셀 프로그래밍 시 **높은 쓰기 오버헤드** 발생: MLC/TLC NVM은 쓰기 지연 시간과 에너지가 SLC 대비 **최대 10배** 증가
- 기존 하드웨어 로깅 설계의 문제점:
  - **Undo 설계**: 트랜잭션 커밋 시 모든 업데이트된 데이터의 지속을 기다려야 함 → 순서 제약 조건
  - **Redo 설계**: 트랜잭션의 모든 로그 데이터가 지속될 때까지 제자리 데이터 업데이트를 금지 → 순서 제약 조건
  - **Undo+Redo 설계**: 순서 제약 조건은 완화하지만, 여전히 보수적으로 모든 로그 데이터를 기록 → 중복 로그 데이터

## 방법론

### 3.1. Morphable Logging 메커니즘

- **Undo 데이터 처리**: 원자성을 보장하기 위해 eager하게 NVMM에 기록
- **Redo 데이터 처리**: 휘발성 로그 버퍼와 L1 캐시에 버퍼링하여 최신 redo 데이터만 NVMM에 기록
- **동적 전환**: 트랜잭션 실행 중 undo+redo 모드에서 redo-only 모드로 동적 전환
- **복구 시 보장**: 각 데이터 항목에 대해 가장 오래된 undo 값과 최신 redo 값만 필요

### 3.2. Selective Log Data Encoding

- **Differential Log Data Compression**: 로그 데이터의 특성을 활용한 차별화 압축 방법
  - 클린 비트(값이 변경되지 않은 비트)는 로그 데이터에서 직접 폐기
  - 더러운 비트(값이 변경된 비트)만 압축하여 저장
- **동적 인코딩 선택**: 여러 인코딩 방법을 동시에 적용하여 최소 쓰기 비용을 선택
- **인코딩 방법**: 다양한 압축 알고리즘을 조합하여 로그 데이터의 특성에 최적화

### 3.3. 아키텍처 구성요소

- **Log Buffer**: 휘발성 메모리에 위치한 로그 데이터 버퍼링 구조
- **L1 Cache Integration**: L1 캐시를 활용한 로그 데이터 일시적 저장
- **Persistence Controller**: NVMM에 대한 쓰기 순서 및 지속성을 관리하는 하드웨어 컨트롤러

## 핵심 기여

- **핵심 기여**: 복구에 필요한 최소 로그 데이터만 기록하는 MorLog 설계 제안
- **성능 향상**: 기존 최신 하드웨어 로깅 설계 대비 **72.5%** 성능 향상 달성
- **효율성**: NVMM 쓰기 트래픽 **41.1%** 감소, 쓰기 에너지 **49.9%** 감소
- **실용성**: NVMM 시스템에서 원자적 지속성을 효율적으로 지원하는 실용적인解决方案 제시

## 주요 결과

- **구현 언어**: RTL(Register Transfer Level) 설계 및 시뮬레이션
- **하드웨어 오버헤드**: 추가적인 로깅 로직 및 인코딩 유닛
- **시스템 구성**: 프로세서 코어, 로그 버퍼, NVMM 컨트롤러로 구성
- **NVMM 인터페이스**: 표준 메모리 버스 프로토콜 사용

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]


## 전체 요약

[[../paper-summaries/2020ISCA-summarize/morlog-morphable-hardware-logging-for-atomic-persistence-in-non-volatile-main-memory.md|전체 요약 보기]]
