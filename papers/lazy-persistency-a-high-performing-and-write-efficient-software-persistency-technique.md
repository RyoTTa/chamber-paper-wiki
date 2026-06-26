---
tags: [paper, 2018, 2018ISCA, topic/cache, topic/nvm]
venue: "International Symposium on Computer Architecture (ISCA) 2018"
year: 2018
summary_path: "../paper-summaries/2018ISCA-summarize/lazy-persistency-a-high-performing-and-write-efficient-software-persistency-technique.md"
---

# Lazy Persistency: A High-Performing and Write-Efficient Software Persistency Technique

**Venue:** International Symposium on Computer Architecture (ISCA) 2018
**저자:** Mohammad Alshboul, James Tuck, Yan Solihin (North Carolina State University)

## 개요

- 비휘발성 메모리(NVM)가 차세대 메인 메모리로 포함될 것으로 예상되지만, 데이터를 영구적으로 보관하려면 프로그램이 장애 안전성(failure-safety)을 고려하여 작성되어야 함
- 기존 Eager Persistency 기술의 한계:
  - 프로그래머가 캐시의 더러운 블록을 NVMM으로 즉시 플러시하도록 강제 (persist barrier, cache line flush 등)
  - 추가 명령어로 인해 명령어 수 대폭 증가
  - LLC와 NVMM을 포함하는 전체 캐시 계층에서 높은 지연 시간 발생 → 파이프라인 스톨 빈번
  - NVMM에 쓰기가 강제됨에 따라 쓰기 내구성(write endurance) 감소 및 높은 전력 오버헤드
- Intel PMEM 모델에서 저장, 캐시 라인 플러시, store fence의 순서가 필요하며, 원자적 내구성은 소프트웨어가 직접 처리해야 함

## 방법론

### 3.1. 영속성 영역(Persistency Region)
- 프로그래머가 복구 단위인 LP 영역의 세분화(granularity)를 정의
- 예: 타일화된 행렬 곱셈에서 ii 반복을 하나의 LP 영역으로 설정
- 복구 코드가 동일 영역의 계산을 재실행하는 방식
- 영역이 멱등(idempotent)인 경우 복구 코드가 본래 영역 코드와 동일

### 3.2. 오류 검출(Checksum) 메커니즘
- Modular Checksum과 Adler-32를 비교 평가
- Modular Checksum이 기본 기법으로 선택됨 (오버헤드 최소화)
- 오류 탐지 확률: 2 × 10⁻⁹ 미만 (Modular 및 Adler-32 모두)
- 체크섬을 별도 해시 테이블에 저장하는 구조 선택 (데이터 구조에 임베디드하는 것보다 프로그래밍 복잡도 낮음)
- 충돌 없는 해시 테이블: 행렬 크기의 1% 공간 오버헤드

### 3.3. 복구(Recovery) 메커니즘
- 실패 후 체크섬 불일치가 발견된 영역을 재계산으로 복구
- 복구 코드에는 Eager Persistency 적용 (복구 중 추가 실패 방지를 위해)
- 영역 내 멱등성 보장을 위한 역순 kk 반복 처리
- 무한한 복구 시간 제한을 위해 주기적 캐시 정리(periodic cache flushing) 사용 가능

### 3.4. 코드 변환 예시 (타일화된 행렬 곱셈)
- 원래 코드에 체크섬 리셋, 체크섬 업데이트, 해시 테이블 저장 등 3줄만 추가
- 멀티스레드 시 체크섬 변수를 스레드별로 비공개 선언하면 됨
- 충돌 없는 해시 테이블로 락 불필요

## 핵심 기여

- Lazy Persistency는 Eager Persistency의 쓰기 증폭 및 성능 오버헤드를 크게 감소
- 실행 시간 오버헤드 9% → 1%, 쓰기 증폭 21% → 3%로 개선
- 과학 컴퓨팅 커널에 적용 가능하며, 컴파일러 자동 변환 가능성
- 복구 시간의 비용을 정상 실행의 빠름과 교환하는 새로운 영속성 패러다임 제시

## 주요 결과

- 소프트웨어 기반 접근: 프로그래머가 LP 영역 정의, 오류 검출 코드 삽입, 복구 코드 작성
- 컴파일러 패스를 통한 자동 변환 가능성 언급
- 체크섬은 32비트 정수 연산 (Modular Checksum)
- 해시 테이블: 충돌 없는 구조, 행렬 크기 대비 1% 공간

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]


## 전체 요약

[[../paper-summaries/2018ISCA-summarize/lazy-persistency-a-high-performing-and-write-efficient-software-persistency-technique.md|전체 요약 보기]]
