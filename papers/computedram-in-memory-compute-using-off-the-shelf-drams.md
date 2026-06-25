---
tags: [paper, 2019, 2019MICRO, topic/dram, topic/pim]
venue: "52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO-52), 2019"
year: 2019
summary_path: "../paper-summaries/2019MICRO-summarize/computedram-in-memory-compute-using-off-the-shelf-drams.md"
---

# ComputeDRAM: In-Memory Compute Using Off-the-Shelf DRAMs

**Venue:** 52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO-52), 2019
**저자:** Fei Gao (Princeton University), Georgios Tziantzioulis (Princeton University), David Wentzlaff (Princeton University)

## 개요

- 현대 컴퓨팅 시스템에서 프로세서와 메모리 간 데이터 이동은 전체 시스템 에너지의 상당 부분을 차지하고, 프로그램 실행 시간에 큰 비중으로 기여한다. 프로세서 코어 수가 증가하는 반면 **메모리 대역폭은 이를 따라가지 못하여 "Memory Wall" 문제가 지속**된다.
- 프로세서와 오프칩 DRAM 간 통신 레이턴시 개선이 컴퓨팅 리소스 증가 속도보다 느려, 메모리 병목 현상이 더욱 심화되고 있다.
- 기존 인메모리 컴퓨팅(In-Memory Computing) 접근법들은 △최신 메모리 기술(ReRAM, PCM 등)을 사용하거나 △RAM 배열에 추가 회로를 탑재하는 방식을 취하였다. 그러나 **DRAM 산업의 치열한 저마진 특성**으로 인해 제조사들은 DRAM에 추가 로직을 통합하는 것을 꺼려왔으며, 상용화에 실패하였다.
- 기존 연구들은 메모리 계층 구조를 통한 데이터 이동 에너지를 절감할 수 있는 인메모리 컴퓨팅의 잠재력을 보여주었으나, **수정되지 않은(unmodified) 상용 DRAM에서 인메모리 컴퓨팅을 구현한 사례는 없었다**.
- Moore의 Law 둔화/종료 가능성과 함께, 전통적인 실리콘 CMOS 로직 게이트를 대체할 수 있는 인메모리 컴퓨팅의 필요성이 대두되고 있다.

## 방법론

### 3.1. DRAM 시스템 조직 및 기본 동작 (Figure 1)

- **DRAM 계층 구조:** Channel → Rank → Bank → Sub-array → Row/Column
  - 각 Rank는 8개의 물리 칩으로 구성, 병렬 접근
  - 각 칩은 8개의 독립 Bank로 구성
  - 각 Bank는 수만 개의 행(row)으로 구성, sub-array 단위(보통 512행)로 분할
- **기본 DRAM 명령어:**
  - **PRECHARGE:** 모든 비트라인을 Vdd/2로 초기화하고 현재 열린 행을 닫음
  - **ACTIVATE:** 특정 행의 워드라인을 높여 비트라인과 셀 간 전하 공유 발생
  - **READ:** 열린 행의 데이터를 비트라인에서 읽음
  - **WRITE:** 비트라인의 값을 셀에 기록
- **타이밍 위반 활용:** 표준 DRAM 사양에서는 한 번에 하나의 행만 활성화 가능하나, ACTIVATE 명령을 충분히 빠르게 연속 발행하면 **여러 행이 동시에 열린 상태**가 됨

### 3.2. 비트라인 전하 공유 기반 연산 (Figure 2, 3)

- **전하 공유 원리:**
  - 비트라인의 커패시턴스(C_bitline)가 셀 커패시턴스(C_cell)보다 훨씬 큼
  - 두 행(R1, R2)을 동시에 활성화하면, 비트라인의 전압은 Vdd/2에서 셀 값에 따라 변동
  - R1=1, R2=0인 경우 비트라인 전압 상승 (AND 연산 동작)
  - R1=0, R2=1인 경우 비트라인 전압 하락 (OR 연산 동작)

