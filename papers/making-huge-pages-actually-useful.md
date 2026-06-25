---
tags: [paper, 2018, 2018ASPLOS, topic/virtual-memory, topic/memory-management]
venue: "ASPLOS 2018"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/making-huge-pages-actually-useful.md"
---

# Making Huge Pages Actually Useful

**Venue:** ASPLOS 2018
**저자:** Ashish Panwar, Aravinda Prasad, K. Gopinath (Indian Institute of Science)

## 개요

Huge pages는 주소 변환 오버헤드를 줄이지만, 단편화 문제로 인해 제대로 활용되지 못함. Linux 커널에서 huge pages 사용 시 높은 CPU 활용률, 지연시간 스파이크 등의 문제가 발생하며, 데이터베이스 서버들은 huge pages를 비활성화한 상태로 출시됨.

Illuminator는 unmovable 페이지를 명시적으로 추적하여 불필요한 작업을 제거하는 메모리 관리 프레임워크로, compaction 비용 최대 99% 감소, 애플리케이션 성능 최대 2.3배 향상, MySQL 최대 지연시간 30배 감소를 달성.

## 방법론

### unmovable 페이지 추적 메커니즘
- Linux 커널에 소소한 변경을 통해 모든 unmovable 페이지를 명시적으로 추적
- 페이지 할당자에게 unmovable 페이지 클러스터링 정보 제공
- 메모리 컴팩션 서브시스템에게 LIU 마이그레이션 회피 정보 제공

### fragmentation via pollution 해결
- unmovable 페이지가 메모리 연속성을 불필요하게 오염시키는 문제 해결
- 페이지 할당자가 unmovable 페이지를 효율적으로 클러스터링

### LIU 마이그레이션 회피
- huge pages 할당 시 불필요한 페이지 마이그레이션으로 인한 지연시간 문제 해결
- 컴팩션 비용을 최대 99%까지 감소

## 핵심 기여

1. Linux 커널의 기존 메모리 관리 정책이 huge pages 관련 성능 이상의 근본 원인임을 규명
2. Illuminator를 통한 단편화 효과적 완화 및 huge pages 활용도 향상
3. 네이티브 및 가상화 시스템 모두에서의 significant 성능 개선

## 주요 결과

- 컴팩션 비용 최대 99% 감소
- 애플리케이션 성능 최대 2.3배 향상
- MySQL 데이터베이스 서버 최대 지연시간 30배 감소
- 다양한 워크로드에서 일관된 성능 개선

## 한계점

- Linux 커널 기반 구현으로 다른 OS에서의 적용 가능성 미검증
- 특정 워크로드에서의 효과가 다른 워크로드보다 클 수 있음
- 가상화 환경에서의 추가 오버헤드 고려 필요

---

**Related Concepts:** [[paper-wiki/concepts/huge-pages|Huge Pages]], [[paper-wiki/concepts/memory-management|Memory Management]], [[paper-wiki/concepts/address-translation|Address Translation]]