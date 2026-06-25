---
tags: [paper, 2018, 2018ASPLOS, topic/gpu, topic/virtual-memory]
venue: "ASPLOS 2018"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/mask-redesigning-the-gpu-memory-hierarchy-to-support-multi-application-concurrency.md"
---

# MASK: Redesigning the GPU Memory Hierarchy to Support Multi-Application Concurrency

**Venue:** ASPLOS 2018
**저자:** Rachata Ausavarungnirun, Vance Miller, Joshua Landgraf, Saugata Ghose, Jayneel Gandhi, Adwait Jog, Christopher J. Rossbach, Onur Mutlu (Carnegie Mellon University, University of Texas at Austin, VMware Research, College of William and Mary, ETH Zürich)

## 개요

GPU는 높은 스레드 수준 병렬성을 활용하지만, 현대 컴퓨팅 환경에서 여러 애플리케이션이 GPU를 공유해야 하는 요구 증가. 현대 GPU는 CPU에서 사용 가능한 멀티 애플리케이션 동시 실행 지원이 부족하여 공유 시 높은 성능 오버헤드 발생.

MASK는 주소 변환을 인식한 캐시 및 메모리 관리 메커니즘을 통해 GPU 공유 성능을 크게 향상하는 프레임워크로, 시스템 처리량 57.8% 향상, IPC 처리량 43.4% 향상, 애플리케이션 수준 불공정성 22.4% 감소를 달성.

## 방법론

### 토큰 기반 TLB 경합 감소 기법
- 여러 애플리케이션이 공유하는 TLB에서의 경합을 줄이기 위한 토큰 기반 접근법
- 애플리케이션별 토큰 할당을 통해 TLB 리소스를 효율적으로 관리

### 주소 변환 캐시 우회 메커니즘
- 캐시된 주소 변환의 효율성을 향상시키는 우회 메커니즘
- 불필요한 주소 변환 작업을 우회하여 성능 오버헤드 감소

### 애플리케이션 인식 메모리 스케줄링
- 주소 변환과 데이터 요청 간의 간섭을 줄이기 위한 스케줄링 체계
- 애플리케이션의 메모리 접근 특성을 고려한 동적 스케줄링

## 핵심 기여

1. 현대 GPU의 가상 메모리 메커니즘이 멀티 애플리케이션 동시 실행 시 주요 성능 병목임을 규명
2. 주소 변환을 인식한 통합 프레임워크를 통한 GPU 공유 성능 크게 향상
3. 대규모 컴퓨팅 환경에서의 GPU 효율적인 활용을 위한 실용적인 접근법

## 주요 결과

- 시스템 처리량 57.8% 향상
- IPC(Instructions Per Cycle) 처리량 43.4% 향상
- 애플리케이션 수준 불공정성 22.4% 감소
- 주소 변환 오버헤드가 없는 이상적인 GPU 시스템 대비 처리량이 23.2% 이내로 회복

## 한계점

- GPU 아키텍처 수준 하드웨어 지원 필요로 구현 복잡성 증가
- 특정 GPU 아키텍처에 최적화되어 다른 아키텍처에서의 일반화 미검증
- 소프트웨어 드라이버 및 런타임 지원과의 통합 복잡성

---

**Related Concepts:** [[paper-wiki/concepts/gpu|GPU]], [[paper-wiki/concepts/virtual-memory|Virtual Memory]], [[paper-wiki/concepts/tlb|TLB]]