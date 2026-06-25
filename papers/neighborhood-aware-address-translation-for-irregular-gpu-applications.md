---
tags: [paper, gpu, address-translation, tlb, virtual-memory, 2018]
venue: MICRO 2018
year: 2018
summary_path: paper-summaries/2018MICRO-summarize/neighborhood-aware-address-translation-for-irregular-gpu-applications.md
---

# Neighborhood-Aware Address Translation for Irregular GPU Applications

## 개요

- 비정형 GPU 워크로드의 주소 변환 병목 해결을 위한 근방 인식(Neighborhood-Aware) 메커니즘 제안
- PTW가 캐시 라인을 읽을 때 같은 근방의 동시 워크 요청을 합치기하여 메모리 접근 37% 감소
- 평균 1.7배, 최대 2.3배 실행 시간 가속

## 방법론

- 근방(Neighborhood) 정의: PTE가 동일한 64바이트 캐시 라인에 저장된 가상 페이지들의 집합
- 리프 레벨 + 상위 레벨 모두에서의 합치기(Coalescing)
- 도착 순서 무관하게 같은 근방의 요청을 즉시 서비스
- 기존 PWC(Page Walk Cache)와 시너지

## 핵심 기여

- 캐시 라인 내 PTE 중복 활용이라는 본질적 관찰
- 거의 제로 비용의 하드웨어 메커니즘
- 리프/상위 레벨 모두에서의 근방 인식 합치기

## 주요 결과

- 페이지 테이블 메모리 접근 평균 37% 감소
- 비정형 GPU 워크로드 실행 시간 평균 1.7배 가속
- 리프 레벨: 약 18% 접근 감소, 상위 레벨: 추가 약 19% 감소

## 한계점

- 완전 선형 접근 패턴에서는 효과 제한
- GPU 워크로드 특화 (CPU에는 적용 불명확)
- x86-64 4단계 페이지 테이블 기반 (ARM 등 다른 아키텍처 미적용)

## 관련 concept 페이지

- [[paper-wiki/concepts/gpu|GPU]]
- [[paper-wiki/concepts/virtual-memory|Virtual Memory]]
