---
tags: [paper, 2018, 2018ISCA, topic/cache, topic/virtual-memory]
venue: "45th Annual International Symposium on Computer Architecture (ISCA '18)"
year: 2018
summary_path: "../paper-summaries/2018ISCA-summarize/seesaw-using-superpages-to-improve-vipt-caches.md"
---

# SEESAW: Using Superpages to Improve VIPT Caches

**Venue:** 45th Annual International Symposium on Computer Architecture (ISCA '18)
**저자:** Mayank Parasar (Georgia Institute of Technology), Abhishek Bhattacharjee (Rutgers University), Tushar Krishna (Georgia Institute of Technology)

## 개요

- L1 캐시는 CPU 및 coherence 요청의 대부분을 서비스하며 시스템 성능과 에너지에 핵심적
- 현대 L1 캐시는 **Virtual Indexed, Physically Tagged (VIPT)** 방식을 사용하여 TLB 조회와 캐시 조회를 병렬로 수행
- **핵심 문제**: VIPT 캐시는 캐시 인덱스 비트가 page offset 필드에 완전히 포함되어야 하므로, 캐시 set 수가 제한됨
  - 예: x86-64 시스템, 4KB 기본 페이지 → page offset 12비트, 캐시 라인 64바이트 → set index에 6비트만 사용 가능 → 최대 64 set
  - 따라서 캐시 용량 증가는 **associativity 증가**에만 의존
- 과도한 associativity의 문제:
  - access time 증가 (SRAM 컴파일러 기반 측정에서 2-way에서 8-way로 증가 시 8.3% 느려짐)
  - hit rate 향상은 미미 (workload에 따라 0.1~2.5% 수준)
  - 에너지 소비 증가 (access 에너지와 면적 모두 약 3배 증가, 연산 에너지 3.76배)
- 상용 프로세서 (AMDZen, Intel Skylake)의 L1 I/D 캐시는 모두 32KB, 8-way VIPT로 고정되어 associativity 확장의 한계를 시사

## 방법론

### 3.1. Superpage-Enhanced Set Indexing
- Superpage 접근 시 page offset의 상위 비트를 캐시 set index로 활용
- 4KB base page: 64 set (6비트 index) × 8 way = 512 entry
- 2MB superpage: 2^{15} set × 8 way 또는 2^{16} set × 4 way 등 다양한 구성 가능
- 기본 세팅: 4KB → 8-way, 2MB → 4-way, 1GB → 2-way (set 수는 동일)

### 3.2. 디코딩 및 조회 메커니즘
- **TLB 연동**: TLB가 superpage 여부를 판별 → superpage hit 시 "superpage bit" 설정
- **Set index 생성**: page offset의 상위 비트를 캐시 인덱스로 사용
- **Way 마스크**: superpage hit 시 적은 way만 활성화 → 나머지 way는 clock gating으로 비활성화
- 물리 주소의 set index가 동일한 superpage entry끼리만 충돌 → 높은 set associativity 필요 없음

### 3.3. Coherence Lookup 최적화
- Coherence 메시지는 물리 주소를 사용 → TLB 조회 불필요
- 기존: superpage/base page 관계없이 모든 way 조회
- SEESAW: coherence 조회 시에도 superpage 여부에 따라 적은 way로 조회 가능
- 모든 coherence lookup의 energy 절감 효과

### 3.4. 하드웨어 오버헤드
- SEESAW 디코더는 기존 VIPT 캐시에 비해 지연 없음
- 세 가지 구성요소:
  - TLB: superpage 판별 정보를 캐시 디코더에 전달
  - 디코더: set index 생성 및 way 마스크 결정
  - 캐시: way 마스크에 따라 일부 way만 조회
- 면적 오버헤드: 미미 (기존 SRAM 컴파일러 기반)

## 핵심 기여

- **핵심 기여**: superpage의 넓은 page offset을 활용하여 VIPT 캐시의 associativity 제약을 극복하는 최초의 접근법
- **성능 향상**: hit rate 1~5% 향상, access latency 및 energy 절감
- **하드웨어 오버헤드**: 미미하며, 기존 VIPT 캐시에 쉽게 통합 가능
- **OS/앱 변경 불필요**: 기존 superpage 지원만 있으면 동작
- **실용성**: 상용 프로세서의 L1 캐시에 적용 가능한 현실적인 솔루션

## 주요 결과

- **평가 방법**: 상용 22nm SRAM 컴파일러를 사용하여 다양한 캐시 구성의 latency, energy, area 측정
- **시뮬레이터**: gem5 시뮬레이터 기반, x86-64 아키텍처 모델링
- **OS**: Linux 커널에서 superpage 할당 지원
- **하드웨어 구성**: SEESAW 디코더 + 기존 VIPT 캐시에 통합

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2018ISCA-summarize/seesaw-using-superpages-to-improve-vipt-caches.md|전체 요약 보기]]
