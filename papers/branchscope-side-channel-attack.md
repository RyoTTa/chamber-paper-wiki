---
tags: [paper, 2018, 2018ASPLOS, topic/security]
venue: "23rd International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '18)"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/branchscope-a-new-side-channel-attack-on-directional-branch-predictor.md"
---

# BranchScope: A New Side-Channel Attack on Directional Branch Predictor

**Venue:** 23rd International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '18)
**저자:** Dmitry Evtyushkin (College of William and Mary), Ryan Riley (Carnegie Mellon University in Qatar), Nael Abu-Ghazaleh (University of California Riverside), Dmitry Ponomarev (Binghamton University)

## 개요

- 현대 마이크로프로세서의 분기 예측 단위(BPU)는 분기 방향 예측(directional predictor)과 분기 목표 버퍼(BTB)로 구성됨
- 기존 연구는 BTB를 대상으로 한 사이드 채널 공격에 집중 (Aciicmez+ 2007, Evtyushkin+ 2016, Lee+ 2017), 그러나 분기 방향 예측기에 대한 공격은 미exploited 상태
- BTB 기반 공격에 대한 방어가 적용되면 분기 예측기가 여전히 취약한지 불분명
- BPU는 프로세서 코어 간 가상 코어 수준에서 공유됨 → 다른 프로세스의 분기 상태를 조작하여 사이드 채널 생성 가능
- 분기 예측기의 취약점은 암호화 키 비트, ASLR 우회, SGX enclave 내부 제어 흐름 추론 등 민감한 정보 유출에 활용 가능
- BranchScope는 분기 방향 예측기를 대상으로 한 **최초의 세밀한 공격**으로, BTB 공격과 구별되는 새로운 공격 벡터를 제시

## 방법론

### 3.1. 예측기 선택 로직 이해

- 현대 하이브리드 예측기는 1-level bimodal 예측기와 gshare 스타일 2-level 예측기의 조합
- 셀렉터 테이블이 어떤 예측기를 선택할지 결정 → 새로운 분기는 1-level 예측기를 사용하는 경향
- 실험 결과: 분기 패턴을 5-7회 반복하면 2-level 예측기가 학습하여 1-level 예측기 대체 (Figure 2)
- **핵심 관찰**: 새로운 분기는 1-level 예측기를 사용하므로, 분기 주소 기반으로 PHT 충돌을 쉽게 생성 가능

### 3.2. 1-level 예측기 강제 사용

**공격자 코드:**
- 피해자 분기와 동일한 가상 주소에 분기를 배치하여 PHT 충돌 생성
- 순환적(randomized) 분기 코드 블록을 실행하여 2-level 예측기의 학습 능력 교란

**피해자 코드:**
- 공격자가 제어할 수 없으므로, 랜덤화 코드를 사용하여 BPU를 1-level 예측기 사용 상태로 유도
- 100,000개의 분기 명령어를 실행하면 대부분의 PHT 엔트리 상태를 무작위화
- 분기 주소의 메모리 위치를 NOP 삽입으로 랜덤화하여 PHT 인덱싱 함수의 효과 최대화

### 3.3. PHT 상태 추론 및 분기 방향 복구

- 2비트 FSM의 4가지 상태: ST(strongly taken), WT(weakly taken), WN(weakly not-taken), SN(strongly not-taken)
- **Prime → Target → Probe 3단계 공격:**
  1. **Prime**: PHT 엔트리를 특정 강한 상태(ST 또는 SN)로 설정
  2. **Target**: 피해자의 분기를 실행하여 PHT 상태 변경
  3. **Probe**: 두 개의 사전 정의된 분기(taken/not-taken)를 실행하고 예측 정확도 관찰

- **FSM 전이 테이블 (Table 1):**
  - Prime 상태가 ST이고 피해자 분기가 taken이면 → Probe에서 HH 패턴
  - Prime 상태가 ST이고 피해자 분기가 not-taken이면 → Probe에서 MH 패턴
  - 두 패턴의 차이를 통해 피해자 분기 방향 결정

### 3.4. 타임스탬프 카운터를 사용한 측정

- 하드웨어 성능 카운터에 접근할 수 없는 경우, rdtscp 명령어를 사용한 타이밍 측정으로 분기 예측 이벤트 감지
- 두 번째 분기 실행의 레이턴시 측정만으로도 충분한 정확도 달성
- 측정 횟수를 10회로 늘리면 오차율이 거의 0%로 감소 (Figure 8)

## 핵심 기여

- BranchScope는 분기 방향 예측기에 대한 **최초의 세밀한 사이드 채널 공격**으로, BTB 공격 방어가 적용된 시스템에서도 여전히 취약함을 입증
- Skylake/Haswell에서 **오차율 1% 미만**으로 높은 정확도 달성
- SGX enclave에서도 공격 가능하며, 일반 시스템보다 더 낮은 오차율
- 분기 예측기의 보안 설계가 필수적임을 강조 — PHT 랜덤화, BPU 파티셔닝 등의 하드웨어 방어 필요

## 주요 결과

- **구현 언어:** C (공격자/피해자 프로그램)
- **측정 도구:** 하드웨어 성능 카운터(perf_event) 또는 rdtscp 타이밍 측정
- **사전 처리:** 공격자가 한 번 생성한 랜덤화 코드 블록은 공격 전 준비 단계에서 미리 생성
- **PHT 엔트리 매핑:** 연속된 가상 주소 범위에 분기를 배치하여 PHT 인덱싱 함수 역공학 (Figure 5)

## 한계점

- 고해상도 공격을 위해 피해자 프로세스를 느리게 해야 함 (스케줄링 제어 필요)
- 랜덤화 코드 블록이 크래시 시 PHT 상태를 초기화할 수 있음
- Meltdown/Spectre와 같은 추측 실행 공격과의 결합 가능성은 미래 연구 주제

## 관련 개념

- [[paper-wiki/concepts/security.md|Security]]


## 전체 요약

[[../paper-summaries/2018ASPLOS-summarize/branchscope-a-new-side-channel-attack-on-directional-branch-predictor.md|전체 요약 보기]]
