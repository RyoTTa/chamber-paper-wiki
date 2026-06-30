---
tags: [paper, 2019, 2019MICRO, topic/cache, topic/compression]
venue: "MICRO 2019"
year: 2019
summary_path: "../paper-summaries/2019MICRO-summarize/touch-towards-ideal-and-efficient-cache-compression-by-mitigating-tag-area-overheads.md"
---

# Touché: Towards Ideal and Efficient Cache Compression By Mitigating Tag Area Overheads

**Venue:** MICRO 2019
**저자:** Seokin Hong (Kyungpook National University); Bulent Abali, Alper Buyuktosunoglu, Michael B. Healy (IBM T. J. Watson Research Center); Prashant J. Nair (The University of British Columbia)

## 개요

LLC(Last-Level Cache) 용량이 코어수 증가와 함께 정체되어 있으며, 데이터 압축은 유효 용량을 증가시키는 방안이지만 태그 영역 오버헤드가 핵심 병목이다. 기존 슈퍼블록 기법은 태그 오버헤드를 절감하지만 압축 블록 배치를 인접 주소로 제한한다.

Touché는 태그 영역 오버헤드 없이 임의 주소의 압축 블록을 캐시라인에 배치하는 LLC 압축 프레임워크로, 세 가지 핵심 구성요소(SIGN, TADA, SMARK)를 통해 이상적 압축에 근접한 성능을 달성한다.

## 방법론

### Signature (SIGN) 엔진
- 전체 태그 주소를 9비트 시그니처로 축약 → 하나의 태그 엔트리에 최대 3개 시그니처 저장
- 512 엔트리 해시 테이블로 충돌 최소화, 1사이클 지연
- 서명 충돌 확률: 최악의 경우 4.58% (8-way LLC)

### Tag Appended Data (TADA) 메커니즘
- 압축된 블록 옆에 전체 태그 주소(29비트)+메타데이터(5비트) = 34비트(4.25바이트) 추가
- 데이터 배열에 전체 태그를 저장하여 서명 충돌 시 정확한 태그 검증 보장
- 유효 캐시 용량 4.15% 포인트만 감소 (이상적 압축 대비)

### Superblock Marker (SMARK) 메커니즘
- 인접 주소의 슈퍼블록을 16비트 랜덤 마커로 표시
- 마커 충돌 확률: 0.012%로 극히 드묾
- 슈퍼블록과 임의 블록을 동시에 지원하여 히트레이트 추가 향상

## 핵심 기여

- 태그 영역 오버헤드 0%로 임의 주소 압축 블록 배치 가능
- 슈퍼블록과 임의 블록의 동시 지원으로 이상적 압축에 근접
- 하드웨어 기반 구현, LLC 컨트롤러 내부에만 변경

## 주요 결과

- 평균 **12%** 가속 (이상적 13%에 근접), 최대 **91%** 가속 (gcc)
- LLC 히트레이트: 평균 **6% 포인트** 증가
- 메모리 읽기 지연시간: 541→**489사이클** 감소
- 대체 정책 독립적: LRU 12%, DIP 14.5%, DRRIP 16.7% 가속
- 다양한 LLC 크기(2MB~8MB)에서 9~10% 가속 유지

## 한계점

- 서명 충돌로 인한 지연시간 오버헤드 0.26%
- 공유 LLC 가정; 프라이빗 LLC의 경우 코어 간 일관성 처리 필요

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/compression.md|Compression]]

## 전체 요약

[[../paper-summaries/2019MICRO-summarize/touch-towards-ideal-and-efficient-cache-compression-by-mitigating-tag-area-overheads.md|전체 요약 보기]]
