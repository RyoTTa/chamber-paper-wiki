---
tags: [ndp, near-memory-processing, memory-channel-network, distributed-computing, mpi]
venue: MICRO
year: 2018
summary_path: paper-summaries/2018MICRO-summarize/application-transparent-near-memory-processing-architecture-with-memory-channel-network.md
---

# Application-Transparent Near-Memory Processing Architecture with Memory Channel Network (MCN)

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Mohammad Alian, Seung Won Min, Hadi Asgharimoghaddam, Ashutosh Dhar, Dong Kai Wang, Thomas Roewer, Adam McPadden, Oliver O'Halloran, Deming Chen, Jinjun Xiong, Daehoon Kim, Wen-mei Hwu, Nam Sung Kim (University of Illinois Urbana-Champaign, IBM Research, IBM Systems, DGIST)

---

## 개요

DDR 메모리 채널 위에서 이더넷 통신을 에뮬레이션하는 MCN(Memory Channel Network) 아키텍처를 제안. 호스트와 NDP 프로세서가 이더넷 링크로 연결된 독립 노드처럼 보이게 하여, 기존 분산 컴퓨팅 프레임워크(MPI, Spark)를 변경 없이 NDP와 함께 사용 가능.

## 방법론

- **MCN DIMM:** Buffered DIMM 확장 — 소형 AP(예: Snapdragon 835)를 버퍼 디바이스에 통합, DDR PHY로 호스트 MC와 인터페이스
- **MCN 드라이버:** TCP/IP 패킷을 DDR 메모리 채널로 리다이렉트하여 이더넷 연결错觉 제공
- **패킷 포워딩:** 호스트가 모든 트래픽을 중재 (MCN-to-MCN 통신도 호스트를 통해)
- **네트워크 최적화:** IPv4 체크섬 바이패스, 9KB MTU, TCP Segmentation Offload (TSO), 메모리 인터리빙
- **FPGA 프로토타입:** ConTutto FPGA 보드 + IBM POWER8 시스템으로 실증

## 핵심 기여

- **애플리케이션 투명성:** 기존 MPI/Spark 코드를 변경 없이 NDP 프로세서와 함께 실행
- DDR 메모리 채널 위에서 TCP/IP 기반 네트워킹 에뮬레이션
- 서버 내 NDP + 서버 간 분산 컴퓨팅을 하나의 프레임워크로 통합

## 주요 결과

- 8 MCN DIMM 서버가 9 노드 이더넷 클러스터 대비 **4.56배** 처리량, **47.5%** 에너지 절감
- 호스트-MCN 간 레이턴시가 10GbE 대비 **최대 75.4%** 감소
- 집적 DRAM 대역폭 활용이 최대 **8.17배** 향상
- NPB 애플리케이션에서 1~3 MCN DIMM으로 **27.2~45.3%** 실행 시간 단축
- IBM POWER8 + FPGA 프로토타입으로 실현 가능성 입증

## 한계점

- TCP 혼잡 제어가 빠른 메모리 채널에 비해 느려 풀 대역폭 도달에 수 초 소요
- ACK 메시지 오버헤드가 최대 **~25%**
- 각 MCN DIMM은 단일 채널 대역폭(최대 12.8GB/s)만 사용 가능
- 소프트웨어 폴링 기반 패킷 수신으로 인한 CPU 오버헤드

## 관련 개념

- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]

## 전체 요약

[application-transparent-near-memory-processing-architecture-with-memory-channel-network.md](../../paper-summaries/2018MICRO-summarize/application-transparent-near-memory-processing-architecture-with-memory-channel-network.md)
