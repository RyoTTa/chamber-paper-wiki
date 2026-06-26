---
tags: [paper, 2018, 2018MICRO, topic/cache, topic/dram]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/chameleon-a-dynamically-reconfigurable-heterogeneous-memory-system.md"
---

# CHAMELEON: A Dynamically Reconfigurable Heterogeneous Memory System

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Jagadish B. Kotra, Haibo Zhang, Alaa R. Alameldeen, Chris Wilkerson, Mahmut T. Kandemir (AMD Research, Pennsylvania State University, Intel Labs, NVIDIA)

## 개요

- 모던 컴퓨팅 시스템은 고대역폭/고용량 메모리에 대한 수요가 지속적으로 증가 (고해상도 그래픽, 머신 러닝 등)
- Die-stacked/on-die 메모리(HBM, HMC 등)는 높은 대역폭을 제공하지만, 스택 수 제한과 인포저 문제로 단독 사용 불가 → **이종 메모리 시스템**(빠른 메모리 + 느린 DDR) 구성
- 기존 이종 메모리 활용 방식의 한계:
  - **캐시 기반:** 빠른 메모리를 캐시로 활용 → 성능 우수하지만 OS 가시 메모리 용량 감소 (데이터 중복 저장)
  - **PoM(Part of Memory) 기반:** 빠른 메모리를 OS에 노출하여 용량 확장 → 스왑 오버헤드로 성능 저하 가능
- 캐시와 PoM은 본질적으로 상반된 특성: 캐시는 성능 우선, PoM은 용량 우선
- 멀티프로그래밍 워크로드에서 각 애플리케이션의 메모리 사용량이 시간에 따라 변동 → 정적 구조로는 최적 응답 불가

## 방법론

### 3.1. 하드웨어 구성요소

- **Segment Restricted Remapping Table (SRRT):**
  - PoM 아키텍처의 핵심 메타데이터 구조체
  - 세그먼트 그룹(SegGrp) 단위로 스택 드램과 오프칩 드램 간 세그먼트 리매핑 관리
  - Chameleon에서 추가 확장:
    - **ABV (Alloc Bit Vector):** 세그먼트 할당 상태 추적 (1비트 per 세그먼트)
    - **Mode Bit:** 세그먼트 그룹의 운영 모드 (0: PoM, 1: 캐시)
    - **Dirty Bit:** 캐시 모드에서 세그먼트의 더러움 상태 추적
- **세그먼트 그룹 구성:**
  - 스택 드램(4GB)과 오프칩 드램(20GB)의 비율 1:5 → 세그먼트 그룹당 6개 세그먼트
  - 스택 드램 세그먼트는 동일 그룹의 오프칩 드램 세그먼트와만 교환 가능 (리매핑 제약)

### 3.2. PoM ↔ 캐시 모드 전환

- **ISA-Alloc (PoM→캐시 전환 트리거):**
  - OS가 페이지를 할당할 때 호출
  - 세그먼트 그룹이 캐시 모드이고 아무것도 캐싱하지 않으면 → PoM 모드로 전환
  - 캐시 모드에서 오프칩 세그먼트를 캐싱 중이면 → 더러운 경우 writeback 후 새 세그먼트 할당
  - 오프칩 세그먼트 할당 시 → 기존 모드 유지
- **ISA-Free (캐시→PoM 전환 트리거):**
  - OS가 페이지를 해제할 때 호출
  - 세그먼트 그룹의 모든 세그먼트가 해제되면 → 캐시 모드로 전환
  - 하드웨어가 자동으로 캐시 교체 정책으로 빈 세그먼트 활용

### 3.3. Chameleon-Opt (최적화된 변형)

- **능동적 세그먼트 리매핑:**
  - 스택 드램 세그먼트를 오프칩 드램으로 능동적으로 리매핑하여 캐시용 공간 확보
  - 캐시 히트율进一步 향상
- **성능 오버헤드 최소화:**
  - 세그먼트 크기(2KB)로 인한 스왑 오버헤드 관리
  - Dirty 세그먼트 writeback와 동시 접근 간섭 최소화

### 3.4. OS 지원

- **알고리즘 1 (OS 할당 루틴):**
  - `free_one_page()` 함수에서 `ISA-Free` 호출
  - `GFP_TRANSHUGE` 플래그로 2MB THP 할당 감지
  - 세그먼트 크기에 따라 `ISA-Alloc/ISA-Free` 호출 횟수 결정 (2KB 세그먼트 → 1024회, 64B 세그먼트 → 32,768회)
- **알고리즘 2 (OS 해제 루틴):**
  - 페이지 해제 시 해당 세그먼트에 대해 `ISA-Free` 호출

## 핵심 기여

- **핵심 기여:** 캐시의 성능과 PoM의 용량을 동시에 달성하는 Chameleon 하이브리드 아키텍처 제시
- **성능:** PoM 대비 11.6%, 캐시 대비 24.2% 성능 향상
- **용량:** PoM과 동등한 OS 가시 메모리 용량 유지
- **실용성:** 2개의 ISA 명령어로 구현되는 하드웨어-소프트웨어 공동 설계로 실현 가능성 확보
- **의의:** 이종 메모리 시스템에서 정적 구조의 한계를 극복하고 동적 적응을 통해 최적 성능/용량 균형을 달성하는 새로운 패러다임 제시

## 주요 결과

- **하드웨어 확장:** SRRT에 ABV, Mode Bit, Dirty Bit 추가 (minimal area overhead)
- **소프트웨어 확장:** OS 메모리 할당/해제 루틴에 `ISA-Alloc`/`ISA-Free` 호출 삽입
- **시뮬레이션 기반 평가**
- **시스템 구성:** 4GB 스택 드램(HBM) + 20GB 오프칩 드램(DDR4)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/chameleon-a-dynamically-reconfigurable-heterogeneous-memory-system.md|전체 요약 보기]]
