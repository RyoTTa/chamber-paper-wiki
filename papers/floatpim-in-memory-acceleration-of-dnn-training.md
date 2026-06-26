---
tags: [paper, 2019, 2019ISCA, topic/gpu, topic/llm-inference, topic/nvm, topic/pim]
venue: "The 46th Annual International Symposium on Computer Architecture (ISCA '19)"
year: 2019
summary_path: "../paper-summaries/2019ISCA-summarize/floatpim-in-memory-acceleration-of-deep-neural-network-training.md"
---

# FloatPIM: In-Memory Acceleration of Deep Neural Network Training

**Venue:** The 46th Annual International Symposium on Computer Architecture (ISCA '19)
**저자:** Mohsen Imani (UC San Diego), Saransh Gupta (UC San Diego), Yeseong Kim (UC San Diego), Tajana Rosing (UC San Diego)

## 개요

- 딥러닝(DNN) 학습은 대용량 데이터와 대규모 행렬 연산을 요구하며, 기존 GPU 기반 구현은 **데이터 이동(data movement) 병목**에 직면
- 학습 과정에서 중간 뉴런 값(activation)과 가중치(weight)가 끊임없이 메모리-프로세서 간 주고받으며, 특히 **대용량 데이터셋(ImageNet 등)** 학습 시 GPU 메모리 용량 부족으로 디스크 스와핑이 발생하여 학습 속도가 크게 저하
- 기존 PIM(Processing-in-Memory) 기반 DNN 가속기는 대부분 **추론(inference)에만 특화**되어 있으며, 학습을 지원하는 설계가 부재
- 기존 PIM 가속기의 한계:
  - **ISAAC**: 아날로그 기반 설계로 ADC/DAC 비용이 크고, 고정밀도(fixed-point) 연산만 지원 → 학습 정확도 저하 (최대 5.1% 하락)
  - **PipeLayer**: 스파이크 기반 고정밀도 연산 한계, 인접 블록 간 데이터 이동 비용 높음
- 부동소수점(floating point) 연산은 DNN 학습 정확도에 필수적이나, 기존 PIM 아키텍처에서는 ** 메모리 내 부동소수점 연산을 처음으로 구현하지 못함

## 방법론

### 3.1. 메모리 블록 기반 설계

- 전체 아키텍처는 **32개 타일(tile)**로 구성, 각 타일은 **256개 메모리 블록**을 포함
- 각 메모리 블록은 1K×1K 크로스바 배열(Array)을 기반으로 하며, NOR 연산을 통해 디지털 연산 수행
- 각 블록은 연산 모드와 데이터 전송 모드를 전환하며 동작
- **블록 스케일리빌리티**: 1K×1K 크로스바를 32개 서브블록으로 캐스케이딩하여 1K×32K 크기로 확장 → DNN 레이어 전체를 하나의 블록에서 처리 가능
  - 캐스케이딩 시 실행 시간 3.8% 증가, 에너지 오버헤드 3.4% 이내 (이상적 1K×32K 블록 대비)

### 3.2. 인접 블록 간 인터레이어 통신

- 기존 PIM의 핵심 병목인 블록 간 데이터 이동을 해결하기 위한 **스위치 기반 병렬 전송** 설계
- 각 메모리 블록은 인접 2개 블록과 스위치로 연결
  - **S1 스위치**: 홀수 인덱스 블록 → 짝수 인덱스 블록으로 전송
  - **S2 스위치**: 짝수 인덱스 블록 → 홀수 인덱스 블록으로 전송
- 데이터 전송은 **비트 직렬(bit-serial) 방식**으로 행 병렬(row-parallel) 처리
  - bw 비트 데이터 전송 시 2×bw 사이클 소요 (데이터 양과 무관)
- **파이프라인 구조**:
  - T0 사이클: 모든 블록이 연산 모드로 병렬 동작
  - T1 사이클: 홀수 블록 → 짝수 블록 데이터 전송
  - T2 사이클: 짝수 블록 → 홀수 블록 데이터 전송
  - 비주기적 연결(ResNet 등)도 컨트롤러가 순차적으로 전송하여 처리

### 3.3. 부동소수점 곱셈 구현

- IEEE 754 부동소수점 곱셈 3단계:
  1. **부호 비트 XOR**: 6 사이클 소요
  2. **지수 비트 덧셈**: NOR 연산 기반, 13×Ne 사이클 (Ne = 지수 비트 수)
  3. **가수비트(mantissa) 고정소수점 곱셈**: NOR 연산 기반
- 전체 곱셈 지연 시간: `TMul = (12Ne + 6.5Nm² − 7.5Nm − 2) × TNOR`
- 에너지: `EMul = (12Ne + 6.5Nm² − 7.5Nm − 2) × ENOR`
- 모든 행에서 병렬로 연산 가능

### 3.4. 부동소수점 덧셈 구현

- 기존 방식의 한계: 지수 차이에 따른 가수비트 시프팅이 병렬화 어려움
- **정확한 탐색(exact search) 기반 혁신적 접근**:
  1. 두 피연산자의 지수 차이(exp') 계산 → NOR 기반 고정소수점 뺄셈
  2. exp'에서 '0'을 탐색하여 더 큰 지수 식별
  3. 더 큰 지수를 가진 수의 가수비트를 tm1에 복사
  4. exp' 범위 내 각 쿼리(qexp)에 대해 시프트된 가수비트를 tm2에 생성
  5. tm1 + tm2 고정소수점 덧셈 수행
  6. 정규화: 캐리 발생 시 오른쪽 1비트 시프트 및 지수 증가
- 전체 덧셈 지연 시간: `TAdd = (3 + 16Ne + 19Nm + Nm²) × TNOR + (2Nm + 1) × Tsearch`

### 3.5. 병렬화 전략

- **피드포워드 병렬화**: 배치(batch) 내 서로 다른 데이터 포인트를 타일별로 병렬 처리
  - 32타일 사용 시 16타일 대비 **1.83× 성능 향상**
- **역전파 병렬화**: 배치 내 데이터 포인트별 병렬 가중치 업데이트
  - FloatPIM-LP(저전력): P=b/8 — 단일 블록에서 소규모 배치 처리
  - FloatPIM-HP(고성능): P=b — 모든 데이터 포인트를 별도 블록에서 병렬 처리
  - P=b/8 → P=b 시 **78.3× 성능 향상** (에너지 15.4% 감소, 메모리 3.9× 증가)

## 핵심 기여

- **핵심 Contribution**: 메모리 내 부동소수점 연산을 최초로 구현한 PIM 기반 DNN 학습 아키텍처 — 기존 PIM의 추론 전용 한계를 극복
- **성능 향상**: 학습에서 GPU 대비 **303×**, 기존 최첨단 PIM(ISAAC/PipeLayer) 대비 **4.3~6.3×**
- **에너지 효율**: 학습에서 GPU 대비 **48.6×**, 테스트에서 **297.9×** 에너지 절감
- **실용적 기여**: 30.64mm² 면적, 62.60W 전력으로 실리콘 수준의 구현 가능성 입증 — 인메모리 컴퓨팅의 DNN 학습 적용을 위한 기반 기술 확립

## 주요 결과

- **구현 언어/도구**: Tensorflow 기반 사이클 정확 시뮬레이터, HSPICE(회로 레벨 시뮬레이션), SystemVerilog + Synopsys DesignCompiler(컨트롤러 합성)
- **기술 노드**: 28nm
- **소자 모델**: VTEAM 기반忆阻기(memristor) — ON 저항 10kΩ, OFF 저항 10MΩ
- **하드웨어 구성**:
  - 32 타일, 총 8Gb 용량
  - 타일당 면적: 0.96mm², 소비 전력: 7.64mW
  - 전체 면적: **30.64mm²**, 평균 전력: **62.60W**
- **면적 분석**: 95.1%가 크로스바 메모리, 인터컨넥트 0.15%, 스위치 0.24%, 컨트롤러 3.0%
- **내구성 관리**: 가장 활발한 가수비트 저장 컬럼을 시간에 따라 교체 → 디바이스 수명 **약 11× 향상**
  - 10⁹ 내구성 시 3.1×10⁸ 분류 태스크 수행 가능

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2019ISCA-summarize/floatpim-in-memory-acceleration-of-deep-neural-network-training.md|전체 요약 보기]]
