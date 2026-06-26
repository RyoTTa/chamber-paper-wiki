---
tags: [paper, 2020, 2020HPCA, topic/cache, topic/disaggregation, topic/dram]
venue: "2020 IEEE International Symposium on High Performance Computer Architecture (HPCA '20)"
year: 2020
summary_path: "../paper-summaries/2020HPCA-summarize/impala-algorithm-architecture-co-design-for-in-memory-multi-stride-pattern-matching.md"
---

# Impala: Algorithm-Architecture Co-Design for In-Memory Multi-Stride Pattern Matching

**Venue:** 2020 IEEE International Symposium on High Performance Computer Architecture (HPCA '20)
**저자:** Elaheh Sadredini (University of Virginia), Danning Jiang (University of Virginia), Mohsen Imani (University of California, Irvine), Tajana Rosing (University of California, Irvine), Kevin Skadron (University of Virginia)

## 개요

- 자동차 처리(Automata Processing, AP)는 네트워크 보안, 바이오informatics, 데이터 마이닝 등 다양한 분야에서 정규 표현식 패턴 매칭에 활용
- 기존 자동차 처리 가속기의 한계:
  - **Micron Automata Processor (AP):** DRAM 기반 공간적(spatial) 자동차 처리. 8비트 심볼 기반 1-스트라이드 처리. 상태 수용력 제한 (48K 상태), 대역폭 제한
  - **Cache Automaton (CA):** 온칩 SRAM 기반. 256×256 메모리 서브어레이 사용. 스트라이드 처리 시 높은 면적 오버헤드 (서브어레이 면적이 상태 수에 비례하여 증가)
  - **FPGA 기반 다중 스트라이드:** 낮은 클록 레이트 (0.2~0.24 GHz), 낮은 처리량 (3.47~3.91 Gbps)
- 핵심 문제: **다중 스트라이드(multi-stride) 처리 시 상태 수와 전이 수가 급격히 증가**하여 기존 설계의 면적/에너지 효율성 저하

## 방법론

### 3.1. 4비트 압축 (Squashing)

- 원래 8비트 심볼 매칭을 4비트로 분할
- 각 상태의 매칭 벡터를 4비트 입력에 대해 재설계
- 상태 수 평균 2.52배 증가 (오버헤드)
- **장점:** 더 작은 메모리 서브어레이 사용 가능 (16×16 vs 256×256)

### 3.2. 시간적 스트라이딩 (Temporal Striding)

- 4비트 압축 후 인접 심볼을 결합하여 다중 스트라이드 처리
- 2-스트라이드: 8비트/사이클, 4-스트라이드: 16비트/사이클
- **상태 수 오버헤드:** 4-스트라이드 기준 평균 1.68배 (원래 8비트 대비)
- **전이 수 오버헤드:** 4-스트라이드 기준 평균 3.97배
- 실제 크기 벤치마크(EntityResolution, RandomForest, SPM)는 높은 노드 수로 인해 더 높은 오버헤드

### 3.3. Espresso를 이용한 상태 분할

- 다중 스트라이드 시 거짓 양성(false positive) 매칭 문제 발생
- Espresso (IBM CAD 도구)를 활용하여 최소 상태 분할 수행
- **문제 정의:** Set Covering Problem과 동등 (NP-hard)
- **해결:** Espresso의 휴리스틱으로 Sum Of Product (SOP) 최소화
- 각 분할된 상태는 하나의 캡슐에 매핑되어 거짓 양성 방지

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1. 상태 매칭 서브어레이 (State Matching)

- **캡슐(Capsule) 구조:** 동일 인덱스의 메모리 컬럼을 AND 게이트로 결합
  - 각 컬럼은 4비트 입력을 단일 메모리 행 액세스로 처리
  - 최종 1비트 매칭 결과 = AND 게이트 출력
- **서브어레이 크기:** 16×16 (6T SRAM 셀)
  - CA의 256×256 대비 5.2배 작은 면적
  - 지연 시간: 180ps (CA의 220ps 대비 18% 감소)
- **병렬 처리:** 4-스트라이드 시 16개 캡슐이 동시에 16비트 심볼 처리
- **주파수:** 5 GHz (CA의 3.6 GHz 대비 39% 향상)

### 4.2. 인터커넥트 (Interconnect)

- **풀 크로스바(Full Crossbar) 기반:** 상태 간 전이 연결 지원
- **지역 스위치(Local Switch) + 글로벌 스위치(Global Switch):**
  - 지역 스위치: 256×256, 8T SRAM 셀 (지연: 150ps)
  - 글로벌 스위치: 지역 스위치 간 연결 (지연: 170ps)
- **G4 (Group of Four) 모델:** 4개 지역 스위치 + 1개 글로벌 스위치로 최대 1024 상태 지원
- **유전자 알고리즘(Genetic Algorithm) 기반 배치:**
  - BFS 레이블링의 한계 해결 (장거리 루프 문제)
  - G4 연결 패턴을 고려한 최적 상태 배치
  - 다이어고널 구조 활용으로 자동차 처리의 연결 패턴 최적화

### 4.3. 시스템 통합

- **구성:** 온칩 SRAM 또는 오프칩 메모리 어레이로 구현 가능
- **입력/출력:** 비동기 FIFO (입력 버퍼 2.5KB, 출력 버퍼 512 엔트리)
- **호스트 통신:** 인터럽트 기반 메모리 매핑 I/O 또는 DMA
- **설정:** 컴파일된 비트 스트림을 메모리에 기록하여 설정

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2020HPCA-summarize/impala-algorithm-architecture-co-design-for-in-memory-multi-stride-pattern-matching.md|전체 요약 보기]]
