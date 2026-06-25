---
tags: [paper, 2022, 2022MICRO, topic/dram, topic/pim, topic/storage]
venue: "MICRO 2022 (55th IEEE/ACM International Symposium on Microarchitecture)"
year: 2022
summary_path: "../paper-summaries/2022MICRO-summarize/coruscant-fast-efficient-processing-in-racetrack-memories.md"
---

# CORUSCANT: Fast Efficient Processing-in-Racetrack Memories

**Venue:** MICRO 2022 (55th IEEE/ACM International Symposium on Microarchitecture)
**저자:** Sebastien Ollivier, Stephen Longofono, Prayash Dutta, Jingtong Hu, Sanjukta Bhanja, Alex K. Jones (University of Pittsburgh / University of South Florida)

## 개요

- 현대 애플리케이션의 데이터 수요 급증으로 인해 프로세서-메모리 간 데이터 이동 병목이 심각한 **memory wall** 문제 발생
- Intel Xeon X5670에서 32비트 워드 2개를 더하는 것보다 메모리에서 프로세서로 바이트 1개를 전송하는 데 **11배 더 많은 에너지** 소모 (Fig. 1 reference)
- 기존 DRAM PIM(Ambit, ELP2IM)은 **2피연산자 제한**: 멀티 피연산자 bulk-bitwise 연산 지원 불가
- PCM/ReRAM은 **내구성 문제** (PCM: ~10^8회 쓰기, 최대 29.7pJ/bit 쓰기 에너지), STT-MRAM은 **밀도 부족** (28-32F²)으로 메인 메모리 레벨 배치 불가
- DWM(Domain-Wall Memory)은 1-4F² 셀 밀도, ~0.1pJ 쓰기 에너지, ~1ns 접근 지연 시간으로 유망하나, 기존 DWM PIM(DW-NN, SPIM)은 **bitwise serial** 처리로 병렬성이 제한적

## 방법론

### 3.1. 메모리 아키텍처 (DWM Bank/Subarray/DBC)

- 기존 DRAM과 동일한 I/O 인터페이스를 유지하는 **DWM 메인 메모리** 아키텍처 (Fig. 2a)
- **Domain Block Cluster(DBC):** 각 나노와이어에 대해 Y개의 데이터 도메인과 X개의 병렬 접근 가능 비트로 구성 (Fig. 2d)
  - 일반적인 512×512 타일에서 X=512, Y=32 (보수적)
  - 2개의 Access Point(AP) 사용: 하나는 일반 읽기, TRD(Transverse Read Distance) 간격으로 배치하여 TR 가능
  - TRD=7을 가정 (최신 연구 [40]에서 검증), TRD ∈ {3, 5, 7}에 대한 민감도 분석 수행

### 3.2. TR 기반 다형 게이트 (Polymorphic Gate, Fig. 4, 5)

**수정된 센스 앰플리파이어 (7-트랜지스터 SA):**
- 각 SA_i가 7단계 출력 비트를 생성: SA_i[j] = '1' if ≥j개의 '1'이 TR 범위 내에 존재
- PIM 유닛(Fig. 4b)에서 멀티 피연산자 논리 연산 직접 구현

**지원 연산:**
| 연산 | TR 기반 구현 |
|------|-------------|
| OR | TR level ≥ 1 → '1' |
| AND | 최고 TR level → '1' |
| XOR | 홀수 TR level에서만 '1' (NAND/NAND 구현) |
| C (carry) | TR level > 2 AND ≤ 4 OR > 6 |
| C' (super carry) | TR level > 4 |
| S (sum) | XOR와 동일 |

**동작 예시 (Fig. 5):**
- 나노와이어의 두 AP 사이 영역에서 TR을 수행하면 **7개 피연산자의 bulk-bitwise 연산을 단일 단계**에서 병렬 처리
- 사용하지 않는 위치는 영(0) 또는 영(1)로 패딩하여 2~6 피연산자 연산 지원

### 3.3. 멀티 피연산자 덧셈 (Multi-operand Addition, Fig. 6)

**알고리즘 (5-피연산자 덧셈 예시):**
1. **Step 1:** dwm_0의 TR 수행 → a₀...e₀의 XOR = S₀ 계산
2. **동시에:** carry C₀(→ dwm_1 port R), super carry C'₀(→ dwm_2 port L) 계산
3. **Step 2:** dwm_1에서 TR 수행 (C₀ + a₁...e₁ 포함)
4. **Step 3 이후:** dwm_k에서 C'_{k-2}, a_k...e_k, C_{k-1}의 7개 요소에 대해 TR 수행
5. 모든 nanowire에 대해 S, C, C'을 병렬로 계산하고 쓰기 → **O(n) 복잡도** (n: 비트 폭)

**패딩 전략 (Fig. 7):**
- AND/NAND: 위치 a, b에 피연산자 배치, c~f에 '1' 사전 로드
- OR/NOR/XOR/ADD: '0' 사전 로드

