---
tags: [paper, 2018, 2018HPCA, topic/nvm]
venue: "IEEE International Symposium on High Performance Computer Architecture (HPCA) 2018"
year: 2018
summary_path: "../paper-summaries/2018HPCA-summarize/crash-consistency-in-encrypted-non-volatile-main-memory-systems.md"
---

# Crash Consistency in Encrypted Non-Volatile Main Memory Systems

**Venue:** IEEE International Symposium on High Performance Computer Architecture (HPCA) 2018
**저자:** Sihang Liu (University of Virginia), Aasheesh Kolli (VMware Research/Pennsylvania State University), Jinglei Ren (Microsoft Research), Samira Khan (University of Virginia)

## 개요

- 비휘발성 메인 메모리(NVMM) 시스템은 메모리 내에서 직접 지속성 데이터를 조작하여 높은 성능을 제공하지만, 시스템 크래시 시 데이터 복구를 위한 crash consistency 지원 필요
- 물리적 접근이 가능한 공격자로부터 데이터를 보호하기 위해 메모리 암호화 필수
- 기존 counter-mode 암호화는 각 캐시 라인과 연결된 카운터를 사용하여 병렬로 복호화하지만, 크래시 시 암호화된 데이터와 관련 카운터가 원자적으로 기록되지 않으면 데이터 복구 실패
- 모든 NVMM 쓰기에 대해 counter-atomicity를 엄격히 적용하면 메모리 접근 직렬화로 성능 저하 발생

## 방법론

### 3.1. Counter-Atomicity 문제점 분석

- 모든 NVMM 쓰기에 대해 암호화된 데이터와 카운터가 원자적으로 기록되어야 함
- naively 적용 시 메모리 접근 직렬화 → 심각한 성능 저하
- 버전 관리 메커니즘을 활용하여 복구 가능한 지속적 상태를 보존하는 관찰

### 3.2. 선택적 Counter-Atomicity 설계

- 복구 가능한 지속적 상태를 변경하지 않는 쓰기의 경우 쓰기 순서 재배치 허용
- 소프트웨어 및 하드웨어 지원을 통한 효율적 구현
- 기존 crash consistency 메커니즘(버전 관리)과의 호환성 확보

### 3.3. 성능 최적화 전략

- 선택적 적용을 통한 불필요한 직렬화 방지
- 다양한 코어 수(1/2/4/8)에서의 성능 향상 검증
- 이상적인 NVMM 시스템 대비 5% 이내 성능 달성

## 핵심 기여

- 암호화된 NVMM 시스템에서 crash consistency와 메모리 암호화 간의 상호작용 분석
- 선택적 counter-atomicity를 통해 성능 저하 최소화
- 다양한 코어 수에서 최대 40% 성능 향상 달성
- NVMM 시스템 설계 시 보안과 성능을 동시에 고려하는 방안 제시

## 주요 결과

- 소프트웨어 및 하드웨어 지원을 통한 선택적 counter-atomicity 구현
- 기존 crash consistency 메커니즘과의 통합
- 다양한 NVMM 기술(PCM, STT-RAM, ReRAM, 3D XPoint)과의 호환성

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]


## 전체 요약

[[../paper-summaries/2018HPCA-summarize/crash-consistency-in-encrypted-non-volatile-main-memory-systems.md|전체 요약 보기]]
