---
tags: [cache, dnn-accelerator, in-memory-computing, bit-serial]
venue: ISCA
year: 2018
summary_path: paper-summaries/2018ISCA-summarize/neural-cache-bit-serial-in-cache-acceleration-of-deep-neural-networks.md
---

# Neural Cache: Bit-Serial In-Cache Acceleration of Deep Neural Networks

## 개요

Neural Cache는 현대 프로세서의 LLC 캐시 구조를 대규모 병렬 연산 유닛으로 재활용하여 DNN 추론을 가속화하는 아키텍처입니다.

## 방법론

- **SRAM 제자리 연산**: 비트 라인에서 직접 AND/NOR 연산 수행 (워드 라인 동시 활성화)
- **비트 직렬 연산**: 전치(transpose) 레이아웃에서 비트 간 곱셈, 덧셈, 축소 연산
- **필터 고정(stationary) 방식**: 필터 가중치를 캐시에 고정하고 입력을 스트리밍
- **트랜스포즈 메모리 유닛(TMU)**: 비트 병렬↔전치 레이아웃 변환 하드웨어

## 핵심 기여

1. 데이터 이동 없이 캐시 내에서 합성곱, 완전 연결, 풀링, 양자화 연산 지원
2. Xeon E5 캐시에서 최대 1,146,880개의 비트 직렬 ALU 슬롯 확보
3. CPU 대비 18.3배, GPU 대비 7.7배 지연 시간 향상

## 주요 결과

- 지연 시간: CPU 대비 18.3×, GPU 대비 7.7× 향상
- 처리량: CPU 대비 12.4×, GPU 대비 2.2× 향상
- 전력: CPU 대비 50%, GPU 대비 53% 절감
- 면적 오버헤드: 프로세서 다이 기준 2% 미만

## 한계점

- 8비트 양자화 정밀도에 의존 (정확도 손실 가능성)
- 캐시 크기에 따른 연산 용량 제한
- 동작 중 캐시 교체와의 충돌 관리 필요

## 관련 concept

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dnn-accelerator.md|DNN Accelerator]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
