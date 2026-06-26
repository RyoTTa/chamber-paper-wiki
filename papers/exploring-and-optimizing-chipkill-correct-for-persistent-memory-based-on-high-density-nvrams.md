---
tags: [paper, 2018, 2018MICRO, topic/cache, topic/dram, topic/nvm]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/exploring-and-optimizing-chipkill-correct-for-persistent-memory-based-on-high-density-nvrams.md"
---

# Exploring and Optimizing Chipkill-Correct for Persistent Memory Based on High-density NVRAMs

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Da Zhang (Virginia Tech), Vilas Sridharan (AMD), Xun Jian (Virginia Tech)

## 개요

- 고밀도 비휘발성 랜덤 액세스 메모리(NVRAM: PCM, ReRAM, STT-RAM)는 DRAM보다 높은 밀도와 빠른 지속 메모리 제공
- 서버 메모리 시스템의 핵심 요구사항: **신뢰성(Reliability)** — 수정 불가능한 오류는 시스템 크래시나 영구적 데이터 손실 초래
- 기존 DRAM 서버는 **chipkill-correct**로 비트 오류와 칩 고장을 동시에 보호
- 그러나 고밀도 NVRAM은 DRAM보다 높은 **원시 비트 오류율(RBER)** 보유:
  - ReRAM: 리프레시 없이 1년 후 RBER ~10⁻³
  - 3비트 PCM: 리프레시 없이 1주 후 RBER ~10⁻³
- 기존 DRAM chipkill-correct를 NVRAM에 그대로 적용하면 **>=69%** 저장 비용 발생 (비효율적)
- 저장 시스템은 **긴 ECC 워드(VLEWs)**로 높은 RBER를 효율적으로 보호하나:
  - 메인 메모리의 접근 세분성(64B)이 VLEW 크기(256B+)보다 작아 읽기 대역폭 오버헤드 발생
  - 쓰기 시 VLEW 코드 비트 업데이트에 read-modify-write 필요 → 쓰기 대역폭 오버헤드

## 방법론

### 3.1. 저장 비용 분석

- **14-bit-EC BCH** (비트 오류만 보호): **28%** 저장 비용
- **기존 DRAM chipkill-correct 확장**: 비트 오류 + 칩 고장 보호 시 **>=69%** 저장 비용
- **VLEW + 패리티 칩**: 256B 데이터 VLEW 사용 시 총 **27%** 저장 비용
  - 비트 오류 보호(28%)와 동일 수준이나 칩 고장 보호까지 추가

### 3.2. 읽기 과제 및 해결

- **문제**: VLEW가 32개 메모리 블록을 보호 → 블록 1개 읽기 시 추가 35개 블록 페칭 필요
  - RBER 7×10⁻⁵(런타임) 시 4% 접근에 비트 오류 → 140% 대역폭 오버헤드
- **해결**: 런타임에 칩 고장 보호 비트를 활용한 기회주의적 비트 오류 교정
  - 블록별 RS ECC로 비트 오류 교정 → 읽기 대역폭 오버헤드 최소화

### 3.3. 쓰기 과제 및 해결

- **문제**: VLEW 코드 비트 업데이트 시 old data + old ECC 필요 → 200% 쓰기 대역폭 오버헤드
- **OMV LLC 캐싱**:
  - L1/L2 캐시에서 LLC로 더러운 지속 메모리 블록 퇴출 시 OMV 보존
  - LLC 태그에 **SAM 비트** (SameAsMem)와 **OMV 비트** 추가
  - OMV 히트율 평균 **98.6%** → 거의 모든 쓰기에서 오프칩 OMV 페칭 불필요
- **Bitwise Sum 쓰기**:
  - 프로세서가 쓰기 요청 시 (x XOR x')를 메모리로 전송
  - NVRAM 칩이 내부에서: (1) old data를 비트wise 차로 새 데이터 복원, (2) BCH 선형성으로 VLEW 코드 비트 업데이트
  - 칩 내부 인코더: XOR 트리 기반, 면적 0.1mm², 지연 1.6ns

### 3.4. NVRAM 칩 내부 지원

- **BCH 인코더**: 선형 코드 특성 활용, 비트wise 합으로 직접 VLEW 업데이트 가능
- **ECC Update Register File (EUR)**: 같은 VLEW의 반복 쓰기 시 코드 비트 업데이트 병합
  - 라인 클로즈 시에만 EUR → 라인으로 드레인

## 핵심 기여

- **핵심 기여**: 고밀도 NVRAM 기반 지속 메모리의 효율적인 chipkill-correct 제안
- **저장 효율**: 기존 >=69% → **27%** 로 대폭 절감 (비트 오류 교정만과 동일 수준)
- **성능 비용**: 칩 고장 보호 추가에 따른 평균 **2%** 성능 오버헤드 (거의 무시 가능)
- **신뢰성**: chipkill-correct로 **40배** 신뢰성 개선 → 시스템 크래시/데이터 손실 위험 대폭 감소
- **실용성**: 기존 NVRAM 칩 구조와 호환, BCM 인코더 면적 0.1mm²로 제한적
- **의의**: NVRAM 기반 지속 메모리의 상용화를 위한 신뢰성 문제를 실용적으로 해결하는 방안 제시

## 주요 결과

- **시뮬레이터**: gem5 + Ramulator (메모리 성능 시뮬레이션)
- **프로세서**: 4코어, 3GHz, 4-issue OOO, 168 ROB
- **캐시**: L1 64KB (2-way), LLC 4MB (32-way)
- **메모리**: DDR4-2400, 1채널 (DRAM 랭크 1개 + NVRAM 랭크 1개)
- **NVRAM 지연 시간**:
  - ReRAM: 읽기 120ns, 쓰기 300ns
  - PCM: 읽기 250ns, 쓰기 600ns
- **벤치마크**: WHISPER (Echo, Memcached, HashMap, BTree, RBTree, Redis, Vacation) + SPLASH3 (Barnes, Cholesky, FFT, LU, Ocean, Radix, Water)
- **RBER 목표**: 10⁻³ (부팅 시), 7×10⁻⁵ (런타임, 1초 리프레시 시)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/exploring-and-optimizing-chipkill-correct-for-persistent-memory-based-on-high-density-nvrams.md|전체 요약 보기]]
