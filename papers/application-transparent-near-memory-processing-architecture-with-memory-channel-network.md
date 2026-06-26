---
tags: [paper, 2018, 2018MICRO, topic/cache, topic/dram, topic/near-data-processing]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/application-transparent-near-memory-processing-architecture-with-memory-channel-network.md"
---

# Application-Transparent Near-Memory Processing Architecture with Memory Channel Network

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Mohammad Alian, Seung Won Min, Hadi Asgharimoghaddam, Ashutosh Dhar, Dong Kai Wang, Thomas Roewer, Adam McPadden, Oliver O'Halloran, Deming Chen, Jinjun Xiong, Daehoon Kim, Wen-mei Hwu, Nam Sung Kim (University of Illinois Urbana-Champaign, IBM Research, IBM Systems, DGIST)

## 개요

- 데이터 집약적 애플리케이션의 서버 성능은 DRAM 용량과 DDR 대역폭에 의해 제한됨
- 3D XPoint 등 차세대 비휘발성 메모리 기술의 배포가 예상되지만, 컴퓨팅 처리량과 메모리 대역폭도 용량 증가에 비례하여 증가해야 비용 효율적
- 기존 NDP(Near-Memory Processing) 아키텍처의 한계:
  - 프로세서와 메모리를 긴밀하게 통합하여 프로세서에 더 높은 대역폭 노출
  - 그러나 **애플리케이션 준비도(application readiness) 문제:** 타겟 애플리케이션에 큰 변경이 필요
  - 호스트와 NDP 프로세서 간 통신을 오케스트레이션하는 데 상당한 변경 필요 → 광범위한 도입 장벽
- 많은 데이터 집약적 애플리케이션이 이미 분산 컴퓨팅 프레임워크(Hadoop, Spark, MPI)를 기반으로 구축됨
- 기존 NDP 아키텍처의 처리 모델도 분산 컴퓨팅 프레임워크에서 영감을 받았으나, 호스트-NDP 간 통신에 비표준 인터페이스 사용

## 방법론

### 3.1. MCN DIMM (하드웨어)

- **MCN 프로세서:** Qualcomm Snapdragon 835과 같은 소형 AP(Application Processor)를 버퍼 디바이스에 통합
- **MCN 인터페이스:**
  - DDR PHY를 사용하여 호스트 메모리 컨트롤러(MC)와 MCN 프로세서 간 인터페이스
  - 네트워크 인터페이스와 유사하지만 Ethernet PHY 대신 DDR PHY 사용
  - **SRAM 버퍼:** 48KB TX/RX 순환 버퍼로 패킷 전송/수신 관리
  - 패킷 길이 필드 + 패킷 데이터로 MCN 메시지 포맷
- **MCN 프로세서:** 경량 OS + 분산 컴퓨팅 프레임워크 실행에 필요한 네트워크 소프트웨어 레이어
- **구성 예:** 8개 MCN DIMM이 서버에 장착되어 최대 8개 NDP 노드 제공

### 3.2. MCN 드라이버 (소프트웨어)

- **패킷 포워딩 엔진(C1):**
  - 호스트 측: dst-mac이 호스트 인터페이스 MAC과 일치하면 → 상위 네트워크 스택으로 전달
  - MCN 측: dst-m이 호스트 인터페이스 MAC과 일치하면 → 상위 네트워크 스택으로 전달
  - 브로드캐스트: 받은 패킷을 모든 연결된 MCN 노드로 전달
  - MCN-to-MCN 통신: 호스트가 패킷을 중계하여 모든 MCN 간 통신 가능
- **메모리 매핑 유닛(C2):**
  - ioremap으로 uncacheable 메모리 매핑 → 읽기 대역폭 제한
  - memremap + MEMREMAP_WC 플래그로 쓰기 결합(write combining) 지원 → 캐시 라인 크기로 메모리 접근 가능
  - 호스트/MCN 모두에서 쓰기 결합 사용으로 대역폭 극대화
