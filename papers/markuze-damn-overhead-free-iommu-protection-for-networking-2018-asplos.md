---
tags: [paper, 2018, 2018ASPLOS, topic/security, topic/storage, iommu, dma, networking]
venue: "ASPLOS '18"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/damn-overhead-free-iommu-protection-for-networking.md"
---

# DAMN: Overhead-Free IOMMU Protection for Networking

**Venue:** 23rd International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '18)
**저자:** Alex Markuze, Igor Smolyar, Adam Morrison, Dan Tsafrir

## 개요

DAMN(DMA-Aware Malloc for Networking)은 IOMMU 기반 DMA 공격 보호에서 **보안과 성능의 트레이드오프를 제거**하는 새로운 보호 모델을 제시합니다. 기존 DMA API 수준이 아닌 사용자/커널 경계에서 보호를 제공하여 100Gb/s 네트워킹에서도 오버헤드 없는 보호를 구현합니다.

**핵심 문제:** 기존 IOMMU 보호 모델은 DMA API에서 버퍼 소유권을 전환하는데, 이는 보안과 성능 중 하나를 타협해야 함:
- Strict 보호: 매 DMA마다 IOTLB 무효화 → 처리량 58%
- Deferred 보호: 보안 취약窗口 존재
- Shadow buffers: CPU/메모리 대역폭 2배 소비

## 방법론

### 새로운 보호 모델
- **DMA API가 아닌 높은 수준에서 보호**: 패킷 데이터는 커널→사용자 복사 시 이미 커널 범위를 벗어남
- **영구 매핑된 메모리 풀**: DAMN이 할당한 버퍼는 항상 IOMMU에 매핑됨 → 매 DMA마다 매핑/해제 불필요
- **TOCTTOU 방어**: OS가 패킷 데이터에 처음 접근할 때만 해당 바이트를 복사

### 시스템 구조
- **DMA Cache**: 디바이스+권한 조합별 2계층 할당기 (하위: 청크 캐시, 상위: bump pointer)
- **Magazine 기반 캐싱**: per-core LIFO 스택으로 동기화 없이 빠른 할당
- **IOVA 인코딩**: 상위 비트에 코어/권한/디바이스 정보 저장

## 핵심 기여

1. **새로운 DMA 공격 보호 모델**: DMA API 수준이 아닌 높은 수준에서 보호 제공
2. **거의 오버헤드 없는 보호**: 네트워킹 성능에 미치는 영향 최소화
3. **100Gb/s NIC에서 실용적 검증**: 상용 하드웨어에서 동작
4. **비-networking 디바이스와 호환**: 기존 DMA API 보호와 공존 가능

## 주요 결과

- **단일 코어 RX**: DAMN 67Gb/s (unprotected 65Gb/s 대비 동등), shadow buffers 26Gb/s 대비 **2.7x 향상**
- **양방향 200Gb/s**: DAMN 171Gb/s (unprotected 196Gb/s 대비 87%), shadow buffers 160Gb/s
- **메모리 대역폭**: shadow buffers는 ≈80GB/s 고갈, DAMN은 절반 이하
- **CPU 사용률**: shadow buffers 대비 50% 감소
- **NVMe**: shadow buffers가 스토리지에 적합 (DAMN과 호환)

## 한계점

- zero-copy 경로(sendfile, IP 포워딩)에는 적용 불가 → 기존 DMA API로 폴백
- 커널 바이패스 애플리케이션(RDMA, DPDK)에는 직접 적용 불가
- 스토리지 디바이스와는 불호환 → 별도 보호 방식 필요

## 관련 개념

- [[paper-wiki/concepts/security.md|Security]] — DMA 공격 및 IOMMU 보호
- [[paper-wiki/concepts/storage.md|Storage]] — NVMe 및 스토리지 DMA
