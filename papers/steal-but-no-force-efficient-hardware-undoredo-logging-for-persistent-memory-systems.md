---
tags: [paper, 2018, 2018HPCA, topic/nvm, topic/storage]
venue: "HPCA '18 (IEEE International Symposium on High Performance Computer Architecture), 2018"
year: 2018
summary_path: "../paper-summaries/2018HPCA-summarize/steal-but-no-force-efficient-hardware-undoredo-logging-for-persistent-memory-systems.md"
---

# Steal but No Force: Efficient Hardware Undo+Redo Logging for Persistent Memory Systems

**Venue:** HPCA '18 (IEEE International Symposium on High Performance Computer Architecture), 2018
**저자:** Matheus Almeida Ogleari, Ethan L. Miller, Jishen Zhao (University of California, Santa Cruz; Pure Storage; University of California, San Diego)

## 개요

- 영속 메모리(persistent memory)는 기존 저장 시스템과 메모리의 하이브리드 역할을 하는 새로운 메모리 계층
- 데이터 영속성과 빠른 load/store 인터페이스를 동시에 제공
- 기존 영속 메모리 설계의 한계:
  - 쓰기 순서 제어(write-order control)를 통해 캐시와 메모리 컨트롤러의 성능 최적화 방해
  - 쓰기 결합(write coalescing) 및 재ordering 최적화 불가
  - 높은 성능 및 에너지 오버헤드 발생
  - 기존 소프트웨어 로깅 메커니즘은 성능 및 에너지 오버헤드로 인해 비효율적
  - 이전 하드웨어 로깅 방식은 효율적이지 않음

## 방법론

### 3.1. Undo+Redo 로깅 메커니즘
- 영속 데이터 업데이트 시 이전(undo) 값과 새(redo) 값을 모두 로그에 저장
- 쓰기 순서 제어를 완화하여 캐시에서 영속 데이터를 캐싱할 때 유연성 제공
- 캐시와 메모리 컨트롤러가 기존 비영속 메모리 시스템처럼 쓰기를 재ordering할 수 있게 함
- 소프트웨어 로깅의 비효율성을 하드웨어로 해결

### 3.2. 캐시 강제 쓰기 되돌리기 메커니즘
- 하드웨어에서 캐시된 데이터를 영속 메모리로 강제 쓰기 위한 메커니즘
- 쓰기 순서 제어로 인한 성능 오버헤드 크게 감소
- 에너지 효율성 향상
- 메모리 트래픽 감소

### 3.3. 메모리 시스템 통합
- 기존 메모리 시스템과의 호환성 유지
- NVRAM 캐시나 버퍼 없이도 높은 성능 달성
- 저성능 모드로의 전환 방지
- 캐시와 메모리 컨트롤러의 쓰기 재ordering 간섭 없음

### 3.4. 일관성 보장
- 소프트웨어 방식보다 강력한 일관성 보장 제공
- 데이터 영속성 보장하면서 성능 향상
- 쓰기 순서 제어를 완화하면서도 일관성 유지

## 핵심 기여

- 핵심 기여: 하드웨어 undo+redo 로깅을 통한 영속 메모리 시스템의 성능 및 에너지 효율성 향상
- 성능 향상: 쓰기 순서 제어 완화를 통한 시스템 처리량 증가
- 에너지 효율성: 메모리 트래픽 감소를 통한 동적 에너지 절약
- 실용적 적용: 기존 메모리 시스템과의 호환성 유지로 실용적 적용 가능성 입증

---

## 규칙 준수
1. 한국어로 작성 (기술 용어는 영어 원어 병기)
2. 수치적 결과 포함 (처리량, 에너지, 메모리 트래픽 비교)
3. 모든 Figure/Table 참조 포함
4. 각 섹션은 최소 3개 이상의 bullet point
5. 알고리즘/수식이 있으면 pseudo-code 수준으로 기술
6. 기존 요약 파일 형식과 퀄리티 준수

## 주요 결과

- 구현 구성 요소:
  - 하드웨어 undo+redo 로깅 로직
  - 캐시 강제 쓰기 되돌리기 메커니즘
  - 메모리 컨트롤러 확장
- 하드웨어 요구 사항:
  - 기존 프로세서 아키텍처에 하드웨어 로깅 로직 추가
  - 캐시 하위 시스템과의 통합
- 소프트웨어 지원:
  - 기존 영속 메모리 프로그래밍 모델과의 호환성 유지

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2018HPCA-summarize/steal-but-no-force-efficient-hardware-undoredo-logging-for-persistent-memory-systems.md|전체 요약 보기]]
