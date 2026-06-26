---
tags: [paper, 2019, 2019ISCA, topic/dram, topic/gpu, topic/virtual-memory]
venue: "The 46th Annual International Symposium on Computer Architecture (ISCA '19)"
year: 2019
summary_path: "../paper-summaries/2019ISCA-summarize/translation-ranger-os-support-for-contiguity-aware-tlbs.md"
---

# Translation Ranger: Operating System Support for Contiguity-Aware TLBs

**Venue:** The 46th Annual International Symposium on Computer Architecture (ISCA '19)
**저자:** Zi Yan (Rutgers University & NVIDIA), Daniel Lustig (NVIDIA), David Nellans (NVIDIA), Abhishek Bhattacharjee (Yale University)

## 개요

- 가상 메모리(VM)는 프로그래밍 편의성을 제공하지만, 주소 변환(address translation) 오버헤드가 성능 병목이 됨
- 기존 해법: TLB 용량을 늘리지만, 이는 상당한 하드웨어 리소스(면적, 전력)를 소모
  - Intel은 Sandybridge~Skylake에서 매 세대 CPU TLB 용량을 약 2배로 증가시킴
  - AMD GPU는 더 큰 TLB를 구현하지만 면적/전력 비용이 큼
  - 가속기(accelerator)에는 하드웨어 리소스가 제한되어 대형 TLB 부적합
- **번역 연속성(translation contiguity)** 활용 방안:
  - 연속된 가상 페이지 → 물리적으로 인접한 프레임 매핑 시, N개 번역을 단일 TLB 엔트리로 압축 가능
  - Range TLB [23], devirtualizing memory [18], direct segments [4], COLT [9,39] 등 다양한 제안 존재
- **기존 연속성 생성 방식의 한계**:
  - Huge pages: 특정 크기(2MB/1GB)와 정렬 제한
  - Identity mapping [18]: 물리-가상 주소 동일 매핑 요구 → copy-on-write, disk paging, ASLR 등 OS 기능과 충돌
  - Direct segments/Range TLB: 메모리 (pre)allocation 시점에만 연속성 생성 가능
  - TLB coalescing [39]: 우연적(serendipitous) 연속성에 의존
- **핵심 문제**: 시스템이 장시간 온라인 상태에서 메모리 단편화(fragmentation)가 발생해도, 임의의 시작 조건에서 제한 없는 연속성을 능동적으로 생성하는 OS 지원이 부재

## 방법론

### 3.1. 능동적 페이지 병합(Active Page Coalescing)

- 가상적으로 연속된 페이지 그룹을 물리적으로 인접한 프레임으로 병합하는 핵심 메커니즘
- **할당 시 병합(Allocation-time coalescing)**: 새 메모리 할당 시 연속된 물리 프레임을 선호하여 할당
- **할당 후 병합(Post-allocation coalescing)**: 기존에 분산된 페이지를 페이지 마이그레이션을 통해 병합
- 페이지 마이그레이션 시 성능 오버헤드 최소화 필요

### 3.2. 페이지 마이그레이션 최적화

- 기존 OS의 페이지 마이그레이션은 오버헤드가 커서 post-allocation 병합에 부적합
- Translation Ranger의 최적화:
  - 불필요한 복사(copy) 최소화
  - 비이동 불가(non-movable) 페이지 처리
  - 커널 수준에서 마이그레이션 비용 절감
- 페이지 병합이 사용자 애플리케이션 성능에 미치는 영향 최소화

### 3.3. 비이동 불가 페이지 처리

- Linux 커널은某些 페이지를 non-movable로 표시 (커널 내부 데이터 구조 등)
- Translation Ranger는 non-movable 페이지도 병합 대상으로 처리:
  - non-movable 페이지가 연속된 물리 영역에 위치하도록 배치
  - 병합 과정에서 non-movable 페이지의 위치를 고려한 최적 매핑 생성

### 3.4. 연속성 영역 관리

- 120GB 애플리케이션 footprint를 **128개 이하의 연속 영역**으로 압축
- 연속 영역 관리 구조:
  - 각 연속 영역: 시작 가상 주소, 시작 물리 주소, 크기 정보 저장
  - 영역 간 병합/분할 동적 관리
- 영역 수 최소화로 TLB 엔트리 효율 극대화

## 핵심 기여

- **핵심 Contribution**: OS 수준에서 능동적 페이지 병합을 통해 제한 없는 번역 연속성을 생성하는 Translation Ranger 제안
- **성능**: 40× 더 큰 연속 영역, 120GB를 128개 영역으로 압축, <2% 오버헤드
- **범용성**: 기존 모든 contiguity-aware TLB 최적ization과 호환, 하드웨어 지원 불필요
- **실용성**: Linux v4.16 커널에 구현 및 오픈소스 공개
- **의의**: 번역 연속성 생성의 OS 지원 공백을 해소하여 주소 변환 오버헤드를 근본적으로 완화하는 인프라 제공

## 주요 결과

- **구현 환경**: Linux v4.16 커널
- **소스코드**: 오픈소스 공개 (https://github.com/ysarch-lab/translation_ranger_isca_2019)
- **커널 패치**: 페이지 할당기(allocator), 페이지 테이블 관리, 마이그레이션 서브시스템 수정
- **호환성**: 기존 contiguity-aware TLB(COLT, direct segments 등)와 통합 가능
- **하드웨어 요구사항**: 특수 하드웨어 지원 불필요, 기존 x86-64 TLB로 동작

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2019ISCA-summarize/translation-ranger-os-support-for-contiguity-aware-tlbs.md|전체 요약 보기]]
