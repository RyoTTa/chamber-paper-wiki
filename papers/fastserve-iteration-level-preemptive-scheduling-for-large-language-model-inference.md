---
tags: [paper, llm, inference, scheduling, preemption, nvidia, gpu]
venue: NSDI
year: 2026
summary_path: paper-summaries/2026NSDI-summarize/fastserve-iteration-level-preemptive-scheduling-for-large-language-model-inference.md
---

# FastServe: Iteration-Level Preemptive Scheduling for Large Language Model Inference

## 개요

FastServe는 LLM 추론의 자동 회귀 패턴을 활용한 분산 LLM 서빙 시스템으로, 각 출력 토큰 단위로 선점(preemption)이 가능합니다. 기존 시스템(vLLM, Orca)의 First-Come-First-Served(FCFS) 방식 대신 Skip-join Multi-Level Feedback Queue(MLFQ) 스케줄러를 통해 head-ofline blocking 문제를 해결하고 지연 시간을 최소화합니다.

## 방법론

- **Skip-join MLFQ 스케줄러**: 입력 길이에 따른 첫 번째 출력 토큰 실행 시간을 활용하여 적절한 큐 선택
- **GPU 메모리 관리**: 선점된 작업들의 KV 캐시를 호스트 메모리로 오프로딩하고 재개 시 다시 업로딩
- **Iteration-level 스케줄링**: 각 출력 토큰 생성 후 작업 계속/선점 결정

## 핵심 기여

- LLM 추론의 "semi information-agnostic" 설정 활용 (출력 길이 미지, 입력 길이 지)
- Skip-join 메커니즘을 통한 큐 축소 최소화
- Proactive memory management로 KV 캐시 효율적 관리

## 주요 결과

- vLLM 대비 최대 6.1배 처리량 향상
- 다양한 워크로드(ShareGPT, Alpaca)에서 일관된 성능 개선
- 큐잉 지연이 전체 지연의 주요 부분임을 확인

## 한계점

- GPU 메모리 관리 오버헤드 존재
- 매우 긴 출력을 생성하는 작업에서의 성능 제한
- 분산 환경에서의 통신 오버헤드

## 관련 개념

- [[paper-wiki/concepts/llm-inference|LLM Inference]]
- [[paper-wiki/concepts/gpu-scheduling|GPU Scheduling]]
- [[paper-wiki/concepts/memory-management|Memory Management]]

## 관련 논문

- [vLLM](paper-summaries/2023SOSP-summarize/vllm-efficient-memory-management-for-large-language-model-serving.md)
- [Orca](paper-summaries/2022OSDI-summarize/orca-a-distributed-serving-system-for-transformer-based-generative-models.md)