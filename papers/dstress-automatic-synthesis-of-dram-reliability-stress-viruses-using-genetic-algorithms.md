---
tags: [paper, 2020, 2020MICRO, topic/cache, topic/dram]
venue: "53rd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '20)"
year: 2020
summary_path: "../paper-summaries/2020MICRO-summarize/dstress-automatic-synthesis-of-dram-reliability-stress-viruses-using-genetic-algorithms.md"
---

# DStress: Automatic Synthesis of DRAM Reliability Stress Viruses using Genetic Algorithms

**Venue:** 53rd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '20)
**저자:** Lev Mukhanov (Queen's University Belfast), Dimitrios S. Nikolopoulos (Virginia Tech), Georgios Karakonstantis (Queen's University Belfast)

## 개요

- 클라우드/엣지 데이터센터에서 DRAM 밀도 증가가 필수적이지만, 셀 크기 축소로 인한 DRAM 고장은 불가피
- 기존 DRAM 테스트 방법(MARCH, MATS)은 워드 간(inter-word) 결함에 최적화되어 있어 워드 내(intra-word) 결함이나 인접 셀 간 간섭 패턴의 효과적인 탐지가 불가
- 물리적 메모리 셀 레이아웃(스캠블링, 로우 리맵핑 포함)은 벤더가 공개하지 않아, 셀 간 간섭 효과를 유발하는 데이터 패턴을 사전에 분석하는 것이 매우 어려움
- 기존 마이크로벤치마크(all1s, all0s, checkerboard, walking0s, walking1s, random)는 실제 최악의 DRAM 오류 동작을 유발하지 못함 — 실제 오류 셀의 상당수를 탐지하지 못할 위험
- 서버 등급 DRAM의 에너지 소비 증가: 보수적 운영 마진(TREFP=64ms, VDD=1.5V) 사용으로 DRAM 에너지 효율성 크게 저하
- DIMM 간 오류 변동: 동일 벤치마크(kmeans, memcached)라 해도 DIMM2/rank0와 DIMM3/rank0에서 단일 비트 오류 수가 최대 1000배 차이 (Figure 1b)
- 데이터 패턴에 따라 동일 애플리케이션의 최대 CE 수가 최대 8배까지 변동 가능

## 방법론

### 3.1. 패턴 프로그래밍 (Pattern Programming)

- C 언어 기반 프로그래밍 템플릿으로 4개 섹션 정의:
  - **parameters:** GA가 탐색할 변수 타입 및 범위 선언 (`$$$VAR1$$$ [DB3,UB3]`, `$$$ARRAY1_VEC$$$ [N1][DB1,UB1]`)
  - **global_data:** 힙에 할당되는 배열(var1, var2) 선언
  - **local_data:** 일반 C 타입 변수 선언
  - **body:** 실제 실행될 C 프로그램 코드
- 템플릿 예시(Figure 3): 데이터 패턴을 var1에서 로드하고, 접근 패턴을 var2 순서대로 접근하는 구조
- 변수 타입:
  - 스칼라 변수: `$$$VAR$$$ [lower_bound, upper_bound]`
  - 벡터 변수: `$$$ARRAY_VEC$$$ [size][lower_bound, upper_bound]`

### 3.2. 데이터 및 메모리 접근 패턴

**데이터 패턴(Data Patterns):**

- **64비트 패턴:** 64비트 워드 하나로 구성된 이진 배열, 탐색 공간 2^64
- **24KB 패턴:** 인접 3개 로우의 데이터 패턴 (각 8KB × 3행 = 24KB), 셀 간 간섭 효과 조사
  - BankX/Row1 (인접 상위 로우), BankX/Row2 (오류 발생 로우), BankX/Row3 (인접 하위 로우)
- **512KB 패턴:** 여러 뱅크의 인접 로우까지 확장한 패턴, 은행 간 간섭 효과 조사

**접근 패턴(Access Patterns):**

- **로우 접근 패턴:** 오류 발생 로우 주변 64개 로우(상위 32개 + 하위 32개)에 대한 이진 배열(접근: 1, 미접근: 0)
- **요소 접근 패턴:** 16개 인접 로우의 특정 요소를 반복 접근, 수식 `a_i × x + b_i` (x: 0~65536, a_i, b_i: 0~20)

