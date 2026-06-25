---
tags: [paper, 2018, 2018MICRO, topic/dram, topic/memory-controller]
venue: "MICRO 2018"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/duplicon-cache-mitigating-off-chip-memory-bank-and-bank-group-conflicts-via-data-duplication.md"
---

# Duplicon Cache: Mitigating Off-Chip Memory Bank and Bank Group Conflicts via Data Duplication

**Venue:** MICRO 2018
**저자:** Ben (Ching-Pei) Lin, Michael B. Healy, Rustam Miftakhutdinov, Philip G. Emma, Yale Patt (University of Texas at Austin, IBM, Intel)

## 개요

DRAM 뱅크 및 뱅크 그룹 충돌은 메모리 집약적 워크로드의 주요 성능 병목이다. Duplicon Cache는 선택적 데이터를 대체 �뱅크 그룹에 복제하여 메모리 컨트롤러가 충돌을 피할 수 있도록 하며, 상용 DRAM 변경 없이 8.3% 성능 향상과 5.6% 에너지 절감을 달성한다.

## 방법론

### 데이터 복제 전략
- **제한적 복제**: 전체 데이터가 아닌 선별된 데이터만 대체 뱅크 그룹에 복제
- 실험结果显示 대체 뱅크 그룹으로의 복제만으로도 완전 복제 대비 대부분의 이득 유지
- 4-way 세트 연관 구조: 홈 뱅크 그룹(m)의 데이터를 대체 �뱅크 그룹(m+1 mod 4)의 4개 뱅크 중 하나에 복제

### 핵심 구성 요소
1. **세트 연관 및 섹터 기반 구조**: 효율적인 복제 데이터 추적
2. **Demand Activates Filtering**: 복제할 행을 식별하는 정책 (DAC 카운터 + Threshold=15)
3. **Usefulness Tracking 및 Probabilistic Replacement**: 유용한 복제 데이터 보호

### 태그 저장소
- 메모리 컨트롤러의 전용 SRAM 테이블 (채널별 142KB)
- Address Tag (9비트) + Valid Columns Mask (128비트) + DAC (4비트) + Useful Bit (1비트)

## 핵심 기여

1. 메모리 컨트롤러에 완전히 구현되는 데이터 복제 캐시 제안
2. 상용 DRAM 변경 불필요 — 메모리 컨트롤러 수정만으로 구현
3. Demand Activates Filtering과 Usefulness Tracking의 시너지 효과 입증
4. 영역 동등 기준선(4.5MB/8MB LLC) 대비 우수한 성능

## 주요 결과

- **성능 향상**: 평균 8.3%, 최대 ~17%
- **에너지 절감**: 평균 5.6%
- **이상치 대비 실현**: 이상적 Duplicon 20.2% → 실제 8.3% (모든 제약 고려)
- **삽입/교체 정책 효과**: Filtering 제거 시 2.1%, Tracking 제거 시 -0.9%, 둘 다 제거 시 -30.7%
- **태그 저장소 비용**: 284KB (비트/바이트 비율이 높으나 uncore 영역에서 수용 가능)
- **DRAM 저장 오버헤드**: 코어당 32MB (전체 16GB의 0.78%)

## 한계점

- 최종 성능 향상(8.3%)은 이상치(20.2%)와 큰 차이 — 냉간 미스, 필터링, 저장소 제한 영향
- 뱅크/스레드 비율이 높은 시스템에서는 효과 감소 가능
- 태그 저장소 면적이 uncore 영역에서 무시할 수 없는 수준

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]: 뱅크/뱅크 그룹 구조와 충돌 문제
- [[paper-wiki/concepts/memory-controller.md|Memory Controller]]: 메모리 컨트롤러에서의 데이터 복제 관리

## 관련 논문 요약

- [paper-summaries/2018MICRO-summarize/duplicon-cache-mitigating-off-chip-memory-bank-and-bank-group-conflicts-via-data-duplication.md]
