---
tags: [persistent-memory, nvm, crash-consistency, software-persistency]
venue: ISCA
year: 2018
summary_path: paper-summaries/2018ISCA-summarize/lazy-persistency-a-high-performing-and-write-efficient-software-persistency-technique.md
---

# Lazy Persistency: A High-Performing and Write-Efficient Software Persistency Technique

## 개요

Lazy Persistency(LP)는 캐시의 자연적 퇴출을 통해 NVM으로 데이터를 전송하는 소프트웨어 영속성 기법입니다. Eager Persistency의 높은 쓰기 증폭과 성능 오버헤드를 크게 감소시킵니다.

## 방법론

- **자연적 캐시 퇴출**: 캐시가 더러운 블록을 NVMM으로 강제 플러시하지 않고 자연적 캐시 교체를 통해 전송
- **소프트웨어 오류 검출**: 체크섬(checksum)을 통해 영속성 실패 탐지
- **재계산 기반 복구**: 불일치하는 결과를 재계산하여 복구 (복구 시에만 Eager Persistency 적용)

## 핵심 기여

1. 정상 실행 시 NVMM 쓰기 없음 → 쓰기 내구성 저하 없음
2. 캐시 라인 플러시/배리어로 인한 성능 오버헤드 제거
3. Modular Checksum으로 높은 오류 탐지 정확도(2×10⁻⁹ 미만) 달성

## 주요 결과

- 실행 시간 오버헤드: Eager Persistency 9% → LP 1%
- 쓰기 증폭 오버헤드: Eager Persistency 21% → LP 3%
- 체크섬 및 해시 테이블 공간 오버헤드: 행렬 크기의 1%

## 한계점

- 복구 시 Eager Persistency 적용 필요 → 복구 시간 비용 발생
- 복구 코드가 프로그램 의존적 (비멱등 영역의 경우)
- 과학 컴퓨팅 커널에 최적화되어 일반적인 워크로드 적용은 추가 연구 필요

## 관련 concept

- [[paper-wiki/concepts/nvm.md|NVM (Non-Volatile Memory)]]
- [[paper-wiki/concepts/persistent-memory.md|Persistent Memory]]
