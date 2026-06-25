---
tags: [paper, 2022, 2022HPCA, topic/dram, topic/rowhammer, topic/virtual-memory]
venue: "IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2022"
year: 2022
summary_path: "../paper-summaries/2022HPCA-summarize/mithril-cooperative-row-hammer-protection-on-commodity-dram-leveraging-managed-refresh.md"
---

# Mithril: Cooperative Row Hammer Protection on Commodity DRAM Leveraging Managed Refresh

**Venue:** IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2022
**저자:** Michael Jaemin Kim (Seoul National University), Jaehyun Park (Seoul National University), Yeonhong Park (Seoul National University), Wanju Doh (Seoul National University), Namhoon Kim (Seoul National University), Tae Jun Ham (Seoul National University), Jae W. Lee (Seoul National University), Jung Ho Ahn (Seoul National University)

## 개요

- Row Hammer (RH) 현상은 DRAM에서 반복적인 활성화(Activation)로 인해 인접 행의 데이터가 손상되는 보안 취약점으로, 2010년대 중반 이후 지속적으로 연구community의 주목을 받아옴
- 기존 RH 보호 기법은 크게 두 가지로 분류됨:
  - **메모리 컨트롤러(MC) 기반**: CBT, Graphene, BlockHammer 등 — DRAM 뱅크 수와 RH 임계값에 대해 보수적으로 설계되어 비용이 기하급수적으로 증가
  - **DRAM 기반**: TWiCe 등 — RH 보호 조치를 위한 시간 마진이 제한적이거나 표준 DRAM 인터페이스의 광범위한 수정이 필요
- DDR5/LPDDR5 표준에 새로 도입된 **Refresh Management (RFM)** 명령이 RH 보호의 새로운 가능성을 열었으나, RFM 기반 RH 보호 기법의 실제 적용 가능성과 효과가 공개적으로 검증되지 않음
- 기존 결정론적(Deterministic) 보호 기법은 RFM 인터페이스와 직접 호환되지 않음 — RFM의 주기적 특성 때문에 단기적으로 많은 행이 보수적 리프레시를 필요로 하는 최악의 시나리오에 취약
- **Table I**에서 기존 기법들의 분류를 확인할 수 있음: PARA(확률적, ARR, MC), CBT(결정론적, ARR, MC), TWiCe(결정론적, ARR, DRAM), Graphene(결정론적, ARR, MC), BlockHammer(결정론적, Throttling, MC), Mithril(결정론적, RFM, DRAM)

## 방법론

### 3.1. RFM 인터페이스와 과제

- RFM 명령은 MC가 특정 활성화 주기마다 DRAM에 전송하고, DRAM이 주어진 시간 윈도우 내에서 적절한 RH 보호 조치를 수행
- MC와 DRAM 간의 임무 분담: MC는 RFM 명령 생성, DRAM은 RH 보호 조치 실행
- **핵심 과제**: RFM의 주기적 특성으로 인해 많은 행이 동시에 예방적 리프레시를 필요로 하는 상황 방지
- 기존 ARR 기반 기법(CBT, Graphene 등)은 사전 정의된 임계값에 도달하면 특정 행을 타겟으로 리프레시하지만, RFM 구간에서 행이 집중되면 대기 시간이 급증하여 보호 보장이 불가능

### 3.2. Greedy Selection 메커니즘

- RFM 명령이 도착할 때마다 **추정 활성화 수(Estimated Count)**가 가장 높은 행을 타겟으로 선택
- 선택된 행의 인접 victim 행들을 예방적 리프레시 수행
- 타겟 행의 추정 활성화 수를 테이블의 최소값으로 리셋
- **수학적 보장 (Theorem 1)**: 어떤 tREFW 구간에서든 단일 행의 추정 활성화 수 상승은 Nentry와 RFM TH의 함수인 상한 M 이하로 제한
  - `M = Σ(k=1 to Nentry) [RFM TH / (k + RFM TH)] × Nentry × [tREFW × (1 - tRFC/tREFI) / (tRC × RFM TH + tRFM) - 2]`
  - M < Flip_TH/2가 되도록 Nentry와 RFM TH를 설정하면 이중 공격(Double-sided Attack)으로부터 결정론적 보호 보장

