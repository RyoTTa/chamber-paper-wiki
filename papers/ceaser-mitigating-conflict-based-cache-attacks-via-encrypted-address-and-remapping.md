---
tags: [cache-security, side-channel, encryption, randomized-mapping]
venue: MICRO
year: 2018
summary_path: paper-summaries/2018MICRO-summarize/ceaser-mitigating-conflict-based-cache-attacks-via-encrypted-address-and-remapping.md
---

# CEASER: Mitigating Conflict-Based Cache Attacks via Encrypted-Address and Remapping

## 개요

- LLC의 conflict-based 캐시 기반 사이드 채널 공격을 암호화된 주소 공간과 동적 리매핑으로 완화
- CEASE(암호화된 주소 기반 캐시)와 CEASER(동적 리매핑 포함)의 두 단계 설계
- 100년 이상의 연속 공격 견딤, 1% 성능 오버헤드, 24바이트 미만 스토리지
- OS 지원 불필요, 완전히 하드웨어 기반 구현

## 방법론

- **CEASE:** LLBC(Low-Latency Block-Cipher)로 PLA→ELA 변환, 암호화의 avalanche effect로 라인 분산
- **CEASER:**
  - 에포크 기반 키 변경으로 매핑 주기적 리매핑
  - 점진적 리매핑 (Gradual-Remapping): SPtr와 ACtr로 캐시 라인을 에포크 기간에 걸쳐 점진적으로 리매핑
  - APLR=100으로 리매핑 오버헤드 1% 유지

## 핵심 기여

- 암호화된 주소 공간을 캐시 인덱싱에 활용하는 새로운 패러다임 제시
- 기존 테이블 기반 랜덤화의 비현실적 스토리지/OS 의존성 문제 해결
- Spectre/Meltdown 등 캐시 기반 공격에 대한 실용적 하드웨어 완화 방안

## 주요 결과

- **보안:** 100년 이상의 연속 공격 견딤
- **성능:** 평균 1% 미만 느림
- **스토리지:** 24바이트 미만 추가 구조체
- **OS 지원:** 불필요
- CEASE 대비 CEASER의 보안 강건성 크게 향상 (동적 리매핑 효과)

## 한계점

- LLBC의 2사이클 암호화 오버헤드가 캐시 접근 지연에 기여
- 은행 기반 LLC에서의 은행 간 레이턴시 차이 미고려
- 새로운 암호화 기술 발전에 따른 보안 재평가 필요

---

**관련 개념:** [[paper-wiki/concepts/security.md|Security]], [[paper-wiki/concepts/cache.md|Cache]]
