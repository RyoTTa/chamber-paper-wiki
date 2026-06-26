---
tags: [paper, 2018, 2018ASPLOS, topic/cache, topic/gpu, topic/virtual-memory]
venue: "ASPLOS 2018 (Architectural Support for Programming Languages and Operating Systems)"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/filtering-translation-bandwidth-with-virtual-caching.md"
---

# Filtering Translation Bandwidth with Virtual Caching

**Venue:** ASPLOS 2018 (Architectural Support for Programming Languages and Operating Systems)
**저자:** Hongil Yoon (Google), Jason Lowe-Power (University of California, Davis), Gurindar S. Sohi (University of Wisconsin-Madison)

## 개요

- CPU와 동일한 칩에 통합된 GPU가 보편화되어 있으며, 프로그래밍 용이성을 위해 많은 시스템이 GPU 하드웨어에서의 가상 주소 접근을 지원
- 그러나 이는 모든 메모리 접근 시 주소 번역을 필요로 하며, 이는 성능과 에너지에 significant한 오버헤드 발생
- 기존 CPU 스타일 MMU(Memory Management Unit)는 GPU의 마이크로아키텍처와 워크로드 차이로 인해 효과적이지 않음
- GPU의 세 가지 특성으로 인해 CPU 대비 가상 메모리 오버헤드 증가:
  1. GPU는 대부분의 CPU보다 많은 컴퓨팅 유닛 보유 (예: XBOX ONE에서 40개 컴퓨팅 유닛) → 공유 번역 리소스에 대한 압력 증가
  2. GPU는 와이드 SIMD 유닛 보유 → 단일 GPU 로드/스토어 명령이 여러 다른 주소에 scatter/gather 요청 발행 가능
  3. GPU는 많은 실행 컨텍스트를 통해 메모리 레이턴시를 허용 → 최대 40개의 활성 컨텍스트 보유

## 방법론

### 3.1. 가상 캐시 아키텍처
- 전체 GPU 캐시 계층 (L1 및 L2)을 가상 캐시로 구성
- L1 캐시: 프라이빗 캐시로 각 컴퓨팅 유닛에 할당
- L2 캐시: 공유 캐시로 모든 컴퓨팅 유닛이 접근
- 가상 주소를 직접 사용한 캐시 접근으로 주소 번역 오버헤드 제거

### 3.2. 주소 번역 대역폭 필터링 메커니즘
- 프라이빗 TLB miss 발생 시 가상 캐시에서 먼저 확인
- 가상 캐시 히트 시 주소 번역 하드웨어 접근 불필요
- 가상 캐시 미스 시에만 주소 번역 하드웨어 접근
- 대역폭 요구사항 효과적 필터링

### 3.3. 동의어(Synonym) 문제 해결
- GPU의 가속기 특화 속성 활용: 동의어 가능성이 낮음
- 태그 기반 동의어 검출 메커니즘
- 불필요한 캐시 코히어런스 오버헤드 최소화

## 핵심 기여

- GPU에서의 가상 캐시 계층은 주소 번역 대역폭을 효과적으로 필터링
- 소프트웨어 수정 없이 기존 GPU 프로그램과 호환
- 이상적인 MMU에 근접하는 성능 달성 가능
- 향후 GPU 가상 메모리 시스템 설계를 위한 기초 기술 제공

## 주요 결과

- GPU 시뮬레이터 기반 구현
- gem5 시뮬레이터 확장
- 가상 캐시 계층 구현 및 평가 환경 구축
- 기존 GPU 아키텍처와의 호환성 확인

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2018ASPLOS-summarize/filtering-translation-bandwidth-with-virtual-caching.md|전체 요약 보기]]
