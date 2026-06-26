---
tags: [paper, 2019, 2019ISCA, topic/dram, topic/nvm, topic/security]
venue: "The 46th Annual International Symposium on Computer Architecture (ISCA '19)"
year: 2019
summary_path: "../paper-summaries/2019ISCA-summarize/anubis-ultra-low-overhead-and-recovery-for-secure-nvms.md"
---

# Anubis*: Ultra-Low Overhead and Recovery Time for Secure Non-Volatile Memories

**Venue:** The 46th Annual International Symposium on Computer Architecture (ISCA '19)
**저자:** Kazi Abu Zubair (University of Central Florida), Amro Awad (University of Central Florida)

## 개요

- NVM(Non-Volatile Memory) 기술(PCM 등)은 DRAM 대체 후보로 주목받지만, **보안과 지속성(persistence)의 동시 달성**이 핵심 과제
- 현대 보안 메모리 시스템은 counter-mode encryption을 사용하며, 각 메모리 블록(캐시라인)에 암호화/복호화에 사용되는 카운터가 할당됨
- 카운터의 무결성 보호를 위해 **Merkle Tree**가 일반적으로 사용됨 — 리프 노드가 카운터이고, 루트는 프로세서 칩 내부에 유지
- NVM 시스템에서의 보안 메타데이터 복원 문제:
  - **수정된 카운터와 Merkle Tree 노드가 NVM에 완전히 반영되기 전에 크래시 발생** → 데이터와 보안 메타데이터 간 불일치
  - **SGX 스타일의 병렬 가능 integrity tree의 복원은 특별한 처리 필요** — 레벨 간 의존성(inter-level dependency)으로 인해 리프(카운터)만 복원해서는 불가능
  - **실용적 NVM 용량(TB급)에서의 복원 시간이 수 시간 소요** — Intel Xeon 서버는 6TB NVM 탑재 예정, 8TB NVM 복원에 **7.8시간** 소요
  - 클라우드 시스템에서 다운타임 비용: Amazon 기준 **분당 약 7만 달러**, 99.999% 가용성 목표 시 연간 최대 5.25분 다운타임 허용

## 방법론

### 3.1. 보안 NVM의 문제 분석

- **카운터-모드 암호화**: 각 캐시라인에 고유 카운터가 할당, 프로세서 키와 함께 암호화/복호화 수행
- **Merkle Tree 구조**: 리프 = 카운터, 중간 노드 = 해시, 루트 = 프로세서 칩 내부 유지
- 카운터 업데이트 시 트리 루트까지 모든 레벨이 업데이트되어야 하며, 이 과정이 NVM에 원자적으로 persist되어야 함
- 문제점:
  - Merkle Tree의 모든 레벨(수십 개)을 업데이트하는 것은 NVM의 느린 쓰기와 제한된 수명으로 인해 비실용적
  - SGX 스타일 integrity tree는 병렬 업데이트를 지원하지만, 리프 복원만으로는 트리 전체 복원 불가능

### 3.2. Anubis 복원 메커니즘

- **복원 시간 극대 단축**: 하드웨어 전용 로직으로 NVM에 persist된 보안 메타데이터를 즉시 복원
- **SGX 트리 복원 지원**: 레벨 간 의존성이 있는 integrity tree를 효과적으로 복원하는 새로운 방법론
- **하드웨어 전용 구현**: 소프트웨어 오버헤드 없이 순수 하드웨어로 구현되어 극도로 낮은 복원 시간 달성
- **Merkle Tree와 SGX 트리 모두 지원**: 가장 도전적인 integrity 보호 스키마 중 하나인 SGX 트리의 복원을 보장하면서도 일반 Merkle Tree도 지원

### 3.3. 복원 프로세스

- 크래시 후 전원 복구 시, Anubis 하드웨어가 NVM에 저장된 보안 메타데이터 블록들을 순차적으로 복원
- 복원된 메타데이터를 기반으로 첫 메모리 접근 시 integrity 검증 수행
- 기존 방식(Osiris) 대비 복원 시간이 **8시간 → 0.03초**로 **약 10^7배** 단축
- 메모리 데이터베이스 시스템 등에서 크래시 직후 트랜잭션 커밋 후 바로 새 트랜잭션/질의 수행 가능

## 핵심 기여

- **핵심 Contribution**: 보안 NVM의 복원 시간을 거의 10^7배 단축하는 하드웨어 전용 솔루션 Anubis 제안
- **실용성**: 99.999% 가용성 요구사항을 충족하는 즉시 복원 능력 (0.03초)
- **성능 오버헤드 최소화**: 최첨단 방식 대비 2% 수준의 오버헤드로 보안과 성능을 동시에 달성
- **의의**: NVM 기반 보안 메모리 시스템의 실용화를 위한 핵심 기술로, 데이터 센터, 클라우드, HPC 시스템에서의 즉시 복구 보장

## 주요 결과

- **구현 방식**: 순수 하드웨어 전용(hardware-only) 솔루션
- **호환 대상**: Intel SGX 스타일 integrity tree 및 일반 Merkle Tree 모두 지원
- **성능 오버헤드**: 최첨단 방식인 Osiris 대비 2% 수준
- **복원 대상 용량**: 실용적 NVM 크기(TB급)에서도 즉시 복원 가능

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/security.md|Security]]


## 전체 요약

[[../paper-summaries/2019ISCA-summarize/anubis-ultra-low-overhead-and-recovery-for-secure-nvms.md|전체 요약 보기]]
