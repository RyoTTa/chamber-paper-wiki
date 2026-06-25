---
tags: [paper, 2024, 2024ATC, topic/cache, topic/memory-tiering]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024ATC-summarize/atc24-xu-dong.md"
---

# FlexMem: Adaptive Page Profiling and Migration for Tiered Memory

**Venue:** 
**저자:** 

## 개요

- 메모리 비용과 소비 급증으로 데이터센터 TCO(Total Cost of Ownership) 절감이 과제
  - Microsoft Azure 서버 비용의 50%, Meta 서버 비용의 37%가 메모리 차지
  - 양자역학 시뮬레이션, 인메모리 데이터베이스, 그래프 분석, 대규모 AI 모델 추론/학습 등의 애플리케이션이 TB 규모 메모리 필요
- Tiered memory는 빠르고 작은 fast memory + 느리고 큰 slow memory 조합으로 비용 대비 효과적인 메모리 확장 솔루션
- 기존 시스템 소프트웨어의 세 가지 한계:
  1. **경직된 메모리 프로파일링**: 성능 카운터 기반은 시간 변화하는 접근 패턴에 둔감, fault 기반은 false positive 발생 → 정확도와 민감도의 trade-off 미해결
  2. **경직된 페이지 디모션**: 디모션양이 고정된 free memory 공간 요구사항에 의해 결정 → hot page 프로모션 실패 빈발
  3. **경직된 warm page 범위**: hot bin에서 단 하나 bin 차이나는 페이지를 warm으로 분류 → 불필요한 디모션 발생
- 기존 솔루션(TPP, MEMTIS, Tiering-0.8 등)의 구체적 한계:
  - MEMTIS: 프로파일링 시간 간격 100K 이벤트, 페이지 마이그레이션 500ms 간격으로 비동기 → 오래된 hot threshold 사용으로 지연
  - TPP: fault 기반 프로파일러가 즉시 프로모션 → 두 프로파일러 간 동기화 없음
  - Tiering-0.8: NUMA hint fault 기반, 256MB 샘플링 한정

## 핵심 아이디어

- **FlexMem**: 두 프로파일러(performance counter + fault-based)를 결합하여 적응형 프로파일링 구현
- **적응형 디모션**: 프로모션 실패 빈도와 효과에 따라 디모션양을 동적 결정
- **적응형 warm bin**: cold bin 중 최근 hot bin으로 프로모션된 비율에 따라 warm 범위를 동적 확장/축소
- 핵심 도전 과제:
  1. 두 프로파일러의 프로모션 타이밍 조정 및 hot page 판정 불일치 조율
  2. 디모션이 프로모션의 pace를 따라가지 못하는 문제 해결
  3. Warm page 분류의 비효율성 제거

## FlexMem 시스템

## 방법론

- **Performance Counter-based Profiler** (MEMTIS/MTM 기반 확장):
  - PEBS로 LLC load miss와 retired store instruction 샘플링
  - Exponential Moving Average (EMA)로 페이지별 접근수 누적: `EMA_i = k × x + (1-k) × EMA_{i-1}`
  - 16-bin 히스토그램 구성 (n-th bin: EMA 범위 [2^n, 2^{n+1}))
  - **새로운 설계 1**: hot page threshold 결정과 페이지 마이그레이션을 동기화
    - 기존: threshold 적응(100K 이벤트)과 마이그레이션(500ms)이 비동기
    - 개선: `kmigrated`가 깨어날 때마다 최신 histogram으로 threshold 갱신 → 최신 hot page 즉시 마이그레이션
  - **새로운 설계 2**: histogram에 페이지 주소 정보 포함
    - 기존: histogram은 페이지 수만 기록 → promotion list 별도 관리 필요
    - 개선: 각 bin에 slow/fast memory 페이지 주소 저장 → threshold 결정 즉시 마이그레이션 대상 파악, promotion list 오버헤드 제거

- **Fault-based Profiler**:
  - Linux active/inactive list (LRU 기반) 사용
  - 페이지 fault 발생 시 active list에 추가, 두 번 접근 시 즉시 프로모션
  - **변경**: 즉시 프로모션 제거 → active list에만 추가, `kmigrated`가 active list와 histogram을 동시에 확인하여 동일 기회 부여

- **두 프로파일러 간 조율**:
  - Fault 기반 profiler가 식별한 hot page는 countdown timer(초기값 5) 적용
  - Timer가 0에 도달하기 전 hot bin으로 이동하면 프로모션 유지, 0에 도달하면 디모션 (false positive 시정)
  - Fault 기반 profiler의 디모션 메커니즘 제거 (performance counter 기반에 의존)

### 3.2. 적응형 디모션 (Adaptive Demotion)

