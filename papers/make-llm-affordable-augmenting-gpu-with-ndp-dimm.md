---
tags: [paper, 2025, 2025HPCA, topic/dram, topic/gpu, topic/llm-inference, topic/near-data-processing, topic/pim]
venue: "2025 IEEE International Symposium on High Performance Computer Architecture (HPCA 2025)"
year: 2025
summary_path: "../paper-summaries/2025HPCA-summarize/make-llm-affordable-augmenting-gpu-with-ndp-dimm.md"
---

# Make LLM Inference Affordable to Everyone: Augmenting GPU Memory with NDP-DIMM

**Venue:** 2025 IEEE International Symposium on High Performance Computer Architecture (HPCA 2025)
**저자:** Lian Liu, Shixin Zhao, Bing Li, Haimeng Ren, Zhaohui Xu, Mengdi Wang, Xiaowei Li, Yinhe Han, Ying Wang (Institute of Computing Technology, Chinese Academy of Sciences; University of Chinese Academy of Sciences; Zhongguancun Laboratory; Institute of Microelectronics, Chinese Academy of Sciences; ShanghaiTech University)

## 개요

- 대규모 언어 모델(LLM)은 서버급 GPU와 대용량 HBM(High Bandwidth Memory)이 필요하며, LLaMA2-70B 로컬 배포 시 NVIDIA A100-40GB GPU 5대(총 $50,000 이상)가 필요
- 소비자용 GPU(예: NVIDIA RTX 4090)는 1321 Tensor TOPS의 높은 연산 능력을 보유하나, 24GB 그래픽 메모리로 LLM 파라미터 전체를 수용할 수 없음
- 기존 오프로딩 솔루션(FlexGen, Huggingface Accelerate 등)은 DIMM 기반 호스트 메모리를 GPU 메모리 확장으로 활용하나, PCIe 대역폭 제한(PCIe 4.0 ~64GB/s vs GPU 내부 메모리 ~1TB/s)으로 인해 LLM 추론 시간의 99%가 PCIe 데이터 전송에 소요
- OPT-66B 모델 기준 오프로딩 시스템에서 PCIe 데이터 전송이 전체 추론 레이턴시의 90%를 차지
- 기존 비활성화 희소성(activation sparsity) 기반 접근법(Deja Vu 등)은 오프로딩의 PCIe 병목을 완전히 해결하지 못하며, MLP 기반 예측기의 높은 오버헤드로 실시간 조정에 한계

## 방법론

### 3.1. NDP-DIMM 하드웨어 설계

- **NDP 코어 구성 (Table II):**
  - 256개 멀티플라이어, 감소 트리 기반 어큐뮬레이터
  - 버퍼 크기: 256KB
  - DIMM당 NDP 코어 1개, 클럭: 1GHz
  - 면적 오버헤드: 코어당 1.23mm²
- **DIMM 파라미터:**
  - DDR4-3200, 32GB/DIMM × 8
  - 2 DIMM/채널, 4 랭크/DIMM
  - 2 뱅크 그룹/랭크, 4 뱅크/뱅크 그룹
- **DIMM-링크 파라미터:**
  - 25Gb/s/레인, 1.17pJ/b
  - 8 × 레인 (링크당 25GB/s)

### 3.2. 이단계 뉴런 파티션 전략

- **오프라인 ILP(Integer Linear Programming) 솔버:**
  - 프로파일링 데이터를 기반으로 최적의 초기 핫/콜드 뉴런 분할 결정
  - 정수 선형 프로그래밍 문제로 공식화하여 최적 해 탐색
- **경량 온라인 예측기:**
  - 핫/콜드 뉴런의 뚜렷한 분포 패턴을 활용한 실시간 예측
  - MLP 기반 예측기 대비 최소화된 마이그레이션 비용으로 실시간 핫/콜드 뉴런 조정
  - 활성화 희소성 특성을 활용한 가벼운 예측 알고리즘

### 3.3. 윈도우 기반 온라인 스케줄링 (Algorithm 1)

- **부하 균형 달성 알고리즘:**
  1. 윈도우 내 각 뉴런의 활성화 횟수 계산
  2. NDP-DIMM별 총 활성화된 뉴런 수 계산
  3. NDP-DIMM을 내림차순 정렬
  4. 가장 많은 활성화를 가진 DIMM과 가장 적은 DIMM 페어링
  5. 가장 활성화된 뉴런을 한 DIMM에서 다른 DIMM으로 리매핑
- **장점:**
  - 고정된 DIMM 간 통신 트래픽이 다른 브릿지로 분산되어 혼잡 방지
  - 탐욕적 리매핑으로 최소 데이터 전송으로 빠른 균형 달성
  - 윈도우 크기 내 NDP-DIMM 간 성능 차이가 5% 미만으로 균형 잡힌 할당 달성

### 3.4. 시스템 아키텍처

- **구성:** NVIDIA RTX 4090 GPU(24GB GDDR6) + 8개 NDP-DIMM(각 32GB DDR4)
- **인터커넥트:** PCIe 4.0 (64GB/s)
- **작동 원리:**
  - 핫 뉴런: GPU 메모리에 저장 및 GPU 텐서 코어로 연산
  - 콜드 뉴런: NDP-DIMM에 오프로딩 및 NDP 코어로 연산
  - NDP-DIMM 내부 대역폭(~1.6TB/s)을 활용하여 PCIe 데이터 전송 최소화
  - 연산 결과만 kB 수준으로 전송 → 데이터 전송 비용 무시 가능

## 핵심 기여

- **핵심 기여:** NDP-DIMM을 활용한 경제적 LLM 추론 시스템 Hermes 제안
- **성능:** FlexGen 대비 **148.98×**, Deja Vu 대비 **75.24×** 가속
- **혁신성:**
  1. 활성화 희소성을 활용한 핫/콜드 뉴런 이중화 전략
  2. NDP-DIMM의 내부 대역폭을 활용하여 PCIe 병목 완전 해결
  3. 경량 온라인 예측기로 실시간 뉴런 파티션 조정
  4. 윈도우 기반 온라인 스케줄링으로 다중 NDP-DIMM 부하 균형
- **경제성:** 소비자용 GPU($1,600) + NDP-DIMM($900) = 총 ~$2,500으로 LLaMA2-70B 추론 가능
- **의의:** 서버급 GPU 대비 약 5% 예산으로 경쟁력 있는 LLM 추론 성능을 달성하여, 로컬 배포의 경제적 접근성 크게 향상

## 주요 결과

- **GPU:** NVIDIA RTX 4090 (24GB GDDR6, 330 tensor TOPS FP16)
- **NDP-DIMM:** 8개 DIMM, 각 32GB DDR4
- **NDP 코어:** RTL 구현 후 Synopsys Design Compiler로 TSMC 7nm 기술 합성
- **시뮬레이터:** Ramulator 2.0 기반 커스텀 시뮬레이터
- **LLM 모델:** OPT-13B, OPT-30B, OPT-66B, LLaMA2-13B, LLaMA2-70B, Falcon-40B
- **오프라인 ILP 솔버:** PuLP 라이브러리 사용

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2025HPCA-summarize/make-llm-affordable-augmenting-gpu-with-ndp-dimm.md|전체 요약 보기]]
