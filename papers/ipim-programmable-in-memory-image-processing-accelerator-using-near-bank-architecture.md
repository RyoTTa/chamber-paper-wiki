---
tags: [paper, 2020, 2020ISCA, topic/dram, topic/gpu, topic/pim]
venue: "2020 ACM/IEEE 47th Annual International Symposium on Computer Architecture (ISCA 2020)"
year: 2020
summary_path: "../paper-summaries/2020ISCA-summarize/ipim-programmable-in-memory-image-processing-accelerator-using-near-bank-architecture.md"
---

# iPIM: Programmable In-Memory Image Processing Accelerator Using Near-Bank Architecture

**Venue:** 2020 ACM/IEEE 47th Annual International Symposium on Computer Architecture (ISCA 2020)
**저자:** Peng Gu, Xinfeng Xie, Yufei Ding, Guoyang Chen, Weifeng Zhang, Dimin Niu, Yuan Xie (UCSB, Alibaba Cloud, Alibaba DAMO Academy)

## 개요

- 이미지 처리 워크로드(머신러닝, 바이오메디컬, GIS 등)는 고성능/고효율 가속기를 필요로 하며, GPU는 현재 최첨단 가속기이나 메모리 대역폭 병목(memory bandwidth bottleneck)에 직면.
- NVIDIA Tesla V100 GPU 프로파일링 결과: 이미지 처리 벤치마크에서 **57.55% DRAM Utilization**, **3.43% ALU Utilization**으로 명백한 대역폭 제한(bandwidth-bound) 동작 확인.
- 3D-PIM near-bank 아키텍처는 각 DRAM 뱅크 인접에 연산 로직을 배치하여 TSV 대역폭 제약을 극복하고 **10× 피크 대역폭** 향상 가능하나, 프로그래머빌리티(programmability) 지원이 부족.
- 기존 near-bank 설계는 제어 코어(control core)를 각 뱅크에 직접 연결 시 면적 오버헤드가 크며, 다양한 이미지 처리 파이프라인의 이질적인 연산/메모리 패턴을 지원하기 어려움.
- Halide 컴파일러 최적화(GPU용 pipeline fusion)도 이미지 처리의 메모리 바운드 특성을 근본적으로 해결하지 못함.

## 방법론

### 3.1. 마이크로아키텍처 개요

- iPIM은 **cube → vault → process group → process engine**의 위계적 구조 (Figure 2(a))
- **Cube**: HMC/HBM 유사 구조, SERDES 링크로 다중 cube 간 연결
- **Vault**: 각 cube에 16개, 다중 3D 스택 레이어(PIM 다이 4-8개 + 베이스 로직 다이)로 구성
- **Process Group**: 각 vault 내에서 동일 기능을 가진 뱅크 그룹
- **Process Engine**: 각 뱅크에 부착된 경량 연산 유닛 (ALU + 소규모 버퍼)
- 베이스 로직 다이의 제어 코어가 TSV를 통해 모든 process engine에 명령어를 브로드캐스트하고, 모든 연산 유닛이 병렬로 잠금 동기(lockstep) 실행
- 면적 오버헤드: DRAM 다이 대비 **약 10.71%** 수준으로 경량 설계

### 3.2. SIMB (Single-Instruction-Multiple-Bank) ISA

- SIMD 방식의 명령어 집합으로, 하나의 명령어가 여러 뱅크의 연산 유닛을 동시에 제어
- **SIMD 연산**: 뱅크의 높은 I/O 폭(128b)을 활용한 병렬 연산 지원
- **유연한 데이터 이동**: near-bank 메모리 계층 내에서의 데이터 전송 명령어
- **제어 흐름 명령어**: 인덱스 계산(index calculation)을 위한 분기/점프 명령어
- **동기화 프리미티브**: vault 간 통신을 위한 동기화 명령어
- Figure 3에서 SIMB ISA의 명령어 포맷과 예시 제시
- 이미지 처리의 핵심 연산(element-wise, stencil, histogram 등)을 SIMB 명령어로 효율적으로 매핑

### 3.3. Halide 기반 컴파일 플로우

- **프론트엔드**: Halide 알고리즘 설명을 iPIM용 새로운 스케줄로 변환
  - iPIM 전용 스케줄 설계: 데이터 병렬성과 뱅크 간 분배 최적화
- **백엔드 최적화**:
  1. **레지스터 할당**: 리소스 충돌을 줄이기 위한 레지스터 최적 배치
  2. **명령어 재배치**: 명령어 수준 병렬성(ILP) 활용을 위한 명령어 순서 최적화
  3. **메모리 순서 강제(memory-order enforcement)**: DRAM row-buffer locality 최적화
- 프로그래머는 Halide 알고리즘과 스케줄만 기술하면 iPIM 하드웨어로의 매핑을 컴파일러가 자동으로 수행

## 핵심 기여

- iPIM은 3D-stacking near-bank 아키텍처를 활용한 최초의 프로그래머블 인메모리 이미지 처리 가속기로, GPU의 메모리 대역폭 병목을 극복.
- Decoupled control-execution 아키텍처와 SIMB ISA로 경량 프로그래머빌리티를 달성하고, Halide 기반 컴파일 프레임워크로 광범위한 이미지 처리 앱을 지원.
- **11.02× speedup, 79.49% energy saving** (NVIDIA V100 GPU 대비), 백엔드 최적화만으로도 **3.19× 추가 성능 향상**.
- 이미지 처리 워크로드의 핵심 병목이 연산이 아닌 대역폭에 있음을 실증하고, near-bank PIM이 이를 효과적으로 해결하는 방법을 제시.
- 프로그래밍 가능성, 하드웨어 효율성, 컴파일러 지원의 세 가지 측면을 동시에 해결한 종합적 연구.

## 주요 결과

- **구현 언어**: C++ 기반 Halide 컴파일러 프레임워크 + RTL 하드웨어 설계
- **하드웨어 기술**: 3D-stacking DRAM (HBM/HMC 기반)
- **시뮬레이션**: 커스텀 사이클-레벨 시뮬레이터 + 면적/전력 추정 도구
- **시스템 구성 요소**:
  - 제어 코어 (베이스 로직 다이)
  - Process Engine: ALU (INT32/FP32), 레지스터 파일, 로컬 버퍼
  - TSV 인터커넥트 (vault당 64개)
  - 온칩 네트워크 (vault 간 통신)
- **평가 대상**: 10개 대표적 이미지 처리 애플리케이션 (단일 스테이지 + 다중 스테이지 파이프라인)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2020ISCA-summarize/ipim-programmable-in-memory-image-processing-accelerator-using-near-bank-architecture.md|전체 요약 보기]]
