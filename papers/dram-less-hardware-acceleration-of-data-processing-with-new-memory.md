---
tags: [paper, 2020, 2020HPCA, topic/dram, topic/gpu, topic/near-data-processing, topic/nvm, topic/pim, topic/storage]
venue: "IEEE International Symposium on High Performance Computer Architecture (HPCA '20)"
year: 2020
summary_path: "../paper-summaries/2020HPCA-summarize/dram-less-hardware-acceleration-of-data-processing-with-new-memory.md"
---

# DRAM-less: Hardware Acceleration of Data Processing with New Memory

**Venue:** IEEE International Symposium on High Performance Computer Architecture (HPCA '20)
**저자:** Jie Zhang, Gyuyoung Park, David Donofrio, John Shalf, Myoungsoo Jung (Korea Advanced Institute of Science and Technology (KAIST), Lawrence Berkeley National Laboratory)

## 개요

- 현대 하드웨어 가속기(GPU, MIC 등)는 수백~수천 개의 코어를 통해 CPU-only 대비 10배 이상의 성능을 제공하지만, 데이터 집약형 워크로드에서 SSD↔가속기 간 데이터 이동 오버헤드로 인해 심각한 성능 저하 발생
- 기존 가속 시스템에서 SSD에서 가속기로 데이터를 전송할 때 PCIe 인터커넥션과 소프트웨어 인터페이스 경계를 여러 번 통과해야 하며, 이 과정에서 상당한 에너지 소모 발생 (이상적 시스템 대비 평균 9배 더 많은 에너지 소비)
- 실험 결과, 기존 가속 시스템의 데이터 처리 성능은 이상적 환경(가속기 내부에 모든 데이터가 상주) 대비 최대 74%까지 저하됨
- 기존 솔루션(Active SSD, P2P DMA 등)은 소프트웨어 간섭, PCIe 전송 지연, 제한된 연산 유연성 등의 한계를 가짐
- 데이터 이동 비용이 연산 비용을 크게 초과하는 문제가 핵심 병목으로 부각

## 방법론

### 3.1. PRAM 마이크로아키텍처

- **스토리지 셀:** GST(GeSbTe) 소재의 상변화를 이용. ~300°C에서 결정화(SET, 저항 "1"), ~600°C 이상에서 비정질화(RESET, 고항 "0")
- **멀티 로우 버퍼:** 각 PRAM 모듈은 다수의 RAB(Row Address Buffer)와 RDB(Row Data Buffer)를 보유. LPDDR2-NVM 인터페이스로 노출
- **멀티 파티션 아키텍처:** 하나의 PRAM 뱅크에 16개 파티션이 존재하며, 각 파티션은 64개 서브어레이(resistive tile)로 구성
  - 각 타일은 2048 비트라인(BL)과 4096 워드라인(WL) 보유
  - 뱅크 레벨에서 256비트 병렬 I/O 지원
  - 반 파티션(half partition)당 64 I/O 동시 처리 가능

### 3.2. 메모리 인터페이스 프로토콜

- **쓰리페이즈 어드레싱 (Three-Phase Addressing):**
  - 프리액티브(Pre-active) 단계: BA 선택 신호로 RAB 선택, 상위 로우 주소 저장
  - 액티베이트(Activate) 단계: 하위 로우 주소 전송, 실제 로우 주소 조합, 로우 데이터를 RDB에 로드
  - 리드/라이트(Read/Write) 단계: RDB에서 특정 데이터 위치(컬럼 주소) 전달
- **오버레이 윈도우 & 프로그램 버퍼:** PRAM 스토리지 코어에 직접 쓰기를 시도하면 해당 모듈의 모든 동작이 일시 정지됨. 이를 해결하기 위해 특수 레지스터 세트(오버레이 윈도우)와 내부 버퍼(프로그램 버퍼)를 도입

### 3.3. 하드웨어 자동화 메모리 컨트롤러

- **FPGA 기반 구현:** Virtex-7 FPGA에서 400MHz PRAM PHY와 컨트롤러를 처음부터 구현
- **트랜슬레이터:** 32비트 주소와 모드 레지스터를 MCU에 노출. 오버레이 윈도우 관리
- **메모리 제어 로직:** 커맨드 생성기와 이니셔라이저로 구성
  - 커맨드 생성기: 쓰리페이즈 어드레싱과 LPDDR2 트랜잭션 처리
  - 이니셔라이저: PRAM 부팅, 온다임피던스 캘리브레이션, 버스트 길이 설정

### 3.4. PRAM-Aware 스케줄링 기법

- **멀티 리소스 어웨어 인터리빙 (Multi-Resource Aware Interleaving):**
  - PRAM의 멀티 파티션과 로우 버퍼를 인식한 요청 스케줄링
  - 하나의 파티션에서 데이터를 읽으면서 다른 RDB에서 캐시로 데이터 전송을 병렬 처리
  - 데이터 전송 시간을 파티션 접근 지연 시간 뒤에 숨김 (Figure 12 참조)
  - 인터리빙만으로 최대 54% 대역폭 향상 (trmm 기준)
- **셀렉티브 이레이싱 (Selective Erasing):**
  - PRAM 오버라이트 전에 오버라이트될 셀들을 미리 리셋(모두 0으로 프로그래밍)
  - 오버레이트 지연 시간을 55% 절감
  - erase 작업(약 60ms)의 3000배 짧은 지연으로 덮어쓰기 최적화
- **Final 조합 효과:** 인터리빙 + 셀렉티브 이레이싱 결합 시 Bare-metal 대비 평균 77% 대역폭 향상 (Figure 13)

### 3.5. 프로그래밍 및 커널 실행 모델

- 전용 PE가 커널 이미지를 처리하고 데이터 처리 태스크를 스케줄링
- 모든 PE가 PRAM에 직접 접근하므로 커널 실행마다 데이터를 전송할 필요 없음
- 기존 가속기의 호스트 측 소프트웨어 간섭 오버헤드 최소화

## 핵심 기여

- **핵심 기여:** PRAM을 가속기에 하드웨어 자동화로 통합하여 SSD↔가속기 간 데이터 이동 오버헤드를 근본적으로 제거하는 DRAM-less 아키텍처 제안
- **성능 향상:** 기존 고급 가속기(P2P DMA 기반) 대비 평균 47%, 액티브 스토리지 기반 대비 80% 성능 향상
- **에너지 효율:** 기존 가속 시스템의 19% 에너지만 소비하면서 동일 데이터 처리 가능
- **기술적 의의:** PRAM의 읽기/쓰기 비대칭성(읽기 100ns vs 쓰기 10μs)을 멀티 파티션 인터리빙과 셀렉티브 이레이싱으로 효과적으로 완화
- **한계 및 고찰:** PRAM의 실제 쓰기 지연 시간(10~18μs)이 DRAM(10ns) 대비 여전히 매우 길어, 모든 워크로드에서 일관된 이득을 보장하지는 않음. 또한 PRAM의 내구성(endurance) 문제가 장기적 사용 시 고려 필요

## 주요 결과

- **구현 언어/도구:** Virtex-7 FPGA (28nm 기술), TMS320C6 시리즈 호환 멀티코어 프로세서
- **PRAM 디바이스:** 3x nm 멀티 파티션 PRAM 엔지니어링 샘플 (실제 하드웨어)
- **가속기 플랫폼:** PCIe 기반 하드웨어 플랫폼에서 상용 멀티코어 프로세서 사용
- **스토리지 에뮬레이션:** 다양한 NVM 기술(Flash, PRAM 등)을 에뮬레이션하는 내부 스토리지 시스템
- **하드웨어 구성요소:** 400MHz PRAM PHY, FPGA 컨트롤러, 256비트 데이터패스 레지스터

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2020HPCA-summarize/dram-less-hardware-acceleration-of-data-processing-with-new-memory.md|전체 요약 보기]]
