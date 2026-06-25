---
tags: [paper, 2019, 2019ASPLOS, topic/cache, topic/dram, topic/storage]
venue: "24th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '19)"
year: 2019
summary_path: "../paper-summaries/2019ASPLOS-summarize/soml-read-rethinking-read-granularity-of-3d-nand-ssds.md"
---

# SOML Read: Rethinking the Read Operation Granularity of 3D NAND SSDs

**Venue:** 24th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '19)
**저자:** Chun-Yi Liu (Pennsylvania State University), Jagadish B. Kotra (AMD Research), Myoungsoo Jung (KAIST), Mahmut T. Kandemir (Pennsylvania State University), Chita R. Das (Pennsylvania State University)

## 개요

- 3D NAND 기술은 셀을 수직으로 적층(32/64/96단)하여 높은 밀도를 달성하지만, 칩 밀도 증가로 인해 SSD를 구성하는 칩 수가 감소함.
- 칩 수 감소 = **chip-level 병렬성(small multi-chip parallelism) 감소** → 읽기 성능 심각하게 저하.
- 실제 벤치마크 비교 (Samsung 950 Pro: 16칩 vs Samsung 960 Pro: 8칩): 960 Pro가 Iometer, CrystalDiskMark, AS-SSD 등 3개 읽기 중심 벤치마크에서 950 Pro보다 성능이 떨어짐 (Figure 1).
- 600개 스토리지 워크로드 분석 결과: 읽기 요청의 대부분이 4KB/8KB 크기로, 3D NAND의 최소 읽기 단위(16KB)보다 작음 (Figure 3b).
- 읽기 응답 locality가 낮음: 600개 워크로드 중 처음 400개에서 주소의 80% 이상이 한 번만 읽힘 (Figure 3a) → DRAM 캐싱으로 읽기 지연 시간 개선 불가.
- 기존 읽기 연산(multi-plane, cache, random-output)은 칩 내부 병렬성을 개선하지 못함 → 칩 밀도 증가에 따른 성능 병목 미해결.

## 방법론

### 3.1. 3D NAND Micro-Architecture 분석

- 2D NAND: 블록이 평면(plane)에 나란히 배치, 페이지가 직렬로 연결.
- 3D NAND: 블록이 수직 슬라이스(slice)로 구성, 여러 슬라이스가 두꺼운 cross-layer signal을 공유.
- 2D NAND에서 read granularity를 줄이면 밀도가 떨어지지만, **3D NAND에서는这种 관계가 없음** (Section 2.1.1).
- 3D NAND 읽기 지연 시간 최대 90µs (cell sensing time이 병목).
- ECC(에러 교정 코드) 관련 추가 read 연산(re-read)이 읽기 지연을 추가로 증가시킴.

### 3.2. SOML Read 동작 원리

- 기존 읽기: 하나의 페이지(≥16KB)를 한 번에 읽음 → 하나의 요청이 칩 리소스를 독점.
- SOML Read: 여러 다른 블록의 partial-page를 동시에 읽음 → 여러 요청이 병렬 처리 가능.
- Figure 4a/4b의 읽기 연산 비교:
  - Baseline read: 전체 페이지 단위, 하나의 plane에서 읽기
  - Multi-plane read: 여러 plane에서 동시에 읽기
  - Cache read: 두 세트의 내부 버퍼로 읽기와 전송 병렬화
  - Random-output read: 필요 데이터만 전송하여 채널 트래픽 감소
  - **SOML Read:** 여러 위치에서 partial-page를 동시에 읽어 칩 내부 병렬성 최대화

### 3.3. SOML Read Scheduling Algorithm

- 스케줄러: 대기 중인 여러 작은 읽기 요청을 감지하여 하나의 SOML read로 병합.
- Figure 5a: 8칩 시스템에서 요청 대기 큐가 길어지는 것을 SOML read로 완화.
- SOML read 기반 8칩 SSD가 baseline 16칩 SSD보다 2.8x 높은 throughput 달성.

## 핵심 기여

- **핵심 Contribution:** 3D NAND SSD의 읽기 성능 병목을 칩 내부 병렬성 향상으로 해결하는 최초의 연구.
- **성능 향상:** SOML read 기반 8칩 SSD가 16칩 SSD 대비 2.8x throughput 향상.
- **의의:** 고밀도 3D NAND SSD의 광범위한 도입을 가로막는 읽기 성능 문제를 근본적으로 해결하여, 차세대 스토리지 시스템 설계에 중요한 함의를 제공.

## 주요 결과

- **구현 언어:** C (SSDSim 시뮬레이터 기반)
- **시뮬레이터:** SSDSim [15]를 확장하여 SOML read 지원.
- **평가 환경:** 3가지 동일 용량 SSD 설정:
  - (A) 32칩 × 16GB
  - (B) 16칩 × 32GB
  - (C) 8칩 × 64GB
- 채널 수는 모두 4로 동일 (채널 병렬성 통제).
- 워크로드: OpenStr [27]에서 600개 스토리지 워크로드 사용.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2019ASPLOS-summarize/soml-read-rethinking-read-granularity-of-3d-nand-ssds.md|전체 요약 보기]]
