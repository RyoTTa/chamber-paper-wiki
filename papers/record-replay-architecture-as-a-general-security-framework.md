---
tags: [paper, 2018, 2018HPCA, topic/dram, topic/security]
venue: "HPCA '18 (IEEE International Symposium on High Performance Computer Architecture), 2018"
year: 2018
summary_path: "../paper-summaries/2018HPCA-summarize/record-replay-architecture-as-a-general-security-framework.md"
---

# Record-Replay Architecture as a General Security Framework

**Venue:** HPCA '18 (IEEE International Symposium on High Performance Computer Architecture), 2018
**저자:** Yasser Shalabi, Mengjia Yan, Nima Honarmand, Ruby B. Lee, Josep Torrellas (University of Illinois at Urbana-Champaign, Stony Brook University, Princeton University)

## 개요

- 하드웨어 보안 기능은 설계 침입성과 방법의 완성도 사이에서 신중한 균형을 유지해야 함
- 보안 위협이 지속적으로 진화하므로 하드웨어 보안 기능은 유연해야 함
- 기존 하드웨어 보안 기능의 한계: 높은 정확도를 요구하는 비용 효율성 문제
- 보안 공격의 다양화와 진화에 대응하기 위한 새로운 보안 프레임워크의 필요성
- 특히 Return Oriented Programming (ROP) 공격과 같은 코드 재사용 공격에 대한 효과적인 방어 기법 부재

## 방법론

### 3.1. Checkpoint Replayer (항상 켜져 있는 빠른 재생기)
- 주기적으로 체크포인트를 생성하는 항상 작동하는 재생기
- 기록된 실행과 유사한 실행 속도 달성
- 시스템 오버헤드 최소화를 위한 최적화된 설계

### 3.2. Alarm Replayer (상세 분석 재생기)
- 위협 알람이 발생할 때 트리거되는 상세 분석 재생기
- 거짓 양성(false positive)을 투명하게 검증
- 실제 공격과 거짓 양성을 정확하게 구분

### 3.3. Return Address Stack (RAS) 확장
- ROP 공격 방지를 위한 RAS 하드웨어 확장
- 상대적으로 저렴한 하드웨어 추가를 통한 보안 강화
- 가상 머신 환경에서의 효과적인 보안 메커니즘 구현

## 핵심 기여

- RnR-Safe는 하드웨어 보안 기능을 보완하기 위한 새로운 프레임워크 제안
- 기록 및 결정론적 재생을 통한 효율적이고 유연한 보안 메커니즘 구현
- ROP 공격과 같은 코드 재사용 공격에 대한 효과적인 방어 제공
- 보안 하드웨어의 비용을 줄이면서도 높은 보안 수준 달성

---

**References:** [paper-summaries/2018HPCA-summarize/record-replay-architecture-as-a-general-security-framework.md]

## 주요 결과

- RAS 하드웨어 확장 및 하이퍼바이저 변경
- 가상 머신 환경에서의 리눅스 시스템 지원
- 기존 프로세서 아키텍처와의 호환성 유지

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/security.md|Security]]


## 전체 요약

[[../paper-summaries/2018HPCA-summarize/record-replay-architecture-as-a-general-security-framework.md|전체 요약 보기]]
