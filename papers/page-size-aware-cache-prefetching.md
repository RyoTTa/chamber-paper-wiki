---
tags: [paper, 2022, 2022MICRO, topic/cache, topic/security, topic/virtual-memory]
venue: "MICRO 2022 (55th IEEE/ACM International Symposium on Microarchitecture)"
year: 2022
summary_path: "../paper-summaries/2022MICRO-summarize/page-size-aware-cache-prefetching.md"
---

# Page Size Aware Cache Prefetching

**Venue:** MICRO 2022 (55th IEEE/ACM International Symposium on Microarchitecture)
**저자:** Georgios Vavouliotis (BSC/UPC), Paul V. Gratz (Texas A&M), Gino Chacon (Texas A&M), Daniel A. Jimenez (Texas A&M), Lluc Alvarez (BSC/UPC), Marc Casas (BSC/UPC)

## 개요

- 현대 응용 프로그램의 워크셋 크기 증가가 캐시 용량 증가를 앞서며, 프로세서-메모리 속도 격차(Memory Wall)로 인한 성능 병목이 지속
- 현대 시스템은 주소 변환 오버헤드 완화를 위해 2MB/1GB 대형 페이지(large page)를 널리 사용하지만, 물리 주소 공간에서 동작하는 캐시 프리페처는 4KB 물리 페이지 경계를 넘어서는 프리페칭을 허용하지 않음
- 4KB 물리 페이지 경계 제한으로 인해 프리페처가 안전하게 탐지할 수 있는 패턴이 제한되어 성능 잠재력이 축소 (Fig. 1)
- 대형 페이지 사용 시 4KB 경계를 넘는 프리페칭이 기술적으로 가능하나, 현재까지 이를 활용하는 마이크로아키텍처적 기법이 없음 (Finding 1)

## 방법론

### 3.1. PPM 동작 원리

- 1차 캐시(L1D/L1I) miss 발생 시, 주소 변환 메타데이터에서 페이지 크기 비트 추출
- 추출된 페이지 크기 정보를 MSHR 엔트리에 추가 1비트로 하위 레벨 캐시(L2C/LLC) 프리페처에 전달
- 프리페처는 페이지 크기 정보를 이용하여 2MB 페이지 거주 블록에 대해 4KB 경계 초과 프리페칭 결정
- **오버헤드:** MSHR당 1비트 추가뿐, 프리페처 설계 변경 불필요

### 3.2. 안전한 4KB 경계 초과 프리페칭

- 2MB 페이지 거주 블록: 물리적 연속성이 보장되므로 4KB 경계를 넘는 프리페칭이 안전
- 4KB 페이지 거주 블록: 기존처럼 4KB 경계에서 프리페칭 중단 (물리 주소 연속성 불 보장)
- 보안 측면: side-channel 공격 가능성 없음 (대형 페이지 내에서만 경계 초과 허용)

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1. Pref-PSA (기본 구조)

- 하위 레벨 캐시 프리페처(SPP, VLDP, PPF, BOP 등)를 PPM과 결합
- 프리페처 자체의 설계 변경 없이 페이지 크기 정보만 활용
- 2MB 페이지 거주 시: delta 범위 확장 (예: SPP의 경우 -32768~+32768)
- 4KB 페이지 거주 시: 기존 동작 유지 (delta: -64~+64)

### 4.2. Pref-PSA-2MB

- 프리페처 내부 구조를 2MB 페이지로 인덱싱
- 장점: 4KB 페이지 대비 조잡한 접근 패턴 표현, 예측 테이블 얼리어싱 감소
- 단점: 일부 워크로드에서 서로 다른 4KB 페이지의 패턴을 동일 엔트리로 일반화하여 성능 저하 (Finding 4)

### 4.3. Pref-PSA-SD (Set Dueling 기반)

- 동일한 프리페처의 PSA 버전과 PSA-2MB 버전을 병렬로 구성
- Set-Dueling 기반 적응형 로직으로 워크로드 특성에 따라 최적 버전 동적 선택
- 4KB 페이지 중심 워크로드: PSA 활성화 (예: sphinx3, pr_road)
- 2MB 페이지 중심 워크로드: PSA-2MB 활성화 (예: milc, qmm_fp_67)
- 실행 단계별 전환 가능으로 평균 최대 성능 달성

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/security.md|Security]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2022MICRO-summarize/page-size-aware-cache-prefetching.md|전체 요약 보기]]
