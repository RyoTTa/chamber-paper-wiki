---
tags: [paper, 2022, 2022HPCA, topic/dram, topic/llm-inference, topic/pim, topic/virtual-memory]
venue: "IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2022"
year: 2022
summary_path: "../paper-summaries/2022HPCA-summarize/transpim-a-memory-based-acceleration-via-sw-hw-co-design-for-transformer.md"
---

# TransPIM: A Memory-based Acceleration via Software-Hardware Co-Design for Transformer

**Venue:** IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2022
**저자:** Minxuan Zhou (UC San Diego), Weihong Xu (UC San Diego), Jaeyoung Kang (UC San Diego), Tajana Rosing (UC San Diego)

## 개요

- Transformer 기반 모델은 NLP, 컴퓨터 비전, 비디오 분석 등 다양한 ML 작업에서 최첨단 성능을 제공하지만, 대규모 메모리 사용량과 낮은 데이터 재사용율로 인해 긴 실행 시간이 요구됨
- 기존 CNN 중심 가속기(compute-intensive 연산 최적화)는 Transformer의 memory-intensive 특성에 최적이 아님 — Figure 3(a)에서 RoBERTa 기반 PIM-only 시스템의 실행 시간 분석 시 **약 60%가 데이터 이동에 소요**
- Layer-based dataflow의 경우 시퀀스 길이가 증가함에 따라 Attention 레이어의 계산 데이터 크기가 **제곱수준으로 증가** (Figure 3(b))
- PIM의 bit-serial row-parallel 연산에서 reduction 연산이 전체 실행 시간의 **23%~32%**를 차지하며, 일반적인 PIM 산술 연산(4%~10%)에 비해 현저히 낮은 처리량
- 기존 ASIC 기반 가속기(SpAtten, A3)는 병렬도 제한과 오프칩 메모리 대역폭 제한으로 성능에 한계

## 방법론

### 3.1. Token-based Data Sharding

- 입력 토큰을 균등하게 N개 메모리 뱅크로 분배 — 각 뱅크는 `L/N × D` 크기의 서브행렬 처리
- 각 뱅크가 할당된 토큰의 FC, Attention, FFN 연산을 독립적으로 처리
- Encoder 블록:
  - **Intra-shard local attention**: 각 뱅크가 로컬 Q, K로 부분 attention score `S_i,i` 독립 계산
  - **Inter-shard cross attention**: Ring broadcast를 이용한 K 행렬 이동 — 각 뱅크가 원격 K와 로컬 Q를 곱셈
  - N-step ring broadcast로 전체 attention score matrix S 완성
  - Softmax는 로컬 행 데이터로 각 뱅크에서 독립 계산 (데이터 이동 불필요)
- Decoder 블록: 마지막 뱁크가 새 Q, K, V 벡터 처리, 이후 모든 뱅크로 Q_new 브로드캐스트

### 3.2. Auxiliary Computing Unit (ACU)

- **목적**: PIM의 비효율적 연산(reduction, Softmax)을 효율적으로 처리
- **구조**: Subarray에 연결된 256-bit bit-serial adder tree — P_add = 4개의 파이프라인 adder tree 병렬 구현
- **Vector Multiplication**: 메모리 셀에서 점별 곱셈(PIM) 수행 후 ACU에서 reduction 처리
- **Softmax 계산**:
  - 5차 Taylor 급수 전개로 지수 함수 근사 → PIM 곱셈/덧셈으로 계산
  - Row accumulation을 ACU에서 offload → 나눗셈기로 역수 계산
  - 역수를 메모리 셀에 복사 후 점별 곱셈으로 최종 Softmax 출력
- 은행당 P_sub = 16개 ACU, 총 512개 ACU → 면적 오버헤드 **4.0%** (2.15 mm² per 8GB HBM)

### 3.3. Data Communication Architecture

- **Data Buffer**: 8 × 256b 구성 가능한 버퍼 — fine-grained data copy 및 재구성 지원, subarray 간 데이터 이동 가능
- **Ring Broadcast Unit**: HBM의 글로벌 공유 버스를 대체하는 은행 간 직접 256-bit 링크
  - 기존 HBM: 8T (은행 간 복사 시각) → TransPIM: **3T**로 단축
  - Bank Group Bus와 Ring Broadcast Buffer의 병렬 처리 활용
- HBM의 internal bandwidth를 최대한 활용하여 데이터 이동 오버헤드 대폭 절감

## 핵심 기여

- **핵심 기여**: Transformer를 위한 최초의 end-to-end 메모리 기반 가속기 — PIM과 NMC의 장점을 하이브리드로 결합
- **성능**: GPU 대비 **22.1×~114.9×** 가속, ASIC 대비 **2.0×** 이상 처리량 향상
- **소프트웨어-하드웨어 공동 설계**: Token-based dataflow로 데이터 이동 대폭 절감 + 경량 ACU로 복잡 연산 효율화
- **범용성**: Encoder-decoder(TransPegasus), Encoder-only(RoBERTa), Decoder-only(GPT-2) 모두 지원
- **한계점**: 메모리 밀도 4.0% 감소 (ACU 면적), 에너지 효율은 NBP 대비 약간 낮음 (bit-serial 연산의 row activation 오버헤드)
- **확장성**: 장 시퀀스 Transformer에 대한 거의 선형적 확장 가능성 — 미래 메모리 기반 가속기의 프레임워크 제시

## 주요 결과

- **하드웨어**: Verilog HDL 구현, Synopsys Design Compiler (65nm library)로 합성
- **배치/배선**: Synopsys IC Compiler, clock gating 적용
- **ACU 클럭**: 500 MHz (column access time tCCD = 2ns에 맞춤)
- **스케일링**: ACU 면적/전력 데이터를 22nm로 스케일링 (DRAM 공정 고려)
- **시뮬레이터**: TensorFlow 프론트엔드 + 수정된 Ramulator 백엔드
- **HBM 스택**: 최대 8개 HBM 스택 연결, 총 64GB, host-HBM 대역폭 256GB/s

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2022HPCA-summarize/transpim-a-memory-based-acceleration-via-sw-hw-co-design-for-transformer.md|전체 요약 보기]]
