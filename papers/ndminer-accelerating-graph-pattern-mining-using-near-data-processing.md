---
tags: [paper, 2022, 2022ISCA, topic/dram, topic/near-data-processing]
venue: "ISCA 2022 (The 49th Annual International Symposium on Computer Architecture)"
year: 2022
summary_path: "../paper-summaries/2022ISCA-summarize/ndminer-accelerating-graph-pattern-mining-using-near-data-processing.md"
---

# NDMiner: Accelerating Graph Pattern Mining Using Near Data Processing

**Venue:** ISCA 2022 (The 49th Annual International Symposium on Computer Architecture)
**저자:** Nishil Talati, Haojie Ye, Yichen Yang, Leul Belayneh, Kuan-Yu Chen, David Blaauw, Trevor Mudge, Ronald Dreslinski (University of Michigan)

## 개요

- 그래프 패턴 마이닝(GPM)은 바이오인포매틱스, 사이버 보안, 소셜 네트워크 분석, 스팸 탐지 등 다양한 분야에서 사용되지만, 현대 하드웨어에서 심각한 성능 병목에 시달림
- GPM 워크로드의 병목 원인: **set intersection/difference 연산에 사용되는 데이터 의존적 분기(data-dependent branches)**와 **불규칙한 메모리 접근 패턴**으로 인한 제어 흐름 및 메모리 스타일
- 기존 접근 방식의 한계:
  - **도메인 특화 가속기(FlexMiner):**\application-specific 제어/데이터 경로를 제안하지만, 범용 메모리 서브시스템의 비효율적인 데이터 이동 문제 미해결
  - **SISA (Set-centric ISA):** improved intersection 알고리즘을 사용하지만, 범용 NDP 아키텍처(Ambit 등)에 GPM 연산을 매핑하여 도메인 특화 부족
- GPM 워크로드의 네 가지 새로운 비효율성 관찰:
  1. 비용이 큰 집합 연산의 입력이 서로 다른 메모리 뱅크에서 가져옴
  2. 대칭성 탐색(symmetry breaking)으로 인한 캐시 오염 및 DRAM 대역폭 낭비
  3. 희소 패턴 마이닝 알고리즘의 중복 메모리 읽기 및 연산
  4. DRAM 내부 데이터 병렬성 미활용

## 방법론

### 3.1. Load Elision Unit (하드웨어 대칭성 제거)

- **목적:** 대칭성 탐색(symmetry breaking)으로 인한 불필요한 메모리 로드를 하드웨어에서 탐지 및 종료
- **동작 원리:**
  - 대칭성 제약 조건을 하드웨어에서 검사 (예: $v \geq u$, $w \geq v$)
  - 만족 불가능한 조건을 즉시 탐지하여 해당 로드 작업 중단
  - Figure 1에 따르면 Load Elision Unit 적용 시 **7.7×** 성능 향상 (baseline 대비)

### 3.2. 컴파일러 최적화 (희소 GPM 효율성 개선)

- **목적:** 희소 패턴 마이닝에서의 중복 읽기 및 계산을 줄이기 위한 소프트웨어 최적화
- **기법:**
  - 루프 네스트를 복합 집합 연산(composite set operations)으로 평탄화(flattening)
  - 루프 불변 계산(loop invariant computations)을 루프 밖으로 호이스팅
  - NDP 하드웨어로의 매핑 지원
- Figure 1에 따르면 컴파일러 최적화 적용 시 **3.5×** 추가 성능 향상

### 3.3. 그래프 리매핑 및 집합 연산 재순서

- **그래프 리매핑(Graph Remapping):**
  - DRAM 내부에서 그래프 데이터를 재배치하여 bank, rank, channel 수준 병렬성 활용 가능
  - 새로운 그래프 데이터 레이아웃 제안
- **집합 연산 재순서(Set Operation Reordering):**
  - 새로운 vertex ID 기반 재순서 하드웨어 설계
  - 1024개 엔트리 윈도우의 집합 연산을 검사하고 재순서
  - 크기가 제한된 메모리 컨트롤러 큐에 요청을 삽입하기 위한 최적화
  - DRAM 내부 데이터 병렬성을 효과적으로 활용

### 3.4. 전체 시스템 구성

- **호스트 ISA 확장:** NDP 명령어를 추가하여 CPU에서 NDP 연산을 명시적으로 호출
- **컴파일러 변환:** GPM 소스 코드를 NDP 명령어를 사용하도록 변환
- **메모리 컨트롤러 확장:** in-DRAM 연산을 조율하기 위한 컨트롤러 설계 변경
- **DIMM 기반 구현:** 기존 DRAM DIMM의 버퍼 칩에 연산 유닛 통합

## 핵심 기여

1. **GPM 워크로드의 네 가지 새로운 비효율성 관찰:** set 연산의 서로 다른 뱅크 접근, 대칭성 탐색의 대역폭 낭비, 희소 패턴의 중복 연산, DRAM 병렬성 미활용
2. **Load Elision Unit으로 하드웨어 수준에서 대칭성 제거:** 불필요한 로드를 즉시 종료하여 7.7× 성능 향상
3. **컴파일러 최적화로 희소 GPM 효율성 개선:** 복합 집합 연산과 루프 호이스팅으로 3.5× 추가 향상
4. **그래프 리매핑 + 집합 연산 재순서로 DRAM 병렬성 최대 활용:** 최종 12.7× 성능 달성
5. **범용 하드웨어와의 통합:** FlexMiner 대비 2.5×, GraphPi 대비 6.4× 성능 while 면적 오버헤드 무시 가능

**Broader Significance:** NDMiner는 GPM 가속을 위한 도메인 특화 NDP 아키텍처로, 하드웨어-소프트웨어 공동 최적화를 통해 기존 소프트웨어 및 하드웨어 솔루션을 크게 능가하는 성능을 달성. 특히 기존 DRAM DIMM 인프라와의 호환성을 확보하여 실용적인 배포 가능성을 제시

## 주요 결과

- **구현 언어:** Verilog (하드웨어), C++ (소프트웨어)
- **시스템 구성요소:**
  - CPU: 범용 프로세서 (호스트)
  - NDP 유닛: 각 DRAM 채널당 1개의 set operation 유닛 (baseline)
  - Load Elision Unit: 하드웨어 대칭성 제거 유닛
  - 그래프 리매핑 및 재순서 하드웨어
- **평가 그래프 데이터셋:** 5개 실세계 그래프 사용
- **GPM 알고리즘:** cliques, 사용자 정의 서브그래프, motifs를 마이닝하는 7개 알고리즘

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]


## 전체 요약

[[../paper-summaries/2022ISCA-summarize/ndminer-accelerating-graph-pattern-mining-using-near-data-processing.md|전체 요약 보기]]
