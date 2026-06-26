---
tags: [paper, 2020, 2020MICRO, topic/dram, topic/rowhammer]
venue: "53rd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '20)"
year: 2020
summary_path: "../paper-summaries/2020MICRO-summarize/graphene-strong-yet-lightweight-row-hammer-protection.md"
---

# Graphene: Strong yet Lightweight Row Hammer Protection

**Venue:** 53rd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '20)
**저자:** Yeonhong Park, Woosuk Kwon, Jung Ho Ahn, Eojin Lee, Jae W. Lee, Tae Jun Ham (서울대학교)

## 개요

- Row Hammer는 공격자가 DRAM row를 빈번히 활성화(ACT)하여 인접 row의 셀에서 전하 누수를 유발하고 비트 플립을 일으키는 보안 위협
- DDR3의 Row Hammer 임계값이 약 139K인 반면, 기술 스케일링으로 DDR4에서는 50K로 감소 — 보호가 점점 어려워지고 있음
- 최신 DDR4 시스템도 특정 메모리 접근 패턴에서 여전히 Row Hammer에 취약 (Trrespass, S&P 2020)
- Row Hammer 공격이 PC, 모바일, 클라우드 서버 등 모든 플랫폼에서 시스템 크래시, 권한 상승, 전체 시스템 탈취에 악용 가능
- 기존 해결책의 한계:
  - **확률적 방식 (PARA):** 낮은 하드웨어 복잡도 대신 충분한 보호 수준 확보를 위해 상당한 추가 리프레시 필요, 확실한 보호 보장 불가 (false negative 존재)
  - **카운터 기반 방식 (CBT, TWiCe):** 높은 정밀도와 낮은 비용을 동시에 달성하는 것이 도전 과제, 최신 솔루션도 여전히 높은 영역 오버헤드
  - **소프트웨어 기반 방식:** 시스템 소프트웨어 스택의 침습적 수정 필요, 실용화 어려움
- 비 인접 row에 대한 Row Hammer (±n) 영향도 점점 중요해지고 있으나 기존 연구에서 충분히 다루지 않음

## 방법론

### 3.1. Misra-Gries 알고리즘 기반 테이블 관리

- **핵심 알고리즘:** 데이터 스트림에서 빈번한 요소를 공간 효율적으로 식별하는 Misra-Gries 알고리즘 적용
- **카운터 테이블 구조 (Figure 4):**
  - 두 개의 CAM 배열로 구성:
    - **Address CAM:** row 주소 저장 (각 항목 ⌈log₂(row_num)⌉ 비트, 64K row의 경우 16비트)
    - **Count CAM:** 추정된 활성화 횟수 저장 (각 항목 14비트 + 1비트 오버플로우 = 총 15비트)
  - **Spillover Count Register:** 테이블에서 가장 작은 추정 카운트值를 추적
- **테이블 업데이트 알고리즘 (Figure 5, Pseudo-code):**
  ```
  process_activation(activated_addr):
    if (i ← ROW_ADDR_CAM.SEARCH(activated_addr)):
      // Row Address HIT: 기존 항목의 카운트 증가
      incremented_cnt ← COUNT_CAM.READ(i) + 1
      COUNT_CAM.WRITE(i, incremented_cnt)
    else:
      // Row Address MISS
      if (i ← COUNT_CAM.SEARCH(SPCNT)):
        // Spillover Count와 같은 값의 엔트리 교체
        incremented_cnt ← SPCNT + 1
        ROW_ADDR_CAM.WRITE(i, activated_addr)
        COUNT_CAM.WRITE(i, incremented_cnt)
      else:
        // 교체 불가: Spillover Count만 증가
        SPCNT++
  ```
- **오버플로우 비트 활용:** 카운트가 T(임계값)에 도달하면 오버플로우 비트 설정 후 카운트 리셋 → 21비트 → 15비트로 축소
- **Critical Path:** 주소 미스 + 엔트리 교체 시 3개 CAM 연산 (2개 검색 + 1개 쓰기)

### 3.2. 수학적 보장 (보안 증명)

- **Lemma 1:** 어떤 시점에서든 모든 엔트리의 추정 카운트 ≥ 실제 카운트
  - 강한 귀납법으로 증명: 초기값 0(추정=실제), 엔트리 교체 시 Spillover Count + 1 ≥ 실제 카운트
