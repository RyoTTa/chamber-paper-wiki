---
tags: [paper, 2020, 2020MICRO, topic/cache, topic/dram]
venue: "53rd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '20)"
year: 2020
summary_path: "../paper-summaries/2020MICRO-summarize/figaro-improving-system-performance-via-fine-grained-in-dram-data-relocation-and-caching.md"
---

# FIGARO: Improving System Performance via Fine-Grained In-DRAM Data Relocation and Caching

**Venue:** 53rd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '20)
**저자:** Yaohua Wang, Lois Orosa, Xiangjun Peng, Yang Guo, Saugata Ghose, Minesh Patel, Jeremie S. Kim, Juan Gómez Luna, Mohammad Sadrosadati, Nika Mansouri Ghiasi, Onur Mutlu (National University of Defense Technology, ETH Zürich, Chinese University of Hong Kong, UIUC, CMU, ITRC)

## 개요

- DRAM은 현대 컴퓨터 시스템의 주 메모리이지만, 수십 년간 용량은 증가했음에도 접근 레이턴시는 크게 개선되지 않음
- In-DRAM 캐시는 빠른 영역(fast subarray)과 느린 영역(slow subarray)을 혼합하여 DRAM 레이턴시를 완화하지만, 두 가지 본질적 비효율에 시달림:
  1. **데이터 재배치(granularity)가 너무 큼:** 기존 설계는 entire DRAM row(8KB)를 재배치하지만, 많은 애플리케이션은 row의 작은 부분만 접근하여 캐시 공간 낭비 발생
  2. **거리 종속 레이턴시:** 물리적으로 먼 subarray 간 데이터 이동 시간이 길어, 이를 완화하기 위해 fast subarray를 여러 개 interleaving 배치해야 하므로 면적 오버헤드와 제조 복잡도 증가
- Tiered-Latency(TL) DRAM: 비트라인 격리 트랜지스터 사용 → open-bitline 아키텍처에서 3.15% 면적 오버헤드
- CHARM: 정적 프로파일링 기반 → 동적 적응 불가, 성능 제한
- DAS-DRAM/LISA-VILLA: 벌크 데이터 재배치 지원하지만 전체 row 단위 재배치 → 캐시 활용도 낮음
- 기존 in-DRAM 캐시의 실제 캐시 히트율은 높지만, row buffer hit rate는 개선되지 않아 성능 이득이 제한적

## 방법론

### 3.1. RELOC 명령어 동작 원리 (Figure 4)

- **동작 순서:**
  1. 소스 subarray(A)의 특정 row를 ACTIVATE → LRB A에 데이터 로드
  2. RELOC 명령어: LRB A의 column 3을 GRB를 통해 LRB B의 column 1로 전송
  3. 목적지 subarray(B)를 ACTIVATE → LRB B의 해당 column에 새 데이터 덮어쓰기 (다른 셀은 유지)
  4. PRECHARGE로 bank 준비
- **비정렬 데이터 전송 지원:** 소스 column과 목적지 column이 다를 수 있음 → column 디코더에 멀티플렉서 추가
- **그리드 독립 레이턴시:** GRB가 global bitline(금속 배선, 낮은 커패시턴스)을 통해 전송하므로 거리에 따른 레이턴시 차이 미미
  - SPICE 시뮬레이션 결과: RELOC 레이턴시 0.57ns (최악 거리 기준)
  - 43% 가드밴드 추가 → 최종 RELOC 레이턴시: 1ns
  - 전체 재배치 비용: 63.5ns (2개 ACTIVATE + 1개 RELOC + 1개 PRECHARGE)
  - 에너지 소비: 0.03µJ/cache block (Micron 전력 계산기 기준)

### 3.2. 멀티 액티베이션 지원

- 기존 DRAM: 한 bank에 하나의 row만 활성화 가능
- FIGARO: 소스 row와 목적지 row를 순차적으로 활성화하기 위해 subarray별 디코딩 로직에 latch 추가
  - 추가 latch가 소스 row 주소를 저장, local row 디코더가 latch 주소와 일반 주소를 선택 가능
- Subarray-Level Parallelism(SALP) 기술과 유사한 접근

### 3.3. 하드웨어 오버헤드

- 각 subarray에 column MUX (4.7µm², 2.1µW), row MUX (18.8µm², 8.4µW), row address latch (35.2µm², 19.1µW) 추가
- 전체 DRAM 칩 대비 면적 오버헤드: **< 0.3%**
- 전력 오버헤드: 무시할 수 있는 수준 (ACTIVATE 51.2mW 대비 미미)

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1. 캐시 관리 (FTS - FIGCache Tag Store)

- 메모리 컨트롤러에 FTS 태그 스토어 유지 (뱅크당 512 엔트리)
- 각 엔트리: row segment 주소 태그(19비트), 유효 비트, 더러운 비트, 이점 카운터(5비트)
- **삽입 정책:** insert-any-miss → 모든 캐시 미스 시 row segment를 캐시에 삽입
- **교체 정책 (RowBenefit):**
  - 행 단위(granularity) 교체: 캐시 row 전체의 이점 합산으로 최저 점수 row 선택
  - 개별 row segment 단위로 하나씩 교체 → 시간적 로컬리티 활용
  - 캐시 row에 여러 row segment를 co-locate → row buffer hit rate 향상

### 4.2. In-DRAM 캐시 구현 옵션

**Fast Subarray 기반 (FIGCache-Fast):**
- 은행당 fast subarray 2개 추가 (각 32 row, vs. 일반 512 row)
- 기존 LISA-VILLA는 16개 fast subarray 사용 → FIGCache는 8배 적은 수량으로 더 높은 성능
- 캐시 row에 row segment를 co-locate하여 row buffer hit rate 대폭 향상

**Slow Subarray 기반 (FIGCache-Slow):**
- 일반 DRAM의 slow subarray에서 64 row를 예약하여 캐시로 사용
- fast subarray 불필요 → 면적 오버헤드 0.2%
- 동일 subarray 내 재배치는 비효율적이므로, 캐시 row가 있는 subarray의 데이터는 캐싱하지 않음
- 기존 homogeneous DRAM에서도 성능 이득 제공

**Fast Row 기반 (CROW/CLR-DRAM 통합):**
- Cell coupling 기술을 활용하여 subarray 내 fast row 구현 가능
- FIGARO의 RELOC로 일반 row에서 fast row로 데이터 전송

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2020MICRO-summarize/figaro-improving-system-performance-via-fine-grained-in-dram-data-relocation-and-caching.md|전체 요약 보기]]
