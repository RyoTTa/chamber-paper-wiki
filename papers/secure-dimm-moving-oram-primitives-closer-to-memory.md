---
tags: [oram, security, memory-systems, privacy]
venue: HPCA
year: 2018
summary_path: paper-summaries/2018HPCA-summarize/secure-dimm-moving-oram-primitives-closer-to-memory.md
---

# Secure DIMM: Moving ORAM Primitives Closer to Memory

## 개요

Secure DIMM(SDIMM)은 ORAM 기능의 일부를 메모리 시스템으로 이동하여 성능 및 에너지 효율성을 크게 향상시키는 시스템입니다.

## 방법론

- SDIMM 설계: 상용 저비용 메모리와 ASIC을 안전 버퍼 칩으로 사용
- Independent ORAM: 각 SDIMM이 ORAM 트리의 일부를 담당
- Split ORAM: ORAM 트리를 SDIMM 간에 분할

## 핵심 기여

1. ORAM 기능을 메모리 시스템으로 이동하여 성능 및 에너지 효율성 향상
2. 상용 하드웨어 활용으로 실용적 적용 가능성 입증
3. Path ORAM과 동일한 무시성(obliviousness) 보장
4. 클라우드 환경에서의 프라이버시 보장에 대한 중요 발전

## 주요 결과

- Independent ORAM과 Split ORAM은 Freecursive ORAM 대비:
  - 성능: 1.9배 향상
  - 에너지: 2.55배 향상
- 메인 메모리 채널의 대역폭 사용량 크게 감소
- 높은 수준의 병렬 ORAM 작업 달성

## 한계점

- 안전 버퍼 칩의 추가 비용
- 특정 DIMM 구성에 대한 의존성
- 다양한 워크로드에서의 성능 변동

## 관련 concept 페이지

- [[paper-wiki/concepts/oram|ORAM]]
- [[paper-wiki/concepts/security|Security]]
- [[paper-wiki/concepts/privacy|Privacy]]

## 관련 논문 요약

- [paper-summaries/2018HPCA-summarize/secure-dimm-moving-oram-primitives-closer-to-memory.md]