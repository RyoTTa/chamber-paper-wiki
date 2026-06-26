---
tags: [paper, 2018, 2018HPCA, topic/cache, topic/compression, topic/gpu]
venue: "IEEE International Symposium on High Performance Computer Architecture (HPCA) 2018"
year: 2018
summary_path: "../paper-summaries/2018HPCA-summarize/latte-cc-latency-tolerance-aware-adaptive-cache-compression-management-for-energy-efficient-gpus.md"
---

# LATTE-CC: Latency Tolerance Aware Adaptive Cache Compression Management for Energy Efficient GPUs

**Venue:** IEEE International Symposium on High Performance Computer Architecture (HPCA) 2018
**저자:** Arunkumar A., Lee S.Y., Soundararajan V., Wu C.J. (Indiana University, University of Michigan)

## 개요

- 일반 목적 GPU(GPGPU) 애플리케이션은 메모리 서브시스템 효율성과 데이터 캐시 용량에 크게 의존
- GPU 캐시 압축은 캐시 용량을 효과적으로 확장하고 캐시 효율성을 향상시킬 수 있지만, 캐시 히트 레이턴시 증가라는 비용이 발생
- 기존 고성능 캐시 압축 기법은 주로 하위 레벨 캐시(L2/L3)에 적용되어 왔으며, GPU의 L1 캐시에는 적용이 제한적
- 최신 캐시 압축 기법을 GPU에 직접 적용하면 성능 변동이 -52%에서 +48%까지 크게 발생 (Fig. 1 참조)
- GPU 워크로드의 동적 레이턴시 내성 특성이 고려되지 않은 정적 압축 방식은 에너지 효율성에 한계

## 방법론

### 3.1. 레이턴시 내성 예측기 (Latency Tolerance Estimator)

- GPU SMP의 동적 레이턴시 내성 특성을 실시간으로 추정
- 워크로드 특성에 따라 압축 모드 결정에 필요한 정보 제공
- SIMD 레인 활성도, 메모리 접근 패턴 등을 기반으로 레이턴시 내성 추정

### 3.2. 용량 이점 예측기 (Capacity Benefit Estimator)

- 캐시 압축을 통한 효과적 용량 증가가 가져오는 성능 이점을 추정
- 캐시 히트율 향상 및 메모리 대역폭 절감 효과 예측
- 워크로드별 최적 압축 모드 선택을 위한 의사 결정 지원

### 3.3. 적응형 압축 모드 선택

- **비압축 모드 (No Compression):** 레이턴시 내성이 낮을 때 선택, 오버헤드 없음
- **저레이턴시 압축 모드 (Low-latency Compression):** 빠른 압축/해제 속도, 중간 수준의 압축률
- **고용량 압축 모드 (High-capacity Compression):** 높은 압축률, 상대적으로 높은 레이턴시
- 동적인 워크로드 변화에 따라 실시간으로 모드 전환

## 핵심 기여

- LATTE-CC는 GPU 캐시 압축에서 레이턴시 내성 특성을 효과적으로 활용하는 최초의 적응형 관리 기법
- 동적인 워크로드 변화에 따른 실시간 압축 모드 조정으로 성능 및 에너지 효율 동시 향상
- GPU 메모리 에너지 소비 절감에 크게 기여하며,未来的 GPU 설계에 중요한 시사점 제공
- 캐시 압축 기술의 GPU 적용 가능성을 높이고 에너지 효율적인 GPU 설계를 위한 기반 기술로 활용 가능

---

## 참고 자료

- 논문 원문: `/home/ryotta205/Chamber_paper/paper-source/2018HPCA/LATTE-CC_Latency_Tolerance_Aware_Adaptive_Cache_Compression_Management_for_Energy_Efficient_GPUs.pdf`
- 관련 개념: GPU Cache Compression, Latency Tolerance, Energy Efficiency, Adaptive Compression, GPGPU

## 주요 결과

- GPU 캐시 계층 구조에 레이턴시 내성 예측기 및 용량 이점 예측기 하드웨어 추가
- 세 가지 압축 모드를 지원하는 다중 모드 압축 인코더/디코더 구현
- 캐시 라인 태그에 압축 모드 정보 저장 (3비트 오버헤드)
- 압축/해제 하드웨어의 에너지 오버헤드 최소화
- 기존 GPU 아키텍처와의 호환성 확보를 위한 비침습적 설계

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/gpu.md|GPU]]


## 전체 요약

[[../paper-summaries/2018HPCA-summarize/latte-cc-latency-tolerance-aware-adaptive-cache-compression-management-for-energy-efficient-gpus.md|전체 요약 보기]]
