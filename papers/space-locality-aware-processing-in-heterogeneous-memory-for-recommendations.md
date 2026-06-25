---
tags: [paper, 2021, 2021ISCA, topic/dram, topic/pim]
venue: "48th Annual International Symposium on Computer Architecture (ISCA 2021)"
year: 2021
summary_path: "../paper-summaries/2021ISCA-summarize/space-locality-aware-processing-in-heterogeneous-memory-for-recommendations.md"
---

# SPACE: Locality-Aware Processing in Heterogeneous Memory for Personalized Recommendations

**Venue:** 48th Annual International Symposium on Computer Architecture (ISCA 2021)
**저자:** Hongju Kal, Seokmin Lee, Gun Ko, Won Woo Ro (Yonsei University)

## 개요

- personalized recommendation 시스템은 현대 데이터 센터의 주요 AI 애플리케이션으로, embedding layer의 large memory footprint과 high bandwidth requirement가 핵심 병목임.
- 기존 DIMM 기반 NMP (Near Memory Processing) 방식(TensorDIMM, RecNMP)은 DIMM 수를 늘려 성능을 확장하지만, comodity DIMM의 낮은 대역폭으로 인해 비효율적인 scaling 발생 → DIMM 수가 늘어날수록 energy 소비가 비례적으로 증가 (Figure 5).
- 3D-stacked DRAM (HBM 등)은 높은 대역폭을 제공하지만 용량이 제한적(수 GB)으로, production-scale recommendation 모델의 embedding table 전체를 저장하기에 부족함 (Figure 1).
- Facebook DLRM 기준, embedding table의 size가 수백 MB~수 GB에 달하며, batch size=64에서 embedding layer의 실행 시간이 bottom-FC layer보다 길어지는 임계점이 존재 (16개 embedding table 이상).
- DIMM ×8 구성을 사용해도 Emb-64(workload)에서는 bottom-FC보다 빠른 실행 시간을 달성하지 못함 (Figure 4).

## 방법론

### 3.1. Locality-Aware Preprocessing (Algorithm 1)

- **STEP 1 (Reserve Embedding Size):** HBM에 저장할 embedding 크기를 2MB의 거듭제곱으로 초기 설정.
- **STEP 2 (Align Embedding Table):** item의 access count 기준으로 내림차순 정렬.
- **STEP 3 (Set Item-line):** item-line 결정 — 상위 item들의 access 비율이 HBM 대역폭 비율과 일치하도록 설정. 실험에서 HBM: DIMM 대역폭 비율은 약 4:1.
- **STEP 4 (Set Psum-line):** HBM의 잔여 공간에 저장 가능한 psum의 수를 결정. psum2(2개 item의 부분합)를 기본으로 사용.
- **Buddy Table Allocator:** HBM embedding을 buddy allocation 방식으로 할당. 공간 부족 시 psum 영역을 대체하여 item 저장 우선.

### 3.2. Hardware Design

- **Extended Memory Controller:** offload된 embedding kernel을 해석하여 SPACE instruction으로 변환.
- **SPACE Instruction Format:**
  - `Add.M`: HBM에 저장된 item/psum 벡터의 메모리 주소 연산
  - `Add.I`: DIMM에서 가져온 item 벡터를 immediate value로 사용하는 연산
- **Item/Psum Classification:** item-line과 psum-line 값을 사용하여 각 item index가 HBM인지 DIMM인지, psum이 존재하는지 판별.
- **Coalescer:** HBM에 저장된 item들의 psum index를 계산하여 중복 접근 방지.
- **NMP Module:** HBM logic die에 위치, vector logic unit으로 element-wise summation 수행. 채널당 0.33 mm², 342.5 mW.

### 3.3. Data Allocation Framework

- Gather locality 기반: access 상위 ~21.3%의 item을 HBM에 배치 (실험 평균).
- HBM-DIMM 서빙 비율: 약 4:1 → 전체 대역폭 60.3% 향상 (HBM-only 대비).
- Psum2 활용: 전체 reduction 요청의 19.7%를 psum으로 처리하여 element-wise summation 9.8% 절감.
- 모든 dataset에서 유사한 locality 패턴 확인 (Google Maps, Amazon, LastFM, MovieLens, Anime, Steam Game — Figure 7, 8).

## 핵심 기여

- SPACE는 personalized recommendation을 위한 **heterogeneous memory 기반 NMP** 아키텍처로, HBM의 high bandwidth와 DIMM의 large capacity를 결합.
- **Gather locality** (소수 인기 item의 집중 접근)와 **Reduction locality** (반복적 item 조합의 partial sum 재사용)를 체계적으로 분석하고 활용.
- 기존 DIMM 기반 NMP(TensorDIMM) 대비 **3.2× performance 향상** 및 **56% energy 절감**을 달성 while DIMM 크기의 1/8 크기의 3D-stacked DRAM 사용.
- 기존 heterogeneous memory 기법(BEAR) 대비 **31.5%** 성능 향상.
-acebook scale recommendation 시스템에서의 embedding operation 최적화에 기여하며, social phenomenon(long-tail)이 embedding access pattern에도 동일하게 나타남을 발견.

## 주요 결과

- **시뮬레이터:** Gem5 (cycle-level CPU simulator) + DRAMsim3 (memory simulator).
- **하드웨어 합성:** Synopsys ASIP Designer로 RTL 모델 생성, Synopsys Design Compiler로 면적/功耗 추정 (45nm CMOS, 250MHz).
- **SRAM 구조:** CACTI로 22nm 기반 power 추정.
- **소프트웨어:** Python 기반 recommendation system 구현, NMP embedding kernel offloading.
- **시스템 구성:** 8 OoO cores, 3GHz, L3 16MB; HBM 4-hi 1 stack (8ch, 512MB/channel); DDR4-3200 (2ch, 16GB/channel).

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2021ISCA-summarize/space-locality-aware-processing-in-heterogeneous-memory-for-recommendations.md|전체 요약 보기]]
