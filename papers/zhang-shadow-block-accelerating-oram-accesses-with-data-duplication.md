---
tags: [paper, oram, security, data-duplication, memory-access]
venue: MICRO 2018
year: 2018
summary_path: paper-summaries/2018MICRO-summarize/shadow-block-accelerating-oram-accesses-with-data-duplication.md
---

# Shadow Block: Accelerating ORAM Accesses with Data Duplication

## 개요

- ORAM 보안을 유지하면서 의도된 데이터 블록의 조기 접근을 가능하게 하는 Shadow Block 기법
- 더미 블록을 활용한 데이터 중복화(duplication) 방법
- RD-Dup(무작위 중복화)과 HD-Dup(핫 데이터 중복화)의 동적 결합

## 방법론

- **RD-Dup**: 무작위 위치의 더미 블록에 데이터 복사본 저장 (지역성 낮은 경우 효과적)
- **HD-Dup**: 핫 주소 캐시를 활용하여 핫 데이터 추적 및 가까운 위치에 복사본 저장 (지역성 높은 경우 효과적)
- **동적 분할**: DRI Counter(Data Request Interval Counter)를 이용한 자동 분할 레벨 조정
- **하드웨어**: Hot Address Cache, RD-queue, HD-queue, 분할 레벨 레지스터, DRI Counter

## 핵심 기여

- ORAM 보안을 유지하면서 접근 순서 변경 가능한 Shadow Block 기법 제안
- RD-Dup과 HD-Dup의 동적 결합으로 다양한 워크로드 대응
- 기존 ORAM 최적화 및 보안 기법과 호환

## 주요 결과

- 기본 ORAM 대비 유의미한 성능 향상
- RD-Dup과 HD-Dup의 결합이 단일 기법보다 우수한 성능
- 동적 분할이 정적 분할 대비 추가적인 성능 개선
- XOR 압축 기법보다 더 나은 성능 (DRAM 내부 대역폭 병목 해결)

## 한계점

- DRAM 내부 대역폭이 주요 병목이라는 가정
- 동적 분할의 오버헤드 (DRI Counter 업데이트)
- 모든 ORAM 변형에 적용 가능한지 추가 검증 필요

## 관련 개념

- [[paper-wiki/concepts/security.md|Security]]
- [[paper-wiki/concepts/dram.md|DRAM]]
