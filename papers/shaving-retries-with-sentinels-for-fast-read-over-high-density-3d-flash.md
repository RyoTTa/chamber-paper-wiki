---
tags: [paper, 2020, 2020MICRO, topic/storage]
venue: "53rd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '20)"
year: 2020
summary_path: "../paper-summaries/2020MICRO-summarize/shaving-retries-with-sentinels-for-fast-read-over-high-density-3d-flash.md"
---

# Shaving Retries with Sentinels for Fast Read over High-Density 3D Flash

**Venue:** 53rd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '20)
**저자:** Qiao Li, Min Ye, Yufei Cui, Liang Shi, Xiaoqiang Li, Tei-Wei Kuo, Chun Jason Xue (City University of Hong Kong / East China Normal University / YEESTOR Microelectronics)

## 개요

- 고밀도 3D NAND 플래시 메모리의 수요가 데이터의 기하급수적 성장과 함께 급증하고 있으며, TLC(Triple-Level Cell)가 현재 주류이며 QLC(Quad-Level Cell)가 곧 상용화될 전망
- 고밀도 플래시의 원시 비트 오류율(RBER, Raw Bit Error Rate)이 10⁻³~10⁻² 수준으로, ECC(Error Correction Codes)의 비용이 급격히 증가
- 기본 읽기 전압으로 읽기 실패 시, 전압을 조정한 후 read retry를 수행해야 하며, 이로 인해 읽기 성능이 크게 저하됨
- MSB(Most Significant Bit) 페이지는 단일 페이지 읽기 위해 여러 읽기 전압이 필요하여 특히 취약하며, 올바른 읽기 전압 위치를 찾아야 함
- 기존 연구의 한계:
  - **전압 이동 추정 방식:** 정확한 추정이 어렵고, 특히 3D NAND에서는 오류 특성이 다양하여 더 큰 오버헤드 발생
  - **최적 전격 추적 방식 (Lee et al.):** 주기적으로 최적 전압을 업데이트하는 비용이 높음 (FTL에 정보 저장 필요)
  - **Shim et al.:** 층별 최적 전압이 동일하다는 특성을 활용하나, 층 간 변동이 크고 최적 전압을 찾는 과정에서 높은 비용 발생
- 온도 변화로 인해 최적 읽기 전격이 짧은 시간 내에 급격히 변할 수 있어 정적 접근법으로는 대응 불가

## 방법론

### 3.1. Error Difference 계산 및 최적 전압 추론

- **Up error / Down error 정의 (Figure 9):**
  - Sentinel 전압 Vi는 인접 상태 Si-1과 Si 사이에 위치
  - **Up error:** Si-1의 셀이 Si로 잘못 읽힌 오류
  - **Down error:** Si의 셀이 Si-1로 잘못 읽힌 오류
  - Error difference d = up error 수 - down error 수
  - d < 0이면 최적 전압이 기본 전격보다 낮음을 의미 (상태가 왼쪽으로 이동)

- **최적 전압 추론 알고리즘:**
  ```
  infer_optimal_voltage(wordline):
    // 1. 기본 전압으로 읽기 시도
    read_data = read_with_default_voltage(wordline)
    if read_fails:
      // 2. Sentinel 전압으로 추가 읽기 (LSB 페이지 읽기 수준)
      sentinel_data = read_with_sentinel_voltage(wordline)
      d = count_up_errors(sentinel_data) - count_down_errors(sentinel_data)
      // 3. 다항식 함수로 최적 오프셋 추론
      V_optimal = f(d)  // degree-5 다항식 피팅
    // 4. 다른 읽기 전압들의 최적값은 선형 상관관계로 추론
    for each read_voltage Vi:
      V_optimal_i = V_optimal_sentinel + correlation_offset_i
  ```

- **피팅 함수:** 수백 쌍의 (d, V_optimal) 데이터를 수집하여 degree-5 다항식으로 피팅 (Figure 10)
- QLC 플래시에서는 15개 읽기 전압(V1~V15) 존재, 각 전압의 최적값이 서로 강한 선형 상관관계

### 3.2. Calibration 절차

- **문제:** sentinel cell의 오류 분포가 전체 워드라인의 오류 분포와 다를 수 있음
- **두 가지 실패 케이스 (Figure 11):**
  - Case 1: 추론된 전압 오프셋이 실제보다 작음 → 같은 방향으로 더 조정 필요
  - Case 2: 추론된 전압 오프셋이 실제보다 큼 → 약간 되돌려야 함
- **통합 보정 방법:** 첫 번째 읽기(기본 전압)와 두 번SENTinel 추론 전압으로의 읽기 차이를 비교하여 케이스 구분
- 보정 후 94%의 워드라인에서 최적 전압 성공적으로 획득 (추론만으로는 83%)

### 3.3. Sentinel Cell 설계

- 각 워드라인에 소수의 셀을 sentinel cell로 예약 (0.2% 공간 오버헤드)
- Write 시 sentinel cell를 sentinel 전압의 양쪽 상태로 프로그래밍
- 읽기 시 sentinel cell의 원래 프로그래밍 데이터와 읽기 데이터를 비교하여 정확한 오류 방향과 크기 파악
- 제조 과정에서 한 번 측정한 전압 간 상관관계를 같은 배치의 모든 칩에 기록 가능 (추가 측정 불필요)

## 핵심 기여

- Sentinel cell을 활용한 읽기 전격 추론 방식으로 고밀도 3D 플래시의 read retry를 82% 감소
- 추가 읽기/쓰기 오버헤드 없이 최적 전격 추론 가능하며,仅 0.2% 공간 오버헤드로 실현
- 94%의 케이스에서 최적 전격을 즉시 획득하여 읽기 성능을 74% 향상
- 제조 시 한 번 측정한 전압 상관관계를 같은 배치의 모든 칩에 적용할 수 있어 확장성 우수
- 3D TLC 및 QLC 플래시 모두에서 효과적으로 동작하며,未来的 고밀도 플래시 기술에도 적용 가능

## 주요 결과

- 평가 대상: 실제 3D TLC 및 QLC 플래시 메모리 칩
- 평가 도구: SSDSim 트레이스 기반 시뮬레이터
- 워크로드: Microsoft Research Cambridge의 8개 실 워크로드
- TLC 칩: 5000 P/E 사이클, 1년 리텐션 시간 (고온으로 가속화)
- QLC 칩: 최적화된 읽기 전격 조정 방식 미장착 상태에서 평가

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2020MICRO-summarize/shaving-retries-with-sentinels-for-fast-read-over-high-density-3d-flash.md|전체 요약 보기]]
