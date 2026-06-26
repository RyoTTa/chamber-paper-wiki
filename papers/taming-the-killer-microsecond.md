---
tags: [paper, 2018, 2018MICRO, topic/dram, topic/nvm, topic/storage]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/taming-the-killer-microsecond.md"
---

# Taming the Killer Microsecond

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Shenghsun Cho, Amoghavarsha Suresh, Tapti Palit, Michael Ferdman, Nima Honarmand (Stony Brook University)

## 개요

- 현대 애플리케이션은 대규모 데이터셋에 대한 저지연(low latency) 접근을 요구함 (웹 검색, 광고, 머신 번역, 과학적 분석, 금융 분석 등).
- Flash 메모리(수십 마이크로초), 3D XPoint(수백 나노초), Infiniband/Ethernet(단일 자릿수 마이크로초)와 같은 새로운 메모리 기술들이 등장.
- **"Killer Microsecond" 문제:** 마이크로초 수준의 지연 시간을 기존 하드웨어/소프트웨어 지연 시간 숨김 기술로 효과적으로 숨길 수 없음.
  - 나노초 수준 기술(캐시, DRAM): 하드웨어 기반 지연 시간 숨김 (캐시, 프리페칭, 아웃오브더더 오더 실행 등)이 효과적.
  - 밀리초 수준 기술(디스크, 네트워크): OS 기반 컨텍스트 스위칭으로 효과적.
  - **마이크로초 수준:** 위 두 기술 모두 효과적이지 않은 갭(gap) 영역.
- 기존 마이크로아키텍처 기술은 마이크로초 지연을 효과적으로 숨길 수 없으며, 특히 포인터 기반 직렬 의존 체인(serial dependence chain)이 있는 워크로드에서 심각한 성능 저하 발생.
- OS 기반 메커니즘 자체가 수 마이크로초의 오버헤드를 발생시켜, 저지연 디바이스의 이점을 상실.

## 방법론

### 3.1. FPGA 기반 스토리지 디바이스 에뮬레이터

- **목적:** 마이크로초 수준 지연을 가진 스토리지 디바이스를 에뮬레이션.
- **구성:** Xilinx Virtex-7 FPGA 기반, PCIe 인터페이스.
- **기능:** 
  - 지연 시간을 자유롭게 조절 가능 (나노초~밀리초)
  - 다양한 디바이스 인터페이싱 메커니즘 지원 (큐 기반, 메모리 매핑 등)
  - 커스텀 스토리지 디바이스 드라이버 통합

### 3.2. 마이크로벤치마크 설계

- **파라미터:** 
  - MLP(Memory-Level Parallelism): 동시에 진행되는 메모리 접근 수
  - 계산-메모리 명령 비율(compute-to-memory instruction ratio)
- **목적:** 데이터 집약적 애플리케이션의 성능에 영향을 미치는 두 가지 주요 요인을 분리하여 연구.

### 3.3. 분석 대상 플랫폼

- Intel Xeon 기반 최신 서버 플랫폼
- 다양한 지연 시간 숨김 메커니즘의 효과를 정량적으로 분석

## 핵심 기여

- **Killer Microsecond 문제의 정량적 분석:** 기존 시스템이 마이크로초 지연을 숨길 수 없는 이유를 최초로 정량적으로 분석.
- **핵심 발견:** 급진적 아키텍처 변경 불필요. 단순한 하드웨어/소프트웨어 수정으로 충분.
- **해결책:** 프리페치 기반 접근 + 빠른 사용자 모드 컨텍스트 스위칭 + 하드웨어 큐 확장.
- **디자인 시사점:** 
  - 마이크로초 지연 디바이스는 메모리 매핑 방식으로 접근해야 함.
  - NVMe/RDMA 스타일의 큐 기반 인터페이스는 확장 불가능.
- **의의:** Killer Microsecond 문제에 대한 직관적 이해를 넘어, 실硬件 플랫폼을 이용한 정량적 분석을 통해 실제 해결책을 제시한 최초의 연구.

## 주요 결과

### 4.1. 기존 시스템의 병목 분석

- **큐 기반 인터페이스의 한계:** NVMe, RDMA 장치에서 사용되는 소프트웨어 관리 큐 기반 인터페이스는 마이크로초 지연 디바이스에 확장 불가능.
- **하드웨어 큐 크기 부족:** 기존 프리페치 큐, LOD 큐 등이 마이크로초 지연을 처리하기에 부족.
- **컨텍스트 스위칭 오버헤드:** OS 기반 컨텍스트 스위칭은 수 마이크로초 소요되어 마이크로초 지연 디바이스의 이점을 상실.

### 4.2. 제안 해결책

1. **프리페치 기반 접근:**
   - 온디맨드 접근을 프리페치 명령으로 변경
   - 접근 수준 병렬성(access-level parallelism)을 증가시켜 지연 시간 숨김.

2. **사용자 모드 컨텍스트 스위칭:**
   - 빠른 사용자 모드 컨텍스트 스위칭으로 오버헤드 최소화.
   - 하드웨어 멀티스레딩과 결합하여 효과적인 지연 시간 숨김.

3. **하드웨어 큐 확장:**
   - 진행 중인(in-flight) 메모리 접근을 추적하는 하드웨어 구조물의 크기 적절히 조정.
   - 프리페치 큐, LOD 큐 등의 깊이 증가.

4. **메모리 매핑 인터페이스:**
   - 큐 기반 대신 메모리 매핑 방식으로 디바이스 접근.
   - 로드/스토어/프리페치 명령을 통한 직접 접근.
   - QPI 링크나 DDR 버스와 같은 저지연 인터페이스에 연결.

### 4.3. 검증

- 3개 오픈소스 데이터 집약적 애플리케이션으로 검증.
- 마이크로벤치마크와 동일한 일반적 트렌드를 따르며 동일한 병목 현상에 직면.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/taming-the-killer-microsecond.md|전체 요약 보기]]
