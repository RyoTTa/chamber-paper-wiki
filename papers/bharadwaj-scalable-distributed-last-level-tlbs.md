---
tags: [paper, virtual-memory, tlb, network-on-chip, scalability]
venue: MICRO 2018
year: 2018
summary_path: paper-summaries/2018MICRO-summarize/scalable-distributed-last-level-tlbs-using-low-latency-interconnects.md
---

# Scalable Distributed Last-Level TLBs Using Low-Latency Interconnects

## 개요

- 공유 TLB의 높은 히트율과 프라이빗 L2 TLB의 낮은 접근 시간을 결합하는 NOCSTAR 인터커넥트
- 분산 슬라이스 + 경량 단일 사이클 인터커넥트로 TLB 조회 지연시간 감소
- TLB 접근의 단순하고 예측 가능한 패턴을 활용한 맞춤형 인터커넥트 설계

## 방법론

- **분산 슬라이스**: 모놀리식 공유 TLB를 여러 작은 슬라이스로 분산
- **NOCSTAR 인터커넥트**: 최대 16hop까지 한 사이클에 동시 중재
  - HPCmax=4/8/16 설정으로 동시 중재 링크 수 조정
- **Invalidation Leader**: 특정 코어만 공유 TLB 슬라이스에 무효화 신호를 중계하여 혼잡 방지
- **페이지 테이블 워크**: 미스 메시지를 요청 노드로 반환하여 처리

## 핵심 기여

- NOCSTAR: 공유 TLB의 높은 히트율과 프라이빗 L2 TLB의 낮은 접근 시간을 결합하는 경량 인터커넥트
- 단일 사이클 멀티홉 통신으로 TLB 조회 지연시간 대폭 절감
- Invalidaton Leader 메커니즘으로 TLB Shootdown 효율적 처리

## 주요 결과

- 모놀리식/분산 방식보다 유의미한 지연시간 감소
- 에너지 소비 절감 (지연시간 절감 → 에너지 절감으로 전환)
- 코어 수 증가에 따른 TLB 지연시간 증가가 모놀리식 방식보다 적음
- 높은 침투율에서도 메시 인터커넥트보다 낮은 지연시간

## 한계점

- Invalidaton Leader 수 설정에 대한 튜닝 필요
- 특정 워크로드에서만 큰 효과 발휘 가능
- 하드웨어 구현 복잡도 (동시 중재 로직)

## 관련 개념

- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]
- [[paper-wiki/concepts/cache.md|Cache]]
