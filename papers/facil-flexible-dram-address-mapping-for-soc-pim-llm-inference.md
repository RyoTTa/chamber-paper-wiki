---
tags: [paper, 2025, 2025HPCA, topic/dram, topic/llm-inference, topic/pim, topic/virtual-memory]
venue: "2025 IEEE International Symposium on High-Performance Computer Architecture (HPCA '25)"
year: 2025
summary_path: "../paper-summaries/2025HPCA-summarize/facil-flexible-dram-address-mapping-for-soc-pim-llm-inference.md"
---

# FACIL: Flexible DRAM Address Mapping for SoC-PIM Cooperative On-device LLM Inference

**Venue:** 2025 IEEE International Symposium on High-Performance Computer Architecture (HPCA '25)
**저자:** Seong Hoon Seo, Junghoon Kim, Donghyun Lee, Seonah Yoo, Seokwon Moon, Yeonhong Park, Jae W. Lee (Seoul National University, Hanyang University)

## 개요

- 온디바이스 LLM 추론에 대한 수요가 급증: Samsung Galaxy AI, Apple Intelligence, Android AI Core 등 주요 IT 벤더들이 모바일/노트북 기반 LLM 서비스를 출시.
- 온디바이스 LLM 추론은 주로 단일 쿼리를 처리하며, GEMV(일반 행렬-벡터 곱셈) 연산이 지배적 → 메모리 대역폭 벽(memory wall)이 핵심 병목.
- DRAM 기반 Processing-in-Memory (PIM)는 near-bank 연산 단위를 배치하여 메모리 대역폭 문제를 해결하는 유망한 기술. 최근 출시된 모든 양산용 PIM 디바이스(AiM, HBM-PIM 등)가 이 패러다임을 채택.
- **핵심 문제:** 엣지 디바이스의 제한된 메모리 용량으로 인해 PIM이 연산 유닛과 메모리 디바이스 역할을 모두 수행해야 함. PIM이 최적화된 데이터 레이아웃(특수 DRAM 주소 매핑)은 기존 메모리 컨트롤러의 일반 매핑과 상이.
- LLM 가중치는 GEMM(PIM에 부적합, SoC 프로세서에 유리)과 GEMV(PIM에 유리) 양쪽에서 사용됨. 동일 가중치에 대해 PIM과 SoC 프로세서 각각에 최적화된 서로 다른 메모리 매핑이 필요.
- 기존 접근법:
  - **중복 배치 (Weight Duplication):** 두 가지 매핑으로 가중치 복사 → 메모리 사용량 2배 증가, 엣지 디바이스에 부적합
  - **온디맨드 재레이아웃:** PIM 가중치를 SoC용 매핑으로 재배치 후 GEMM 수행 → TTFT(Time-to-First-Token) 약 3배 증가 (Jetson AGX Orin, Llama3-8B에서 100ms→300ms)
  - TTFT 100ms 미만이어야 "즉시 반응", 음성 비서는 TTFT 250ms 이하 권장

## 방법론

### 3.1. pimalloc (메모리 할당)

- Figure 7(a): 사용자가 행렬 차원(dim)과 데이터 타입(dtype)을 입력하면:
  - **매핑 셀렉터:** 행렬 구성, 메모리 구성, PIM 구성에 기반하여 최적 PA-to-DA 매핑(MapID) 결정
  - **OS 메모리 할당자:** huge page를 할당하고 물리적 주소 + MapID를 page table에 기록
  - **가상 주소 반환:** 사용자에게 표준 가상 주소 반환

### 3.2. DRAM 주소 매핑 공식화

- **AiM 스타일 PIM:**
  - chunk(행렬의 타일)가 하나의 bank 내에 연속 배치되도록 설계
  - matrix row가 하나의 bank에 완전히 매핑 (부분 합 감소 오버헤드 방지)
  - MapID: PU-changing 비트(bank, rank, channel 비트)와 chunk column 비트 사이의 비트 수
- **HBM-PIM 스타일:**
  - chunk row 차원이 8이므로 3개의 column 비트가 먼저 prepended
  - 요소가 동일 DRAM row에 배치되도록 보장
- **MapID 계산 공식:** `max(MapID) = log2(OS huge page size / (total bank count × DRAM transfer size))`
  - LPDDR5 DRAM의 최대 MapID = 13 (2MB huge page, 8-bank, 32B 전송 크기 기준)
  - 적은 MapID 수 → OS 및 메모리 컨트롤러 수정 최소화

### 3.3. 매핑 선택 알고리즘

- Figure 9: `select_mapping(matrix_config, memory_config, pim_config)` 함수
  - 행렬 column 차원, dtype, huge page 크기, 채널/rank/bank 수, chunk column 차원을 입력으로 받음
  - memory_per_bank < row_size일 때 분할 필요 여부 결정
  - MapID 계산: `map_id = (need_partition ? log2(memory_per_bank) : log2(row_size)) - log2(chunk_col)`
  - O(1) 복잡도의 효율적인 매핑 선택

### 3.4. 프로그래머 투명한 접근

- **저장 (Figure 7(b)):** 프로그래머는 가상 주소와 데이터만 전달
  - Page table entry에 PA + MapID 포함
  - 메모리 컨트롤러가 MapID에 따라 적절한 PA-to-DA 변환 수행
- **로드 (Figure 7(c)):** 프로그래머는 가상 주소만 전달
  - 메모리 컨트롤러가 MapID에 따라 DA 변환 후 데이터 로드
  - BLAS 라이브러리(Intel oneMKL, NVIDIA cuBLAS 등)와 호환되는 row-/column-major 순서 유지

## 핵심 기여

- **핵심 Contribution:** SoC-PIM 협업 온디바이스 LLM 가속을 위한 PIM과 SoC 프로세서 간 효율적 데이터 공유 문제를 해결하는 최초의 메모리 시스템 솔루션 제안.
- **성능 향상:** 4개 플랫폼에서 TTFT 평균 2.37×~2.89×, TTLT 1.20× 향상 (SoC-PIM hybrid baseline 대비)
- **프로그램 투명성:** 애플리케이션 수정 없이 기존 BLAS 라이브러리와 호환되는 row-/column-major 순서 유지
- **최소 수정:** OS와 메모리 컨트롤러에 대한 최소한의 수정으로 실현 가능한 솔루션
- **의의:** 엣지 디바이스에서 PIM 기술을 효과적으로 통합하기 위한 메커니즘을 제시하여, 온디바이스 LLM 추론의 반응성(responsiveness)을 크게 향상시킴. 향후 PIM 기반 엣지 AI 가속에 중요한 기반 기술로 활용 가능

## 주요 결과

- **구현 플랫폼:** NVIDIA Jetson AGX Orin 64GB, Apple Macbook Pro (M3 Max), Lenovo IdeaPad Slim 5 (Intel Core Ultra 7 155H), Apple iPhone 15 Pro (A17 Pro)
- **하드웨어 수정:** 메모리 컨트롤러에 MapID 기반 다중 PA-to-DA 매핑 지원 모듈 추가
  - MapID당 매핑 스킴을 lookup table로 저장
  - 페이지 테이블 엔트리에서 MapID 비트 추가
- **소프트웨어 수정:**
  - pimalloc 사용자 레벨 라이브러리 (행렬 차원/dtype 기반 매핑 선택)
  - OS 메모리 할당자의 huge page 할당 시 MapID 기록
- **프레임워크:** Llama3-8B(TinyChatEngine/MLX), OPT-6.7B(Intel NPU Library), Phi-1.5(MLX Swift) FP16 정밀도
- **최소 수정 원칙:** OS와 메모리 컨트롤러에 대한 최소한의 수정으로 기존 커널과의 호환성 유지

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2025HPCA-summarize/facil-flexible-dram-address-mapping-for-soc-pim-llm-inference.md|전체 요약 보기]]
