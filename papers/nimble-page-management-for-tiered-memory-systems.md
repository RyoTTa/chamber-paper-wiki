---
tags: [paper, 2019, 2019ASPLOS, topic/disaggregation, topic/dram, topic/memory-tiering, topic/virtual-memory]
venue: "24th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '19)"
year: 2019
summary_path: "../paper-summaries/2019ASPLOS-summarize/nimble-page-management-for-tiered-memory-systems.md"
---

# Nimble Page Management for Tiered Memory Systems

**Venue:** 24th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '19)
**저자:** Zi Yan (Rutgers University & NVIDIA), Daniel Lustig (NVIDIA), David Nellans (NVIDIA), Abhishek Bhattacharjee (Yale University)

## 개요

- 현대 컴퓨팅 시스템은 이기종 메모리 시스템(Heterogeneous Memory Systems)으로 점점 변화하고 있으며, HBM, DDR4, 3D XPoint, 분산 메모리(Disaggregated Memory) 등 다양한 특성의 메모리가 혼재하는 구조가 등장
- 기존 Linux의 페이지 마이그레이션 메커니즘은 성능 병목이 심각하여, 4KB 기본 페이지 마이그레이션 시 하드웨어 대역폭의 5% 수준인 40MB/s에 불과 (하드웨어 잠재력 19.2GB/s 대비 95% 미활용)
- Linux는 투명 거대 페이지(THP, Transparent Huge Page)를 마이그레이션할 때 512개의 기본 페이지로 분할한 후 개별 마이그레이션을 수행하여, 추가 오버헤드와 TLB 커버리지 손실 발생
- autoNUMA는 프로파일링을 위해 페이지를 오프라인으로 전환하거나 디스크로 스왑하는 방식을 사용하여, 예측 불가능한 메모리 접근 지연시간과 대역폭 변동을 유발
- 분산 메모리 시스템에서 로컬 메모리가 워크로드 메모리 풋프린트보다 작은 경우, 기존 기법은 성능을 오히려 저하시키는 결과 (551.ppalm, 556.psp, graph500에서 All Remote 대비 열화)

## 방법론

### 3.1. 네이티브 THP 마이그레이션

- 기존 Linux는 THP 마이그레이션 시 512개 기본 페이지로 분할하여 마이그레이션 → TLB 무효화 512회, 커널 작업 512회 발생
- 네이티브 THP 마이그레이션은 2MB 페이지를 분할 없이 직접 마이그레이션하여 커널 오버헤드를 512배 감소
- `mbind()`, `move_pages()`, cpuset/cgroup 등 모든 리소스 관리 요청에서 THP 마이그레이션 지원
- THP 마이그레이션만으로 2.9× 처리량 향상 (750MB/s → 2.15GB/s)

### 3.2. 병렬화된 THP 마이그레이션

- 기존 Linux 페이지 마이그레이션은 싱글스레드로 동작하여 데이터 복사 대역폭 활용도 저조
- 커널 workqueues를 사용하여 여러 보조 스레드가 임의의 물리적 범위 간 데이터 복사
- sysfs 인터페이스를 통해 스레드 수와 병렬화 수준을 동적 구성 가능
- `move_pages()` 시스템 콜에 `MPOL_MF_MT` 플래그 추가하여 마이그레이션별 병렬화 수준 선택 가능
- 2MB THP에서 멀티스레드 복사 시 2.8× 처리량 향상 (단, 4KB 페이지에서는 스레드 시작 오버헤드로 인해 효과 미미)

### 3.3. 동시 다중 페이지 마이그레이션

- 기존 `move_pages()`는 여러 페이지를 마이그레이션할 때 직렬로 처리하여 대역폭 활용도 저조 (Figure 5a)
- 제안 기법: 모든 페이지의 복사 프로세스를 단일 논리적 단계로 통합하여 동시 마이그레이션 수행 (Figure 5b)
- 16개 THP(32MB) 동시 마이그레이션 시, 각 페이지를 per-CPU workqueues에 분배하여 병렬 처리
- THP 마이그레이션 + 동시 마이그레이션 조합으로 네이티브 THP 대비 추가 10-25% 성능 향상

### 3.4. 대칭 교환 (Symmetric Exchange)

- 빠른 메모리로 페이지를 마이그레이션할 때, 해당 위치의 페이지를 느린 메모리로 마이그레이션해야 함
- 기존: 두 개의 단방향 마이그레이션 (할당/해제 포함) → `exchange_pages()` 시스템 콜로 교환 연산 통합
- 할당/해제 오버헤드 제거로 처리량 10-50% 추가 향상
- 512개 2MB THP 교환 시 11.2GB/s 달성 (하드웨어 잠재력 11.7GB/s의 96%)

## 핵심 기여

- 페이지 마이그레이션 처리량을 100MB/s 미만에서 10GB/s 이상으로 개선하여 이기종 메모리 시스템 관리에 적합한 수준으로 향상
- 기존 Linux 인터페이스(active/inactive 리스트)를 재사용하여 광범위한 적용 가능성 확보
- 분산 메모리 시스템에서 End-to-End 40% 성능 향상으로, 단순한 관책과 고성능 마이그레이션의 결합이 이기종 메모리 시스템의 핵심임을 입증
- 일부 최적화 기법이 Linux 메인스트림에 채택되어 실제 시스템에 기여

## 주요 결과

- Linux 커널 v4.14 기반 구현 (23개 파일 변경, 627줄 삽입, 114줄 삭제)
- x86, IBM Power 8, NVIDIA TX1(ARM64) 세 가지 아키텍처에서 포팅 및 평가
- 기존 Linux의 active/inactive 페이지 리스트를 재사용한 저오버헤드 페이지 추적 정책
- 분산 메모리 시스템 에뮬레이션: 두 개의 메모리 노드를 사용하고, memhog로 원격 메모리 대역폭/지연시간 에뮬레이션
- GitHub 오픈소스 공개: https://github.com/ysarch-lab/nimble_page_management_asplos_2019

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2019ASPLOS-summarize/nimble-page-management-for-tiered-memory-systems.md|전체 요약 보기]]
