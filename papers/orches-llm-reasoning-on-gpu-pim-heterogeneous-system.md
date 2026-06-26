---
tags: [paper, 2025, 2025MICRO, topic/gpu, topic/llm-inference, topic/pim]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO 2025)"
year: 2025
summary_path: "../paper-summaries/2025MICRO-summarize/orches-llm-reasoning-on-gpu-pim-heterogeneous-system.md"
---

# ORCHES: Orchestrated Test-Time-Compute-based LLM Reasoning on Collaborative GPU-PIM Heterogeneous System

**Venue:** IEEE/ACM International Symposium on Microarchitecture (MICRO 2025)
**저자:** Sixu Li, Yuzhou Chen, Chaojian Li, Yonggan Fu, Zheng Wang, Zhongzhi Yu, Haoran You, Zhifan Ye, Wei Zhou, Yongan Zhang, Yingyan (Celine) Lin (Georgia Institute of Technology)

## 개요

- LLM 기반 AI 추론의 실용화를 위해 Test-Time Compute (TTC) 패러다임이 부상: 단일 추론이 아닌 다단계 분기(branch) 기반 추론으로 성능 향상
- TTC 기반 추론은 1B 모델이 405B+ 모델보다 MATH500 벤치마크에서 우수한 성능을 보이나, 하드웨어 효율성 문제로 실용화에 한계
- Edge GPU에서 MATH500 단일 문제 해결에 약 10분 소요 — 실용성 심각하게 제한
- 기존 GPU/PIM 가속 솔루션은 단일 단계 LLM 추론에 최적화되어 있으며, TTC의 고유한 과제를 해결하지 못함
- TTC 추론의 세 가지 핵심 장벽:
  1. **가변 병렬성 (Variable Parallelism):** 추론 의존적 동적 제어 흐름과 변하는 배치 크기로 인해 워크로드 스케줄링이 복잡
  2. **분기 의존성 (Branch Dependencies):** 순차적 추론 단계 간 효율적인 파이프라이닝을 방해
  3. **분기 가지치기 (Branch Pruning):** 메모리 단편화 및 비정형 데이터 접근 패턴 발생

## 방법론

### 3.1. 시스템 개요

- GPU와 PIM이 협업하는 이기종(heterogeneous) 시스템
- GPU: Policy 모델 (decoding) 및 PRM (Process Reward Model, prefilling) 실행
- PIM: 메모리 대역폭 병목을 완화하고 병렬 처리 가속화
- Figure 1에서 TTC 기반 추론과 표준 단일 단계 추론의 비교 시각화
- TTC 기반 추론은 모델 크기를 �이면서 추론 능력을 강화 ("width"와 "depth" 증가)

### 3.2. 적응적 워크로드 할당 (Adaptive Workload Assignment)

- TTC 추론에서 Policy 모델과 PRM은 서로 다른 병렬성 특성 보유
  - Policy 모델: token-by-token decoding → memory-bound
  - PRM: 여러 후보(branch) 동시 평가 → compute-bound 가능
- 공유 KV 캐시 사용 시 연산이 compute-bound가 될 수 있음 (병렬성 증가)
- 고유 KV 캐시 접근은 memory-bound 유지
- 추론 진행에 따라 공유 대 고유 KV 캐시 비율이 동적으로 변화 → 워크로드 특성 변화
- ORCHES: 실시간으로 GPU-PIM 간 워크로드를 동적 배분하여 병렬성 극대화

### 3.3. 분기 인식 파이프라이닝 (Branch-Aware Pipelining)

- 표준 LLM 디코딩: 각 토큰 생성이 이전 토큰에 순차적으로 의존 (auto-regressive)
- TTC 추론: 추론 단계 간 추가적인 순차적 의존성 존재
  - Step N의 결과가 Step N+1의 입력이 됨
  - 분기 간 의존성으로 인해 파이프라인 스타그 발생
- 스펙큘러티브 실행 활용: 미래 분기를 미리 추론하여 파이프라인 브레이크를 최소화
- Figure 2에서 세 가지 과제 (C1, C2, C3)와 ORCHES의 솔루션 시각화

### 3.4. 단편화 인식 메모리 구조화 (Fragmentation-Aware Memory Structuring)

- Branch 가지치기로 인해 메모리 단편화 발생
- 불규칙한 데이터 접근 패턴 → 캐시 효율성 저하
- ORCHES: �ordinated caching과 최적화된 메모리 레이아웃 재구성을 통해 데이터 접근 효율성 향상
- PIM의 메모리 접근 패턴을 최적화하여 단편화 문제 완화

### 3.5. GPU-PIM 협업 메커니즘

- GPU가 추론 파이프라인의 메인 제어를 담당
- PIM이 병렬성이 높은 연산을 오프로딩
- 동적 워크로드 분배 알고리즘으로 시스템 전체 효율성 최적화
- TTC의 고유한 워크로드 특성 (가변 배치 크기, 분기 의존성)에 대응하는 유연한 아키텍처

## 핵심 기여

- **핵심 기여:** TTC 기반 LLM 추론의 효율성을 해결하는 최초의 GPU-PIM 협업 시스템 ORCHES 제안
- **성능 향상:** Text-based reasoning에서 4.16×, Vision-based reasoning에서 3.10× speedup
- **정확도 유지:** 원래 추론 파이프라인의 정확도를 완전히 보존
- **실용성:** Edge 디바이스에서의 TTC 기반 추론을 현실화하여, 소형 모델로도 강력한 추론 능력 구현 가능
- **의의:** LLM 추론의 패러다임을 단일 단계에서 다단계 TTC 기반 추론으로 전환하는 데 필요한 하드웨어 지원을 제시
- **향후 연구:** 다양한 PIM 아키텍처와의 통합, 더 복잡한 추론 파이프라인으로의 확장

## 주요 결과

- **시스템 구성:** GPU + PIM 이기종 아키텍처
- **소프트웨어 스택:** LLM 추론 프레임워크와 통합된 ORCHES 런타임
- **하드웨어:** PIM 유닛 (메모리 기반 연산 가속기) + 기존 GPU
- **프로토 타입:** 실험용 GPU-PIM 협업 시스템
- **평가 대상:** Text-based 및 Vision-based 추론 태스크

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2025MICRO-summarize/orches-llm-reasoning-on-gpu-pim-heterogeneous-system.md|전체 요약 보기]]
