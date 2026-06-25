---
tags: [paper, 2025, 2025ISCA, topic/cache, topic/compression, topic/gpu, topic/llm-inference]
venue: "ISCA '25 (52nd Annual International Symposium on Computer Architecture), June 21–25, 2025, Tokyo, Japan"
year: 2025
summary_path: "../paper-summaries/2025ISCA-summarize/ecco-entropy-aware-cache-compression-for-llms.md"
---

# Ecco: Improving Memory Bandwidth and Capacity for LLMs via Entropy-Aware Cache Compression

**Venue:** ISCA '25 (52nd Annual International Symposium on Computer Architecture), June 21–25, 2025, Tokyo, Japan
**저자:** Feng Cheng, Cong Guo, Chiyue Wei, Junyao Zhang, Changchun Zhou, Edward Hanson, Jiaqi Zhang, Xiaoxiao Liu, Hai Li, Yiran Chen

## 개요

- LLM 추론 시 메모리 병목이 심각: KV 캐시가 전체 메모리의 최대 72.7% (LLaMA-7B, 시퀀스 길이 2K, 배치 32 기준 34.4GB/47.3GB)
- 디코딩 단계는 small-batch GEMM → batched GEMV로 연산 밀도가 극도로 낮아 memory-bound
- 기존 양자화 기법의 한계:
  - **AWQ:** 2-3x 메모리 절감, 1.5x 가속이나 runtime 인코딩 오버헤드 존재
  - **Quarot:** 정확도 SOTA이나 Hadamard 변환 등으로 FP16 대비 0.6x 속도 (오히려 느림)
  - 복잡한 압축 체계는 인코딩/디코딩 오버헤드가 저장 대역폭 절감 효과를 상쇄
- GPU L2 캐시 압축(A100 등)은 상용 가속기에서 이미 채택 중이나, LLM에 최적화된 압축 기법 부재
- **핵심 통찰:** 압축의 주요 목표는 bit efficiency (η = H / Breal) 향상 → 정보 엔트로피 H 증가 또는 실제 비트 오버헤드 Breal 감소

## 방법론

### 3.1. 가중치/KV 캐시 압축 (4x 압축)

- **Step 1:** 128개 FP16 값으로 그룹 생성 (그룹 단위 양자화)
- **Step 2:** 각 그룹의 최대 절대값을 FP16→FP8 스케일 팩터로 추출하고 정규화
- **Step 3:** 스케일 팩터를 제외한 127개 값에 대해 k-means 클러스터링 (15 클러스터)
  - 각 클러스터 중심값을 k-means 패턴으로 저장
- **Step 4:** 모든 그룹의 k-means 패턴에 대해 두 번째 k-means 클러스터링 (S=64 공유 패턴)
- **Step 5:** 각 그룹은 64개 공유 패턴 중 MSE가 최소인 패턴 선택 → 선택된 패턴 인덱스(ID_KP) 기록
- **Step 6-7:** 공유 패턴별 인덱스 분포에 k-means 클러스터링 (H=4 Huffman 코드북)
- **Step 8:** 각 그룹은 최적 압축률을 제공하는 Huffman 코드북 선택 (ID_HF 기록)
- **Step 9:** 클리핑/패딩으로 고정 블록 크기 유지

**압축 블록 형식 (512 bits):**
- ID_HF (2 bits) + 스케일 팩터 (8 bits) + 패딩 아웃라이어 (0~240 bits) + ID_KP (1~15 bits) + Huffman 코딩 데이터 (256~501 bits)

### 3.2. KV 캐시 압축 (온라인 최적화)

- 가중치 압축과 동일한 오프라인 단계 (Step 1~4, 6~7) 적용
- **차이점:** 패턴 선택은 온라인 실행 (Step 5)
  - MSE 기반 최적 패턴 선택은 하드웨어 비용이 과도 (S배 하드웨어 중복 또는 S배 지연)
  - **최적화:** 그룹의 min/max값만으로 공유 패턴의 min/max와 비교 → 비교 횟수를 G에서 2로 감소
  - 실험적 결과, 이 단순화로 perplexity 미세 하락만으로 하드웨어 복잡도 대폭 감소
- 가중치와 동일한 압축 블록 구조 → 통합 디압스 구현 가능

### 3.3. 활성값 압축 (2x 압축)

- 더 동적인 특성을 고려하여 8비트 정수 기반 균일 양자화 + zero point 사용
- 스케일 팩터와 zero point를 매 8비트마다 저장
- 7비트 압축 데이터 + 1비트(매 8비트)로 메타데이터 저장

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1. 4x 디암프레서

- **Parallel Huffman Decoder:** 64개 디코더가 오버랩된 섹션에 병렬 처리
  - 코드 길이 2~8비트로 제한하여 효율적 디코딩
  - 각 디코더는 8비트 그룹 처리 → 1~4개 데이터 디코딩 + 7비트 오버랩으로 다음 세그먼트 시작점 확인
  - 8개 서브디코더가 동일 15비트 데이터를 다른 시작 위치(0~7)로 처리
- **Data Concatenator:** 인접 2개 디코더 출력을 6단계 트리 방식으로 병합
  - EOP(Every Other Position) 인디케이터로 올바른 쌍 매칭
- **Data Mapper:** 128개 병렬 매퍼가 디코딩된 인덱스를 실제 클러스터 중심값으로 매핑
  - 아웃라이어 주소 + 마스크로 k-means 패턴 값 vs 아웃라이어 값 선택

### 4.2. 2x 디암프레서

- 스케일 팩터와 zero point 추출 (매 8비트)
- 7비트 양자화 값을 8비트로 부호 확장
- 비트 조작 기반 효율적 디압스 (2개 연산만으로 완료)

### 4.3. 4x 컴프레서

- **Bitonic Sorter:** 스케일 팩터, 상위 16개 정렬 값/인덱스, 그룹 min/max 추출
- **Pattern Selector:** 16개 공유 패턴(하드웨어 비용 절감을 위해 64→16 축소)의 min/max와 그룹 min/max 간 제곱차 합산 → 최소 오류 패턴 선택
- **4개 병렬 인코더:** 각 Huffman 코드북에 대해 병렬 인코딩 → 최短 길이 선택
- **클리핑:** 비트스트림이 블록 크기를 초과하면 초과분 클리핑

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]


## 전체 요약

[[../paper-summaries/2025ISCA-summarize/ecco-entropy-aware-cache-compression-for-llms.md|전체 요약 보기]]
