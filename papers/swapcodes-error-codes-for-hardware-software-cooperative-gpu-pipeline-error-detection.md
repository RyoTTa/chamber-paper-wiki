---
tags: [paper, 2018, 2018MICRO, topic/gpu, topic/security]
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
- **기존 해결책의 문제점:** 스레드 내 명령어 중복(Intra-thread instruction duplication)은 효과적이지만 명시적 체크 명령어 사용으로 인한 성능 오버헤드 발생.

## 방법론

### 1. Swap-ECC (소프트웨어 중심 접근)

- **SEC-DED-DP:** SEC-DED 코드 제약 없이 동작하는 알고리즘
- **SEC-DP:** SEC-DED 코드에 추가 제약을 적용하여 오버헤드를 줄이는 알고리즘
- **동작 원리:**
  1. 명령어 중복 실행
  2. 레지스터 파일에 기록 시 ECC 체크 비트를 스왑
  3. 레지스터 파일 읽기 시 ECC 디코더로 파이프라인 오류 암묵적 감지

### 2. Swap-Predict (선택적 ECC 체크 비트 예측)

- Swap-ECC를 확장하여 선택적 ECC 체크 비트 예측을 통해 효율성 향상.
- Mixed-operand-width GPU MAD 명령어에 대한 레시듀 코드(residue code) 예측 문제 해결.

### 3. 하드웨어 영향 범위

- **보호 대상:** SM(Streaming Multiprocessor) 파이프라인 데이터패스.
- **추가 하드웨어:** 새로운 하드웨어 에러 체커 또는 버퍼 필요 없음.
- **스테이트 오버헤드:** 스레드당 그림자 상태(shadow state) 예약 없음 → 병렬성 유지.

## 핵심 기여

- 기존 레지스터 파일 ECC 하드웨어를 재사용하여 파이프라인 오류를 암묵적으로 감지하는 소프트웨어-하드웨어 협력 메커니즘.
- 기존 소프트웨어 명령어 중복 대비 **성능 오버헤드 절반 감소** (15% vs 30%).
- **99.3% 이상의 파이프라인 오류 감지율** 달성.

## 주요 결과

- **성능:** 기존 소프트웨어 명령어 중복 대비 **평균 느림 비율을 절반으로 감소** (15% vs 30%).
- **오류 감지율:** 표준 ECC 보호 레지스터 파일에서 **98.8% 이상**, 동일 잉여도 코드에서 **99.3% 이상** 달성.
- **효율성:** 추가 하드웨어 에러 체커나 버퍼 불필요, 기존 ECC 하드웨어 재사용.

## 한계점

- 주로 NVIDIA GPU 아키텍처에 특화되어 있어 다른 GPU 벤더와의 호환성 필요.
- 단일 스레드 내 명령어 중복에 의존하여 멀티스레드 환경에서의 효과 미검증.

## 관련 개념

- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/security.md|Security]]

## 전체 요약

[[../paper-summaries/2018MICRO-summarize/swapcodes-error-codes-for-hardware-software-cooperative-gpu-pipeline-error-detection.md|전체 요약 보기]]