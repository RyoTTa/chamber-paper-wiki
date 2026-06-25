---
tags: [paper, 2018, 2018MICRO, topic/compression, topic/dram]
venue: "MICRO 2018"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/compresso-pragmatic-main-memory-compression.md"
---

# Compresso: Pragmatic Main Memory Compression

**Venue:** MICRO 2018
**저자:** Esha Choukse, Mattan Erez, Alaa R. Alameldeen (University of Texas at Austin, Intel Labs)

## 개요

하드웨어 메모리 압축은 시스템 비용 증가 없이 성능과 에너지 효율을 향상시키는 유망한 방향이지만, 두 가지 주요 과제에 직면한다: (1) 압축된 데이터 관리 시 평균 63%의 추가 메모리 접근 발생, (2) OS 수정 필요성으로 인한 배포 지연.

Compresso는 데이터 이동 관련 새로운 트레이드오프를 식별하고 최적화하여, OS 수정 없이 하드웨어 메모리 압축을 구현한 최초의 아키텍처이다. 평균 1.85× 압축률을 달성하며, 기존 최첨단 압축 기법(LCP) 대비 단일 코어 24%, 4코어 27% 성능 향상을 보인다.

## 방법론

### 압축 알고리즘
- **BPC (Bit-Plane Compression)** 채택: Delta-Bitplane-Xor 변환으로 높은 압축률
- CPU용으로 granularity를 128B→64B로 축소
- BPC 변환 없이 압축하는 병렬 경로 추가로 평균 13% 추가 절약

### 데이터 이동 최적화
1. **정렬 친화적 캐시라인 크기**: 0/8/32/64B → split-access 30.9%→3.2%
2. **페이지 오버플로 예측**: 2비트 포화 카운터 + 3비트 글로벌 예측기
3. **동적 인플레이션 룸 확장**: 추가 512B 청크 할당으로 재압축 대신 1회 쓰기
4. **동적 페이지 리패킹**: 메타데이터 캐시 퇴출 시 트리거, 압축률 손실 24%→2.6%
5. **메타데이터 캐시 최적화**: 비압축 페이지 메타데이터 절반 크기 저장으로 캐시 용량 2×

### OS-투명성
- 수정되지 않은 Linux/Windows/macOS에서 동작
- 페이지 오버플로 처리: 하드웨어 내부 처리
- 메모리 부족 시: Linux memory ballooning 기능 활용

## 핵심 기여

1. 압축 공격성과 데이터 이동 오버헤드 사이의 새로운 트레이드오프 식별
2. OS 수정 없이 하드웨어 메모리 압축을 구현한 최초의 아키텍처
3. 데이터 이동을 63%→15%로 감소시키는 5가지 최적화 기법
4. 메모리 용량 영향을 고려한 홀리스틱 평가 방법론 제안

## 주요 결과

- **압축률**: 평균 1.85×
- **단일 코어**: 메모리 제한 시 1.29× speedup (LCP 1.11× 대비 16% 향상)
- **4코어**: 메모리 제한 시 2.33× relative performance (LCP 1.97× 대비 18% 향상)
- **전체 성능**: 단일 코어 24%, 4코어 27% LCP 대비 향상
- **데이터 이동**: 63% → 15%로 감소
- **에너지**: 압축 미사용 대비 DRAM 에너지 11% 절감, LCP 대비 60% 더 많은 절약
- **OS 투명성**: 수정되지 않은 OS에서 동작

## 한계점

- 메타데이터 캐시 미스가 높은 워크로드(omnetpp, Forestfire 등)에서 성능 저하 가능
- 비압축 워크로드(mcf, GemsFDTD 등)에서는 압축 이점 없음
- BPC 압축기/해제기 하드웨어 오버헤드 존재 (7mW, 43Kμm²)

## 관련 개념

- [[paper-wiki/concepts/compression.md|Compression]]: 메모리 압축의 데이터 이동 문제를 해결하는 접근
- [[paper-wiki/concepts/dram.md|DRAM]]: OS-투명 메모리 압축을 위한 메모리 컨트롤러 확장

## 관련 논문 요약

- [paper-summaries/2018MICRO-summarize/compresso-pragmatic-main-memory-compression.md]
