---
tags: [paper, 2020, 2020MICRO, topic/cache, topic/dram, topic/rowhammer, topic/security, topic/virtual-memory]
venue: "53rd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '20)"
year: 2020
summary_path: "../paper-summaries/2020MICRO-summarize/pthammer-cross-user-kernel-boundary-rowhammer-through-implicit-accesses.md"
---

# PThammer: Cross-User-Kernel-Boundary Rowhammer through Implicit Accesses

**Venue:** 53rd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '20)
**저자:** Zhi Zhang, Yueqiang Cheng, Dongxi Liu, Surya Nepal, Zhi Wang, Yuval Yarom (University of New South Wales, Data61/CSIRO, Baidu Security, Florida State University, University of Adelaide)

## 개요

- Rowhammer는 DRAM의 하드웨어 취약점으로, 동일한 메모리 주소에 대한 반복적 접근이 인접 메모리 위치의 비트 플립(bit flip)을 유발할 수 있음
- Rowhammer 공격은 시스템의 모든 메모리 보호를 우회하여 공격자가 데이터의 무결성과 기밀성을 침해할 수 있으며, 특권 승계(privilege escalation), 샌드박스 탈출, 암호화 키 유출 등에 활용 가능
- 기존의 소프트웨어 기반 방어 기법(CTA 등)은 공간적 근접성(spatial proximity)을 활용하여 공격자가 민감한 데이터 근처의 메모리 위치에 접근하는 것을 차단하는 것에 기반
  - CTA: 페이지 테이블 메모리를 DRAM의 별도 영역에 할당하여 비特权 사용자가 접근 가능하지 않은 영역에 배치
  - 이러한 방어는 공격자가 exploit 가능한 hammer row에 대한 접근 권한을 박탈하는 것을 전제로 함
- 기존 Rowhammer 공격의 핵심 제약: 공격자가 exploit 가능한 hammer row에 대한 접근 권한(access permission)을 가져야 함 (explicit hammer)
- Figure 1에서 공격자 E가 hammer row에 직접 접근하는 것이 explicit hammer이며, 이는 기존 모든 Rowhammer 공격의 전제 조건

## 방법론

### 3.1. 페이지 테이블 워크를 이용한 Implicit Hammer

- 현대 x86 프로세서에서 프로그램이 메모리에 접근하면 주소 번역이 수행됨:
  1. TLB(Translation-Lookaside Buffer)에서 해당 물리 주소 검색
  2. TLB miss 시 paging-structure cache에서 부분 주소 매핑 검색
  3. 부분 매핑도 없는 경우 페이지 테이블 워크(page-table walk) 수행
- 페이지 테이블 워크에서 L1PTE는 DRAM에서 직접 읽힘 → 이것이 implicit hammer의 핵심
- PThammer는 다음 세 가지 요소를 결합하여 공격 수행:
  1. TLB eviction set으로 특정 가상 주소의 TLB 엔트리 제거
  2. LLC(Last-Level Cache) eviction set으로 L1PTE를 캐시에서 제거
  3. 해당 가상 주소에 접근 → 프로세서가 페이지 테이블 워크를 수행 → L1PTE가 DRAM에서 읽힘

### 3.2. Eviction Set 구성 및 LLC 캐시 제거 (Section III-D)

- **최소 Eviction Set 크기 결정 (오프라인 단계):**
  - TLB: Algorithm 1을 사용하여 최소 eviction set 크기 결정. 4-way L1dTLB와 L2sTLB에서 12개 이상의 엔트리가 일관되게 높은 eviction rate 달성 (Figure 3)
  - LLC: 캐시 연관도(associativity)보다 1 큰 크기로 eviction set 선택. Lenovo(12-way LLC)는 13개, Dell(16-way LLC)는 17개 엔트리 사용 (Figure 4)

