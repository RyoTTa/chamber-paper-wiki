---
tags: [paper, 2020, 2020MICRO, topic/disaggregation, topic/dram, topic/memory-tiering, topic/near-data-processing, topic/security, topic/virtual-memory]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO) 2020"
year: 2020
summary_path: "../paper-summaries/2020MICRO-summarize/thymesisflow-a-software-defined-hw-sw-co-designed-interconnect-stack-for-rack-scale-memory-disaggregation.md"
---

# ThymesisFlow: A Software-Defined, HW/SW co-Designed Interconnect Stack for Rack-Scale Memory Disaggregation

**Venue:** IEEE/ACM International Symposium on Microarchitecture (MICRO) 2020
**저자:** Christian Pinto, Dimitris Syrivelis, Michele Gazzetti, Panos Koutsovasilis, Andrea Reale, Kostas Katrinis, H. Peter Hofstee (IBM Research Europe, IBM Systems)

## 개요

- 클라우드 인프라에서 CPU 대비 메모리 수요 비율이 3개 이상의 차이를 보이며, 정적 서버 구성으로는 리소스 활용도가 낮음
- 기존 소프트웨어 기반 메모리 분리(remote memory) 접근 방식은 page-fault/스와핑 기반으로 과도한 OS 수정, 메모리 스래싱, 호스트 네트워크 스택 과부하 문제 발생
- Google Cluster Data Traces 분석: 기존 고정형 데이터센터에서 CPU 파편화 지수 16%, 메모리 파편화 지수 29.5% 발생; 분리형 모델은 각각 3.86%, 9.2%로 대폭 감소
- 하드웨어 수준의 메모리 분리(hardware-level memory disaggregation)는 OS 수준 접근의 한계를 극복할 수 있지만, 상용 하드웨어에서의 완전한 프로토타입 구현 사례가 없었음
- 메모리 분리가 제대로 작동하면 총소유비용(TCO) 절감, 하드웨어 갱신 주기 분리, 리소스 활용도 극대화 가능

## 방법론

### 3.1. 하드웨어 인터커넥트 아키텍처

- **Compute endpoint:** 원격 메모리를 호스트 물리 주소 공간에 매핑
  - Effective address → Real address (MMU) → Device Internal Address → Remote Effective address 변환
  - RMMU(Remote Memory Management Unit)가 섹션 테이블 기반 주소 변환 수행
  - Linux kernel sparse memory model과 1:1 매핑으로 섹션 단위 분리 메모리 관리
- **Memory-stealing endpoint:** 로컬 호스트 메모리의 일부를 원격 노드에 노출
  - PASID(Process Address Space ID)를 하드웨어에 등록하여 원격 접근 허용
  - 수동 동작: 트랜잭션을 수신 채널로 응답, 자체 수정 불필요
- **Routing layer:** 네트워크 정보 기반 독립적 트랜잭션 포워딩
  - Channel bonding: 활성 thymesisflow의 트랜잭션을 라운드로빈 방식으로 다중 물리 채널 활용
  - 동시 연결된 엔드포인트 수에 제한 없음
- **네트워크 facing stack:** credit 기반 백프레셔, 프레임 리플레이 지원
  - 32B wide 데이터 패스, 4개 bonded GTX 트랜시버 (25Gbit/sec each)
  - 커스텀 프레이밍 스킴으로 신뢰성 보장

### 3.2. 주소 변환 프로세스

- Compute endpoint에서 emitted effective address가 RMMU를 거쳐 변환됨
- 섹션 테이블 엔트리: 주소 오프셋 + 네트워크 식별자
- 동일 섹션에 속한 모든 트랜잭션은 동일한 네트워크 포워딩 정보 수신
- 활성 thymesisflow: 주어진 compute-memory 엔드포인트 간 특정 섹션의 모든 트랜잭션 그룹

### 3.3. 운영체제 지원

- ThymesisFlow 설정 공간을 MMIO 영역으로 Linux에 노출 (OpenCAPI 범용 드라이버)
- 사용자 공간 에이전트가 데몬으로 실행되어 구성 명령 수행
- Linux memory hotplug 기능으로 런타임에서 분리된 메모리의 물리적/논리적 연결 수행
- 각 분리 메모리 섹션이 CPU 없는 NUMA 노드로 매핑 → NUMA 페이지 마이그레이션 알고리즘 활용 가능

### 3.4. 제어 플레인 (Control Plane)

- 시스템 상태를 무방향 그래프로 모델링 (노드: compute/memory 엔드포인트, 트랜시버, 스위치 포트)
- 분리 메모리 할당 요청 시 그래프를 순회하여 최적 경로 탐색 및 자원 예약
- JanusGraph 분산 그래프 데이터베이스를 백엔드로 사용
- REST API를 통한 상호작용, 접근 제어 시스템으로 보안 보장
- 향후 OpenStack, Kubernetes와의 통합 계획

## 핵심 기여

- ThymesisFlow는 상용 하드웨어에서 구현한 최초의 하드웨어 수준 메모리 분리 풀스택 프로토타입으로, 실용성을 입증
- OpenCAPI + POWER9 조합으로 950ns RTT 지연시간 달성, 약 10GiB/s sustainable bandwidth 확보
- 클라우드 워크로드(VoltDB, Memcached, Elasticsearch)에서 disaggregated memory가 유사하거나 더 나은 성능을 달성하면서도 절반의 CPU 리소스 사용 가능
- Scale-out 대체 가능성을 보여주어, 리소스 활용도 향상 및 TCO 절감 기대
- 소프트웨어 정의 제어 플레인과 Linux NUMA 통합으로 런타임 동적 리소스 할당 지원
- 오픈소스 공개로 하드웨어 수준 분리 연구 가속화에 기여

## 주요 결과

- IBM POWER9 AC922 서버 3대 사용 (각각 듀얼소켓, 32 물리코어, 128 병렬 스레드, 512GB RAM)
- 2대에 Alpha Data 9V3 FPGA 카드 장착 (Xilinx Ultrascale)
- OpenCAPI FPGA 스택 인스턴스: POWER9 프로세서와 200Gbit/sec로 인터페이스
- Xilinx Aurora 프로토콜 기반 네트워크 (CRC 지원)
- 2개 독립 채널, 각 100Gbit/sec (bonding 시 200Gbit/sec)
- 하드웨어 데이터 패스 RTT 지연: 약 950ns (FPGA 4회, serDES 6회 교차)
- Linux 커널 5.0.0, memory hotplug 및 NUMA 확장 적용
- 소프트웨어 및 하드웨어 디자인 모두 OpenPower 오픈소스로 공개

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/security.md|Security]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2020MICRO-summarize/thymesisflow-a-software-defined-hw-sw-co-designed-interconnect-stack-for-rack-scale-memory-disaggregation.md|전체 요약 보기]]
