---
tags: [paper, 2022, 2022ASPLOS, topic/dram, topic/rowhammer, topic/security, topic/virtual-memory]
venue: ""
year: 2022
summary_path: "../paper-summaries/2022ASPLOS-summarize/randomized-row-swap-mitigating-row-hammer-by-breaking-spatial-correlation.md"
---

# Randomized Row-Swap: Mitigating Row Hammer by Breaking Spatial Correlation between Aggressor and Victim Rows

**Venue:** 
**저자:** Gururaj Saileshwar (Georgia Tech / TU Graz), Bolin Wang (Univ. of British Columbia), Moinuddin Qureshi (Georgia Tech), Prashant J. Nair (Univ. of British Columbia)

## 개요

### 1.1 Row Hammer 공격의 심각성

Row Hammer (RH)는 공격자가 특정 DRAM row를 빠르게 반복 활성화(activate)하면 인접 row에서 bit flip이 발생하는 하드웨어 취약점. 2014년에 처음 발견 이후 지속적으로 공격 기법이 정교화되고 있음.

**RH Threshold의 급격한 감소:**

| DRAM 세대 | RH Threshold |
|-----------|-------------|
| DDR3 (old, 2014) | **139K** activations |
| DDR3 (new) | 22.4K |
| DDR4 (old) | 17.5K |
| DDR4 (new) | 10K |
| LPDDR4 (old) | 16.8K |
| LPDDR4 (new, 2020) | **4.8K** activations |

- 7년 동안 **약 30배** 감소 → 공격 용이성 크게 증가
- 공격자는 RH를 이용해 page table의 bit을 flip시켜 **권한 상승(privilege escalation)** 달성 가능
- 데이터 의존적 성질을 이용한 **정보 유출**도 가능

### 1.2 기존 Victim-Focused Mitigation의 근본적 한계

모든 기존 정밀 RH 방어(PRA, PARA, TRR, CRA, TWiCE, Graphene 등)는 동일한 완화 정책 사용: **aggressor row의 인접 victim row에 refresh 적용**

**한계 1: DRAM 매핑 정보 필요**
- victim row를 특정하기 위해 DRAM 내부 행 매핑 알아야 함
- DRAM 칩은 독점적 매핑 체계 사용, 메모리 컨트롤러에서 접근 불가능할 수 있음

**한계 2: 복잡한 공격 패턴에 취약 (Figure 1)**
- **Half-Double 공격 (Google, 2021):** Near-Aggressor에 대량 활성화 → mitigating refresh가 Far-Aggressor의 활성화를 도움 → distance-2에서 bit flip 발생
- Near-Aggressor에 900K 활성화 in 64ms로 100+ bit flip 유발 실험적 검증
- Distance 3 이상에서도 공격 가능 → victim-focused mitigation으로는 **불가능하게 방어**
- 공격 패턴이 점점 더 복잡해지는 추세 → 근본적 한계

### 1.3 핵심 인사이트: Aggressor-Focused Mitigation

기존 모든 방어는 aggressor와 victim 간의 **공간적 연결(spatial connection) 유지** → 공격자에게 충분한 시간 부여

**핵심 통찰:** aggressor row를 임의의 다른 위치로 이동시켜 공간적 상관관계를 **파괴**하면?
- 공격자가 같은 지역에서 공격 패턴을 구성할 수 있는 **시간 창을 극도로 축소**
- classical RH 패턴과 복잡한 패턴 모두에 대해 강력한 방어 가능

## 방법론

### 3.1 Hot-Row Tracker (HRT) (Section 4.2)

**Misra-Gries Tracker 사용 (Graphene [25]에서 제안):**
- ρ = ⌈T_A_max / T"⌉ = ⌈1.36M / 800⌉ = **1700 entries** 필요
- T_A_max = 1.36M activations (64ms 내 은행당 최대 활성화 수)
- guarantee: T" 이상의 활성화를 받는 모든 row를 감지

**3-entry Misra-Gries 트래커 작동 원리 (Figure 3):**
- 새 row가 도착하면:
  - 트래커에 있으면 → 해당 카운터 증가
  - 없으면 → 모든 카운터의 최솟값과 spill-counter 비교
    - 최솟값 > spill-counter → spill-counter만 증가
    - 최솟값 == spill-counter → 최소 카운터 엔트리를 새 row로 교체 (count = spill-counter + 1)

### 3.2 Row Indirection Table (RIT) (Section 4.3)

**역할:** swap된 row의 물리적 위치 변환 추적
- `<X, Y>` 튜플: Row-X와 Row-Y가 swap됨
- 양방향 조회 지원: X로 조회하면 Y, Y로 조회하면 X