### 3.3. 기본 연산 구현

- **Row Copy (행 복사):**
  - 소스 행과 대상 행을 동시에 활성화하여 비트라인에서 전하 공유
  - 소스 행의 값이 대상 행의 비트라인에 복사됨
  - **DRM 저항성:** 하드웨어 수정 불필요, 상용 DRAM에서 동작 확인
- **Logical OR:**
  - 두 입력 행을 동시에 활성화
  - 비트라인 전압이 Vdd/2 이상이면 1, 미만이면 0으로 판정
  - **DRM 저항성:** 주요 DRAM 벤더(Samsung, SK Hynix, Micron) 모듈에서 동작 확인
- **Logical AND:**
  - OR 연산과 유사한 회로 동작, 비트라인 전압 판정 기준 변경
  - 입력과 그 논리적 부정(negation)을 모두 저장하여 AND 연산 구현
  - **DRM 저항성:** 특정 벤더 모듈에서 안정적 동작 확인

### 3.4. 임의의 함수 계산을 위한 아키텍처

- **비트 직렬(bit-serial) 방식:** 각 비트를 순차적으로 처리하여 임의의 논리 함수 계산 가능
- **논리적 부정(negation) 활용:** AND, OR, COPY만으로 임의의 Boolean 함수를 구성하는 기법 제시
  - 모든 입력 값과 그 논리적 부정을 비트맵으로 저장
  - AND/OR 연산의 조합으로 임의의 논리 함수 구현 가능
- **대규모 병렬 처리:** 비트 단위 병렬 연산으로 데이터 병렬 애플리케이션에 적합
- **응용 분야:** 이미지/신호 처리, 컴퓨터 비전, 신경망 추론 등

## 핵심 기여

- ComputeDRAM은 **최초로 수정되지 않은 상용 DRAM에서 인메모리 컴퓨팅을 구현**한 연구로, DRAM 제조사의 하드웨어 변경 없이도 인메모리 연산이 가능함을 증명
- **핵심 기여:**
  1. 수정되지 않은 상용 DRAM에서의 row copy, logical AND, logical OR 최초 구현
  2. 주요 DRAM 벤더 DDR3 모듈에서의 연산 저항성 특성 분석
  3. 공급 전압/온도 변화에 대한 연산 안정성 측정
  4. 임의 함수 계산을 위한 비트 직렬 연산 기법 제시
  5. 실제 시스템에서 구동되는 소프트웨어 프레임워크 구현
- **산업적 의의:** DRAM 제조사가 거의 비용 없이 인메모리 컴퓨팅을 지원할 수 있음을 입증. 향후 모든 컴퓨터 시스템에 인메모리 컴퓨팅을 통합할 수 있는 경제적 실현 가능성 제시
- **Moore의 Law 대응:** 실리콘 CMOS 로직 트랜지스터 스케일링 둔화 시 인메모리 컴퓨팅이 대안으로 부상할 수 있음을 시사

## 주요 결과

- **하드웨어 플랫폼:** FPGA 기반 커스텀 DRAM 컨트롤러 + 상용 DDR3 DIMM 모듈
- **DRAM 컨트롤러:** 타이밍을 의도적으로 조정하여 여러 행 동시 활성화 가능
- **소프트웨어 프레임워크:** 대규모 병렬 비트 직렬 컴퓨팅을 실행하는 소프트웨어 프레임워크 구현
- **실제 시스템에서의 검증:** FPGA 프로토타입을 사용하여 실제 상용 DRAM 모듈에서 연산 검증
- **벤더별 특성 분석:** Samsung, SK Hynix, Micron 등 주요 DRAM 벤더의 DDR3 모듈에서 각 연산의 저항성(robustness) 측정

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2019MICRO-summarize/computedram-in-memory-compute-using-off-the-shelf-drams.md|전체 요약 보기]]
