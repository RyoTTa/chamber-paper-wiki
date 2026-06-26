---
tags: [paper, 2025, 2025ISCA, topic/dram, topic/gpu, topic/llm-inference, topic/pim]
venue: "International Symposium on Computer Architecture (ISCA) 2025"
year: 2025
summary_path: "../paper-summaries/2025ISCA-summarize/heterogeneous-processing-in-memory-acceleration-for-retrieval-augmented-generation.md"
---

# HeterRAG: Heterogeneous Processing-in-Memory Acceleration for Retrieval-augmented Generation

**Venue:** International Symposium on Computer Architecture (ISCA) 2025
**저자:** Chaoqiang Liu, Haifeng Liu, Dan Chen, Yu Huang, Yi Zhang, Wenjing Xiao, Xiaofei Liao, Hai Jin (Huazhong University of Science and Technology, National University of Singapore, Guangxi University)

## 개요

- RAG(Retrieval-augmented Generation)는 외부 지식 베이스를 통합하여 지식 집약적 시나리오에서 LLM의 응답 품질을 향상
- RAG 시스템은 두 가지 주요 단계로 구성:
  1. 검색 단계: 그래프 기반 근접 이웃 검색(ANNS)을 통해 관련 문서 검색
  2. 생성 단계: 검색된 문서를 기반으로 LLM이 응답 생성
- 메모리 병목 문제:
  - 검색 단계: 무작위 및 불규칙한 메모리 접근 패턴으로 인해 낮은 대역폭 활용도
  - 생성 단계: GEMV 연산의 낮은 데이터 재사용으로 인해 메모리 대역폭 의존적
- 메모리 용량 문제:
  - 대규모 지식 베이스 저장을 위한 수백 GB~TB 규모의 메모리 필요
  - HBM 기반 PIM은 높은 대역폭을 제공하지만 제한된 용량과 높은 비용 (약 $110/GB)
  - DDR DIMM은 높은 용량(최대 64GB)과 낮은 비용을 제공하지만 낮은 대역폭

## 방법론

### 3.1. 전체 구조
- 호스트, 고대역폭 인터커넥트, 다수의 AccelDIMM 및 AccelHBM 디바이스로 구성
- AccelDIMM: 검색 단계를 위한 DIMM 기반 PIM 디바이스
  - 다수의 DIMM이 병렬로 대규모 벡터 데이터 처리
  - 그래프 데이터를 버텍스 수준에서 분할하여 랭크 간 균일 분배
- AccelHBM: 생성 단계를 위한 HBM 기반 PIM 디바이스
  - 텐서 병렬성 및 파이프라인 병렬성 지원
  - GEMM은 메모리 외부, GEMV는 인메모리에서 처리

### 3.2. AccelDIMM 아키텍처
- 상위 처리 모듈(TPM): 호스트 명령어 파싱, 디바이스 메모리 관리
- 기능 블록(FB): 이웃 가져오기, 대기열 업데이트, PIM 요청 생성
- 메모리 컨트롤러: PIM 요청 지원을 위한 확장 통합
- PIM 활성화 DIMM:
  - 랭크 수준 처리 모듈(RPM): PIM 명령어 디코딩, 벡터 거리 계산
  - DIMM 수준 처리 모듈(DPM): PIM 명령어 전달 및 결과 중계
  - 벡터 캐시: 자주 접근되는 버텍스 벡터 캐싱

### 3.3. AccelHBM 아키텍처
- 상위 처리 모듈(TPM):
  - 메트릭스 유닛: GEMM 계산을 위한 시스톨릭 어레이
  - 벡터 유닛: 기타 모든 연산을 위한 VLIW 프로세서
  - 트리 검색 유닛, KV 치환 유닛, 토큰 필터링 유닛
- PIM 활성화 HBM:
  - 은행 수준 처리 모듈(BPM): 은행 수준에서 GEMV 병렬 실행
  - 각 BPM은 2개의 벡터 내적 연산 유닛 포함

### 3.4. 소프트웨어-하드웨어 공동 최적화
- 지역성 인식 검색:
  - 자주 접근되는 버텍스 벡터를 캐싱하여 DRAM 접근 최소화
  - 반복 RAG 시나리오에서 이전 반복의 검색 결과를 재사용
  - 로컬/글로벌 캐시 분리로 캐시 효율성 향상
- 지역성 인식 생성:
  - 접두사 트리와 선택적 계산을 결합한 KV 캐시 최적화
  - 밀도(dense)와 희소(sparse) KV로 분리하여 저장 효율 극대화
  - 중요한 토큰만 선택적으로 저장 (10-20% 토큰 선택 시 0.2% 주의도 편차)
- 세분화된 병렬 파이프라인:
  - 검색 완료 전에 부분 결과를 전송하여 생성 단계와 겹침(overlap) 허용
  - 호스트가 고정된 간격으로 검색 결과 집계

## 핵심 기여

- RAG 시스템은 전통적인 LLM 대비 더 심각한 메모리 대역폭 및 용량 문제에 직면
- 이종 PIM 시스템은 HBM과 DIMM의 장점을 결합하여 높은 성능, 에너지 효율, 낮은 비용 달성
- 소프트웨어-하드웨어 공동 최적화는 시스템 효율성을 크게 향상
- HeterRAG는 다양한 구성을 통해 6.6배~26.5배 처리량 향상 달성
- 그래프 처리, 추천 시스템 등 다른 메모리 집약적 애플리케이션에도 일반화 가능

## 주요 결과

- AccelDIMM 구현:
  - DDR4-3200 MT/s, 16Gb ×8, 2 랭크
  - 128 엔트리 명령 큐, 1KB 결과 버퍼
- AccelHBM 구현:
  - HBM2E 스택 기반
  - 시스톨릭 어레이 기반 메트릭스 유닛
  - VLIW 프로세서 기반 벡터 유닛
- 소프트웨어 스택:
  - ANNS-ACC 및 LLM-ACC API 제공
  - HeterRAG 컴파일러를 통한 호스트 실행 파일 및 디바이스 바이너리 생성

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2025ISCA-summarize/heterogeneous-processing-in-memory-acceleration-for-retrieval-augmented-generation.md|전체 요약 보기]]
