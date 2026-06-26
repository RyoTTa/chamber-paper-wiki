---
tags: [paper, 2022, 2022MICRO, topic/disaggregation, topic/dram, topic/memory-tiering, topic/near-data-processing, topic/pim]
venue: "55th IEEE/ACM International Symposium on Microarchitecture (MICRO 2022)"
year: 2022
summary_path: "../paper-summaries/2022MICRO-summarize/beacon-scalable-near-data-processing-accelerators-for-genome-analysis-near-memory-pool-with-the-cxl-support.md"
---

# BEACON: Scalable Near-Data-Processing Accelerators for Genome Analysis near Memory Pool with the CXL Support

**Venue:** 55th IEEE/ACM International Symposium on Microarchitecture (MICRO 2022)
**저자:** Wenqin Huangfu (University of California, Santa Barbara), Andrew Chang (Samsung Semiconductor), Krishna T. Malladi (Samsung Semiconductor), Yuan Xie (University of California, Santa Barbara)

## 개요

- 게놈 분석은 정밀 의료, 야생 동물 보존, 팬데믹 대응(COVID-19) 등에서 중요성이 지속적으로 증가하나, NGS(Next Generation Sequencing) 기술 발전과 정밀 의료를 위한 대용량 시퀀싱 데이터로 인해 **게놈 데이터 생성 속도가 처리 속도를 크게 초과** (Moore's Law를 상회하는 데이터 성장률).
- 게놈 분석의 핵심 애플리케이션(DNA seeding, k-mer counting, DNA pre-alignment)은 단순 산술 연산 + 대용량 메모리 접근 특성으로 PIM/NDP에 적합하나, 기존 DIMM 기반 가속기에는 두 가지 핵심 한계 존재.
- **한계 1 - 통신 병목:** MEDAL 기준 DIMM 내부 메모리 대역폭(inta-DIMM)과 DIMM 간 통신 대역폭(inter-DIMM) 사이에 **12배 차이**가 존재하여 통신이 성능 병목. 이상적 통신(infinite bandwidth, zero latency) 가정 시 **4.36x 성능**, **2.32x 에너지 효율** 향상 가능(Figure 3).
- **한계 2 - 메모리 확장 제약:** DDR-DIMM의 메모리 채널/슬롯 수 제한, 메모리 비집적화(memory disaggregation) 트렌드로 인해 로컬 DDR 메모리 양이 감소. NEST는 DDR 채널에서 512GB 제공하나, SMUFIN은 2TB 필요 → DDR-DIMM으로는 확장 불가능. 반면 memory pool은 4.5TB 이상 제공 가능.
- DDR-DIMM 기반 가속기는 DIMM 커스터마이제이션을 통해 높은 intra-DIMM 대역폭을 활용하지만, **unmodified DIMM을 메모리 확장에 사용하면 잦은 inter-DIMM 통신**이 발생하여 설계 철학과 모순.

## 방법론

### 3.1. 하드웨어 아키텍처

- **NDP 모듈 (BEACON-D의 경우 CXLG-DIMM 내부, BEACON-S의 경우 CXL-Switch 내부):**
  - Memory Controller (MC): 메모리 접근 관리 + Switch-Bus를 통한 인터커넥트.
  - Processing Engines (PEs): 애플리케이션별 고정 기능 연산 (FM-index, Hash-index, k-mer counting, pre-alignment).
  - Atomic Engine: 원자적 메모리 연산(RMW data race 해결 + 대역폭 절감) 지원.
  - Data Packer/Unpacker: 불필요한 데이터 이동 최소화를 위한 데이터 패킹/언패킹.
- **CXL-Interface:** CXL-Switches와의 통신 인터페이스. Data Packer를 통해 전송 전후 데이터 패킹/언패킹 수행.
- **PE 규모:** BEACON-D는 CXLG-DIMM당 128 PEs, BEACON-S는 CXL-Switch당 256 PEs.
- **하드웨어 오버헤드 (Table II):** BEACON PE 면적 14,090.23 μm², 동적 전력 9.48 mW, 누설 전력 18.97 μW → MEDAL/NEST 대비 작거나 동등.

### 3.2. 메모리 관리 프레임워크

- **DIMM 할당:** 애플리케이션/알고리즘/데이터셋/파라미터 정보 기반으로 CXL-Switch가 CXL-DIMM을 할당. NDP 모듈과 인접한 DIMM 우선 할당 → 메모리 클린으로 활성 데이터 마이그레이션.
- **메모리 접근 최적화:** CXL 프로토콜의 device-biased 모드 활용으로 unmodified CXL-DIMM에 대한 불필요한 coherence 이동 제거(Figure 9). host 경유 중복 데이터 이동 원천 차단.
- **데이터 배치 및 주소 매핑:** 
  - CXLG-DIMM: chip-level 인터리빙으로 미세한 메모리 접근 지원.
  - Unmodified CXL-DIMM: rank-level 인터리빙.
  - 공간적 로컬리티가 있는 데이터는 DRAM row-by-row 매핑 (예: Hash-index 기반 DNA seeding에서 매칭 위치를 동일 DRAM row에 연속 배치).
- **메모리 할당 해제:** host → CXL-Switch → CXLG-DIMM(또는 CXL-DIMM) 순으로 할당 해제 처리.

### 3.3. 알고리즘별 최적화

- **FM-index 기반 DNA Seeding - Multi-Chip Coalescing:**
  - 기존 DIMM: 모든 DRAM 칩이 lock-step으로 접근되어 불필요한 데이터 대량 읽힘 (Figure 11(a)).
  - 이전 가속기: 단일 칩을 여러 번 읽어 미세 접근 지원 → 칩별 접근 불균형 (Figure 11(b)).
  - **Multi-Chip Coalescing:** 여러 칩을 coalesce하여 접근 → 불필요한 데이터 없이 균형 잡힌 메모리 접근 달성 (Figure 11(c)). 최적의 coalescing 칩 수를 세밀하게 조정.
  - 결과: FM-index DNA seeding에서 **1.34x** 추가 성능 향상(Figure 12(a)).

- **k-mer Counting - Single-Pass k-mer Counting:**
  - NEST의 기존 방식: 3-pass (1) 로컬 Bloom filter 구축 → (2) 병합/배포 → (3) 독립적 k-mer counting. 전체 입력 데이터 2회 처리.
  - **BEACON-S의 single-pass:** 글로벌 Bloom filter를 CXL-DIMM에 분산 배포하고 단일 패스로 직접 처리. 첫 번째/마지째 단계 생략 → 처리량 향상.
  - k-mer counting에서 **1.48x** 추가 성능 향상(Figure 15(c)).

## 핵심 기여

- **핵심 기여:** CXL 기반 메모리 풀 근처의 DIMM 기반 NDP 가속기 BEACON으로 기존 DDR-DIMM 기반 가속기의 통신 병목과 메모리 확장 한계를 동시에 해결.
- **성능:** State-of-the-art DIMM 기반 NDP 가속기(MEDAL, NEST) 대비 평균 **4.70x (BEACON-D)**, **4.13x (BEACON-S)** 성능 향상.
- **메모리 확장:** Unmodified CXL-DIMMs을 활용한 온디맨드 메모리 확장으로 memory pool의 풍부한 메모리 활용 가능.
- **범용성:** FM-index, Hash-index DNA seeding, k-mer counting, DNA pre-alignment의 3가지 게놈 분석 애플리케이션을 하나의 아키텍처로 지원.
- **비침습적:** DRAM 다이 수정 없이 기존 DIMM의 비용 효율성과 확장성 유지.
- **의의:** 메모리 비집적화(memory disaggregation) 시대에 게놈 분석의 병렬 처리 병목을 CXL 인터커넥트와 소프트웨어-하드웨어 공동 설계로 극복한 최초의 실용적 NDP 아키텍처.

## 주요 결과

- **시뮬레이터:** Ramulator 기반 cycle-accurate 시뮬레이터 (BEACON 및 baseline 모두).
- **하드웨어 합성:** Synopsys Design Compiler, 28nm 기술로 PE의 timing/energy/area 합성.
- **DRAM 모델:** DRAMPower로 에너지 소비 계산.
- **CPU Baseline:** Intel Xeon E5-2680 v3 @ 2.50 GHz, 384GB 메모리, 48 threads.
- **소프트웨어 Baseline:** BWA-MEM (FM-index DNA seeding), SMALT (Hash-index DNA seeding), BFCounter (k-mer counting), Shouji (DNA pre-alignment).
- **데이터셋:** 5개 게놈 (Pinus taeda, Picea glauca, Sequoia sempervirens, Ambystoma mexicanum, Neo-ceratodus forsteri) from NCBI; k-mer counting은 human genome 50x coverage.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2022MICRO-summarize/beacon-scalable-near-data-processing-accelerators-for-genome-analysis-near-memory-pool-with-the-cxl-support.md|전체 요약 보기]]
