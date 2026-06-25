---
tags: [paper, 2025, 2025ISCA, topic/dram, topic/gpu, topic/nvm, topic/pim]
venue: "International Symposium on Computer Architecture (ISCA) 2025"
year: 2025
summary_path: "../paper-summaries/2025ISCA-summarize/atim-autotuning-tensor-programs-for-processing-in-dram.md"
---

# ATiM: Autotuning Tensor Programs for Processing-in-DRAM

**Venue:** International Symposium on Computer Architecture (ISCA) 2025
**저자:** Yongwon Shin (POSTECH), Dookyung Kang (Seoul National University), Hyojin Sung (Seoul National University)

## 개요

- 현대 애플리케이션은 데이터 집약적 특성으로 인해 성능 병목이 연산 유닛 효율에서 메모리 성능으로 이동
- Processing-in-DRAM (DRAM-PIM)은 메모리 뱅크 근처에 연산 유닛을 배치하여 데이터 전송 오버헤드를 줄이는 유망한 기술
- UPMEM과 같은 상용 DRAM-PIM 제품은 최대 16배의 인메모리 연산 대역폭을 제공하지만, 기존 소프트웨어 스택은 심각한 한계에 직면:
  - **프로그래밍 가능성 부재**: 핸드튜닝된 라이브러리에 의존하여 높은 수준의 추상화 부족
  - **제한된 최적화 지원**: 호스트/커널 코드를 체계적으로 최적화하는 프레임워크 부재
  - **자동화 부재**: 자동 튜닝 통합 코드 생성 지원 불가
- 기존 텐서 컴파일러(TVM, Halide)는 CPU/GPU에 최적화되어 있지만, DRAM-PIM의 고유한 특성(뱅크 레벨 병렬성, 제한된 연산 자원)을 고려하지 않음
- UPMEM 커널 최적화는 호스트 코드 파라미터에 의존하여 더 크고 복잡한 탐색 공간을 생성

## 방법론

### 3.1. 시스템 아키텍처

- **전체 파이프라인**:
  1. 설계 공간 생성 (Design Space Generation)
  2. 진화적 탐색 (Evolutionary Search)
  3. TIR 로워링 및 최적화 (TIR Lowering and Optimization)
  4. 컴파일 및 하드웨어 평가
  5. 비용 모델 업데이트 및 반복

- **자동 튜너 (Autotuner)**:
  - 스케치 생성 규칙을 사용하여 호스트/커널 스케줄 후보 생성
  - 비용 모델 기반 유망 후보 선택
  - 하드웨어 측정을 통한 성능 검증

- **코드 생성기 (Code Generator)**:
  - 스케줄 프리미티브를 루프 기반 TIR로 변환
  - UPMEM 호스트/커널 코드 생성
  - PIM-aware 최적화 적용

### 3.2. 탐색 공간

- **호스트 수준 최적화**:
  - DPU당 데이터 분배 전략
  - 타일 크기 및 모양
  - DPU 수 및 배치

- **커널 수준 최적화**:
  - 루프 타일링 팩터 (split factors)
  - 태스크 병렬화 (tasklet 병렬화)
  - 캐싱 타일 크기 및 위치
  - 언롤링 팩터

- **상호 의존성**: 호스트 최적화가 커널 성능에 영향을 미치고, 그 반대도 성립하여 공동 최적화 필요

### 3.3. PIM-aware 최적화

- **DMA-aware 경계 검사 제거**:
  - 요소별 메모리 할당 및 경계 검사를 DMA 명령어로 대체
  - MRAM-WRAM DMA를 통한 안전한 데이터 오버페치 허용
  - 최대 23.7% 가속 달성

- **루프 경계 강화 (Loop-bound Tightning)**:
  - 정렬되지 않은 열을 가진 텐서에서 중복된 경계 검사 제거
  - 계산 루프 내부의 조건문 최소화

- **불변 브랜치 호이스팅 (Invariant Branch Hoisting)**:
  - 행 변수에 의존하는 불변 브랜치를 메인 루프 외부로 이동
  - 불필요한 반복 스킵으로 브랜치 패널티 감소

## 핵심 기여

- **핵심 기여**: DRAM-PIM을 위한 최초의 완전 자동화된 자동 튜닝 통합 텐서 컴파일러 개발
- **성능 향상**: 벤치마크 커널에서 최대 6.18x, GPT-J 레이어에서 최대 8.21x 가속
- **프로그래밍 가능성**: 고수준 텐서 추상화를 통한 DRAM-PIM 프로그래밍 용이성 향상
- **확장성**: UPMEM 외에 HBM-PIM 등 다른 DRAM-PIM 아키텍처로의 확장 가능성 제시
- **의의**: DRAM-PIM 소프트웨어 스택의 발전을 위한 기반 기술로, 메모리 병목 문제 해결에 기여

## 주요 결과

- **구현 언어**: Python (컴파일러), C (UPMEM 커널)
- **프레임워크**: Apache TVM 기반 확장
- **하드웨어 대상**: UPMEM DDR4 PIM 시스템
  - 호스트 CPU + PIM 활성화 메모리
  - 각 DPU: 32비트 RISC 코어, 24 스레드 (tasklet)
  - 메모리: 24KB IRAM, 64KB WRAM, 64MB MRAM
- **컴파일**: TVM 백엔드 + LLVM 컴파일러
- **자동 튜닝**: 1000 trials, 진화적 탐색 + 비용 모델

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2025ISCA-summarize/atim-autotuning-tensor-programs-for-processing-in-dram.md|전체 요약 보기]]