- **Lemma 2:** Spillover Count ≤ W / (N_entry + 1)
  - Spillover Count가 모든 추정 카운트보다 작거나 같으므로, 최대값은 모두 같을 때
- **Theorem (False Negative 없음):** row X의 실제 카운트가 T−1에서 T로 증가하는 시점에서:
  - 추정 카운트 = 실제 카운트이면 즉시 victim row refresh 수행
  - 추정 카운트 > 실제 카운트이면 과거에 이미 victim row refresh 수행됨

### 3.3. 설정 및 리셋 윈도우

- **T (임계값) 설정:** `T < T_RH / 2 + 1`
  - 일반 리프레시가 현재 또는 이전 리셋 윈도우에서 발생하므로, 단일 row의 최대 ACT 수는 T−1
- **테이블 크기 (N_entry):** `N_entry > 2 × W / (T − 1)`
  - W: 리셋 윈도우 내 최대 ACT 수 (기본 1,360K)
- **리셋 윈도우 조정 (Section III-C):**
  - 윈도우를 tREFW/k로 줄이면 T와 N_entry 재구성 가능
  - k=2 선택: N_entry=81, 추가 리프레시는 약간 증가하지만 영역 절약 효과
  - k 증가 시 테이블 크기는 급속히 포화, 추가 리프레시는 지속 증가 (Figure 6)

### 3.4. 비 인접 Row Hammer 보호 (Section III-D)

- **±n Row Hammer:** 공격자 row에서 n행 떨어진 row까지 영향 가능
- **확장 방법:**
  - T 값 감소: `T < T_RH / (4(1 + μ₂ + ... + μ_n) + 1)`
  - N_entry 증가: 인자 (1 + μ₂ + ... + μ_n) 배
  - μ_i: 거리 i에서의 전하 간섭 계수 (μ_i < 1, 거리 증가에 따라 감소)
- **전하 간섭 모델:** μ_i = 1/i² 가정 시 전체 인자 ≈ 1.64배 → 테이블 크기 1.64배 증가 (_manageable_)
- **추가 리프레시:** n배 증가하지만, 현실적 워크로드에서는 T 도달 확률이 극히 낮음

## 핵심 기여

- **핵심 Contribution:**
  - Misra-Gries 알고리즘을 Row Hammer 방지에 최초로 적용, 영역 효율적인 카운터 기반 방식 제안
  - 수학적으로 증명된 보호 보장 (false negative 없음, false positive 엄격히 경계)
  - TWiCe 대비 약 15배 적은 테이블 비트로 동등 이상의 보호 달성
- **성능 향상:**
  - 현실적 워크로드: 에너지/성능 오버헤드 거의 0%
  - 최악 adversarial 패턴: 추가 리프레시 에너지 0.34%에 불과
  - 영역: bank당 약 2,500 비트 (TWiCe 대비 15배 절감)
- **의의:**
  - 기술 스케일링으로 Row Hammer 임계값이 낮아지는 미래 DRAM에도 확장 가능한 보호 방식
  - 비 인접 row 보호까지 확장 가능하여 실제 시스템에서의 실용성 높음
  - 기존 확률적 방식의 보호 보장 부재와 카운터 기반 방식의 높은 영역 비용을 동시에 해결

## 주요 결과

- **하드웨어 구조:** 메모리 컨트롤러(MC) 내부에 Graphene 배치
- **DRAM 인터페이스 확장:** NRR(Nearby Row Refresh) 커맨드 추가 (DDR3의 TRR과 유사)
  - DRAM 디바이스가 NRR 커맨드 수신 시 지정된 aggressor row의 인접 row들을 리프레시
- **테이블 구현:** CAM 기반 (Address CAM + Count CAM + Spillover Count Register)
- **구현 언어:** Verilog (하드웨어 설계)
- **평가 도구:** McSimA+ (메모리 시뮬레이터), GPU-Sim 기반 확장
- **시스템 구성:** 4개 메모리 채널, 각 채널당 1개 single-rank DDR4 DIMM (16 banks/rank)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]


## 전체 요약

[[../paper-summaries/2020MICRO-summarize/graphene-strong-yet-lightweight-row-hammer-protection.md|전체 요약 보기]]
