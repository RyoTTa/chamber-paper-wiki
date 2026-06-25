---
tags: [paper, 2020, 2020ASPLOS, topic/disaggregation, topic/dram, topic/nvm]
venue: "25th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '20)"
year: 2020
summary_path: "../paper-summaries/2020ASPLOS-summarize/asymnvm-an-efficient-framework-for-persistent-data-structures-on-asymmetric-nvm-architecture.md"
---

# AsymNVM: An Efficient Framework for Implementing Persistent Data Structures on Asymmetric NVM Architecture

**Venue:** 25th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '20)
**저자:** Teng Ma, Mingxing Zhang, Kang Chen, Zhuo Song, Yongwei Wu, Xuehai Qian (Tsinghua University, Sangfor, Alibaba, University of Southern California)

## 개요

- NVM (Non-Volatile Memory)은 DRAM 유사 성능(읽기 100ns, 쓰기 300ns), 디스크 유사 용량(TB 규모), 영속성을 동시에 제공하는 유망 기술이지만, 기존 대칭형(symmetric) 배포 방식에서 한계가 존재
- 기존 대칭형 배포: NVM이 개별 서버에 직접 연결되어 있어 서버 다운 시 데이터 접근 불가. 가용성을 높이려면 원격 NVM에 데이터 복제가 필요하지만, 로컬 메모리에 완전 복제본을 유지해야 하므로 워킹셋 크기가 제한됨 (Mojim [42], Hotpot [79])
- Google 연구에 따르면 데이터센터 리소스 활용률이 평균 40% 미만이며, NVM도 동일한 낮은 활용률이 예상됨. 높은 밀도를 가진 NVM은 단일 서버의 필요량을 초과하는 용량을 제공 가능
- RDMA를 통한 원격 NVM 접근 시 네트워크 지연 시간(latty)과 지속성(persistency) 병목, 백엔드 NVM 노드의 단순 인터페이스 문제가 핵심 과제로 부각
- 단순 RDMA_Read/RDMA_Write로 store/load 명령어를 대체하면 네트워크 라운드 트립이 급증하여 NIC가 세밀한 데이터 구조 접근에 충분한 IOPS를 제공하지 못함

## 방법론

### 3.1. 아키텍처 개요

- **프론트엔드 (Front-end):** 클라이언트 서버. CPU, DRAM, RNIC 보유. 프론트엔드 DRAM은 원격 NVM 데이터의 캐시 역할
- **백엔드 (Back-end):** NVM 블레이드. 프론트엔드보다 적은 수의 NVM 디바이스로 다수 서버에 서비스 제공. DRAM보다 느리지만 훨씬 큰 용량의 NVM 보유
- **원격 NVM 접근:** One-sided RDMA (RDMA_Read/RDMA_Write)를 사용하여 프론트엔드가 백엔드의 처리 유닛에 알리지 않고 직접 데이터 접근. Two-sided 연산보다 성능 우수
- 백엔드 노드는 수동적(passive)으로 동작: 프론트엔드의 API 호출에만 응답

### 3.2. API 인터페이스 (Table 1)

| 타입 | API | 설명 |
|------|-----|------|
| **기본 (네이티브)** | `rnvm_read` | 로컬 캐시 또는 원격 NVM에서 데이터 읽기 |
| | `rnvm_write` | 원격 NVM에 데이터 쓰기 |
| **트랜잭션** | `rnvm_mem_log` | 메모리 로그를 프론트엔드 버퍼에 기록 |
| | `rnvm_op_log` | 오퍼레이션 로그를 원격 NVM에 기록 |
| | `rnvm_tx_write` | 배치된 메모리 로그 묶음을 원격 NVM에 쓰기 |
| **메모리 관리** | `rnvm_malloc` / `rnvm_free` | 원격 NVM 공간 할당/해제 |
| **동시성** | `writer_(un)lock` / `reader_(un)lock` | 독점 쓰기 잠금 / 동시 읽기 잠금 |

### 3.3. Efficient Persistent Update

- **Memory Log:** 기존 DudeTM의 redo log 방식을 원격 분산 환경에 적용. 프론트엔드에서 {주소, 값} 쌍을 로그로 생성하고, 백엔드에서 atomic하게 NVM에 기록. `rnvm_tx_write` 호출 시 단일 RDMA_Write로 로그를 전송하여 네트워크 라운드 트립 절약
- **Operation Log:** Memory Log의 한계를 극복하는 핵심 혁신. 오퍼레이션 타입, 파라미터, 체크섬으로 구성된 고수준 로그. Operation Log가 영속화되면 실제 데이터 구조 수정을 연기(defer)하고 배치 가능
  - Memory Log: Low-level, 데이터 구조 의미 없음. 쓰기마다 여러 RDMA_Write 필요
  - Operation Log: High-level, 데이터 구조 오퍼레이션 의미 보유. 쓰기마다 단 하나의 RDMA_Write로 완료
  - 배칭 효과: 다수 쓰기의 메모리 로그를 하나의 `rnvm_tx_write`로 통합. RDMA_Write 연산을 대폭 절감
