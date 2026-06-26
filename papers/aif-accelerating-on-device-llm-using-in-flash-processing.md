---
tags: [paper, 2025, 2025ISCA, topic/compression, topic/dram, topic/llm-inference, topic/storage]
venue: "ISCA '25 (52nd Annual International Symposium on Computer Architecture), June 21–25, 2025, Tokyo, Japan"
year: 2025
summary_path: "../paper-summaries/2025ISCA-summarize/aif-accelerating-on-device-llm-using-in-flash-processing.md"
---

# AiF: Accelerating On-Device LLM Inference Using In-Flash Processing

**Venue:** ISCA '25 (52nd Annual International Symposium on Computer Architecture), June 21–25, 2025, Tokyo, Japan
**저자:** Jaeyong Lee, Hyeunjoo Kim, Sanghun Oh, Myoungjun Chun, Myungsuk Kim, Jihong Kim

## 개요

- 최신 LLM의 메모리 수요가 급증: Meta의 LLaMA-3 시리즈 기준 최소 8B 모델도 16GB 이상의 메모리 필요. 그러나 고급 스마트폰은 8~12GB, 노트북은 약 16GB의 DRAM을 보유
- SSD 오프로딩은 DRAM 대비 50배 이상의 비트 밀도를 제공하지만, SSD 읽기 대역폭(4~8 GB/s)은 DRAM(80~100 GB/s) 대비 현저히 낮음
- 온디바이스 LLM 추론은 arithmetic intensity가 극도로 낮음 (1~2 ops/byte), 모델 파라미터 전체를 토큰 생성마다 반복 읽어야 하므로 토큰 생성 속도가 읽기 대역폭에 직접 의존
- **수치적 근거:** max tokens/s ≤ read bandwidth (GB/s) / model size (GB). 40GB 파라미터 오프로딩 시理淪적으로 0.1~0.2 tokens/s 이하로 제한됨
- 기존 In-Storage Processing (ISP) 솔루션의 최대 대역폭은 12.8~19.2 GB/s로, 실시간 챗봇에 필요한 ~100 GB/s 대역폭에 턱없이 부족
- 16개 플래시 칩 병렬 읽기도 25.6 GB/s에 불과하여 LLM 추론 요구사항 미충족
- LLM 추론은 오류에 극도로 민감하여 기존 IFP 연구의 오류 허용 범위를 적용 불가

## 방법론

### 3.1. Charge-Recycling Read (cr-read)

- 기존 NAND 플래시 읽기는 3단계: precharge → evaluation → discharge. 각 워드라인마다 이 3단계 반복
- cr-read는 동일 블록 내 연속 워드라인 읽기 시 discharge 대신 recycling 단계 사용
  - 이전 워드라인을 VREF(3.5V)에서 VPASS(6V)로 충전 (단일 워드라인만)
  - BL은 소폭 리충전 (평가 중 전압 드롭 미미)
- **수식:**
  - 기존: tR = tPRE + tEVAL + tDISCH
  - cr-read: tR = tRECY + tEVAL (tRECY << tPRE)
- **성능:** tR 64% 감소, 유효 대역폭 6.4 GB/s (기존 대비 2.8x), 에너지 72.1% 절감 (18.278 → 5.098 pJ/bit)
- **구현:** X-데코더의 전압 제어와 플래시 스케줄러의 타이머 코드 수정만으로 구현 가능

### 3.2. Bias-Error Encoding (be-enc)

- TLC NAND의 3페이지(LSB, CSB, MSB) 간 신뢰성 차이를 의도적으로 확대
- **기존 (2,3,2) coding:** LSB=2회, CSB=3회, MSB=2회 감지 → 균형잡힌 tR
- **제안 (1,3,3) coding:** LSB=1회, CSB=3회, MSB=3회 감지 → LSB 우선
- LSB 페이지 비트 오류율 80% 감소 (4K P/E + 1년 보존 기준)
- MSB 페이지 tR 증가(2→3회 감지)는 일반 I/O에만 영향, SSD 외부 대역폭이 bottleneck이므로 실질적 성능 영향 미미
- **근거 1:** tR 증가에도 SSD 내부 대역폭은 외부 대역폭(4-8 GB/s)에 의해 제한됨
- **근거 2:** 현대 SSD의 ECC 마진이 충분히 큼 (LDPC soft-decision 기반)

### 3.3. AiFChip 아키텍처

- **Page Buffer 재활용:** be-enc로 단일 감지로 읽으므로 불필요한 page latch를 입력 벡터 버퍼로 활용
- **온칩 GEMV 흐름:**
  1. 컨트롤러가 GEMV 명령 전송 (벡터 차원, 블록 ID, 오프셋 등)
  2. 입력 벡터를 PB에 로드
  3. 플래인이 매트릭스를 순차 읽기
  4. PEs에서 곱셈-누적 연산 (INT8 곱셈기 + adder tree)
  5. ECC LITE로 오류 정정 후 연산
  6. 결과를 FIFO에 저장, 라운드로빈으로 회수
- **면적/전력:** 0.209 mm² (플래시 칩 면적의 ~0.2%), 51.68 mW 평균 전력 (87%가 ECC)

## 핵심 기여

- AiF는 플래시 칩 내 GEMV 연산 통합으로 온디바이스 LLM 추론의 대역폭 병목을 근본적으로 해결
- **핵심 기여:** cr-read (대역폭 2.8x) + be-enc (오류율 80% 감소) + ECC LITE (면적/전력 15x 절감)의 통합 설계
- SSD 오프로딩 대비 14.6x, 인메모리 대비 1.4x throughput 향상
- 메모리 사용량 대폭 감소하면서 실시간 추론 가능 → 엣지 디바이스에서의 대규모 LLM 배포 가능성을 입증

## 주요 결과

- **ECC LITE:** BCH 디코더 세트, 1KiB당 최대 10비트 오류 정정, 6.4 GB/s Throughput
- **PE:** INT8 곱셈기 + adder tree로 GEMV 연산 지원
- **기술 노드:** 45nm, 200 MHz 동작 주파수로 합성
- **AiFSSD:** 16개 AiFChip으로 구성된 1TB SSD, 내부 읽기 대역폭 102.4 GB/s

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2025ISCA-summarize/aif-accelerating-on-device-llm-using-in-flash-processing.md|전체 요약 보기]]