- 디모션양(DR) 공식: `DR = cold_pages + promo_fails_histo + α × promo_fails_pf`
  - `cold_pages`: fast memory 내 cold 페이지 수 (histogram의 cold bins에서 계산)
  - `promo_fails_histo`: histogram이 프로파일링한 hot page 중 프로모션 실패 수
  - `promo_fails_pf`: fault 기반 profiler가 식별한 promising hot page 중 프로모션 실패 수
  - `α ∈ [0,1]`: promising hot page의 최근 프로모션 효과 측정 변수

- **α 적응형 조정**:
  - 초기값 1 (최대 프로모션)
  - Countdown timer 만료 시까지 hot bin으로 이동하지 못한 promising hot page 수 추적
  - Mistaken promotion 많으면 α 감소 (과도한 프로모션 억제), 적으면 α 유지/증가

- **기존 대비 차이**: 고정 free memory 임계값(2%)이 아닌, 실시간 프로모션 실패 빈도에 따라 디모션양 결정

### 3.3. 적응형 Warm Bin

- 기존(MEMTIS 등): warm bin = hot threshold - 1 bin 고정
- **FlexMem**: hot threshold 결정 후 cold bin 방향으로 warm 범위 동적 확장
  - cold bin의 일정 비율 이상 페이지가 최근 hot bin으로 프로모션되면 해당 cold bin을 warm으로 격상
  - Warm bin으로 격상된 페이지는 fast memory 부족 시에만 디모션
- 동작 예시 (Figure 4 - Silo 벤치마크):
  - Beginning phase: bin 4~7이 warm/hot, bin 1~3이 cold
  - Middle phase: hot page 감소로 warm 범위 축소
  - End phase: hot page 증가로 warm 범위 확대

## 핵심 기여

- **핵심 기여**: Tiered memory의 세 가지 주요 한계(경직된 프로파일링, 디모션, warm page 범위)를 적응형으로 해결하는 FlexMem 시스템 제안
- **성능 향상**: Tiering-0.8 대비 평균 32%, TPP 대비 23%, MEMTIS 대비 27% 성능 개선
- **실용성**: Linux 커널 기반 구현, 프로파일링 오버헤드 ~2%로 기존과 동일, CXL 기반 tiered memory와 호환
- **응용**: CXL, Optane 등 최신 메모리 기술을 활용하는 tiered memory 시스템의 효율적 관리 방향 제시

## 주요 결과

### 방법론

| 항목 | 내용 |
|------|------|
| **테스트베드** | 2개의 64코어 AMD EPYC 7763 (2TB RAM), CXL extender로 tiered memory 시뮬레이션 |
| **모델/구성** | Fast memory: 32GB (DDR4), Slow memory: 1.5TB+ (DDR4 via CXL) |
| **벤치마크** | NASPB (bt, cg, ep, is, lu, mg, sp, ua), Graph500 (SSSP, BFS), Silo, MySQL, GAPBench (PageRank, BFS, SSSP) |
| **지표** | Execution time, 프로모션 실패율, fast memory 활용률, 페이지 마이그레이션 수 |
| **Baselines** | Tiering-0.8, TPP, MEMTIS |

### 주요 결과

- **전체 성능 향상** (Tiering-0.8 대비):
  - NASPB: 평균 32% 향상 (bt: +51%, ep: +36%, lu: +12%, sp: +44%)
  - Graph500 SSSP: +15%, BFS: +22%
  - Silo: +21%
  - MySQL: +19%
- **기존 솔루션 대비 성능**:
  - Tiering-0.8 대비 평균 32% 향상
  - TPP 대비 평균 23% 향상
  - MEMTIS 대비 평균 27% 향상
- **프로모션 실패율 감소**: 25% 감소
- **Fast memory 활용률 향상**: 21% 향상
- **페이지 마이그레이션 수**: Tiering-0.8 대비 감소 (불필요한 마이그레이션 억제)
- **적응형 디모션 효과**:
  - α 값이 높을 때 (hot page 정확히 식별) 프로모션 실패율 감소
  - α 값이 낮을 때 (false positive 많음) 불필요한 디모션 감소
- **적응형 warm bin 효과**: 고정 warm bin 대비 fast memory 활용률 향상, 디모션 횟수 감소

### Design Choices / Ablation Study

- **두 프로파일러 결합 효과**: 단일 프로파일러(performance counter 또는 fault-based) 대비 성능 향상
  - Performance counter 단독: 민감도 부족 (time-changing 패턴 대응 미흡)
  - Fault-based 단독: false positive로 불필요한 프로모션/디모션
- **적응형 디모션 vs 고정 디모션**: 적응형이 프로모션 실패율 25% 감소
- **적응형 warm bin vs 고정 warm bin**: 적응형이 fast memory 활용률 향상
- **Histogram 주소 정보 포함**: promotion list 제거로 오버헤드 감소, 마이그레이션 지연 감소
- **Countdown timer**: hot page의 ping-pong 효과 방지, fault 기반 profiler의 false positive 시정

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]


## 전체 요약

[[../paper-summaries/2024ATC-summarize/atc24-xu-dong.md|전체 요약 보기]]