### 3.4. 곱셈 구현 (Multiplication)

**상수 곱셈 (Constant Multiplication):**
- Booth 인코딩 활용: 상수를 P(1), N(-1), 0으로 표현
- 예: 20061 = "100111001011101" → P0P00N0P0N00N0P
- **2단계 덧셈**으로 20061×A 계산 가능
  - Step 1: A<<9 + A<<1 + A → 515A
  - Step 2: 515A<<5 - 515A + A<<12 → 20061A

**임의 곱셈 (Arbitrary Multiplication):**
- 곱셈기의 '1' 비트 위치에 해당하는 시프트된 복사본을 부분곱으로 합산
- 최악의 경우 O(n²) 복잡도

**최적화 곱셈 (Optimized Multiplication):**
- **7→3 피연산자 축소** (CSA 영감): 7개 피연산자를 S, C, C'의 3개로 병렬 축소
- 축소 반복 후 ≤(TRD-2)개 피연산자가 남으면 단일 덧셈으로 최종 결과 계산
- **곱셈이 O(n) 복잡도**로 개선

### 3.5. Transverse Write(TW) 및 세그먼트 시프팅 (Fig. 9)

- **TW:** 두 Write/Read 헤드 사이 세그먼트의 데이터를 단일 작업으로 쓰고 시프트
- Max 함수 구현 시 TW 사용 시 사이클 **28.5% 감소**
- 세그먼트 시프팅으로 나노와이어 전체 시프팅 없이 로컬 업데이트 가능

### 3.6. ISA 지원 및 N-모듈리티 중복성

- **cpim dst, src, op, blocksize** 명령어로 메모리 컨트롤러에 PIM 작업 지시
- blocksize ∈ {8, 16, 32, 64, 128, 256, 512}: 64바이트 크기 숫자 64개의 패킹 덧셈에서 전체 512비트 덧셈 지원
- **N-modular redundancy(N={3,5,7}):** 동일 연산을 N회 수행 후 다수결 투표로 오류 정정
  - TMR(N=3): 동일 비트 위치에서 2개 이상의 오류 필요 시 uncorrectable error 발생
  - N=5: 3개 이상의 오류 필요, N=7: 4개 이상의 오류 필요

## 핵심 기여

1. **DWM의 TR을 활용한 다형 게이트로 멀티 피연산자 PIM 달성:** 최대 7개 피연산자의 bulk-bitwise 연산을 단일 단계에서 병렬 처리 가능
2. **기존 DWM PIM 대비 Significant 성능/에너지 향상:** SPIM 대비 add **6.9×** 속도, **5.5×** 에너지 절약; multiply **2.3×** 속도, **3.4×** 에너지 절약
3. **DRAM PIM 대비 멀티 피연산자 이점:** bulk-bitwise 연산에서 **1.6×** 속도 향상, 피연산자 수 증가 시 성능 유지
4. **CNN 가속에서 최대 14.4× 성능 향상:** ISAAC ReRAM 대비, SPIM 대비 **2.8×**, ELP2IM 대비 **5.1×**
5. **내장 신뢰성 지원:** N={3,5,7}-modular redundancy로 오류율 **5×10⁻¹²** 이하 달성하면서도 기존 무결성 PIM보다 빠름
6. **10% 면적 오버헤드**로 실용적인 PIM 활성화, TRD 조절로 오버헤드 <4%까지 축소 가능

**Broader significance:** CORUSCANT은 DWM의 물리적 특성(나노와이어 내 도메인 근접성)을 최대한 활용하여, memory wall 문제를 해결하는 새로운 PIM 패러다임을 제시한다. 연산 밀도가 높은 CNN, 데이터베이스 검색 등에서 실질적인 가속 효과를 제공하며, 향후 부동소수점 연산 및 온라인 학습 지원으로 확장 가능성을 열어둔다.

## 주요 결과

- **시뮬레이터:** RTSIM (cycle-accurate) 확장, DDR3-1600 표준
- **회로 합성:** FreePDK45 (45nm)로 PIM 로직 합성 후 32nm로 스케일링
- **센스 회로:** LTSPICE에서 커스텀 설계
- **에너지 계산:** NVSIM 수정 버전으로 DWM 에너지, ASIC 합성 결과로 PIM 로직 게이트 스케일링
- **시스템 구성 (Table II):**
  - 메모리: 1GB (8Gb), 32 banks, 64 subarrays/bank, 16 tiles/subarray
  - 프로세서: Intel Xeon X5670, DDR3-1600
  - DWM: tRAS-tRCD-tRP-tCAS-tWR = 9-4-S-4-4 cycles
  - add(32비트): 111 pJ/op, mult(32비트): 164 pJ/op
- **면적 오버헤드 (Table I):** PIM 활성화 1타일 기준 10% (full ISA: mult + add + bulk-bitwise)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2022MICRO-summarize/coruscant-fast-efficient-processing-in-racetrack-memories.md|전체 요약 보기]]
