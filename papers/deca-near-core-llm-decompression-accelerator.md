---
tags: [paper, 2025, 2025MICRO, topic/cache, topic/compression, topic/dram, topic/llm-inference, topic/virtual-memory]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO 2025)"
year: 2025
summary_path: "../paper-summaries/2025MICRO-summarize/deca-near-core-llm-decompression-accelerator.md"
---

# DECA: A Near-Core LLM Decompression Accelerator Grounded on a 3D Roofline Model

**Venue:** IEEE/ACM International Symposium on Microarchitecture (MICRO 2025)
**저자:** Gerasimos Gerogiannis (Intel; University of Illinois at Urbana-Champaign), Stijn Eyerman (Intel), Evangelos Georganas (Intel Labs), Wim Heirman (Intel), Josep Torrellas (University of Illinois at Urbana-Champaign)

## 개요

- LLM 추론에서 Fully-Connected (FC) 레이어의 GeMM이 next-token 생성 시간의 85–95%를 차지하며, 이는 메모리 대역폭에 절대적으로 의존적 (Table 1: DDR5에서 95% 이상, HBM에서 85–90%)
- 메모리 대역폭 병목을 완화하기 위해 저비트 양자화(quantization)와 희소화(sparsification)를 적용하지만, TMUL 같은 하드웨어 GeMM 엔진은 BF16/INT8 형식의 밀집(dense) 타일만 처리 가능 → 압축된 타일의 역양자화(dequantization)와 역희소화(de-sparsification) 필요
- 기존 소프트웨어 기반 해소 (Intel libxsmm): AVX 벡터 연산으로 타일 압축 해제 후 TMUL에 전달 → HBM 환경에서 심각한 비효율 발생.的传统 2D Roofline 모델로는 이 병목을 설명 불가 (Figure 3b: BF8_5%에서 Optimal 대비 5.25× 격차)
- HBM 탑재 SPR 서버에서 압축된 GeMM의 관측 성능이 roofline 예측치와 크게 어긋나며, 벡터 처리 유닛(AVX)이 실제 병목 → 메모리 대역폭이나 TMUL 처리량이 아닌 벡터 디크萊스 성능이 시스템 성능을 결정

## 방법론

### 3.1. 3D 성능 모델 수식화

- 세 가지 처리 속도: MEM = MBW × AIXM, VEC = VOS × AIXV, MTX = MOS
  - AIXM: 메모리 바이트당 행렬 연산 수 (행렬-to-메모리 산술 강도)
  - AIXV: 벡터 연산당 행렬 연산 수 (행렬-to-벡터 산술 강도)
- **최종 성능 (Roof-Surface 방정식):** TPS = min{MBW × AIXM, VOS × AIXV, MOS}
- 3D 시각화: FLOPS(z축) = f(AIXM(x축), AIXV(y축)), 세 개의 하부 표면(subsurface)으로 구성된 곡면
- 기존 2D roofline 대비 정확도 대폭 향상 (Table 2: MXFP4에서 R-L은 25.2 TFLOPS 예측, R-S는 11.5 TFLOPS, 실제 10.6 TFLOPS)

### 3.2. BORD (Bounding Region Diagram)

- Roof-Surface를 2D 평면에 투영한 시각화 도구: 어떤 리소스(MEM/VEC/MTX)가 특정 커널의 성능을 제약하는지 식별
- HBM SPR에서 대부분의 압축 커널이 VEC-bound 영역에 위치 → 벡터 처리가 병목 (Figure 5a)
- DDR SPR에서는 대부분 MEM-bound → traditional roofline이 정확 (Figure 5b)
- 4× VOS 스케일링으로도 모든 커널을 VEC-bound에서 탈출시키지 못함 → 코어 리소스의 과도한 스케일링 불가피

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1. 시스템 통합 및 배치

- 각 CPU 코어에 하나의 DECA PE 연결 (Figure 6): PE, 제어 레지스터, TOut 레지스터로 구성
- 메모리 매핑 인터페이스로 코어가 명령을 쓰고 데이터를 읽음 → privileged store로 양자화 체계 구성
- L2 캐시를 통해 메모리 접근, L2 TLB 공유 → 코어의 가상 주소 공간 활용
- 멀티 프로세스 지원: 상태 저장/복원 메커니즘, SMT에서는 스레드당 DECA 접근 1개로 제한

### 4.2. 디크萊스 마이크로아키텍처 (Figure 10)

- **파이프라인 3단계:** Dequantization → Expansion (de-sparsification) → Scaling
  - Dequantization: SQQ에서 값을 읽어 LUT 배열로 BF16 값으로 변환
  - Expansion: 비트마스크 기반 Parallel Prefix Sum → XBAR로 영位置에 제로 삽입
  - Scaling: 그룹 양자화 시 스케일링 팩터 적용 → 최종 TOut 레지스터에 저장
- **더블 버퍼링:** 2개 Loader + 2개 TOut 레지스터 → 한쪽에서 로딩하면서 다른쪽에서 디크莱스 수행
- **vOp (DECA Vector Operation):** 각 vOp이 W개 요소를 한 사이클에 처리, 파이프라인 기법으로 매 사이클 새 청크 생성
- **LUT 배열:** L개의 "큰" LUT(각 256 엔트리) → 8비트 이하 양자화 값을 BF16으로 역변환, 6비트 이하에서는 4개 서브-LUT 병렬 사용

### 4.3. TEPL ISA 확장

- 기존 store 기반 호출: 매 반복마다 fence 필요 + 직렬화된 실행 → 통신 레이턴시 노출 (Figure 8)
- **TEPL:** 메타데이터 전달 + 디크莱스 완료까지 하나의 명령으로 결합 → fence 제거, 비순차 실행 가능 (Figure 9)
- TEPL Queue + 2개 실행 포트: ROB에 즉시 입고되어 스페큘레이티브 실행, 파이프라인 플러시 시 DECA에 스큐시 신호 전송
- 낮은 희소성(5% 밀도)에서 TEPL이 성능을 2배로 향상 (Figure 16)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2025MICRO-summarize/deca-near-core-llm-decompression-accelerator.md|전체 요약 보기]]
