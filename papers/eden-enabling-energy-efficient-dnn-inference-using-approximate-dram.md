---
tags: [paper, 2019, 2019MICRO, topic/cache, topic/dram, topic/gpu, topic/llm-inference, topic/pim]
venue: "The 52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO-52), 2019"
year: 2019
summary_path: "../paper-summaries/2019MICRO-summarize/eden_enabling_energy-efficient_dnn_inference_using_approximate_dram.md"
---

# EDEN: Enabling Energy-Efficient, High-Performance Deep Neural Network Inference Using Approximate DRAM

**Venue:** The 52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO-52), 2019
**저자:** Skanda Koppula, Lois Orosa, A. Giray Yağlıkçı, Roknoddin Azizi, Taha Shahroodi, Konstantinos Kanellopoulos, Onur Mutlu (ETH Zürich)

## 개요

- DNN(Depth Neural Network)은 컴퓨터 비전, 음성 인식, 언어 번역 등에서 광범위하게 사용되지만, 높은 연산 및 메모리 요구 사항으로 인해 에너지 효율성과 성능 확보가 어려움.
- 주 메인 메모리(DRAM)가 시스템 에너지 소비의 상당 부분을 차지하며, 선행 연구에 따르면 DNN 가속기 시스템에서 DRAM이 시스템 에너지의 30~80%를 소비함.
- DRAM 접근 지연 시간도 큰 문제: LLC miss 시 L1 cache hit 대비 최대 100배 이상의 지연 시간 발생.
- 최신 DNN 모델의 파라미터 수가 급격히 증가하는 추세 (ResNeXt: 837M FP32 파라미터 = 3.3GB, AlexNet 대비 13.5배). 일부 모델은 10억 파라미터를 초과.
- 기존 접근법의 한계: 1) 수치 비트 폭 축소, 가중치 재사용 등 알고리즘적 최적화, 2) 저에너지/저지연 신규 DRAM 설계, 3) Processing-in-Memory 접근법 — 모두 기존 DRAM 칩의 동작 매개변수를 변경하지 않는 접근.

## 방법론

### 3.1. DNN 재훈련 메커니즘 (Curricular Retraining)

- 대상 approximate DRAM 장치의 오류 특성에 맞춰 DNN을 재훈련하여 오류 내성(error resiliency)을 한 차례(order of magnitude) 향상.
- Curriculum learning 방식 적용: 낮은 비트 오류율(BER)에서 시작하여 점진적으로 높은 BER로 학습 진행.
- 단일 비트 오류가 부동소수점 값의 지수 비트(exponent bits)에 발생하면 정확도 붕괴(collapse) 가능 → implausible value 보정 메커니즘 적용 (임계값 범위 외 값을 0으로 설정).

### 3.2. DNN 데이터 유형별 오류 내성 특성화

- DNN의 각 데이터 유형(가중치, 활성화, 출력 등)이 서로 다른 오류 내성 수준 보유.
- 알고리즘 1의 Fine-grained Mapping: DNN 데이터를 오류 내성 기준으로 정렬한 후, 각 데이터 유형의 허용 BER보다 낮은 BER을 가진 DRAM 파티션에 매핑.
- DRAM 파티션은 chip, rank, bank, 또는 subarray 수준의 세밀한(granularity) 분할 지원.

### 3.3. 오류 모델 (Error Models)

- **Error Model 0:** DRAM bank 전체에 균일한 무작위 분포의 비트 오류 (약화된 셀에서의 제조 공정 변동).
- **Error Model 1:** 비트라인(bitline)을 따라 수직 분포의 비트 오류 (센스 앰플리파이어 간 공정 변동 + 디자인 유도 지연 변동).
- **Error Model 2:** 워드라인(wordline)을 따라 수평 분포의 비트 오류 (DRAM 행 간 공정 변동).
- **Error Model 3:** 셀 내용에 의존하는 데이터 종속 오류 모델 (0→1 비트 전환 확률이 더 높음).
- 각 모델은 실제 DDR3/DDR4 DRAM 모듈의 SoftMC 기반 특성화 데이터를 기반으로 매개변수화 가능.

### 3.4. DNN-to-DRAM 매핑 알고리즘

```
Algorithm 1: Fine-grained DNN to DRAM Mapping
1. DNN 데이터를 오류 내성 기준으로 정렬 (sorted_data)
2. 각 (target_BER, DNN_data)에 대해:
   a. DRAM 파티션 순회
   b. 파티션의 BER이 target_BER 이하인지 확인
   c. 파티션에 충분한 공간이 있는지 확인
   d. 가장 큰 매개변수 감소를 가진 파티션 선택
   e. 해당 파티션에 DNN 데이터 할당
3. 최종 매핑 반환
```

### 3.5. EDEN Offloading

- 대상 approximate DRAM 장치가 사용 불가능한 경우(예: 사전 프로덕션 단계), 다른 시스템에서 EDEN 프레임워크 실행 가능.
- 핵심 과제: 대상 approximate DRAM이 주입하는 오류를 정직하게(emulate) 재현하는 것.
- 네 가지 오류 모델을 사용하여 대상 장치의 오류 패턴을 재현.

## 핵심 기여

- **핵심 Contribution:** 최초로 상용 DRAM의 approximate 동작을 DNN 추론에 적용하는 일반적 프레임워크인 EDEN을 제안.
- **성능 향상:** 원본 정확도 1% 이내 유지 조건에서 DRAM 에너지 21~37% 절감, 최대 17% speedup 달성.
- **실용성:** EDEN은 DNN 추론 하드웨어 수정 없이 적용 가능하며, 다양한 하드웨어 플랫폼(CPU, GPU, 가속기)에서 효과적.
- **의의:** 메모리 에너지/지연 문제를 하드웨어 변경이 아닌 기존 DRAM 칩의 매개변수 조정으로 해결하는 새로운 패러다임 제시. 향후 DNN 추론 시스템의 에너지 효율성 향상에 기여.

## 주요 결과

- 구현 언어: C/C++, CUDA (GPU 실험용)
- 실험 플랫폼: ZSim 기반 마이크로아키텍처 시뮬레이터 + SoftMC 기반 실제 DRAM 특성화
- 대상 하드웨어: 멀티코어 CPU, GPU, 두 가지 DNN 가속기 아키텍처
- EDEN은 DNN 추론 하드웨어, 프레임워크, 또는 알고리즘 수정 불필요 (implausible value 보정만 추가).
- 코arse-grained 매핑: BIOS에서 Vdd/tRCD/tRP 변경 가능. Fine-grained 매핑: 메모리 컨트롤러 + DRAM 전압 조정 하드웨어 변경 필요.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2019MICRO-summarize/eden_enabling_energy-efficient_dnn_inference_using_approximate_dram.md|전체 요약 보기]]
