---
tags: [paper, 2018, 2018MICRO, topic/dram, topic/nvm, topic/storage]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/amber-enabling-precise-full-system-simulation-with-detailed-modeling-of-all-ssd-resources.md"
---

# Amber*: Enabling Precise Full-System Simulation with Detailed Modeling of All SSD Resources

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Donghyun Gouk, Miryeong Kwon, Jie Zhang, Sungjoon Koh, Wonil Choi, Nam Sung Kim, Mahmut Kandemir, Myoungsoo Jung (Yonsei University, Pennsylvania State University, University of Illinois Urbana-Champaign)

## 개요

- SSD는 모던 메모리 계층의 주요 스토리지 구성 요소로, 핸드헬드 및 범용 컴퓨팅 디바이스에서 대부분의 기존 디스크를 대체
- 서버 및 고성능 컴퓨터는 SSD를 캐시, 버스트 버퍼, 또는 QoS/SLA 충족을 위한 핫 데이터 저장소로 활용
- 시뮬레이션 기반 연구가 SSD의 전체 설계 공간 탐색에 필수적이지만, 풀시스템 시뮬레이션 환경에서 SSD 서브시스템을 모델링하는 것은 여러 어려움이 존재:
  1. **독립 시스템으로서의 SSD:** SSD는 자체 CPU, DRAM, 인터커넥트 네트워크를 갖춘 완전한 시스템 위에서 구현됨
  2. **하드웨어 병렬성:** SSD는 내장 CPU 코어, DRAM 모듈, 메모리 컨트롤러를 사용하며 호스트와 병렬로 운영
  3. **다양한 스토리지 인터페이스:** SATA, UFS, NVMe, Open-Channel SSD(OCSSD) 등 다양한 프로토콜 지원 필요
  4. **펌웨어 스택:** FTL(Flash Translation Layer), HIL(Host Interface Layer), DRAM 캐시 로직 등 다양한 소프트웨어 모듈 필요
- 기존 시뮬레이터의 한계:
  - **DiskSim:** 특정 플래시 펌웨어(FTL)의 기능만 캡처, SSD 하드웨어 리소스 미모델링
  - **최신 시뮬레이터들:** 연산 컴플렉스(computation complex) 모델 부재, 펌웨어 실행에 대한 상세 타이밍 시뮬레이션 불가
  - **기존 접근법:** 시스템 버스와 데이터 이동을 미모델링하여 풀시스템 환경에 통합 불가

## 방법론

### 3.1. SSD 내부 아키텍처 모델링

- **연산 컴플렉스(Computation Complex):**
  - 내장 CPU 코어: SSD 내부에서 펌웨어 실행 및 관리
  - DRAM 모듈: SSD 내부 캐시/버퍼 역할
  - 메모리 컨트롤러: CPU-DRAM 간 데이터 흐름 관리
- **스토리지 백엔드(Storage Backend):**
  - 다수의 플래시 패키지: 내부 시스템 버스를 통해 연결
  - 채널 및 웨이 기반 병렬 I/O 액세스
- **펌웨어 스택 (하위 레이어부터):**
  - **FIL (Flash Interface Layer):** 플래시 트랜잭션 스케줄링 및 병렬화
  - **FTL (Flash Translation Layer):** LBA→PPN 주소 변환, 가비지 컬렉션(GC), 웨어레벨링
  - **ICL (Internal Caching Layer):** DRAM 캐시 관리 (완전 연결, 세트 연결, 직접 매핑 등 다양한 캐시 구조 지원)
  - 모든 소프트웨어 모듈은 **재구성 가능(reconfigurable)**하여 다양한 SSD 디바이스 시뮬레이션 가능

### 3.2. 스토리지 인터페이스 지원

- **SATA:** 기존 SATA 프로토콜 에뮬레이션
- **UFS (Universal Flash Storage):** 모바일 디바이스용 인터페이스
- **NVMe (Non-Volatile Memory Express):** 고성능 스토리지 인터페이스
- **OCSSD (Open-Channel SSD) 1.2 및 2.0:**
  - 호스트 측 FTL(pblk) 및 드라이버(lightNVM) 구현
  - SSD 서브시스템에서 FTL/ICL을 데이터 경로에서 비활성화
  - chunk 관리, 메모리 레이턴시 데이터, erase count 정보 지원

### 3.3. 플래시 펌웨어 최적화

- **내부 캐싱(ICL) 최적화:**
  - 캐시 연관성, 페이지 교체 방식 등을 다양한 형태로 구성 가능
  - 읽기 성능 개선을 위한 플래시 내부 병렬성 인식 최적화
- **FTL 최적화:**
  - GC 알고리즘: Greedy, Cost-benefit 등 다양한 전략 지원
  - 웨어레벨링 알고리즘 통합
- **데이터 전송 에뮬레이션:**
  - 호스트 ↔ SSD 간 DMA 엔진 수정
  - gem5의 시스템 버스 수정으로 실제 데이터 흐름 에뮬레이션

### 3.4. 풀시스템 통합

- **gem5 수정:**
  - 모든 기능/타이밍 CPU 모델 지원
  - 호스트 DMA 엔진 수정으로 데이터 전송 에뮬레이션
  - 시스템 버스 수정으로 SSD ↔ 호스트 통신 지원
- **OS 지원:**
  - 다양한 OS (리눅스 등)에서 SSD 서브시스템을 풀시스템으로 시뮬레이션
  - 모바일 및 범용 컴퓨팅 플랫폼 지원

## 핵심 기여

- **핵심 기여:** 풀시스템 시뮬레이션 환경에서 SSD의 모든 하드웨어/소프트웨어 리소스를 정밀 모델링하는 Amber 프레임워크 제시
- **정확성:** 다양한 스토리지 인터페이스(SATA, UFS, NVMe, OCSSD)와 완전한 펌웨어 스택을 에뮬레이션하여 실제 SSD 동작을 정확히 캡처
- **실용성:** gem5와의 통합으로 모바일 및 범용 컴퓨팅 플랫폼에서의 SSD 영향을 체계적으로 분석 가능
- **의의:** SSD 연구 커뮤니티에 정밀한 풀시스템 시뮬레이션 인프라를 제공하여, SSD 설계空间 탐색의 정확도 향상
- **활성/패시브 스토리지:** Amber를 활용한 시스템 수준 비교 분석으로 향후 SSD 아키텍처 방향성 제시
- **오픈소스:** 소스 코드 공개로 재현성 및 확장성 보장

## 주요 결과

- **시뮬레이션 프레임워크:** gem5 기반, SimpleSSD 2.0 (Amber)로 명명
- **소스 코드:** https://simplessd.org 에서 다운로드 가능
- **플랫폼 지원:**
  - PC 플랫폼: Intel i7-4790K (X86), DDR4-2400 2채널
  - 모바일 플랫폼: NVIDIA Jetson TX2 (ARM v8), LPDDR4-3733 1채널
- **시스템 구성 (Table II):**
  - L1D/L1I 캐시: 프라이빗, 32KB, 8-way
  - L2 캐시: 프라이빗 256KB (PC) / 공유 2MB (모바일)
  - L3 캐시: 공유 8MB, 16-way (PC만 해당)
- **펌웨어 스택:** 완전한 FTL, ICL, HIL 구현

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/amber-enabling-precise-full-system-simulation-with-detailed-modeling-of-all-ssd-resources.md|전체 요약 보기]]
