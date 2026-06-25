---
tags: [paper, 2025, 2025MICRO, topic/dram, topic/gpu, topic/llm-inference, topic/memory-tiering, topic/pim]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO) 2025"
year: 2025
summary_path: "../paper-summaries/2025MICRO-summarize/stratum-tiered-monolithic-3d-stackable-dram-for-moe-serving.md"
---

# Stratum: System-Hardware Co-Design with Tiered Monolithic 3D-Stackable DRAM for Efficient MoE Serving

**Venue:** IEEE/ACM International Symposium on Microarchitecture (MICRO) 2025
**저자:** Yue Pan, Zihan Xia, Po-Kai Hsu, Lanxiang Hu, Hyungyo Kim, Janak Sharda, Minxuan Zhou, Nam Sung Kim, Shimeng Yu, Tajana Rosing, Mingu Kang (UC San Diego / Georgia Tech / UIUC / Illinois Tech)

## 개요

- Transformer 기반 LLM이 다양한 분야에서 최첨단 성능을 달성하며, LLaMA 3.1(405B), DeepSeek-V3(671B), Kimi-K2(1T) 등 모델 규모가 전례 없이 증가
- **Mixture of Experts(MoE) 아키텍처**가 희소 게이팅을 활용하여 소수의 전문가 서브네트워크만 활성화함으로써, 추론 비용은 작고 밀집된 모델 수준으로 유지하면서도 거대 파라미터 용량 달성 — OLMoE, Mixtral, DeepSeek V3 등에서 표준화
- 그러나 MoE 모델은 **MoE 레이어에서 도입되는 막대한 데이터 볼륨**으로 인해 하드웨어 배포에 어려움 겪음:
  - MoE 모델은 거대한 용량 필요 (Mixtral 8×7B에서 전문가 가중치가 전체 모델의 **95% 이상** 차지)
  - 전문가 사용이 동적으로 변하며 사전 예측 불가능 → 이질적 컴퓨팅 유닛 간 부하 불균형 초래
  - 추론 시 token당 소수의 전문가만 활성화되지만, 전체 가중치가 메모리에 상주해야 함
- **HBM(High Bandwidth Memory)**이 현재 고성능 GPU의 주요 메모리 솔루션이지만:
  - HBM3 기준 800GB/s 대역폭 제공이나, interposer를 통한 외부 대역폭은 여전히 **GPU 컴퓨팅 리소스의 충분한 활용을 제한** (특히 LLM 디코딩 같은 memory-bound 연산)
  - TSV(T Through-Silicon Via) 기반의 수직 연결은 **pitch 10μm로 내부 대역폭 한계**
- 기존 PIM/NMP 접근법의 한계:
  - HBM base die 위의 NMP: TSV I/O를 통한 수직 데이터 전송으로 제한된 대역폭
  - 메모리 die 내 로직 통합: DRAM 공정은 계산 최적화가 아닌 저장 최적화 → 높은 PPA 오버헤드, 열 문제
  - Mono3D DRAM의 잠재력: **Cu-Cu hybrid bonding(1μm pitch)**으로 HBM 대비 약 **5배 더 촘촘한 수직 인터커넥트**, 높은 내부 대역폭 가능
  - 그러나 Mono3D DRAM은 **수직 스케일링에 따른 레이어 간 접근 지연 차이**가 심각 (상위 레이어 1.11ns vs 하위 레이어 22.88ns, Figure 2)

## 방법론

### 3.1. Mono3D DRAM 아키텍처

- **구조**: 수평적 1T1C DRAM 셀을 수직으로 적층, wordline staircase와 수직 연결 bitline 사용
- **레이턴시 특성**: wordline staircase 구조로 인해 레이어별로 선형적으로 증가하는 접근 지연 — 최상위 레이어 1.11ns, 최하위 레이어 22.88ns (Figure 2)
- **8개 타이밍 티어**로 분류:最快的 tier가 가장 느린 tier보다 **1.6배 빠름**
- **HBM 대비 장점**: Cu-Cu hybrid bonding(1μm pitch)으로 TSV(10μm pitch) 대비 약 5배 더 촘촘한 수직 인터커넥트, 로직 die와 face-to-face 직접 연결
- **밀도**: 2.156 Gb/mm² — 최신 32Gb DDR5 die(0.417 Gb/mm²) 대비 **5.2배 높음**
- **내부 대역폭**: 티어에 따라 **19.01~30.34 TB/s**

### 3.2. Stratum NMP 프로세서

- **Chip-level**: 로직 die에 16개 PU(Processing Unit) 배치, 양방향 링 기반 온칩 네트워크로 상호 연결
- **Channel-level PU**: 근 bank PE 클러스터, 공유 메모리, 특수 기능 엔진, 링 라우터, 리듀서로 구성
  - 특수 기능 엔진: 256-way SIMD로 Softmax, SiLU, GeLU 등 비선형 연산 처리
  - 링 라우터: 로컬 스위치와 집계기로高效 efficient inter-PU 통신 및 in-situ 데이터 리덕션
