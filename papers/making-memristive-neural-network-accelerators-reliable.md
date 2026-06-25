---
tags: [paper, 2018, 2018HPCA, topic/pim, topic/ai]
venue: "HPCA 2018"
year: 2018
summary_path: "../paper-summaries/2018HPCA-summarize/making-memristive-neural-network-accelerators-reliable.md"
---

# Making Memristive Neural Network Accelerators Reliable

**Venue:** HPCA 2018
**저자:** Ben Feinberg, Shibo Wang, Engin Ipek (University of Rochester)

## 개요

memristive 신경망 가속기에서 아날로그 컴퓨팅의 오류 문제를 해결하기 위한 새로운 오류 수정 방식을 제안합니다. 산술 코드 기반 오류 수정으로 낮은 오버헤드(영역 4.5% 미만, 에너지 4.7% 미만)로 높은 오류 수정 효율을 달성합니다. 데이터 인식 인코딩을 통해 MNIST에서 1.5배, ILSVRC-2012에서 1.1배 오류율 감소를 보입니다.

## 방법론

### 기본 산술 코드 기반 오류 수정
- 정수 곱셈을 통한 데이터 인코딩
- 분배 법칙을 통한 덧셈 연산 보존
- 모듈러 연산을 통한 오류 검출
- 수정 테이블 조회를 통한 오류 수정

### 데이터 인식 인코딩
- 오류의 상태 종속성을 활용한 개선
- 물리적 행의 1 비트 수에 따른 오류 취약성 차이 활용
- 연산의 전체 시스템 정확도에 대한 중요도 고려

### 효율적인 오류 수정
- 물리적 행에 1이 적게 포함될수록 오류에 덜 취약하다는 특성 활용
- 효과적인 오류 수정 능력 증가
- 영역 오버헤드 4.5% 미만, 에너지 오버헤드 4.7% 미만

## 핵심 기여

1. memristive 신경망 가속기에서 아날로그 컴퓨팅의 오류 문제 해결을 위한 새로운 방식 제안
2. 산술 코드 기반 오류 수정으로 낮은 오버헤드로 높은 오류 수정 효율 달성
3. 데이터 인식 인코딩을 통한 추가적인 성능 향상

## 주요 결과

- **오류율 감소**: MNIST 1.5배, ILSVRC-2012 1.1배
- **오버헤드**: 영역 4.5% 미만, 에너지 4.7% 미만
- **일관성**: 다양한 데이터셋에서 일관된 성능 향상

## 한계점

- memristive DNN 가속기 시뮬레이션에 한정
- 실제 하드웨어 구현에서의 검증 필요

## 관련 개념

- [[paper-wiki/concepts/pim.md|PIM]]
- [[paper-wiki/concepts/ai.md|AI]]