---
tags: [paper, 2018, 2018ISCA]
venue: "45th Annual International Symposium on Computer Architecture (ISCA '18)"
year: 2018
summary_path: "../paper-summaries/2018ISCA-summarize/hiding-intermittent-information-leakage-with-architectural-support-for-blinking.md"
---

# Hiding Intermittent Information Leakage with Architectural Support for Blinking

**Venue:** 45th Annual International Symposium on Computer Architecture (ISCA '18)
**저자:** Alric Althoff (UC San Diego), Joseph McMahan (UC Santa Barbara), Luis Vega (UC Washington), Scott Davidson (UC Washington), Timothy Sherwood (UC Santa Barbara), Michael B. Taylor (UC Washington), Ryan Kastner (UC San Diego)

## 개요

- 전력 분석 공격(DPA 등)은 암호화 시스템의SECRET 키를 전력 소비 패턴으로 추출하는 강력한 공격 기법
- 공격자는 무제한 수의 전력 트레이스를 수집하여 노이즈를 극복
- 기존 방어 기법의 한계:
  - **마스킹(Masking)**: 모든 연산에 노이즈 추가 → 면적/전력 오버헤드 큼
  - **Dual-rail 로직**: 신호 독립적 전력 소비 → 라우팅 제약, 면적 2배
  - **하드웨어 기반 대책**: 특정 암호화 유닛에만 적용 가능, 일반화 어려움
- 핵심 관찰: **정보 유출은 시간에 따라 균일하지 않음** — 특정 시간 간격에서 대부분의 유출 발생
  - TVLA(Test Vector Leakage Assessment) 분석: AES 실행 시 특정 시간 포인트에서 −log(p-values)가 극적으로 변화
  - 대부분의 시간 구간은 거의 유출이 없으나, 특정 구간에서 정보 대량 유출

## 방법론

### 3.1. 비균일 정보 유출 분석
- TVLA 분석으로 시간별 정보 유출량 측정
- −log(p-values) > 11.51 구간이 취약 구간 (p < 0.00001)
- 대부분의 시간에서 유출이 거의 없으나, 특정 포인트에서 대량 유출 → **선택적 보호 가능**

### 3.2. Blink 메커니즘
- **3단계 순차 실행**:
  1. **Blink Computing**: on-chip 에너지 저장장치를 사용하여 격리된 환경에서 연산 수행
  2. **Discharge (발산)**: 고정된 시간 동안 에너지 저장장치를 완전히 방전 → 이전 연산의 잔여 정보 제거
  3. **Recharge (충전)**: 고정된 시간 동안 에너지 저장장치를 다시 충전
- **고정 시간 보장**: discharge/recharge 시간은 고정되어 정보가 누출되지 않도록 보장
- **소프트웨어 제어**: ISA에 새로운 명령어 추가로 blink 연산을 프로그래밍 가능

### 3.3. 유출 구간 커버리지 최적화
- **집합 커버 문제(Set Cover)**: 유출이 가장 큰 시간 구간들을 선택하여 최소 비용으로 커버링
- **알고리즘**: 각 시간 구간의 정보 유출량과 해당 구간을 보호하는 비용(성능/에너지)을 정량화
- **트레이드오프 곡선**: 보호 비율(15~30%)에 따른 성능 오버헤드(15~50%)와 mutual information 감소(75% 이상) 제공

### 3.4. 아키텍처 영향
- **ISA 확장**: blink 명령어 추가 → 소프트웨어에서 보안 핵심 구간을 지정
- **에너지 관리**: on-chip 커패시터/배터리로 격리된 연산 중 전력 공급
- **메모리 격리**: 분리된 구간에서의 메모리 접근도 격리
- **다중 보호 수준**: 완전 보호(2.7× 느림) ~ 절반 보호(12% 느림)까지 선택 가능

## 핵심 기여

- **핵심 기여**: 정보 유출의 시간적 비균일성을 활용한 최초의 소프트웨어 제어형 전력 채널 방어 아키텍처
- **실용성**: 일반 프로세서에 blink 명령어를 추가하여 기존 소프트웨어와 호환 가능
- **보안 효과**: 15~30% 구간 보호로 75% 이상의 정보 유출 차단
- **의의**: 하드웨어-소프트웨어 협력을 통한 전력 분석 공격 방어의 새로운 패러다임 — 완전 보호와 제한된 보호 사이에서 정량적 선택 가능

## 주요 결과

- **하드웨어**: AVR 마이크로컨트롤러 (SimAVR 시뮬레이터 + 실제 하드웨어 측정)
- **소프트웨어**: C 언어, AES 구현 기반
- **시뮬레이터**: SimAVR (오픈소스 AVR 시뮬레이터)
- **전력 측정**: 실제 AVR 보드에서 전력 트레이스 수집
- **분석 도구**: TVLA 분석, mutual information 측정

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- 개념 매칭 없음

## 전체 요약

[[../paper-summaries/2018ISCA-summarize/hiding-intermittent-information-leakage-with-architectural-support-for-blinking.md|전체 요약 보기]]
