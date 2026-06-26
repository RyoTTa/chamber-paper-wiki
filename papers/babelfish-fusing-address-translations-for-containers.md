---
tags: [paper, 2020, 2020ISCA, topic/cache, topic/dram, topic/virtual-memory]
venue: "ACM/IEEE 47th Annual International Symposium on Computer Architecture (ISCA) 2020"
year: 2020
summary_path: "../paper-summaries/2020ISCA-summarize/babelfish-fusing-address-translations-for-containers.md"
---

# BabelFish: Fusing Address Translations for Containers

**Venue:** ACM/IEEE 47th Annual International Symposium on Computer Architecture (ISCA) 2020
**저자:** Dimitrios Skarlatos, Umur Darbaz, Bhargava Gopireddy, Nam Sung Kim, Josep Torrellas (University of Illinois at Urbana-Champaign)

## 개요

- 클라우드 컴퓨팅이 VM에서 컨테이너로 급속히 전환 — 컨테이너는 단일 커널을 공유하여 메모리 리소스 절약 및 오버헤드 감소
- 클라우드 제공업체는 소수의 코어에서 수백 개의 컨테이너를 과다 구독(oversubscribed) 방식으로 운영
- 서버리스 컴퓨팅(FaaS) 패러다임 확산 — Amazon Lambda, Azure Functions, Google Cloud Functions 등에서 짧은 코드 스니펫을 이벤트 트리거로 실행
- 컨테이너 환경에서 동일한 VPN-to-PPN 변환(동일 permission bits 포함)이 TLB와 페이지 테이블에서 광범위하게 중복(replicated)
  - 컨테이너 스케일아웃 시 동일 애플리케이션이 공통 데이터 세트의 다른 섹션에서 실행 → 대량의 페이지 공유
  - fork 기반 컨테이너 생성으로 변환 복제
  - 마운트된 디렉토리와 파일 메모리 매핑을 통한 무상태(stateless) 접근
- 기존 TLB/페이지 테이블 하드웨어/소프트웨어는 소수의 다양한 프로세스를 위해 설계 — per-process tagged TLB, 분리된 per-process 페이지 테이블, lazy 페이지 테이블 관리

**Quantitative Analysis:**
- 8코어 프로세서에서 Docker 컨테이너 실행 환경에서 분석
- 컨테이너화된 워크로드의 변환 중 53%가 공유 가능(shareable)
- 서버리스 워크로드의 변환 중 93%가 공유 가능
- 컨테이너화된 데이터 서빙 워크로드의 평균/테일 지연 시간 각각 11%/18% 증가 초래

## 방법론

### 3.1. TLB 엔트리 공유

- 기존 TLB: 동일 {VPN, PPN} 변환이 서로 다른 PCID로 태깅되어 복제 → 컨테이너 환경에서 TLB thrashing 초래
- BabelFish: CCID 필드를 각 TLB 엔트리에 추가 — 동일 CCID 그룹의 프로세스가 동일 엔트리 공유
- OS가 프로세스를 스케줄링할 때 해당 프로세스의 CCID를 레지스터에 로드 (PCID와 유사)
- TLB 접근 시 VPN 태그 + CCID 매칭 — 매칭되면 PPN 반환

**Ownership-PrivateCopy (O-PC) 필드:**
- Ownership (O) 비트: 설정 시 해당 페이지가 프라이빗 — PCID 매칭도 필요
- PrivateCopy (PC) 비트마스크: 32비트, CCID 그룹 내 프라이빗 복사본을 가진 프로세스별 1비트
- OR PC 비트: PC 비트마스크의 논리 OR — 공유 엔트리에서 프라이빗 복사본 존재 여부 빠른 확인
- CoW 쓰기 시 OS가 해당 프로세스의 pid를 MaskPage의 pid_list에 추가 → PC 비트마스크에 비트 할당
- 최대 32개 프라이빗 복사본 지원 — 저장 비용 최소화

