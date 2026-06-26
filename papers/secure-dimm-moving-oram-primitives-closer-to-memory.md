---
tags: [paper, 2018, 2018HPCA, topic/dram]
venue: "HPCA '18 (IEEE International Symposium on High Performance Computer Architecture), 2018"
year: 2018
summary_path: "../paper-summaries/2018HPCA-summarize/secure-dimm-moving-oram-primitives-closer-to-memory.md"
---

# Secure DIMM: Moving ORAM Primitives Closer to Memory

**Venue:** HPCA '18 (IEEE International Symposium on High Performance Computer Architecture), 2018
**저자:** Ali Shafiee, Rajeev Balasubramonian, Feifei Li (University of Utah), Mohit Tiwari (University of Texas, Austin)

## 개요

- 클라우드 환경에서 데이터와 연산의 프라이버시 보장에 대한 긴요한 필요성 증가
- 신뢰할 수 없는 클라우드 운영자가 서버에 물리적 접근이 가능하고 프로세서 소켓에서 나오는 신호를 모니터링할 수 있는 공격 모델
- 데이터 패킷이 암호화되어 있더라도 프로그램이 접근하는 주소 시퀀스는 정보 사이드 채널로 작용
- Oblivious RAM(ORAM)은 수십 년간 연구되어 왔지만 여전히 큰 오버헤드를 발생
- 기존 ORAM의 한계:
  - 단일 메모리 접근을 100개 이상의 메모리 접근으로 변환
  - 프로세서의 제한된 메모리 채널 대역폭을 빠르게 포화
  - 높은 지연시간과 에너지 소비

## 방법론

### 3.1. SDIMM 구조
- 상용 DDR 호환 제품과 DIMM 인터페이스 활용
- 안전 버퍼 칩(ASIC)을 DIMM에 통합
- 신뢰 컴퓨팅 기반(TCB)의 일부로 구성
- 메모리 용량 및 비용: 기존 활성 메모리 아키텍처보다 높은 용량과 낮은 비용

### 3.2. Independent ORAM 프로토콜
- 각 SDIMM이 ORAM 트리의 독립적인 부분 담당
- SDIMM 내에서 대부분의 ORAM 작업 수행
- 메인 메모리 채널의 대역폭 사용 최소화
- 높은 수준의 병렬 ORAM 작업 달성

### 3.3. Split ORAM 프로토콜
- ORAM 트리를 SDIMM 간에 분할
- 각 SDIMM이 트리의 다른 레벨 담당
- 셔플(shuffle) 작업을 SDIMM 간에 분산
- 메인 메모리 채널의 부담 최소화

### 3.4. 보안 분석
- Path ORAM과 동일한 무시성(obliviousness) 보장
- 암호화 및 디크립션 로직을 안전 버퍼 칩에 통합
- 주소 패턴의 정보 누출 방지

## 핵심 기여

- 핵심 기여: ORAM 기능을 메모리 시스템으로 이동하여 성능 및 에너지 효율성 크게 향상
- 성능 향상: Freecursive ORAM 대비 1.9배 성능, 2.55배 에너지 효율성
- 상용 하드웨어 활용으로 실용적 적용 가능성 입증
- 클라우드 환경에서의 프라이버시 보장에 대한 중요한 발전 방향 제시

---

## 규칙 준수
1. 한국어로 작성 (기술 용어는 영어 원어 병기)
2. 수치적 결과 포함 (성능 및 에너지 향상 수치)
3. 모든 Figure/Table 참조 포함
4. 각 섹션은 최소 3개 이상의 bullet point
5. 알고리즘/수식이 있으면 pseudo-code 수준으로 기술
6. 기존 요약 파일 형식과 퀄리티 준수

## 주요 결과

- 구현 구성 요소:
  - SDIMM: 상용 DRAM 칩 + 안전 버퍼 칩(ASIC)
  - ORAM 컨트롤러: 기존 보안 CPU에서 SDIMM으로 이동
  - 메모리 인터페이스: 표준 DDR 인터페이스 활용
- 하드웨어 요구 사항:
  - 안전 버퍼 칩: 암호화/디크립션 로직, ORAM 제어 로직
  - 상용 DRAM: 비신뢰 환경에서도 사용 가능

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2018HPCA-summarize/secure-dimm-moving-oram-primitives-closer-to-memory.md|전체 요약 보기]]
