---
tags: [paper, 2019, 2019MICRO, topic/cache, topic/compression, topic/dram, topic/nvm, topic/storage]
venue: "52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO-52), 2019"
year: 2019
summary_path: "../paper-summaries/2019MICRO-summarize/fidr-scalable-storage-for-fine-grain-inline-data-reduction.md"
---

# FIDR: A Scalable Storage System for Fine-Grain Inline Data Reduction with Efficient Memory Handling

**Venue:** 52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO-52), 2019
**저자:** Mohammadamin Ajdari (POSTECH), Wonsik Lee (Seoul National University), Pyeongsu Park (Seoul National University), Joonsung Kim (Seoul National University), Jangwoo Kim (Seoul National University)

## 개요

- 데이터 집약적 애플리케이션(데이터베이스, 머신러닝 등)의 증가로 데이터 서버는 PB(Petabyte) 규모의 저장 용량과 Tbps(Terabits per second)급 성능을 요구하며, SSD 어레이를 활용한 인라인 데이터 축소(deduplication + compression)가 필수적.
- 기존 HW 가속 기반 데이터 축소 시스템(CIDR 등)은 대형 블록(32KB) 기반 chunking만 지원하여, 4KB 단위 IO 요청이 빈번한 워크로드에서 **read-modify-write 오버헤드가 최대 17.5배** 증가하고, 중복 데이터 검출 효율이 크게 저하됨 (Figure 3).
- 하드웨어 가속기를 활용하더라도 CPU 코어 수가 부족한 병목이 발생: 1 Tbps 대역폭을 달성하기 위해 **최대 67개의 Xeon 코어**가 필요하며, 이는 고급 CPU 소켓(22코어)의 약 3배 (Figure 5a).
- 메모리 대역폭 병목: 75 GB/s 처리량을 위해 **317 GB/s의 호스트 메모리 대역폭**이 요구되지만, 고급 소켓의 이론적 최대 대역폭은 170 GB/s에 불과하여 **1.9배 부족** (Figure 4).
- 기존 시스템은 해싱과 압축을 동일 가속기에 통합하여 가중치 높은 호스트 기반 스케줄링(unique chunk predictor)이 필요하며, 이는 전체 CPU 자원의 **32.7%**와 메모리 대역폭의 **23.7%**를 소모하는 새로운 병목 원인.

## 방법론

### 3.1. 메모리 대역폭 병목 분석 (Observation #1, #2)

- 데이터 축소 작업들은 서로 다른 메모리 대역폭/용량 요구사항을 가짐:
  - **대역폭 집약적 작업** (85.1% 사용): NIC↔호스트 메모리, 고유 청크 예측, 호스트↔FPGA 간 데이터 전송 — 메모리 용량은 1GB 미만
  - **용량 집약적 작업** (25.7% 사용): 테이블 캐시 관리 — 10~100GB DRAM 필요
- 호스트 메모리 대역폭의 **85.1%**가 단순 버퍼링과 중간 데이터 이동에 소모되며, 복잡한 처리(압축)는 FPGA에서 수행됨.
- **해결**: 메모리 대역폭/용량 집약적 작업을 분리하여 각각 다른 메모리 타입에 매핑.

### 3.2. NIC 오프로딩 및 In-NIC 버퍼링 (Figure 6, 7)

- **FIDR NIC 마이크로아키텍처** (Figure 7):
  - 클라이언트 요청 수신 시 NIC 내부에서 데이터 및 LBA(Logical Block Address) 버퍼링
  - 각 청크의 해시값을 NIC에서 직접 계산 → PCIe/DMA 컨트롤러를 통해 호스트로 전송
  - 호스트에서 유니크/중복 상태를 판단한 후, NIC가 유니크 청크만 압축 가속기로 스케줄링
- **읽기 요청 처리**: NIC가 수신 버퍼에서 LBA를 직접 검색(Write-Through) → 히트 시 즉시 응답, 미스 시에만 호스트 개입
- **장점**: 클라이언트에게 즉시 쓰기 완료 ACK 전송(배터리 백업 기반 NVRAM 버퍼링)으로 쓰기 지연 시간 제거