**TLB 조회 과정:**
1. VPN 태그로 인덱싱 → CCID 매칭 검사
2. 매칭 엔트리에서 O-PC 및 PCID 필드 검사
3. O=1 (프라이빗): PCID 일치 필요
4. O=0 (공유): 프로세스의 PC 비트 확인 — 비트 설정됨 → 프라이빗 복사본 존재하므로 사용 불가, 비트 해제됨 → 공유 엔트리 사용 가능

### 3.2. 페이지 테이블 엔트리 공유

- 동일 {VPN, PPN} 변환과 permission bits를 가진 다른 프로세스의 페이지 테이블 엔트리를 하나로 병합
- 기존 Linux: 프로세스 생성 시 lazy하게 페이지 테이블 엔트리 업데이트 → 컨테이너 환경에서 중복 엔트리 대량 발생
- BabelFish: 공유 가능한 PTE를 단일 엔트리로 통합 — active LRU 리스트의 shareable active PTE 30~57% 감소

**MaskPage 구조:**
- 512개 PTE를 하나의 PMD 테이블 세트로 관리
- 각 MaskPage에 PC 비트마스크와 pid_list 저장
- 페이지 테이블의 데이터 레이아웃 변경 없음 — OS 소프트웨어 구조체로 관리

### 3.3. Prefetching 및 캐시 관리

- BabelFish는 프로세스가 다른 프로세스의 TLB 엔트리를 L2 TLB와 캐시로 프리페치
- "Shared Hits" — 다른 프로세스가 가져온 L2 TLB 엔트리에 대한 히트 → 캐시 워밍 효과
- L1 TLB는 공유하지 않음 (보수적 설계) — 향후 확장 가능

## 핵심 기여

1. **컨테이너 환경의 주소 변환 중복 문제 최초 정량화:** 동일 {VPN, PPN} 변환이 컨테이너 간 광범위하게 복제됨을 확인 — 컨테이너화된 워크로드의 53%, 서버리스의 93%가 공유 가능
2. **CCID + O-PC 기반 TLB/페이지테이블 공유:** 가벼운 하드웨어 수정(0.4% 면적)으로 중복 변환 제거 — 기존 TLB 확장보다 효과적
3. **실질적 성능 향상:** 평균 지연 시간 11%, 테일 지연 시간 18%, 서버리스 함수 실행 시간 최대 55% 감소
4. **서버리스 컴퓨팅에 특히 효과적:** 함수 시작 시간 8% 감소, 실행 시간 10~55% 감소 — 짧은 수명의 함수에서 주소 변환 오버헤드 비중이 큰 영향
5. **최소 리소스 오버헤드:** 하드웨어 0.4% 면적, 소프트웨어 1300 LoC, 메모리 0.238% — 실용적 구현 가능성

## 주요 결과

- **소프트웨어:** Linux 커널에 BabelFish 페이지 테이블 공유 메커니즘 구현
  - MMU 모듈: 300 Lines of Code (LoC)
  - 페이지 폴트 핸들러: 200 LoC
  - 페이지 테이블 관리 연산: 800 LoC
  - Simics shadow 페이지 테이블에도 구현
- **하드웨어:** L2 TLB에 CCID와 O-PC 필드 추가 — baseline 코어 대비 면적 0.4% 오버헤드 (PC bitmask 제거 시 0.07%)
- **L2 TLB 파라미터 (22nm, CACTI 기반):**

| 항목 | Baseline | BabelFish |
|------|----------|-----------|
| 면적 | 0.030 mm² | 0.062 mm² |
| 접근 시간 | 327 ps | 456 ps |
| 동적 에너지 | 10.22 pJ | 21.97 pJ |
| 누설 전력 | 4.16 mW | 6.22 mW |

- **메모리 공간 오버헤드:** 0.238% (MaskPage + 16비트 카운터) — PC bitmask 제거 시 0.048%

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2020ISCA-summarize/babelfish-fusing-address-translations-for-containers.md|전체 요약 보기]]
