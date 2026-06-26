---
tags: [paper, 2018, 2018ASPLOS, topic/cache, topic/security]
venue: "ASPLOS 2018 (Architectural Support for Programming Languages and Operating Systems)"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/vault-reducing-paging-overheads-in-sgx-with-efficient-integrity-verification-structures.md"
---

# VAULT: Reducing Paging Overheads in SGX with Efficient Integrity Verification Structures

**Venue:** ASPLOS 2018 (Architectural Support for Programming Languages and Operating Systems)
**저자:** Meysam Taassori, Ali Shafiee, Rajeev Balasubramonian (University of Utah)

## 개요

- Intel SGX는 민감한 페이지에 대한 기밀성, 무결성, 인증(CIA) 보장을 제공하는 최첨단 보안 기능
- 민감한 페이지는 물리적 메모리 내의 Enclave Page Cache(EPC)에 배치되어 프로세서에 의해 접근됨
- EPC는 제한된 용량(현재 128MB)으로 운영되어 빈번한 페이지 스왑 필요
- 페이지 스왑은 OS 시스템 호출, 페이지 복사, 무결성 트리 및 메타데이터 업데이트 등으로 약 40K 사이클 소요
- 페이징 오버헤드가 시스템을 평균 5배 느리게 하며, 메모리 집약적 워크로드에서는 더 큰 성능 저하 발생

## 방법론

### 3.1. VAULT 트리 구조

- **가변 아리티 통합 트리**: 기존 이진 트리보다 더 컴팩트하고 낮은 깊이
- 트리 깊이 감소 → 메모리 대역폭 오버헤드 최소화
- 캐시 친화적인 구조로 무결성 트리 캐시 효율성 향상
- 메모리 접근당 트리 탐색 비용 절감

### 3.2. MAC 공유 및 압축

- **MAC(Medium Access Control) 공유**: 여러 페이지가 동일한 MAC을 공유하여 저장 공간 절약
- **압축 기법**: 무결성 트리 및 MAC 데이터를 압축하여 공간 오버헤드 추가 절감
- 기존 SGX 대비 메모리 용량 오버헤드를 4.7%로 유지

### 3.3. EPC 확장 전략

- 비민감한 페이지도 EPC에 수용 가능하도록 확장
- 확장된 EPC에서의 효율적인 페이지 관리 메커니즘
- 페이징 빈도 감소를 통한 성능 향상

## 핵심 기여

- VAULT는 SGX의 페이징 오버헤드를 해결하기 위한 효율적인 무결성 검증 구조 제시
- VAULT 트리와 MAC 공유/압축 기법을 통해 기존 SGX 대비 3.7배 성능 향상
- 메모리 용량 오버헤드를 4.7%로 유지하면서 실용적인 보안 시스템 구현
- 클라우드 환경에서의 보안-성능 트레이드오프를 효과적으로 해결

## 주요 결과

- 시뮬레이션 기반 구현 및 평가
- SGX 하드웨어와의 호환성 확보
- 기존 SGX 소프트웨어 스택과의 통합

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/security.md|Security]]


## 전체 요약

[[../paper-summaries/2018ASPLOS-summarize/vault-reducing-paging-overheads-in-sgx-with-efficient-integrity-verification-structures.md|전체 요약 보기]]
