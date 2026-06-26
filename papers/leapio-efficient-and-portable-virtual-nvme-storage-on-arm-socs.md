---
tags: [paper, 2020, 2020ASPLOS, topic/dram, topic/near-data-processing, topic/nvm, topic/storage, topic/virtual-memory]
venue: "25th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '20)"
year: 2020
summary_path: "../paper-summaries/2020ASPLOS-summarize/leapio-efficient-and-portable-virtual-nvme-storage-on-arm-socs.md"
---

# LeapIO: Efficient and Portable Virtual NVMe Storage on ARM SoCs

**Venue:** 25th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '20)
**저자:** Huaicheng Li, Mingzhe Hao (University of Chicago), Stanko Novakovic (Microsoft Research), Vaibhav Gogte (University of Michigan), Sriram Govindan (Microsoft), Dan R. K. Ports, Irene Zhang, Ricardo Bianchini (Microsoft Research), Haryadi S. Gunawi (University of Chicago), Anirudh Badam (Microsoft Research)

## 개요

- 클라우드 스토리지 스택은 극도로 리소스 집약적이어서, 데이터센터 x86 코어의 10-20%를 스토리지 기능에 소비하는 "스토리지 세금(storage tax)"이 발생
- 오늘날의 클라우드 스토리지 기능(가상화, 캐싱, 원자적 쓰기, 버전 관리, 우선순위 지정, 압축, 암호화 등)은 IO 가속기에 완전히 오프로드 ready하지 않음: (1) 기능이 저비용 하드웨어 가속에 너무 복잡함, (2) 가속 하드웨어는 일반적인 경우에만 최적화됨, (3) 기능 간 합성(composability) 부족
- ARM 기반 공동 프로세서(cloud coprocessor)가 서버 워크로드에 배포되는 새로운 트렌드: ARM SoC의 BOM 비용이 낮고 전력 소비가 ~10W로 연간 TCO가 ~$100 미만 (일반 서버 연간 TCO의 ~3%)
- 단순히 ARM SoC를 PCIe 슬롯에 연결하는 것으로는 불충분; 하드웨어 fungibility, 소프트웨어 portability, virtualizability, composability, efficiency, extensibility 등 배포 과제를 해결해야 함
- 기존 IO 가속기(SmartSSD, SmartNIC 등)는 하드웨어 진화로 인해 서버 플릿의 조각화(fragmentation) 위험 초래

## 방법론

### 3.1. 하드웨어 요구 사항 (HW1-HW4)

- **HW1: SoC에 의한 호스트 DRAM 접근:** SoC가 사용자 공간 LeapIO 런타임에서 DMA 엔진을 사용하여 호스트 DRAM의 NVMe 큐 페어에 접근 가능하도록 지원
- **HW2: SoC에 의한 IOMMU 접근:** 신뢰할 수 있는 SoC 런타임이 호스트 IOMMU에 접근하여 VM의 게스트 주소를 호스트 물리 주소로 변환 (페이지 테이블 워크)
- **HW3: 호스트에 매핑된 SoC DRAM:** SoC의 DRAM이 PCIe BAR로 호스트에 노출되어 rNIC과 SSD가 제로-copy DMA 가능 (집합 호스트 주소 공간 = 호스트 + SoC DRAM)
- **HW4: NIC 공유:** ARM SoC와 호스트 x86 간에 NIC를 공유하여 VM 트래픽과 오프로딩된 원격 스토리지 함수 모두 NIC 사용 가능

### 3.2. 소프트웨어 아키텍처

- **NVMe 큐 페어 매핑:** VM-런타임, 런타임-SSD 간 NVMe 큐 페어를 하드웨어/소프트웨어 경계에 걸쳐 매핑하여 통신 추상화
- **런타임 폴링:** VM 측 NVMe 제출 큐를 지속적으로 폴링하여 빠른 지연 시간과 높은_throughput 유지
- **사용자 공간 스토리지 함수:** 커널 공간 대신 사용자 공간에서 스토리지 함수를 구현하여 확장성 극대화
- **SoCV M (포터빌리티):** ARM SoC 없이도 x86에서 LeapIO를 실행할 수 있는 SoC 유사 VM 기능. 하이퍼바이저가 SoCV M의 주소 공간을 호스트 DRAM 전체 크기만큼 확장

