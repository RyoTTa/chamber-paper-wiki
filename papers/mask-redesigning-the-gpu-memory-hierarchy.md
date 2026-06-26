---
tags: [paper, 2018, 2018ASPLOS, topic/gpu, topic/virtual-memory]
venue: "ASPLOS 2018 (Architectural Support for Programming Languages and Operating Systems)"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/mask-redesigning-the-gpu-memory-hierarchy-to-support-multi-application-concurrency.md"
---

# MASK: Redesigning the GPU Memory Hierarchy to Support Multi-Application Concurrency

**Venue:** ASPLOS 2018 (Architectural Support for Programming Languages and Operating Systems)
**저자:** Rachata Ausavarungnirun, Vance Miller, Joshua Landgraf, Saugata Ghose, Jayneel Gandhi, Adwait Jog, Christopher J. Rossbach, Onur Mutlu (Carnegie Mellon University, University of Texas at Austin, VMware Research, College of William and Mary, ETH Zürich)

## 개요

- GPU는 높은 스레드 수준 병렬성을 활용하여 높은 명령 처리량을 제공하지만, 현대 컴퓨팅 환경에서 여러 애플리케이션이 GPU를 공유해야 하는 요구 증가
- 대규모 컴퓨팅 환경(클라우드 서버 등)에서 다양한 애플리케이션의 연산 및 메모리 요구사항을 효율적으로 수용하기 위해 멀티 애플리케이션 동시 실행 필요
- 현대 GPU는 CPU에서 사용 가능한 멀티 애플리케이션 동시 실행 지원이 부족하여 공유 시 높은 성능 오버헤드 발생
- 가상 메모리 메커니즘의Poor한 성능이 GPU 공유의 주요 장애물
- 최신 주소 변환 메커니즘이 단일 애플리케이션 실행용으로 설계되어 여러 애플리케이션이 공간적으로 GPU를 공유할 때 상당한 애플리케이션 간 간섭 발생
- 공유된 TLB(Translation Lookaside Buffer)에서의 빈번한 미스가 수백 개의 스레드에 장시간 지연STALL을 유발

## 방법론

### 3.1. 토큰 기반 TLB 경합 감소 기법

- 여러 애플리케이션이 공유하는 TLB에서의 경합을 줄이기 위한 토큰 기반 접근법
- 애플리케이션별 토큰 할당을 통해 TLB 리소스를 효율적으로 관리
- TLB 미스로 인한 장시간 지연을 최소화

### 3.2. 주소 변환 캐시 우회 메커니즘

- 캐시된 주소 변환의 효율성을 향상시키는 우회 메커니즘
- 불필요한 주소 변환 작업을 우회하여 성능 오버헤드 감소
- 메모리 접근 패턴을 분석하여 최적의 우회 결정

### 3.3. 애플리케이션 인식 메모리 스케줄링

- 주소 변환과 데이터 요청 간의 간섭을 줄이기 위한 스케줄링 체계
- 애플리케이션의 메모리 접근 특성을 고려한 동적 스케줄링
- 메모리 대역폭 효율성을 극대화

## 핵심 기여

- 현대 GPU의 가상 메모리 메커니즘이 멀티 애플리케이션 동시 실행 시 주요 성능 병목임을 규명
- MASK는 주소 변환을 인식한 통합 프레임워크를 통해 GPU 공유 성능을 크게 향상
- 대규모 컴퓨팅 환경에서의 GPU 효율적인 활용을 위한 실용적인 접근법 제시
-未来的 GPU 아키텍처 설계에 중요한 시사점을 제공

---

## 참고 자료

- 논문 원문: `/home/ryotta205/Chamber_paper/paper-source/2018ASPLOS/MASK_Redesigning_the_GPU_Memory_Hierarchy.pdf`
- 관련 개념: GPU, Virtual Memory, TLB, Multi-Application Concurrency, Memory Management

## 주요 결과

- GPU 아키텍처 수준에서의 하드웨어 지원 필요
- 기존 GPU 메모리 계층 구조의 확장 및 수정
- 소프트웨어 드라이버 및 런타임 지원
- 가상화 레이어와의 통합

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2018ASPLOS-summarize/mask-redesigning-the-gpu-memory-hierarchy-to-support-multi-application-concurrency.md|전체 요약 보기]]
