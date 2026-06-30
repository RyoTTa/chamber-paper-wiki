---
tags: [paper, 2025, 2025DAC, topic/pim, topic/llm, topic/dram]
venue: "DAC 2025"
year: 2025
summary_path: "../paper-summaries/2025DAC-summarize/pimpal-accelerating-llm-inference-on-edge-devices-via-in-dram-arithmetic-lookup.md"
---

# PIMPAL: Accelerating LLM Inference on Edge Devices via In-DRAM Arithmetic Lookup

**Venue:** DAC 2025
**저자:** Yoonho Jang, Hyeongjun Cho, Yesin Ryu, Jungrae Kim, Seokin Hong (성균관대학교)

## 개요

엣지 기기에서의 LLM 추론은 높은 연산 및 메모리 요구로 인해 큰 도전 과제이다. LLM 추론의 핵심 연산인 GEMV(General Matrix-Vector Multiplication)는 메모리 집약적이다. PIMPAL은 LUT(LookUp Table) 기반 PIM(Processing-in-Memory) 아키텍처를 활용하여 sLLM(small LLM)의 GEMV 연산을 가속화하는 비용 효율적 솔루션이다.

## 방법론

### 서브어레이 수준 병렬 룩업 조직
- DRAM 뱅크의 서브어레이를 컴퓨터 블록으로 분할
- 각 컴퓨터 블록에서 데이터 공급 및 LUT 저장 담당 서브어레이 분리
- 여러 컴퓨터 블록에서 병렬 처리로 확장 가능한 프레임워크 제공

### 지역성 인식 컴퓨팅 매핑 (LCM)
- 열 주요(column-major) GEMV 접근법 적용
- 행렬 열을 컴퓨터 블록에 분산하여 부분 곱 계산
- 활성화된 LUT 행의 재사용을 통한 locality 향상

### LUT 집합화 (LAG)
- INT8, BF16 등 다중 정밀도 연산 지원
- 두 개의 LUT에서 지수/가수 비트 결과를 결합
- BF16의 경우 LUT 엔트리를 2^32에서 2^16으로 감소

## 핵심 기여

- LUT 기반 PIM으로 sLLM GEMV 가속화를 위한 비용 효율적 아키텍처 제시
- 서브어레이 수준 병렬 룩업으로 높은 처리량 달성
- LCM으로 행 활성화 횟수를 획기적으로 감소 (1회)
- LAG로 고정밀 연산 지원 및 LUT 크기 최소화

## 주요 결과

- 기존 LUT 기반 PIM 대비 **17.8배** 성능 향상
- PU 기반 PIM 대비 **40%** 영역 오버헤드 감소
- PU 기반 PIM 대비 **25%** 더 높은 면적당 성능(performance per area)
- Table II: 16비트 정밀도 지원 및 행 활성화 횟수 1회로 기존 설계 대비 개선

## 한계점

- sLLM(small LLM)에 최적화되어 있어 대규모 LLM에는 적용 어려울 수 있음
- DRAM 프로세스 기반 구현으로 인한 제한 사항 존재

## 관련 개념

- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/llm.md|LLM Inference]]
- [[paper-wiki/concepts/dram.md|DRAM]]

## 전체 요약

[[../paper-summaries/2025DAC-summarize/pimpal-accelerating-llm-inference-on-edge-devices-via-in-dram-arithmetic-lookup.md|전체 요약 보기]]
