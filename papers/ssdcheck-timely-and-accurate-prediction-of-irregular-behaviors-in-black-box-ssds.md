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
- **SSD의 불규칙한 동작 문제:** SSD는 단순한 빠른 스토리지가 아닌, 임베디드 프로세서와 다양한 하드웨어 유닛으로 구성된 복잡한 컴퓨터 시스템.
- **블랙박스 특성:** SSD 내부 구조와 디바이스별 최적화는 독점 자산(proprietary asset)으로 사용자에게 공개되지 않음.
- **예측 불가능한 접근 지연 시간:** 디바이스 내 최대 100배의 지연 시간 변동 발생.

## 방법론

### 1. 핵심 기능 분석

- **재구성 가능한 SSD 디바이스 구축:** 다양한 성능 민감한 기능을 구현하고 성능 측정 유닛을 통합.
- **프로파일링 및 아키텍처 분석:** 지연 시간에 가장 큰 영향을 미치는 두 가지 핵심 기능 식별:
  1. **Write Buffer (WB):** 쓰기 버퍼링으로 지연 시간 감소.
  2. **Garbage Collection (GC):** 가비지 컬렉션으로 인한 지연 시간 증가.

### 2. 일반 SSD 성능 모델

- **WB 기반 지연 시간 예측:** 쓰기 버퍼에 여유 공간이 있는 경우 지연 시간 짧음, 가득 찬 경우 지연 시간 급증.
- **GC 기반 지연 시간 예측:** GC 발생 시 추가 지연 시간 발생, GC 발생 빈도 및 지속 시간 예측.

### 3. 진단 코드 스니펫

- **목표:** 애플리케이션 실행 전에 타겟 SSD의 정적 특성을 추출.
- **추출 파라미터:** 내부 볼륨 존재 여부, 쓰기 버퍼 크기, 버퍼 플러시 알고리즘, GC 트리거 임계값.

### 4. 동적 성능 모델 관리

- **런타임 모니터링:** 입출력 요청을 모니터링하여 SSD의 현재 상태를 추정.
- **상태 추적:** WB 상태, GC 발생 여부 등을 동적으로 추적.
- **지연 시간 예측:** 현재 상태와 일반 모델을 기반으로 다음 접근의 지연 시간 예측.

## 핵심 기여

- 블랙박스 SSD의 다음 접근 지연 시간을 정확하게 예측하는 소프트웨어 기반 성능 모델.
- 하드웨어 변경 없이 상용 SSD에 적용 가능.
- 일반 지연 시간 **98.96%**, 높은 지연 시간 **79.96%** 예측 정확도 달성.

## 주요 결과

- **예측 정확도:** 일반 지연 시간 **98.96%**, 높은 지연 시간 **79.96%** 달성.
- **볼륨 관리자(VA-LVM):** 처리량 **4.29×** 향상, 테일 지연 시간 **6.53%**로 감소.
- **I/O 스케줄러(PAS):** 처리량 **44.0%** 향상, 테일 지연 시간 **26.9%**로 감소.

## 한계점

- 주로 합성 벤치마크와 제한된 실제 애플리케이션으로 평가.
- 모델 범위를 벗어나는 SSD에는 무해하게 비활성화해야 하므로 범용성 한계.

## 관련 개념

- [[paper-wiki/concepts/storage.md|Storage]]

## 전체 요약

[[../paper-summaries/2018MICRO-summarize/ssdcheck-timely-and-accurate-prediction-of-irregular-behaviors-in-black-box-ssds.md|전체 요약 보기]]