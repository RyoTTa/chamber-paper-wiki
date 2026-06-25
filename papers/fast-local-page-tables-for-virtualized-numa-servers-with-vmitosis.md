---
tags: [paper, 2021, 2021ASPLOS, topic/virtual-memory]
venue: "Proceedings of the 26th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '21)"
year: 2021
summary_path: "../paper-summaries/2021ASPLOS-summarize/fast-local-page-tables-for-virtualized-numa-servers-with-vmitosis.md"
---

# Fast Local Page-Tables for Virtualized NUMA Servers with vMitosis

**Venue:** Proceedings of the 26th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '21)
**저자:** Ashish Panwar (Indian Institute of Science), Reto Achermann (University of British Columbia), Arkaprava Basu (Indian Institute of Science), Abhishek Bhattacharjee (Yale University), K. Gopinath (Indian Institute of Science), Jayneel Gandhi (VMware Research)

## 개요

- 가상화된 NUMA 서버에서 애플리케이션이 비균일 메모리 접근 (NUMA) 지연 시간으로 성능 저하를 경험
- 기존 NUMA 최적화는 애플리케이션 데이터에 초점을 맞추었으나, 커널 데이터 구조(특히 페이지 테이블)의 배치는 무시되어 왔음
- 큰 메모리 워크로드에서 TLB 미스율이 높아 빈번한 2D 페이지 테이블 워크 발생 (가상화 환경에서 게스트 페이지 테이블(gPT) + 확장 페이지 테이블(ePT) 탐색 필요)
- 2D 페이지 테이블 워크는 최대 24회 메모리 접근 필요 (5단계 페이지 테이블에서는 35회로 증가), 각 접근이 직렬로 처리되어 메모리 수준 병렬성 활용 불가
- 단일 소켓 머신에서 페이지 테이블 워크 오버헤드는 10-50%이나, 다중 소켓에서는 **최대 3.1배**까지 지연
- Thin 워크로드의 NUMA 소켓 간 마이그레이션 시 커널 데이터 구조가 고정되어 페이지 테이블이 원격에 배치됨
- Wide 워크로드는 여러 소켓을 사용하지만 단일 복사본의 페이지 테이블을 공유하여 원격 접근 불가피

## 방법론

### 3.1. 페이지 테이블 마이그레이션

- **목적**: Thin 워크로드가 NUMA 소켓 간 이동될 때 원격 페이지 테이블 접근 제거
- **동작 방식**:
  - 페이지 테이블 페이지의 각 PTE에 대해 어느 소켓을 가리키는지 추적하는 메타데이터 유지
  - 리프(leaf) PTE가 원격 소켓을 가리키는 비율이 기준을 초과하면 해당 페이지 테이블 페이지 마이그레이션
  - 리프 수준에서 루트 수준으로 자동 전파되는 상향식 마이그레이션
- **NV 구성 (NUMA-visible)**: 게스트 OS의 AutoNUMA 데이터 페이지 마이그레이션을 활용하여 gPT 마이그레이션 트리거
- **NO-P/NO-F 구성 (NUMA-oblivious)**: 하이퍼바이저의 데이터 페이지 마이그레이션이 gPT를 자동으로 마이그레이션하며, ePT는 별도로 마이그레이션
- Linux/KVM에서 AutoNUMA 확장으로 구현, 각 gPT 페이지 마이그레이션 시 mmap_sem 쓰기 락 획득

### 3.2. 페이지 테이블 복제

- **목적**: Wide 워크로드의 여러 소켓에서 로컬 주소 변환 보장
- **ePT 복제 (모든 구성 공통)**:
  - ePT 위반 핸들러 확장하여 모든 NUMA 소켓에 적극적(eagerly) 복제 할당
  - 소켓별 "페이지 캐시" 도입으로 원하는 소켓에서 복제 할당 보장
  - 마스터 ePT 수정 시 모든 복제본에 즉시 전파 + TLB 플러시로 변환 일관성 유지
  - 접근/더티 비트는 모든 복제본에서 OR 연산으로 조회, 일관성 보장
- **gPT 복제 (NV 구성)**: Mitosis 오픈소스 활용, NUMA 토폴로지 노출 시 직접 복제
- **gPT 복제 (NO-P 구성)**: 패러 가상화 - 하이퍼바이저에 vCPU의 물리적 소켓 ID 조회, 소켓별 gPT 복제 할당
- **gPT 복제 (NO-F 구성)**: 완전 가상화 - 마이크로벤치마크로 가상 NUMA 그룹 구성, vCPU 간 캐시라인 전송 지연 측정으로 물리적 토폴로지 추론
  - Table 4: vCPU 쌍 간 캐시라인 전송 시간 (50-126ns), 낮은 지연의 그룹핑으로 물리적 토폴로지 매핑

### 3.3. NO-F 완전 가상화 상세

- 하이퍼바이저 지원 없이 게스트 OS 내부에서 gPT 복제
- 통신 지연 기반 가상 NUMA 그룹 구성:
  - 모든 vCPU 쌍 간 캐시라인 전송 레이턴시 측정 (192x192 매트릭스)
  - 동일 그룹 내 vCPU는 낮은 레이턴시, 다른 그룹은 높은 레이턴시
  - 물리적 토폴로지와 일대일 대응 보장
- 하이퍼바이저의 로컬 메모리 할당 정책 활용하여 각 그룹의 로컬 소켓에 복제 할당
- NO-P 대비 배포 용이, NO-F 대비 성능 보장 (일반적으로 동일 성능)

## 핵심 기여

- vMitosis는 가상화된 NUMA 서버에서 2D 페이지 테이블의 NUMA 효과를 효과적으로 제거
- **Thin 워크로드**: 페이지 테이블 마이그레이션으로 **최대 3.1x** 성능 향상
- **Wide 워크로드**: 페이지 테이블 복제로 **최대 1.6x** 성능 향상 (NUMA-visible), **1.4x** (NUMA-oblivious)
- 커널 데이터 구조의 배치가 점점 더 중요해지고 있음을 입증
- NUMA-visible과 NUMA-oblivious 모두 지원하는 실용적 시스템
- **의의**: 가상화 환경에서 커널 페이지 테이블의 NUMA 인식 관리의 첫 번째 체계적 해결책 제시

## 주요 결과

- Linux/KVM 기반 구현, Linux v4.17 커널 사용
- ePT/gPT 마이그레이션: AutoNUMA 확장으로 구현
- ePT 복제: ePT 위반 핸들러 확장, per-VM spinlock으로 직렬화
- gPT 복제: Mitosis 오픈소스 활용 (NV), 패러/완전 가상화 모듈 추가 (NO-P/NO-F)
- 총 메모리 오버헤드: 4소켓 시스템에서 1.2% (4KiB 페이지, 4회 복제)
- mprotect 시스템 호출에서 복제 오버헤드 가장 큼 (4MiB에서 0.28x throughputs 저하)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2021ASPLOS-summarize/fast-local-page-tables-for-virtualized-numa-servers-with-vmitosis.md|전체 요약 보기]]
