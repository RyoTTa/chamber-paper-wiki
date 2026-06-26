---
tags: [paper, 2018, 2018MICRO, topic/cache, topic/compression, topic/virtual-memory]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/compresso-pragmatic-main-memory-compression.md"
---

# Compresso: Pragmatic Main Memory Compression

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Esha Choukse, Mattan Erez, Alaa R. Alameldeen (University of Texas at Austin, Intel Labs)

## 개요

- 머신러닝, 그래프 분석, 데이터베이스, 게임, 자율주행 등 많은 클라이언트/데이터센터 애플리케이션이 더 큰 메모리 용량과 높은 대역폭을 필요로 함
- 하드웨어 메모리 압축은 시스템 비용 증가 없이 성능과 에너지 효율을 향상시키는 유망한 방향이지만, 두 가지 주요 과제에 직면:
  1. **추가 데이터 이동 오버헤드**: 압축된 데이터 관리 시 메타데이터 접근, 압축률 변화, 캐시라인 경계를 넘어선 압축 등으로 인해 평균 **63%의 추가 메모리 접근** 발생 (최대 180%)
  2. **OS 지원 필요성**: 기존 기법들은 압축된 메모리의 용량 증가를 활용하기 위해 OS 수정이 필요하거나, 비압축 데이터 처리를 위한 하드웨어 변경이 필요
- 기존 주요 기법들의 한계:
  - **IBM MXT**: OS 수정 필요 (free page zeroing, out-of-memory 알림), 1KB 압축 granularity로 인해 32MB L3 캐시 필요
  - **LCP (Linearly Compressed Pages)**: OS-aware, 페이지 오버플로 시 page fault 발생
  - **RMC**: OS-aware, 하드웨어 BST(Block Size Table) 필요
  - **Buri/DMC**: 부분적으로 OS 변경 필요
- **Split-access 문제**: 압축된 캐시라인이 메모리의 캐시라인 경계를 넘어 저장되면 추가 메모리 접근 발생 — 기존 연구에서 간과된 주요 문제

## 방법론

### 3.1. 압축 알고리즘 및 granularity

- **BPC (Bit-Plane Compression)** 채택: 높은 평균 압축률 (BDI 대비 우수)
  - Delta-Bitplane-Xor 변환으로 데이터 압축률 향상
  - CPU용으로 granularity를 128B→64B로 축소 (캐시라인 크기에 맞춤)
  - BPC 변환 없이 압축하는 병렬 경로를 추가하여 평균 13% 더 많은 메모리 절약
- **압축 granularity**: 64B (캐시라인 크기)
- **캐시라인 패킹**: LinePack 방식, 4가지 압축 크기 (0/8/32/64B)
  - LCP-Packing 대비 BPC 사용 시 압축률 13% 높음
  - 캐시라인 오프셋 계산: 커스텀 저지연 산술 유닛으로 1클래시 내 계산 가능

### 3.2. 주소 번역 경계

- **OS-투명 번역**: VA→OSPA(기존 가상→물리), OSPA→MPA(압축 메모리) 두 단계 번역
  - OSPA→MPA 변환은 메모리 컨트롤러에서 처리
  - OS는 4KB 고정 페이지 크기를 사용 (2MB/1GB huge page도 4KB 블록으로 분할 가능)
- **메타데이터 구조**: OSPA 페이지당 64B 메타데이터 (총 용량의 1.6%)
  - 페이지 크기, valid/zero/compressed 플래그, 최대 8개 MPFN(512B 청크), 인플레이션 포인터

### 3.3. 데이터 이동 최적화

#### 3.3.1. 정렬 친화적 캐시라인 크기
- 기존 LCP: 0/22/44/64B → split-access 30.9%
- Compresso: 0/8/32/64B → split-access 3.2%로 감소 (압축률 손실仅 0.25%)
- 추가 접근: 63% → 36%로 감소

#### 3.3.2. 페이지 오버플로 예측
- 스트리밍 비압축 데이터의 캐시라인 오버플로를 사전에 예측
- 메타데이터 캐시 엔트리당 2비트 포화 카운터 + 3비트 글로벌 예측기
- 예측된 페이지는 최대 크기(4KB)로 사양적 확장하여 데이터 이동 방지
- false negative 22.5%, false positive 19% → 추가 접근 36% → 26%로 감소

#### 3.3.3. 동적 인플레이션 룸 확장
- 캐시라인 오버플로 시 인플레이션 룸에 저장, 공간 부족 시 추가 512B 청크 할당
- 기존: 페이지 전체 재압축 (최대 64 읽기+64 쓰기)
- Compresso: 추가 512B 청크 할당으로 1회 쓰기만 필요
- 추가 접근 26% → 19%로 감소

#### 3.3.4. 동적 페이지 리패킹
- 메타데이터 캐시 퇴출 시 리패킹 트리거 (핫 페이지의 메타데이터 캐시 퇴출 특성 활용)
- 압축률 손실: 24% → 2.6%로 감소, 추가 접근 1.8%만 발생

#### 3.3.5. 메타데이터 캐시 최적화
- 비압축 페이지의 메타데이터를 절반 크기(32B)로 저장하여 캐시 유효 용량 2배 확장
- 추가 접근 19% → 15%로 감소

### 3.4. OS-투명성 구현

- **페이지 오버플로 처리**: OS에 예외를 발생시키지 않고 하드웨어 내부에서 처리
- **메모리 부족 시**: Linux의 memory ballooning 기능 활용
  - Compresso 드라이버가 `__alloc_pages()` API를 사용하여 메모리 회수
  - OS 수정 불필요, 기존 가상 머신 인프라 재사용
- **리패킹**: 동적 페이지 리패킹으로 압축률 복원

## 핵심 기여

- **핵심 기여**: 압축 공격성과 데이터 이동 오버헤드 사이의 새로운 트레이드오프를 식별하고 최적화
- **실용성**: OS 수정 없이 하드웨어 메모리 압축을 구현한 최초의 아키텍처 — 기존 OS(Linux, Windows, macOS)에서 그대로 동작
- **성능**: 비압축 메모리 대비 29% speedup (메모리 제한 시), 기존 최첨단 압축 기법(LCP) 대비 24-27% 향상
- **압축률**: 평균 1.85× 압축률 달성, 추가 메모리 접근을 63%에서 15%로 크게 감소
- **평가 방법론**: 메모리 용량 영향을 고려한 홀리스틱 평가 방법론 제안 — 기존 사이클 기반 시뮬레이션만으로는 압축의 전체 효과를 측정할 수 없음을 지적
- **의의**: 메모리 압축을 실제 시스템 채택에 가깝게 실용화 — 데이터 이동 최적화와 OS 투명성을 동시에 달성

## 주요 결과

- **구현**: zsim 시뮬레이터 확장
- **압축/해제 지연**: BPC 기준 12사이클 (8사이클 DDR4 버퍼링 + 2사이클 비트플ANE 처리 + 2사이클 연결)
- **메타데이터 캐시**: 96KB, 8-way
- **에너지 추정**: McPAT + CACTI, BPC는 40nm TSMC 표준 셀로 합성
  - BPC 활성 전력: 7mW (DDR4 채널 활성 전력의 0.4% 미만)
  - 메타데이터 캐시 접근 에너지: 0.08nJ (DRAM 읽기 에너지의 0.8% 미만)
- **면적**: BPC 압축기 43Kμm², 메타데이터 캐시 ~100Kμm²

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/compresso-pragmatic-main-memory-compression.md|전체 요약 보기]]