- **완전한 Eviction Set 풀 준비 (Algorithm 2):**
  - Superpage가 활성화된 경우: 가상 주소와 물리 주소의 최하위 21비트가 동일 → 물리 주소 비트 0-20을 알 수 있음 → 캐시 셋 인덱스 결정 가능
  - Superpage가 비활성화된 경우: 최하위 12비트(4 KiB 페이지 오프셋)만 공유 → 캐시 셋 인덱스의 비트 6-11만 알 수 있음 → 기존 기법[14]을 활용하여 잠재적으로 일치하는 메모리 라인을 그룹핑

- **타겟 LLC Eviction Set 선택 (Algorithm 2):**
  - 풀에서 L1PTE와 동일한 page offset을 가진 eviction set을 수집 (Line 14)
  - 수집된 각 eviction set에 대해 프로파일링 함수 적용 (Lines 2-11):
    - eviction set의 모든 메모리 라인에 접근하여 L1PTE를 LLC에서 flush
    - 관련 TLB 엔트리를 flush
    - targetaddr 접근 지연 시간 측정
  - 최대 지연時間を 유발하는 eviction set을 선택 (Lines 17-18) → 이것이 L1PTE를 flush하는 eviction set

### 3.3. 전체 공격 흐름

- 반복적으로 두 개의 가상 주소 쌍을 선택
- 각 쌍에 대해:
  1. LLC eviction set으로 해당 주소의 L1PTE를 캐시에서 제거
  2. TLB eviction set으로 관련 TLB 엔트리 제거
  3. 가상 주소에 접근 → 프로세서가 페이지 테이블 워크 수행
  4. L1PTE가 DRAM에서 읽힘 → hammer row에 반복적 접근 발생
  5. 인접한 victim row에 비트 플립 유발
- Superpage 사용 시 eviction set 구성이 더 빠르게 수행 가능

## 핵심 기여

- **핵심 기여:** Implicit hammer라는 새로운 Rowhammer 공격 클래스를 처음으로 제시하고, PThammer를 통해 실용적 공격 입증
- **공격의 의미:** 모든 소프트웨어 기반 Rowhammer 방어의 핵심 가정(premise)을 무효화 — 공격자가 hammer row에 대한 접근 권한이 없어도 공격 가능
- **실용적 위협:** 현대 프로세서의 주소 번역 메커니즘을 이용하여 비特权 사용자가 커널 특권을 탈취할 수 있음
- **방어에 대한 시사점:** 소프트웨어 기반 방어만으로는 충분하지 않으며, 하드웨어 수준의 방어 메커니즘이 필요함을 시사
- **확장성:** PThammer 외에도 시스템 콜 핸들러 등 다른 하드웨어/소프트웨어 기능을 이용한 추가 implicit hammer 공격 가능성을 시사

## 주요 결과

- **시스템 환경:** Ubuntu 16.04 기반 구현
- **하드웨어 플랫폼 (Table I):**

| 모델 | 아키텍처 | CPU | TLB | LLC |
|------|----------|-----|-----|-----|
| Lenovo T420 | SandyBridge | i5-2540M | 4-way L1d, 4-way L2s | 12-way, 3 MiB |
| Lenovo X230 | IvyBridge | i5-3230M | 4-way L1d, 4-way L2s | 12-way, 3 MiB |
| Dell E6420 | SandyBridge | i7-2640M | 4-way L1d, 4-way L2s | 16-way, 4 MiB |

- **커널 모듈:** 물리 주소 매핑, cache-line eviction 이벤트 카운트(longest_lat_cache.miss), eviction set 구성에 활용
- **소프트웨어 방어 우회:** CTA, ANVIL, TAO, PDDRA 등 기존 소프트웨어 기반 방어 기법 모두 우회 가능

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]
- [[paper-wiki/concepts/security.md|Security]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2020MICRO-summarize/pthammer-cross-user-kernel-boundary-rowhammer-through-implicit-accesses.md|전체 요약 보기]]
