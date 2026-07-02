---
tags: [paper, 2018, 2018ASPLOS, topic/cache, topic/dram, topic/virtual-memory]
venue: "23rd International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '18)"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/devirtualizing-memory-in-heterogeneous-systems.md"
---

# Devirtualizing Memory in Heterogeneous Systems

**Venue:** 23rd International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '18)
**저자:** Swapnil Haria (University of Wisconsin-Madison), Mark D. Hill (University of Wisconsin-Madison), Michael M. Swift (University of Wisconsin-Madison)

## 개요

- Dennard Scaling의 종료와 Moore's Law 둔화로 이종 가속기(heterogeneous accelerators)에 대한 관심 증가
- 그래프 처리, 데이터 분석, 신경망 컴퓨팅을 위한 가속기가 성능/전력 측면에서 범용 프로세서 대비 수 배 향상
- **공유 가상 메모리(SVM)의 문제점:** 가속기에 SVM을 제공하면 프로그래밍 용이성과 메모리 보호를 제공하지만, 가속기의 가상 메모리 오버헤드는 범용 프로세서보다 더 큼
- 그래프 워크로드에서 128-entry TLB 사용 시 **TLB 미스율 21%** (Figure 2) → 2MB 페이지를 사용해도 1%만 개선
- CPU에서도 큰 메모리 워크로드에서 주소 변환 오버헤드가 **최대 50%**까지 증가
- 기존 가속기 주소 변환 방식의 한계:
  - 별도 주소 공간: 데이터 복사 필요, 프로그래밍 복잡도 증가
  - Direct Segments: 단일 연속 메모리 영역만 지원, 유연성 부족
  - Range TLBs: 전력/면적 소비가 높아 가속기에 부적합

## 방법론

### 3.1. Identity Mapping

- **Eager contiguous allocation:** 메모리 할당 시 물리 프레임을 즉시 예약하고 VA==PA로 매핑
- **Flexible address space:** 힙 세그먼트가 주소 공간 어디에든 위치 가능 (표준 레이아웃 제약 제거)
- **Fallback:** 적합한 주소 범위를 찾을 수 없으면 기존 demand paging으로 복귀
- 메모리 할당 시 인접 물리 페이지가 필요 → buddy allocator의 eager paging 수정 사용

### 3.2. Permission Entry (PE)

- **구조:** 8바이트 크기, 기존 PTE와 동일한 크기로 교체 가능
- **16개 권한 필드:** 각 필드가 PE가 매핑하는 VA 범위의 1/16에 해당하는 영역의 권한 저장
  - L2PE: 2MB 범위 → 128KB 영역별 권한
  - L3PE: 1GB 범위 → 64MB 영역별 권한
- **컴팩트 페이지 테이블:** PE가 L1 PTE 전체 트리를 대체 → 페이지 테이블 크기 98% 이상 축소 (Table 1)
  - Flickr: 616KB → 48KB
  - Wikipedia: 2520KB → 48KB
  - LiveJournal: 4280KB → 48KB

### 3.3. Access Validation Cache (AVC)

- **4-way set-associative 캐시:** 64B 블록, 128 엔트리 (1KB)
- PEs와 일반 PTE 모두 캐싱 → TLB와 PWC를 대체
- 컴팩트한 페이지 테이블로 인해 높은 히트율 → 메모리 접근 없이 페이지 워크 완료 가능
- 페이지 워크: 2-4회 AVC 접근으로 완료 (최악의 경우)

### 3.4. Read Preload 최적화

- 읽기 접근 시 DAV와 병렬로 데이터 preload 실행
- Identity-mapped 페이지(대부분)에서는 preload가 실제 메모리 접근이 됨
- Non-identity-mapped 페이지(드묾)에서는 preload를 폐기하고 정상 주소 변환 수행
- **stores에는 적용 불가:** 물리 주소가 확인되기 전까지 메모리 업데이트 불가

### 3.5. CPU 확장 (cDVM)

- CPU의 모든 세그먼트(code, data, heap, stack)를 identity mapping
- 스택: 8MB로 eager 할당, Split Stacks로 확장 지원
- Write-allocate 정책 활용: 스토어 시 캐시라인 fetch를 주소 변환과 병렬로 수행

## 핵심 기여

- DVM은 가속기를 위한 **가상 메모리 오버헤드를 1.7-3.5%로 대폭 감소**하는 새로운 메모리 관리 방식
- Identity Mapping과 Permission Entry를 통해 주소 변환을 권한 검증으로 대체
- PE로 페이지 테이블 크기를 98% 이상 축소하여 AVC의 효율성을 극대화
- CPU(cDVM)로 확장 가능하여 이종 시스템 전체에 적용 가능
- Meltdown/Spectre 대응 필요성承认 (2018년 초 발표)

## 주요 결과

- **구현 언어:** C (Linux 4.10 커널)
- **코드 라인 수:** 251 LOC (Table 5)
  - 코드 세그먼트: 39 LOC
  - 힙 세그먼트: 1 LOC (mmap 세그먼트 변경으로 대체)
  - 메모리 매핑 세그먼트: 56 LOC
  - 스택 세그먼트: 63 LOC
  - 페이지 테이블: 78 LOC
  - 기타: 15 LOC
- **시뮬레이션:** gem5 기반 사이클 레벨 시뮬레이션
- **가속기:** Graphicionado 그래프 처리 가속기 (8개 프로세싱 엔진)

## 한계점

- Eager paging으로 인한 메모리 단편화 위험
- Copy-on-Write 시 identity mapping 깨질 수 있음 (첫 쓰기 시 복사본 생성)
- Meltdown/Spectre와의 호환성 문제 (preloader가 미세 아키텍처 상태 변경 가능)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2018ASPLOS-summarize/devirtualizing-memory-in-heterogeneous-systems.md|전체 요약 보기]]
