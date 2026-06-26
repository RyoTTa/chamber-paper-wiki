---
tags: [paper, 2025, 2025ISCA, topic/gpu, topic/llm-inference]
venue: "ISCA '25 (52nd Annual International Symposium on Computer Architecture), June 21–25, 2025, Tokyo, Japan"
year: 2025
summary_path: "../paper-summaries/2025ISCA-summarize/specee-accelerating-llm-with-speculative-early-exiting.md"
---

# SpecEE: Accelerating Large Language Model Inference with Speculative Early Exiting

**Venue:** ISCA '25 (52nd Annual International Symposium on Computer Architecture), June 21–25, 2025, Tokyo, Japan
**저자:** Jiaming Xu, Jiayi Pan, Yongkang Zhou, Siming Chen, Jinhao Li, Yaoxiu Lian, Junyi Wu, Guohao Dai

## 개요

- LLM 추론 시 디코더 레이어가 end-to-end 추론 시간의 70~95%를 차지 → 기존 가속 기법(양자화, 프루닝 등)으로는 Pareto 전선을 충분히 전진시키지 못함
- **Early exiting의 검색 공간 문제:** LLM 어휘(vocabulary)가 온라인 검색 공간으로 작동 → Llama2 기준 ~3×10⁴ 토큰 어휘 크기가 예측기(predictor) 부하에 직접적 영향 (전체 추론 지연의 ~20%)
- **기존 예측기의 비효율:** AdaInfer는 SVM 사용, 고차원 입력(~5×10³)에 특성 분석 없음 → ~30% 전체 연산, ~15% 추론 지연
- **레이어별 예측기 배포의 비효율:** 모든 디코더 레이어에 균일하게 예측기 배포 → 성공 확률의 왜곡된 분포(skewed distribution)로 대부분의 예측기 계산이 비효율적 (~20% 추가 오버헤드)
- **추측 디코딩과의 결합 문제:** 토큰 트리의 각 토큰을 독립적 검색 공간으로 취급 → 지수적 복잡도로 high-throughput 이점 통합 실패

## 방법론

### 3.1. 추측 기반 경량 예측기 설계 (Tech-1)

- **Feature 선택:** 추측 토큰 로짓(logits), 로컬 확률(local probabilities), 확률 변이(probability variation)의 3가지 특성 사용
  - 추측 토큰 로짓: hidden_states와 speculative_lm_head의 행렬곱으로 LLM의 추측 토큰에 대한 신뢰도 제공
  - 로컬 확률: softmax로 변환된局部 정보 기반 확률
  - 확률 변이: 이전 레이어 대비 현재 레이어의 확률 변화량
- **판단 메커니즘:** 2MLP (은닉 차원 512) 사용 → SVM 대비 ~100배 파라미터/FLOPS 감소
  - ReLU 활성화 함수, 출력층 Sigmoid로 이진 분류
  - 추측 모델이 4개 토큰 생성 시 입력 차원 12 (4×3)
- **검증 알고리즘:** 전체 lm_head로 글로벌 토큰 로짓 계산 후 추측 토큰에 존재 여부 확인 → 정확도 보장
- **설계 공간 탐색:** 2MLP, 은닉 차원 512에서 최적 정확도-실행 시간 트레이드오프 달성

### 3.2. Two-level 휴리스틱 예측기 스케줄링 (Tech-2)

- **왜곡된 분포(Skewed Distribution):** 레이어별 exit 확률이 하위 50%에 해당하는 레이어들의 확률 합이 전체의 20% 미만 → 많은 레이어에서 예측기 계산 불필요
- **컨텍스트 유사성(Context Similarity):** 이전 5개 토큰의 exit 레이어 근처(±2 레이어)에 현재 토큰의 exit 레이어가 존재할 확률 ~80%
- **오프라인 스케줄링:** LLM별로 모든 예측기를 통합하여 추론 수행 후 레이어별 활성화 빈도를 순위화 → 모델 설정 파라미터로 저장 (한 번만 수행)
- **온라인 스케줄링:** 런타임에서 circular queue(길이 5)로 이전 토큰들의 exit 레이어 위치를 추적 → 컨텍스트 유사성을 활용하여 예측기 위치 동적 결정
- **효과:** ~68% 예측기 감소, ~1.21x 추론 가속 (평균 ~10.2 레이어에 예측기 배포)

### 3.3. 컨텍스트 인식 병합 맵핑 (Tech-3)

- **추측 디코딩과의 결합:** 토큰 트리의 각 경로를 하나의 하이퍼토큰(hyper-token)으로 병합 → 지수적 매핑 복잡도를 선형으로 변환
- **Cannikin Law 적용:** 토큰 시퀀스의 exit 위치는 시퀀스 내 가장 늦은 위치로 결정 → 하이퍼토큰으로 병합하면 컨텍스트 의존성이 활용됨
- **GPU 구현:** MegaBlocks의 block-wise GEMM과 cutlass의 그룹 GEMM 구현을 기반으로 커스텀 GPU 오퍼레이터 개발
- **효과:** 1.66x 추론 가속 달성
- **직교 가속 기법 통합:** 양자화(AWQ), 희소 활성화(PowerInfer) 등 기존 가속 기법과 결합 가능 → Pareto 전선 추가 전진

## 핵심 기여

- **핵심 기여:** 추측 모델을 이용한 어휘 검색 공간 축소라는 새로운 패러다임 제시 → LLM 가속에 새로운 관점 제공
- **성능:** 클라우드에서 **2.25x**, PC에서 **2.43x** speedup 달성 (Llama2-7B)
- **정확도:** **<1%** 정확도 손실로 기존 모델 성능 유지
- **범용성:** 모든 LLM에 적용 가능, 사전 학습 오버헤드 미미, 기존 가속 기법(양자화, 희소화)과 직교적으로 결합 가능
- **실용성:** 오프라인 학습 한 번만 필요, 메모리 오버헤드 미미 (~416KB 예측기), 에너지 효율 ~1.57x 향상

## 주요 결과

- **구현 언어:** Python (PyTorch 프론트엔드), C++/CUDA 백엔드
- **하드웨어 플랫폼:**
  - 클라우드: NVIDIA Tesla A100-80GB, NVIDIA RTX 4090-24GB
  - PC: Lenovo Legion Y7000 (Intel i7-13650HX, NVIDIA RTX 4060 Laptop 8GB)
- **추측 모델:** EAGLE의 DLM 사용 (Llama2-7B 기준 ~24시간 RTX 3090에서 학습)
- **예측기 파라미터:** Llama2-7B 기준 총 ~416KB (12×512+512×1)×32×4/1024
- **오프라인 학습:** MT-Bench 데이터셋으로 ~16K 학습 데이터 생성, 예측기별 ~1시간 (A100), 전체 ~10분, ~2% 데이터로 충분한 성능

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]


## 전체 요약

[[../paper-summaries/2025ISCA-summarize/specee-accelerating-llm-with-speculative-early-exiting.md|전체 요약 보기]]
