---
tags: [paper, 2021, 2021ASPLOS, topic/dram, topic/gpu, topic/pim]
venue: "Proceedings of the 26th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '21)"
year: 2021
summary_path: "../paper-summaries/2021ASPLOS-summarize/simdram-a-framework-for-bit-serial-simd-processing-using-dram.md"
---

# SIMDRAM: A Framework for Bit-Serial SIMD Processing using DRAM

**Venue:** Proceedings of the 26th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '21)
**저자:** Nastaran Hajinazar (ETH Zürich, Simon Fraser University), Geraldo F. Oliveira (ETH Zürich), Sven Gregorio (ETH Zürich), João Dinis Ferreira (ETH Zürich), Nika Mansouri Ghiasi (ETH Zürich), Minesh Patel (ETH Zürich), Mohammed Alser (ETH Zürich), Saugata Ghose (University of Illinois at Urbana–Champaign), Juan Gómez-Luna (ETH Zürich), Onur Mutlu (ETH Zürich)

## 개요

- 현대 애플리케이션의 데이터 증가로 기존 CPU/GPU 중심 아키텍처에서 메모리와 프로세서 간 데이터 이동 비용이 전체 에너지의 **60% 이상** 차지
- Processing-in-Memory (PIM)은 데이터가 있는 곳 근처에서 연산을 수행하여 데이터 이동 비용을 줄이는 패러다임
- Processing-using-DRAM은 DRAM 셀의 물리적 특성을 활용하여 메모리 어레이 내에서 직접 연산 수행, 내부 대역폭과 병렬성을 활용
- Ambit 등 기존 Processing-using-DRAM 연구는 AND, OR, NOT과 같은 **기본 논리 연산만 지원**하며, 복잡한 연산(덧셈, 곱셈 등)은 지원하지 못하는 한계
- 기존 설계들은 DRAM 서브어레이에 **상당한 수정**이 필요하거나, **제한된 연산 세트**만 지원하여 유연성이 부족
-Processing-using-DRAM을 실용적으로 채택하기 위해서는 복잡한 연산의 효율적 구현과 임의 연산 지원이 모두 필요

## 방법론

### 3.1. 서브어레이 구성 (Subarray Organization)

- Ambit과 동일한 서브어레이 구조를 사용하여 DRAM 서브어레이의 최소 수정으로 연산 지원
- 세 가지 행 그룹으로 구성:
  - **D-group (Data)**: 프로그램 또는 시스템 데이터 저장, 일반 행 디코더로 접근
  - **C-group (Control)**: 상수 행 C0(전부 0)과 C1(전부 1)로 구성, 초기 입력값 또는 AND/OR 리듀싱에 사용
  - **B-group (Bitwise)**: 6개의 일반 행(T0-T3, DCC0, DCC1)로 구성, **세 행 동시 활성화(TRA)**가 가능한 특수 행 디코더에 연결
- B-group의 특수 행 디코더가 single address로 세 행을 동시에 활성화하여 MAJ 연산 수행

### 3.2. Step 1: 효율적 MAJ/NOT 구현

- AND/OR/NOT 기반 논리 표현을 MAJ/NOT 기반 표현으로 변환하는 과정
- **AOIG (AND-OR-Inverter Graph)** → **MIG (Majority-Inverter Graph)** 변환:
  - Step 1a: 각 AND/OR 프리미티브를 3-입력 MAJ 프리미티브로 단순 치환 (AND는 C=0, OR는 C=1)
  - Step 1b: 탐욕 알고리즘을 사용하여 비효율적인 MIG를 여러 MAJ 프리미티브를 합친 더 작은 MIG로 최적화
- 최적화된 MIG는 동일한 연산을 수행하면서 더 적은 논리 프리미티브와 AAP/AP 명령 시퀀스 필요

### 3.3. Step 2: µProgram 생성

