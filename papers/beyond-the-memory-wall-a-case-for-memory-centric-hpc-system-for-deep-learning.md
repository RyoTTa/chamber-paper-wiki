---
tags: [paper, 2018, 2018MICRO, topic/dram, topic/gpu]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/beyond-the-memory-wall-a-case-for-memory-centric-hpc-system-for-deep-learning.md"
---

# Beyond the Memory Wall: A Case for Memory-centric HPC System for Deep Learning

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Youngeun Kwon, Minsoo Rhu (KAIST)

## 개요

- 딥러닝 모델과 학습 데이터셋이 기하급수적으로 성장하여, DNN 학습의 핵심 제약은 모델 평가 속도와 학습에 사용 가능한 메모리 용량으로 변환
- 기존 디바이스 중심(DC-DLA) 아키텍처: GPU/TPU 디바이스 간 고대역폭 인터커넥트(NVLINK 등)를 사용하여 빠른 통신을 달성하지만, **메모리 "용량" 벽(capacity wall)**에 직면
  - 온패키지 3D 스택 메모리(HBM 등)의 용량 확장이 실리콘 인포저 와이어링, 칩 핀 아웃, 수직 통합 기술 한계로 어려움
- 호스트-디바이스 메모리 가상화(PCIe 기반)의 한계:
  - 디바이스 컴퓨팅 파워는 5년간 20-34배 향상된 반면, PCIe/InfiniBand 대역폭은 각각 1배/3.5배에 불과
  - 성능 오버헤드가 지속적으로 증가하는 추세 (Fig. 2)
  - 멀티 GPU/TPC 시스템에서는 디바이스당 유효 대역폭이 비례적으로 감소하여 더 큰 성능 저하

## 방법론

### 3.1. 시스템 구성요소

- **Device-Nodes:** GPU/TPU 가속기, 각각 NVLINK 링크 보유
- **Memory-Nodes:** 용량 최적화된 DRAM 모듈, 디바이스 사이드 인터커넥트에 로컬로 배치
- **디바이스 사이드 인터커넥트:** NVLINK 기반 고대역폭 링크로 가속기-메모리 노드 직접 연결
- **호스트 인터페이스:** MC-DLA는 PCIe를 통한 메모리 가상화를 사용하지 않음 → 호스트 의존성 제거

### 3.2. 링 기반 인터커넥트 설계

- **링 구조:** N개의 디바이스 노드와 N개의 메모리 노드를 3개의 링으로 구성 (N/2 = 3 링)
- **대역폭:** 각 디바이스 노드는 좌우 메모리 노드와 고대역폭 링크 연결
  - 디바이스당 메모리 접근 대역폭: **150 GB/sec** (8개 디바이스 × 150 GB/sec = 1200 GB/sec 총 대역폭)
  - 기존 PCIe 기반 DC-DLA의 CPU 소켓 메모리 대역폭(80-120 GB/sec)를 크게 초과
- **팩AGING 최적화:** 링 구조를 물리적으로 최적화하여 등간격 인터노드 링크 구현 (Fig. 8)

### 3.3. 소프트웨어 인터페이스

- **CUDA 런타임 API 확장:**
  - `cudaMallocRemote`: 디바이스 리모트 메모리 할당
  - `cudaFreeRemote`: 디바이스 리모트 메모리 해제
  - `cudaMemcpyAsync`: 방향 확장 (LocalToRemote, RemoteToLocal)
- **시스템 소프트웨어:**
  - 디바이스 드라이버가 디바이스 로컬 및 리모트 물리 메모리를 단일 디바이스 메모리 주소 공간으로 관리
  - 디바이스 로컬 메모리: 하위 주소 공간, 디바이스 리모트 메모리: 상위 주소 공간에 매핑
  - 기존 시스템 소프트웨어 API(mmap 등) 그대로 사용 가능
  - 대역폭 인식(BW_AWARE) 페이지 할당/배치 정책으로 고대역폭 채널 최대 활용

### 3.4. 메모리 용량 확장

- 현재 설계로 각 디바이스 노드에 최대 **1.3TB × 8 = 10.4TB**의 추가 물리 메모리 확장 가능
- 기존 GPU의 49비트 가상 주소(512TB), 47비트 물리 주소(128TB) 범위 내에서 충분히 수용

## 핵심 기여

- **핵심 기여:** 딥러닝 학습에서 메모리 용량 벽과 호스트-디바이스 통신 병목을 동시에 해결하는 MC-DLA 아키텍처 제시
- **성능:** DC-DLA 대비 2.8배 속도 향상, 수십 TB 메모리 용량 확장
- **의의:** 디바이스 사이드 인터커넥트의 중요성을 최초로 강조하고, 메모리 중심 아키텍처가 딥러닝 HPC의 차세대 방향임을 입증
- **실용성:** 기존 CUDA API 확장으로 기존 딥러닝 프레임워크와의 통합 용이
- **확장성:** NVLINK 대역폭 비례적 확장으로 차세대 가속기와의 호환성 보장

## 주요 결과

- **시뮬레이션 기반 평가**
- **소프트웨어 프레임워크:** 기존 DNN 메모리 가상화 솔루션((cudaMemcpyAsync) 기반 확장
- **하드웨어:** NVLINK 기반 디바이스 사이드 인터커넥트, 용량 최적화 DRAM 모듈
- **DNN 프레임워크:** 기존 딥러닝 프레임워크에서의 투명한 통합 지원

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/beyond-the-memory-wall-a-case-for-memory-centric-hpc-system-for-deep-learning.md|전체 요약 보기]]
