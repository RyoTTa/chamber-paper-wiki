---
tags: [paper, 2018, 2018MICRO, topic/compression, topic/dram, topic/llm-inference]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/permdnn-efficient-compressed-dnn-architecture-with-permuted-diagonal-matrices.md"
---

# PERM DNN: Efficient Compressed DNN Architecture with Permuted Diagonal Matrices

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Chunhua Deng (City University of New York / Rutgers University), Keshab K. Parhi (University of Minnesota), Siyu Liao (City University of New York / Rutgers University), Xuehai Qian (University of Southern California), Yi Xie (City University of New York / Rutgers University), Bo Yuan (City University of New York / Rutgers University)

## 개요

- DNN 모델 크기의 지속적 증가로 에너지 효율적인 하드웨어 실행이 주요 과제
- 오프칩 DRAM은 온칩 SRAM 대비 100배 이상의 에너지 비용 → 모델 압축이 필수적
- **기존 네트워크 희소화(Sparsity) 방식의 한계:**
  - 비정형(Irregular) 희소 구조 → 인덱싱 오버헤드, 하드웨어 비효율
  - 휴리스틱(Heuristic) 특성 → 압축률 제어 불가능
  - 사전 훈련된 모델의 반복적 프루닝+재훈련 필요 → 학습 비용 큼
- **CIRCNN(순환 행렬 기반) 방식의 한계:**
  - FFT 기반 곱셈으로 복잡한 산술 연산 필요
  - 압축률 유연성 제한 (2^t 크기의 순환 행렬로 제한)
  - 입력 희소성(inout sparsity)을 활용하지 못함
- 기존 EIE(Efficient Inference Engine)는 인덱싱 오버헤드와 부하 불균형으로 성능 제한

## 방법론

### 3.1. 블록-순열 대각 행렬

- 가중치 행렬 W ∈ R^(m×n)을 k×k 블록으로 분할
- 각 블록을 순열 대각 행렬로 변환: 모든 비영 항목이 대각선에 위치
- 순열 대각 행렬의 k×k 블록은 k개의 가중치만 저장 → k배 압축
- 행렬-벡터 곱셈: 단순 요소별 곱셈으로 연산 복잡도 O(k) vs O(k^2)

### 3.2. PERM DNN 추론 엔진

- 다중 PE(Processing Element) 아키텍처로 FC(Fully-Connected) 레이어 가속
- **PE 구성:** 각 PE에 8개의 곱셈기, 고유한 순열 대각 블록 담당
- **스케일러빌리티:** PE 수를 조절하여 다양한 모델 크기에 대응
- **유연성:** 임의 크기의 순열 대각 행렬 지원 (CIRCNN의 2^t 제한 없음)
- 인덱싱 오버헤드 없음: 비영 항목 위치가 구조적으로 고정됨
- 부하 균형 유지: 모든 PE가 동일한 수의 연산 수행

### 3.3. 입력 희소성 활용

- PERM DNN은 시간 영역(time-domain) 입력 벡터의 희소성을 직접 활용 가능
- CIRCNN은 주파수 영역 입력만 처리 가능 → 시간 영역 희소성 손실
- 비영 입력 요소에 대해서만 곱셈 수행 → 추가적인 처리량/에너지 효율 향상

### 3.4. 학습 방식

- 구조화된 희소 모델을 처음부터 학습 (pruning 불필요)
- 순열 대각 행렬 구조를 유지하면서 역전파 및 가중치 업데이트
- 다양한 데이터셋(CIFAR-10, CIFAR-100, Tiny ImageNet, Speech Commands)에서 높은 정확도 달성

## 핵심 기여

- 순열 대각 행렬이라는 새로운 구조화된 희소 표현으로 DNN 압축의 세 가지 핵심 과제(비정형성, 휴리스틱, 인덱싱 오버헤드)를 해결
- 기존 최첨단 EIE 대비 3.3~4.8배 처리량, 2.8~4.0배 에너지 효율 향상
- CIRCNN 대비 11.51배 처리량 향상으로 구조화된 행렬 기반 압축의 실용성 입증
- 입력 희소성 활용이라는 추가적인 최적화 기회를 제공

## 주요 결과

- **기술 노드:** CMOS 28nm
- **설계:** 32-PE 설계, 클럭 주파수 1.2GHz
- **소비 전력:** 703.4mW
- **면적:** 8.85mm²
- **처리 능력:** 614.4 GOPS (압축 모델 기준) ≈ 14.74 TOPS (비압축 기준)
- **각 PE:** 8개의 곱셈기 탑재

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/permdnn-efficient-compressed-dnn-architecture-with-permuted-diagonal-matrices.md|전체 요약 보기]]
