---
tags: [paper, 2018, 2018MICRO, topic/cache, topic/dram, topic/server]
venue: "MICRO 2018"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/farewell-my-shared-llc-a-case-for-private-die-stacked-dram-caches-for-servers.md"
---

# Farewell My Shared LLC! A Case for Private Die-Stacked DRAM Caches for Servers

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Amna Shahab, Mingcan Zhu, Artemiy Margaritov, Boris Grot (University of Edinburgh)

## 개요

기존 서버 프로세서의 공유 LLC(Last-Level Cache)는 온칩 면적 제약, 긴 와이어 지연, 워크로드 간 캐시 경쟁 등 여러 한계를 가짐. 이 논문은 다이 스택 DRAM 기반 프라이빗 LLC를 제안하는 SILO(SILO: Die-Stacked Private LLC Organization) 아키텍처를 제시. 각 코어 위에 직접 스택된 DRAM 볼트로 프라이빗 LLC를 구현하여 온칩 면적 제약, 긴 와이어 지연, 캐시 경쟁 문제를 해결.

## 방법론

### SILO 아키텍처
- **프라이빗 LLC 구조:** 각 코어 위에 직접 스택된 독립적인 DRAM 캐시 슬라이스(볼트)
- **지연 시간 최적화 DRAM:** 기존 용량 최적화 설계 대비 45% 지연 시간 감소 (22nm)
- **캐시 일관성:** 디렉토리 기반 프로토콜로 프라이빗 캐시 간 일관성 유지
- **볼트 구조:** Hybrid Memory Cube(HMC)와 유사하나 CPU 다이 위에 스택

### 워크로드 민감도 분석
- **용량 민감도:** 64MB 이상에서 세컨더리 워킹 세트가 캐시에 들어가면서 큰 성능 향상
- **레이턴시 민감도:** 큰 LLC는 낮은 레이턴시에서만 높은 성능 발휘
- **RW-공유:** 스케일아웃 워크로드에서 RW-공유는 매우 제한적 (Web Search 4%, Data Serving 3%)

## 핵심 기여

- 공유 LLC의 한계를 극복하기 위한 SILO 아키텍처 최초 제시
- 다이 스택 DRAM 기반 프라이빗 LLC로 온칩 면적 제약, 긴 와이어 지연, 캐시 경쟁 문제 해결
- 지연 시간 최적화된 DRAM 캐시 설계로 45% 지연 시간 감소, 11.5ns 접근 지연 시간 달성
- 서버 프로세서의 캐시 계층 설계에 새로운 방향성 제시

## 주요 결과

- 16코어 SILO 배포 시 CloudSuite 워크로드에서 **5-54% 성능 향상**
- 기존 공유 LLC + DRAM 캐시 대비 높은 성능 달성
- **강력한 성능 격리:** 프라이빗 캐시로 워크로드 콜로케이션 시 성능 격리 제공
- 지연 시간 최적화 DRAM 캐시가 성능 향상의 핵심 요인

## 한계점

- 다이 스택 기술의 성숙도 및 제조 비용 문제
- 열 관리 등실용화 과제 존재
- 스케일아웃 워크로드 외 다른 워크로드에서의 효과 추가 검증 필요

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/server.md|Server]]

## 전체 요약

[[../paper-summaries/2018MICRO-summarize/farewell-my-shared-llc-a-case-for-private-die-stacked-dram-caches-for-servers.md|전체 요약 보기]]
