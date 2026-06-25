---
tags: [paper, 2018, 2018MICRO, topic/storage, topic/flash]
venue: "MICRO 2018"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/invalid-data-aware-coding-to-enhance-the-read-performance-of-high-density-flash-memories.md"
---

# Invalid Data-Aware Coding to Enhance the Read Performance of High-Density Flash Memories

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Wonil Choi, Myoungsoo Jung, Mahmut Kandemir (Pennsylvania State University, Yonsei University)

## 개요

고비트 밀도 플래시(MLC, TLC, QLC)는 읽기 성능 변동 문제를 가짐. TLC 셀의 LSB, CSB, MSB 읽기 지연 시간이 서로 다르며, 기존 코딩에서는 LSB가 무효화되어도 CSB/MSB 읽기 지연 시간이 줄어들지 않음. 이 논문은 비트 무효화 시 읽기 지연 시간을 감소시키는 IDA(Invalid Data-Aware) 코딩을 제시.

## 방법론

### IDA 코딩 원리
- **전압 조정(Voltage Adjustment):** 비트 무효화 시 중복 전압 상태를 병합하여 감지 전압 수 감소
- **효과:** MSB 읽기 4회→1-2회, CSB 읽기 2회→1회 액세스로 감소
- **범용성:** MLC, TLC, QLC 등 고비트 밀도 플래시에 일반적으로 적용 가능

### 데이터 리프레시 통합
- **데이터 리프레시:** SSD의 기본 연산 - 데이터 읽기→오류 정정→새 블록에 기록
- **통합 방식:** 전압 조정 시간을 리프레시 과정에 은폐
- **이점:** 성능/신뢰성 오버헤드 없이 IDA 코딩 적용 가능

## 핵심 기여

- 고비트 밀도 플래시의 읽기 성능 변동 문제를 해결하는 IDA 코딩 최초 제시
- 전압 조정으로 읽기 지연 시간 대폭 감소
- 데이터 리프레시와의 통합으로 오버헤드 완전 은폐
- TLC, MLC 등 다양한 고비트 밀도 플래시에서 효과 입증

## 주요 결과

- TLC에서 읽기 응답 시간 **평균 28% 향상**
- MLC에서도 **14.5% 읽기 성능 향상**
- 다양한 메모리 타이밍 파라미터에서도 효과적
- 신뢰성 저하 없이 성능 향상 달성

## 한계점

- 쓰기 중심 워크로드에서는 효과 제한적
- 전압 조정의 정밀도와 신뢰성에 대한 추가 연구 필요
- 실제 상용 SSD에서의 검증 필요

## 관련 개념

- [[paper-wiki/concepts/storage.md|Storage]]

## 전체 요약

[[../paper-summaries/2018MICRO-summarize/invalid-data-aware-coding-to-enhance-the-read-performance-of-high-density-flash-memories.md|전체 요약 보기]]
