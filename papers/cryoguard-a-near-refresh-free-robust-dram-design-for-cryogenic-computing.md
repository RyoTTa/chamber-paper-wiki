---
tags: [paper, 2021, 2021ISCA, topic/cache, topic/dram]
venue: "ISCA 2021 (48th Annual IEEE/ACM International Symposium on Computer Architecture)"
year: 2021
summary_path: "../paper-summaries/2021ISCA-summarize/cryoguard-a-near-refresh-free-robust-dram-design-for-cryogenic-computing.md"
---

# CryoGuard: A Near Refresh-Free Robust DRAM Design for Cryogenic Computing

**Venue:** ISCA 2021 (48th Annual IEEE/ACM International Symposium on Computer Architecture)
**저자:** Gyu-Hyeon Lee (Seoul National University), Seongmin Na (Seoul National University), Ilkwon Byun (Seoul National University), Dongmoon Min (Seoul National University), Jangwoo Kim (Seoul National University)

## 개요

- 극저온 컴퓨팅(cryogenic computing, 77K)은 와이어 지연과 누설 전류가 크게 감소하여 성능과 전력 효율을 크게 개선할 수 있는 유망한 기술
- 기존 CLP-DRAM(Cryogenic Low-Power DRAM)은 공급 전압 및 임계 전압을 낮춰 접근 지연시간 34.7% 단축, 전력 90.8% 절감을 달성했으나, 메모리 집약적 워크로드에서 냉각 비용(cooling power)이_DRAM 소비 전력의 9.65배에 달해 전체 전력에서는 RT-DRAM 대비 1.2% 더 높은 소비
- DRAM refresh는 CLP-DRAM 소비 전력의 30.3%를 차지하며, 77K에서 누설 전류가 거의 제거되어 셀 데이터 보존 시간이 최소 20배 이상 증가하므로 refresh 주기를 대폭 늘릴 수 있는 기회 존재
- 그러나 refresh 주기를 단순히 늘리면 row-hammer 취약성이 급격히 증가하여, 일반 워크로드에서도 row-hammer failure가 발생하는 심각한 신뢰성(reliability) 문제가 부각

## 방법론

### 3.1. 극저온 DRAM 특성 분석

- **Data retention time**: 77K에서 누설 전류가 거의 제거되어 최소 보존 시간이 64ms 대비 최소 20배 증가 (실측에서 수초 이상)
- **Row-hammer threshold(RHth)**: 300K에서 DDR4 기준 최소값 11,600이었으나, 150K에서는 8,100으로 오히려 감소 (DDR4 DRAM의 임계 전압 감소로 노이즈 마진이 줄어들기 때문)
- **핵심 관찰(Observation 2)**: 극저온에서 row-hammer threshold는 크게 증가하지 않거나 오히려 감소하여, refresh-free DRAM는 row-hammer에 훨씬 더 취약
- **일반 워크로드에서도 발생**: 77K에서 refresh 주기가 20배 늘어나면 0.05%의 DRAM 행이 RHth를 초과하여 activation → 일반 애플리케이션에서도 row-hammer failure 발생 (Observation 3)

### 3.2. Counter 기반 보호 가이드라인

- **가이드라인 1**: Counter 기반 보호 방식 사용 (In-DRAM, 소프트웨어 기반, 확률 기반 방식은 77K에서 신뢰성 보장 불가)
- **가이드라인 2**: 77K에서 counter 오버헤드 최소화 필수
  - TWiCe (time-window 기반): 300K에서 694kB이나 77K에서 16MB 이상 필요 (L3 캐시 용량과 비슷)
  - CAT (multi-row counter): 300K에서 256kB이나 77K에서 4MB 필요 (16배 증가)
  - 77K에서는 hot row가 급증하여 기존 동적 counter 할당 방식의 오버헤드가 비현실적으로 증가

### 3.3. CryoGuard 최적화 기법

- **SCA (Static Counter Allocation)**: CAT의 동적 트리 기반 할당을 제거하고 균등 할당으로 전환
  - 77K에서 추가 refresh가 69.5% 감소 (warm row로 인한 과도한 counter 분할 방지)
  - Counter 면적이 44.1% 감소 (내부 노드 불필요)
  - Row-hammer 관련 전력 33.1% 절감
- **3T-eDRAM counter**: 극저온에서 SRAM 대비 2배 작은 3T-eDRAM 셀 사용
  - 셀 면적 2.13배 절감, 전체 면적 50% 이상 절감
  - 동적 전력 22.4% 감소, refresh 전력은 관리 가능한 수준 (4.65%)
- **ECC-assisted protection**: DRAM ECC(SECDED)로 단일 비트 오류를 처리하고, 2비트 이상 오류에 대해서만 counter로 보호
  - 77K에서 RHth,2 (2비트 오류 기준) = 20,000으로 RHth,1 (8,100) 대비 2.5배 증가
  - Counter 수를 1024에서 256으로 축소, 면적 79.5% 감소, 전력 48.6% 감소

## 핵심 기여

- **핵심 Contribution**: 극저온(77K) DRAM에서 refresh를 거의 제거하면서도 신뢰성을 보장하는 최초의 종합 솔루션 제시
- **성능**: CLP-DRAM 대비 전체 전력(냉각 포함) 25.9% 절감 달성
- **신뢰성**: 일반 워크로드에서도 발생하는 row-hammer failure를 counter 기반으로 완벽 보호
- **실용성**: RT-CAT 대비 14.2% 낮은 counter 면적으로 실용적인 하드웨어 오버헤드
- **의의**: row-hammer 보호가 300K에서는 "보안" 문제였으나, 77K에서는 "신뢰성" 문제로 전환됨을 최초로 규명하고 해결

## 주요 결과

| 항목 | 내용 |
|------|------|
| **구현 언어** | Chisel3 (Scala 기반 HDL) → Verilog 변환 → Synopsys Design Compiler 합성 |
| **기술 노드** | TSMC 40nm |
| **DRAM 구성** | 256GB DDR4 (32 DIMM, 1024 bank) |
| **Counter 수/bank** | CryoGuard: 256개 (SCA + 3T-eDRAM + ECC) |
| **DRAM 사양** | DDR4-2400, 접근 에너지 0.51nJ/access, 정적 전력 1.29mW |
| **CPU 모델** | Intel i7-6700 기반 |
| **시뮬레이터** | gem5 + custom row-hammer 시뮬레이터 |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2021ISCA-summarize/cryoguard-a-near-refresh-free-robust-dram-design-for-cryogenic-computing.md|전체 요약 보기]]
