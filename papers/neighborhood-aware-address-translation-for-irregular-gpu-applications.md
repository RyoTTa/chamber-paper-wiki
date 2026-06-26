---
tags: [paper, 2018, 2018MICRO, topic/cache, topic/dram, topic/gpu, topic/virtual-memory]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/neighborhood-aware-address-translation-for-irregular-gpu-applications.md"
---

# Neighborhood-Aware Address Translation for Irregular GPU Applications

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Seunghee Shin (Binghamton University), Michael LeBeane (AMD), Yan Solihin (University of Central Florida), Arkaprava Basu (Indian Institute of Science)

## 개요

- GPU의 SIMT(Single-Instruction-Multiple-Thread) 실행 모델은 비정형(Irregular) 워크로드에서 대량의 동시 메모리 접근을 생성
- 비정형 워크로드의 메모리 접근 패턴은 공간적 지역성이 낮아 주소 변환 오버헤드가 심각 (최대 4배 성능 저하)
- GPU의 대규모 병렬성으로 인해 동시 TLB(T Translation Lookaside Buffer) 미스가 급증 → 페이지 테이블 워크(PTW)의 대기 시간 증가
- x86-64 아키텍처에서 페이지 테이블 워크는 최대 4번의 순차적 메모리 접근 필요
- 기존 IOMMU의 다중 PTW도 비정형 워크로드의 burst TLB 미스를 효과적으로 처리하지 못함

## 방법론

### 3.1. 리프(Leaf) 레벨에서의 합치기(Coalescing)

- PTW가 64바이트 캐시 라인을 가져오면, 해당 라인에 포함된 모든 PTE에 대한 대기 중인 페이지 워크 요청을 즉시 서비스
- 도착 순서에 관계없이 같은 근방의 요청을 병렬로 처리
- 기존 하드웨어: 요청과 관련 없는 PTE는 단순히 폐기 → 새로운 메모리 접근 필요
- 제안 기법: 이미 가져온 PTE를 활용하여 후속 요청의 메모리 접근을 제거

### 3.2. 상위(Upper) 레벨에서의 합치기

- x86-64의 4단계 페이지 테이블(L4→L3→L2→L1)에서 상위 레벨(L4, L3, L2)의 엔트리도 동일하게 근방 인식 합치기 적용 가능
- 상위 레벨의 엔트리도 8바이트 크기 → 캐시 라인당 8개의 엔트리 저장
- 상위 레벨 워크에서도 같은 근방의 동시 요청을 합치기하여 메모리 접근 횟수 대폭 감소

### 3.3. 페이지 워크 캐시(PWC)와의 시너지

- 페이지 워크 캐시(PWC)는 상위 레벨의 최근 사용된 엔트리를 캐싱하여 워크 단계를 줄임
- 근방 인식 합치기와 PWC는 독립적으로 작동하며, 각각 유사한 수준의 성능 향상 제공
- 리프 레벨과 상위 레벨의 합치기가 거의 동등한 중요도

## 핵심 기여

- 비정형 GPU 워크로드의 주소 변환 병목을 해결하는 간단하고 효율적인 하드웨어 메커니즘 제시
- 캐시 라인 내 PTE의 중복 활용이라는 본질적 관찰에 기반 → 거의 제로 비용으로 구현
- 페이지 테이블 접근 37% 감소, 실행 시간 1.7배 가속 달성
- GPU의 공유 가상 메모리(SVM) 환경에서 주소 변환 오버헤드를 효과적으로 완화

## 주요 결과

- **시뮬레이션 환경:** gem5 시뮬레이터 기반 GPU 모델
- **시스템 구성:** 다중 CU(Compute Unit), 다중 SIMD 유닛, 공유 GPU TLB + IOMMU
- **IOMMU 구성:** 다중 독립 PTW (8-16개), 2단계 TLB
- **페이지 테이블:** x86-64 4단계 레이디크스 트리 (512-ary)
- **워크로드:** Rodinia 벤치마크, Pannotia 그래프 애플리케이션, Polybench

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/neighborhood-aware-address-translation-for-irregular-gpu-applications.md|전체 요약 보기]]
