---
tags: [paper, 2018, 2018ASPLOS, topic/security, topic/cache, side-channel, branch-predictor, sgx]
venue: "ASPLOS '18"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/branchscope-a-new-side-channel-attack-on-directional-branch-predictor.md"
---

# BranchScope: A New Side-Channel Attack on Directional Branch Predictor

**Venue:** 23rd International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '18)
**저자:** Dmitry Evtyushkin, Ryan Riley, Nael Abu-Ghazaleh, Dmitry Ponomarev

## 개요

BranchScope는 분기 예측 장치(BPU)의 **방향 예측기(directional predictor)**를 대상으로 한 최초의 세밀한 사이드 채널 공격입니다. 기존 BTB(Branch Target Buffer) 기반 공격과 구별되는 새로운 공격 벡터를 제시하며, BTB 방어가 적용된 시스템에서도 여전히 취약함을 입증합니다.

**핵심 문제:** 현대 프로세서의 BPU는 물리 코어 수준에서 프로세스 간 공유됨. 분기 예측기의 방향 예측 컴포넌트(PHT)를 조작하여 피해자의 분기 방향(taken/not-taken)을 추론할 수 있음.

## 방법론

### 공격 3단계
1. **Prime**: PHT 엔트리를 공격자가 원하는 상태로 설정
2. **Target**: 피해자의 분기 실행 → PHT 상태 변경
3. **Probe**: 두 개의 사전 정의된 분기로 예측 정확도 관찰 → 피해자 분기 방향 결정

### 핵심 기법
- **1-level 예측기 강제 전환**: 복합 하이브리드 예측기를 단순 1-level 모드로 유도하여 PHT 충돌 생성 단순화
- **FSM 상태 추론**: 2비트 포화 카운터의 전이 특성(Table 1)을 이용한 정밀 분기 방향 복구
- **타임스탬프 측정**: rdtscp를 사용한 비권한 측정으로도 1% 미만 오차율

## 핵심 기여

1. **분기 방향 예측기에 대한 최초의 세밀한 사이드 채널 공격** — BTB와 구별되는 새로운 공격 벡터
2. **하이브리드 예측기 조작**: 복잡한 예측기를 1-level 모드로 강제 전환하는 기법
3. **SGX enclave 공격 가능**: 악성 OS가 스케줄링을 제어할 수 있는 환경에서 더 낮은 오차율
4. **방어 기법 제시**: PHT 랜덤화, BPU 파티셔닝, if-conversion 등

## 주요 결과

- **Skylake/Haswell**: 오차율 0.16-0.74% (격리 환경), 0.37-0.74% (노이즈 존재)
- **Sandy Bridge**: 오차율 0.68-2.44% (격리), 1.76-4.88% (노이즈)
- **SGX enclave**: 오차율 0.003-0.73% — 일반 시스템보다 더 정확
- **공격 응용**: Montgomery Ladder(RSA/ECC 키 비트 유출), libjpeg(픽셀 복잡도 복원), ASLR 우회

## 한계점

- 고해상도 공격을 위해 피해자 프로세스를 느리게 해야 함 (스케줄링 제어 필요)
- 랜덤화 코드 블록이 크래시 시 PHT 상태를 초기화할 수 있음
- Meltdown/Spectre와 같은 추측 실행 공격과의 결합 가능성은 미래 연구 주제

## 관련 개념

- [[paper-wiki/concepts/security.md|Security]] — 사이드 채널 공격 및 방어
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]] — SGX 및 메모리 격리
