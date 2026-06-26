---
tags: [paper, 2018, 2018MICRO, topic/compression, topic/dram, topic/gpu]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/cambricon-s-addressing-irregularity-in-sparse-neural-networks-through-a-cooperative-software-hardware-approach.md"
---

# Cambricon-S: Addressing Irregularity in Sparse Neural Networks through A Cooperative Software/Hardware Approach

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Xuda Zhou, Zidong Du, Qi Guo, Shaoli Liu, Chengsi Liu, Chao Wang, Xuehai Zhou, Ling Li, Tianshi Chen, Yunji Chen (University of Science and Technology of China, Intelligence Processor Research Center, Institute of Computing Technology, CAS, Cambricon Technologies, Michigan State University, Institute of Software, CAS, CAS Center for Excellence in Brain Science)

## 개요

- 현대 신경망은 깊고 큰 구조로 발전하여 엄청난 양의 데이터와 연산을 필요로 함: AlexNet(2012)은 65만 뉴런, 6천만 시냅스; VGGNet(2014)은 1억 뉴런, 10억 시냅스; 2015년 모델은 1천만 뉴런, 100억 시냅스
- **희소성(Sparsity)** 은 시냅스/뉴런을 제거하여 계산 및 메모리 접근량을 10× 이상 줄이는 효과적인 해결책이지만, 희소성으로 인한 **불규칙성(Irregularity)** 이 가속기 효율을 심각하게 저해
- 기존 가속기의 한계:
  - **DianNao/DaDianNao/ShiDianNao**: 희소성 지원 없음
  - **Cambricon-X**: 시냅스 희소성만 지원 (인덱싱 모듈이 면적의 31.07%, 에너지의 34.83% 차지)
  - **Cnvlutin**: 뉴런 희소성만 지원, 시냅스 희소성 활용 불가
  - **EIE**: 시냅스+뉴런 희소성 지원하나 fully-connected layer에만 한정
  - **SCNN**: 좌표 저장/계산 비용이 높아 밀집 네트워크 대비 성능 79%, 에너지 33% 증가
- 희소 신경망의 불규칙성으로 인해 CPU/GPUs에서 희소 네트워크 처리 성능이 밀집 버전보다 오히려 낮음

## 방법론

### 3.1. 코어스 그레인드 프루닝 (Software)

- **블록 단위 프루닝**: 가중치 행렬을 블록으로 나누고, 블록 내 최대/평균 절대값이 임계값 이하이면 전체 블록을 제거
  - fully-connected layer: 블록 크기 (B_in, B_out)로 슬라이딩
  - convolutional layer: 4차원 텐서 (N_fin, N_fout, K_x, K_y)에서 블록 (B_fin, B_fout, B_x, B_y)으로 슬라이딩
- **지역 수렴 활용**: 슬라이딩 윈도우 내 큰 가중치의 분포를 분석하여, 학습된 레이어는 초기화된 레이어보다 4개 이상의 큰 가중치가 블록 내에 집중됨
- **평균 프루닝 vs 최대 프루닝**: 희소율 15% 이하에서 평균 프루닝이 최대 프루닝보다 더 높은 정확도 달성 → 평균 프루닝 채택
- **블록 크기 최적화**: AlexNet 기준 컨볼루션 레이어 (1,16,1,1), fc6/fc7 (32,32), fc8 (16,16) → 압축률 79× 달성

### 3.2. 인덱스 및 압축 최적화 (Software)

- **인덱스 크기 축소**: 코어스 그레인드 프루닝으로 인덱스가 2.95MB → 29.38KB로 102.82× 감소
- **지역 양자화**: 블록 내 가중치를 동일한 양자화 레벨로 양자화
  - 컨볼루션 레이어: 8비트, fully-connected 레이어: 4비트
- **엔트로피 코딩**: Huffman encoding으로 추가 압축
- **전체 압축률**: AlexNet에서 79× 압축률 달성

### 3.3. Cambricon-S 하드웨어 가속기

- **뉴런 셀렉터 모듈 (NSM)**: 뉴런 선택을 통해 동적 뉴런 희소성 활용
  - 0 출력값을 가진 뉴런을 필터링하여 불필요한 시냅스 접근 제거
- **시냅스 셀렉터 모듈 (SSM)**: 코어스 그레인드 프루닝 후 남은 시냅스 희소성 처리
  - 불필요한 시냅스를 필터링하여 PE(Processing Element)로 전달
- **기존 가속기 대비 장점**:
  - Cambricon-X의 인덱싱 모듈 비용(31.07% 면적, 34.83% 에너지)을 크게 절감
  - 시냅스+뉴런 희소성을 모두 지원

## 핵심 기여

- **핵심 기여**: 지역 수렴 현상을 발견하고 이를 활용한 코어스 그레인드 프루닝 기법 제안 — 희소 신경망의 불규칙성을 20.13× 감소
- **소프트웨어/하드웨어 협력**: 소프트웨어 프루닝으로 불규칙성을 크게 줄인 후, 하드웨어 가속기(Cambricon-S)가 남은 불규칙성을 효율적으로 처리
- **성능**: 기존 최첨단 희소 신경망 가속기(Cambricon-X) 대비 성능 1.71×, 에너지 효율 1.37× 향상
- **압축률**: AlexNet에서 79× 압축률 달성 (인덱스 크기 102.82× 감소)
- **의의**: 희소 신경망 가속기 설계에서 불규칙성이 핵심 병목이라는 점을 명확히 하고, 효과적인 해결책을 제시

## 주요 결과

- **구현 언어**: Verilog
- **공정**: 65nm 기술
- **면적**: 6.73mm²
- **소비 전력**: 798.55mW
- **소프트웨어 파이프라인**: 학습 시 코어스 그레인드 프루닝 → 지역 양자화 → 엔트로피 코딩 순서로 적용

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/cambricon-s-addressing-irregularity-in-sparse-neural-networks-through-a-cooperative-software-hardware-approach.md|전체 요약 보기]]
