---
tags: [paper, 2018, 2018MICRO, topic/security, topic/memory, topic/integrity]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO), 2018"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/morphable-counters-enabling-compact-integrity-trees-for-low-overhead-secure-memories.md"
---

# Morphable Counters: Enabling Compact Integrity Trees For Low-Overhead Secure Memories

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Gururaj Saileshwar, Prashant J. Nair, Prakash Ramrakhyani, Wendy Elsasser, Jose A. Joao, Moinuddin K. Qureshi (Georgia Institute of Technology, IBM Research, Arm Research)

## 개요

- 오프칩 메모리 보안은 물리적 접근이 가능한 공격자로부터 시스템을 보호하는 데 필수적
- 기존 보안 메모리 설계는 무결성 트리 순회에 필요한 다수의 메모리 접근으로 상당한 성능 오버헤드 유발
- Morphable Counters는 보안 메모리에서 사용되는 카운터를 위한 새로운 저장 효율적 표현 방식 제시

## 방법론

### 3.1. 카운터 표현 방식

- **Split Counters (기존):** 하나의 큰 카운터를 여러 개의 작은 카운터로 분할 (저장 효율성은 좋으나 캐시 가능성 낮음)
- **Morphable Counters (제안):** 동적으로 카운터 크기와 표현 방식을 전환 가능 (캐시 라인당 더 많은 카운터 저장 가능)

### 3.2. Compact Integrity Tree

- **128-ary 트리 구조:** 기존 64-ary 트리 대비 더 높은 차수로 트리 깊이 감소
- 16GB 메모리 기준 트리 크기: **4MB → 1MB** (75% 감소)

### 3.3. 동적 카운터 전환 메커니즘

- 사용 패턴 모니터링에 따라 동적으로 카운터 크기 전환
- 오버플로우 발생 시 동적 전환으로 오버헤드 최소화

## 핵심 기여

- **핵심 기여:** Morphable Counters를 통한 compact integrity tree 구현으로 보안 메모리 성능 향상
- **성능 향상:** 기존 설계 대비 최대 **28.3%** 성능 향상, VAULT 대비 최대 **47.4%** 속도 향상
- **저장 공간 절약:** 무결성 트리 크기 **75%** 감소 (4MB → 1MB)

## 주요 결과

- 기존 split counter 64-ary 트리 대비 평균 **6.3%** (최대 **28.3%**) 성능 향상
- VAULT 대비 평균 **13.5%** (최대 **47.4%**) 속도 향상
- 시스템 에너지-지연 곱(EDP) 평균 **8.8%** 감소
- 보안 저하 없이 성능 향상 달성

## 한계점

- 다양한 보안 메모리 기술 및 실제 시스템에서의 통합 검증 필요
- 카운터 전환 메커니즘의 하드웨어 오버헤드 추가 분석 필요
- 더 큰 메모리 시스템에서의 확장성 검증 필요

## 관련 개념

- [[paper-wiki/concepts/memory-security|Memory Security]]
- [[paper-wiki/concepts/integrity-tree|Integrity Tree]]
- [[paper-wiki/concepts/secure-memory|Secure Memory]]

## 관련 논문

- [morphable-counters-enabling-compact-integrity-trees-for-low-overhead-secure-memories.md](../paper-summaries/2018MICRO-summarize/morphable-counters-enabling-compact-integrity-trees-for-low-overhead-secure-memories.md)