**RIT 관리:**
- Epoch 끝에서 bulk reset하지 않음 (torrent of un-swap 방지)
- **Lazy eviction:** 새 엔트리 설치 시 이전 epoch의 엔트리를 교체
- **Lock-bit:** 현재 epoch에 설치된 엔트리는 eviction 불가 (보안 보장)
- Epoch 종료 시 lock-bit 리셋 → 이후 eviction 가능

**크기:** 최대 3400 튜플 (1700 swap 요청 × 2 튜플/요청)

### 3.3 Row Swap 연산 (Section 4.4)

**스왑 대상 선택:**
- 같은 은행 내 임의 row 선택 (128K rows 중)
- HRT/RIT에 없는 row만 후보 (98% 이상이 유효)
- Hardware PRNG 사용: 64-bit PRINCE cipher (CTR mode, **<2ns** 레이턴시)

**Swap 버퍼 구조:**
- 채널당 2개의 SRAM Swap-Buffer (각 8KB = DRAM row 크기)

**교환 과정 (Figure 4):**
1. Row-X 내용을 Swap-Buffer-1로 스트리밍 (365ns)
2. Row-Y 내용을 Swap-Buffer-2로 스트리밍 (365ns)
3. Swap-Buffer-1 내용을 Row-Y로 쓰기 (365ns)
4. Swap-Buffer-2 내용을 Row-X로 쓰기 (365ns)
5. RIT 업데이트

**총 지연 시간:** 약 **1.46μs** (4회 전송)
- Un-swap 포함 시: 약 **2.9μs**
- 최악의 경우 (re-swap + eviction): 약 **4.4μs**

### 3.4 스케일 가능한 하드웨어 구조 (Section 6)

**Conflict Avoidance Table (CAT):**
- MIRAGE [28]에서 영감을 받은 fully-associative 캐시 구조
- 두 개의 set-associative 테이블 (T1, T2)과 독립적 해시 함수 사용
- 각 set에 추가 way (over-provisioning)로 충돌 방지
- **6 extra ways:** 1030회 설치 후 충돌 발생 확률 practically zero (10^18년)

**스케일 가능한 RIT:**
- CAT 기반: 256 sets × 20 ways (14 demand + 6 extra)
- 각 엔트리: 28 bits (valid + lock + src + dest row-id)

**스케일 가능한 Misra-Gries Tracker:**
- CAT 기반: 64 sets × 20 ways
- 각 엔트리: 22 bits (valid + row-id + counter)
- SetMin 카운터: fully-associative search 없이 spill-counter 비교 가능

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1 공격 모델

- 공격자는 비특권(non-privileged) 프로세스로 네이티브 코드 실행 가능
- OS는 가상 메모리/페이지 테이블로 프로세스 격제 제공
- RH vulnerability가 있는 DRAM 하드웨어 사용
- **비타겟 공격(untargeted attack)** 기준: 어떤 DRAM 위치에서든 bit flip 발생 시 공격 성공

### 4.2 공격 전략 및 통계적 모델링 (Figure 7)

**공격자의 최적 전략:**
1. 은행 내 임의 row를 선택
2. T" activations 후 swap 유도
3. 다른 임의 row를 선택하여 반복
4. 이미 swap된 물리적 row를 우연히 발견하기를 기대 (birthday paradox 유사)

**Bucket-and-Balls 모델:**
- 공의 수: ⌊A × D / T"⌋ (D = Duty Cycle = 0.925)
- 통의 수: 128K (은행당 row 수)
- 각 공: T" activations 후 swap 발생
- **n번 swap된 row의 확률:** 이항분포(Bernoulli trial)로 계산

### 4.3 보안 수준 분석 (Table 4)

| RRS Threshold (T") | 공격 반복 횟수 | 성공까지 시간 |
|---------------------|---------------|-------------|
| 960 (n=5) | 9.3 × 10⁶ | **6.9일** |
| **800 (n=6)** | **1.9 × 10⁹** | **3.8년** |
| 685 (n=7) | 3.8 × 10¹¹ | **762년** |

- T" = 800 선택: **1년 이상의 연속 공격으로부터 보장된 보안**
- All-bank 공격 시 duty cycle 감소 (D=0.55) → 성공 시간 **5.1년**으로 증가
- 보안 수준을 높이려면 T"를 줄이면 됨 (성능 트레이드오프 존재)

### 4.4 RIT 보안

- 현재 epoch에서 설치된 엔트리는 epoch 완료까지 보장된 유지
- RIT 크기가 epoch 내 최대 swap 수를 충분히 수용 → overflow로 인한 premature un-swap 불가능
- Swap 후 row buffer close → 공격자가 목적지 row를 추론할 수 없음

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]
- [[paper-wiki/concepts/security.md|Security]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2022ASPLOS-summarize/randomized-row-swap-mitigating-row-hammer-by-breaking-spatial-correlation.md|전체 요약 보기]]
