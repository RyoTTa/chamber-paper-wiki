---
tags: [nvm, security, restoration, non-volatile-memory, encryption]
venue: MICRO
year: 2018
summary_path: paper-summaries/2018MICRO-summarize/osiris-a-low-cost-mechanism-to-enable-restoration-of-secure-non-volatile-memories.md
---

# Osiris: A Low-Cost Mechanism to Enable Restoration of Secure Non-Volatile Memories

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** NOTA 논문 정보에서 확인 필요

---

## 개요

보안 비휘발성 메모리(Secure NVM)의 저비용 복원 메커니즘 Osiris를 제안. 기존 보안 NVM의 복원 과정에서 발생하는 높은 오버헤드를 해결하기 위해 체크포인트 기반 복원 및 점진적 복원 기법을 제시.

## 방법론

- **체크포인트 기반 복원:** 주기적으로 보안 상태 체크포인트 저장으로 빠른 복구
- **점진적 복원 (Incremental Restoration):** 접근 순서에 따라 부분적으로 복원하여 콜드 부팅 시간 단축
- **하드웨어 지원:** 메모리 컨트롤러에 복원 로직, 체크포인트 저장/복원용 레지스터, 암복호화 엔진 통합
- **보안 보장:** 복원 과정에서도 기밀성, 무결성 유지

## 핵심 기여

- 보안 NVM의 저비용 복원 메커니즘 최초 제안
- 점진적 복원을 통한 빠른 시스템 시작 시간 달성
- 기존 보안 메커니즘과의 호환성 확보

## 주요 결과

- 기존 보안 NVM 대비 복원 시간 대폭 단축
- 낮은 하드웨어 오버헤드 (면적, 전력)
- 높은 보안 수준 유지 (기밀성, 무결성)

## 한계점

- 체크포인트 저장을 위한 추가 메모리 영역 필요
- 특정 NVM 기술에 최적화 가능
- 복원 과정에서의 부가적 에너지 소비

## 관련 개념

- [[paper-wiki/concepts/non-volatile-memory.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/security.md|Security]]

## 전체 요약

[paper-summaries/2018MICRO-summarize/osiris-a-low-cost-mechanism-to-enable-restoration-of-secure-non-volatile-memories.md](paper-summaries/2018MICRO-summarize/osiris-a-low-cost-mechanism-to-enable-restoration-of-secure-non-volatile-memories.md)