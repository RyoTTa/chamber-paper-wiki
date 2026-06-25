---
tags: [paper, 2025, 2025HPCA, topic/cache, topic/dram, topic/rowhammer]
venue: "2025 IEEE International Symposium on High-Performance Computer Architecture (HPCA 2025)"
year: 2025
summary_path: "../paper-summaries/2025HPCA-summarize/chronus-understanding-and-securing-the-cutting-edge-of-dram-read-disturbance-defenses.md"
---

# Chronus: Understanding and Securing the Cutting Edge of DRAM Read Disturbance Defenses

**Venue:** 2025 IEEE International Symposium on High-Performance Computer Architecture (HPCA 2025)
**저자:** Oğuzhan Canpolat, A. Giray Yağlıkçı, Geraldo F. Oliveira, Ataberk Olgun, Oğuz Ergin, Onur Mutlu (ETH Zürich, Bilkent University, SAFARI Research Group)

## 개요

- DRAM 기술 스케일링이 진행되면서 행 간 간섭(read disturbance) 문제가 점점 심각해지고 있으며, RowHammer와 RowPress와 같은 메커니즘이 반복적인 활성화나 긴 활성화 상태를 통해 인접 행의 비트 플립을 유발함
- JEDEC DDR5 표준에 PRAC(Per-Row Activation Counter)가 2024년 4월 업데이트에서 도입되었으나, 보안 및 성능 측면에서 주요 미해결 문제가 존재
- PRAC는 행 닫힘(row closing) 시 카운터를 업데이트하여 DRAM 타이밍 파라미터(tRP, tRC)를 증가시켜 성능 오버헤드를 유발하며, 고정된 수의 예방적 리프레시|RFM 명령으로 wave attack에 취약
- 현재 DRAM 칩의 NRH(RowHammer Threshold)는 약 1K 수준이나, 기술 스케일링으로 향후 64 이하로 감소할 것으로 예상되어 더 강력한 완화 메커니즘이 요구됨
- PRAC+PRFM 조합은 안전한 구성에서 평균 13.6% (최대 40.2%)의 성능 오버헤드를 초래하여 실용성이 부족

## 방법론

### 3.1. Concurrent Counter Update (CCU)

- DRAM 뱅크에 별도의 **카운터 서브어레이(counter subarray)** 를 추가하여 기존 데이터 서브어레이와 물리적으로 분리
- 카운터 업데이트는 **동시적(concurrent)** 으로 수행: 다른 서브어레이에 대한 접근과 동시에 카운터 서브어레이의 값을 감소
- 구현에 사용되는 **감소기(decrementer) 회로** 는 21개 게이트, 96개 트랜지스터로 구성되며, critical path delay가 **0.627 ns**로 tRC(47 ns)보다 훨씬 작음 (Global Foundries 22nm 기술 기반)
- 카운터 서브어레이는 DRAM 셀로 구성되어 read disturbance에 취약하므로, 세 가지 보호 방안 제안:
  1) SRAM 배열에서 활성화 수 추적 및 필요 시 리프레시 (Silver Bullet 기법 유사)
  2) REGA 유사 접근으로 별도 감지 증폭기 배열에서 리프레시
  3) 카운터 서브어레이 내 연속 행 간 guard row 할당 (GuardION/ZebRAM 유사)
- 카운터 서브어레이는 DRAM 뱅크의 0.05%에 해당하여 영역 오버헤드는 **<0.1%** 수준
- 주기적 리프레시(refresh) 시 카운터를 리셋하여 공격 패턴 악용 및 불필요한 예방적 리프레시를 방지

### 3.2. Chronus Back-Off

- PRAC Back-Off의 세 가지 한계를 해결:
  - **L1:** 백오프 트리거 후에도 메모리 컨트롤러가 활성화를 계속할 수 있는 시간 창(tABO_ACT) 존재 → Chronus에서는 백오프 신호가 활성화된 동안 모든 예방적 리프레시를 완료
  - **L2:** 고정된 수의 RFM 명령(NRef) 전송 → Chronus는 마지막으로 NBO를 초과하는 활성화 수를 가진 행이 리프레시될 때까지 동적으로 RFM 명령 수 조절
  - **L3:** DRAM 모듈이 지연 기간(NDelay) 동안 새로운 백오프를 트리거할 수 없음 → Chronus는 지연 기간을 적용하지 않아 공격 가능성을 원천 차단
- 백오프 신호의 레이턴시는 낮아 동적 제어가 가능: RFM 명령의 지속 시간(350 ns)이 메모리 컨트롤러가 alert_n 신호를 인지하고 RFM 전송을 중지하기에 충분
- JEDEC DDR5 표준의 alert_n 핀은 이미 Write CRC 에러 처리 및 PRAC Back-Off에서 저지연으로 사용되므로, Chronus Back-Off 도입에 대한 근본적 제약 없음

### 3.3. 보안 분석

- Chronus의 세 가지 핵심 보안 속성:
  - **P1:** 모든 행의 활성화 수를 정확히 추적 (per-row activation counter)
  - **P2:** 언제든지 백오프를 트리거할 수 있음 (지연 기간 미적용)
  - **P3:** 백오프는 NBO를 초과하는 모든 행이 리프레시될 때까지 유지
- 웨이브 공격(wave attack)에 대한 정밀 분석 수행
- PRAC-N의 경우 NBO=1, PRAC-4 구성에서 NRH=20까지 안전한 임계값 확인
- Chronus는 백오프 지연 기간이 없어 웨이브 공격이 불가능하며, PRAC보다 더 높은 안전성 달성

## 핵심 기여

- Chronus는 PRAC의 두 가지 주요 약점(카운터 업격 지연, wave attack 취약성)을 동시에 해결하는 최초의 메커니즘
- **CCU:** 물리적으로 분리된 카운터 서브어레이에서 동시 카운터 업데이트로 타이밍 파라미터 증가를 방지 (0.627 ns 감소기 회로)
- **Chronus Back-Off:** 동적 예방적 리프레시 수 조절과 지연 기간 미적용으로 wave attack 원천 차단
- NRH=1K(현재 DRAM)에서 **<0.1%** 성능 오버헤드, NRH=20(미래 DRAM)에서도 **<8.3%** 오버헤드로 최고 확장성
- Graphene(28.1%), Hydra(30.6%), PRAC-4(46.1%) 대비 NRH=32에서 **6.8%**로 현저히 낮은 성능 오버헤드
- DRAM 에너지 오버헤드도 낮은 수준(1.47×)으로 실용적
- **의의:** 현재 및 미래 DRAM 칩의 read disturbance 문제를 낮은 영역, 성능, 에너지 비용으로 해결하는 강건하고 효율적인 솔루션을 제시

## 주요 결과

- **시뮬레이션 프레임워크:** Ramulator 2.0 기반 사이클 레벨 시뮬레이션 (PRAC, RFM, 백오프 신호 구현 포함)
- **에너지 평가:** Ramulator 2.0과 통합된 DRAMPower 사용
- **하드웨어 구현:** Global Foundries 22nm 기술 기반 Synopsys Design Compiler로 감소기 회로 검증
- **오픈소스:** 모든 코드와 스크립트를 GitHub (https://github.com/CMU-SAFARI/Chronus)에 공개

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]


## 전체 요약

[[../paper-summaries/2025HPCA-summarize/chronus-understanding-and-securing-the-cutting-edge-of-dram-read-disturbance-defenses.md|전체 요약 보기]]
