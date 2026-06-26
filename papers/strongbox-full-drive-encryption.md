---
tags: [paper, 2018, 2018ASPLOS, topic/security, topic/storage]
venue: "ASPLOS 2018 (Architectural Support for Programming Languages and Operating Systems)"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/strongbox-confidentiality-integrity-and-performance-using-stream-ciphers-for-full-drive-encryption.md"
---

# StrongBox: Confidentiality, Integrity, and Performance using Stream Ciphers for Full Drive Encryption

**Venue:** ASPLOS 2018 (Architectural Support for Programming Languages and Operating Systems)
**저자:** Bernard Dickens III, Haryadi S. Gunawi, Ariel J. Feldman, Henry Hofmann (University of Chicago)

## 개요

- 전체 드라이브 암호화(FDE: Full Drive Encryption)는 모바일 기기에서 민감한 데이터 보호를 위해 필수적이지만, 표준 방식인 AES-XTS 블록 암호는 암호화되지 않은 저장소보다 3~5배 느림
- 스트림 암호(예: ChaCha20) 기반 인증 암호화는 다른 컨텍스트(예: HTTPS)에서는 AES보다 빠르지만, FDE에서는 기밀성과 성능 문제로 사용되지 않음
- 스트림 암호를 FDE에 단순 적용하면 many-time pad 공격 및 rollback 공격에 취약하며, 이러한 공격을 방어하기 위한 온드라이브 메타데이터가 성능을 크게 저하시킨다는 기존 관념 존재
- 모바일 하드웨어의 두 가지 기술적 변화가 이 관념을 무효화: (1) Flash Translation Layer(FTL)를 사용하는 솔리드 스테이트 스토리지, (2) 신뢰할 수 있는 하드웨어(TEE, 보안 저장 영역)

## 방법론

### 3.1. 시스템 아키텍처

- StrongBox는 블록 장치 계층에서 동작하는 소프트웨어 모듈
- 암호화되지 않은 블록 I/O 요청을 받아 스트림 암호로 암호화/복호화 후 스토리지에 기록
- dm-crypt와 동일한 인터페이스를 제공하여 기존 시스템과 호환

### 3.2. 온드라이브 데이터 구조

- **Nonce 구조**: 각 블록에 고유한 nonce(논스)를 할당하여 many-time pad 공격 방어
- **LFS의 쓰기 패턴 활용**: LFS는 데이터를 오버라이트하지 않으므로, 동일한 블록에 여러 번 쓰는 상황이 발생하지 않음 → nonce 재사용 문제 해결
- **카운터 기반 무결성 보호**: 블록별 카운터를 사용하여 롤백 공격 탐지

### 3.3. 신뢰할 수 있는 하드웨어 통합

- ARM TrustZone과 같은 TEE를 사용하여 카운터 값을 안전하게 저장
- 드라이브 자체에는 암호화된 데이터만 저장되고, 무결성 검증에 필요한 메타데이터는 TEE에 보관
- 하드웨어 카운터가 rollback 공격을 탐지하면 시스템이 복구 조치 수행

## 핵심 기여

- StrongBox는 모바일 하드웨어의 기술적 변화(LFS + TEE)를 활용하여 스트림 암호 기반 FDE를 실현
- 기존 AES-XTS 기반 dm-crypt보다 읽기 성능을 평균 1.72배 향상하면서 더 강력한 무결성 보장 제공
- 모바일 기기의 전체 드라이브 암호화에 실용적인 대안 제시
- 하드웨어와 소프트웨어의 공동 설계를 통한 보안-성능 트레이드오프 극복의 사례

## 주요 결과

- ARM big.LITTLE 모바일 프로세서에서 구현
- Linux 커널 모듈로 구현하여 기존 스토리지 스택과 통합
- ChaCha20 스트림 암호 사용
- Poly1305 메시지 인증 코드(MAC) 사용하여 인증 암호화 구현

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/security.md|Security]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2018ASPLOS-summarize/strongbox-confidentiality-integrity-and-performance-using-stream-ciphers-for-full-drive-encryption.md|전체 요약 보기]]