- **폴링 에이전트(C3):**
  - 메모리 매핑된 SRAM 버퍼를 주기적으로 폴링하여 수신된 패킷 확인
  - 하드웨어 인터럽트 대신 소프트웨어 폴링으로 오버헤드 최소화

### 3.3. 네트워크 최적화

- **IPv4 체크섬 바이패스:** 메모리 채널이 ECC/CRC로 보호되므로 TCP/IP 체크섬 계산 불필요 → 오버헤드 감소
- **대형 MTU (9KB):** 메모리 채널의 BER(Bit Error Rate)이 이더넷 대비 수 배 낮으므로 큰 프레임 크기 사용 가능 → 프로토콜 처리 오버헤드 경감
- **TCP Segmentation Offload (TSO):**
  - 대용량 사용자 데이터를 MTU 크기의 여러 세그먼트로 분할하는 작업을 MCN 프로세서에 오프로딩
  - MCN 프로세서가 TCP/IP 헤더와 함께 대용량 데이터를 전달하면, MCN 하드웨어가 세그먼테이션 수행
- **메모리 인터리빙:** 두 채널에서 64바이트 단위로 인터리빙하여 대역폭 활용도 극대화

### 3.4. FPGA 프로토타입 구현

- **ConTutto FPGA 보드:** Intel Altera Stratix V FPGA 기반
- **NIOS II 임베디드 프로세서:** 266MHz로 구동되는 MCN 프로세서 역할
- **Avalon 버스:** FPGA 내부 인터커넥트
- **BRAM:** MCN SRAM 버퍼 구현
- **DMI (Differential Memory Interface):** IBM POWER8 시스템과의 인터페이스
- IBM S824L 시스템에 실험용 버퍼 DIMM으로 장착하여 프로토타입 검증

## 핵심 기여

- **핵심 기여:** DDR 메모리 채널 위에서 이더넷 통신을 에뮬레이션하는 MCN 아키텍처 제시
- **가장 큰 장점:** **애플리케이션 투명성** — 기존 분산 컴퓨팅 프레임워크(MPI, Spark)를 변경 없이 NDP 프로세서와 함께 사용 가능
- **성능:** 8 MCN DIMM 서버가 9 노드 이더넷 클러스터 대비 **4.56배** 처리량, **47.5%** 에너지 절감
- **레 이턴시:** 호스트-MCN 간 레이턴시가 10GbE 대비 **최대 75.4%** 감소
- **대역폭:** 집적 DRAM 대역폭 활용이 최대 **8.17배** 향상
- **실증:** IBM POWER8 + FPGA 프로토타입으로 MCN DIMM의 실현 가능성 입증
- **의의:** 서버 내 NDP와 서버 간 분산 컴퓨팅을 하나의 표준 프레임워크로 통합하여, NDP의 실용화에 크게 기여
- **한계:** TCP/IP 스택 오버헤드, 단일 채널 대역폭 제한 → 향후 전용 프로토콜로 개선 가능

## 주요 결과

- **하드웨어 프로토타입:**
  - ConTutto FPGA 보드 + IBM POWER8 시스템
  - NIOS II 프로세서 (266MHz), 32GB DDR3-1066 DIMM × 2
  - 실증 가능성 검증: MPI 'Hello World' 프로그램 실행으로 호스트-MCN 간 통신 확인
- **시뮬레이션:**
  - dist-gem5 기반 풀시스템 시뮬레이션
  - NIOS II 프로세서의 제한된 컴퓨팅 능력 보완을 위한 시뮬레이션 기반 평가
- **소프트웨어:**
  - MCN 드라이버 (호스트/MCN 프로세서용)
  - 경량 OS + 네트워크 소프트웨어 레이어
  - MPI, Spark 등 기존 분산 컴퓨팅 프레임워크와 호환

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/application-transparent-near-memory-processing-architecture-with-memory-channel-network.md|전체 요약 보기]]
