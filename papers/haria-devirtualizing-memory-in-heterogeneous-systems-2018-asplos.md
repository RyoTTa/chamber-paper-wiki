---
tags: [paper, 2018, 2018ASPLOS, topic/virtual-memory, topic/gpu, accelerators, identity-mapping, iommu]
venue: "ASPLOS '18"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/devirtualizing-memory-in-heterogeneous-systems.md"
---

# Devirtualizing Memory in Heterogeneous Systems

**Venue:** 23rd International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '18)
**저자:** Swapnil Haria, Mark D. Hill, Michael M. Swift

## 개요

DVM(Devirtualized Memory)은 이종 시스템에서 가속기의 **가상 메모리 오버헤드를 대폭 감소**시키는 새로운 메모리 관리 방식입니다. Identity Mapping(VA==PA)을 통해 주소 변환을 제거하고, Permission Entry로 권한 검증만 수행하여 가상 메모리의 보호는 유지하면서 성능을 획기적으로 향상시킵니다.

**핵심 문제:** 그래프 처리 가속기에서 128-entry TLB 사용 시 TLB 미스율 21% → 2MB 페이지 사용해도 1%만 개선. CPU에서도 큰 메모리 워크로드에서 주소 변환 오버헤드 최대 50%.

## 방법론

### Identity Mapping (VA==PA)
- 물리 주소와 가상 주소가 동일하도록 메모리 할당 → 주소 변환 필요성 제거
- Eager contiguous allocation: 물리 프레임을 즉시 예약하고 VA==PA로 매핑
- Fallback: 적합한 주소 범위 없으면 기존 demand paging으로 복귀

### Permission Entry (PE)
- 새로운 페이지 테이블 엔트리 형식: 8바이트, 16개 권한 필드
- 권한의 연속성을 활용하여 컴팩트한 페이지 테이블 구성
- L1 PTE 98% 이상 제거 → 페이지 테이블 48-68KB로 축소

### Access Validation Cache (AVC)
- TLB와 Page Walk Cache를 대체하는 1KB 캐시
- 컴팩트한 페이지 테이블로 높은 히트율 → 메모리 접근 없이 페이지 워크 완료

### Read Preload 최적화
- 읽기 접근 시 DAV와 병렬로 데이터 preload 실행
- Identity-mapped 페이지에서는 preload가 실제 메모리 접근이 됨

## 핵심 기여

1. **Identity Mapping 기반 가상 메모리 디바이터얼라이제이션**: 주소 변환을 권한 검증으로 대체
2. **Permission Entry로 컴팩트 페이지 테이블**: 페이지 테이블 크기 98% 축소
3. **AVC로 TLB/PWC 대체**: 1KB 크기로도 높은 성능
4. **CPU로 확장 (cDVM)**: 이종 시스템 전체에 적용 가능

## 주요 결과

- **그래프 가속기**: DVM-PE 평균 3.5% 오버헤드 (기존 VM 대비 32x 향상)
- **DVM-PE+ (preload)**: 평균 1.7% 오버헤드 → 이상적 구현에 근접
- **에너지**: DVM-PE 76% 동적 에너지 감소
- **페이지 테이블**: 616KB-13340KB → 48-68KB로 축소
- **CPU (cDVM)**: VM 오버헤드 29% → 5%로 감소
- **Identity mapping 성공률**: 16-64GB 시스템에서 95-97%

## 한계점

- Eager paging으로 인한 메모리 단편화 위험
- Copy-on-Write 시 identity mapping 깨질 수 있음 (첫 쓰기 시 복사본 생성)
- Meltdown/Spectre와의 호환성 문제 (preloader가 미세 아키텍처 상태 변경 가능)

## 관련 개념

- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]] — 가상 메모리 오버헤드 및 TLB
- [[paper-wiki/concepts/gpu.md|GPU]] — 가속기 메모리 관리
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]] — NDP 가속기와의 관련성
