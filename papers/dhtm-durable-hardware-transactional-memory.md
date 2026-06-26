---
tags: [paper, 2018, 2018ISCA, topic/cache, topic/nvm]
venue: "International Symposium on Computer Architecture (ISCA) 2018"
year: 2018
summary_path: "../paper-summaries/2018ISCA-summarize/dhtm-durable-hardware-transactional-memory.md"
---

# DHTM: Durable Hardware Transactional Memory

**Venue:** International Symposium on Computer Architecture (ISCA) 2018
**저자:** Arpit Joshi (University of Edinburgh), Vijay Nagarajan (University of Edinburgh), Marcelo Cintra (Intel, Germany), Stratis Viglas (Google)

## 개요

- 바이트 주소 가능한 영구 메모리(persistent memory)는 낮은 지연 시간과 높은 대역폭을 제공하지만, 시스템 크래시 시 어떤 데이터가 영구 메모리에 남을지 보장이 필요
- ACID 트랜잭션은 크래시 일관성 프로그래밍의 널리 받아들여지는 모델이지만, 기존 소프트웨어 기반 접근 방식은 상당한 성능 오버헤드 발생
- 기존 상용 하드웨어 트랜잭션 메모리(HTM)의 한계:
  - L1 캐시 크기에 의해 트랜잭션 크기 제한 (128 캐시 라인 초과 시.abort 가능성 높음)
  - ACI 보장만 제공 (원자적 가시성만 지원, 내구성 미지원)
- 기존 기술의 분류 (Table I):
  - 소프트웨어 로깅 기반: Atlas, REWIND, DudeTM, Mnemosyne
  - 하드웨어 내구성 지원: WrAP, DPO, LOC, HOPS, ATOM, Kiln
  - HTM + 소프트웨어 내구성: DudeTM, PHyTM, cc-HTM
  - HTM + 하드웨어 내구성: PTM (L1 제한 유지)

## 방법론

### 3.1. 시스템 모델
- 2단계 캐시 계층을 가진 다중 코어 프로세서
- 프라이빗 L1 캐시와 공유 LLC(Last Level Cache)
- MESI 디렉토리 기반 코어런스 프로토콜
- 비휘발성 바이트 주소 가능한 메모리

### 3.2. 하드웨어 로깅 메커니즘
- redo 로깅 선택 이유: 빠른 커밋과 abort 지원
- 커밋 시 redo 로그만 영구 메모리에 기록 (데이터 업데이트는 백그라운드에서 처리)
- L1 캐시 컨트롤러가 LLC를 우회하여 영구 메모리에 직접 로그 항목 기록
- 워드 단위 로깅에서 캐시 라인 단위로 최적화

### 3.3. 로그 병합(Log Coalescing)
- 로그 버퍼(log buffer) 구조를 L1 캐시에 추가
- 완전 연관(associative) 구조로 캐시 라인 주소 추적
- 로그 버퍼에서 제거될 때만 영구 메모리에 로그 기록
- 동일 캐시 라인에 대한 여러 저장을 하나의 로그로 병합
- Figure 2c 예시: 5개 저장 요청이 2개의 로그 쓰기로 감소

### 3.4. HTM과의 통합
- 커밋 프로세스:
  1. 모든 redo 로그 항목을 영구 메모리에 기록
  2. 읽기/쓰기 세트 추적 구조 클리어
  3. 추론적 상태를 다른 스레드에 가시화
- 상태 다이어그램: Active → Commit → Commit Complete / Abort Complete
- 비트랜잭션 접근은 RTM과 동일하게 처리

### 3.5. 오버플로우 관리
- 쓰기 세트가 L1에서 LLC로 오버플로우 허용
- 코어런스 프로토콜에 미세한 변경만으로 구현
- LLC에 추가 트랜잭션 추적 하드웨어 불필요
- 오버플로우된 캐시 라인의 주소를 로그에 기록

## 핵심 기여

- DHTM은 ACID 트랜잭션을 위한 최초의 완전한 하드웨어 솔루션
- L1 캐시 제한 없이 LLC까지 확장된 트랜잭션 크기 지원
- 하드웨어 redo 로깅과 로그 병합을 통한 효율적인 내구성 보장
- 기존 기술 대비 21% ~ 25% 성능 향상
- 크래시 일관성 프로그래밍의 부담을 크게 완화할 잠재력

## 주요 결과

- 인텔 RTM 기반 상용 HTM 활용
- MESI 디렉토리 기반 코어런스 프로토콜
- 로그 버퍼: 완전 연관 구조, 소수의 엔트리
- 영구 메모리: 바이트 주소 가능한 비휘발성 메모리

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]


## 전체 요약

[[../paper-summaries/2018ISCA-summarize/dhtm-durable-hardware-transactional-memory.md|전체 요약 보기]]
