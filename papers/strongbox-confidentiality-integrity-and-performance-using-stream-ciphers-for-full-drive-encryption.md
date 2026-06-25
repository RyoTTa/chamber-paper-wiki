---
tags: [encryption, security, stream-ciphers, mobile, storage]
venue: ASPLOS
year: 2018
summary_path: paper-summaries/2018ASPLOS-summarize/strongbox-confidentiality-integrity-and-performance-using-stream-ciphers-for-full-drive-encryption.md
---

# StrongBox: Confidentiality, Integrity, and Performance using Stream Ciphers for Full Drive Encryption

## 개요

StrongBox는 모바일 기기에서 스트림 암호를 사용한 전체 드라이브 암호화(FDE)를 위한 시스템으로, 기존 AES-XTS 기반 dm-crypt보다 높은 성능과 강력한 무결성 보장을 제공합니다.

## 방법론

- **LFS(Log-structured File System) 특성 활용**: FTL이 데이터를 오버라이트하지 않아 many-time pad 공격 방어
- **신뢰할 수 있는 하드웨어 카운터**: TEE에 저장된 카운터로 rollback 공격 방어
- **dm-crypt 대체 가능**: 표준 Linux FDE 모듈의 드롭인 대체재

## 핵심 기여

- 모바일 하드웨어의 기술적 변화(LFS + TEE)를 활용한 스트림 암호 기반 FDE 실현
- 기존 AES-XTS보다 읽기 성능 평균 1.72배 향상
- 강화된 무결성 보장 제공

## 주요 결과

- 읽기 성능 최대 2.36배, 평균 1.72배 향상
- 쓰기 성능은 dm-crypt와 유사하거나 약간 우수
- 강화된 인증 암호화 제공
- 효과적인 롤백 공격 방어

## 한계점

- ARM big.LITTLE 프로세서에 특화된 구현
- 두 가지 조건(LFS + TEE)을 모두 충족해야 하는 제약

## 관련 개념

- [[paper-wiki/concepts/encryption|Encryption]]
- [[paper-wiki/concepts/security|Security]]
- [[paper-wiki/concepts/storage|Storage]]