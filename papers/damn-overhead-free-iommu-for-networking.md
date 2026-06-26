---
tags: [paper, 2018, 2018ASPLOS, topic/cache, topic/virtual-memory]
venue: "23rd International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '18)"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/damn-overhead-free-iommu-protection-for-networking.md"
---

# DAMN: Overhead-Free IOMMU Protection for Networking

**Venue:** 23rd International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '18)
**저자:** Alex Markuze (Technion – Israel Institute of Technology), Igor Smolyar (Technion – Israel Institute of Technology), Adam Morrison (Tel Aviv University), Dan Tsafrir (Technion – Israel Institute of Technology / VMware Research Group)

## 개요

- 현대 데이터센터 서버는 코어 수가 증가함에 따라 네트워킹 속도도 확장 필요 — Google Jupiter fabric은 40Gb/s 엔드포인트, 100Gb/s NIC 출시
- 악성/비정상 NIC의 DMA 공격으로부터 OS를 보호하기 위해 IOMMU 사용이 필수적
- 기존 IOMMU 보호 모델(DMA API 기반)의 **보안/성능 트레이드오프:**
  - **Strict 보호**: 매 DMA마다 IOTLB 무효화 → 100Gb/s에서 58% 처리량 달성 (unprotected 대비)
  - **Deferred 보호 (Linux 기본값)**: IOTLB 무효화 배치 → 보안 취약窗口 (TOCTTOU 공격 가능)
  - **Shadow buffers**: DMA 불가능한 버퍼로 패킷 복사 → CPU/메모리 대역폭 2배 소비, 메모리 대역폭 고갈로 80Gb/s에서 병목

- **핵심 문제**: DMA API 수준에서 보호를 제공하면 보안과 성능 중 하나를 타협해야 함
- 100Gb/s NIC 환경에서 shadow buffers는 메모리 대역폭(≈80GB/s)을 고갈시켜 NIC가 충분히 빠르게 링프를 비울 수 없음

## 방법론

### 3.1. 보호 모델 변경

- 기존: DMA API가 버퍼 소유권을 커널↔디바이스 간 전환
- 새로운: 영구 매핑된 버퍼에서 커널이 데이터에 접근할 때만 복사하여 보호
- **보안 보장:**
  - TX (송신): 읽기 전용 권한 → 디바이스가 민감한 데이터를 읽을 수 없음 (DAMN은 할당 시 메모리 0 초기화)
  - RX (수신): OS가 접근한 바이트를 복사하여 디바이스의 TOCTTOU 공격 방어

### 3.2. 메모리 할당기 (DMA Cache)

- **구조**: 디바이스 + 접근 권한(read/write) 조합별 DMA 캐시 유지
- **2계층 구조:**
  - 하위 계층: 물리 페이지 청크(chunk)를 IOMMU에 매핑하여 캐싱
  - 상위 계층: 코어별 bump pointer 할당기로 빠른 할당 지원

- **Magazine 기반 캐싱**: per-core LIFO 스택으로 동기화 없이 빠른 할당/해제
- **컨텍스트 분리**: 인터럽트 컨텍스트와 일반 컨텍스트용 별도 DMA 캐시 유지 → 인터럽트 비활성화 오버헤드 제거

### 3.3. IOMMU 매핑 관리

- **IOVA 인코딩**: 상위 비트에 코어, 접근 권한, 디바이스 정보를 인코딩 (Figure 3)
- **DMA API 호환**: dma_map/dma_unmap 호출을 가로채어 DAMN 할당 여부 확인
  - DAMN 버퍼: IOVA 반환 또는 즉시 반환 (매핑 해제 불필요)
  - 비-DAMN 버퍼: 기존 DMA API로 폴백

### 3.4. TOCTTOU 방어 메커니즘

- skbuff API를 가로채어 OS가 패킷 데이터에 처음 접근할 때마다 복사
- 일반적으로 패킷 헤더만 복사 → 오버헤드 최소화
- 전체 세그먼트를 복사해도 shadow buffers보다 10% 낮은 CPU 소비 (캐시 친화적 할당)

## 핵심 기여

- DAMN은 **보안과 성능의 트레이드오프를 제거**하는 새로운 DMA 공격 보호 모델 제시
- 100Gb/s NIC에서 unprotected 시스템의 90% 처리량 달성, 보호 모델 중 최고 성능
- Shadow buffers 대비 **7% 높은 처리량, 절반의 CPU 사용**
- 네트워킹에 최적화된 보호 모델로, 비-networking 디바이스와 호환 가능

## 주요 결과

- **구현 언어:** C (Linux 4.7 커널)
- **코드 라인 수:** ≈500 LOC (DAMN 구현) + ≈300 LOC (TCP 스택 통합)
- **구성 요소:**
  - DMA 캐시 구현: ≈250 LOC
  - Magazine 구현: ≈250 LOC
  - skbuff 코드 수정: 150 LOC
  - 프로토콜/소켓 코드 수정: 150 LOC

- **배포 용이성:** NIC 드라이버 수정 2 LOC로 가능, 비-networking 디바이스는 기존 DMA API 보호 유지

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2018ASPLOS-summarize/damn-overhead-free-iommu-protection-for-networking.md|전체 요약 보기]]
