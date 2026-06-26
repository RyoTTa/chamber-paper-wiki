---
tags: [paper, 2018, 2018MICRO, topic/dram, topic/nvm, topic/security]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/osiris-a-low-cost-mechanism-to-enable-restoration-of-secure-non-volatile-memories.md"
---

# Osiris: A Low-Cost Mechanism to Enable Restoration of Secure Non-Volatile Memories

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** NOTA 논문 정보에서 확인 필요

## 개요

- 비휘발성 메모리(NVM, Non-Volatile Memory)의 등장:
  - 전원이 꺼져도 데이터를 유지하는 메모리 기술 (PCM, STT-MRAM, ReRAM 등)
  - DRAM 대비 낮은 대기 전력, 높은 집적도
  - 시스템 메모리로의 잠재적 사용 가능성

- 보안 문제:
  - NVM은 물리적으로 접근 가능하여 데이터 탈취 위협
  - 기존 보안 메커니즘: 메모리 암호화, 무결성 검증
  - **복원(Restoration) 문제:** 전원 차단 후 시스템 복구 시 보안 상태 복원 필요

- 기존 복원 메커니즘의 한계:
  - 높은 오버헤드: 암호화된 데이터 복호화, 무결성 검증에 많은 시간과 에너지 소비
  - 복원 시간이 시스템 시작 시간을 크게 증가
  - 실용적 배치를 위한 저비용 복원 메커니즘 필요

## 방법론

### 3.1. 보안 NVM 아키텍처

- **기존 NVM 보안 메커니즘:**
  - 메모리 암호화: 데이터를 암호화하여 저장
  - 무결성 검증: 태그(tag)를 사용하여 데이터 변조 감지
  - 랜덤 액세스 패턴 암호화: 패턴 분석 공격 방지

- **복원 과정의 문제점:**
  - 전원 차단 후 복구 시 암호화 키 복구 필요
  - 무결성 태그 재계산 오버헤드
  - 전체 메모리 복호화에 많은 시간 소요

### 3.2. Osiris 복원 메커니즘

- **체크포인트 기반 복원:**
  - 주기적으로 보안 상태 체크포인트 저장
  - 복원 시 체크포인트에서 빠르게 복구
  - 전체 메모리 복원 대비 빠른 복원 시간

- **점진적 복원(Incremental Restoration):**
  - 전체 메모리를 한 번에 복원하지 않고, 접근 순서에 따라 점진적 복원
  - 콜드 부팅(cold boot) 시간 단축
  - 지연된 복원(deferred restoration) 지원

- **하드웨어 지원:**
  - 메모리 컨트롤러에 복원 로직 추가
  - 체크포인트 저장/복원을 위한 전용 레지스터
  - 암복호화 엔진 통합

### 3.3. 보안 보장

- **기밀성(Confidentiality):**
  - 복원 과정에서도 암호화된 데이터 유지
  - 복원 중간 상태에서의 데이터 유출 방지

- **무결성(Integrity):**
  - 복원된 데이터의 무결성 검증
  - 부분 복원 시 무결성 태그 검증

- **내성(Tamper Resistance):**
  - 물리적 접근 시 데이터 자동 삭제
  - 복원 과정에서의 변조 감지

## 핵심 기여

- **핵심 기여:** 보안 비휘발성 메모리의 저비용 복원 메커니즘 Osiris 제안
- **성능 향상:** 기존 보안 NVM 대비 복원 시간 크게 단축, 낮은 하드웨어 오버헤드
- **의의:** 
  - NVM의 실용적 보안 배치 가능성을 높임
  - 시스템 시작 시간 문제 해결
  - 보안과 성능의 균형 달성
- **한계점:** 
  - 체크포인트 저장을 위한 추가 메모리 영역 필요
  - 특정 NVM 기술에 최적화 가능
  - 복원 과정에서의 부가적 에너지 소비

## 주요 결과

- 기존 NVM 메모리 컨트롤러에 하드웨어 추가
- 체크포인트 저장을 위한 전용 메모리 영역
- 암복호화 엔진 (AES 등)
- 무결성 검증 회로 (GHASH 등)
- 복원 제어 로직

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/security.md|Security]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/osiris-a-low-cost-mechanism-to-enable-restoration-of-secure-non-volatile-memories.md|전체 요약 보기]]
