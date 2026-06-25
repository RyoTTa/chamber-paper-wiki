---
tags: [paper, 2022, 2022ASPLOS, topic/disaggregation, topic/dram, topic/memory-tiering]
venue: "ACM SIGPLAN International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS) 2022"
year: 2022
summary_path: "../paper-summaries/2022ASPLOS-summarize/clio-a-hardware-software-co-designed-disaggregated-memory-system.md"
---

# Clio: A Hardware-Software Co-Designed Disaggregated Memory System

**Venue:** ACM SIGPLAN International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS) 2022
**저자:** Zhiyuan Guo, Yizhou Shan, Xuhao Luo, Yutong Huang, Yiying Zhang (University of California, San Diego)

## 개요

- 현대 데이터센터 애플리케이션(그래프 컴퓨팅, 데이터 분석, 딥러닝)은 대용량 메모리 접근에 대한 수요가 지속적으로 증가
- 서버는 pin, space, power 제한으로 인해 **메모리 용량 벽(Memory Capacity Wall)**에 직면 → 로컬 머신이 제공할 수 있는 것 이상의 솔루션이 필요
- 기존 메모리 분산(Memory Disaggregation) 연구는 두 극단적 접근법으로 나뉨:
  - **서버 기반 MN(Memory Node)**: 일반 서버로 MN 구축/에뮬레이션 → 높은 비용, tail latency 및 확장성 한계
  - **원시 장치 기반 MN**: 처리 능력이 없는 원시 메모리 디바이스 사용 → 성능, 보안, 관리 문제
- 서버 기반 접근의 근본적 문제: 호스트 서버의 NIC와 가상 메모리 시스템 간 상호작용에서 기인하는 비용 및 성능/확장성 한계
- 원시 장치 기반 접근의 문제: MN에 처리 능력이 없어 모든 데이터 및 제어 플레인이 CN(Compute Node)에서 처리 → 확장성 및 성능 문제

## 방법론

### 3.1. 전체 시스템 구성

- **CLib**: CN 측 사용자 공간 라이브러리 → 애플리케이션이 원격 메모리에 접근하는 인터페이스
- **CBoard**: 하드웨어 기반 MN 디바이스 (Xilinx ZCU106 MPSoC FPGA 보드로 프로토타이핑)
- 여러 애플리케이션 프로세스가 다른 CN에서 동일한 CBoard로부터 메모리 할당 가능
- 각 프로세스는 자체 원격 가상 메모리 주소 공간 보유, 하나의 원격 가상 메모리 주소 공간은 여러 CBoard에 걸쳐 확장 가능
- 바이트(granularity) 수준 원격 메모리 읽기/쓰기 지원, 동기화 프리미티브 제공

### 3.2. 하드웨어 기반 가상 메모리 시스템

- **오버플로우 없는 해시 기반 페이지 테이블 설계**:
  - 모든 페이지 테이블 조회가 경계 있고 낮은 지연 시간 보장 (구현에서 최대 1회 DRAM 접근 시간)
  - 모든 페이지 테이블 엔트리의 총 크기가 클라이언트 프로세스 수에 비례하지 않음
- 페이지 테이블은 MN 하드웨어 파이프라인에서 가상-물리 메모리 주소 매핑 및 접근 권한 검사에 사용
- 하드웨어에서 페이지 폴트 처리 완료: 물리적 메모리 할당을 SoC에서 실행되는 소프트웨어로 이동
- **사전 생성 기반 페이지 폴트 처리**: freely available 물리적 페이지를 고정 크기 버퍼에 미리 생성 → 하드웨어 파이프라인이 페이지 폴트 처리 시 가져다 사용 → 할당 연산을 성능 결정적 경로에서 제거

### 3.3. 네트워크 시스템

- CN-요청-MN-응답 모델 기반 커스텀 연결 없는 신뢰성 전송 프로토콜
- 요청 ID, 전송 로직, 재전송 버퍼, 혼잡 및 incast 제어를 모두 CN 측에서 관리
- CN 측에서 전체 메모리 요청의 순서 지정 및 재시도로 신뢰성 보장
- MN은 요청 간 상태나 순서를 고려할 필요 없음 → MN의 하드웨어 리소스가 클라이언트 수에 비례하지 않음

### 3.4. 연산 오프로딩 프레임워크

- MN에서의 연산 오프로딩 지원 → CN 측에서 MN으로 연산을 오프로딩할 수 있는 프레임워크 제공
- 하드웨어 기반으로 효율적인 연산 오프로딩 가능

## 핵심 기여

- **핵심 기여 1**: MN에 적절한 수준의 처리 능력을 갖춘 하드웨어 기반 메모리 분산 솔루션 제안 → 기존 두 극단적 접근의 단점 극복
- **핵심 기여 2**: 상태 제거 기법을 통해 100Gbps throughput, 마이크로초급 latency를 달성하면서도 높은 확장성 확보
- **핵심 기여 3**: 하드웨어/소프트웨어 공동 설계(Co-design)로 가상 메모리, 네트워크, 연산 오프로딩을 통합
- **핵심 기여 4**: FPGA 프로토타입으로 실용적 구현 가능성 입증, CPU/SmartNIC 기반 대비 1.1x~3.4x 에너지 절약
- **의의**: 메모리 분산을 위한 새로운 하드웨어-소프트웨어 공동 설계 패러다임 제시, 데이터센터의 메모리 용량 벽 문제 해결을 위한 실용적 방향 제시

## 주요 결과

- **프로토타입 하드웨어**: Xilinx ZCU106 MPSoC FPGA 보드
- **구현 언어**: 하드웨어 파이프라인(Verilog/VHDL), 소프트웨어(C/C++)
- **ARM SoC**: 메타데이터/제어 플레인 처리를 위한 저전력 프로세서
- **지원 애플리케이션**: FaaS 스타일 이미지 압축 유틸리티, radix-tree 인덱스, 키-값 스토어
- **소스 코드**: https://github.com/WukLab/Clio 에 공개

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]


## 전체 요약

[[../paper-summaries/2022ASPLOS-summarize/clio-a-hardware-software-co-designed-disaggregated-memory-system.md|전체 요약 보기]]
