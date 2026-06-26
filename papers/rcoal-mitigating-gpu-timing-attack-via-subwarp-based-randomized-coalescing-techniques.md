---
tags: [paper, 2018, 2018HPCA, topic/gpu]
venue: "HPCA '18 (IEEE International Symposium on High Performance Computer Architecture), 2018"
year: 2018
summary_path: "../paper-summaries/2018HPCA-summarize/rcoal-mitigating-gpu-timing-attack-via-subwarp-based-randomized-coalescing-techniques.md"
---

# RCoal: Mitigating GPU Timing Attack via Subwarp-based Randomized Coalescing Techniques

**Venue:** HPCA '18 (IEEE International Symposium on High Performance Computer Architecture), 2018
**저자:** Gurunath Kadam (College of William and Mary), Danfeng Zhang (Penn State University), Adwait Jog (College of William and Mary)

## 개요

- GPU는 HPC, 딥러닝, VR/AR 등 다양한 영역에서 기본 가속기로 사용됨
- GPU는 보안 민감한 애플리케이션(암호화 등)에서도 높은 성능 향상 제공
- GPU의 메모리 대역폭 최적화를 위한 핵심 기능인 intra-warp 메모리 접근 코얼레싱(coalescing)
- 코얼레싱은 단일 warp의 다른 스레드에서 발생하는 메모리 요청을 최소한의 캐시 라인으로 병합
- 그러나 이 코얼레싱 기능이 GPUs를 상관 관계 타이밍 공격에 취약하게 만들 수 있음
- 공격자가 암호화된 데이터와 실행 시간을 반복적으로 수집하여 AES 개인 키를 정확히 노출 가능
- GPU에서 보안 민감한 애플리케이션 가속 시 보안 취약성 문제의 심각성

## 방법론

### 3.1. Fixed-Sized Subwarp (FSS)
- 고정된 크기의 서브워프를 사용한 코얼레싱 무작위화
- 서브워프 크기를 고정하여 일관된 보안 수준 제공
- 구현 복잡도가 낮고 성능 오버헤드가 적음

### 3.2. Random-Sized Subwarp (RSS)
- 가변적인 크기의 서브워프를 사용한 코얼레싱 무작위화
- 서브워프 크기를 무작위로 변경하여 공격자의 예측 가능성 감소
- 더 높은 보안 수준 제공 가능

### 3.3. Random-Threaded Subwarp (RTS)
- 각 서브워프 내에서 코얼레싱될 스레드를 무작위로 선택
- 스레드 선택의 무작위화를 통한 보안 강화
- 가장 높은 수준의 보안 제공

### 3.4. 통합 방어 전략
- FSS, RSS, RTS의 조합을 통한 다층 방어 구현
- 보안 수준과 성능 트레이드오프의 최적화
- 상황에 따른 적응적인 방어 전략 적용 가능

## 핵심 기여

- RCoal은 GPU 타이밍 공격을 완화하기 위한 효과적인 방어 메커니즘 제공
- 코얼레싱 로직의 무작위화를 통한 보안 강화 가능
- 성능 트레이드오프를 수용하여 실용적인 보안 수준 달성
- GPU 기반 보안 민감한 애플리케이션의 안전한 가속화에 기여

---

**References:** [paper-summaries/2018HPCA-summarize/rcoal-mitigating-gpu-timing-attack-via-subwarp-based-randomized-coalescing-techniques.md]

## 주요 결과

- GPU 하드웨어 수준에서의 코얼레싱 로직 수정
- 기존 GPU 아키텍처와의 호환성 유지
- 추가 하드웨어 오버헤드 최소화

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/gpu.md|GPU]]


## 전체 요약

[[../paper-summaries/2018HPCA-summarize/rcoal-mitigating-gpu-timing-attack-via-subwarp-based-randomized-coalescing-techniques.md|전체 요약 보기]]