- **Bank-level PE**: 
  - 텐서 코어: n개 병렬 k-tap dot-product 엔진 + n개 로컬 어큐뮬레이터
  - **Tiering Table**: 행 주소를 티어 ID로 변환하여 tRCD(Activation Latency) 적응형 제어
  - Row Swap Buffer: 티어 간 데이터 이동 지원 (외부 데이터 fetch 불필요)
  - 이중 버퍼링된 psum 메모리로 중간 결과 누적과 출력 전송 동시 지원
- **성능**: 128 TFLOPS (64k MAC 유닛, 1GHz, FP16)
- **면적**: 로직 die 전체 76.63mm² (121mm² 예산 대비 63% 활용)
- **소비전력**: 피크 144.53W (DRAM 104W + 로직 42.67W)

### 3.3. 전문가 계산 매핑

- **토큰 라우팅**: xPU에서 경량 라우터가 토큰을 전문가에 할당 (연산 비용 무시 가능)
- **행렬 분할 전략**:
  - GeMM1/GeMM2(Up Projection): 가중치 행렬을 수직으로 분할
  - GeMM3(Down Projection): 가중치 행렬을 수평으로 분할
  - 토큰 행렬 M 차원은 분할하지 않음 (가중치 중복 방지)
- **실행 흐름**: 
  1. xPU가 입력 토큰을 Mono3D DRAM에 전송
  2. 모든 PU가 텐서 병렬성으로 한 전문가씩 순차 처리
  3. 각 전문가: GeMM1, GeMM2 → SiLU → Hadamard → GeMM3 → Reduce-Scatter
  4. 전문가 출력의 가중 합으로 최종 토큰 생성
- **실행 최적화**: GeMM2와 활성화 함수 중첩, Reduce-Scatter와 다음 전문가 GeMM1 중첩, 가중 합 즉시 수행

### 3.4. Attention 처리

- **헤드 수준 병렬성**: PU를 여러 PU 그룹으로 유연하게 분할, 각 그룹에서 2개 이상의 헤드를 교차 처리
- **Softmax 처리**: 각 PU가 로컬 최대값/합산을 독리적으로 계산 후 스칼라 교환으로 글로벌 값 도출
- **성능**: q×k와 attn×v 연산 사이에서 Softmax 교차 실행으로 지연 최소화

## 핵심 기여

- **핵심 기여**: Mono3D DRAM 기반 MoE 서빙을 위한 최초의 시스템-하드웨어 공동 설계 솔루션 제안
- **성능**: GPU 기준선 대비 최대 8.29배 decoding throughput, 7.66배 에너지 효율 향상
- **혁신적 접근**: 
  - 인메모리 티어링으로 Mono3D DRAM의 수직 스케일링 한계를 장점으로 전환
  - 주제 인식 전문가 배치로 MoE 모델의 동적 특성을 활용한 최적화
- **비용 효율성**: 2.5D 실리콘 인터포저를 통한 GPU-Mono3D DRAM 통합으로 기존 GPU-HBM 아키텍처 대비 비용 절감 가능성
- **의의**: 고밀도 3D 적층 메모리와 근 메모리 처리의 융합을 통해 LLM 서빙의 메모리 병목을 근본적으로 해결하는 방향 제시

## 주요 결과

### 4.1. 전문가 사용 예측 (Topic-Aware Expert Placement)

- 사전 학습된 MoE 모델은 추론 시 **도메인별 전문가 전문화** 발생 — 예: LLaMA-4 Scout의 MMLU 서브셋에서 수학/논리 관련 주제의 **90% 이상**의 도메인 특화 전문가 친화성 (Figure 4)
- **DistillBERT 기반 주제 분류기**: 67M 파라미터, 6개 주제 분류, 94.5% (MMLU) / 85.0% (Chatbot Arena) 정확도
- 오프라인 프로파일링으로 주제별 전문가 사용 테이블 구축 → 온라인 서빙 시 쿼리 주제 분류 후 핫 전문가를 빠른 티어에 배치
- GPT-4o 기반 데이터 합성 파이프라인으로 분포 변화 대응

### 4.2. 데이터 배치 전략

- **4가지 데이터 유형**: 핫 전문가 가중치, 콜드 전문가 가중치, KV 캐시, 비-NMP 데이터
- 핫 전문가 → 빠른 티어, 콜드 전문가 → 느린 티어, 비-NMP 데이터(위치 임베딩 등) → 가장 느린 티어
- **전문가 스왑**: 토크 변경 시 전문가 가중치를 행 단위로 교환 — Row Swap Buffer를 활용한 내부 대역폭에서의高效 efficient swap
  - 스왑 오버헤드: 시간 <1ms (0.2~0.4%), 에너지 <0.03%로 무시 가능

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2025MICRO-summarize/stratum-tiered-monolithic-3d-stackable-dram-for-moe-serving.md|전체 요약 보기]]
