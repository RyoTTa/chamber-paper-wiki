---
tags: [paper, 2020, 2020HPCA, topic/dram, topic/pim]
venue: "2020 IEEE International Symposium on High Performance Computer Architecture (HPCA '20)"
year: 2020
summary_path: "../paper-summaries/2020HPCA-summarize/fulcrum-a-simplified-control-and-access-mechanism-toward-flexible-and-practical-in-situ-accelerators.md"
---

# Fulcrum: a Simplified Control and Access Mechanism toward Flexible and Practical In-situ Accelerators

**Venue:** 2020 IEEE International Symposium on High Performance Computer Architecture (HPCA '20)
**저자:** Marzieh Lenjani (University of Virginia), Patricia Gonzalez (University of Virginia), Elaheh Sadredini (University of Virginia), Shuangchen Li (University of California, Santa Barbara), Yuan Xie (University of California, Santa Barbara), Ameen Akel (Micron Technology, Inc.), Sean Eilert (Micron Technology, Inc.), Mircea R. Stan (University of Virginia), Kevin Skadron (University of Virginia)

## 개요

- 메모리 집약적(memory-intensive) 애플리케이션에서 데이터 이동 비용이 전체 에너지 소비의 대부분을 차지 (45nm 기준 32-bit 단어 DRAM에서 읽기 비용이 ADD 연산 대비 6400배)
- 기존 인시츄(in-situ) PIM 접근법의 4가지 핵심 한계:
  1. **유연성 부족:** 모든 서브어레이에서 동일한 로우 와이드 비트 연산만 지원. 데이터 의존성이 있는 연산이나 조건부(predicate) 연산 지원 불가 (예: Sort, FilterByKey, FilterByPredicate, Sparse 연산)
  2. **가속기 용량 제한:** 서브어레이 수준에서 비트 연산 + 덧셈 + 곱셈이 가능한 PU는 서브어레이 대비 최소 52배 더 큰 면적 필요 → 비트 ALU만 사용 가능, 복잡한 연산은 다수의 비트 연산으로 에뮬레이션 필요
  3. **물리적 레이아웃 문제:** 32비트 워드의 각 4비트가 별도의 매트(mat)에 저장됨 (mat interleaving). 기존 인시츄 접근법은 1비트, 2비트, 4비트 값에 대해서만 연산 가능
  4. **주변 로직 비효율:** 서브어레이 간 값 공유 시 직렬화(serialization) 발생, 독립적 컬럼 선택 불가, 서브어레이 간 데이터 이동 비효율

## 방법론

### 3.1. 단순화된 제어 및 접근 메커니즘 (Walkers)

- **Walkers:** 로우 버퍼의 연속적인 워드에 대한 순차적 접근 제공
  - 각 Walker는 입력 피연산자(서브어레이에서 읽은 값) 또는 출력 결과(서브어레이에 기록할 값)를 저장
  - **One-hot 인코딩 기반 컬럼 선택:** 래치에 저장된 one-hot 값을 시프팅하여 다음 컬럼 선택
  - 전통적 코어의 제어/접근 오버헤드를 회피하면서 조건부 연산 지원 가능 (Figure 5)
- **장점:**
  - 순방향/역방향 읽기/쓰기 가능
  - 레이아웃 변경 없이 구현 가능 (shift register 대비 에너지 효율적)
  - 하나의 워드만 처리하므로 mat interleaving 문제 해결 가능

### 3.2. Narrow and Simple ALU (ALPU)

- **AddressLess Processing Unit (ALPU):** 컨트롤러, 3개의 임시 레지스터, ALU, 명령 버퍼로 구성 (Figure 4)
- 지원 연산: 정수 덧셈, 뺄셈, 곱셈 + 비트 연산 (단일 워드)
- 피연산자 소스: (i) Walker에서 순차 접근, (ii) 임시 레지스터, (iii) GDLs, (iv) ALU 출력 (순환 가능)
- 연산당 1/64 로우 버퍼만 처리하지만, 비트 연산 기반 에뮬레이션보다 우수한 성능

### 3.3. 효율적인 주변 로직 (Peripheral Logic)

- **브로드캐스팅:** 모든 처리 요소가 공유 버스의 데이터를 수신/캡처 가능
- **LISA (Low-cost Inter-linked SubArrays):** 서브어레이 간 전체 로우를 한 번에 전송 (기존 대비 큰 폭의 오버헤드 절감)
- **독립적 컬럼 선택:** 각 서브어레이에 one-hot 인코딩된 컬럼 주소를 래치에 저장 → 이전 연산 결과에 따라 시프팅 방향 결정
  - 기존 컬럼 디코더/컬럼 주소 버스 공유 문제 해결

### 3.4. 매트 인터리빙 문제 해결

- **해결책 1:** 매트 인터리빙 완전 제거 (애플리케이션이 임의 컬럼 접근이나 소프트 에러에 유연한 경우)
- **해결책 2:** 매트 인터리빙 유지 + Helper Flip-Flops(HFF)를 파이프라인으로 연결
  - 인접 매트의 LDL 세그먼트와 연결하여 서브어레이 측면으로 32비트 전달
  - 4클록 사이클로 32비트 전송 (segmented TSV 사용 시 TSV 지연 0.3ns로 최소화)

## 핵심 기여

- **핵심 기여:** 인시츄 PIM 가속기의 4가지 핵심 한계를 해결하는 새로운 제어 및 접근 메커니즘 제안
- **성능 향상:** GPU 대비 23.4x 성능, 96% 에너지 절감
- **유연성:** 정수/부동소수점 연산, 조건부 연산, 데이터 의존성 연산을 모두 지원하는 최초의 인시츄 가속기
- **실용성:** 22nm 공정에서 164MHz 동작, 10W 파워 예산으로도 GPU 대비 6x 성능
- **의의:** 로우 와이드 비트 연산이 아닌 단일 워드 ALU가 인시츄 컴퓨팅에서 더 효율적이라는 것을 입증. CXL 인터페이스와의 통합을 통해 실용적 배포 가능성 제시

## 주요 결과

- **구현 언어:** RTL 설계 + CACTI-3DD 에너지/면적 모델링
- **공정:** 22nm 기술, 199MHz (여유분 포함 164MHz로 평가)
- **하드웨어 구성:**
  - Fulcrum: 32 vault, 각 vault당 32 서브어레이, 4 매트/서브어레이, 256바이트/로우
  - 로직 레이어: 128KB SRAM 기반 FIFO, ARM Cortex-A35 코어
  - 인-로직 레이어: Walkers, ALPU, 컨트롤러, 명령 버퍼
- **소프트웨어:** 고수준 프로그래밍 모델 구상 (TensorFlow 유사, DFG → 프리미티브/커널 변환)
- **데이터 배치:**
  - 장기 거주 데이터: offload 패러다임 (CUDA 유사 API)
  - 임시 거주 데이터: (i) 브로드캐스팅 → 인-로직 레이버 버퍼에 저장, (ii) 비브로드캐스팅 → on-the-fly 레이아웃 최적화

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2020HPCA-summarize/fulcrum-a-simplified-control-and-access-mechanism-toward-flexible-and-practical-in-situ-accelerators.md|전체 요약 보기]]
