---
tags: [paper, 2021, 2021HPCA, topic/cache, topic/dram, topic/nvm]
venue: "2021 IEEE International Symposium on High-Performance Computer Architecture (HPCA '21)"
year: 2021
summary_path: "../paper-summaries/2021HPCA-summarize/stealth-persist-architectural-support-for-persistent-applications-in-hybrid-memory.md"
---

# Stealth-Persist: Architectural Support for Persistent Applications in Hybrid Memory Systems

**Venue:** 2021 IEEE International Symposium on High-Performance Computer Architecture (HPCA '21)
**저자:** Mazen Alwadi (University of Central Florida), Vamsee Reddy Kommareddy (University of Central Florida), Clayton Hughes (Sandia National Laboratories), Simon David Hammond (Sandia National Laboratories), Amro Awad (North Carolina State University)

## 개요

- 비휘발성 메모리(NVM)는 바이트 주소 지정 가능하면서도 영속성을 가지지만, 읽기 지연 시간이 DRAM 대비 **4.3배** 높음 (Optane DC 기준 300ns vs 70ns)
- 하이브리드 메모리 시스템은 DRAM과 NVM을 결합하여 DRAM이 NVM 데이터를 캐싱하지만, 이는 **캐시된 페이지의 영속성을 무효화**할 수 있음
- 현재 Optane DC 모듈의 통합 옵션은 두 가지 모드로 나뉨:
  - **메모리 모드**: DRAM이 NVM의 하드웨어 관리 캐시로 동작하나 영속성 보장 불가
  - **애플리케이션 다이렉트 모드**: NVM 영역의 영속성은 보장되나 제한된 프로세서 캐시만 사용 가능하여 높은 지연 시간 발생
- 기존 NVDIMM 표준(NVDIMM-N, NVDIMM-P, NVDIMM-F)은 각각 다른 용량, 영속성 보장, 관리 복잡도 트레이드오프를 제공하지만, 성능과 영속성을 동시에 만족하는 옵션 부재
- 지속성 있는 애플리케이션(데이터베이스, 파일 시스템 등)은 **느린 NVM을 사용하여 영속성을 확보**하거나 **빠른 DRAM을 사용하여 영속성을 포기**하는 선택에 직면

## 방법론

### 3.1. 영속성錯覺 메커니즘

- 애플리케이션은 NVM 주소 공간에 대해 load/store 명령을 사용
- Stealth-Persist가 이를 DRAM 캐시로 리다이렉션하면서 영속성 보장
- **Write Path**: 
  - 애플리케이션의 쓰기 요청을 DRAM 캐시에 기록
  - 캐시 라인 더티비트(tracking)를 통한 영속성 관리
  - 캐시 라인 플러시 시 NVM으로의 안전한 데이터 전송 보장
- **Read Path**:
  - DRAM 캐시 히트 시 빠른 읽기 (70ns)
  - 캐시 미스 시 NVM에서 데이터 로드 후 캐시에 저장

### 3.2. 영속성 관리 하드웨어

- **Persistent Cache Line Controller (PCLC)**:
  - 각 DRAM 캐시 라인의 영속성 상태를 추적
  - 영속성 플래그(persistent bit)를 캐시 라인 메타데이터에 추가
  - 캐시 라인 교체 시 영속성 보장 여부 확인 후 NVM 플러시 수행
- **Write Ahead Log (WAL) 통합**:
  - 기존 PMDK의 WAL 메커니즘과 통합
  - 캐시 라인 플러시 전에 WAL에 기록하여 crash consistency 보장
  - WAL은 NVM에 별도 영역으로 할당

### 3.3. 캐시 교체 정책

- **Persistence-Aware Eviction**:
  - 영속성이 필요한 캐시 라인은 교체 우선순위 낮춤
  - 영속성 비필요 캐시 라인이 먼저 교체되도록 정책 조정
- **Selective Flush**:
  - 더티 캐시 라인 중 영속성이 필요한 것만 NVM으로 플러시
  - 불필요한 플러시를 줄여 성능 오버헤드 최소화

## 핵심 기여

- Stealth-Persist는 DRAM/NVM 하이브리드 메모리에서 **영속성과 성능을 동시에 보장**하는 최초의 아키텍처 지원 기능
- NVM-only 대비 **42.02%** 성능 향상하면서 영속성 손실 없음
- 기존 메모리 모드의 영속성 손실 문제를 해결하면서도 유사한 성능 수준 달성
- 향후 NVM 기술 발전에 따른 영속성 애플리케이션 성능 개선에 기여
- 실제 시스템 구현을 위한 하드웨어/소프트웨어 코디자인 가이드라인 제시

## 주요 결과

- **시뮬레이션 환경**: gem5 시뮬레이터 기반 구현
- **하드웨어 추가**: 캐시 라인당 영속성 비트 및 컨트롤러 로직
- **소프트웨어 지원**: 수정된 메모리 관리자와 영속성 관리 라이브러리
- **시스템 구성**: 
  - 8코어 프로세서, 32KB L1 캐시, 256KB L2 캐시, 8MB L3 캐시
  - DRAM: 8GB DDR4 (3000MHz)
  - NVM: 8GB Optane DC (모델링)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]


## 전체 요약

[[../paper-summaries/2021HPCA-summarize/stealth-persist-architectural-support-for-persistent-applications-in-hybrid-memory.md|전체 요약 보기]]