### 3.3. 하이브리드 CPU/Memory/FPGA 테이블 캐싱 (Figure 8, 9)

- **Hash-PBN 테이블**: 4KB 청크 기준, 1PB 유니크 데이터 저장 시 테이블 크기 **9.5TB** → 호스트 메모리에 전체 저장 불가
- **테이블 캐시 관리 구성 요소 분석** (Table 2):
  - **트리 인덱싱**: 68.8% CPU 오버헤드, 3GB 미만 메모리 → **FPGA에서 가속**
  - **캐시 콘텐츠 접근**: 6.3% CPU 오버헤드, 10~100GB 메모리 → **호스트 메모리에서 처리**
- **FIDR Cache HW-Engine** (Figure 8): FPGA 기반 B+ 트리 인덱싱 + 캐시 라인 교체 관리
  - 트리 노드: 비리프 노드는 FPGA 온칩 메모리(단일 사이클 접근), 리프 노드는 FPGA 보드 DRAM
  - 100GB 캐시 인덱싱을 13단계 트리로 구성, FPGA 온칩 메모리에 완전 적재 가능

### 3.4. 동시 업데이트 지원 최적화 (Algorithm 1, 2; Figure 9)

- FPGA 기반 트리의 동시 업데이트(삽입/삭제) 시 노드 충돌 가능성이 문제.
- **추측 실행(Speculative Execution) + 복구(Recovery)** 기법 적용:
  - 해시 값이 highly random하여 동일 노드에 대한 동시 업데이트 확률이 **0.1% 미만**
  - 충돌 발생 시 변경 사항 무효화하고 요청 큐에 재삽입하여 재실행
  - 재실행 오버헤드는 **0.1% 미만**으로 미미

## 핵심 기여

- FIDR은 **최초로 fine-grain(4KB) 인라인 데이터 축소를 지원하는 확장 가능한 스토리지 시스템**을 제안하고 프로토타입으로 검증.
- **핵심 기여:**
  1. 데이터 축소 시스템의 가속기 관리, 스케줄링, 테이블 캐싱 문제를 최초로 식별
  2. 메모리 대역폭/용량 집약적 작업 분리 및 최적 디바이스 매핑을 위한 4가지 관찰 제시
  3. NIC 오프로딩, PCIe P2P, 하이브리드 CPU/FPGA 캐싱의 조합으로 **처리량 최대 3.3배 향상**
  4. 호스트 메모리 대역폭 최대 **79.1% 절감**, CPU 사용률 최대 **68% 절감**
  5. PB 규모 스토리지 서버에서 비용 효율적인 솔루션임을 비용 분석으로 입증
- **산업적 의의**: 기존 HW 가속 데이터 축소 시스템의 확장성 한계를 정량적으로 규명하고, NIC/가속기/호스트 간 최적 작업 분배를 통해 Tbps급 처리량을 달성할 수 있는 실용적 아키텍처를 제시.

## 주요 결과

- **하드웨어**: 3개의 Xilinx VCU1525 FPGA 보드 사용
  - FIDR NIC: 64 Gbps 목표 대역폭, SHA-256 해시 코어, TCP 오프로드 엔진
  - FIDR Compression Engine: 해싱 코어 제거, 유니크 청크만 수신하여 압축
  - FIDR Cache HW-Engine: B+ 트리 인덱싱 + NVMe SSD 컨트롤러
- **소프트웨어**: Linux 커널 드라이버 내 FIDR 모듈 구현
  - 데이터 SSD: 소프트웨어 기반 NVMe 관리 (순차 쓰기 → 오버헤드 허용)
  - 테이블 SSD: 하드웨어 기반 NVMe 관리 (랜덤 접근 → CPU 오버헤드 제거)
- **프로토타입 구성**: Intel E5-2650 v4 CPU, 4x Samsung Pro 970 1TB SSD (데이터 2개 + 테이블 2개)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2019MICRO-summarize/fidr-scalable-storage-for-fine-grain-inline-data-reduction.md|전체 요약 보기]]
