---
tags: [paper, 2024, 2024ATC, topic/cache, topic/disaggregation, topic/dram, topic/nvm, topic/storage]
venue: "USENIX Annual Technical Conference (ATC) 2024"
year: 2024
summary_path: "../paper-summaries/2024ATC-summarize/atc24-cai.md"
---

# Ethane: An Asymmetric File System for Disaggregated Persistent Memory

**Venue:** USENIX Annual Technical Conference (ATC) 2024
**저자:** Miao Cai (Nanjing University of Aeronautics and Astronautics), Junru Shen (Hohai University), Baoliu Ye (Nanjing University)

## 개요

- **Persistent Memory (PM)의 등장**: PM은 초고속 (∼300ns latency), 제한된 용량 (≤512GB per DIMM slot), 높은 가격 ($3.27/GB)의 혁신적인 저장 기술
- **기존 PM 아키텍처의 한계 (Symmetric PM Architecture)**:
  1. **비싼 노드 간 상호작용 (Expensive Cross-node Interaction)**: 
     - 파일 시스템 데이터가 클러스터의 여러 머신에 분산되어 있어 서버 노드가 요청 처리 시 다른 노드와 상호작용 필요
     - CephFS 분석: 파일 경로 해석 시 65,535개 디렉토리 항목에서 노드 간 상호작용이 전체 실행 시간의 60.24% 차지, 6-컴포넌트 경로 해석 시 91.71% 차지
     - 상호작용 지연: ∼162µs (RDMA-over-RoCE 사용 시)
  2. **단일 노드의 취약한 성능 (Weak Single-node Capability)**:
     - 제조사 제한으로 머신당 PM DIMM 수 제한 → 총 PM 용량이 수 TB로 제한
     - PM 디바이스의 제한된 대역폭: 256B IO 크기로 4개의 병렬 쓰기만으로 대역폭 포화
     - 비균등 데이터 접근 패턴에서 핫 노드가 병목 → 전체 시스템 성능 저하
     - Octopus 테스트: Zipf 분포 적용 시 최대 2배까지 총 Throughput 감소
  3. **비싼 스케일아웃 성능 (Costly Scale-out Performance)**:
     - 단일 노드 약점을 보완하기 위해 더 많은 PM 머신 구매 필요
     - 추가 머신의 CPU/기기 장치가 과잉 provisioning → TCO 증가
     - MapReduce 애플리케이션에서 유연한 리소스 스케일링 어려움

## 방법론

### 3.1. Control-plane FS: Shared Log 기반

- **Shared Log 추상화**: 
  - MN이 모든 CN에 대한 중앙 집중식 뷰 제공 → 효율적 데이터 공유
  - 복잡한 제어 기능을 shared log에 위임 (linearizability, crash consistency, concurrency control)
- **Log Arena 메커니즘 (Figure 3)**:
  - mlog 영역을 arena로 분할, 각 arena는 mlog 저장을 위한 슬롯으로 구성
  - **세 가지 삽입 케이스**:
    - Case I: 이상적 케이스 (앞쪽 빈 슬롯 없음)
    - Case II: 앞쪽 빈 슬롯 존재 → pseudo mlog로 채움
    - Case III: 비동기 케이스 → 빈 슬롯 채우기 필요
  - **Optimizations**: arena 슬롯 수 < 동시 스레드 수, log playback 후 step (2) 수행
- **Durability 위임 (Section 4.1.1)**:
  - oplog = dlog (data log) + mlog (meta log)
  - dlog: 파일 경로, 자격 증명, 메타 객체 주소 등 저장
  - mlog: 8바이트 (12비트 cacheFS ID, 2바이트 경로 지문, 26비트 dlog 영역 오프셋, 9비트 dlog 크기, 1비트 플래그)
  - RDMA_WRITE로 dlog 쓰기 + RDMA_READ로 PCIe 버퍼 플러시 → 5.48µs 지연
- **Linearizability 위임 (Section 4.1.2)**:
  - log ordering으로 동시 syscall 실행을 순차 history로 변환
  - log arena으로 RDMA_CAS 경쟁 대폭 감소 → 선형적 throughput 확장
