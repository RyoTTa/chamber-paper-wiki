---
tags: [paper, 2018, 2018ISCA, topic/gpu]
venue: "International Symposium on Computer Architecture (ISCA) 2018"
year: 2018
summary_path: "../paper-summaries/2018ISCA-summarize/enabling-scientific-computing-on-memristive-accelerators.md"
---

# Enabling Scientific Computing on Memristive Accelerators

**Venue:** International Symposium on Computer Architecture (ISCA) 2018
**저자:** Ben Feinberg, Uday Kumar Reddy Vengalam, Nathan Whitehair (University of Rochester), Shibo Wang, Engin Ipek (University of Rochester)

## 개요

- 선형 대수(linear algebra)는 과학 및 공학의 거의 모든 분야에서 필수적이며, 하드웨어 가속화를 통한 성능 및 에너지 효율 개선이 필요
- 기존 메모리스트 가속기는 머신러닝에 적합한 8~16비트 연산만 지원하며, 고정밀 부동소수점이 요구되는 과학 기산에는 부적합
- 과학 기산에서의 주요 도전 과제:
  - 머신러닝 워크로드의 느슨한 정밀도 요구사항에 의존한 기존 접근 방식
  - 과학 기산에서 요구하는 IEEE-754 호환 고정밀 부동소수점 연산 지원 부재
  - 희소 행렬 처리의 비효율성
- 기존 가속기들의 한계:
  - FPGA 기반 가속기: GPU 대비 성능 향상 불분명
  - ASIC 기반 가속기: 이중 정밀도 스케일링 불확실
  - 평균 가속도 1.28배 수준으로 제한적

## 방법론

### 3.1. 시스템 조직
- 은행(bank)과 클러스터의 계층적 구조
- 각 은행은 이종 클러스터(다양한 크로스바 크기)와 로컬 프로세서 포함
- 클러스터: 고정된 행렬 블록에 대해 희소 MVM 수행
- 로컬 프로세서: 크로스바가 처리하지 못하는 연산 담당

### 3.2. 크로스바 설계
- 이중 정밀도 부동소수점 계수를 118비트 고정점 피연산자로 변환
  - 53비트 가수(mantissa), 1비트 부호, 최대 64비트 패딩
- 9비트 오류 정정 AN 코드 적용 (최대 127비트 전체 피연산자 폭)
- 127개의 단일 비트 셀을 가진 크로스바로 구성
- 시프트-앤--add 감소 네트워크를 통한 부분 곱 합산

### 3.3. 고정밀 부동소수점 연산
#### 3.3.1. 지수 범위 국소성 활용
- IEEE-754 이중 정밀도: 11비트 지수 필드 (동적 범위 약 10^616)
- 실제 응용에서는 훨씬 작은 동적 범위 필요
- 동일 블록 내 값들만 아날로그 영역에서 합산되므로 정렬 오버헤드 감소
- 수백 비트로 충분한 패딩 (이중 정밀도 최대 2046비트 대비)

#### 3.3.2. 조기 종료(Early Termination)
- 연산 수행 중 IEEE-754 정밀도 요구사항 충족 시 조기 종료
- 부분 곱 합산 과정에서 선행 1(leading 1) 위치 감지
- 안정 영역(stable region), 캐리 영역(carry region), 정렬 영역(aligned region)으로 실행 합 분할
- 배리어 비트를 통한 캐리 전파 방지

#### 3.3.3. 정적 연산 스케줄링
- 세 가지 스케줄링 정책 비교:
  - 수직 그룹링(Vertical): 모든 크로스바가 동일한 벡터 비트 슬라이스로 활성화
  - 대각 그룹링(Diagonal): 최소 크로스바 활성화 (에너지 절약, 지연 시간 증가)
  - 하이브리드 그룹링(Hybrid): 에너지-지연 트레이드오프 균형 (채택)

### 3.4. 희소 행렬 처리
- 이종 크로스바 크기를 가진 은행 구조
- 밀도-크기 트레이드오프 활용:
  - 큰 크로스바: 높은 피크 대역폭, 낮은 밀도
  - 작은 크로스바: 낮은 피크 대역폭, 높은 밀도
- 사전 처리 단계에서 희소 행렬의 밀집 서브블록을 적절한 클러스터에 매핑

## 핵심 기여

- 메모리스트 가속기를 과학 기산 분야에 처음으로 적용하는 연구
- 세 가지 최적화 기법을 통해 고정점 하드웨어에서 고정밀 부동소수점 연산 지원
- 이종 크로스바 구조로 희소 행렬 처리 효율성 향상
- GPU 대비 10.3배 성능 향상, 10.9배 에너지 절감
- 머신러닝을 넘어선 과학 기산 분야에서의 메모리스트 컴퓨팅 가능성 입증

## 주요 결과

- 기술: 메모리스트 크로스바 기반 아날로그 인시추(in-situ) 컴퓨팅
- ADC: 샘플-앤-홀드 회로 + 아날로그-디지털 변환기
- 감소 네트워크: 시프트-앤-add 구조
- 오류 정정: AN 코드 기반 (A=2^51 코드, 8비트 정정, 1비트 검출)
- 최대 크로스바 블록 크기: 512×512 (메모리스트 동적 범위 1.5×10^3 고려)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/gpu.md|GPU]]


## 전체 요약

[[../paper-summaries/2018ISCA-summarize/enabling-scientific-computing-on-memristive-accelerators.md|전체 요약 보기]]
