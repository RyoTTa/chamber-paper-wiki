---
tags: [paper, 2022, 2022MICRO, topic/dram, topic/rowhammer]
venue: "MICRO 2022 (55th IEEE/ACM International Symposium on Microarchitecture)"
year: 2022
summary_path: "../paper-summaries/2022MICRO-summarize/aqua-scalable-rowhammer-mitigation-by-quarantining-aggressor-rows-at-runtime.md"
---

# AQUA: Scalable Rowhammer Mitigation by Quarantining Aggressor Rows at Runtime

**Venue:** MICRO 2022 (55th IEEE/ACM International Symposium on Microarchitecture)
**저자:** Anish Saxena, Gururaj Saileshwar, Prashant J. Nair, Moinuddin Qureshi (Georgia Tech / University of British Columbia)

## 개요

- DRAM 기술 축소로 셀 간 간섭이 증가하여, 인접 row를 빠르게 활성화(activation)하면 victim row에 bitflip이 발생하는 **Rowhammer** 보안 취약점이 심각한 위협이 됨
- Rowhammer Threshold(TRH)가 급격히 감소: DDR3(2014) 130K → DDR4 22K → LPDDR4(2020) 4.8K → DDR5(2022) 5K 이하로 하락 중 (Fig. 2)
- 기존 victim refresh 기반 방어는 **Half-Double 공격**에 취약: 공격자가 victim refresh를 악용해 거리-2 위치에 bitflip을 유발할 수 있음 (Fig. 1a)
- Randomized Row-Swap(RRS)는 Half-Double에 강인하나, TRH=1K에서 **평균 19.8% 성능 저하** 및 **2.4MB SRAM 오버헤드**(per rank)로 실용성이 부족 (Fig. 1b, Fig. 3)
- CROW는 DRAM 서브어레이에 copy-row를 추가하나, TRH=1K에서 **1060% DRAM 오버헤드** 필요
- Blockhammer는 TRH=1K에서 최악의 경우 **1280× slowdown** 발생 → denial-of-service 취약

## 방법론

### 3.1. 전체 구조 (Overview, Fig. 4)

- **Aggressor-Row Tracker (ART):** per-bank Misra-Gries 트래커로 row 활성화 수를 추적, TRH/2 = 500 활성화 시 격리 트리거
- **Row Quarantine Area (RQA):** 메모리의 전용 격리 영역. circular buffer로 관리되며, 새 aggressor는 가장 오래된 위치에 저장
- **Forward-Pointer Table (FPT):** 격리된 row의 원래 위치 → RQA 내 위치 매핑. fully-associative collision-avoidance table(CAT), 32K 엔트리, 108KB
- **Reverse-Pointer Table (RPT):** RQA 위치 → 원래 위치 매핑. direct-mapped, 23K 엔트리, 64KB
- **Copy Buffer:** row 단위(8KB) 데이터 전송을 위한 임시 버퍼

### 3.2. 격리 프로세스 (Quarantine Process, Fig. 5)

1. ART가 aggressor row를 감지 (500회 활성화)
2. RQA의 가장 오래 위치(RQA-Head-Pointer)를 목적지로 지정
3. 원래 row 내용을 copy-buffer로 스트리밍 (DRAM row activation 후 640ns, 총 685ns)
4. copy-buffer에서 RQA 목적지로 스트리밍 (추가 685ns) → 총 **1.37μs**
5. FPT에 <원래주소, Q1> 엔트리, RPT에 <Q1, 원래주소> 엔트리 갱신
6. RQA 내에서 재격리 시에도 동일한 1.37μs 비용 (기존 RQA 위치에서 새 RQA 위치로 이동)

### 3.3. 격리 영역 크기 분석 (Bounding RQA Size)

격리 영역 크기는 공격자의 worst-case 접근 패턴에서 보안을 보장하기 위해 결정됨:

**수식:**
- tAGG = A × tRC (격리 트리거까지의 시간)
- tB = tAGG + B × tmov (B개 bank에서 격리 트리거 시 최대 동시 격리 시간)
- Rmax = tREFW × B / (tAGG + B × tmov) (64ms 내 최대 격리 row 수)

**격리 영역 크기 (Table III):**
| Effective Threshold (A) | Rmax (rows) | 크기 | DRAM 오버헤드 |
|------------------------|-------------|------|-------------|
| 1000 | 15,302 | 120MB | 0.7% |
| 500 | 23,053 | 180MB | 1.1% |
| 250 | 30,872 | 241MB | 1.5% |
| 125 | 37,176 | 290MB | 1.8% |
| 1 | 46,620 | 364MB | 2.2% |

