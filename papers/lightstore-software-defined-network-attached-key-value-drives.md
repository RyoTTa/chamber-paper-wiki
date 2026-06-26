---
tags: [paper, 2019, 2019ASPLOS, topic/cache, topic/dram, topic/nvm, topic/storage]
venue: "2019 Architectural Support for Programming Languages and Operating Systems (ASPLOS '19)"
year: 2019
summary_path: "../paper-summaries/2019ASPLOS-summarize/lightstore-software-defined-network-attached-key-value-drives.md"
---

# LightStore: Software-defined Network-attached Key-value Drives

**Venue:** 2019 Architectural Support for Programming Languages and Operating Systems (ASPLOS '19)
**저자:** Chanwoo Chung (Massachusetts Institute of Technology), Jinhyung Koo (DGIST), Junsu Im (DGIST), Arvind (Massachusetts Institute of Technology), Sungjin Lee (DGIST)

## 개요

- 데일리센터에서 스토리지 서버는 상당한 CAPEX/OPEX를 차지. 기존 x86 기반 스토리지 서버는 10TB급 HDD, 수백 GB DRAM, 1~2개 Xeon 프로세서로 구성.
- **HDD 기반 아키텍처의 한계:**
  - 큰 DRAM 버퍼가 무작위 접근의 레이턴시를 보상하지만, 현대 NVMe SSD의 100만 IOPS 달성 시 DRAM 캐시 효과 미미.
  - HDD 기반 시스템은 디스크를 집계하여 내부 버스/네트워크 대역폭을 활용하지만, SSD 기반에서는 **네트워크가 병목** (최신 NVMe SSD: 10GB/s 순차 읽기, 40GbE는 5GB/s).
  - 깊은 소프트웨어 스택 (NFS, 파일 시스템 등)이 SSD의 높은 대역폭을 저하시킴.
- **All-Flash Array (AFA)의 한계:** 단순히 HDD를 SSD로 교체하는 것만으로는 NAND 플래시의 특성을 완전히 활용하지 못함.
- 핵심 문제: x86 기반 스토리지 서버를 저전력 임베디드 기반의 드라이브 크기 노드로 대체하여, 네트워크에 직접 연결하고 KV 인터페이스로 소프트웨어 정의 스토리지를 구현하는 아키텍처.

## 방법론

### 3.1. 전체 구조 (Figure 1, 2)

- **LightStore 노드:** ARM Cortex-A53 쿼드코어(1.2GHz), 4GB DDR4 DRAM, 커스텀 플래시 카드(512GB), 10GbE NIC.
- **클러스터 구성:** 여러 LightStore 노드를 네트워크에 추가하여 대규모 분산 스토리지 클러스터 형성.
- **어댑터 계층:**
  - **블록 어댑터 (BUSE):** POSIX API(read/write) → bio 요청 → KV 요청(LBA를 해시한 키). 8KB 데이터 전송 단위.
  - **YCSB 어댑터:** YCSB 명령(INSERT, READ, UPDATE, DELETE) → KV 명령(SET, GET, MSET, MGET). 멀티 필드 지원을 위해 MSET/MGET 활용.
  - **파일 시스템 어댑터:** 블록 스토리지 위에 파일 시스템 마운트.
- **일관 해싱 (Consistent Hashing):** 키를 LightStore 노드에 분산.

### 3.2. 경량 KV 저장소 엔진 (LightStore-Engine)

- **LSM-tree 기반:** 기존 RocksDB를 임베디드 ARM에서 사용하면 충분한 성능 미달 → ARM에 최적화된 경량 KV 저장소를 처음부터 구현.
- **데이터 구조 (Figure 7):**
  - **L0 메모리 테이블 (L0 memtable):** DRAM 내 키-값 캐시. 값은 8KB 청크로 관리.
  - **L0 키테이블 (L0 keytable):** 키의 순서 정보를 별도 관리 (값과 키 분리).
  - **영구 메모리 테이블 (Persistent Memtable):** L1~Ln 레벨로 플래시에 저장.
  - **B+ 트리:** DRAM에서 키테이블 위치를 추적.
- **컴팩션 최적화:**
  - 물리적 값 재배치 대신 키테이블만 정렬하여 컴팩션 비용 대폭 감소.
  - FTL 가비지 컬렉션 불필요 (삭제된 KV 쌍은 컴팩션 과정에서 제거).
- **Bloom Filter:** GET/MGET 시 불필요한 레벨 탐색을 방지.
- **키테이블 캐싱:** DRAM의 여유 공간에 키테이블을 캐싱 (약 1GB/1TB 플래시). FTL 매핑 테이블 불필요로 추가 캐싱 공간 확보.

### 3.3. 하드웨어 FTL

- **목적:** LSM-tree의 append-only 쓰기 패턴을 활용하여 FTL을 완전히 하드웨어(FPGA)로 구현.
- **효과:** 임베디드 ARM 코어의 리소스를 KV 저장소와 네트워크 스택에 전부 할당 가능.
- **AMF (Application-Managed Flash) 인터페이스 활용:** 블록 I/O 인터페이스의 append-only 특성 사용.
- **데이터 지속성/일관성:** 엔터프라이즈 SSD의 내장 커패시터를 활용하여 전원 장애 시 임시 데이터를 비휘발성 미디어에 플러시. 추가 I/O나 외부 배터리 불필요.

## 핵심 기여

- LightStore는 x86 기반 스토리지 서버를 대체하는 저전력 KV 플래시 스토어 아키텍처를 제안.
- **핵심 기여:**
  1. 드라이브 크기의 네트워크 직접 연결 KV 스토어 아키텍처
  2. LSM-tree 기반 경량 KV 저장소 (ARM 임베디드 최적화)
  3. 하드웨어 FTL로 임베디드 리소스 효율적 활용
  4. 소프트웨어 정의 스토리지 (어댑터를 통한 블록/파일/YCSB 가상화)
- **성능:** 4노드 클러스터에서 x86 서버 대비 **7.4× ops/J** 향상.
- **효율:** 동일 용량/처리량 조건에서 commercial AFA 대비 **2.0× 전력, 2.3× 공간** 효율.
- **의의:** 스토리지 아키텍처에서 x86 서버의 필수성을 재고하고, 네트워크 직접 연결 임베디드 KV 스토어가 데이터센터 스토리지의 새로운 패러다임이 될 수 있음을 입증.

## 주요 결과

- **프로토타입:** Xilinx Zynq Ultrascale+ ZCU102 보드 (ARM Cortex-A53 쿼드코어 1.2GHz + FPGA, 4GB DDR4)
- **플래시:** 커스텀 플래시 카드 (512GB)
- **OS:** Ubuntu 16.04, Linux 4.9.0 커널
- **네트워크:** 10GbE
- **소프트웨어 크기:** KV 프로토콜 서버 + LSM-tree 엔진 + 어댑터
- **DRAM 사용량:** B+ 트리, lock-free 큐, L0 메모리 테이블에 **82MB** 필요. 나머지는 키테이블 캐싱에 사용.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2019ASPLOS-summarize/lightstore-software-defined-network-attached-key-value-drives.md|전체 요약 보기]]
