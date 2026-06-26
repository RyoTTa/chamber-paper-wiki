---
tags: [paper, 2023, 2023ASPLOS, topic/dram, topic/storage]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023ASPLOS-summarize/leaftl-a-learning-based-flash-translation-layer-for-solid-state-drives.md"
---

# LeaFTL: A Learning-Based Flash Translation Layer for Solid-State Drives

**Venue:** 
**저자:** 

## 개요

SSD의 FTL(Flash Translation Layer)에서 주소 매핑 테이블(address mapping table)은 가장 큰 메모리 풋프린트를 차지하는 자료구조다. 현대 SSD는 page-level mapping(예: DFTL)을 사용하지만, 4바이트 LPA + 4바이트 PPA = 8바이트 per entry로, 2TB SSD의 경우 매핑 테이블만 ~4GB가 필요하다. SSD 컨트롤러의 DRAM은 비용/전력 제약으로 크게 확장할 수 없어, 매핑 테이블이 DRAM 캐싱의 병목이 된다.

기존 최적화(SFTL 등)는 사람이 설계한 휴리스틱 기반으로, sequential access 같은 특정 패턴만 압축할 수 있으며 동적이고 다양한 access pattern을 런타임에 포착하지 못한다. 학습 기반 접근(learned index)은 in-memory 데이터셋에서 성공했지만, SSD의 out-of-place write, GC, wear leveling 특성상 직접 적용이 어렵다.

## 방법론

### 3.1 방법론

| 항목 | 상세 |
|------|------|
| **Simulator** | WiscSim (trace-driven, event simulation) |
| **SSD Spec** | 2TB, 4KB page, 1GB DRAM, 16 channels, 256 pages/block, 128B OOB |
| **Real SSD** | 1TB open-channel SSD, 16KB page, 16 channels, 256 pages/block |
| **Workloads (Sim)** | MSR Cambridge traces (hm, src2, prxy, prn, usr), FIU traces (home, mail) |
| **Workloads (Real)** | FileBench (OLTP, CompFlow), BenchBase/MySQL (TPCC, AuctionMark, SEATS) |
| **Baselines** | DFTL (demand-based page-level), SFTL (spatial-locality-aware) |
| **Metrics** | Mapping table size, storage latency, throughput, WAF, lookup overhead |

### 3.2 매핑 테이블 크기 감소

- DFTL 대비: **7.5–37.7×** 감소
- SFTL 대비: 평균 **2.9×** (최대 5.3×) 감소 (γ=0, accurate only)
- γ=16 → 추가 1.3× 감소 (sim), 1.2× 감소 (real SSD)

### 3.3 성능 향상

**Simulator (DRAM 주로 매핑 테이블용):** SFTL 대비 평균 **1.6×** (최대 2.7×) latency 감소

**Simulator (DRAM 80% 매핑, 20% 데이터 캐시):** SFTL 대비 **1.4×** (최대 3.4×), DFTL 대비 **1.6×** (최대 4.9×)

**Real SSD prototype:** SFTL/DFTL 대비 평균 **1.4×** (최대 1.5×) throughput 향상. OLTP workload latency 분포에서 tail latency 증가 없음, cache hit ratio 증가로 전반적 latency 감소.

### 3.4 Sensitivity Analysis

- **DRAM 크기 (256MB–1GB):** 모든 크기에서 LeaFTL > SFTL > DFTL
- **Page 크기 (4KB–16KB):** 16KB에서 SFTL 대비 1.1×, 8KB에서 1.2× 성능 우위 (고정 total capacity 기준)

### 3.5 Overhead 분석 (ARM Cortex-A72)

| 연산 | γ=0 | γ=1 | γ=4 |
|------|-----|-----|-----|
| Learning (256 LPAs) | 9.8 μs | 10.8 μs | 10.8 μs |
| LPA lookup | 40.2 ns | 60.5 ns | 67.5 ns |

- Learning overhead: 256 writes당 1회 → flash write latency의 **0.02%**
- LPA lookup overhead: flash read latency의 평균 **0.21%**, 99.99% lookup에서 <1%

### 3.6 SSD Lifetime

WAF (Write Amplification Factor): DFTL > SFTL ≈ LeaFTL. SFTL과 LeaFTL은 translation page flush가 가끔 발생하지만 무시할 수준. SSD 수명에 부정적 영향 없음.

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

- **Simulator:** WiscSim 기반, LRU read-write cache 추가, linear regression 알고리즘 [66] 통합. 기존 FTL 기능(GC, wear leveling) 보존.
- **Real SSD prototype:** 1TB open-channel SSD, 호스트 측 FTL 구현. SDK library 활용 C 언어로 **4,016 LOC**.
- GitHub: https://github.com/platformxlab/LeaFTL

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2023ASPLOS-summarize/leaftl-a-learning-based-flash-translation-layer-for-solid-state-drives.md|전체 요약 보기]]
