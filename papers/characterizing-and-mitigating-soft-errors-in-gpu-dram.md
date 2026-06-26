---
tags: [paper, 2021, 2021MICRO, topic/dram, topic/gpu]
venue: "54th Annual IEEE/ACM International Symposium on Microarchitecture (MICRO 2021)"
year: 2021
summary_path: "../paper-summaries/2021MICRO-summarize/characterizing-and-mitigating-soft-errors-in-gpu-dram.md"
---

# Characterizing and Mitigating Soft Errors in GPU DRAM

**Venue:** 54th Annual IEEE/ACM International Symposium on Microarchitecture (MICRO 2021)
**저자:** Michael B. Sullivan (NVIDIA), Nirmal Saxena (NVIDIA), Mike O'Connor (NVIDIA), Donghyuk Lee (NVIDIA), Paul Racunas (NVIDIA), Saurabh Hukerikar (NVIDIA), Timothy Tsai (NVIDIA), Siva Kumar Sastry Hari (NVIDIA), Stephen W. Keckler (NVIDIA)

## 개요

- GPU는 HPC, 자율 주행 등 고신뢰 시스템에서 필수적이며, 현대 compute-class GPU는 고대역폭 메모리를 위해 온패키지 HBM2 메모리를 사용. 그러나 HBM2는 **64b 와이드 per pseudo-channel**로 각 메모리 접근이 단일 DRAM 디바이스에서 이루어지므로, CPU DIMM의 "chipkill" ECC처럼 전체 디바이스 보정이 불가능.
- DRAM 공정 미세화로 인해 **비트셀 오류율은 감소**하고 있으나, 로직 오류(logic errors)는 공정 축소에 비례하지 않고 지속적으로 발생하여 **다중비트 오류의 상대적 비중이 증가**하는 추세 (Figure 1).
- 기존 GPU는 SEC-DED ECC를 사용하지만, HBM2의 다중비트 오류 패턴에는 **비최적(suboptimal)**. 특히 SEU의 약 **31.5%가 단일 워드 내 다중비트에 영향**을 미치며, 이 중 **~75%는 논리적으로 연속된 바이트에 국한**.
- 자율 주행 및 데이터센터 환경에서 **Silent Data Corruption (SDC)** 위험이 점점 커지고 있어, GPU DRAM의 정확한 오류 특성 분석과 효과적인 보호 체계가 필요.

## 방법론

### 3.1. Displacement Damage와 간헐적 오류

- 고에너지 중성자에 의해 DRAM access transistor가 물리적으로 손상되어 **셀 누설 전류 증가** 및 **유지 시간(retention time)이 수 배 감소**.
- 간헐적 오류는 빔 노출 없이도 지속되며, GPU당 **수천 개의 단일비트 오류**로 나타남.
- DRAM refresh rate를 조절하여 특성화: refresh period 증가에 따라 **약한 셀(weak cell) 수가 단조 증가**하며, 정규분포로 잘 피팅됨 (Figure 3).
- displacement damage는 현장(field)에서는 발생하지 않으므로, **오류 보호 체계에서 제외 가능**.
- 필터링 방법: GPU DRAM ECC를 활성화한 상태에서 빔 테스트하거나, 후처리로 필터링.

### 3.2. 소프트 에러 패턴 분석

- HBM2 소프트 에러는 **희소하지만 심각(rare but severe)**: SEU의 **~31.5%가 다중비트 오류**.
- 다중비트 오류의 **~75%는 논리적으로 연속된 8b 바이트에 국한** (byte-aligned).
- 이는 HBM2의 계층적 구조와 일치: 데이터가 **mat 단위 8b 접근 그레뉼리티**로 저장됨.
- HBM2 구조: 8 channels × 16 banks × 32 subarrays × 32 data mats, 각 mat은 **512×512 비트 배열**.
- 단일 DRAM read는 단일 subarray에서 모든 데이터를 가져오며, 각 mat은 **8b wide slice**를 담당.
- 다중비트 오류는 DRAM 로직 구조(logic structures)에서 기원하며, 비트셀 오류와는 다른 패턴을 보임.

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1. DuetECC / TrioECC (이진 ECC)

- SEC-DED ECC의 **드롭인 교체(drop-in replacement)**: 동일한 하드웨어 포트폴리오에서 작동.
- **단일비트 보정 + 단일핀 보정** 기능 유지 (영구 핀 오류 대응 가능).
- DuetECC: SEC-DED 대비 **SDC 위험 3자릿수 이상 감소**.
- TrioECC: 더 공격적인 보정 수행 → **미보정 오류(DUE) 7.87× 감소**, SDC 위험 **2자릿수 감소**.
- **재구성 가능한 디코더(reconfigurable decoder)**를 통해 보정/SDC 트레이드오프 노출.
- 추가적인 redundancy 없이 기존 SEC-DED 대비 개선.

### 4.2. SSC-DSD+ (심볼 기반 ECC)

- 심볼 기반 ECC 코드로, DuetECC 대비 **SDC 위험을 2자릿수 더 추가로 감소**.
- TrioECC에 근접하는 보정율 달성.
- SEC-DED로부터의 출발이 큰 경우에 유리: **디코더가 더 크고 느림**.
- 영구 핀 오류 보정 능력을 희생하는 대가로 더 높은 보호 수준 제공.
- 메모리 접근당 12.5% redundancy 내에서 설계.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]


## 전체 요약

[[../paper-summaries/2021MICRO-summarize/characterizing-and-mitigating-soft-errors-in-gpu-dram.md|전체 요약 보기]]
