---
tags: [paper, 2025, 2025HPCA, topic/pim, topic/interconnect]
venue: "HPCA 2025"
year: 2025
summary_path: "../paper-summaries/2025HPCA-summarize/pimnet-a-domain-specific-network-for-efficient-collective-communication-in-scalable-pim.md"
---

# PIMnet: A Domain-Specific Network for Efficient Collective Communication in Scalable PIM

**Venue:** HPCA 2025
**저자:** Hyojun Son, Gilbert Jonatan, Xiangyu Wu, Haeyoon Cho (KAIST); Kaustubh Shivdikar, David Kaeli (Northeastern University); José L. Abellán (Universidad de Murcia); Ajay Joshi (Boston University)

## 개요

Processing-in-Memory (PIM)은 메모리 근처에서 연산을 수행하여 메모리 병목을 해결하지만, 모든 상용 PIM 시스템(UPMEM, Samsung HBM FIM, SK Hynix GDDR PIM)에서 각 연산 유닛은 로컬 메모리에만 접근 가능하며, 원격 메모리 접근은 호스트 CPU를 통해야 한다. 이로 인해 집합 통신(collective communication)이 호스트 CPU 대역폭에 의해 제한되어 PIM 확장성이 저해된다.

PIMnet은 PIM 뱅크 간 직접 연결을 제공하는 도메인 특화 네트워크로, 호스트 CPU를 통한 간접 통신을 제거하여 집합 통신 성능을 최대 85배 향상시킨다.

## 방법론

- **다중 계층 네트워크 구조:** Inter-bank (칩 내), Inter-chip (DIMM 내), Inter-rank (채널 내)의 3계층으로 DRAM 패키징 계층을 매칭
- **PIM 제어 통신 스케줄링:** 집합 통신의 deterministic 패턴을 활용하여 사전 스케줄링 기반 통신으로 버퍼/arbitrator 하드웨어 제거
- **대역폭 병렬성:** 여러 PIM 뱅크/칩 간 병렬 통신으로 성능 확장
- **설계 제약:** DRAM 공정의 제한된 로직/와이어 자원 → 저-radix 링 네트워크, 하드웨어 arbitratrion 없음

## 핵심 기여

- PIM 아키텍처의 근본적 확장성 병목(호스트 CPU 통신)을 해결하는 최초의 PIM 특화 도메인 네트워크
- DRAM 패키징 계층을 매칭하는 다중 계층 네트워크 토폴로지
- Deterministic 통신 패턴 기반 PIM 제어 스케줄링으로 최소 하드웨어 오버헤드

## 주요 결과

- 집합 통신 AllReduce: 최대 **85배** 가속
- All-to-All: Software(Ideal) 대비 **2배** 성능 향상 (256 DPU)
- 실제 애플리케이션: **11.8배** 성능 향상
- 확장성: Baseline PIM/Software(Ideal)은 64 DPU 이상에서 포화; PIMnet은 성능 확장 유지

## 한계점

- 동일 메모리 채널 내 PIM 뱅크만 직접 연결 (256 DPU까지); 멀티 채널 간 통신은 여전히 호스트 CPU 필요
- DRAM 공정 기반의 제한된 로직/와이어 자원으로 일반-purpose 네트워크 구현 불가

## 관련 개념

- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/interconnect.md|Interconnect]]

## 전체 요약

[[../paper-summaries/2025HPCA-summarize/pimnet-a-domain-specific-network-for-efficient-collective-communication-in-scalable-pim.md|전체 요약 보기]]
