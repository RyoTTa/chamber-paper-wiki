---
tags: [paper, 2018, 2018MICRO, topic/cache, topic/dram]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/farewell-my-shared-llc-a-case-for-private-die-stacked-dram-caches-for-servers.md"
---

# Farewell My Shared LLC! A Case for Private Die-Stacked DRAM Caches for Servers

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Amna Shahab, Mingcan Zhu, Artemiy Margaritov, Boris Grot (Institute for Computing Systems Architecture (ICSA), School of Informatics, University of Edinburgh)

## 개요

- 데이터센터는 실시간 스토리지, 검색, 처리 기능을 제공하며, 서버 프로세서의 성능 향상이 필수적
- 기술 스케일링의 종말로 인해 싱글스레드 성능 향상이 정체되고, 무어의 법칙 둔화와 제조 비용 증가로 코어 수 증가에도 한계
- 현대 서버 프로세서는 대용량 온칩 LLC(Last-Level Cache)를 사용하지만, 다음과 같은 한계 존재:
  - **온칩 면적 제약:** Intel 18코어 프로세서의 45MB LLC가 다이 면적의 30-35% 차지
  - **접근 지연 시간:** 다이 크기가 커질수록 와이어 지연 및 멀티홉 네트워크로 인해 LLC 슬라이스 접근 시간 증가
  - **캐시 경쟁:** 공유 LLC 설계로 인한 워크로드 간 캐시 경쟁 (workload colocation 시 성능 저하)
- Scale-out 워크로드는 대용량 LLC 용량이 필요하지만, 높은 접근 지연 시간에 매우 민감 (Fig. 2: 1024MB LLC가 레이턴시 40% 증가 시 64MB LLC 성능과 동일)
- 스케일아웃 워크로드에서 쓰기-읽기 공유(RW-sharing)는 매우 제한적 (Web Search 4%, Data Serving 3%, MapReduce/SAT Solver는 무시 가능)

## 방법론

### 3.1. 다이 스택 프라이빗 LLC 구조

- **볼트(Vault) 구조:**
  - 각 볼트는 코어 위에 직접 스택된 독립적인 DRAM 캐시 슬라이스
  - Hybrid Memory Cube(HMC)와 유사하지만, CPU 다이 위에 스택된다는 점에서 차별화
  - 각 볼트는 자체 메모리 컨트롤러를 가지며 다른 볼트와 데이터 저장/액세스에서 완전히 독립
- **지연 시간 최적화된 DRAM 설계:**
  - 기존 용량 지향 DRAM 대비 지연 시간 45% 감소 (22nm 기술 노드)
  - 대량의 뱅크를 서브어레이와 타일로 분할하여 접근 시간 최소화
  - 256MB 용량의 프라이빗 볼트에서 11.5ns 접근 지연 시간 달성
- **일관성 유지:**
  - 디렉토리 기반 프로토콜로 캐시 일관성 유지
  - 다이 스택 LLC에 인-DRAM 메타데이터 저장
  - 높은 히트율로 디렉토리 접근이 성능에 미치는 영향 최소화

### 3.2. 캐시 계층 구조

- **프라이빗 L1/L2 캐시:** 기존 온칩 프라이빗 캐시 유지
- **프라이빗 LLC:** 다이 스택 DRAM에 구현된 각 코어 전용 LLC
- **캐시 일관성:** 디렉토리 기반 프로토콜로 프라이빗 캐시 간 일관성 유지
- **데이터 공유:** 스케일아웃 워크로드의 특성상 코어 간 데이터 공유가 제한적이므로 프라이빗 캐시가 적합

### 3.3. 워크로드 민감도 분석

- **용량 민감도 (Fig. 1):**
  - 8MB에서 64MB까지는 성능 향상 미미
  - 64MB 이상에서 세컨더리 워킹 세트가 캐시에 들어가면서 큰 성능 향상
  - Data Serving, Web Frontend, SAT Solver: 256MB에서 8MB 대비 10-20% 성능 향상
- **레이턴시 민감도 (Fig. 2):**
  - 큰 LLC는 낮은 레이턴시에서만 높은 성능 발휘
  - 레이턴시가 증가하면 큰 LLC의 이점이 급격히 감소
  - 레이턴시가 2배에 가까워지면 대부분의 구성이 8MB LLC 성능 수준으로 하락
- **RW-공유 민감도 (Fig. 3, 4):**
  - 스케일아웃 워크로드에서 RW-공유는 매우 제한적
  - RW-공유 블록의 레이턴시를 4배로 증가시켜도 성능 영향은 미미 (최대 8% 성능 저하)

## 핵심 기여

- **핵심 기여:** 공유 LLC의 한계를 극복하기 위한 SILO 아키텍처 제시
  - 다이 스택 DRAM 기반 프라이빗 LLC로 온칩 면적 제약, 긴 와이어 지연, 캐시 경쟁 문제 해결
- **성능 향상:** CloudSuite 워크로드에서 5-54% 성능 향상
- **성능 격리:** 프라이빗 캐시로 워크로드 콜로케이션 시 강력한 성능 격리 제공
- **기술적 기여:** 지연 시간 최적화된 DRAM 캐시 설계로 45% 지연 시간 감소, 11.5ns 접근 지연 시간 달성
- **의의:** 서버 프로세서의 캐시 계층 설계에 새로운 방향성 제시, 데이터센터 성능 향상에 기여
- **한계점:** 다이 스택 기술의 성숙도, 제조 비용, 열 관리 등의 실용화 과제 존재

## 주요 결과

- **시뮬레이션:** 풀시스템 사이클-정확 시뮬레이션 사용
- **기반 프로세서:** 16코어 서버 프로세서
- **캐시 구성:**
  - L1: 프라이빗 32KB
  - L2: 프라이빗 (옵션)
  - LLC: 다이 스택 DRAM 기반 프라이빗 (볼트당 256MB)
- **기술 노드:** 22nm
- **DRAM 최적화:** 지연 시간 최적화 설계로 기존 용량 최적화 설계 대비 45% 지연 시간 감소

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/farewell-my-shared-llc-a-case-for-private-die-stacked-dram-caches-for-servers.md|전체 요약 보기]]