### 3.3. Counter-based Summary (CbS) 추적 메커니즘

- 제한된 CAM(Content-Addressable Memory) 엔트리로 각 행의 활성화 수를 근사 추적
- 스트리밍 알고리즘의 일종으로, 데이터 스트림에서 요소별 발생 빈도를 근사 계산
- 기존 Graphene과 동일한 CbS 알고리즘을 기반으로 하되, Mithril은 다음 최적화 적용:
  - **래핑 카운터(Wrapping Counter)**: 테이블 리셋 불필요 — 최대값이 M으로 제한되므로 기존 대비 **2배 메모리 절감**
  - **카운터 비트폭 최소화**: 최대값이 M으로 제한되어 Graphene 대비 더 적은 비트폭으로 엔트리 표현
- Table IV에서 per-bank 테이블 크기 비교: Mithril은 Flip_TH=6.25K에서 **0.68~1.45 KB/bank** (RFM TH에 따라)

### 3.4. Adaptive Refresh (Mithril+)

- 일반 워크로드에서 불필요한 RFM 명령으로 인한 성능/에너지 오버헤드를 줄이기 위한 확장
- **MaxP_tr와 MinP_tr 차이**를 이용하여 일반 워크로드와 RH 공격 패턴을 구별
  - 차이가 클수록 소수의 행에 대한 집중적 접근(RH 공격 패턴) 가능성 높음
  - 차이가 작으면 대규모 객체 순회 등 일반적인 워크로드 패턴
- **적응형 임계값(AdTH)**: 차이가 AdTH를 초과할 때만 예방적 리프레시 수행
- Benign 워크로드에서 추가 에너지 오버헤드를 거의 완전히 제거 (Figure 7)
- AdTH는 100~200 범위에서 모든 실험에서 효과적으로 작동

### 3.5. 하드웨어 구현 (Figure 4)

- 각 DRAM 칩의 모든 뱅크마다 동일한 Mithril 모듈을 구성
- **구성요소**: Logic + CAM 구조
- 명령 흐름: ① RFM 명령 수신 → ② Mithril 테이블에서 최대 추정 활성화 수 행 선택 → ③ 예방적 리프레시 수행
- TSMC 40nm 표준 셀 라이브러리로 합성 후 DRAM 20nm로 스케일링, 다시 10× 스케일링하여 보수적 면적 추정
- Flip_TH=6.25K에서 면적 오버헤드: **0.024 mm²** — DDR5 칩 1개의 약 **1%**

## 핵심 기여

- **핵심 기여**: RFM 인터페이스와 호환되는 최초의 결정론적 RH 보호 기법 Mithril을 제안하고, 수학적 보장을 통해 보호 보장 성능을 입증
- **성능**: 일반 워크로드에서 2% 미만의 성능 오버헤드, Flip_TH=6.25K에서 0.5% 미만
- **면적 효율**: per-bank 0.68~1.45 KB로 기존 MC 기반 기법(CBT, BlockHammer)보다 낮은 면적 오버헤드
- **실용성**: DDR5/LPDDR5 표준의 RFM 명령을 활용하여 상용 DRAM에 실장 가능한 현실적解决方案
- **의의**: MC-DRAM 협력적 구조를 통해 각 구현 위치의 한계를 극복하고, 확률적 기법 대비 결정론적 보호를 제공하여 DRAM 보안 분야에 기여

## 주요 결과

- **하드웨어**: Verilog RTL 구현, TSMC 40nm 표준 셀 라이브러리 합성 (Synopsys Design Compiler)
- **시뮬레이터**: McSimA+ 기반 성능 평가
- **설정 (Table III)**:
  - 16코어, 3.6 GHz 4-way OOO 코어
  - LLC: 16 MB
  - DDR5-4800, 2채널, 1랭크, 뱅크당 32개
  - tRFC=295ns, tRC=48.64ns, tRFM=97.28ns
  - 스케줄러: BLISS, 페이지 정책: Minimalist-open
- **웨이크로드**: SPEC CPU2017 (100M 명령 트레이스), 다중 스레드 벤치마크 (FFT, Barnes, Water-nsquared)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2022HPCA-summarize/mithril-cooperative-row-hammer-protection-on-commodity-dram-leveraging-managed-refresh.md|전체 요약 보기]]
