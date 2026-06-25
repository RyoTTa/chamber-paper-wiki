---
tags: [paper, 2018, 2018HPCA, topic/cache, topic/energy-efficiency, topic/gpu]
venue: "HPCA 2018"
year: 2018
summary_path: "../paper-summaries/2018HPCA-summarize/latte-cc-latency-tolerance-aware-adaptive-cache-compression-management-for-energy-efficient-gpus.md"
---

# LATTE-CC: Latency Tolerance Aware Adaptive Cache Compression Management for Energy Efficient GPUs

**Venue:** HPCA 2018
**저자:** Arunkumar A., Lee S.Y., Soundararajan V., Wu C.J. (Indiana University, University of Michigan)

## 개요

GPU의 동적 레이턴시 내성 특성을 활용한 적응형 캐시 압축 관리 기법입니다. 세 가지 압축 모드(비압축, 저레이턴시, 고용량)를 실시간으로 선택하여 성능 및 에너지 효율을 동시 향상시킵니다. 캐시 민감 GPGPU 애플리케이션의 성능을 최대 48.4% 향상시키며, GPU 에너지 소비를 평균 10% 절감합니다.

## 방법론

### 레이턴시 내성 예측기 (Latency Tolerance Estimator)
- GPU SMP의 동적 레이턴시 내성 특성을 실시간으로 추정
- SIMD 레인 활성도, 메모리 접근 패턴 등을 기반으로 레이턴시 내성 추정
- 워크로드 특성에 따라 압축 모드 결정에 필요한 정보 제공

### 용량 이점 예측기 (Capacity Benefit Estimator)
- 캐시 압축을 통한 효과적 용량 증가가 가져오는 성능 이점을 추정
- 캐시 히트율 향상 및 메모리 대역폭 절감 효과 예측
- 워크로드별 최적 압축 모드 선택을 위한 의사 결정 지원

### 적응형 압축 모드 선택
- **비압축 모드 (No Compression):** 레이턴시 내성이 낮을 때 선택, 오버헤드 없음
- **저레이턴시 압축 모드 (Low-latency Compression):** 빠른 압축/해제 속도, 중간 수준의 압축률
- **고용량 압축 모드 (High-capacity Compression):** 높은 압축률, 상대적으로 높은 레이턴시
- 동적인 워크로드 변화에 따라 실시간으로 모드 전환

## 핵심 기여

1. GPU의 동적 레이턴시 내성 특성을 활용한 최초의 적응형 캐시 압축 관리 기법 제안
2. 세 가지 압축 모드를 동적으로 선택하여 성능 및 에너지 효율 동시 향상
3. 레이턴시 내성 예측기와 용량 이점 예측기를 통한 실시간 최적화
4. 기존 정적 압축 기법 대비 2배의 에너지 절감 효과 달성

## 주요 결과

- **성능 향상**: 캐시 민감 GPGPU 애플리케이션의 성능을 최대 48.4% 향상, 평균 19.2% 향상
- **에너지 절감**: GPU 에너지 소비를 평균 10% 절감 (기존 최신 압축 기법 대비 2배)
- **효율성**: 다양한 워크로드에서 일관된 성능 향상 및 에너지 효율성 달성

## 한계점

- GPU 시뮬레이터(GPGPU-Sim) 기반 검증에 한정, 실제 하드웨어 구현에서의 검증 필요
- 특정 GPU 아키텍처(Maxwell) 모델링에 국한된 평가
- 레이턴시 내성 예측기의 정확도가 전체 성능에 미치는 영향 추가 연구 필요
- 다양한 워크로드에서의 일반화 가능성 추가 검증 필요

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache Compression]]
- [[paper-wiki/concepts/energy-efficiency.md|Energy Efficiency]]
- [[paper-wiki/concepts/gpu.md|GPU Architecture]]
- [[paper-wiki/concepts/memory-systems.md|Memory Systems]]