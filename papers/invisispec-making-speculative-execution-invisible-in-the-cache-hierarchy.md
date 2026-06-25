---
tags: [paper, 2018, 2018MICRO, topic/security, topic/cache, topic/speculation]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO), 2018"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/invisispec-making-speculative-execution-invisible-in-the-cache-hierarchy.md"
---

# InvisiSpec: Making Speculative Execution Invisible in the Cache Hierarchy

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Mengjia Yan, Jiho Choi, Dimitrios Skarlatos, Adam Morrison, Christopher W. Fletcher, Josep Torrellas (University of Illinois at Urbana-Champaign, Tel Aviv University)

## 개요

- 하드웨어 스페큘레이션은 마이크로아키텍처 은닉 및 사이드 채널 공격의 주요 표면을 제공
- Spectre 및 Meltdown 공격은 스페큘레이션 실행의 미시적 발자국을 모니터링하여 정보를 유출
- 기존 방어 기법(fence 기반)은 높은 오버헤드를 유발: TSO 환경에서 Spectre 방어 시 **74%** 실행 속도 저하
- InvisiSpec은 스페큘레이션을 데이터 캐시 계층에서 보이지 않게 만들어 공격을 방어하는 새로운 전략 제시

## 방법론

### 3.1. 스페큘레이션 버퍼

- 안전하지 않은 스페큘레이션 로드가 캐시 계층을 수정하지 않고 별도의 스페큘레이션 버퍼에 데이터를 저장
- 로드가 안전해지면 버퍼의 데이터를 캐시로 전달하거나 검증 후 삭제

### 3.2. 검증 메커니즘

- 스페큘레이션 로드가 메모리 일관성을 위반할 가능성이 있는지 식별
- 검증 단계에서 로드의 유효성을 확인하고, 유효하지 않은 경우 데이터를 폐기

### 3.3. 두 가지 설계 변형

- **IS-Sp:** Spectre 공격에 특화된 방어 (TSO 환경에서 평균 **22%** 실행 속도 저하)
- **IS-Fu:** 모든 스페큘레이션 로드가 위협이 될 수 있는 미래형 공격 방어 (TSO 환경에서 평균 **80%** 실행 속도 저하)

## 핵심 기여

- **핵심 기여:** 스페큘레이션을 데이터 캐시 계층에서 보이지 않게 만들어 보안을 달성하는 새로운 전략 제시
- **성능 향상:** 기존 fence 기법 대비 크게 낮은 오버헤드로 동등한 수준의 보안 달성
  - Spectre 방어: 74% → 22% 실행 속도 저하로 개선
  - 미래형 공격 방어: 208% → 80% 실행 속도 저하로 개선

## 주요 결과

- TSO 환경에서 Spectre 방어: Fence 기반 88% → InvisiSpec 22% 실행 시간 증가
- TSO 환경에서 미래형 공격 방어: Fence 기반 246% → InvisiSpec 80% 실행 시간 증가
- RC 환경에서: IS-Sp 15%, IS-Fu 55% 실행 시간 증가
- 검증 스타일은 대부분의 애플리케이션에서 미미하며, LLC 히트 시 빠르게 서비스됨

## 한계점

- 메모리 바운드 애플리케이션에서 검증 오버헤드가 가장 큼
- 캐시 상태 재사용 부족 및 이중 접근으로 인한 오버헤드 존재
- 다중처리기 환경에서의 확장성 추가 검증 필요

## 관련 개념

- [[paper-wiki/concepts/speculative-execution-security|Speculative Execution Security]]
- [[paper-wiki/concepts/cache-hierarchy|Cache Hierarchy]]
- [[paper-wiki/concepts/side-channel-attacks|Side Channel Attacks]]

## 관련 논문

- [invisispec-making-speculative-execution-invisible-in-the-cache-hierarchy.md](../paper-summaries/2018MICRO-summarize/invisispec-making-speculative-execution-invisible-in-the-cache-hierarchy.md)
