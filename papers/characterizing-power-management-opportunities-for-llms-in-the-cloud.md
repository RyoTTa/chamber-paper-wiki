---
tags: [paper, 2024, 2024ASPLOS, topic/cache, topic/gpu, topic/llm-inference]
venue: "29th ACM International Conference on Architectural Support for Programming Languages and Operating Systems, Volume 3 (ASPLOS '24), April 27-May 1, 2024"
year: 2024
summary_path: "../paper-summaries/2024ASPLOS-summarize/characterizing-power-management-opportunities-for-llms-in-the-cloud.md"
---

# Characterizing Power Management Opportunities for LLMs in the Cloud

**Venue:** 29th ACM International Conference on Architectural Support for Programming Languages and Operating Systems, Volume 3 (ASPLOS '24), April 27-May 1, 2024
**저자:** Pratyush Patel, Esha Choukse, Chaojie Zhang, Íñigo Goiri, Brijesh Warrier, Nithish Mahalingam, Ricardo Bianchini (University of Washington, Microsoft Azure)

## 개요

- 클라우드 제공업체와 기업들이 LLM 수요 급증으로 대규모 GPU 클러스터 구축에 막대한 투자를 하고 있으나, 데이터센터 건설은 비용이 많이 들고 시간이 오래 걸려 즉각적인 수요 충족이 어려움
- 데이터센터의 주요 병목 자원은 전력(power)으로, LLM의 모델 크기 급증으로 전력 소비가 빠르게 증가하고 있음
- GPU 서버는 피크 전력으로 프로비저닝하는 것이 일반적: (1) GPU는 최대 FLOPS를 위해 설계되어 피크 전력 도달이 빈번, (2) 클라우드 서버는 어떤 워크로드든 실행할 수 있어 최악의 경우를 대비해야 함
- 기존 CPU 클러스터는 다양한 전력 관리 기법(derating, workload-aware power capping 등)을 활용하고 있으나, LLM 클러스터는 GPU의 비표준적이고 느린 OOB(Out-of-Band) 관리 인터페이스로 인해 효과적인 전력 관리가 어려움
- 기존 연구들의 한계: 가상화 환경에서 GPU의 텔레메트리와 제어 인터페이스가 제한적이며, SMBPBI와 같은 OOB 인터페이스는 단일 서버에서 최대 40초가 소요되어 UPS의 10초 전력 캡핑 데드라인을 충족하기 어려움

## 방법론

### 3.1. LLM 학습 특성화

- **피크 전력:** 학습 반복(iteration) 동안 GPU 전력이 TDP에 도달하거나 초과 (GPT-NeoX, Flan-T5는 TDP 초과)
- **전력 스윙(Power Swings):** 각 반복에서 계산密集相과 통신密集相이 교대로 발생하며 큰 전력 변동 발생
  - RoBERTa: 반복 경계에서 TDP의 75% 수준 유지
  - GPT-NeoX: TDP의 50%까지 하락
  - Flan-T5: 유휴 전력 수준까지 하락
  - 대규모 학습에서는 수천 개 GPU에서 전력 스윙이 상관되어 전력 전달 인프라에 큰 부하
- **캡핑 효과:** 주파수 잠금(frequency locking)과 전력 캡핑(power capping) 모두 피크 전력 최대 20% 절감 가능
  - 전력 캡핑은 피크를 낮추면서 트러프(trough)를 높여 전력 스윙 완화에 효과적
  - 주파수 잠금은 전체 전력 소비를 낮추어 요구 시 전력 회수에 효과적

### 3.2. LLM 추론 특성화

- **프롬프트/토큰 단계 분리:** LLM 추론은 두 가지 명확한 전력 소비 단계로 구분
  - **프롬프트 처리(Prompt Processing):** 병렬로 모든 입력 토큰 처리, 높은 연산 집약적 → 피크 전력 TDP 초과 (짧은 시간)
  - **토큰 샘플링(Token Sampling):** 순차적 오토레그레시브 생성, KV-cache 활용 → 낮고 안정적 전력 (긴 시간)
  - Figure 6: 모든 모델에서 프롬프트 단계의 급격한 전력 스파이크와 토큰 단계의 안정적 저전력 패턴 확인
- **입력 크기 영향:** 입력 크기 증가 시 피크 전력 급격히 증가 (프롬프트 연산 증가), 평균 전력은 안정적 유지
- **배치 크기 영향:** 배치 크기 증가는 피크/평균 전력 모두 증가 (병렬 처리 효율 증가)
- **출력 크기 영향:** 출력 크기는 전력에 거의 영향 없음, 다만 실행 시간을 선형적으로 증가
- **데이터 타입 영향:** FP16 양자화는 텐서 코어 활용으로 더 높은 피크 전력이나 더 빠른 성능; 모델 크기 감소로 적은 서버로 동일 워크로드 처리 가능

### 3.3. 클러스터 레벨 전력 패턴

- **학습 vs 추론 비교 (Table 4):**
  - 학습: 피크 전력 97%, 2초 내 최대 37.5% 전력 스윙
  - 추론: 피크 전력 79%, 2초 내 최대 9% 전력 스윙
  - 추론은 일일적(diurnal) 패턴이나 단기적으로는 안정적
- **GPU 비중:** GPU가 서버 전력의 약 60%를 차지하며, 피크 GPU 전력은 전체 서버 GPU TDP를 최대 500W 초과
- **핵심 통찰:** 추론 클러스터는 프롬프트/토큰 단계의 통계적 멀티플렉싱으로 인해 학습 클러스터보다 훨씬 더 많은 전력 오버스크립션 여유

## 핵심 기여

- **핵심 기여:** LLM 학습/추론의 전력 소비 패턴에 대한 최초의 체계적 특성화 및 프로덕션 검증
- **핵심 발견:** 추론 클러스터는 통계적 멀티플렉싱으로 인해 상당한 전력 오버스크립션 여유(21%) 보유, 학습 클러스터는 3%에 불과
- **실용적 프레임워크:** POLCA를 통해 기존 클러스터에 30% 더 많은 서버 배포 가능, 전력 브레이크 0건
- **GPU 전력 관리:** GPU가 서버 전력의 60%를 차지하므로 GPU 전력 관리가 LLM 클러스터 관리의 핵심
- **OOB 인터페이스 개선 필요:** 현재 GPU OOB 인터페이스(40초 지연)는 비표준적이고 느려, 향후 표준화와 속도 개선이 필요
- **의의:** LLM 추론 클러스터의 전력 효율성을 체계적으로 분석하고, 프로덕션 수준에서 검증된 전력 오버스크립션 프레임워크를 제시하여 데이터센터 비용 절감과 수용 능력 확대에 기여

## 주요 결과

### 4.1. 설계 목표

- 단순성과 구성 가능성: 프로덕션 배포에 적합한 간단하고 신뢰할 수 있는 정책
- 워크로드 우선순위 지원: 지연 시간에 민감한 워크로드(검색)와 덜 민감한 워크로드(요약, 코드 생성) 차등 처리
- 지연 시간 제약 조건 내 설계: OOB 인터페이스의 40초 지연을 고려한 안전장치 포함

### 4.2. 이중 임계값 정책 (Two-Threshold Policy)

- **하한 임계값 T1 (80%):** 저우선순위 워크로드에 대해 주파수 캡핑 (1275 MHz, A100 기본 주파수)
- **상한 임계값 T2 (89%):** 저우선 추가 캡핑 (1110 MHz) + 고우선순위 워크로드 캡핑 (1305 MHz, 성능 영향 미미)
- **전력 브레이크:** 안전망으로 모든 GPU를 288MHz로 급격히 캡핑 (10초 UPS 데드라인 충족)
- 임계값 간 5% 이상 차이를 유지하여 히스테리시스(hysteresis) 방지

### 4.3. 평가 결과

- 6주 간 프로덕션 추론 클러스터 트레이스 기반 시뮬레이션
- **30% 더 많은 서버** 배포 가능 (기존 대비)
- 고우선순위 워크로드의 P50 지연 시간 영향 < 1%, P99 < 5%
- 저우선순위 워크로드의 P50 지연 시간 영향 < 5%
- 전력 브레이크 이벤트 0건 달성
- 기존 기법 대비 비교:
  - 단일 임계값(저우선): 저우선 SLO 미충족
  - 단일 임계값(전체): 양쪽 모두 P99 SLO 위반
  - 캡핑 없음: 전력 브레이크 보호 부재, 모델 전력 변화에 취약

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]


## 전체 요약

[[../paper-summaries/2024ASPLOS-summarize/characterizing-power-management-opportunities-for-llms-in-the-cloud.md|전체 요약 보기]]
