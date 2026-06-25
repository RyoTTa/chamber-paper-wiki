---
tags: [paper, 2020, 2020ISCA, topic/dram]
venue: "2020 ACM/IEEE 47th Annual International Symposium on Computer Architecture (ISCA '20)"
year: 2020
summary_path: "../paper-summaries/2020ISCA-summarize/clr-dram-a-low-cost-dram-architecture-enabling-dynamic-capacity-latency-trade-off.md"
---

# CLR-DRAM: A Low-Cost DRAM Architecture Enabling Dynamic Capacity-Latency Trade-Off

**Venue:** 2020 ACM/IEEE 47th Annual International Symposium on Computer Architecture (ISCA '20)
**저자:** Haocong Luo (ShanghaiTech University), Taha Shahroodi (ETH Zürich), Hasan Hassan (ETH Zürich), Minesh Patel (ETH Zürich), A. Giray Yağlıkçı (ETH Zürich), Lois Orosa (ETH Zürich), Jisung Park (ETH Zürich), Onur Mutlu (ETH Zürich)

## 개요

- DRAM은 현대 컴퓨팅 시스템의 주 메모리 기술이지만, 높은 접근 지연 시간이 많은 워크로드의 성능을 저하시킴
- 지난 20년 동안 상용 DRAM 칩의 저장 용량은 100배 이상 증가했으나(128Mb → 16Gb), 접근 지연 시간은 16.7%만 감소
- 현대 프로세서는 DRAM 데이터 접근에 수백 개의 클록 사이클을 소모하여 시스템 수준 성능 병목 발생
- 기존 기술들의 한계:
  - 고밀도 최적화 DRAM: 높은 저장 용량을 제공하지만 긴 접근 지연 시간
  - 저지연 최적화 DRAM: 낮은 지연 시간을 제공하지만 상당히 낮은 저장 용량
  - 이종 DRAM 아키텍처 [7,13,55,98]: 고정된 크기의 저지연 영역을 제공하나, 설계 시점에서 용량-지연 트레이드오프가 고정
- 핵심 문제: 기존 DRAM 아키텍처는 설계 시점에 용량-지연 트레이드오프를 고정하므로, 동적으로 변하는 워크로드 요구사항에 적응 불가

## 방법론

### 3.1. 최대 용량 모드 (Max-capacity Mode)

- 기존 오픈 비트라인(open-bitline) DRAM 아키텍처와 동일하게 작동
- 각 DRAM 셀이 개별 센스 앰플리피어에 연결되어 높은 저장 밀도 유지
- 밀도 최적화 상용 DRAM 칩과 동일한 스토리지 밀도 제공
- 일반적인 메모리 용량이 필요한 워크로드에 적합

### 3.2. 고성능 모드 (High-performance Mode)

- 인접한 두 개의 DRAM 셀이 하나의 논리 셀로 결합
- 두 셀이 하나의 논리 센스 앰플리피어에 의해 구동되어 저지연 접근 가능
- 센스 앰플리피어의 설계 특성 활용: 두 셀의 충전/방전 상태를 동시에 검출
- 지연 시간 최적화가 필요한 워크로드에 적합

### 3.3. 격리 트랜지스터 구현

- 각 DRAM 서브어레이(subarray)의 비트라인을 따라 격리 트랜지스터 추가
- 격리 트랜지스터를 통해 DRAM 셀과 센스 앰플리피어 간 연결을 동적으로 제어
- 행(row) 수준의 미세한 Granularity에서 모드 전환 가능
- 기존 오픈 비트라인 아키텍처를 기반으로 하므로 구현 비용 최소화

### 3.4. 동적 모드 전환 메커니즘

- 워크로드의 메모리 용량 및 지연 시간 요구사항에 따라 동적 전환
- 운영 체제(OS) 또는 하드웨어 매니저에 의해 결정
- 런타임 시 워크로드 특성 분석 후 최적 모드 선택
- 레지스터 설정을 통해 행별 모드 전환 제어

## 핵심 기여

- **핵심 기여:** 동적으로 용량-지연 트레이드오프를 조정할 수 있는 최초의 DRAM 아키텍처 제안
- **성능 향상:** 기존 대비 18.6% 성능 향상, 29.7% 에너지 절감
- **연구 방향 제시:** 워크로드 적응형 메모리 시스템 설계의 새로운 패러다임 제시
- **실용성:** 기존 DRAM 아키텍처를 기반으로 하므로 상용화 가능성 높음
- **의의:** 정적 용량-지연 트레이드오프의 한계를 극복하고, 런타임 적응형 메모리 시스템의 기반 마련

## 주요 결과

- **구현 언어:** Verilog (하드웨어 설명 언어)
- **기술 노드:** 32nm 공정 기반 시뮬레이션
- **구성 요소:**
  - 격리 트랜지스터: 각 서브어레이당 추가 트랜지스터 수
  - 센스 앰플리피어 수정: 이중 모드 지원을 위한 확장
  - 제어 레지스터: 행별 모드 설정을 위한 메모리 맵드 레지스터
- **오버헤드:** 격리 트랜지스터 추가에 따른 면적 증가 및 전력 소비

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2020ISCA-summarize/clr-dram-a-low-cost-dram-architecture-enabling-dynamic-capacity-latency-trade-off.md|전체 요약 보기]]