### 3.3. 데이터 경로 및 주소 변환

- **4개 주소 공간:** guestAddr (gA), hostAddr (hA), logicalAddr (lA), socAddr (sA)
- **클라이언트 측 변환:** 
  - 게스트 VM이 NVMe 명령을 제출하면 런타임이 IOMMU를 통해 gA→hA 변환 후 DMA로 SoC DRAM에 데이터 복사
  - RDMA 전송을 위해 logicalAddr를 ibverbs에 등록
- **서버 측 변환:**
  - 수신된 데이터를 SoC DRAM에 저장 후 스토리지 함수 실행
  - SSD 기록 시 lA→sA→hA 변환 (p2p-mem 기술로 SoC DRAM을 호스트 주소 공간에 매핑)
- **효율성:** 호스트-SoC 데이터 전송은 불필요한 오버헤드가 아닌 PCIe 경계를 반드시 통과해야 하는 필수 복사. 하드웨어 DMA로 수행됨

### 3.4. 합성 가능한 스토리지 서비스

- **우선순위 지정 서비스:** 시간에 민감한 쿼리를 배치 워크로드보다 우선 처리. 검색 엔진 트레이스에서 배경 워크로드와 동일 시 실행 시 지연 시간을 배경 없음 수준으로 복원
- **스냅샷/버전 서비스:** NVMe 다중 블록 원자적 쓰기 명령으로 로그에 기록 후 백그라운드 스레드가 점진적으로 체크포인트
- **원격 랙 로컬 SSD:** RDMA/TCP를 통한 원격 스토리지 접근으로 컴퓨팅과 스토리지 분리
- **랙 로컬 RAID:** 중앙 billboard를 통해 각 서버의 여유 SSD IOPS/용량을 게시하고, 필요 시 P2P 트랜잭션으로 가상 랙 로컬 SSD 구성
- **가상화된 OpenChannel SSD:** 게스트 VM이 LightNVM을 실행하면서 LeapIO가 채널을 리매핑하여 OC 성능 격리 이점 제공

## 핵심 기여

- **핵심 기여:** ARM SoC를 활용한 차세대 클라우드 스토리지 스택 LeapIO 제안. x86에서 ARM으로의 이동이 미치는 엔지니어링 및 성능 오버헤드가 최소화됨을 입증
- **성능:** 소프트웨어 런타임 오버헤드 2-5% (bare-metal 대비), 데이터센터 SSD에서 0.65M IOPS 달성. 현재 SoC 프로토타입은 서버 측 5% 추가 감소, 클라이언트 측 최대 30% 감소이지만 20배 이상 비용 절감
- **합성성:** 70~4,400 LOC로 다양한 스토리지 함수(RAID, 복제, 우선순위, 원자적 쓰기, 스냅샷, OC 가상화 등)를 사용자 공간에서 쉽게 구현 및 합성
- **의의:** 클라우드 제공자가 서버 구현에 관계없이 동일한 스토리지 서비스를 VM에 노출할 수 있게 함. 스토리지 오프로딩을 "기회"로 취급하여 하드웨어 종속성 없는 유연한 배포 가능
- **향후 연구:** 게스트 소프트웨어 스택 전체를 ARM으로 오프로딩하는 장기적 목표

## 주요 결과

- **구현 언어:** C
- **총 코드 라인 수:** 14,388 LOC
  - 코어 런타임: 8,865 LOC
  - SoCV M: +850 LOC
  - 에뮬레이션: +680 LOC
  - QEMU 변경: 1,388 + 385 LOC
  - 호스트 OS: 2,340 + 560 + 360 LOC
- **하드웨어 플랫폼:** Broadcom StingRay V1 SoC 기반 커스텀 개발 보드 (8개 Cortex-A72 ARM 코어 @ 3GHz, 100Gb 이더넷 NIC 통합)
- **스토리지 서비스:** 70~4,400 LOC로 다양한 서비스 구현 (RAID, 복제, 우선순위, 원자적 쓰기, 스냅샷, OC 가상화, 블록 캐시 등)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2020ASPLOS-summarize/leapio-efficient-and-portable-virtual-nvme-storage-on-arm-socs.md|전체 요약 보기]]
