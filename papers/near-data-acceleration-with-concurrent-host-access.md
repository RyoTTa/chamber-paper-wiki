---
tags: [paper, 2020, 2020ISCA, topic/dram, topic/pim]
venue: "IEEE/ACM International Symposium on Computer Architecture (ISCA), 2020"
year: 2020
summary_path: "../paper-summaries/2020ISCA-summarize/near-data-acceleration-with-concurrent-host-access.md"
---

# Near Data Acceleration with Concurrent Host Access

**Venue:** IEEE/ACM International Symposium on Computer Architecture (ISCA), 2020
**저자:** Benjamin Y. Cho, Yongkee Kwon, Sangkug Lym, Mattan Erez (The University of Texas at Austin)

## 개요

- Near-Data Accelerators(NDAs)는 메인 메모리와 통합되어 전력 및 성능 이점을 제공하는 하드웨어 가속기
- NDAs는 낮은 시간적 로컬리티와 낮은 산술 강도를 가진 애플리케이션에 적합
- 기존 NDA 연구의 한계:
  - **동시 접근 미지원**: 호스트 프로세서와 NDAs가 동시에 메모리 디바이스에 접근하는 아키텍처 과제 미해결
  - **미세한-grained 작업 제한**: 기존 연구는 캐시 라인 수준의 미세한 NDA 작업에 한정
  - **데이터 복사 오버헤드**: 호스트와 NDA 간 협업 처리 시 비용이 많이 드는 데이터 복사 필요
- 핵심 과제:
  1. 호스트에서 NDAs로의 **로컬리티 간섭 완화**
  2. 미세한 인터리빙으로 인한 **읽기/쓰기 전환 오버헤드** 감소
  3. NDAs의 로컬리티와 호스트 성능을 모두 지원하는 **메모리 레이아웃 설계**
  4. **패킷화 및 전통적 메모리 인터페이스** 동시 지원

## 방법론

### 3.1. DIMM 기반 메모리 시스템

- **구성 요소**: 각 DIMM은 여러 칩으로 구성, 각 칩은 3DS 유사 접근 방식으로 스택된 DRAM 다이와 로직 다이 포함
- **처리 요소(PEs)**: 로직 다이에 위치하며 NDA 메모리 컨트롤러를 통해 내부 메모리에 접근
- **메모리 컨트롤러**: 호스트 외부 접근과 NDA 내부 접근을 관리
- **동시 접근 제약**: 특정 랭크가 호스트에 의해 접근되는 동안 NDA 요청을 처리할 수 없음 (다른 랭크의 대역폭은 사용 가능)

### 3.2. 로컬리티 간섭 완화

- **호스트-NDA 간섭 문제**: 인터리브된 접근이 로컬리티를 감소시키고 읽기/쓰기 전환 패널티를 추가
- **해결책**: 호스트와 NDA 접근을 시간적/공간적으로 분리하는 메커니즘
- **성능 영향 최소화**: 호스트 접근 성능을 유지하면서 NDA의 로컬리티를 보장

### 3.3. 읽기/쓰기 전환 오버헤드 감소

- **전환 오버헤드 원인**: 미세한 인터리빙으로 인한 읽기-쓰기 전환 비용
- **최적화 기법**: 접근 패턴 분석을 통한 전환 빈도 최소화
- **하드웨어 지원**: 메모리 컨트롤러 레벨에서의 전환 오버헤드 관리

### 3.4. 메모리 레이아웃 설계

- **이중 요구사항 충족**:
  1. NDA 커널所需的 로컬리티 보장
  2. 호스트 성능을 위한 효과적인 인터리빙
- **물리적 주소 매핑**: 채널, 랭크, 뱅크 수준에서의 최적화된 주소 분배
- **데이터 배치 전략**: NDA 커널의 전체 배열 소비를 지원하는 메모리 배치

## 핵심 기여

- **핵심 기여**: NDA 지원 메모리에서 호스트와 NDAs의 동시 접근을 지원하는 아키텍처 메커니즘 제안
- **실용성**: DDRx 호환 DIMM 인터페이스를 사용하여 실용적 구현 가능성 입증
- **성능 잠재력**: SVRG 알고리즘을 통해 실제 워크로드에서의 성능 향상 가능성 시연
- **효율성**: 데이터 이동 최소화를 통한 전력 및 성능 이점 동시 달성
- **미래 연구 방향**: NDA와 호스트 간의 더 효율적인 협업 처리를 위한 추가 최적화 필요

## 주요 결과

- **시뮬레이션 환경**: 다중 코어 CPU와 NDA 지원 DDR4 메모리 모듈로 구성된 시뮬레이션 시스템
- **구현 언어**: 시뮬레이터 및 하드웨어 설계 언어
- **시스템 구성**: CPU 코어, NDA가 통합된 DIMM 기반 메모리 시스템
- **호스트 인터페이스**: DDRx 호환 DIMM 인터페이스

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2020ISCA-summarize/near-data-acceleration-with-concurrent-host-access.md|전체 요약 보기]]
