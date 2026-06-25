---
tags: [paper, 2022, 2022ISCA, topic/cache, topic/dram]
venue: "ISCA 2022 (The 49th Annual International Symposium on Computer Architecture)"
year: 2022
summary_path: "../paper-summaries/2022ISCA-summarize/hydra-enabling-low-overhead-mitigation-of-row-hammer-at-ultra-low-thresholds-via-hybrid-tracking.md"
---

# Hydra: Enabling Low-Overhead Mitigation of Row-Hammer at Ultra-Low Thresholds via Hybrid Tracking

**Venue:** ISCA 2022 (The 49th Annual International Symposium on Computer Architecture)
**저자:** Moinuddin Qureshi, Aditya Rohan, Gururaj Saileshwar, Prashant J. Nair (Georgia Tech / University of Toronto)

## 개요

- Row-Hammer(RH)은 DRAM 행(row)을 반복 활성화하여 인접 행의 비트를 뒤집는 보안 취약점으로, RH 임계값(RH Threshold, T_RH)이 점점 낮아지고 있음
- 기존 연구에서는 T_RH=32K를 기준으로 했으나, 최신 공격에서는 T_RH가 수백 이하로 낮아지고 있어 ultra-low threshold에서의 RH 완화가 필수적
- **SRAM 기반 트래커의 한계 (Table 1):**
  - OCPR(One-Counter-Per-Row): 16GB rank에서 2~4MB 필요, 온칩 저장 불가
  - Graphene (state-of-the-art): T_RH=500에서 rank당 340KB 필요, 5400-entry CAM는 실용적 한계 초과
  - TWiCE: T_RH=32K에서 효과적이나 T_RH=500에서 OCPR 수준의 오버헤드
  - CAT: T_RH=500에서 rank당 1.5MB 필요
  - D-CBF: T_RH=500에서 rank당 768KB 필요, delay 완화만 지원 (victim refresh 미지원)
- **DRAM 기반 트래커의 한계 (CRA):**
  - 메모리 공간에 카운터 배치로 SRAM 오버헤드 최소화하지만, 메타데이터 캐시 부족으로 평균 25.8% 성능 저하 (64KB 캐시) ~ 16.8% (256KB 캐시)
- 이상적 목표: SRAM 기반의 낮은 성능 오버헤드 + DRAM 기반의 낮은 SRAM 오버헤드 동시 달성 (≤64KB SRAM, ≤1% 성능 오버헤드)

## 방법론

### 3.1. 구조 (Section 4.4)

#### 3.1.1. Group-Count Table (GCT)
- **목적:** 대부분의 행 activation 업데이트를 효율적으로 필터링
- **구조:** 비태그(non-tagged) 카운터 테이블, 행 주소의 일부 비트로 인덱싱
- 모든 행이 같은 GCT 엔트리에 매핑되면 해당 행들은 Row-Group을 형성
- **예시:** 32GB 메모리 = 400만 행 (8KB each), 32K entry GCT → Row-Group당 128행
- T_TG = 200일 때, 32K entry GCT는 최대 640만 activation을 필터링 가능
- activation 시 GCT 엔트리가 T_TG 미만이면 증가, T_TG에 도달하면 해당 상태 유지

#### 3.1.2. Row-Count Table (RCT)
- **목적:** GCT가 부족할 때 per-row 트래킹 제공
- 메모리 주소 공간의 예약된 영역에 비태그 카운터 테이블로 저장
- **크기:** T_TH=250을 지원하려면 엔트리당 1바이트, 32GB 시스템에서 총 4MB (메모리 용량의 0.02% 미만)
- GCT 엔트리가 T_TG에 도달하면 해당 row-group의 모든 RCT 엔트리를 T_TG로 초기화
- 128행이 인접 메모리 라인(64 bytes × 2)에 저장되도록 매핑하여 초기화 오버헤드 최소화

#### 3.1.3. Row-Count Cache (RCC)
- **목적:** RCT 접근의 높은 레이턴시를 완화하기 위해 자주 접근되는 RCT 엔트리를 온칩 캐싱
- **구조:** 세트 associative, 엔트리당 3바이트 (valid + 13비트 태그 + 8비트 카운터)
- 기본 설정: 8K entry (rank당 4K entry), 총 24KB
- RCC 히트 시 로컬에서 카운터 업데이트 가능, 미스 시 DRAM에서 RCT 엔트리 로드 후 RCC 설치

