---
tags: [paper, 2019, 2019MICRO, topic/cache, topic/dram, topic/near-data-processing]
venue: "52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '19)"
year: 2019
summary_path: "../paper-summaries/2019MICRO-summarize/netdimm_low-latency_near-memory_network_interface_architecture.md"
---

# NetDIMM: Low-Latency Near-Memory Network Interface Architecture

**Venue:** 52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '19)
**저자:** Mohammad Alian, Nam Sung Kim (University of Illinois Urbana-Champaign)

## 개요

- 데이터센터의 확산으로 인해 네트워크 설계 요구사항이 높은 대역폭 위주에서 **초저지연(low-latency)**으로 변화하고 있음
  - 인메모리 캐싱, 고성능 컴퓨팅, 금융 트레이딩 등 초저지연 애플리케이션이 서브마이크로초 수준의 지연 시간 개선에 의존
- **PCIe 인터커넥트가 네트워크 지연 시간의 병목**: PCIe 서브시스템이 전체 네트워크 지연 시간의 **77.2~90.6%**를 차지 (ExaNIC 10Gbps NIC 기준)
  - PCIe Gen 4.0 x16 이론 대역폭 31.51GBps이나, 프로토콜 오버헤드로 인한 지연 시간 문제
- NIC에서 메모리로의 데이터 이동도 주요 병목: DMA 버퍼에서 애플리케이션 메모리로의 복사가 바이트당 오버헤드의 **18~92%**를 차지
- 기존 해결책들의 한계:
  - **S0 (PCIe 트랜잭션 수 감소):** 소규모 패킷에만 효과적, NIC는 여전히 PCIe로 연결됨
  - **S1 (NIC-프로세서 통합):** 면적/전력 오버헤드가 크고, NIC와 CPU가 다른 벤더 제조
  - **S2/S3 (대용량 버퍼 NIC / NIC 프로세싱):** 일반 애플리케이션에 적용 어려움
  - **S4 (Zero-copy):** 보안 침해, 메인 메모리 고갈, 가상 메모리 오버헤드 문제
- 네트워크 트래픽이 메모리 서브시스템에 미치는 간섭도 심각: 최대 메모리 압력에서 iperf 대역폭이 **72.1% 감소**

## 방법론

### 3.1. 하드웨어 아키텍처

- **NetDIMM 버퍼 디바이스 구성요소:**
  - **nNIC:** 통합 네트워크 인터페이스 카드
  - **nMC:** 로컬 DRAM 모듈 접근을 위한 메모리 컨트롤러 (1개 이상)
  - **nController:** NVDIMM-P 컨트롤러를 확장한 NetDIMM 라우팅/관리 로직
  - **DDR5 PHY 인터페이스:** DDR5 물리 인터페이스 및 프로토콜 엔진
  - **nCache:** RX 데이터를 캐싱하는 이중 포트 SRAM 버퍼
  - **nPrefetcher:** 로컬 DRAM에서 nCache로 RX 패킷을 프리페치하는 라인 프리페처
  - **RowClone 지원 DRAM:** 인메모리 데이터 복사를 지원하는 DRAM 디바이스
- **메모리 주소 공간:** NetDIMM의 로컬 DRAM 용량을 호스트 주소 공간에 통합 노출 (NVDIMM-P의 통합 주소 공간과 유사)
- **DMA 접근 패턴 관찰:** NIC의 DMA 엔진은 패킷 수신 시 캐시라인 단위로 버스트 접근을 생성 → nCache와 nPrefetcher로 활용
  - 각 패킷 수신 시 24개 캐시라인 (1536 Bytes) 버스트, 세 번째 패킷의 경우 143ns 간격
- **nCache 정책:** 첫 번째 캐시라인(헤더)만 캐싱, 나머지는 nPrefetcher로 프리페치
  - TCP/IP 패킷 최대 헤더 크기 52 Bytes → 첫 64 Bytes 캐싱으로 모든 헤더 포함
  - 인클루시브, 세트 어소시에이티브 구조, 랜덤 교체 정책

### 3.2. In-Memory Buffer Cloning

