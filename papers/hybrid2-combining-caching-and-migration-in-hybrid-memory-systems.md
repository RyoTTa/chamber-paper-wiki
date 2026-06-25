---
tags: [paper, 2020, 2020HPCA, topic/cache, topic/dram, topic/gpu, topic/memory-tiering, topic/pim]
venue: "2020 IEEE International Symposium on High Performance Computer Architecture (HPCA '20)"
year: 2020
summary_path: "../paper-summaries/2020HPCA-summarize/hybrid2-combining-caching-and-migration-in-hybrid-memory-systems.md"
---

# Hybrid2: Combining Caching and Migration in Hybrid Memory Systems

**Venue:** 2020 IEEE International Symposium on High Performance Computer Architecture (HPCA '20)
**저자:** Alexandros K. Kanellopoulos (Chalmers University of Technology), Nectarios Koziris (National Technical University of Athens), Georgios Goumas (National Technical University of Athens)

## 개요

- 메모리 월(emory wall) 문제: 프로세서와 메모리 간 성능 격차가 지속적으로 확대되어, 메모리 집약적 애플리케이션의 성능을 저해
- 3D 스택 DRAM(예: HBM)과 같은 고대역폭 Near Memory(NM)와 대용량 Low Bandwidth Far Memory(FM)를 혼합한 이종 메모리 시스템이 대두
- 기존 접근법의 한계:
  - **캐시 기반 접근 (Tagless DRAM Cache, DFC):** NM의 전체 용량을 캐시로 사용하여 캐시 미스 시 FM으로의 스왑 오버헤드 발생. 캐시 교체 시 데이터 손실로 인해 실제 사용 가능한 메모리 용량 감소 (5.9~24.6% 용량 손실)
  - **마이그레이션 기반 접근 (Mempod, LGM, Chameleon):** 데이터를 NM으로 투명하게 마이그레이션하지만, 마이그레이션 메타데이터 관리 오버헤드, 주소 변환 비용, 그리고 마이그레이션 결정의 비효율성으로 인해 성능 제한 (최대 9.1%까지 성능 격차)
  - **기존 시스템의 캐시 용량 한계:** 작은 캐시 크기와 큰 섹터 크기로 인해 NM 활용률 저하 (평균 42~88% 활용)

## 방법론

### 3.1. 시스템 구성

- 프로세서: 8코어, 아웃오브オーダー, 4-way issue/commit, 3.2 GHz
- NM: HBM2 2GHz, 1/2/4 GB, 8채널 (128비트), 8뱅크
- FM: DDR4-3200, 16 GB, 2채널 (64비트), 8뱅크
- DCMC(DRAM Cache Migration Controller): 캐시 관리, 주소 변환, 마이그레이션 결정을 담당
- 64 MByte DRAM 캐시, 2 KByte 섹터, 256 Byte 캐시 라인, 16-way 연관성 (최적 설계)

### 3.2. eXtended Tag Array (XTA)

- **온칩 태그 배열:** 모든 DRAM 캐시 태그를 온칩에 유지하여 최소 지연 시간으로 태그 조회
- **섹터 기반 설계:** 각 XTA 엔트리에 섹터 태그 + 유효/더티 비트 벡터 + 접근 카운터 + NM/FM 포인터 포함
- **NM/FM 포인터:** 캐시 라인의 물리적 위치를 추적하여 인디렉션 기반 마이그레이션 지원
  - NM 포인터: NM 내 위치 (캐시 라인 수준)
  - FM 포인터: FM 내 원래 위치 (섹터 수준)
- **적응형 마이그레이션 결정:** 접근 카운터 기반으로 가장 많이 접근된 섹터를 NM으로 마이그레이션

### 3.3. 메모리 접근 경로 (Memory Access Path)

- **XTA 히트/캐시 라인 히트 (1a):** 데이터가 NM에 존재 → NM 포인터로 직접 접근
- **XTA 히트/캐시 라인 미스 (1b):** 캐시 라인이 FM에만 존재 → FM 포인터로 읽기 후 NM 포인터로 기록
- **XTA 미스/섹터 in NM (2a):** 리맵 테이블 조회 → XTA 엔트리 업데이트
- **XTA 미스/섹터 in FM (2b):** NM 할당 필요 → 마이그레이션 프로세스 실행

### 3.4. 마이그레이션 결정 알고리즘

- **마이그레이션 오버헤드 계산:**
  - FM 트래픽 비용: `MOcost = 2*Nall - Nvalid - Ndirty + 1`
  - Nall: 섹터의 전체 캐시 라인 수
  - Nvalid: 캐시에 유효한 캐시 라인 수
  - Ndirty: 더티 캐시 라인 수
- **트래픽 균형 메커니즘:** FM 접근 카운터를 통해 마이그레이션 트래픽과 프로세서 트래픽 간 균형 유지 (100K 사이클마다 리셋)
- **가장 많이 접근된 섹터 선택:** XTA의 접근 카운터를 비교하여 가장 많이 접근된 섹터만 마이그레이션

## 핵심 기여

- **핵심 기여:** 캐시와 마이그레이션을 결합한 최초의 메모리 시스템 제안. 공통 XTA 메커니즘을 통해 메타데이터 관리 오버헤드 최소화
- **성능 향상:** 마이그레이션 기반 설계 대비 6.4~9.1% 성능 향상, 캐시 기반 설계 대비 5.9~24.6% 더 많은 메모리 용량 제공
- **실용성:** 64 MByte 캐시, 2 KByte 섹터, 256 Byte 캐시 라인의 실용적 구성으로 최적 성능
- **의의:** DRAM 캐시와 데이터 마이그레이션을 결합하여 메모리 용량과 성능 모두를 달성하는 새로운 패러다임 제시. 주소 변환 오버헤드를 최소화하여 실제 시스템 적용 가능성 입증

## 주요 결과

- **시뮬레이터:** Pin 기반 인하우스 시뮬레이터 + DRAMSim2 (사이클 정확도)
- **에너지/면적 모델링:** Cacti (캐시 접근 시간), NVProf + GPUWattch (비교용)
- **구현 언어:** C++ (시뮬레이터), Python (분석)
- **시스템 구성 요소:**
  - 프로세서: 8코어, L1 64KB, L2 256KB, L3 8MB (공유)
  - NM: HBM2 (1/2/4 GB), FM: DDR4 (16 GB)
  - DCMC: XTA (512KB), 리맵 테이블, 역리맵 테이블, Free-FM-스택

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2020HPCA-summarize/hybrid2-combining-caching-and-migration-in-hybrid-memory-systems.md|전체 요약 보기]]
