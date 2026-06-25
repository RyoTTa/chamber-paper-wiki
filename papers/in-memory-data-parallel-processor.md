---
tags: [in-memory-computing, nvm, reram, data-parallel, simd]
venue: ASPLOS
year: 2018
summary_path: paper-summaries/2018ASPLOS-summarize/in-memory-data-parallel-processor.md
---

# In-Memory Data Parallel Processor

## 개요

NVM(Non-Volatile Memory) 기반 인메모리 데이터 병렬 프로세서 아키텍처와 프로그래밍 프레임워크를 제안합니다. TensorFlow 기반 컴파일러를 통해 데이터 병렬 애플리케이션에서 significant한 성능 및 에너지 효율성 향상을 달성합니다.

## 방법론

- **인메모리 프로세서 아키텍처:** 메모리 배열과 디지털 컴포넌트가 타일로 그룹화된 구조
- **프로그래밍 프레임워크:** 데이터 흐름과 벡터 프로세싱 개념의 융합
- **컴파일러 프레임워크:** TensorFlow 입력을 인메모리 프로세서 코드로 변환

## 핵심 기여

1. 프로그래밍 가능한 인메모리 프로세서 아키텍처의 실현 가능성 입증
2. 데이터 병렬 애플리케이션에서 significant한 성능 및 에너지 효율성 향상
3. TensorFlow 기반 컴파일러 프레임워크로 프로그래밍 용이성 제공

## 주요 결과

- Parsec 벤치마크에서 멀티코어 CPU 서버 대비 7.5배 속도 향상
- Rodinia 벤치마크에서 서버급 GPU 대비 763배 속도 향상
- 데이터 이동량 평균 90% 이상 감소
- 에너지 효율성: CPU 대비 100배, GPU 대비 500배 향상

## 한계점

- ReRAM 기반 구현으로 다른 NVM 기술과의 호환성 검증 필요
- 벤치마크 워크로드에 최적화된 평가
- 실제 상용 애플리케이션에서의 검증 필요

## 관련 concept 페이지

- [[paper-wiki/concepts/nvm|NVM (Non-Volatile Memory)]]
- [[paper-wiki/concepts/in-memory-computing|In-Memory Computing]]
- [[paper-wiki/concepts/data-parallel|Data Parallel Processing]]

## 관련 논문 요약

- [in-memory-data-parallel-processor.md](paper-summaries/2018ASPLOS-summarize/in-memory-data-parallel-processor.md)