- **RowClone 확장 구현:** 메모리 내 대량 데이터 복사 가속
  - **FPM (Fast Parallel Mode):** 소스/대상 페이지가 동일 서브어레이에 위치 → 두 번의 연속 활성화로 완료 (가장 빠름)
  - **PSM (Pipeline Serial Mode):** 동일 디바이스 내 다른 뱅크 → DRAM 내부 버스를 통한 파이프라인 복사
  - **GCM (General Cloning Mode):** 그 외 → NetDIMM 버퍼 디바이스를 통해 읽고 파이프라인으로 쓰기 (가장 느리지만 일반적)
  - **지능적 메모리 할당:** 소스/대상 페이지를 동일 서브어레이에 할당하여 최대 성능 추출

### 3.3. 소프트웨어 아키텍처

- **NETi 메모리 존:** Linux에 새로운 메모리 존 생성으로 NetDIMM 로컬 메모리 영역 관리
  - 각 NetDIMM마다 고유한 메모리 존 할당
- **__alloc_netdimm_pages(zone, hint):** 동일 서브어레이의 페이지를 할당하는 Linux API
  - allocCache: 각 서브어레이에서 2페이지씩 사전 할당 (32K 페이지 = 128MB, 16GB NetDIMM의 0.8% 오버헤드)
- **Flex 채널 인터리빙:** 메모리 채널 인터리빙을 비활성화하여 NetDIMM 주소 공간을 단일 채널 모드로 노출
- **NetDIMM 드라이버:** Intel e1000 드라이버를 기반으로 개발
  - ioremap()으로 설정 공간 생성, 컨벤셔널 PCIe NIC와 동일한 기능 지원
  - **COPY_NEEDED 플래그:** SKB 헤더에 추가하여 TX 시 DMA 버퍼로의 사전 복사 관리
  - **폴링 에이전트:** 고해상도 커널 타이머 기반, 인터럽트보다 효율적
- **알고리즘 1 (TX/RX 처리):**
  - TX: allocCache에서 DMA 버퍼 할당 → COPY_NEEDED 시 느린 경로에서 복사 → flush 후 전송
  - RX: rxDesc 무효화 → allocCache에서 RX 버퍼 할당 → netdimmClone()으로 인메모리 버퍼 클로닝

## 핵심 기여

- **핵심 기여:** DDR5 NVDIMM-P 프로토콜의 비동기 메모리 접근을 활용한 **최초의 근메모리 NIC 아키텍처** 제시
- PCIe 완전 제거로 인메모리 네트워크 서브시스템의 지연 시간 **최대 52.9% 감소**
- 대역폭 손상 없이 지연 시간 대폭 개선 (DDR5 채널 대역폭이 충분)
- 애플리케이션 투명성 보장 (최소한의 리눅스 커널 수정으로 전체 스택 지원)
- Facebook 프로덕션 클러스터 트레이스 기반 실증적 평가로 실용성 확인
- 향후 과제: NIC 칩의 물리적 실현성 검증 (전력/열 관리), 다양한 네트워크 애플리케이션에서의 확장 검토

## 주요 결과

- **시스템 구성:**
  - CPU: 8코어, 3.4GHz
  - 메모리: DDR4-2400MHz, 16GB, 2채널
  - 네트워크: 40GbE, 스위치 지연: 100ns
  - NIC: ×8 PCIe Gen4
- **시뮬레이션 도구:** gem5 + PCIe/메모리 컨트롤러 분석 모델
- **드라이버 구현:**
  - 베어메탈 드라이버 (저지연 유저스페이스 드라이버 유사)
  - 리눅스 커널 드라이버 (전체 소프트웨어 스택 지원)
- **물리적 실현성:**
  - IBM Centaur 디바이스 TDP: 20W (22nm), Intel XXV710 이더넷 컨트롤러 TDP: 6.5W
  - DIMM 버퍼 디바이스에 NIC 칩 통합 가능성 확인
  - 외부 전원 케이블 연결 가능 (NVDIMM과 유사)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]


## 전체 요약

[[../paper-summaries/2019MICRO-summarize/netdimm_low-latency_near-memory_network_interface_architecture.md|전체 요약 보기]]
