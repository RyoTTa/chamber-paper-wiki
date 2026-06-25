---
tags: [gpu, security, timing-attack, coalescing, side-channel]
venue: HPCA
year: 2018
summary_path: paper-summaries/2018HPCA-summarize/rcoal-mitigating-gpu-timing-attack-via-subwarp-based-randomized-coalescing-techniques.md
---

# RCoal: Mitigating GPU Timing Attack via Subwarp-based Randomized Coalescing Techniques

## 개요

RCoal은 GPU의 타이밍 공격을 완화하기 위한 방어 메커니즘을 제안하는 논문입니다. GPU의 코얼레싱 기능이 타이밍 공격에 취약하게 만드는 문제를 해결하기 위해 코얼레싱 로직을 무작위화하는 기법을 제안합니다.

## 방법론

- **Fixed-Sized Subwarp (FSS)**: 고정된 크기의 서브워프를 사용한 코얼레싱 무작위화
- **Random-Sized Subwarp (RSS)**: 가변적인 크기의 서브워프를 사용한 코얼레싱 무작위화
- **Random-Threaded Subwarp (RTS)**: 각 서브워프 내에서 코얼레싱될 스레드를 무작위로 선택

## 핵심 기여

1. GPU 타이밍 공격을 완화하기 위한 효과적인 방어 메커니즘 제안
2. 코얼레싱 로직의 무작위화를 통한 보안 강화 가능
3. 성능 트레이드오프를 수용하여 실용적인 보안 수준 달성

## 주요 결과

- FSS, RSS, RTS의 조합은 상관 관계 타이밍 공격에 대한 보안을 24배에서 961배까지 향상
- 성능 저하는 5%에서 28% 수준으로 관리 가능
- 보안과 성능 간의 효과적인 트레이드오프 달성

## 한계점

- 성능 오버헤드가 상당할 수 있음 (최대 28%)
- 특정 공격 시나리오에만 효과적일 수 있음
- 추가적인 하드웨어 지원이 필요할 수 있음

---

**Related Concepts:**
- [[paper-wiki/concepts/gpu|GPU Architecture]]
- [[paper-wiki/concepts/security|Security]]
- [[paper-wiki/concepts/side-channel|Side-Channel Attacks]]

**Related Papers:**
- [paper-summaries/2018HPCA-summarize/rcoal-mitigating-gpu-timing-attack-via-subwarp-based-randomized-coalescing-techniques.md]