- MIG와 DRAM 행 할당을 기반으로 연산을 실행할 µProgram 생성
- **µOps (마이크로연산)** 유형:
  - **Row Copy (AAP)**: 소스 주소에서 목적지 주소로 DRAM 행 복사
  - **Majority (AP)**: 세 DRAM 행에 대해 MAJ 논리 프리미티브 수행 (TRA 사용)
  - **Arithmetic**: addi, subi, comp, module 등 SIMDRAM 컨트롤 레지스터 연산
  - **Control**: bnez, done 등 루프 및 종료 제어
- **µRegisters**: 컨트롤 유닛에 위치한 레지스터 파일, B-group/C-group 행 주소 및 연산 피연산자 저장
- **DRAM 행 할당 알고리즘**: 선형 스캔 레지스터 할당에서 영감을 받되, TRA의 파괴적 특성과 제한된 compute row 수를 고려한 최적화 수행
- **µOp 최적화**: 동일 소스에서 복사하는 연쇄된 AAP를 하나의 AAP로 병합, AP 후 AAP 순서를 병합하여 명령 수 최소화
- **n-비트 연산 일반화**: 1-비트 MIG 연산을 n-비트 연산으로 확장하기 위해 루프 카운터와 주소 시프팅 활용

### 3.4. Step 3: 연산 실행

- **SIMDRAM 컨트롤 유닛**: 메모리 컨트롤러 확장, µProgram 실행 관리
- 핵심 구성 요소: bbop FIFO, µProgram Memory, µProgram Scratchpad, µOp Memory, µRegister Addressing Unit, µRegister File, Loop Counter, µOp Processing FSM, µPC
- 실행 흐름: CPU에서 bbop 명령 수신 → µProgram Scratchpad에서 로드 → µOp Memory로 복사 → µOp 순차 실행 → 반복

### 3.5. 지원 연산

- 16개 연산, 5개 유형 지원:
  - **N-입력 논리**: AND/OR/XOR 리듀싱
  - **관계 연산**: equality/inequality check, greater/less than, max/min
  - **산술 연산**: 덧셈, 뺄셈, 곱셈, 나눗셈, 절대값
  - **Predication**: if-then-else
  - **기타**: bitcount, ReLU
- 4개 요소 크기 지원: 8, 16, 32, 64비트

## 핵심 기여

- SIMDRAM은 Processing-using-DRAM을 위한 **최초의 엔드투엔드 유연한 프레임워크**로, 임의 연산의 효율적 DRAM 구현을 가능하게 함
- MAJ/NOT 기반 논리 최적화를 통해 Ambit 대비 **2.0×** 처리량 향상 달성
- 16개 뱅크 구현 시 CPU 대비 **88×** 처리량, **257×** 에너지 효율 향상
- 면적 오버헤드 **0.2%**로 실현 가능한 수준의 하드웨어 비용
- DRAM 공정 기술이 축소되더라도 올바른 동작을 보장하는 높은 신뢰성
- Future work: 컴파일러 자동 코드 생성, THP와의 통합, RowHammer 방지 기법과의 결합

## 주요 결과

- **gem5 시뮬레이터** 기반 구현
- Intel Skylake CPU, NVIDIA Titan V GPU, Ambit과 비교 평가
- **데이터 전처리 유닛 (Transposition Unit)**: LLC와 메모리 컨트롤러 사이에 위치, 수평/수직 데이터 레이아웃 간 변환 수행
  - Object Tracker: SIMDRAM 객체 추적
  - 수평→수직 및 수직→수평 변환 버퍼: single cycle 변환 지원
- **ISA 확장**: bbop_trsp_init, bbop_op, bbop_if_else 등 SIMDRAM 명령 추가
- x86 ISA의 미사용 opcode 공간 활용 (389개 미사용 opcode 확인)
- **서브어레이당 compute row**: 1024행 중 1006행 D-group, 2행 C-group, 16행 B-group

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2021ASPLOS-summarize/simdram-a-framework-for-bit-serial-simd-processing-using-dram.md|전체 요약 보기]]
