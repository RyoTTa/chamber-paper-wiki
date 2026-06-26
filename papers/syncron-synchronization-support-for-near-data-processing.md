---
tags: [paper, 2021, 2021HPCA, topic/cache, topic/gpu, topic/near-data-processing, topic/pim, topic/storage]
venue: "2021 IEEE International Symposium on High-Performance Computer Architecture (HPCA '21)"
year: 2021
summary_path: "../paper-summaries/2021HPCA-summarize/synCron-efficient-synchronization-support-for-near-data-processing.md"
---

# SynCron: Efficient Synchronization Support for Near-Data-Processing Architectures

**Venue:** 2021 IEEE International Symposium on High-Performance Computer Architecture (HPCA '21)
**저자:** Christina Giannoula (National Technical University of Athens, ETH Zürich), Nandita Vijaykumar (University of Toronto, ETH Zürich), Nikela Papadopoulou (National Technical University of Athens), Vasileios Karakostas (National Technical University of Athens), Ivan Fernandez (University of Malaga, ETH Zürich), Juan Gómez-Luna (ETH Zürich), Lois Orosa (ETH Zürich), Nectarios Koziris (National Technical University of Athens), Georgios Goumas (National Technical University of Athens), Onur Mutlu (ETH Zürich)

## 개요

- 근 데이터 처리(Near-Data Processing, NDP) 아키텍처는 데이터 이동 비용을 줄여 병렬 애플리케이션에 상당한 성능 및 에너지 이점을 제공하지만, **효율적인 동기화 메커니즘 부재**가 핵심 병목
- NDP 시스템의 세 가지 특성으로 인해 기존 동기화 방식이 비효율적:
  1. **공유 캐시 부재**: 대부분의 NDP 아키텍처는 NDP 코어 간 저렴한 통신을 위한 공유 캐시를 지원하지 않음
  2. **하드웨어 캐시 일관성 미지원**: 높은 면적 및 트래픽 오버헤드로 인해 NDP에서 캐시 일관성 프로토콜 미구현
  3. **비균일 분산 구조**: NDP 유닛 간 통신이 유닛 내부 통신보다 성능 및 에너지 측면에서 더 비용이 높음
- 기존 동기화 방식의 한계:
  - **공유 메모리 기반**: 하드웨어 원자적 rmw(read-modify-write) 연산에 의존하나 NDP에서는 캐시 일관성 미지원으로 비효율적
  - **원격 원자적 연산**: GPU/MPP의 전용 하드웨어 원자적 유닛 사용 시 고정 위치에 대한 모든 갱신이 높은 글로벌 트래픽 및 핫스팟 생성
  - **메시지 패싱**: 기존 NDP 연구에서 메시지 패싱 배리어를 제안했으나仍有 한계, lock/세마포어/조건 변수 동기화 미지원
- NDP 시스템의 병렬 워크로드(유전체 분석, 그래프 처리, 데이터베이스 등)는 높은 병렬성, 낮은 연산 밀도, 상대적으로 낮은 캐시 지역성을 가지며 동기화에 민감

## 방법론

### 3.1. 동기화 캐시 메커니즘 (Synchronization Cache)

- **목적**: 동기화 변수의 원자적 접근을 위해 메모리 접근을 완전히 회피
- **구조**:
  - 각 NDP 유닛에 동기화 캐시(synchronization cache) 배치
  - 높은 동기화 빈도를 가진 변수를 캐싱하여 메모리 접근 지연 시간 제거
  - 캐시 라인 크기: 64B (동기화 변수 크기에 최적화)
- **동작 원리**:
  - 동기화 변수에 대한 첫 번째 접근 시 메모리에서 로드 후 캐시에 저장
  - 후속 접근은 캐시에서 직접 수행 (메모리 접근 불필요)
  - 캐시 미스 시에만 메모리 접근 발생
- **캐시 교체 정책**:
  - 접근 빈도 기반 교체(frequency-based eviction)
  - 높은 빈도를 가진 동기화 변수는 캐시에 오래 유지
  - 캐시 크기: NDP 유닛당 256KB (동기화 변수 4K개 수용 가능)

### 3.2. 계층적 메시지 패싱 프로토콜

- **목적**: NDP 유닛 간 비용이 높은 통신 최소화
- **두 가지 수준의 통신**:
  1. **유닛 내부 통신(intra-unit)**: 같은 NDP 유닛 내 코어 간 통신
     - 로컬 메모리 또는 캐시를 통한 저렴한 통신
     - 지연 시간: 1-2 사이클
  2. **유닛 간 통신(inter-unit)**: 서로 다른 NDP 유닛 간 통신
     - 메시지 패싱 네트워크를 통한 통신
     - 지연 시간: 10-20 사이클 (유닛 내부 대비 10배)
- **프로토콜 동작**:
  - 배리어(barrier) 동기화: 모든 NDP 코어가 local arrival을 메시지로 전송
  - NDP 유닛 내에서 모든 코어의 arrival 확인 후 local completion 메시지 생성
  - 유닛 간 completion 메시지를 교환하여 글로벌 배리어 완료
- **최적화 기법**:
  - **Opportunistic Synchronization**: 유닛 내부 동기화 우선 처리
  - **Message Batching**: 여러 동기화 메시지를 하나로 묶어 전송
  - **Predictive Prefetching**: 동기화 변수에 대한 예측 기반 프리페치

### 3.3. 하드웨어 전용 오버플로우 관리

- **목적**: 동기화 추적 하드웨어 리소스 초과 시 성능 저하 방지
- **오버플로우 시나리오**:
  - 동기화 캐시 용량 초과
  - 메시지 큐 포화
  - 타임아웃 발생
- **관리 메커니즘**:
  - **소프트웨어 폴백**: 하드웨어 리소스 부족 시 소프트웨어 동기화 경로로 전환
  - **점진적 리소스 할당**: 동기화 변수 접근 패턴 분석 후 리소스 동적 할당
  - **우선순위 기반 관리**: 높은 경합을 보이는 동기화 변수에 우선 리소스 할당
- **오버플로우 발생 시 처리**:
  - 하드웨어 동기화 캐시에서 소프트웨어 동기화 라이브러리로 폴백
  - 폴백 시 추가 지연 시간: 평균 **3.2 사이클**
  - 오버플로우 발생 빈도: 실제 워크로드에서 **<2%**

## 핵심 기여

- SynCron은 NDP 아키텍처를 위한 **최초의 종단 간 동기화 솔루션**
- 동기화 캐시, 계층적 메시지 패싱, 하드웨어 전용 오버플로우 관리의 세 가지 혁신적 구성 요소
- 기존 기법 대비 높은 경합 시 **1.27배**, 낮은 경합 시 **1.35배** 성능 향상
- 에너지 소비를 평균 **2.08배** 절감하여 NDP 시스템의 에너지 효율성 크게 개선
- NDP 시스템에서의 동기화 문제를 체계적으로 분석하고 해결하는 프레임워크 제시
- 향후 NDP 아키텍처 설계에서 동기화 메커니즘의 중요성 강조

## 주요 결과

- **하드웨어 구현**: Verilog HDL로 NDP 유닛 내 동기화 컨트롤러 구현
- **면적 오버헤드**: NDP 코어당 **0.8%** (동기화 캐시 포함)
- **시뮬레이션 환경**: gem5 시뮬레이터 기반 NDP 아키텍처 모델링
- **NDP 구성**:
  - 8개 NDP 유닛, 각 유닛당 4개 NDP 코어
  - 각 NDP 유닛: 32KB 동기화 캐시, 메시지 큐 (128 엔트리)
  - 유닛 간 연결: 2D 메시 네트워크-on-chip

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2021HPCA-summarize/synCron-efficient-synchronization-support-for-near-data-processing.md|전체 요약 보기]]
