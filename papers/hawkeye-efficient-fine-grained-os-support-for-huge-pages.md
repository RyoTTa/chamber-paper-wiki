---
tags: [paper, 2019, 2019ASPLOS, topic/cache, topic/dram, topic/virtual-memory]
venue: "2019 Architectural Support for Programming Languages and Operating Systems (ASPLOS '19)"
year: 2019
summary_path: "../paper-summaries/2019ASPLOS-summarize/hawkeye-efficient-fine-grained-os-support-for-huge-pages.md"
---

# HawkEye: Efficient Fine-grained OS Support for Huge Pages

**Venue:** 2019 Architectural Support for Programming Languages and Operating Systems (ASPLOS '19)
**저자:** Ashish Panwar (Indian Institute of Science), Sorav Bansal (Indian Institute of Technology Delhi), K. Gopinath (Indian Institute of Science)

## 개요

- 현대 애플리케이션의 대규모 메모리 사용으로 주소 변환 오버헤드(address translation overhead)가 핵심 병목으로 부상. 다단계 TLB와 페이지 워크 캐시를 지원하는 아키텍처에서 적절한 페이지 크기 결정이 OS 설계의 중요한 과제.
- 기존 Huge Page 관리 시스템의 한계:
  - **Linux THP:** 동기식 제로잉(synchronous page-zeroing)으로 페이지 폴트 지연 시간이 극대화됨. base page(4KB) 제로잉에 전체 폴트 시간의 25%가 소요되지만, huge page(2MB)에서는 **97%**로 증가.
  - **FreeBSD:** 모든 base page가 할당될 때까지 huge page 승격을 연기하여 메모리 블로트는 줄이지만, MMU 오버헤드 증가.
  - **Ingens:** FMFI(Free Memory Fragmentation Index) 기반 적응형 전략이지만, 공격적 승격 단계에서 발생한 메모리 블로트를 **복구하지 못함** (Figure 1: Redis 실험에서 Linux 28GB 블로트, Ingens 20GB 블로트).
- 핵심 트레이드오프: 주소 변환 오버헤드 vs. 메모리 블로트, 페이지 폴트 지연 시간 vs. 폴트 횟수 간의 상충 관계를 해결해야 함.

## 방법론

### 3.1. 메모리 블로트 회복 (Bloat Recovery)

- **접근 커버리지(access-coverage):** huge page 영역 내에서 접근된 base page 수를 측정하여 해당 영역의 TLB 필요량을 추정.
- **블로트 탐지:** 백그라운드 스레드가 huge page를 스캔하여 base page가 모두 제로 채워진 경우를 탐지. 평균적으로 base page 내 첫 비제로 바이트까지의 거리는 **9.11바이트**에 불과 (Figure 3), 즉 사용 중인 페이지는 빠르게 필터링 가능.
- **디모션 전략:** MMU 오버헤드가 가장 낮은 애플리케이션부터 먼저 스캔하여, huge page가 가장 덜 필요한 프로세스부터 블로트 회복을 수행.
- **성능:** 스캔 오버헤드는 블로트 페이지 수에 비례하며, 할당된 총 메모리 크기에 비례하지 않아 대규모 메모리 시스템에서도 확장 가능.

### 3.2. 세밀한 Huge Page 승격 (Fine-grained Promotion)

- **access_map 구조:** 프로세스별 10개 버킷으로 구성된 배열. 접근 커버리지 값(0~512)에 따라 huge page 영역을 버킷에 배치.
  - Bucket 0: access-coverage 0~49 (Cold)
  - Bucket 9: access-coverage 450~512 (Hot)
- **동작 방식:**
  1. 30초마다 페이지 테이블 접근 비트를 클리어하고 1초 후 세팅된 비트 수를 측정.
  2. 지수이동평균(EMA)으로 access-coverage 계산.
  3. 높은 인덱스(핫 영역)의 버킷부터 낮은 인덱스 순으로 승격.
  4. 같은 버킷 내에서는 최근 접근된 영역(Head)부터 승격.
- **Linux/Ingens 대비 효과:** 기존 시스템은 VA 순서(낮은 주소→높은 주소)로 순차 스캔 승격但在 HawkEye는 실제 hotness에 따라 승격하여, Graph500, XSBench에서 **13~22% 성능 향상** (Figure 5).

### 3.3. 다중 프로세스 할당 전략

- **HawkEye-G (General):** 모든 프로세스의 비어 있지 않은 최고 access-coverage 인덱스에서 라운드-robin으로 승격하여 공정성 보장.
- **HawkEye-PMU (Performance Monitoring Unit):** HW 성능 카운터로 측정된 실제 MMU 오버헤드가 가장 높은 프로세스를 우선 선택.
- **효율성:** HawkEye-PMU는 MMU 오버헤드가 2% 미만으로 떨어지면 승격을 중지하여 불필요한 승격을 방지. XSBench에서 Linux 대비 **44배** 더 효율적 (time saved per promotion).

## 핵심 기여

- HawkEye는 huge page 관리의 세 가지 핵심 문제 (메모리 블로트, 페이지 폴트 지연, 주소 변환 오버헤드)를 데이터 기반 동적 알고리즘으로 해결.
- **핵심 기여:**
  1. 비동기 사전 제로잉 + zero-page 디-dupelication으로 메모리 블로트 회복
  2. access_map 기반 세밀한 승격으로 기존 VA 순서 승격 대비 **13~22% 성능 향상**
  3. HW 성능 카운터 통합으로 실제 MMU 오버헤드에 기반한 승격决策
- 기존 시스템(Linux THP, Ingens) 대비 다양한 워크로드에서 일관되게 우수한 성능.
- **의의:** Huge page 관리에 "one-size-fits-all" 정책의 한계를 지적하고, 워크로드 특성에 적응하는 동적 데이터 기반 접근법의 효과를 입증.

## 주요 결과

- **구현 언어:** C (Linux 커널 v4.3 기반)
- **실험 플랫폼:** Intel Haswell-EP E5-2690 v3, 96GB 메모리, 48코어 (2.3GHz, 하이퍼스레딩 활성화)
- **TLB 구성:** L1 TLB - 64 엔트리(4KB), 8 엔트리(2MB); L2 TLB - 1024 엔트리(4KB/2MB 공유)
- **캐시:** L1 768KB, L2 3MB, L3 30MB
- **스왑:** 96GB SSD 기반 스왑 파티션 (오버커밋 평가용)
- **오버헤드:** 단일 코어 기준 최대 **≈3.4%**의 알고리즘 오버헤드

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2019ASPLOS-summarize/hawkeye-efficient-fine-grained-os-support-for-huge-pages.md|전체 요약 보기]]
