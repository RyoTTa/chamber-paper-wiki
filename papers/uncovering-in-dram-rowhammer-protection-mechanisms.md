---
tags: [paper, 2024, 2024ISCA, topic/dram, topic/rowhammer]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024ISCA-summarize/uncovering-in-dram-rowhammer-protection-mechanisms.md"
---

# Uncovering In-DRAM RowHammer Protection Mechanisms: A New Methodology, Custom RowHammer Patterns, and Implications

**Venue:** 
**저자:** Hasan Hassan (ETH Zürich), Yahya Can Tuğrul (TOBB University of Economics & Technology), Jeremie S. Kim (ETH Zürich), Victor van der Veen (Qualcomm Technologies Inc.), Kaveh Razavi (ETH Zürich), Onur Mutlu (ETH Zürich)

## 개요

- DRAM 기술 스케일링에 따라 셀 간 간섭이 증가하여 2010년 이후 제조된 대부분의 DRAM 칩에서 RowHammer 교란 오류(disturbance errors)가 발생한다. 공격 행(aggressor row)을 반복 활성화하면 인접 행(victim row)의 비트 플립이 유발되며, 이는 OS 탈취, 웹 브라우저 공격, 클라우드 VM 침해 등 다양한 시스템 보안 위협으로 악용된다.
- DDR3에서 TRH(RowHammer threshold)는 139K, DDR4에서 10K, LPDDR4에서 4.8K까지 급감하며 RowHammer 취약성이 점점 심각해지고 있다.
- DRAM 벤더들은 RowHammer 완화를 위해 TRR(Target Row Refresh) 메커니즘을 구현하고 있으나, 구현 세부사항을 공개하지 않아 보안 보장이 불가능하다. TRRespass 연구는 일부 DDR4 모듈(42개 중 13개)에서 TRR을 우회할 수 있었으나, 나머지 29개 모듈의 TRR 작동 원리와 보안 수준은 불명확했다.
- 보안을 달성하려면 TRR 메커니즘의 내부 작동 방식을 실험적으로 이해하고 체계적으로 평가할 수 있는 방법론이 필요하다.

## 방법론

### 3.1 Row Scout (RS)

- **목적:** TRR-A 실험에 필요한 특정 조건을 만족하는 DRAM 행을 탐색하고 retention time을 프로파일링한다.
- **균일 retention time:** TRR이 여러 victim row를 동시에 refresh하는지 관찰하기 위해, 동일한 retention time을 가진 여러 행(row group)을 찾아야 한다.
- **일관된 retention time:** Variable Retention Time (VRT) 효과 없이 일관된 retention time을 가져야 하며, RS는 각 행의 retention time을 1,000회 검증하여 일관성을 보장한다.
- **데이터 패턴 기반 프로파일링:** 모든 셀에 동일한 데이터 패턴(예: all ones)을 기록한 후 정확한 retention interval을 측정한다.

### 3.2 TRR Analyzer (TRR-A)

- **실험 3단계:**
  1. RS가 제공한 victim row를 초기화하고 aggressor row의 데이터 값을 설정. victim row의 retention time의 절반(T/2) 동안 대기
  2. aggressor row를 hammering하고 REF 명령을 experiment configuration에 따라 발행
  3. 나머지 T/2 동안 대기 후 victim row를 읽고 초기 데이터와 비교하여 비트 플립 여부 확인
- **TRR refresh 감지 원리:** 비트 플립이 없으면 해당 행이 refresh되었음을 의미. regular refresh는 고정된 시간 간격(예: 8K REF commands마다)으로 발생하므로, TRR-induced refresh와 쉽게 구분 가능.
- **유연한 실험 구성:** profiling configuration과 experiment configuration을 통해 다양한 TRR 구현을 분석할 수 있다.

### 3.3 커스텀 RowHammer 패턴 생성

- U-TRR이 밝혀낸 TRR 메커니즘의 세부사항을 기반으로, TRR을 우회하는 맞춤형 RowHammer 접근 패턴을 설계한다.
- 기존 TRRespass의 단순 공격(단순히 aggressor row 수를 늘리는 것)과 달리, TRR의 eviction 정책과 capacity 제한을 정확히 악용하는 정교한 패턴을 사용.
- 45개 DDR4 DRAM 모듈(3개 주요 벤더)에서 기존 패턴보다 훨씬 많은 비트 플립을 유발하는 데 성공.

## 핵심 기여

1. **DRAM 벤더들의 TRR은 보안을 제공하지 않는다:** U-TRR 방법론을 통해 45개 DDR4 모듈 전부에서 TRR을 우회하는 커스텀 RowHammer 패턴을 성공적으로 개발. TRR은 보안-through-obscurity에 의존할 뿐 provable security를 제공하지 않는다.
2. **최초의 TRR 리버스 엔지니어링 방법론:** DRAM의 데이터 보존 실패를 사이드 채널로 활용하는 U-TRR은 TRR 메커니즘의 내부 작동 방식을 체계적으로 밝혀내는 최초의 실험적 방법론이다.
3. **ECC 및 Chipkill의 한계 확인:** 기존 DRAM ECC는 RowHammer 커스텀 패턴으로 인한 다중 비트 플립을 보호할 수 없으며, 강력한 Reed-Solomon 코드는 큰 오버헤드를 수반한다.
4. **향후 연구 방향:** U-TRR은 더 안전한 RowHammer 완화 메커니즘의 개발과 기존 시스템 수준 완화 기법의 보안 평가에 기여할 것으로 기대된다.

## 주요 결과

| 항목 | 세부사항 |
|------|---------|
| **하드웨어 플랫폼** | SoftMC (FPGA 기반 DRAM 테스트 인프라) |
| **FPGA 보드** | Xilinx Virtex UltraScale+ |
| **DRAM 모듈** | 45개 DDR4 SO-DIMM (3개 벤더: Vendor A, B, C) |
| **소프트웨어** | Row Scout (RS), TRR Analyzer (TRR-A) |
| **명령 제어** | DDR4 ACT, PRE, REF 등 명령을 FPGA에서 직접 발행 |
| **실험 온도** | 상온(온도 컨트롤러로 일정 유지) |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]


## 전체 요약

[[../paper-summaries/2024ISCA-summarize/uncovering-in-dram-rowhammer-protection-mechanisms.md|전체 요약 보기]]
