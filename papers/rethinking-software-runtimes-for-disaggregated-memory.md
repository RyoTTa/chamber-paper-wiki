---
tags: [paper, 2021, 2021ASPLOS, topic/cache, topic/disaggregation, topic/dram, topic/virtual-memory]
venue: "ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS) 2021"
year: 2021
summary_path: "../paper-summaries/2021ASPLOS-summarize/rethinking-software-runtimes-for-disaggregated-memory.md"
---

# Rethinking Software Runtimes for Disaggregated Memory

**Venue:** ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS) 2021
**저자:** Irina Calciu (VMware Research), M. Talha Imran (Penn State University), Ivan Puddu (ETH Zürich), Sanidhya Kashyap (EPFL), Hasan Al Maruf (University of Michigan), Onur Mutlu (ETH Zürich), Aasheesh Kolli (Penn State University/Google)

## 개요

- 현대 데이터센터에서 메모리 활용률이 약 65% 수준으로 정체되어 있으며, 피크 수요에 대비한 과잉 프로비저닝으로 인한 비효율이 심각
- 모놀리식 서버 모델에서 컴퓨팅 리소스와 메모리가 강하게 결합되어 있어, 하드웨어 장애 시 전체 서버가 중단되고 인프라 업그레이드가 빈번하게 필요
- 분산 메모리(Disaggregated Memory)는 메모리와 컴퓨팅의 독립적 스케일링을 통해 이러한 문제를 해결할 수 있으나, 애플리케이션의 효율적인 도입이 어려움
- 기존 소프트웨어 런타임(Infiniswap, LegoOS 등)은 가상 메모리에 의존하여 원격 메모리를 투명하게 제공하지만, 가상 메모리는 원래 저지연도나 세밀한 접근을 위해 설계되지 않음
- 가상 메모리 기반 접근의 첫 번째 한계: 페이지 폴트를 통한 원격 데이터 감지로 인해 높은 오버헤드 발생 (네트워크 레이턴시를 초과하는 페이지 폴트 처리 시간)
- 가상 메모리 기반 접근의 두 번째 한계: 페이지 단위(4KB 이상) 데이터 추적로 인한 더티 데이터 증폭(Dirty Data Amplification) - 앱이 각 페이지에서 64개 캐시라인 중 1-8개만 기록하는데도 전체 페이지가 전송됨
- 분석 결과, 4KB 페이지 기준으로 2X~31X의 더티 데이터 증폭 발생
- 기존 시스템 중 일부는 페이지 폴트를 피하고 객체 단위로 작업하지만, 애플리케이션 수정이 필요하여 투명성(Transparency)을 희생

## 방법론

### 3.1. 시스템 아키텍처 개요
- Kona는 분산 메모리를 위한 새로운 소프트웨어 런타임으로, 가상 메모리의 세 가지 핵심 함수를 캐시 일관성 기반으로 재구현
- 로컬 메모리 계층: CMem(로컬 DRAM), FMem(NUMA 메모리), 원격 메모리
- 하드웨어 캐시 일관성 프로토콜을 통해 캐시라인 단위로 메모리 접근 추적
- 페이지 폴트를 사용하지 않고 원격 데이터 접근을 감지하는 CachingHandler 컴포넌트 구현

### 3.2. 원격 데이터 캐싱 (Fetching Remote Data)
- 기존: 페이지 폴트를 통해 원격 데이터 접근 감지 → 높은 레이턴시
- Kona: 캐시 일관성 프로토콜을 통해 원격 접근을 하드웨어가 자동으로 감지
- KCacheSim 시뮬레이션 결과: 25% 데이터 캐싱 시 LegoOS 대비 1.7X, Infiniswap 대비 5X 낮은 AMAT(Average Memory Access Time) 달성
- 캐시 블록 크기 4KB 사용 (메타데이터 관리 간소화를 위한 페이지 단위)
-associativity는 전체 레이턴시에 큰 영향 미치지 않음

### 3.3. 더티 데이터 추적 (Tracking Dirty Data)
- 기존: 페이지 쓰기 보호(Write-Protection)를 통한 더티 페이지 추적 → 첫 쓰기 시 페이지 폴트 발생
- Kona: 캐시라인 단위로 더티 데이터 추적 → 페이지 폴트 불필요
- 캐시라인 64바이트 단위로 변경사항 추적으로 더티 데이터 증폭 대폭 감소
- 원격 메모리로의 데이터 전송 시 더티 캐시라인만 전송 (전체 페이지 전송 불필요)

### 3.4. 캐시 페이지 제거 (Evicting Cached Pages)
- 기존: 페이지를 Not Present로 표시하고 TLB 플러시 필요 → 높은 오버헤드
- Kona: 캐시라인 단위 제거로 TLB 플러시 불필요
- FMem에서 원격 메모리로 직접 데이터 복사 가능 (CMem 경유 불필요)
- NUMA 페널티 회피 가능

### 3.5. 시뮬레이션 및 구현 도구
- Kona-VM: 가상 메모리 기반 구현 (기존 시스템과 비교를 위한 baseline)
- KCacheSim: 원격 데이터 캐싱 시뮬레이터
- 실제 RDMA 하드웨어(100Gbps RoCE)에서 측정된 지연도 기반 시뮬레이션
- CloudLab에서의 실험을 통한 검증

## 핵심 기여

- 가상 메모리는 분산 메모리를 위한 적절한 메커니즘이 아님: 페이지 폴트 오버헤드와 페이지 단위 더티 데이터 추적의 근본적 한계
- 캐시 일관성이 분산 메모리에 더 적합한 하드웨어 프리미티브를 제공: 캐시라인 단위 투명한 접근 추적, 페이지 폴트 제거
- Kona는 가상 메모리 기반 시스템 대비 AMAT 1.7-5X 향상, 더티 데이터 증폭 2-10X 감소라는 실질적 성능 향상 달성
- 애플리케이션 수정 불필요(투명성 유지)하면서도 가상 메모리의 한계를 극복하는 원리 있는 접근법 제시
- CXL 기반 플랫폼의 발전과 함께 캐시 일관성 기반 분산 메모리 런타임의 실용화 가능성 입증
- 데이터센터 메모리 활용률 향상과 비용 절감에 기여할 수 있는 기반 연구

## 주요 결과

- 구현 언어: C/C++
- 하드웨어 요구사항: 캐시 일관성 지원 FPGA 플랫폼(미래 CXL 기반 플랫폼 예상)
- 네트워크: Mellanox ConnectX5 카드, 100Gbps RoCE 스위치
- 서버: Skylake 듀얼 프로세서(2.2GHz)
- 소프트웨어 구성요소: CachingHandler, DirtyTracker, EvictionManager
- 사용자 공간 페이지 폴트 처리(Infiniswap 방식)와의 호환성

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2021ASPLOS-summarize/rethinking-software-runtimes-for-disaggregated-memory.md|전체 요약 보기]]
