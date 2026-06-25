---
tags: [paper, 2018, 2018MICRO, topic/pim, topic/llm-inference]
venue: "MICRO 2018"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/cambricon-s-addressing-irregularity-in-sparse-neural-networks-through-a-cooperative-software-hardware-approach.md"
---

# Cambricon-S: Addressing Irregularity in Sparse Neural Networks through A Cooperative Software/Hardware Approach

**Venue:** MICRO 2018
**저자:** Xuda Zhou, Zidong Du, Qi Guo, Shaoli Liu, Chengsi Liu, Chao Wang, Xuehai Zhou, Ling Li, Tianshi Chen, Yunji Chen (USTC, ICT CAS, Cambricon Technologies, Michigan State University, ISCAS, CAS Center for Excellence in Brain Science)

## 개요

현대 신경망은 깊고 큰 구조로 발전하여 엄청난 양의 데이터와 연산을 필요로 한다. 희소성(Sparsity)은 시냅스/뉴런을 제거하여 계산 및 메모리 접근량을 10× 이상 줄이는 효과적인 해결책이지만, 희소성으로 인한 불규칙성(Irregularity)이 가속기 효율을 심각하게 저해한다.

Cambricon-S는 지역 수렴(Local Convergence) 현상을 활용한 코어스 그레인드 프루닝과 하드웨어 가속기를 결합하여 불규칙성을 20.13× 감소시키고, 기존 최첨단 가속기(Cambricon-X) 대비 성능 1.71×, 에너지 효율 1.37×를 달성한다.

## 방법론

### 코어스 그레인드 프루닝 (Software)
- 시냅스를 독립적으로 제거하는 대신 블록 단위로 제거
- **지역 수렴 활용**: 학습 과정에서 큰 가중치가 가까운 위치에 클러스터를 형성 → 블록 단위 프루닝으로 불규칙성 대폭 감소
- 블록 크기 최적화: 컨볼루션 (1,16,1,1), fc6/fc7 (32,32), fc8 (16,16)
- 평균 프루닝 채택: 희소율 15% 이하에서 최대 프루닝 대비 더 높은 정확도

### 인덱스 및 압축 최적화
- 인덱스 크기: 2.95MB → 29.38KB (102.82× 감소)
- 지역 양자화: 컨볼루션 8비트, FC 4비트
- 엔트로피 코딩: Huffman encoding
- AlexNet 압축률: 79×

### Cambricon-S 하드웨어 가속기
- **뉴런 셀렉터 모듈 (NSM)**: 동적 뉴런 희소성 활용, 0 출력 뉴런 필터링
- **시냅스 셀렉터 모듈 (SSM)**: 코어스 그레인드 프루닝 후 남은 시냅스 희소성 처리
- 65nm 공정, 6.73mm², 798.55mW

## 핵심 기여

1. 지역 수렴 현상 발견 및 이를 활용한 코어스 그레인드 프루닝 기법 제안
2. 불규칙성 측정 방법론 제안 (JBIG 기반)
3. 소프트웨어/하드웨어 협력적 희소 신경망 처리 프레임워크
4. 시냅스+뉴런 희소성을 모두 지원하는 가속기 설계

## 주요 결과

- **성능**: Cambricon-X 대비 1.71× 향상
- **에너지 효율**: Cambricon-X 대비 1.37× 향상
- **불규칙성 감소**: 평균 20.13×
- **AlexNet 압축률**: 79× (인덱스 102.82× 감소)
- **동적 뉴런 희소율**: AlexNet 62.37%, VGG16 40.52%

## 한계점

- 코어스 그레인드 프루닝의 블록 크기 탐색에 많은 학습 시간 필요
- 컨볼루션 레이어에서 프루닝 차원 선택이 정확도에 영향
- 완전한 동적 희소성 지원은 아직 제한적

## 관련 개념

- [[paper-wiki/concepts/pim.md|PIM]]: 신경망 가속기에서의 희소성 활용 및 메모리 접근 최적화
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]: 희소 신경망 가속이 대규모 모델 추론에 미치는 영향

## 관련 논문 요약

- [paper-summaries/2018MICRO-summarize/cambricon-s-addressing-irregularity-in-sparse-neural-networks-through-a-cooperative-software-hardware-approach.md]
