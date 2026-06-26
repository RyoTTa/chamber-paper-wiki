---
tags: [paper, 2018, 2018MICRO, topic/cache, topic/dram]
venue: "MICRO 2018 (51st Annual IEEE/ACM International Symposium on Microarchitecture)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/shadow-block-accelerating-oram-accesses-with-data-duplication.md"
---

# Shadow Block: Accelerating ORAM Accesses with Data Duplication

**Venue:** MICRO 2018 (51st Annual IEEE/ACM International Symposium on Microarchitecture)
**저자:** Xian Zhang (Peking University), Guangyu Sun (Peking University), Peichen Xie (Peking University), Chao Zhang (Peking University), Yannan Liu (Chinese University of Hong Kong), Lingxiao Wei (Chinese University of Hong Kong), Qiang Xu (Chinese University of Hong Kong), Chun Jason Xue (City University of Hong Kong)

## 개요

- Oblivious RAM (ORAM)은 메모리 접근 패턴을 숨기기 위한 암호화 프리미티브
- ORAM 접근 시 의도된 데이터 블록을 로드하고 다른 데이터 블록 및 더미 블록과 함께 내보내야 함
- 타이밍 패턴 보호를 위해 주기적으로 더미 ORAM 접근이 트리거됨
- 이러한 설계로 인해 막대한 메모리 접근 오버헤드 발생
- 기존 기법들은 총 ORAM 접근 수와 블록당 블록 수를 줄이는 데 초점을 맞추었으나, 의도된 데이터 블록의 접근 순서(access order)에 따른 성능 영향은 미해결
- 핵심 인사이트: ORAM 접근에서 의도된 데이터 블록에 대한 접근을 앞당기면 더 높은 성능 달성 가능

## 방법론

### 3.1. RD-Dup (Random Duplicate)

- 무작위 위치의 더미 블록에 데이터 블록의 복사본 저장
- LLC 미스 간격이 긴 경우(지역성 낮음)에 효과적
- 접근 순서 변경으로 ORAM 트리 내 블록 위치 변경

### 3.2. HD-Dup (Hot Duplicate)

- 핫 주소 캐시(Hot Address Cache)를 활용하여 핫 데이터 추적
- 접근 빈도가 높은 데이터의 복사본을 더 가까운 위치에 저장
- LLC 미스 간격이 짧은 경우(지역성 높음)에 효과적
- 핫 주소 캐시: 태그, 데이터, PA, 히트 카운터로 구성

### 3.3. 동적 분할 (Dynamic Partitioning)

- **DRI Counter (Data Request Interval Counter)**: 3비트 포화 카운터
  - 현재 요청이 더미 요청이고 이전이 실 요청이면 +1
  - 현재 요청이 실 요청이고 이전도 실 요청이면 -1
  - 카운터가 최대값의 절반 미만이면 분할 레벨 증가 (HD-Dup 우선)
  - 카운터가 최대값의 절반 이상이면 분할 레벨 감소 (RD-Dup 우선)
- LLC 미스 간격의 주기적 변동을 활용한 동적 적응

### 3.4. 하드웨어 구조 (Fig. 7)

- **ORAM 컨트롤러 구성요소**:
  - Hot Address Cache: 핫 데이터 접근 카운터 저장
  - RD-queue: RD-Dup용 대기열
  - HD-queue: HD-Dup용 대기열
  - 분할 레벨 레지스터: 현재 분할 수준 저장
  - DRI Counter 레지스터: 데이터 요청 간격 카운터
- **블록 구조**: PA, 라벨, DH(Shadow bit), 데이터, 주소, 그림자 비트 포함
- **Stash 수정**: 그림자 블록도 대체 가능 블록으로 표시, 동일 프로그램 주소의 블록 병합 지원

## 핵심 기여

- Shadow Block은 더미 블록을 활용하여 ORAM 보안을 유지하면서 의도된 데이터 블록의 조기 접근을 가능하게 함
- RD-Dup과 HD-Dup의 동적 결합이 다양한 워크로드에서 최적의 성능 제공
- 기존 ORAM 최적화 및 보안 기법과 호환되어 실용적인 성능 향상 가능
- ORAM 성능 병목을 해결하기 위한 새로운 접근법으로, 메모리 대역폭이 아닌 DRAM 내부 대역폭에 초점

## 주요 결과

| 항목 | 세부사항 |
|------|---------|
| **구현 위치** | ORAM 컨트롤러 |
| **하드웨어 추가** | Hot Address Cache, RD-queue, HD-queue, 분할 레벨 레지스터, DRI Counter |
| **보안** | ORAM 보안 유지 (동적 분할도 기존 기법과 동일한 보안 수준) |
| **호환성** | 대부분의 ORAM 최적화와 호환 (super block prefetching, PosMap Lookup Table, treetop caching, fork path 등) |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/shadow-block-accelerating-oram-accesses-with-data-duplication.md|전체 요약 보기]]
