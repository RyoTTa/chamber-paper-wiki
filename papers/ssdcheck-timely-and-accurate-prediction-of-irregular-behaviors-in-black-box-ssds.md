---
tags: [paper, 2018, 2018MICRO, topic/storage]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/ssdcheck-timely-and-accurate-prediction-of-irregular-behaviors-in-black-box-ssds.md"
---

# SSDcheck: Timely and Accurate Prediction of Irregular Behaviors in Black-Box SSDs

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Joonsung Kim, Pyeongsu Park (Seoul National University), Jaehyung Ahn, Jihun Kim, Jong Kim (POSTECH), Jangwoo Kim (Seoul National University)

## 개요

- 현대 서버는 성능, 신뢰성, 에너지 효율성으로 인해 SSD를 주요 스토리지 디바이스로 적극 도입.
- **SSD의 불규칙한 동작 문제:** SSD는 단순한 빠른 스토리지가 아닌, 임베디드 프로세서와 다양한 하드웨어 유닛(NAND 플래시, 채널 등)으로 구성된 복잡한 컴퓨터 시스템.
- **블랙박스 특성:** SSD 내부 구조와 디바이스별 최적화는 독점 자산(proprietary asset)으로 사용자에게 공개되지 않음.
- **예측 불가능한 접근 지연 시간:**
  - 디바이스 내(intra-SSD): 최대 100배의 지연 시간 변동 발생.
  - 디바이스 간(inter-SSD): 서로 다른 SSD 간 성능 차이가 큼.
- **QoS 만족 실패:** 불규칙한 접근 지연 시간으로 인해 서버 아키텍트가 핵심 품질 서비스(QoS) 요구사항을 만족하지 못함.
- **성능 잠재력 미활용:** 불규칙한 성능 변동으로 상용 SSD의 최대 성능을 발휘하지 못함.
- **기존 모델의 한계:** HDD의 지연 시간 모델은 쉽게 구성 가능하지만, SSD의 복잡한 내부 동작으로 인해 정확한 성능 모델 구축이 극히 어려움.

## 방법론

### 3.1. 핵심 기능 분석

- **재구성 가능한 SSD 디바이스 구축:** 다양한 성능 민감한 기능을 구현하고 성능 측정 유닛을 통합.
- **프로파일링 및 아키텍처 분석:** 광범위한 실험을 통해 지연 시간에 가장 큰 영향을 미치는 두 가지 핵심 기능 식별:
  1. **Write Buffer (WB):** 쓰기 요청을 임시 저장하여 지연 시간 감소.
  2. **Garbage Collection (GC):** NAND 플래시 셀에서 유효하지 않은 블록을 정리하는 과정에서 지연 시간 증가 유발.

### 3.2. 일반 SSD 성능 모델

- **WB 기반 지연 시간 예측:**
  - 쓰기 버퍼에 여유 공간이 있는 경우: 지연 시간 짧음.
  - 쓰기 버퍼가 가득 찬 경우: 지연 시간 급증.
- **GC 기반 지연 시간 예측:**
  - GC 발생 시 추가 지연 시간 발생.
  - GC 발생 빈도 및 지속 시간 예측.

### 3.3. 진단 코드 스니펫

- **목표:** 애플리케이션 실행 전에 타겟 SSD의 정적 특성을 추출.
- **추출 파라미터:**
  - 내부 볼륨 존재 여부
  - 쓰기 버퍼 크기
  - 버퍼 플러시 알고리즘
  - GC 트리거 임계값
- **동작 방식:** 짧은 진단 코드를 실행하여 SSD의 반응을 관찰하고 특성을 추론.

### 3.4. 동적 성능 모델 관리

- **런타임 모니터링:** 입출력 요청을 모니터링하여 SSD의 현재 상태를 추정.
- **상태 추적:** WB 상태, GC 발생 여부 등을 동적으로 추적.
- **지연 시간 예측:** 현재 상태와 일반 모델을 기반으로 다음 접근의 지연 시간 예측.
- **모델 보정:** 예측 오차가 커지면 모델 파라미터를 보정.

## 핵심 기여

- **핵심 기여:** SSDcheck — 블랙박스 SSD의 다음 접근 지연 시간을 정확하게 예측하는 소프트웨어 기반 성능 모델.
- **예측 정확도:** 일반 지연 시간 **98.96%**, 높은 지연 시간 **79.96%** 달성.
- **실용성:** 하드웨어 변경 없이 상용 SSD에 적용 가능, 모델 범위 벗어나면 무해하게 비활성화.
- **성능 개선:** 
  - 볼륨 관리자(VA-LVM): 처리량 **4.29×** 향상, 테일 지연 시간 **6.53%**로 감소.
  - I/O 스케줄러(PAS): 처리량 **44.0%** 향상, 테일 지연 시간 **26.9%**로 감소.
- **의의:** SSD의 불규칙한 동작을 정확하게 예측하여 QoS와 성능을 동시에 개선한 최초의 방법. 블랙박스 SSD의 성능 모델링 문제를 해결하는 실용적인 접근법 제시.

## 주요 결과

- **구현 언어:** C/C++ (커널 모듈 및 사용자 레벨 라이브러리)
- **시스템 구성:**
  - 진단 코드 스니펫 실행 모듈
  - 성능 모델 관리 모듈
  - 런타임 모니터링 모듈
- **하드웨어 수정 불필요:** 소프트웨어 기반 솔루션으로 상용 SSD에 하드웨어 변경 없이 적용 가능.
- **호환성:** 모델 범위를 벗어나는 SSD에는 무해하게 비활성화.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/ssdcheck-timely-and-accurate-prediction-of-irregular-behaviors-in-black-box-ssds.md|전체 요약 보기]]
