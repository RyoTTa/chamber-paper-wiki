---
tags: [paper, 2022, 2022ASPLOS, topic/dram]
venue: "ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS) 2022"
year: 2022
summary_path: "../paper-summaries/2022ASPLOS-summarize/software-defined-address-mapping-a-case-on-3d-memory.md"
---

# Software-Defined Address Mapping: A Case on 3D Memory

**Venue:** ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS) 2022
**저자:** Jialiang Zhang (University of Pennsylvania), Michael Swift (University of Wisconsin-Madison), Jing (Jane) Li (University of Pennsylvania)

## 개요

- DDR 기반 메인 메모리는 현대 데이터 센터에서 치명적인 성능 병목 현상이며, 메모리 대역폭이 데이터 폭발에 비해 따라가지 못함
- 프로세서 기술 및 애플리케이션의 새로운 트렌드로 문제 악화: 1) 단일 칩에 통합된 범용 코어와 가속기 수 증가로 DRAM 접근 경쟁 심화, 2) 데이터 분석 및 그래프 처리와 같은 주변장치 애플리케이션이 데이터 집약적이고 점점 더 메모리 바운드가 됨
- 3D-스택 메모리(HBM, HMC)는 TSV 기술을 활용하여 10배 이상의 채널 수준 병렬성(CLP)을 제공하지만, 완전히 활용하기 어려움
- CLP 활용도가 메모리 컨트롤러의 주소 매핑에 크게 의존하며, 프로그램의 데이터 접근 패턴에 매우 민감함
- 기존 하드웨어 전용 메커니즘은 단일 주소 매핑에 기반하여 제한된 성능 향상만 달성
- 기존 소프트웨어 전용 메커니즘(페이지 컬러링 등)은 페이지 단위로 제어하여 3D 메모리에 필요한 캐시라인 수준의 세밀한 제어가 불가능

## 방법론

### 3.1. 청크 기반 주소 매핑 관리
- 거칠은 단위의 청크 기반 주소 매핑을 사용하여 세밀한 하드웨어 데이터 배치 달성
- 변수 수준 데이터 접근 정보를 활용하여 동일한 접근 패턴을 가진 인접 물리적 주소에 메타데이터 연결
- 청크 크기는 페이지 크기와 독립적이며 일반적으로 페이지보다 큼
- 정확성 보장 및 저장/성능 오버헤드 최소화를 위한 청크 크기 선택 필요

### 3.2. 런타임 메모리 할당기
- 메모리 할당 호출을 미리 구성된 물리적 메모리 청크 풀에서 충족하거나 Desired 매핑으로 자유 메모리를 재구성
- 물리적 주소를 채널/뱅크/행의 내부 메모리 구조로 매핑하는 주소 매핑 유닛(AMU) 추가
- AMU 구성을 저장하는 작은 SRAM(67KB)인 청크 매핑 테이블(CMT) 추가
- 가상 페이지와 물리 프레임 할당에 대한 두 가지 간단한 제약 조건으로 데이터 정확성 보장

### 3.3. 머신러닝 기반 접근 패턴 자동 식별
- 외부 메모리 접근에 가장 큰 기여를 하는 변수의 접근 패턴을 자동으로 식별하는 머신러닝 방법 개발
- 유사한 접근 패턴을 가진 변수를 클러스터링하여 SDAM의 오버헤드 감소
- 축소된 데이터 접근 패턴 집합으로 OS가 주소 매핑을 제어하고 관리하기更容易

### 3.4. 하드웨어-소프트웨어 협업 메커니즘
- Linux 컨널과 C 언어 메모리 할당기를 확장하여 다중 주소 매핑 지원
- 하나의 청크에 하나의 주소 매핑만 연결되도록 보장하는 물리 프레임 할당 규칙
- FPGA 기반 RISC-V 프로세서, 근처 메모리 가속기 및 HBM 모듈로 구성된 실제 시스템 프로토타입에서 시연

## 핵심 기여

- SDAM은 소프트웨어와 하드웨어의 협업을 통해 3D 메모리의 CLP를 효과적으로 활용하는 최초의 시스템 메커니즘
- 하드웨어 전용 메커니즘의 세밀한 제어와 소프트웨어 전용 메커니즘의 다중 지원 장점을 결합
- 실제 FPGA 기반 프로토타입에서 표준 CPU 벤치마크 1.41배, 데이터 집약적 벤치마크 1.84배, 근처 메모리 가속기 2.58배 성능 향상 달성
-未来的 3D 메모리 시스템에서 가속기 기반 시스템이 SDAM으로부터 더 큰 이점을 얻을 수 있음을 시사
- 머신러닝을 활용한 접근 패턴 자동 식별로 프로그래머의 부담을 줄이면서 시스템 최적화 달성

## 주요 결과

- 구현 언어: C (Linux 컨널 및 glibc 수정)
- 하드웨어 플랫폼: Xilinx VCU37P FPGA 플랫폼
- 프로세서: 4코어 RISC-V CPU
- 메모리: 8GB HBM2 모듈
- 소프트웨어: Linux 컨널 4.15, glibc 2.26 기반 수정
- 근처 메모리 가속기 통합
- 시스템 구성요소: AMU (Address Mapping Unit), CMT (Chunk Mapping Table), 수정된 메모리 할당기

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2022ASPLOS-summarize/software-defined-address-mapping-a-case-on-3d-memory.md|전체 요약 보기]]
