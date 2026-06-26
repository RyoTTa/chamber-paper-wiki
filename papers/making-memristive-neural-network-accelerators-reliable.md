---
tags: [paper, 2018, 2018HPCA]
venue: "HPCA 2018 (IEEE International Symposium on High-Performance Computer Architecture)"
year: 2018
summary_path: "../paper-summaries/2018HPCA-summarize/making-memristive-neural-network-accelerators-reliable.md"
---

# Making Memristive Neural Network Accelerators Reliable

**Venue:** HPCA 2018 (IEEE International Symposium on High-Performance Computer Architecture)
**저자:** Ben Feinberg, Shibo Wang, Engin Ipek (University of Rochester)

## 개요

- 딥 뉴럴 네트워크(DNN)는 분류 및 회귀 작업에서 뛰어난 성능을 보여 관심을 끌고 있음
- DNN은 대량의 데이터 이동이 필요하여 성능 및 에너지 오버헤드 발생
- memristive 회로의 전기적 특성을 활용한 시트(in-situ) 아날로그 컴퓨팅 기반 가속기가 유망한 해결책
- 아날로그 신경망 가속기는 성능과 에너지 효율성 향상 가능
- 그러나 메모리 내 아날로그 컴퓨팅에서 발생하는 오류를 검출하고 수정하는 방법은 충분히 연구되지 않음
- memristive 디바이스의 전기적 특성이 오류에 취약하게 만들어 정확도 저하 초래

## 방법론

### 3.1. 기본 산술 코드 기반 오류 수정

- 정수 곱셈을 통한 데이터 인코딩
- 분배 법칙을 통한 덧셈 연산 보존
- 모듈러 연산을 통한 오류 검출
- 수정 테이블 조회를 통한 오류 수정

### 3.2. 데이터 인식 인코딩

- 오류의 상태 종속성을 활용한 개선
- 물리적 행의 1 비트 수에 따른 오류 취약성 차이 활용
- 연산의 전체 시스템 정확도에 대한 중요도 고려

### 3.3. 효율적인 오류 수정

- 물리적 행에 1이 적게 포함될수록 오류에 덜 취약하다는 특성 활용
- 효과적인 오류 수정 능력 증가
- 영역 오버헤드 4.5% 미만, 에너지 오버헤드 4.7% 미만

## 핵심 기여

- memristive 신경망 가속기에서 아날로그 컴퓨팅의 오류 문제를 해결하기 위한 새로운 방식 제안
- 산술 코드 기반 오류 수정으로 낮은 오버헤드로 높은 오류 수정 효율 달성
- 데이터 인식 인코딩을 통한 추가적인 성능 향상
- 향후 memristive 기반 신경망 가속기의 실용화를 위한 기초 연구

---

## 참고 자료

- 논문 원문: `/home/ryotta205/Chamber_paper/paper-source/2018HPCA/Making_Memristive_Neural_Network_Accelerators_Reliable.pdf`
- 관련 개념: Memristive, Neural Network Accelerator, Error Correction, Analog Computing

## 주요 결과

- memristive DNN 가속기에서의 구현
- MNIST 및 ILSVRC-2012 데이터셋에서의 추론 적용
- 산술 코드 기반 인코딩/디코딩 하드웨어

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- 개념 매칭 없음

## 전체 요약

[[../paper-summaries/2018HPCA-summarize/making-memristive-neural-network-accelerators-reliable.md|전체 요약 보기]]
