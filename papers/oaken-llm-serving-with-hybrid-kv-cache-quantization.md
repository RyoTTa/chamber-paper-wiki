---
tags: [paper, 2025, 2025ISCA, topic/cache, topic/compression, topic/dram, topic/llm-inference]
venue: "ISCA '25 (52nd Annual International Symposium on Computer Architecture), June 21–25, 2025, Tokyo, Japan"
year: 2025
summary_path: "../paper-summaries/2025ISCA-summarize/oaken-llm-serving-with-hybrid-kv-cache-quantization.md"
---

# Oaken: Fast and Efficient LLM Serving with Online-Offline Hybrid KV Cache Quantization

**Venue:** ISCA '25 (52nd Annual International Symposium on Computer Architecture), June 21–25, 2025, Tokyo, Japan
**저자:** Minsu Kim*, Seongmin Hong*, RyeoWook Ko, Soongyu Choi, Hunjong Lee, Junsoo Kim, Joo-Young Kim, Jongse Park

## 개요

- LLM 추론 서빙 시 배치 처리(batching)가 높은 throughput 달성에 필수적이나, attention 레이어의 activation-activation 연산은 요청별로 고유한 key/value를 사용하여 배칭이 불가능 → memory bandwidth bottleneck
- **KV 캐시의 메모리 압박:** 배치 크기 증가에 따라 KV 캐시가 기하급수적으로 증가하여, Llama2-13B 기준 배치 256에서 KV 캐시가 전체 메모리의 89%를 차지
- **HBM vs LPDDR 트레이드오프:** HBM은 높은 대역폭(2.0 TB/s)이나 제한적 용량(80GB), LPDDR은 낮은 대역폭(1.1 TB/s)이나 대용량(256GB) → 어느 쪽도 LLM 서빙의 대역폭+용량 동시 요구를 충족하지 못함
- **기존 KV 캐시 양자화의 한계:**
  - QServe/Atom: 채널 재ordering + 변환 행렬로 정확도 손실 큼
  - KIVI/KVQuant: 온라인 정렬(sorting) 또는 혼합 정밀도 연산으로 런타임 오버헤드 과도
  - Tender: 간접 인덱싱 기반 채널 재ordering으로 정확도 저하
- **핵심 통찰:** weight-only 양자화는 배치 추론에서 제한적 효과, KV 캐시 양자화가 근본적 메모리 병목 해결에 효과적

## 방법론

### 3.1. KV 캐시 분포 관찰 (Observations)

- **Observation 1:** KV 캐시 값의 범위는 모델과 디코더 레이어마다 고유한 특성을 가짐 → 모델별, 레이어별로 양자화 인자를 독립적으로 결정해야 함
- **Observation 2:** 같은 모델에서 입력 데이터셋에 관계없이 KV 캐시 범위가 일관됨 → 오프라인 프로파일링으로 결정된 임계값이 온라인에서도 유효
- **Observation 3:** 고magnitude 값이 특정 채널에 집중되지만, 예외적 패턴도 존재 → 단순 per-vector 양자화로는 정확도 손실 발생, 여러 양자화 그룹 필요

### 3.2. Threshold-based Online-Offline Hybrid Quantization

- **Four group thresholds:** T^o_lo, T^i_lo, T^i_hi, T^o_hi로 외부/내부/중간 그룹 분리
- **오프라인 프로파일링:** 약 100회 추론으로 topK 연산을 통해 임계값 결정, 모델별 약 10분 소요
- **온라인 양자화:** 토큰별 KV 벡터에서 min/max로 스케일 팩터 σ = (2^m - 1) / (Max - Min) 계산 후 균일 양자화
  - Middle group: 4-bit, Inner/Outer group: 5-bit

### 3.3. Group-Shift Quantization

- 오프라인 임계값을 이용하여 아웃라이어 분포를 shift: x > T^o_hi인 값에서 T^o_hi를 뺌, x < T^o_lo인 값에서 T^o_lo를 뺌
- 중간 그룹도 동일 방식 적용 → 분포를 좁은 범위로 집중시켜 저비트 양자화 가능
- **양자화 함수 Q_o(x):** 각 그룹에 대해 shift 후 uniform quantization 적용

### 3.4. Fused Dense-and-Sparse Encoding

- **Inlier (middle group):** Dense matrix에 4-bit로 저장
- **Outlier (outer/inner groups):** Sparse COO 형식으로 저장 (6비트 인덱스 + 1비트 그룹 + 값)
- **핵심 최적화:** Dense matrix의 zeroed element(원래 아웃라이어 위치)에 5-bit 아웃라이어의 4비트를 퓨즈하여 저장 → 아웃라이어 엔트리를 23비트에서 8비트로 축소
- Memory alignment 유지하면서 압축률 극대화

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1. 전체 구조

- **Compute Cores:** MPU(Matrix Processing Unit) + VPU(Vector Processing Unit)로 LLM 추론 연산 수행
- **Memory Controllers:** 디바이스 메모리에서 모델 파라미터 및 KV 캐시 읽기/쓰기
- **DMA with Oaken Modules:** 양자화/디양자화 엔진과 MMU(Memory Management Unit) 통합

### 4.2. 양자화/디양자화 엔진

- **Quantization Engine (DMA 내):**
  - Decomposer: 활성화를 3개 그룹으로 분리하고 group-shift 수행
  - Inlier Quantizer: dense matrix용 4-bit 양자화
  - Outlier Quantizer: sparse COO용 5-bit 양자화
  - Zero-remove shifter로 fused encoding 구현
- **Dequantization Engine (DMA 내):**
  - Inlier Dequantizer: dense 데이터 버퍼링으로 동기화
  - Outlier Dequantizer: zero-insert로 원래 데이터 정렬 복원
  - Streaming 방식으로 전체 KV 캐시 처리

### 4.3. Memory Management Unit (MMU)

- **Dual Management Tables:** Dense/Sparse 데이터를 각각 별도 테이블로 관리
- **Burst Mode 최적화:** KV 캐시를 attention head별로 분할하여 연속 페이지에 기록 → 다음 토큰 생성 시 burst read 지원
- **Virtual-to-Physical Address Mapping:** 페이지 단위로 동적 할당, 조각화 방지

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]


## 전체 요약

[[../paper-summaries/2025ISCA-summarize/oaken-llm-serving-with-hybrid-kv-cache-quantization.md|전체 요약 보기]]
