---
tags: [paper, 2021, 2021MICRO, topic/dram]
venue: "54th Annual IEEE/ACM International Symposium on Microarchitecture (MICRO 2021)"
year: 2021
summary_path: "../paper-summaries/2021MICRO-summarize/harp-practically-and-effectively-identifying-uncorrectable-errors-in-memory-chips-that-use-on-die-error-correcting-codes.md"
---

# HARP: Practically and Effectively Identifying Uncorrectable Errors in Memory Chips That Use On-Die Error-Correcting Codes

**Venue:** 54th Annual IEEE/ACM International Symposium on Microarchitecture (MICRO 2021)
**저자:** Minesh Patel (ETH Zürich), Geraldo F. Oliveira (ETH Zürich), Onur Mutlu (ETH Zürich)

## 개요

- 현대 메모리 기술(DRAM, PCM, STT-RAM)은 공정 미세화로 인해 **오류율이 지속적으로 증가**하며, 이는 신뢰성, 제조 수율, 성능/에너지 효율에 큰 영향을 미침.
- 메모리 제조사는 공정 미세화를 유지하면서 신뢰성을 유지하기 위해 **온다이 ECC(on-die ECC)**를 채택하고 있으며, LPDDR4, DDR5, STT-RAM 등에서 이미 광범위하게 사용.
- **온다이 ECC는 메모리 칩 외부(메모리 컨트롤러)에서 오류가 어떻게 보이는지를 변경**하여, 기존 에러 프로파일링 기법에 세 가지 핵심 과제를 제기:
  1. **에러 프로파일러가 식별해야 하는 위험 비트(at-risk bits)의 수가 지수적으로 증가**
  2. **개별 위험 비트의 식별이 더 어려워짐**
  3. **위험 비트를 쉽게 식별하도록 설계된 일반적인 메모리 데이터 패턴이 간섭**
- repair 메커니즘은 에러 프로파일(error profile)을 기반으로 위험 비트를 식별하고 수리하지만, 온다이 ECC 하에서의 효과적인 프로파일링 알고리즘이 부재.

## 방법론

### 3.1. 온다이 ECC가 제기하는 세 가지 과제

**과제 1: 위험 비트 수의 지수적 증가**
- 온다이 ECC가 없을 때: 단일 raw bit error는 단일 출력 비트 오류로 나타남.
- 온다이 ECC 있을 때: 동일한 raw bit error가 **ECC 워드 내 여러 출력 비트에 영향**을 미칠 수 있음.
- 특히 미보정 에러(DUE) 상황에서 간접 오류로 인해 위험 비트 수가 **지수적으로 증가**.

**과제 2: 개별 위험 비트 식별 어려움**
- 온다이 ECC의 인코딩/디코딩 과정이 출력에서 관찰되는 에러 패턴을 변경.
- 동일한 raw error가 온다이 ECC의 보정 능력에 따라 **다양한 출력 패턴**으로 나타남.
- 메모리 컨트롤러 관점에서 개별 비트의 에러 원인 추적이 어려워짐.

**과제 3: 데이터 패턴 간섭**
- 기존 프로파일링 기법은 특정 데이터 패턴을 사용하여 위험 비트를 촉발.
- 온다이 ECC가 이러한 패턴을 인코딩하면서 **패턴의 효과를 상쇄**.

### 3.2. HARP의 핵심 설계

- **단계 1 - 직접 오류 위험 비트 식별:**
  - 온다이 ECC 메커니즘에 **소규모 수정**을 추가하여 직접 오류를 식별.
  - 기존 액티브 프로파일링 기법을 온다이 ECC 환경에서 적용 가능하도록 adapting.

- **단계 2 - 간접 오류 위험 비트 식별:**
  - 메모리 컨트롤러 내에 **보조 ECC(secondary ECC)** 배치.
  - 보조 ECC의 보정 능력 ≥ 온다이 ECC의 보정 능력.
  - 온다이 ECC가 미보정 에러를 반환할 때, 보조 ECC가 간접 오류를 안전하게 감지하고 식별.

- **하이브리드 접근의 장점:**
  - 액티브 프로파일링(직접 오류) + 리액티브 프로파일링(간접 오류) 결합.
  - 온다이 ECC의 보정 능력이라는 구조적 제약을 활용하여 효율성 극대화.

## 핵심 기여

- **핵심 기여:** 온다이 ECC를 사용하는 메모리 칩에서 효과적인 에러 프로파일링을 가능하게 하는 HARP 알고리즘 제안.
- **성능:** 기존 프로파일링 알고리즘 대비 **최대 62.1% 더 빠른 위험 비트 커버리지**, **3.7× 더 빠른 에러 식별**.
- **실용성:** 온다이 ECC의 구조적 제약(세 가지 과제)을 체계적으로 분석하고 해결.
- **범용성:** DRAM, PCM, STT-RAM 등 온다이 ECC를 사용하는 다양한 메모리 기술에 적용 가능.
- **의의:** 메모리 공정 미세화에 따른 오류 증가 문제를 해결하기 위한 에러 프로파일링의 실용적 기반을 마련.

## 주요 결과

- **시뮬레이션 기반 평가:** 메모리 컨트롤러와 온다이 ECC를 모델링하는 시뮬레이터.
- **에러 모델:** 다양한 raw per-bit error probability(0.25~0.75)에서 성능 평가.
- **Baseline 알고리즘:** 2개의 최신 액티브 프로파일링 알고리즘과 비교.
- **repair 메커니즘:** 비트그레뉼리티 수리(bit-granularity repair) 통합 평가.
- **평가 지표:** 위험 비트 커버리지 속도, 전체 비트 오류율(BER) 영향.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2021MICRO-summarize/harp-practically-and-effectively-identifying-uncorrectable-errors-in-memory-chips-that-use-on-die-error-correcting-codes.md|전체 요약 보기]]
