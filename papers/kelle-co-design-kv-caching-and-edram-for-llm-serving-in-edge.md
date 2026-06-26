---
tags: [paper, 2025, 2025MICRO, topic/dram, topic/llm-inference]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO 2025)"
year: 2025
summary_path: "../paper-summaries/2025MICRO-summarize/kelle-co-design-kv-caching-and-edram-for-llm-serving-in-edge.md"
---

# Kelle: Co-design KV Caching and eDRAM for Efficient LLM Serving in Edge Computing

**Venue:** IEEE/ACM International Symposium on Microarchitecture (MICRO 2025)
**저자:** Tianhua Xia (New York University, Tandon School of Engineering), Sai Qian Zhang (New York University, Tandon School of Engineering)

## 개요

- 엣지 기기에서 LLM 추론 시 KV 캐시가 시퀀스 길이에 비례하여 선형적으로 증가 → LLaMA2-7B의 8192 시퀀스(FP16)에서 KV 캐시만 4GB 차지, 총 실행 레이턴시가 온칩 SRAM과 오프칩 DRAM 간 빈번한 메모리 접근에 의해 제약 (Figure 3a: SRAM 4MB→8MB 확장 시 평균 1.27× 속도 향상)
- 엣지 기기의 면적/전력 예산 제약 → SRAM 용량 확장은 면적 26%, 전력 29% 증가 (8MB 기준) → 다른 중요 구성요소의 리소스 감소
- eDRAM은 3T 셀 구조(6T SRAM 대비 트랜지스터 절반)로 동일 면적에서 2× 이상의 저장 밀도 달성, 누설 전력 3.5× 감소 (Table 1: 4MB 기준 면적 3.2mm² vs SRAM 7.3mm²)
- **그러나 eDRAM의 치명적 단점:** 데이터 유실 방지를 위한 주기적 리프레시 필요 → 리프레시가 전체 에너지의 최대 46%를 차지 (Figure 3c), 평균 1.7× 에너지 증가
- 기존 KV 캐시 압축 기법 (StreamLLM, H2O 등)은 프로파일링이나 추가 계산 필요 → 엣지 기기에 적합하지 않음

## 방법론

### 3.1. AERP: 어텐션 기반 퇴출 및 재계산

**퇴출 정책 (Eviction):**
- 중요도 점수: s_n^h = Σ A_{n,i}^h (토큰 n의 어텐션 점수 합산, Equation 3)
- 새 토큰 도착 시 중요도 가장 낮은 토큰의 KV 벡터 퇴출 (Figure 6a,b)
- 초기 토큰과 최근 토큰은 성능 영향으로 인해 보존 (StreamLLM/H2O와 동일)
- 각 어텐드별로 중요도 점수가 다르므로 헤드별 퇴출 패턴 상이

**재계산 정책 (Recomputation):**
- eDRAM은 단명(transient) 데이터 저장에 적합 → KV 벡터 대신 입력 벡터 x_N 저장 시 K,V 재계산 가능
- 인기도 θ > 50%의 토큰(2개 이상 헤드에서 중요): KV 벡터 대신 입력 벡터 저장 → 저장 비용 2×(C/H)×θ×H → C로 절감 (Figure 6c)
- 재계산 비용 최소화: RSA가 행렬-행렬 곱셈에 최적화 → x_4와 x_5를 결합해 한 번에 처리 (Figure 11a,b)
- 사전 단계: 중요도 기반 퇴출 후 인기 토큰의 입력 벡터 저장 형식 결정 → 디코딩 중 변경 없음

### 3.2. 2DRP: 2차원 적응형 리프레시 정책

- **LLM의 KV 캐시 오류 내성 실험 (Figure 8a):** 비트 플립 오류율 10⁻³ 이하에서 PPL 증가 미미 (<0.1), 초과 시 급격히 증가 → 오류 내성 존재
- **토큰 중요도 기반 적응형 리프레시 (Figure 8b):** 고점수 토큰(HST)의 비트 플립이 저점수 토큰(LST)보다 정확도에 더 큰 영향 → HST에 더 높은 리프레시 빈도 필요
- **비트 위치 기반 적응형 리프레시 (Figure 8c):** MSB(bits 15-8)의 비트 플립이 LSB(bits 7-0)보다 정확도에 더 큰 영향 → MSB에 더 높은 리프레시 빈도 필요
- **2DRP 구현:** HST-MSB(최고 빈도) → HST-LSB → LST-MSB → LST-LSB(최저 빈도) 4단계 리프레시 (Figure 7b,c)
- 실험 설정: HST-MSB 360μs, HST-LSB 5400μs, LST-MSB 1440μs, LST-LSB 7200μs, 평균 리프레시 간격 1.05ms, 평균 리텐션 실패율 2×10⁻³

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1. 메모리 서브시스템 (Figure 10)

- **혼합 eDRAM-SRAM 구조:** 2MB SRAM(가중치), 256KB 활성화 eDRAM, 4MB KV 캐시 eDRAM
- KV 벡터 MSB/LSB를 별도 eDRAM 뱅크에 분리 저장 → 2DRP의 4단계 리프레시 구현
- 중요도 점수는 4비트 정밀도로 동적 계산 → 레지스터 파일에 저장, 토큰별 4개 뱅크 공유 주소
- 32 뱅크 구분 (Key MSB 8 + Key LSB 8 + Value MSB 8 + Value LSB 8) → 32×32 RSA에 충분한 대역폭 제공
- 리프레시 레이턴시 숨김: 모델이 KV 벡터를 사용하지 않는 시점에 리프레시 수행

### 4.2. 재구성 가능한 수영 배열 (RSA)

- 32×32 2D 수영 배열, 8비트 MAC 연산, 가중치 고정(dataflow)
- 재계산 최적화: 현재 토큰의 입력 벡터와 재계산할 토큰의 입력 벡터를 행렬로 결합 → RSA 활용도 극대화 (Figure 11a,b)
- 재계산 오버헤드 최소화: 동일 RSA에서 현재 토큰 처리와 재계산 병렬 수행

### 4.3. 시스톨릭 이바이터 (Systolic Evictor)

- AERP 알고리즘의 토큰 퇴출을 가속화하는 전용 연산 유닛
- 어텐션 점수(QK^T)를 softmax 없이 직접 계산 → 중요도 점수 실시간 업데이트
- 등록 체인(M)이 주기적으로 최소 중요도 점수를 상→하로 전파 → RSA 연산과 동시에 최소값 탐색 (Figure 11c,d)
- 면적 0.06mm² (온칩 면적의 0.6%), 전력 0.028W (온칩 전력의 0.4%)
- LLM 실행 정지 없이 토큰 퇴출 수행 → 에너지 효율 5%, 레이턴시 7% 향상

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]


## 전체 요약

[[../paper-summaries/2025MICRO-summarize/kelle-co-design-kv-caching-and-edram-for-llm-serving-in-edge.md|전체 요약 보기]]
