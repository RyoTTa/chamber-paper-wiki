---
tags: [paper, 2018, 2018MICRO, topic/gpu]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/swapcodes-error-codes-for-hardware-software-cooperative-gpu-pipeline-error-detection.md"
---

# SwapCodes: Error Codes for Hardware-Software Cooperative GPU Pipeline Error Detection

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Michael B. Sullivan, Siva Kumar Sastry Hari, Brian Zimmer, Timothy Tsai, Stephen W. Keckler (NVIDIA)

## 개요

- 데이터센터 및 HPC 시스템은 하드웨어 신뢰성을 높이기 위해 ECC(Error Checking and Correcting) 코드를 대용량 메모리 구조에 적용.
- **스토리지 ECC의 한계:** 온칩 메모리의 오류를 감지/수정하지만, 파이프라인 구조(데이터패스 레지스터, 산술 로직)에서 발생하는 오류는 보호하지 못함.
- **파이프라인 오류의 심각성:** GPU 기반 프로세서의 SM 파이프라인 오류가 프로그램 출력에서 최대 20~40%의 조용한 데이터 손상(Silent Data Corruption, SDC)을 유발.
- **기존 해결책의 문제점:** 스레드 내 명령어 중복(Intra-thread instruction duplication)은 효과적이지만:
  1. 명시적 체크 명령어 사용 → 최대 35% 동적 명령어 팽창(dynamic instruction bloat)
  2. 프로그램 레지스터 사용량 증가 → 데이터 집약적 프로세서의 병렬성 제한
  3. 산술 명령어 2배 증가 → 계산 대역폭 제한 프로그램의 심각한 성능 저하
- GPU의 경우 스레드당 상태가 제한적이며, 상태 증가는 동시 실행 스레드 수를 감소시켜 성능 저하 유발.

## 방법론

### 3.1. Swap-ECC (소프트웨어 중심 접근)

- **SEC-DED-DP:** SEC-DED 코드 제약 없이 동작하는 알고리즘
  - 모든 SEC-DED 코드에서 파이프라인 오류의 완전한 잘못된 수정(miscorrection) 방지
- **SEC-DP:** SEC-DED 코드에 추가 제약을 적용하여 오버헤드를 줄이는 알고리즘
- **동작 원리:**
  1. 명령어 중복 실행
  2. 레지스터 파일에 기록 시 ECC 체크 비트를 스왑
  3. 레지스터 파일 읽기 시 ECC 디코더로 파이프라인 오류 암묵적 감지
- **장점:** 하드웨어 변경 최소화, 기존 ECC 하드웨어 재사용

### 3.2. Swap-Predict (선택적 ECC 체크 비트 예측)

- Swap-ECC를 확장하여 선택적 ECC 체크 비트 예측을 통해 효율성 향상.
- **Mixed-operand-width GPU MAD 명령어 지원:** 혼합 피연산자 폭의 GPU MAD 명령어에 대한 레시듀 코드(residue code) 예측 문제 해결.
- **기회주의적 최적화:** 예측 가능한 경우에만 ECC 체크 비트를 미리 계산하여 성능 오버헤드 추가 감소.

### 3.3. 하드웨어 영향 범위

- **보호 대상:** SM(Streaming Multiprocessor) 파이프라인 데이터패스.
- **보호하지 않는 대상:** 명령어 전달 및 메모리 서브시스템 (스토리지 ECC 및 버스 패리티로 보호).
- **추가 하드웨어:** 새로운 하드웨어 에러 체커 또는 버퍼 필요 없음.
- **스테이트 오버헤드:** 스레드당 그림자 상태(shadow state) 예약 없음 → 병렬성 유지.

## 핵심 기여

- **핵심 기여:** SwapCodes — 기존 레지스터 파일 ECC 하드웨어를 재사용하여 파이프라인 오류를 암묵적으로 감지하는 소프트웨어-하드웨어 협력 메커니즘.
- **성능:** 기존 소프트웨어 명령어 중복 대비 **성능 오버헤드 절반 감소** (15% vs 30%).
- **신뢰성:** **99.3% 이상의 파이프라인 오류 감지율** 달성.
- **효율성:** 추가 하드웨어 에러 체커나 버퍼 불필요, 기존 ECC 하드웨어 재사용.
- **의의:** 데이터 집약적 프로세서(GPU)의 파이프라인 오류 감지에서 성능과 신뢰성의 효과적인 트레이드오프를 달성한 최초의 메커니즘. 하드웨어 변경 없이 기존 시스템에 통합 가능.

## 주요 결과

- **구현 언어:** 수정된 컴파일러 패스 (컴파일러 수준에서 명령어 중복 및 ECC 비트 스왑 자동 삽입).
- **하드웨어 플랫폼:** NVIDIA Tesla P100 기반 GPU.
- **평가 환경:** 게이트 수준 주입(gate-level fault injection)을 통한 복원력 검증.
- **오픈소스:** 수정된 컴파일러 패스 포함.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/gpu.md|GPU]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/swapcodes-error-codes-for-hardware-software-cooperative-gpu-pipeline-error-detection.md|전체 요약 보기]]
