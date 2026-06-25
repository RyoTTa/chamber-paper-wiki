---
tags: [paper, 2025, 2025ISCA, topic/dram, topic/llm-inference, topic/near-data-processing, topic/pim]
venue: "International Symposium on Computer Architecture (ISCA) 2025"
year: 2025
summary_path: "../paper-summaries/2025ISCA-summarize/h2llm-hardware-dataflow-co-exploration-for-low-batch-llm-inference.md"
---

# H2-LLM: Hardware-Dataflow Co-Exploration for Heterogeneous Hybrid-Bonding-based Low-Batch LLM Inference

**Venue:** International Symposium on Computer Architecture (ISCA) 2025
**저자:** Cong Li, Yihan Yin, Xintong Wu, Jingchen Zhu, Zhutianya Gao, Dimin Niu, Qiang Wu, Xin Si, Yuan Xie, Chen Zhang, Guangyu Sun (Peking University, Shanghai Jiao Tong University, Alibaba Group Inc., Houmo AI, SouthEast University, HKUST)

## 개요

- 엣지 사이드 LLM 추론은 개인 챗봇, 가상 비서, 리셉션 봇 등에서 활용되며,低배치(batch size 1~수십 개) 특성을 가짐
- 기존 NMP(Near-Memory Processing) 기반 이종 가속기는 DRAM 다이 내부에 프로세싱 엔진을 배치하여 낮은 계산 용량을 보유
  - DRAM 기술은 동일 기술 노드의 CMOS 대비 트랜지스터 속도 3배 느림, 논리 밀도 10배 낮음
  - 기존 상용 NMP 설계의 계산-대역폭 비율은 1-2 FLOP/Byte 수준으로 낮음
- 저배치 LLM 추론에서 기존 인다이 NMP의 한계:
  - 배치 크기 8 이상이거나 KV 헤드 수 4 이하일 때 성능 향상 없음
  - 중앙 처리기와 NMP PE 모두 리소스 활용도가 낮음
- 하이브리드 본딩(HB) 기술은 높은 대역폭(110,000/mm²)과 낮은 전력 소비를 제공하지만, 메모리 컨트롤러가 로직 다이 면적의 약 40%를 차지하여 계산-대역폭 트레이드오프 발생

## 방법론

### 3.1. 전체 구조
- 중앙 처리기(xPU)와 NMP 활성화 메모리 시스템으로 구성
- NMP 활성화 메모리 시스템은 일반 DRAM 채널과 HB-NMP 채널로 구성
- 각 HB-NMP 채널은 메모리 다이(상단)와 로직 다이(하단)로 구성
- 메모리 다이의 DRAM 뱅크는 두 가지 모드로 접근 가능:
  - 일반 모드: 중앙 처리기가 외부 인터페이스를 통해 접근
  - NMP 모드: NMP PE가 HB 컨트롤러를 통해 병렬 접근

### 3.2. NMP PE 아키텍처
- 각 PE는 여러 부동소수점 유닛(FPU)을 포함하여 저배치 GEMM 연산 수행
- 가중치 및 출력 버퍼는 각 PE에 분산 배치
- NMP 컨트롤러의 명령에 따라 PE 컨트롤러가 FPU 또는 HB 컨트롤러를 구동
- 입력 글로벌 버퍼는 모든 PE 간에 공유되어 입력 텐서 중복 방지

### 3.3. 연산자 실행 흐름
- 오프로딩 기반 실행 모델: 3단계로 구성
  1. 중앙 처리기가 입력을 준비하고 HB-NMP 채널로 분배
  2. PE가 병렬로 연산 수행
  3. 중앙 처리기가 부분 결과를 읽고 병합하여 다음 연산자를 준비
- 채널 간 연산자 분할: 최적의 타일링 팩터를 해석적 모델로 결정
- 채널 내 실행: 출력 고정(execution flow)을 사용하여 행 버퍼 충돌 방지

## 핵심 기여

- 하이브리드 본딩 기술은 엣지 사이드 저배치 LLM 추론을 위한 유망한 통합 기술
- 계산 용량과 대역폭 간의 트레이드오프를 해결하기 위한 아키텍처 설계 공간 탐색 필요
- 데이터 중심 데이터플로우 추상화는 기존 컴퓨트 중심 접근 방식보다 우수한 성능 달성
- H2-LLM은 기존 인다이 NMP 대비 2.72배 속도 향상, 1.48배 에너지 효율 향상
- 향후 이종 하이브리드 본딩 아키텍처 설계를 위한 시사점 제시

## 주요 결과

- 기술: 40nm 공정 기반 하이드레이트 구현
- HB I/O 핀 수: 1024개 핀당 로직 다이 면적의 약 40% 차지
- 오픈소스: https://github.com/leesou/H2-LLM-ISCA-2025
- DSE 프레임워크: 모델 파서, 탐색 엔진, 용량 검사기로 구성

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2025ISCA-summarize/h2llm-hardware-dataflow-co-exploration-for-low-batch-llm-inference.md|전체 요약 보기]]
