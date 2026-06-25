---
tags: [paper, 2024, 2024MICRO, topic/cache, topic/dram, topic/virtual-memory]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO) 2024"
year: 2024
summary_path: "../paper-summaries/2024MICRO-summarize/distributed-page-table-harnessing-physical-memory-as-an-unbounded-hashed-page-table.md"
---

# Distributed Page Table: Harnessing Physical Memory as An Unbounded Hashed Page Table

**Venue:** IEEE/ACM International Symposium on Microarchitecture (MICRO) 2024
**저자:** Osang Kwon, Yongho Lee, Junhyeok Park, Sungbin Jang, Byungchul Tak, Seokin Hong (Sungkyunkwan University; Kyungpook National University)

## 개요

- 가상 메모리 시스템의 핵심 구성 요소인 페이지 테이블은 가상 주소를 물리 주소로 변환(address translation)하는 역할을 수행하며, 메모리 집약적 응용이 증가하면서 기존 Radix Page Table(RPT)의 구조적 한계가 부각되고 있다
- RPT는 다중 레벨 트리 구조로 인해 TLB miss 시 순차적 메모리 접근(4-level PTW)이 필요하며, 불규칙한 메모리 접근 패턴에서 성능 병목이 된다(Fig.1)
- Hashed Page Table(HPT)은 해시 함수로 단일 메모리 접근으로 주소 변환을 가능하게 하지만, 세 가지 근본적 한계가 존재한다: (1) 해시 충돌 관리 어려움, (2) 큰 연속 물리 메모리 공간 할당 필요, (3) VPN 저장으로 인한 PTE 엔트리 크기 증가 및 캐시 적중률 저하(Fig.2)
- 최신 HPT 연구인 ECPT(Elastic Cuckoo Page Table)는 cuckoo hashing을 도입했으나 여전히 연속 메모리 할당이 필요하며, ME-HPT(Memory-Efficient HPT)는 chunk 크기 확장 시 빈번한 PTE 마이그레이션으로 페이지 할당당 평균 7.5~13.9회 마이그레이션이 발생(Fig.3)
- PTE 마이그레이션은 그래프 워크로드에서 5.3%, 일반 워크로드에서 57.2%, 임의 접근에서 4.4%, XS에서 41%의 실행 시간 증가를 초래하며, 다중 코어에서 CWC(Cuckoo Walk Cache) 일관성 문제를 야기한다(Fig.3)

## 방법론

### 3.1. 주소 변환 흐름

- VPN 태그와 PID를 해시 함수의 입력으로 사용하여 PTE 페이지의 물리 프레임 번호(PFN)를 결정(Fig.5)
- VA를 세 필드로 분할: VPN tag(33비트) + PTE offset(9비트, 2MB 영역 내 512 PTE) + page offset(12비트)
- PID를 hash seed로 사용하여 프로세스 간 충돌 방지
- PTE offset은 4KB PTE 페이지 내에서 특정 PTE의 위치를 지정

### 3.2. PTE 할당 과정

- Frame bitmap으로 대상 물리 프레임의 가용 여부 확인(Fig.6)
- Free frame이면 해당 프레임을 PTE 페이지로 할당하고 PTE offset으로 위치 지정
- 이미 할당된 프레임이면 address collision 해결 기법(SOA, CVA, CPD) 적용
- Bitmap 구조: 각 엔트리는 (Free, PTE) 비트로 구성 — (1,0)은 free, (0,0) 또는 (0,1)은 할당됨

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1. Strided Open Addressing(SOA)

- 충돌이 발생한 프레임이 어떤 페이지 크기(4KB, 2MB, 1GB)에 할당되어 있는지 확인한 후 적절한 stride로 탐색(Fig.7)
- 세 가지 stride 값(1, 512, 256K)을 사용하여 다양한 페이지 크기에 대응
- 예: 4KB 페이지와 충돌 시 stride=1로 연속 프레임 탐색, 2MB large page와 충돌 시 stride=512로 2MB 범위 밖 탐색
- SOA가 현재 stride로 탐색에 실패하면 더 큰 stride로 전환, MAX_SOA_STEP까지 반복
- 프레임 bitmap의 free 비트를 빠르게 확인하여 구현 가능하며, 탐색 오버헤드는 실질적으로 무시 가능

### 4.2. Collision-Aware Virtual Address Allocation(CVA)

- 물리 프레임이 아닌 가상 주소 영역을 선택하여 충돌 회피(Fig.8)
- 메모리 할당 시 충돌이 없는 2MB 가상 메모리 영역을 탐색하여 해당 영역의 VPN 태그에 대해 해시 → PFN이 free인지 확인
- 가상 주소 공간은 물리 메모리보다 훨씬 넓어 충돌 회피 가능성이 높음
- MAX_CVA_SIZE(할당 상한)와 MAX_CVA_CNT(최대 탐색 횟수)로 탐색 오버헤드 제한
- Demand paging 환경에서는 선할당(lazy 할당 전 사전 할당)이나 SOA/CPD와의 협력으로 대응 가능

### 4.3. Collided Page Displacement(CPD)

- SOA와 CVA로도 해결되지 않는 충돌에 대해 충돌된 물리 프레임의 데이터 페이지를 다른 프레임으로 마이그레이션(Fig.9)
- Reverse map을 활용하여 마이그레이션 대상 페이지의 PTE 주소를 직접 획득
- PTE 페이지 자체는 마이그레이션하지 않음 (페이지 테이블의 unmovable 특성 유지)
- 마이그레이션 불가능한 페이지(I/O 드라이버, 커널 컴포넌트)의 경우 SOA와 협력하여 마이그레이션 가능한 후보 페이지를 탐색

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2024MICRO-summarize/distributed-page-table-harnessing-physical-memory-as-an-unbounded-hashed-page-table.md|전체 요약 보기]]
