---
tags: [paper, 2024, 2024ISCA, topic/cache, topic/dram, topic/gpu, topic/virtual-memory]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO 2021)"
year: 2024
summary_path: "../paper-summaries/2024ISCA-summarize/improving-address-translation-in-multi-gpus.md"
---

# Improving Address Translation in Multi-GPUs via Sharing and Spilling aware TLB Design

**Venue:** IEEE/ACM International Symposium on Microarchitecture (MICRO 2021)
**저자:** Bingyao Li (University of Pittsburgh), Jieming Yin (Lehigh University), Youtao Zhang (University of Pittsburgh), Xulong Tang (University of Pittsburgh)

## 개요

- 애플리케이션 복잡도와 데이터셋 규모 증가로 단일 GPU로는 처리 능력이 부족해지면서, 다중 GPU(multi-GPU) 시스템의 사용이 빠르게 증가하고 있음
- 그러나 다중 GPU에서의 성능 확장(scalability)이 기대에 미치지 못하는데, 주요 원인 중 하나가 **주소 변환(address translation) 효율성**
- GPU의 주소 변환은 다단계 TLB 계층(L1 TLB → L2 TLB → IOMMU TLB)과 페이지 테이블 워크(PTW)로 구성되며, TLB miss 시 IOMMU까지의 지연 시간이 매우 큼 (IOMMU TLB lookup: 200 cycles, PTW: 500 cycles)
- 다중 GPU에서는 여러 GPU가 **공유 IOMMU**를 경쟁하여 사용하므로 contention이 심화되어 최대 **50%의 실행 시간**이 주소 변환에 소요될 수 있음
- 기존 TLB 최적화 기법(대형 페이지, range-TLB, cluster-TLB, 추론 기반 등)은 단일 GPU/CPU 실행에 초점을 맞추고 있어 다중 GPU 환경에서 효과적이지 않음

## 방법론

### 3.1. 실험 환경

- **시뮬레이터:** MGPUSim (AMD GCN 아키텍처 기반, AMD R9 Nano로 검증)
- **시스템 구성:** 4-GPU 시스템, 공유 IOMMU. CU 1.0GHz, L1 TLB 16 entries, L2 TLB 512 entries, IOMMU TLB 4096 entries, PTW 8 워커(500 cycles)
- **단일 앱 워크로드:** AMDAPPSDK, Hetero-Mark, SHOC에서 9개 앱 선택 (MPKI: 0.003~2.394)
- **다중 앱 워크로드:** 10개 워크로드(W1~W10) 각각 4개 앱 구성 (LLLL~HHHH MPKI 혼합)

### 3.2. 단일 애플리케이션-다중 GPU 분석

- **관찰 1 (Obsv. 1):** L2 TLB와 IOMMU TLB 모두 낮은 hit rate를 보임
  - ST(MPKI=1.095): L2 TLB hit rate 5%, IOMMU TLB hit rate 35%
  - AES(MPKI=0.003): L2 TLB hit rate 42%, IOMMU TLB hit rate 3%
  - 무한 IOMMU TLB 시 **평균 42.3%** 성능 향상 (최대 2.4x)
- **관찰 2 (Obsv. 2):** 다수의 번역 재사용이 긴 재사용 거리(reuse distance)로 인해 포착되지 못함
  - MM의 경우 70% 이상의 번역이 모든 4개 GPU에 의해 공유됨
  - PR, ST의 경우 90% 이상 공유
  - 평균 45%의 재사용이 IOMMU TLB 용량(4096) 초과
- **관찰 3 (Obsv. 3):** 번역 재사용으로 동일 번역이 L2 TLB와 IOMMU TLB에 중복 저장되어 TLB reach 감소
  - MM의 경우 25%~70%의 엔트리가 L2 TLB와 IOMMU TLB 양쪽에 존재
  - PR의 경우 30%의 엔트리가 양쪽에 동시 존재

### 3.3. 다중 애플리케이션-다중 GPU 분석

- IOMMU TLB contention으로 개별 애플리케이션 성능 저하 발생
- W10(HHHH): 최대 **77.5%** 성능 하락
- W6(LLHH): AES(MPKI=0.003)는 15% 하락, MT(MPKI=2.394)는 **57%** 하락 — MPKI가 높은 앱이 더 큰 영향
- 동일 앱도 다른 워크로드에서 서로 다른 성능 저하를 보임: MT가 W6에서 57%, W9에서 **68%** 하락

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1. Least-Inclusive TLB 계층

- 기본 설계(mostly-inclusive)에서 IOMMU TLB miss 발생 시 번역이 IOMMU TLB, L2 TLB, L1 TLB 세 곳에 모두 저장됨 (중복)
- **least-TLB:** 번역을 L2 TLB에만 삽입하고, L2 TLB에서 eviction될 때만 IOMMU TLB에 spilling (IOMMU를 victim cache로 활용)
- 이렇게 하면 동일 번역의 중복 저장이 제거되어 **TLB reach(유효 용량)가 증가**

### 4.2. Local TLB Tracker (Cuckoo Filter 기반)

- IOMMU에 **Cuckoo filter** 기반 Local TLB tracker를 구현하여 모든 GPU의 L2 TLB에 존재하는 번역을 추적
- **lookup 과정 (Algorithm 1):**
  1. L2 TLB에서 먼저 탐색
  2. miss 시 IOMMU TLB와 Local TLB tracker를 병렬로 탐색
  3. IOMMU TLB 히트 시 → 번역을 L2 TLB로 복사하고 IOMMU TLB에서 제거 (least-inclusive 정책)
  4. Tracker 히트(다른 GPU의 L2 TLB에 존재) 시 → 해당 GPU에서 번역을 가져와 두 L2 TLB에 동시 저장
  5. 둘 다 miss 시 → PTW 수행 후 L2 TLB와 tracker에 저장
- **Cuckoo filter:** Bloom filter와 유사한 공간 효율적 데이터 구조. 삽입/삭제 지원. 오탐(false positive) 가능하나 이를 PTW로 처리

### 4.3. IOMMU TLB Spilling

- 다중 애플리케이션 실행에서 IOMMU TLB contention 완화를 위해, IOMMU에서 eviction된 번역을 적절한 GPU의 L2 TLB로 spilling
- **수신 GPU 선택:** Local TLB tracker의 hit rate를 기반으로 동적으로 선택 — 가장 적은 contention을 유발하는 GPU를 선택하여 spilling
- 이를 통해 IOMMU TLB의 효과적 용량이 증가하고 contention이 감소

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2024ISCA-summarize/improving-address-translation-in-multi-gpus.md|전체 요약 보기]]