- **Coherence 위임 (Section 4.1.3)**:
  - File lineage 기반 log 의존성 검사
  - mlog skip table로 이전에 재생된 로그 건너뛰기
  - Collaborative log playback: 다른 log playback의 경로 해석 결과 재사용

### 3.2. Data-plane FS: Key-Value 스토리지

- **통합 Key-Value 스토리지 패러다임**:
  - 모든 파일 시스템 객체를 key-value 튜플로 변환
  - Key: 유일한 전체 경로
  - Value: 메타 객체 주소 + 상위 디렉토리 메타 객체 주소
  - 하드 링크: 대상 파일 메타 객체를 가리키는 포인터
  - 심볼릭 링크: 독립적인 메타 객체
- **Data Section 기반 파일 매핑**:
  - 세 가지 고정 크기 data section: 1GB, 2MB, 4KB
  - Extent: 논리적 블록의 물리적 블록으로의 연속 매핑
  - 파일 오프셋을 data section으로 변환 후 extent 포인터로 변환
- **Cuckoo Hash 테이블 기반 관리**:
  - 상수 시간 슬롯 탐색 → 병렬 데이터 검색 설계 용이
  - 글로벌 관리 (per-file 관리 아님)
  - 벡터 기반 KV get 인터페이스: 배치 파일 시스템 연산 지원

### 3.3. Data Path Disentanglement

- **병렬, 파이프라인 해시 탐색**:
  - Cuckoo hash의 두 슬롯 탐색은 메모리 접근 의존성 없음
  - 계산 작업 (해시 값, 대상 MN 계산)을 원격 메모리 접근과 겹침
  - Optimistic concurrency control: 슬롯 버전 번호로 무잠금 읽기
- **파일 경로 워크 (Figure 7)**:
  - 경로 components를 병렬로 해석하기 위해 path walk를 배치 dentry 탐색으로 분해
  - vec_kv_get으로 여러 prefix 경로의 메타 객체를 한 번에 검색
  - 빠른 sanity check로 올바른 객체 필터링 후 나머지 연산 일괄 수행
- **파일 데이터 읽기 (Algorithm 1)**:
  - Data section lookup으로 extent를 찾은 후 병렬 블록 읽기 수행
  - vec_kv_get로 배치된 data section lookup → extent 필터링 → 병렬 블록 읽기

## 핵심 기여

- **핵심 Contribution**: Disaggregated Persistent Memory (DPM) 아키텍처를 위한 비대칭 파일 시스템 Ethane 제안
- **문제 해결**: 기존 symmetric PM 아키텍처의 세 가지 문제 (비싼 노드 간 상호작용, 취약한 단일 노드 성능, 비싼 스케일아웃) 효과적으로 해결
- **성능 혁신**: 최대 68× throughput 향상, 17× 애플리케이션 성능 향상, 1.71× 비용 절감
- **설계 원리**: 
  - Control-plane과 Data-plane 분리 → 하드웨어 리소스 최적 활용
  - Shared log 기반 제어 → 복잡한 파일 시스템 기능 효율적 위임
  - Key-value 스토리지 + Disentangled data path → DPM 대역폭 최대 활용
- **실용적 배포**: 실제 하드웨어 프로토타입 평가로 실용성 입증, 현대 분산 파일 시스템보다 우수한 성능 및 비용 효율성

## 주요 결과

- **구현 언어**: C (10,910줄)
- **구성 요소**:
  - CN: Linux OS, POSIX 호환 인터페이스, cacheFS (사용자 수준 라이브러리, 4,922줄)
  - MN: thin sharedFS 데몬 (PM 풀 관리, log 가비지 컬렉션)
  - ZooKeeper: 네임스페이스 관리 및 설정 정보 유지
- **소스코드**: https://github.com/miaogecm/Ethane.git
- **전송 계층**: 신뢰할 수 있는 연결된 RDMA 전송
- **보안**: sharedFS를 신뢰 컴퓨팅 기반으로 가정, cacheFS는 사용자 공간에서 실행

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2024ATC-summarize/atc24-cai.md|전체 요약 보기]]
