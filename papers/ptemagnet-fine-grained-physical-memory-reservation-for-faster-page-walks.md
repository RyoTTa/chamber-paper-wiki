---
tags: [paper, 2021, 2021ASPLOS, topic/dram, topic/virtual-memory]
venue: "ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS) 2021"
year: 2021
summary_path: "../paper-summaries/2021ASPLOS-summarize/ptemagnet-fine-grained-physical-memory-reservation-for-faster-page-walks-in-public-clouds.md"
---

# PTEMagnet: Fine-Grained Physical Memory Reservation for Faster Page Walks in Public Clouds

**Venue:** ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS) 2021
**저자:** Artemiy Margaritov (University of Edinburgh), Dmitrii Ustiugov (University of Edinburgh), Amna Shahab (University of Edinburgh), Boris Grot (University of Edinburgh)

## 개요

- 클라우드 환경에서 데이터 분석 프레임워크, 키-값 스토어, 데이터베이스 등 대규모 인메모리 데이터셋을 처리하는 애플리케이션이 급격히 증가하고 있으며, 이로 인해 가상화된 환경에서의 주소 변환(Address Translation) 병목이 새로운 문제로 부상
- 가상화 환경에서의 중첩 페이지 워크(Nested Page Walk)는 게스트 PT와 호스트 PT를 모두 순회해야 하므로 높은 레이턴시를 유발하며, 이는 기존 연구에서 이미 보고된 바 있음
- 워크로드 코로케이션(Colocation) 시 리눅스 메모리 할당기가 여러 애플리케이션의 요청을 교차 처리하면서 게스트 물리 주소 공간이 심각하게 조각화(Fragmentation)됨
- 조각화된 게스트 물리 주소 공간은 호스트 가상 주소 공간으로 전이되어, 호스트 PT의 캐시 평가_footprint를 크게 증가시킴
- 호스트 PT의 지나친 캐시 footprint로 인해 페이지 워크 중 호스트 PTE(hPTE) 접근이 메인 메모리에서 serving될 확률이 높아져, 페이지 워크 레이턴시가 크게 증가
- 기존 연구들은 호스트 PT 조각화의 근본 원인과 그 성능 영향을 체계적으로 분석하지 않았으며, 호스트 PTE의 캐시 로컬리티를 개선하는 효율적인 방법을 제안하지 못함

## 방법론

### 3.1. 호스트 PT 조각화 메커니즘 분석
- 가상화 환경에서 호스트 OS는 VM을 하나의 프로세스로 취급하며, 게스트 물리 주소 공간을 VM 프로세스의 가상 메모리로 관리
- 게스트 OS의 메모리 할당기가 여러 애플리케이션의 할당 요청을 교차 처리하면, 인접한 가상 페이지들이 물리 주소 공간에서 불연속적으로 배치됨
- 조각화된 게스트 물리 주소 공간은 호스트 가상 주소 공간으로 전이되어, 인접한 가상 페이지에 대한 호스트 PTE들이 여러 캐시 블록에 분산
- 호스트 PT 조각화 측정 지표: 한 캐시 블록에 저장된 gPTE에 대응하는 hPTE가 차지하는 평균 캐시 블록 수 (Figure 5)

### 3.2. 공간적 로컬리티와 캐시 효율성
- 네이티브 실행에서 PT 접근은 애플리케이션의 공간적 로컬리티를 상속: 인접한 가상 페이지의 PTE는 인접한 리프 노드에 위치하여 같은 캐시 블록에 패킹됨
- 캐시 블록 하나에 최대 8개의 인접 8바이트 PTE가 수용 가능 (Figure 3)
- 가상화 및 코로케이션 환경에서는 호스트 PT 조각화로 인해 gPTE는 높은 캐시 히트율을 보이지만, hPTE는 캐시 미스율이 높음极端한 경우 8페이지 그룹에 대해 1개 캐시 블록(gPTE) vs 8개 캐시 블록(hPTE) 필요

### 3.3. 세밀한 예약 기반 할당자 (Reservation-Based Allocator)
- PTEMagnet은 게스트 OS의 메모리 할당자를 수정하여 작은 가상 주소 영역(32KB 영역) 내에서 물리 메모리 할당의 조각화를 방지
- PaRT(Physical Reservation Table) 데이터 구조를 사용하여 각 32KB 영역의 물리 메모리 할당 상태를 관리
- 첫 페이지 폴트 시 32KB 물리 메모리를 buddy 할당자로부터 예약하고, 이후 같은 영역의 페이지 폴트는 빠른 PaRT 접근으로 대체
- 조각화 방지를 위해 인접 물리 페이지 할당을 보장하는 로직 구현

### 3.4. 메모리 관리 및 회수 메커니즘
- 높은 메모리 압력 시 미할당 페이지가 재활용될 수 있는 가능성 대비
- 미할당 페이지 비율이 실제로 매우 낮음(실행 중 0.2% 미만)으로 실질적 문제 없음
- 메모리 회수 메커니즘이 조각화된 메모리를 다른 애플리케이션의 예약에 사용하지 못하도록 보호

## 핵심 기여

- PTEMagnet은 가상화 및 코로케이션 환경에서 호스트 PT 조각화가 주소 변환 성능의 핵심 병목임을 최초로 규명
- 세밀한 예약 기반 할당자를 통해 호스트 PTE의 캐시 로컬리티를 개선하여 평균 4%, 최대 9% 성능 향상 달성
- 기존 시스템과 완전히 호환되는 레거시 프리저빙 소프트웨어 기법으로 실용적 배포 가능성 입증
- 성능 오버헤드 없이(오히려 메모리 할당 시간 0.5% 단축) 클라우드 환경에서의 주소 변환 성능을 크게 개선
- 클라우드 컴퓨팅 시장($350B→$800B 예상)에서 메모리 집약적 워크로드의 성능을 향상시키는 실용적 기여

## 주요 결과

- 구현 언어: C (게스트 OS 커널 모듈)
- 수정 대상: 리눅스 커널의 메모리 할당자(buddy allocator)와 연동되는 부분
- 주요 데이터 구조: PaRT(Physical Reservation Table), reservation group 관리
- 면적 오버헤드: PaRT 엔트리당 최소한의 메모리 사용
- 호환성: 기존 사용자 코드나 가상화 메커니즘(KVM 등) 수정 불필요
- 구현 코드 라인 수:约数百 줄 수준의 커널 패치

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2021ASPLOS-summarize/ptemagnet-fine-grained-physical-memory-reservation-for-faster-page-walks-in-public-clouds.md|전체 요약 보기]]