- TRH=1K에서 DRAM 오버헤드는 **1.1%**로, 16GB 메모리 기준 180MB
- TRH가 극단적으로 낮아져도 DRAM 오버헤드는 2.2% 이하로 유지

### 3.4. Memory-Mapped Table Design (Fig. 8)

**구조:**
- FPT와 RPT를 DRAM에 저장 (FPT: 4MB, RPT: 0.1MB)
- **Resettable Bloom Filter:** 128K 엔트리(16KB SRAM), row가 격리되었는지 빠르게 판별
  - Bloom filter 비트가 0이면 격리되지 않은 row → 즉시 원래 위치 접근
  - 128K 엔트리, 2M row → 16 row가 동일 그룹으로 매핑
  - 엔트리 무효화 시 해당 그룹의 모든 엔트리가 무효일 때만 비트 리셋
- **FPT-Cache:** 16-way set-associative, 4K 엔트리(16KB SRAM), RRIP 교체 정책
  - 격리된 row의 FPT 엔트리를 캐싱
- **Singleton Optimization:** 그룹에 격리된 row가 1개뿐인 경우, FPT-Cache miss 시에도 DRAM 접근 불필요 (0.4% 접근 필터링)
- **Copy Buffer:** 8KB SRAM

**성능 (Fig. 9):**
- SRAM 기반 AQUA: 평균 1.8% slowdown
- Memory-Mapped AQUA: 평균 **2.1% slowdown** (SRAM 대비 거의 동일)

**FPT 접근 분류 (Fig. 10):**
| 접근 유형 | 비율 |
|----------|------|
| Bloom Filter = 0 (즉시 통과) | 92.2% |
| FPT-Cache Hit | 7.3% |
| Singleton in FPT-Cache | 0.4% |
| DRAM Access | 0.02% |

## 핵심 기여

1. **AQUA는 격리 기반 접근으로 Rowhammer을 효과적으로 방어한다:** 격리된 aggressor row는 물리적으로 격리된 영역에서만 활성화 가능하므로, victim row와의 spatial correlation이 완전히 차단됨
2. **SRAM 오버헤드를 대폭 절감한다:** Memory-Mapped 디자인으로 매핑 테이블 SRAM을 172KB→32KB로, 전체 SRAM을 41KB로 절감 (RRS 2.4MB 대비 **약 60배 절감**)
3. **DRAM 오버헤드는 미미하다:** RQA 1.1% + 매핑 테이블 4.1MB = 총 1.13% (CROW 1060% 대비)
4. **RRS 대비 10배 낮은 성능 저하:** 높은 격리 임계값(500 vs 166) 사용으로 인해 row migration 빈도가 9배 감소하고, 각 migration 비용도 절반
5. **상용 DRAM과 호환되며, TRH 하락에 대한 확장성을 가진다:** TRH가 1K에서 500으로 하락해도 DRAM 오버헤드는 2% 이하로 유지

**Broader significance:** AQUA는 Rowhammer 방어에서 randomization(RRS)과 refresh(CROW)의 한계를 극복하고, 확장 가능하며 실용적인 방어 메커니즘을 제시한다. 특히 TRH가 지속적으로 하락하는 미래 DRAM에서도 유지 가능한 유일한 상용 DRAM 호환 솔루션 중 하나이다.

## 주요 결과

- **시뮬레이터:** gem5 (Syscall Emulation 모드, cycle-level)
- **시스템 구성 (Table I):**
  - 4× OoO 코어 @ 3GHz, ROB 192, 8-wide fetch/retire
  - 4MB L3 cache (16-way, 64B line)
  - 16GB DDR4 (Micron MT40A2G4), 2400MT/s
  - 16 banks × 1 rank × 1 channel, 128K rows/bank, 8KB row
- **벤치마크:** SPEC CPU2017 rate 18개 + 16개 혼합 워크로드 (총 34개)
- **트래커:** per-bank Misra-Gries (Graphene, RRS와 동일), TRH/2 = 500에서 격리 트리거
- **시뮬레이션:** 25B 명령어 fast-forward 후 250M 명령어 시뮬레이션
- **오픈소스:** github.com/Anish-Saxena/aqua_rowhammer_mitigation (Unlicense)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]


## 전체 요약

[[../paper-summaries/2022MICRO-summarize/aqua-scalable-rowhammer-mitigation-by-quarantining-aggressor-rows-at-runtime.md|전체 요약 보기]]
