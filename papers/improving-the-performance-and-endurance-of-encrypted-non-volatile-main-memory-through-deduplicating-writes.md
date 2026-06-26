---
tags: [paper, 2018, 2018MICRO, topic/dram, topic/nvm]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/improving-the-performance-and-endurance-of-encrypted-non-volatile-main-memory-through-deduplicating-writes.md"
---

# Improving the Performance and Endurance of Encrypted Non-volatile Main Memory through Deduplicating Writes

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Pengfei Zuo, Yu Hua, Ming Zhao†, Wen Zhou, Yuncheng Guo (Wuhan National Laboratory for Optoelectronics, School of Computer, Huazhong University of Science and Technology, China; †Arizona State University, USA)

## 개요

- DRAM 기술은 높은 전력 누수와 제한된 스케일링으로 인해 차세대 메인 메모리 후보로 NVM(Non-Volatile Memory) 기술이 주목
- NVM 기술(PCM, ReRAM, STT-RAM)의 장점: 높은 밀도, 높은 스케일링, 거의 제로인 대기 전력
- 그러나 NVM은 다음과 같은 문제에 직면:
  - **제한된 쓰기 내구성 및 성능:**
    - PCM의 쓰기 내구성: 10^7 - 10^8회
    - 쓰기가 읽기 대비 3-8배 높은 지연 시간 및 에너지 오버헤드
    - 지속성 메모리(persistent memory)에서 쓰기가 애플리케이션 실행의 크리티컬 패스에 위치
  - **데이터 잔류 취약성(Data Remanence Vulnerability):**
    - NVM은 비휘발성으로 시스템 전원 종료 후에도 데이터 유지
    - 도난된 NVM DIMM에서 공격자가 데이터를 직접 스트림 아웃 가능
    - 메모리 암호화로 데이터 보호 필요
- **메모리 암호화의 문제:**
  - 강한 확산 특성(diffusion property)으로 인해 평문의 단일 비트 변화가 암호문의 약 절반 비트 변화를 초래
  - 기존 비트 수준 쓰기 감소 기법(DCW, Flip-N-Write)이 암호화된 NVM에서 효과 불충분
  - 쓰기 내구성 문제를 악화시킴
- **관찰:** 실제 애플리케이션에서 캐시 라인 수준의 데이터 중복이 풍부
  - 20개 SPEC CPU2006/PARSEC 애플리케이션에서 평균 58%의 쓰기가 기존 데이터와 동일
  - 일부 애플리케이션에서는 98%까지 중복

## 방법론

### 3.1. 경량 중복 제거 기법

- **해싱 접근법:**
  - 기존 암호화 해시(SHA-1, MD5)의 높은 지연 시간 문제 (>300ns)
  - 경량 해시 함수 사용: 낮은 지연 시간으로 캐시 댍인 지문(fingerprint) 계산
  - 해시 매칭 시 실제 데이터 비교로 중복 확인
- **NVM 읽기/쓰기 비대칭 활용:**
  - NVM의 쓰기 지연 시간이 읽기 대비 3-8배 높음
  - 중복 쓰기 제거가 읽기 지연 시간 비용으로 성능 향상 달성
  - 경량 해시 + 읽기 확인이 전체 쓰기 지연 시간보다 짧음
- **인라인 중복 제거:**
  - 중복 쓰기를 NVM에 기록하기 전에 식별 및 제거
  - 기존 아웃오브라인 중복 제거의 한계 극복

### 3.2. 암호화와의 시너지 통합

- **기회적 병렬화:**
  - **중복 예측 기반:** 캐시 라인이 중복으로 예측되면 암호화 없이 중복 제거만 수행
  - **비중복 예측 시:** 암호화와 중복 제거를 병렬로 수행하여 쓰기 지연 시간 감소
  - 간단하지만 효과적인 중복 예측 스킴
- **메타데이터 공유 위치화(Colocation):**
  - 카운터 모드 암호화의 라인당 카운터를 중복 제거 데이터 구조의 널 위치에 임베딩
  - 메타데이터 저장 공간 오버헤드 감소 (6.25%)
  - 카운터와 해시의 통합 관리

### 3.3. 카운터 모드 암호화

- **원리:**
  - 카운터와 비밀 키를 사용하여 원타임 패드(OTP) 생성
  - 평문/암호문을 OTP와 XOR하여 암복호화
  - 라인 주소와 라인당 카운터로 OTP 생성
- **보안 특성:**
  - 각 OTP가 암호화에 재사용되지 않도록 보장
  - 라인당 카운터가 쓰기마다 증가하여 동일 주소의 재쓰기에 다른 OTP 생성
- **성능 특성:**
  - 읽기와 병렬로 복호화 가능하여 지연 시간 숨김
  - XOR 연산의 미세한 지연 시간만 크리티컬 패스에 추가

### 3.4. 시스템 구현

- **시뮬레이션 플랫폼:** gem5 + NVMain
- **구현 구성요소:**
  - 경량 해시 엔진
  - 중복 제거 로직
  - 카운터 모드 암호화 엔진
  - 메타데이터 관리 유닛
- **메타데이터 구조:**
  - 라인당 해시: 중복 제거용
  - 라인당 카운터: 암호화용
  - 주소 매핑 테이블: 중복 데이터 참조용

## 핵심 기여

- **핵심 기여:** 암호화된 NVM의 성능과 수명을 동시에 향상시키는 DeWrite 스킴 제시
  - 경량 인라인 중복 제거로 쓰기 54% 감소
  - 암호화와의 시너지 통합으로 성능 향상
- **성능 향상:**
  - 쓰기 속도 4.2배, 읽기 속도 3.1배 향상
  - 시스템 IPC 82% 향상
  - 에너지 소비 40% 감소
- **실용성:**
  - 메타데이터 오버헤드 6.25%로 낮은 수준 유지
  - gem5 + NVMain에서의 구현으로 실용적 검증
- **의의:**
  - NVM 기반 메인 메모리의 보안과 성능/수명 간의 트레이드오프 해결
  - 차세대 메인 메모리 시스템 설계에 중요한 기여
  - 중복 제거가 메모리 시스템에서의 새로운 최적화 기회 제시
- **한계점:**
  - 중복 제거의 효과가 워크로드에 따라 변동 (평균 58%, 최대 98%)
  - 경량 해시의 거짓 양성 오버헤드 추가 분석 필요
  - 실제 NVM 하드웨어에서의 검증 필요

## 주요 결과

- **시뮬레이션 플랫폼:** gem5 (풀시스템 시뮬레이션) + NVMain (NVM 모델링)
- **워크로드:** SPEC CPU2006 (12개) + PARSEC (8개) = 총 20개 애플리케이션
- **NVM 구성:**
  - 쓰기 지연 시간: 읽기 대비 3-8배
  - 쓰기 내구성: 10^7 - 10^8회
- **암호화:** 카운터 모드 암호화 (AES 기반)
- **중복 제거:** 경량 해시 기반 인라인 중복 제거
- **메타데이터 오버헤드:** 6.25%

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/improving-the-performance-and-endurance-of-encrypted-non-volatile-main-memory-through-deduplicating-writes.md|전체 요약 보기]]
