---
tags: [paper, 2024, 2024HPCA, topic/cache, topic/disaggregation, topic/dram, topic/gpu, topic/llm-inference, topic/pim, topic/storage]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024HPCA-summarize/an-lpddr-based-cxl-pnm-platform-for-llm-inference.md"
---

# An LPDDR-based CXL-PNM Platform for TCO-efficient Inference of Transformer-based Large Language Models

**Venue:** 
**저자:** Sang-Soo Park, KyungSoo Kim, Jinin So, Jin Jung, Jonggeon Lee, Kyoungwan Woo, Nayeon Kim, Younghyun Lee, Hyungyo Kim, Yongsuk Kwon, Jinhyun Kim, Jieun Lee, YeonGon Cho, Yongmin Tai, Jeonghyeon Cho, Hoyoung Song, Jung Ho Ahn, Nam Sung Kim (Samsung Electronics, Seoul National University, University of Illinois Urbana-Champaign)

## 개요

- Transformer 기반 LLM(GPT 등)의 규모가 지속적으로 증가하면서 모델 파라미터와 working set이 수백 GB로 증대. GPT-3.5(175B 파라미터)는 추론 시 326 GB 메모리 용량이 필요하며, 단일 GPU(A100 80GB)로는 이를 수용할 수 없다.
- GPU 기반 가속 시 메모리 병목이 핵심 문제: OPT-30B 추론에서 전체 실행 시간의 상당 부분이 Host-CPU에서 GPU로의 메모리 복수(Memcpy)에 소요되며, 실제 GPU 커널 실행 시간은 93.5ms인데 비해 Memcpy는 1.47ms.
- Gen stage(sequential token generation)의 GEMV 연산은 GPU 활용률이 25% 미만으로 저효율적이며, 전체 추론 시간의 82.3%를 차지. GPU의 on-chip 메모리 용량을 초과하는 행렬에 대해서는 off-chip 메모리 대역폭이 병목이 된다.
- 멀티 GPU 모델 병렬화는 intermediate values의 빈번한 GPU 간 전송을 초래하며, NVLink/PCIe 대역.sulake 제한으로 효율적인 가속이 어렵다. HBM-PIM, AxDIMM 등 기존 PIM/PNM 솔루션은 각각 특정 한계를 가진다.

## 방법론

### 3.1 LPDDR5X의 이점 (Table I)

- **DDR5 대비:** 1.56배 높은 Gbps/pin, 4배 넓은 I/O 폭. CXL 모듈에서 512 GB 용량, 89.6 GB/s 대역폭 달성 가능하나 대역폭이 부족.
- **GDDR6 대비:** 14% 낮은 pJ/bit. CXL 모듈에서 1.5 TB/s 대역폭, 32 GB 용량. 용량이 지나치게 작아 LLM 가속에 부적합.
- **HBM3 대비:** TSV 기반 3D 스택링 대신 저렴한 wire-bonding 기반 3D 스택링 사용. 2.67배 큰 패키지 용량.
- **LPDDR5X:** CXL 모듈에서 **512 GB 용량, 1.1 TB/s 대역폭** 동시 달성. 8개의 LPDDR5X ×128 패키지를 FHHL(full-height/half-length) 폼 팩터에 배치.
- LPDDR5X 패키지당 64 GB 용량, 136 GB/s 대역폭. 3D 스택 4개의 16Gb 다이를 TSV 없이 조립하고 wire-bonding으로 I/O 연결.

### 3.2 기존 PIM/PNM 솔루션의 한계 분석

| 솔루션 | 한계 |
|--------|------|
| **HBM-PIM** | HBM 패키지의 고정 I/O 대역폭으로 bank-level parallelism 활용 어려움; HBM-PIM과 host 간 데이터 전송 비효율 |
| **AxDIMM** | DDR5의 낮은 대역폭; PNM 가속기가 병렬화 불가능한 bank 구조로 LLM 추론에 적합하지 않음 |

### 3.3 CXL 인터커넥트 활용

- CXL 2.0 메모리 프로토콜을 통해 호스트 CPU와 CXL-PNM 디바이스 간의 coherency 보장 및 투명한 메모리 접근 지원.
- CXL 메모리의 독립적인 주소 공간을 활용하여 LLM 모델 파라미터와 KV 캐시를 CXL-PNM 디바이스에 할당.

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1 LLM 추론 가속기 통합

- CXL-PNM 컨트롤러 내에 LLM 추론 가속기(GEMV 엔진, 비선형 변환 엔진 등)를 통합하여, 메모리 데이터가 가속기까지 이동하지 않고 메모리 근처에서 직접 연산 수행.
- HBM-PIM 대비: 고정 I/O 대역폭 제약 없이 bank-level parallelism 활용 가능.
- AxDIMM 대비: bank 구조의 유연성 확보.

### 4.2 메모리 관리 및 데이터 레이아웃

- LLM의 모델 파라미터를 CXL-PNM 디바이스의 LPDDR5X 메모리에 할당.
- KV 캐시(key-value cache)를 CXL-PNM 디바이스에 할당하여 attention 연산의 메모리 대역폭 요구사항 충족.
- Gen stage의 GEMV 연산이 CXL-PNM 디바이스 내에서 수행되어, 데이터 전송 오버헤드를 제거.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2024HPCA-summarize/an-lpddr-based-cxl-pnm-platform-for-llm-inference.md|전체 요약 보기]]