### 3.2. 동작 원리 (Section 4.5, Figure 4)

- **Case 1 [평균 90.7%]:** GCT에서 요청 처리, GCT 엔트리가 T_TG 미만 → 즉시 완료
- **Case 2 [평균 9.0%]:** GCT 엔트리가 T_TG에 도달, RCC 히트 → per-row 카운터 업데이트, T_TH 도달 시 완화 수행 후 리셋
- **Case 3 [평균 0.3%]:** GCT 엔트리가 T_TG에 도달, RCC 미스 → DRAM에서 RCT 엔트리 로드, RCC 설치 (기존 엔트리 dirty 시 write-back), 카운터 업데이트

### 3.3. 보안 분석 (Section 5)

- **Theorem-1:** Hydra는 (a) T_RH/2 활성화 이전 또는 시점에, (b) 완화 이후 T_RH/2 활성화마다 완화를 수행
- **증명:** 3단계 분석 (Phase-1: GCT 트래킹, Phase-2: RCT 트래킹, Phase-3: 완화 후 트래킹)
  - Lemma-1: GCT 엔트리가 T_TG에 도달할 때, T_TG ≥ |ACT_1| (Phase-1의 활성화 수)
  - Lemma-2: RCT 엔트리가 T_TH에 도달할 때, T_TH = T_TG + |ACT_2| (Phase-2의 활성화 수)
  - 따라서 T_TH ≥ |ACT_1| + |ACT_2| → T_RH/2 이전에 완화 보장
- **주기적 리셋:** 64ms마다 SRAM 구조 리셋, 실제 임계값은 2·T_RH - 1이므로 T_RH=500 지원을 위해 T_TH=250 설정
- **적응형 공격 방어:**
  - Victim refresh 활성화를 전체 활성화 카운트에 포함
  - RCT 행에 대한 RH 공격을 별도 512바이트 SRAM 카운터로 방어

## 핵심 기여

- Hydra는 ultra-low Row-Hammer 임계값(T_RH=500 이하)에서도 효율적인 RH 완화를 위한 **하이브리드 트래커** 제안
- GCT(집계 필터링) + RCC(온칩 캐싱) + RCT(DRAM per-row 트래킹)의 3계층 구조로 **56.5KB SRAM + 0.7% 평균 성능 오버헤드** 달성
- 기존 SRAM 트래커(Graphene 680KB, TWiCE 4.6MB) 대비 압도적으로 낮은 SRAM 오버헤드, 기존 DRAM 트래커(CRA 25% slowdown) 대비 압도적으로 낮은 성능 오버헤드
- victim refresh 외에도 row migration 등 다양한 완화 정책과 호환 가능
- future work: 다른 완화 기법(예: randomized row-swap)과의 결합 탐색

## 주요 결과

- **시뮬레이터:** USIMM 기반, JEDEC DDR4 프로토콜 모델링, industrial 16Gb x8-DRAM 칩 파라미터
- **시스템 구성 (Table 2):**
  - 8개 OoO 코어 @ 3.2GHz, ROB 160, fetch/retire width 4
  - 공유 LLC: 8MB, 16-Way, 64B 라인
  - 메모리: 32GB DDR4, 1.6GHz (3.2GHz DDR), T_CL-T_RCD-T_RP = 14-14-14ns
  - 16 bank × 1 rank × 2 channel, 행 크기: 8KB
- **하드웨어 구조 (Table 4):**
  - GCT: 8비트 카운터, 32K entry = 32KB
  - RCC: 24비트 (valid + tag + SRRIP + 8비트 카운터), 8K entry = 24KB
  - RIT-ACT: 8비트 카운터, 512 entry = 0.5KB
  - **총 SRAM 오버헤드: 56.5KB** (+ 4MB DRAM)
- **전력 분석:** SRAM 구조 전력 오버헤드 18.6mW (GCT: 10.6mW, RCC: 8mW), DRAM 추가 접근 전력 오버헤드 0.2%

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2022ISCA-summarize/hydra-enabling-low-overhead-mitigation-of-row-hammer-at-ultra-low-thresholds-via-hybrid-tracking.md|전체 요약 보기]]
