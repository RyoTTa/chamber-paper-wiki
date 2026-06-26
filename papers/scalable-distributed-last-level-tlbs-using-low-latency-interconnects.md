---
tags: [paper, 2018, 2018MICRO, topic/cache, topic/disaggregation, topic/virtual-memory]
venue: "MICRO 2018 (51st Annual IEEE/ACM International Symposium on Microarchitecture)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/scalable-distributed-last-level-tlbs-using-low-latency-interconnects.md"
---

# Scalable Distributed Last-Level TLBs Using Low-Latency Interconnects

**Venue:** MICRO 2018 (51st Annual IEEE/ACM International Symposium on Microarchitecture)
**저자:** Srikant Bharadwaj (Georgia Institute of Technology / AMD Research), Guilherme Cox (Rutgers University), Tushar Krishna (Georgia Institute of Technology), Abhishek Bhattacharjee (Rutgers University)

## 개요

- 빅 데이터 워크로드가 현대 컴퓨터 시스템에 효율적인 가상-물리 주소 변환 도전 과제 제기
- Translation Lookaside Buffers (TLBs)는 빠른 주소 변환을 위한 핵심 구성요소
- TLB 성능은 세 가지 속성에 의존: 접근 시간(access time), 히트율(hit rate), 미스 패널티(miss penalty)
- 최근 연구들은 하드웨어 전용 또는 하드웨어-소프트웨어 공동 설계 접근법으로 TLB 히트율을 개선
- **핵심 문제**: 마지막 수준(last-level) 공유 TLB의 높은 접근 시간이 효과를 저해
- 모놀리식 공유 TLB: 높은 히트율이지만 높은 접근 시간
- 프라이빗 L2 TLB: 낮은 접근 시간이지만 낮은 히트율
- 기존 메시 메시 기반 분산 TLB: 인터커넥트 지연으로 원격 슬라이스 접근 시 추가 지연 발생

## 방법론

### 3.1. 분산 TLB 슬라이스 구조

- 모놀리식 공유 TLB를 여러 작은 슬라이스로 분산
- 각 슬라이스는 특정 가상 페이지 번호 범위를 담당
- 하위 비트 기반 세트 인덱싱으로 슬라이스 선택
- LRU 교체 정책 사용

### 3.2. NOCSTAR 인터커넥트 (Fig. 8)

- **단일 사이클 멀티홉 통신**: 최대 16hop까지 한 사이클에 동시 중재
  - HPCmax=4: 최대 4링크 동시 중재
  - HPCmax=8: 최대 8링크 동시 중재
  - HPCmax=16: 최대 16링크 동시 중재
- **동시 중재(Simultaneous Arbitration)**: 여러 링크를 동시에 중재하여 멀티홉 지연 최소화
- **제어 비용**: 모놀리식/분산 방식보다 약간 높지만, 지연시간 절감으로 전체 에너지 절약 달성

### 3.3. 페이지 테이블 워크 처리

- 원격 슬라이스 미스 시 두 가지 옵션:
  1. 미스 메시지를 요청 노드로 반환하여 페이지 테이블 워크 수행
  2. 원격 노드 자체에서 페이지 테이블 워크 수행
- NOCSTAR는 옵션 1 채택 (원격 노드 혼잡 방지)

### 3.4. TLB Shootdown 처리 (Fig. 9)

- OS가 페이지 테이블 엔트리를 수정할 때 IPI로 다른 코어를 일시 정지
- **Invalidation Leader 지정**: 특정 코어만 공유 TLB 슬라이스에 무효화 신호를 중계
  - 모든 코어가 무효화 신호를 보내면 특정 슬라이스가 혼잡
  - 리더 코어만 중계하도록 설계하여 혼잡 방지
- 리더 수: 코어 수보다 훨씬 적되, 메시지 혼잡이 없는 적절한 수준

### 3.5. 삽입/교체 정책

- L1/L2 TLB는 가상 페이지 번호의 하위 비트를 사용한 모듈로 인덱싱
- LRU 교체 정책 사용
- 대부분 포용적(mostly-inclusive) 다중 수준 TLB (백-인バリ데이션 불필요)

## 핵심 기여

- NOCSTAR는 공유 TLB의 높은 히트율과 프라이빗 L2 TLB의 낮은 접근 시간을 결합하는 경량 인터커넥트
- 단일 사이클 멀티홉 통신으로 TLB 조회 지연시간을 크게 감소
- TLB 접근의 단순하고 예측 가능한 패턴을 활용한 맞춤형 인터커넥트 설계
- 빅 데이터 워크로드에서 메모리 변환 성능을 크게 향상시키는 실용적인解决方案

## 주요 결과

| 항목 | 세부사항 |
|------|---------|
| **시뮬레이터** | Simics 기반 사이클 정확 시뮬레이터 |
| **시스템** | Intel Haswell, Ubuntu Linux 4.14, 투명 슈퍼페이지 |
| **TLB 구성** | L1: 64 엔트리 4-way, L2: 512-2048 엔트리 8-way |
| **인터커넥트** | NOCSTAR, 모놀리식, 분산 방식 비교 |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/scalable-distributed-last-level-tlbs-using-low-latency-interconnects.md|전체 요약 보기]]
