---
tags: [paper, 2018, 2018MICRO, topic/nvm, topic/security, topic/compression]
venue: "MICRO 2018"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/improving-the-performance-and-endurance-of-encrypted-non-volatile-main-memory-through-deduplicating-writes.md"
---

# Improving the Performance and Endurance of Encrypted Non-volatile Main Memory through Deduplicating Writes

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Pengfei Zuo, Yu Hua, Ming Zhao†, Wen Zhou, Yuncheng Guo (Huazhong University of Science and Technology; †Arizona State University)

## 개요

NVM(Non-Volatile Memory)은 차세대 메인 메모리 후보이나, 비휘발성으로 인한 데이터 잔류 취약성으로 메모리 암호화 필요. 그러나 암호화의 강한 확산 특성으로 인해 기존 비트 수준 쓰기 감소 기법이 무효화되고 쓰기 내구성 문제가 악화됨. 이 논문은 암호화된 NVM의 성능과 수명을 동시에 향상시키는 DeWrite 스킴을 제시.

## 방법론

### 경량 중복 제거
- **해싱 접근법:** 경량 해시 함수로 캐시 라인 지문 계산
- **NVM 읽기/쓰기 비대칭 활용:** 쓰기 지연 시간이 읽기 대비 3-8배이므로 중복 쓰기 제거가 성능 향상
- **인라인 중복 제거:** 쓰기 전에 중복 식별 및 제거

### 암호화와의 시너지
- **기회적 병렬화:** 중복 예측 기반으로 암호화와 중복 제거를 병렬 수행
- **메타데이터 공유 위치화:** 카운터와 해시를 널 위치에 임베딩하여 공간 오버헤드 6.25%로 감소
- **카운터 모드 암호화:** 읽기와 병렬 복호화로 지연 시간 숨김

## 핵심 기여

- 암호화된 NVM의 성능과 수명을 동시에 향상시키는 DeWrite 스킴 최초 제시
- 경량 인라인 중복 제거로 쓰기 54% 감소
- 암호화와의 시너지 통합으로 성능 대폭 향상
- 메타데이터 오버헤드 6.25%로 낮은 수준 유지

## 주요 결과

- 암호화된 NVM에 대한 쓰기 **평균 54% 감소**
- 메모리 쓰기 속도 **4.2배 향상**, 읽기 속도 **3.1배 향상**
- 시스템 IPC **82% 향상**
- 에너지 소비 **40% 감소**

## 한계점

- 중복 제거 효과가 워크로드에 따라 변동 (평균 58%, 최대 98%)
- 경량 해시의 거짓 양성 오버헤드 추가 분석 필요
- 실제 NVM 하드웨어에서의 검증 필요

## 관련 개념

- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/security.md|Security]]
- [[paper-wiki/concepts/compression.md|Compression]]

## 전체 요약

[[../paper-summaries/2018MICRO-summarize/improving-the-performance-and-endurance-of-encrypted-non-volatile-main-memory-through-deduplicating-writes.md|전체 요약 보기]]
