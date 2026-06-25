---
tags: [sgx, security, memory-integrity, paging, compression]
venue: ASPLOS
year: 2018
summary_path: paper-summaries/2018ASPLOS-summarize/vault-reducing-paging-overheads-in-sgx-with-efficient-integrity-verification-structures.md
---

# VAULT: Reducing Paging Overheads in SGX with Efficient Integrity Verification Structures

## 개요

VAULT는 Intel SGX의 페이징 오버헤드를 해결하기 위한 효율적인 무결성 검증 구조로, VAULT 트리와 MAC 공유/압축 기법을 통해 기존 SGX 대비 3.7배 성능 향상을 달성합니다.

## 방법론

- **VAULT(Variable Arity Unified Tree)**: 더 컴팩트하고 낮은 깊이를 가진 무결성 트리 구조
- **MAC 공유 및 압축**: 무결성 검증의 공간 오버헤드를 4.7%로 감소
- **EPC 확장 전략**: 비민감한 페이지도 EPC에 수용 가능하도록 확장

## 핵심 기여

- SGX의 페이징 오버헤드를 효과적으로 해결하는 VAULT 트리 제시
- 메모리 용량 오버헤드를 4.7%로 유지하면서 성능 크게 향상
- 클라우드 환경에서의 보안-성능 트레이드오프 극복

## 주요 결과

- 기존 SGX 대비 3.7배 성능 향상
- 메모리 용량 오버헤드 4.7% 유지
- 효과적인 페이징 오버헤드 감소
- 낮은 트리 깊이로 메모리 대역폭 절약

## 한계점

- 시뮬레이션 기반 평가로 실제 하드웨어 검증 필요
- Intel SGX에 특화된 솔루션

## 관련 개념

- [[paper-wiki/concepts/sgx|SGX]]
- [[paper-wiki/concepts/security|Security]]
- [[paper-wiki/concepts/memory-integrity|Memory Integrity]]