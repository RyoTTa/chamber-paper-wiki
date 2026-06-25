---
tags: [security, record-replay, hardware-security, rop, virtualization]
venue: HPCA
year: 2018
summary_path: paper-summaries/2018HPCA-summarize/record-replay-architecture-as-a-general-security-framework.md
---

# Record-Replay Architecture as a General Security Framework

## 개요

Record-Replay Architecture는 하드웨어 보안 기능을 보완하기 위한 새로운 프레임워크를 제안합니다. Record and Deterministic Replay (RnR)를 활용하여 보안 하드웨어의 비용을 줄이면서도 높은 보안 수준을 달성하는 접근법을 제시합니다.

## 방법론

- **Checkpoint Replayer**: 주기적으로 체크포인트를 생성하는 항상 작동하는 재생기
- **Alarm Replayer**: 위협 알람이 발생할 때 트리거되는 상세 분석 재생기
- **Return Address Stack (RAS) 확장**: ROP 공격 방지를 위한 하드웨어 확장

## 핵심 기여

1. RnR을 하드웨어 보안 기능을 보완하는 데 사용하는 새로운 프레임워크 제안
2. 보안 하드웨어의 비용을 줄이면서도 높은 보안 수준 달성
3. ROP 공격과 같은 코드 재사용 공격에 대한 효과적인 방어 제공

## 주요 결과

- RnR-Safe는 매우 효과적인 보안 성능 발휘
- 체크포인트 재생기는 기록된 실행과 유사한 실행 속도 달성
- 알람 재생기는 매우 적은 수의 거짓 양성을 처리

## 한계점

- 하드웨어 확장이 필요하며, 기존 프로세서 아키텍처와의 호환성 문제 가능성
- 특정 보안 공격(ROP)에 초점이 맞춰져 있어 다른 유형의 공격에는 효과적이지 않을 수 있음
- 가상 머신 환경에서의 평가에 한정되어 있어 일반적인 시스템에서의 효과 미확인

---

**Related Concepts:**
- [[paper-wiki/concepts/security|Security]]
- [[paper-wiki/concepts/hardware-security|Hardware Security]]
- [[paper-wiki/concepts/virtualization|Virtualization]]

**Related Papers:**
- [paper-summaries/2018HPCA-summarize/record-replay-architecture-as-a-general-security-framework.md]