### 3.3. 유전 알고리즘(GA) 검색 엔진

- **염색체(Chromosome):** 하나의 데이터/접근 패턴을 인코딩하는 벡터
- **적합도 함수(Fitness Function):** ECC에 의해 감지된 CE(Correctable Errors) 또는 UE(Uncorrectable Errors)의 수 최대화
- **돌연변이(Mutation):** 염색체의 일부를 확률적으로 변경하여 탐색 공간 확장
- **교차(Crossover):** 두 부모 염색체를 확률적으로 결합하여 자손 생성
- **수렴 기준:** Sokal & Michener 유사도 함수(SMF) 사용, 임계값 0.85 초과 시 중단
  - 이진 벡터: `SMF = (a+d) / (a+b+c+d)` (OTU 기반 2×2 contingency table)
  - 실수 벡터: 가중 자카드 유사도 `JW(X,Y) = Σmin(xi,yi) / Σmax(xi,yi)`
- 최적 GA 파라미터: 돌연변이 확률 0.5, 교차 확률 0.9, 집단 크기 40
- 각 GA 검색 실행 시 최대 2주 제한

### 3.4. 처리 및 합성 단계

- **처리 단계(Processing Phase):** 템플릿의 어휘적, 구문적, 의미적 분석을 통해 GA 탐색 변수 추출
- **합성 단계(Synthesis Phase):** GA 기반 프로그램(바이러스) 자동 생성
- **평가 단계(Evaluation Phase):** 생성된 바이러스를 실제 서버에서 컴파일/실행하고 ECC를 통해 오류 수 측정, 결과를 데이터베이스에 기록

## 핵심 기여

- **핵심 Contribution:**
  - DRAM 내부 설계 정보 없이 최악의 데이터/접근 패턴을 자동 합성하는 DStress 프레임워크 최초 제시
  - '1100' 반복 서브패턴이 DRAM 오류 확률을 증가시킨다는 것을 처음으로 보고
  - 기존 마이크로벤치마크 대비 45% 이상 더 많은 오류를 유발하는 패턴 발견
  - 최악 패턴 발견 확률 0.95 이상 달성
- **성능 향상:**
  - DRAM 에너지 17.7% 절감 (TREFP 마진 활용)
  - 시스템 전체 에너지 8.6% 절감
  - 기존 테스트 대비 45%+ 오류 탐지율 향상
- **응용 분야:**
  - DRAM 신뢰성 테스트 개선
  - 하드웨어 예측 유지보수(data center에서 DRAM 고장 예측)
  - Rowhammer 공격 시나리오 탐색
  - 워크로드 인식 DRAM 오류 동작 이해

## 주요 결과

- **프로그래밍 언어:** C (템플릿 기반 코드 생성), Python (GA 검색 엔진)
- **실행 플랫폼:** AppliedMicro/Ampere X-Gene 2 ARMv8 SoC 서버
- **하드웨어 구성:**
  - 4개 MCU(Memory Controller Unit) → 2개 MCB(Memory Controller Bridge)로 그룹화
  - 4개 DDR3 8GB DIMM (MCU당 1개, 총 72개 DRAM 칩)
  - 하드웨어 인터리빙 비활성화로 특정 DIMM에 데이터 할당 가능
- **온도 제어 시스템:**
  - 라즈베리파이 3 기반 제어 보드
  - 4개 폐쇄 루프 PID 컨트롤러
  - 8개 솔리드 스테이트 릴레이로 각 DIMM/rank별 독립 온도 제어
  - 가열 소자 및 커스텀 어댑터 사용
- **DRAM 운영 파라미터:**
  - TREFP: 최대 2.283초 (기본 64ms의 35배)
  - VDD: 1.425V~1.428V (기본 1.5V에서 5% 감소, 벤더 지정 최소 전압)
  - 온도: 50°C~70°C 범위

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2020MICRO-summarize/dstress-automatic-synthesis-of-dram-reliability-stress-viruses-using-genetic-algorithms.md|전체 요약 보기]]