- **Gather-Apply 모델:** 각 오퍼레이션을 데이터 수집(gather)과 변경 적용(apply)으로 분리. 배칭과 캐싱을 통해 여러 읽기/쓰기를 함께 처리

### 3.4. 프론트엔드 데이터 캐시

- 프론트엔드에서 해시맵(hash map)으로 원격 NVM의 데이터 구조 노드 주소 → 로컬 DRAM 주소 변환
- 페이지 단위 캐시. 데이터 구조별로 페이지 크기 조정 가능
- **LRU + RR 하이브리드 대체 정책:** 완전한 LRU는 구현 비용 높음, 완전한 RR은 핫 데이터 보장 없음. 무작위 페이지 세트 선택 후 세트 내에서 가장 오래 사용되지 않은 페이지 제거
- Zipf 분포 워크로드에서 하이브리드(29.2%)가 RR(62.7%) 대비 미스율 33.5% 감소, LRU와 유사한 미스율에서 처리량 27.5% 향상

### 3.5. NVM 데이터 관리

- 백엔드에서 NVML 라이브러리의 persistent memory pool 사용, malloc/free로 인터랙션
- Two-tier slab 기반 할당기: 백엔드가 고정 크기 블록 할당 (영속성 보장), 프론트엔드가 더 세밀한 크기 할당 지원
- 영속 비트맵(persistent bitmap)으로 NVM 사용 상태 기록. 각 비트는 할당 상태 하나를 나타냄
- RPC 할당기 대비 Two-tier 할당기는 Alloc 처리량 4~20배 향상 (Table 2)

### 3.6. 동시성 제어

- **독점 쓰기 잠금 (Writer Lock):** RDMA atomics (`RDMA_Compare_And_Swap`)으로 구현. 프론트엔드에서 분산 락 관리. 크래시 시 lock-ahead 로그로 복구
- **Write-Preferred Read Lock:** 시퀀스 넘버(SN) 기반. 백엔드가 `Write_Begin`과 `Write_End` 사이에서 SN을 원자적으로 2회 증가. 리더는 SN이 홀수일 때 대기, 짝수일 때 읽기 가능
- **Multi-version 데이터 구조:** Lock-free 방식. Path copying으로 변경된 노드 복사 후 루트 포인터를 원자적으로 갱신. 리더에게 일관된 뷰 제공
- Lock 벤치마크: 6 리더 + 1 라이터, 90% 읽기에서 리더 평균 260 KOPS, 라이터 539 KOPS. 읽기 실패율 3%

### 3.7. 복구 및 복제

- 최소 1개의 미러 노드(mirror-node) 사용. 백엔드가 커밋 전 미러 노드에 로그를 비동기적으로 복제
- **Case 1-5 복구 시나리오:** 프론트엔드 크래시, 백엔드 단기 장애, 백엔드 영구 장애, 미러 노드 크래시 등 다양한 실패 케이스를 로그 기반으로 처리
- 미러 노드가 NVM을 보유하면 새 백엔드로 투표(voting)되어 즉시 서비스 가능

## 핵심 기여

- **핵심 기여:** NVM 배포 방식을 대칭형에서 비대칭형으로 재사고(rethink)하고, 이를 위한 범용 프레임워크 AsymNVM을 제안
- **성능:** 10노드 실제 NVM 클러스터에서 구현한 8개 데이터 구조와 2개 트랜잭션 앱이 기존 대칭형 아키텍처 대비 유사하거나 더 나은 성능 달성 (5~12배 Naive 대비 향상)
- **의의:** 리소스 분리(disaggregation)의 장점(유연한 배포, 높은 가용성, 리소스 활용도 향상)을 누리면서도 성능 손실을 최소화하는 최초의 NVM 프레임워크. Operation Log를 통한 배칭/캐싱 메커니즘이 원격 NVM 시스템의 핵심 최적화 기법으로 자리잡을 것을 시사
- 향후 연구 방향: 더 높은 네트워크 대역폭/낮은 지연 시간, 고급 백엔드 하드웨어, 다양한 분산 데이터 구조로의 확장

## 주요 결과

- 구현 언어: C++11 (GCC 4.8.5)
- 8개 데이터 구조 구현: Stack, Queue, HashTable, SkipList, BST, B+Tree, MV-BST, MV-B+Tree
- 2개 트랜잭션 애플리케이션: TATP, SmallBank
- 백엔드 메모리 관리: NVML 라이브러리 기반 persistent memory pool
- RPC 통신: RF-RPC [84,95] 프레임워크

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]


## 전체 요약

[[../paper-summaries/2020ASPLOS-summarize/asymnvm-an-efficient-framework-for-persistent-data-structures-on-asymmetric-nvm-architecture.md|전체 요약 보기]]
