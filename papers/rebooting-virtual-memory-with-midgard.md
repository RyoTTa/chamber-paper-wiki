---
tags: [paper, 2021, 2021ISCA, topic/cache, topic/dram, topic/gpu, topic/virtual-memory]
venue: "ISCA 2021 (48th Annual IEEE/ACM International Symposium on Computer Architecture)"
year: 2021
summary_path: "../paper-summaries/2021ISCA-summarize/rebooting-virtual-memory-with-midgard.md"
---

# Rebooting Virtual Memory with Midgard

**Venue:** ISCA 2021 (48th Annual IEEE/ACM International Symposium on Computer Architecture)
**저자:** Siddharth Gupta (EcoCloud, EPFL), Atri Bhattacharyya (EcoCloud, EPFL), Yunho Oh (Sungkyunkwan University), Abhishek Bhattacharjee (Yale University), Babak Falsafi (EcoCloud, EPFL), Mathias Payer (EcoCloud, EPFL)

## 개요

- 현대 워크로드의 점점 커지는 working set을 수용하기 위해 캐시 계층의 용량이 점점 증가하고 있으나, 이는 주소 변환(address translation)으로 성능 병목이 이동
- 기존 TLB 기반 주소 변환은 시스템 성능의 **10~30%**를 소비할 수 있음
- **기존 대응의 한계**:
  - 대형 two-level TLB 계층 (수천 엔트리), 다중 페이지 크기용 별도 L1 TLB, skew/hash-rehash L2 TLB 등 복잡한 하드웨어 통합
  - OS의 'huge page' 메모리 단편화 해소 로직, 생성/분리/마이그레이션 휴리스틱 등 방대한 소프트웨어 지원 필요
  - MMU cache 기반 page table walk 가속화 → TLB shootdown 프로토콜의 복잡성/버그 증가
- Huge page 휴리스틱은 성능 병리를 유발할 수 있어 범용적 해결책이 아님
- 데이터센터/서버 환경에서 가상 머신, GPU, FPGA 등 다양한 가속기와의 호환성도 과제
- **핵심 문제**: 기존 가상 메모리(VM) 추상화는 성능과 구현 복도의 도전에 시달리며, 프로그래머블리티 이점을 잠식

## 방법론

### 3.1. VMA 기반 주소 변환 (Front Side)

- **Virtual Lookaside Buffer (VLB)**: 기존 TLB와 유사하나 VMA 단위로 동작, **수십 엔트리**로 충분 (기존 TLB의 수천 엔트리 대비 훨씬 작음)
- **VMA Table**: B-tree 기반 per-process 데이터 구조, VMA의 base/bound/offset + permission bits 저장
  - 각 VMA 매핑은 ~24 bytes → ~100개 VMA도 **4KB 페이지**에 적재 가능
- VMA→MMA(Midgard Memory Area) 변환은 범위 비교(range comparison) 기반, 하드웨어에서 빠르게 처리
- VLB는 가상 주소를 Midgard 주소로 변환, 접근 제어도 동시에 수행

### 3.2. Midgard Page Table (Back Side)

- Midgard 주소空间의 MMA를 물리 프레임 번호로 매핑하는 **radix page table** (기존 OS page table과 유사)
- Midgard 주소空间은 물리 주소空间보다 충분히 커야 함 (실험에서 **10~15 bits** 여유)
- **Contiguous allocation 최적화**: radix tree를 완전 확장하여 unmapped 페이지도 연속 배치 (Fig. 3) → M2P 변환 시 다중 레벨 lookup을 **short-circuit**
- 페이지 fault 시 OS가 lazy 매핑 생성, demand paging, 또는 segmentation fault 신호

### 3.3. Midgard Lookaside Buffer (MLB)

- LLC가 상대적으로 작을 때, 백엔드에 중앙 집중형 MLB 도입 가능
- **集中 MLB 장점**: per-core MLB 대비 높은 활용도, 매핑 중복 제거, shootdown 로직 단순화
- 메모리 컨트롤러와 **co-locate**하여 MLB hit 시 로컬 메모리 컨트롤러에서 직접 데이터retrieve
- 다양한 페이지 크기(4KB, huge page) 동시 지원 가능 (L2 TLB보다 느린 latency 허용)
- **최적 MLB 크기**: 16MB LLC에서 평균 **64 엔트리**로 충분, 128 엔트리 이상은 불필요 (Fig. 8, 9)

### 3.4. 하드웨어 지원

- **VMA Table Base Register**: 코어별 B-tree 루트 Midgard 주소 저장
- **Midgard Page Table Base Register**: 메모리 컨트롤러에 물리 주소 루트 포인터
- **Store buffer 확장**: M2P 변환 실패 시 store rollback을 위한 과거 매핑 기록 버퍼링 필요
- **Access/Dirty bit 업데이트**: LLC 캐시 블록 fill/writeback 시 업데이트 (기존 TLB의 업데이트 시점과 차별화)

## 핵심 기여

- **핵심 Contribution**: VMA 개념을 하드웨어에 통합한 최초의 중간 주소 공간 Midgard 제시, VM 추상화를 "미래 보장(future-proofing)"
- **성능**: 256MB LLC에서 Traditional 2MB huge page와 breakeven, 1GB+ LLC에서 오버헤드 **~0%**
- **확장성**: 캐시 계층이 커질수록 Midgard의 변환 오버헤드가 **감소** (전통적 TLB의 반대 동향)
- **프로그래머빌리티**: 기존 바이너리 재컴파일 불필요, homonym/synonym 문제 해결, 프로그래머 투명
- **의의**: 데이터센터/서버 환경의 대형 메모리 시스템에서 VM 성능 문제를 근본적으로 해결하는 방향 제시, 향후 대형 SRAM/DRAM 캐시 트렌드와 자연스럽게 호환

## 주요 결과

| 항목 | 내용 |
|------|------|
| **구현 플랫폼** | QFlex (QEMU 기반 full-system 시뮬레이터) |
| **프로세서** | 16× ARM Cortex-A76 @ 2GHz |
| **L1 캐시** | 64KB 4-way (I/D), 64-byte blocks, 4 cycles |
| **LLC** | 1MB/tile, 16-way, 30 cycles, non-inclusive |
| **메모리** | 256GB (코어당 16GB), 4개 메모리 컨트롤러 (mesh corner) |
| **L1 TLB** | 48 엔트리, fully associative, 1 cycle |
| **L2 TLB** | 1024 엔트리, 4-way, 3 cycles |
| **Midgard L1 VLB** | 48 엔트리, fully associative, 1 cycle |
| **Midgard L2 VLB** | 16 VMA 엔트리, 3 cycles |
| **Midgard MLB** | 메모리 컨트롤러당 최대 32 엔트리 (전체 **128 엔트리**) |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2021ISCA-summarize/rebooting-virtual-memory-with-midgard.md|전체 요약 보기]]
