---
tags: [paper, 2021, 2021ASPLOS, topic/cache, topic/compression, topic/dram]
venue: "ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS) 2021"
year: 2021
summary_path: "../paper-summaries/2021ASPLOS-summarize/bcd-deduplication-effective-memory-compression-using-partial-cache-line-deduplication.md"
---

# BCD Deduplication: Effective Memory Compression using Partial Cache-Line Deduplication

**Venue:** ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS) 2021
**저자:** Sungbo Park (Intel Corporation), Ingab Kang (University of Michigan), Yaebin Moon (Seoul National University), Jung Ho Ahn (Seoul National University), G. Edward Suh (Cornell University)

## 개요

- 메모리 집약적 워크로드(인메모리 데이터베이스, 키-값 스토어 등)는 대규모 워킹 세트를 가지며 성능이 메모리 용량에 크게 민감
- 애플리케이션의 워킹 세트가 메모리에 맞지 않으면 디스크 접근이 성능을 크게 저하시킴
- 현대 데이터 센터에서 메인 메모리(DRAM) 비용이 전체 비용의 상당 부분을 차지하며, 물리적 메모리 용량을 단순히 증가시키는 것은 비용이 많이 듦
- 대용량 DRAM 모듈은 상당한 양의 에너지를 소비하며, 데이터 센터에서 DRAM이 전체 에너지의 20~30%를 소비
- 기존 하드웨어 기반 메모리 압축 기법은 캐시라인 내부에서만 동작하여 캐시라인 간 중복성을 활용하지 못함
- 기존 메모리 중복 제거 기술은 동일한 메모리 블록만 처리할 수 있어 부분적인 일치를 활용할 수 없음

## 방법론

### 3.1. 부분 캐시라인 중복성 식별
- 4바이트 또는 8바이트 데이터 타입의 상위 비트들이 블록 내에서 다르더라도 블록 간에 공통 값을 가지는 경향 발견
- 이러한 부분적 일치를 활용하여 오버헤드 없이 압축 비율을 크게 증가 가능
- BCD는 8바이트마다 상위 2바이트가 동일한 여러 메모리 블록을 식별

### 3.2. 다중 수준 중복 제거 및 압축
- Leading-Zero Count (LZC) 압축과 결합된 다중 수준 중복 제거를 통해 부분적 블록 간 데이터 중복성을 활용하는 새로운 중복 제거 스킴 제안
- 메모리 중복 제거와 압축을 처음으로 긴밀하게 결합한 접근법
- 부분적으로 일치하는 블록의 차이에 대해 추가적인 압축 적용으로 압축 비율进一步 향상

### 3.3. LLC 및 메인 메모리 통합 구현
- L2 캐시와 LLC 경계에서 BCD를 수행하는 구현 개발
- LLC에 대한 단순 적용은 메타데이터 추가 접근으로 인한 성능 저하 초래 가능
- 사용자 정의 캐싱 및 선택적 중복 제거를 포함한 최적화 도입
- 선택적 중복 제거를 통해 BCD의 이점을 받지 못하는 애플리케이션의 성능 저하 제한

### 3.4. OS-하드웨어 협업 메커니즘
- 프로그램 실행 중에는 OS에 거의 투명하지만, OS는 메모리 내 다른 구조체의 크기를 결정하고 애플리케이션 특성 변화 시 하드웨어 실행을 제어해야 함
- 페이지 할당을 통한 선택적 중복 제거로 성능 저하 최소화
- 추가 메타데이터 접근 및 압축/중복 제거 작업에도 불구하고 적절한 면적 오버헤드 달성

## 핵심 기여

- BCD는 기존 캐시라인 압축이나 메모리 중복 제거로 활용되지 못했던 부분적 데이터 중복성을 새로운 방식으로 식별 및 활용하는 최초의 기법
- 압축과 중복 제거를 긴밀하게 결합하여 평균 1.94배 압축 비율 달성 (기존 최고 기술 대비 48.4% 향상)
- LLC 유효 용량 증가를 통해 성능 평균 2.7% 향상 달성
- 선택적 중복 제거를 통해 애플리케이션별 특성에 따른 적응적 압축 가능
- 하드웨어-소프트웨어 협업을 통한 효과적인 메모리 압축 구현으로 현대 메모리 계층 구조에서 실용적 적용 가능성 입증
- 메모리 비용 절감 및 에너지 소비 감소에 기여할 수 있는 유망한 기술

## 주요 결과

- 구현 언어: 하드웨어(ASIC/FPGA) 및 소프트웨어(OS 커널)
- 하드웨어 구성요소: LLC 경계에서의 BCD 압축/해제 유닛, 메타데이터 캐시, 선택적 중복 제거 제어 로직
- 소프트웨어: OS 커널의 페이지 할당 관리, 선택적 중복 제거 제어
- 메모리 구조: Translation Table, Hash Table, Overflow Region으로 구성된 메모리 영역
- 압축 알고리즘: Leading-Zero Count (LZC) 기반 압축
- 면적 오버헤드: 적절한 수준 유지

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2021ASPLOS-summarize/bcd-deduplication-effective-memory-compression-using-partial-cache-line-deduplication.md|전체 요약 보기]]
