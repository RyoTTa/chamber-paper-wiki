---
tags: [automata-processing, spatial-architecture, nfa, pattern-matching, sparseap]
venue: MICRO
year: 2018
summary_path: paper-summaries/2018MICRO-summarize/architectural-support-for-efficient-large-scale-automata-processing.md
---

# Architectural Support for Efficient Large-Scale Automata Processing (SparseAP)

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Hongyuan Liu, Mohamed Ibrahim, Onur Kayiran, Sreepathi Pai, Adwait Jog (College of William & Mary, Advanced Micro Devices Inc., University of Rochester)

---

## 개요

대규모 NFA(Non-deterministic Finite Automata) 기반 애플리케이션을 효율적으로 처리하기 위한 SparseAP 실행 모드를 제안. 프로파일링 기반 핫/콜드 상태 예측으로 AP에 구현하지 않아도 되는 상태를 식별하고, BaseAP/SpAP 이중 실행 모드로 처리 효율성 향상.

## 방법론

- **프로파일링 기반 핫/콜드 상태 예측:** 소량의 입력으로 NFA 상태의 활성화 빈도를 분석하여 핫/콜드 상태 분리
- **위상 순서 기반 NFA 파티셔닝:** 핫 상태만 AP에 배치, 콜드 상태는 AP 외부 처리
- **중간 보고 상태(Intermediate Reporting States):** AP에서 콜드 상태로의 전이를 위한 안전 장치
- **BaseAP 모드:** 핫 상태만 구현하여 실행, 콜드 상태 전이 시 중간 보고 생성
- **SpAP 모드:** 콜드 상태를 구현하여 중간 보고 기반으로 실행
- **점프(Jump) 연산:** SpAP 모드에서 불필요한 입력 심볼을 건너뛰어 시간 절약
- **활성화(Enable) 연산:** 중간 보고의 상태 ID로 해당 STE를 계층적 디코더를 통해 활성화

## 핵심 기여

- 대규모 NFA 애플리케이션을 위한 최초의 AP 아키텍처 지원
- 프로파일링 기반 핫/콜드 상태 예측으로 AP 리소스 효율적 활용
- BaseAP/SpAP 이중 실행 모드 + 점프 연산으로 콜드 상태 처리 오버헤드 최소화

## 주요 결과

- 26개 벤치마크에서 기준 AP 대비 기하평균 **2.1배**(최대 **47배**) 속도 향상
- 1% 프로파일링 입력으로 **2.2배**, 0.1%로 **1.9배** 속도 향상
- 재구성 횟수 대폭 감소 (예: CAV4k: 47회 → 1회)
- 다양한 AP 크기(12K~49K STE)에서 일관된 성능 향상

## 한계점

- 프로파일링 입력의代表性에 따라 예측 정확도가 달라질 수 있음
- 핫/콜드 상태 경계가 명확하지 않은 애플리케이션에서 이득이 제한
- 중간 보고 상태 추가로 총 상태 수가 증가하여 재구성 오버헤드 발생 가능
- enable stall이 동시 중간 보고 처리 시 성능에 영향

## 관련 개념

- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]

## 전체 요약

[architectural-support-for-efficient-large-scale-automata-processing.md](../../paper-summaries/2018MICRO-summarize/architectural-support-for-efficient-large-scale-automata-processing.md)
