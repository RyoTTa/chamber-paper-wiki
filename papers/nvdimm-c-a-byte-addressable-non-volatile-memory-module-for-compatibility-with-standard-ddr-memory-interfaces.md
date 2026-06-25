---
tags: [paper, 2020, 2020HPCA, topic/cache, topic/dram, topic/nvm, topic/storage]
venue: "IEEE International Symposium on High Performance Computer Architecture (HPCA) 2020"
year: 2020
summary_path: "../paper-summaries/2020HPCA-summarize/nvdimm-c-a-byte-addressable-non-volatile-memory-module-for-compatibility-with-standard-ddr-memory-interfaces.md"
---

# NVDIMM-C: A Byte-Addressable Non-Volatile Memory Module for Compatibility with Standard DDR Memory Interfaces

**Venue:** IEEE International Symposium on High Performance Computer Architecture (HPCA) 2020
**저자:** Changmin Lee, Wonjae Shin, Dae Jeong Kim, Yongjun Yu, Sung-Joon Kim, Taekyeong Ko, Deokho Seo, Jongmin Park, Kwanghee Lee, Seongho Choi, Namhyung Kim, Vishak G, Arun George, Vishwas V, Donghun Lee, Kangwoo Choi, Changbin Song, Dohan Kim, Insu Choi, Ilgyu Jung, Yong Ho Song, Jinman Han (Samsung Electronics, SAP Labs Korea)

## 개요

- 비volución 메모리(NVM) 기술(ReRAM, STT-MRAM, PRAM, FeRAM 등)은 DRAM과 경쟁적인 성능과 NAND 플래시와 경쟁적인 밀도를 제공하며, byte-addressable 특성으로 load/store 명령어를 통한 직접 접근이 가능
- 기존 NVDIMM 인터페이스로 Intel의 독자적인 DDR-T와 JEDEC의 NVDIMM-P가 존재하나, 기존 플랫폼에서 지원되지 않음 — 새 플랫폼 도입 비용이 크고 마이그레이션 효율 측정이 복잡
- Intel의 DCPMM(DC Persistent Memory Module)은 DDR4 288-pin DIMM 인터페이스를 사용하지만, 독자적인 DDR-T 통신 프로토콜을 사용하여 비결정적(non-deterministic) 동작을 지원 — 기존 DDR-T 메모리 컨트롤러가 없는 시스템과 호환 불가
- NVM 미디어의 non-deterministic 특성(쓰기 지연, 웨어레벨링, garbage collection 등)으로 인해 기존 DDR4 인터페이스의 결정적(deterministic) 타이밍 요구사항 충족이 어려움
- 최대 밀도 STT-MRAM(2019년 기준 1Gb)은 SCM으로서 부적합 — 고밀도 NVM 기술(NAND 등)을 사용하려면 타이밍 제약 해결 필요

## 방법론

### 3.1. DRAM-as-Frontend 구조

- NVDIMM 모듈의 프론트엔드에 DRAM 배치 — 호스트 iMC는 표준 DDR4 명령어로 DRAM에 직접 접근
- 백엔드 NVMC와 NVM 미디어는 DDR4 메모리 버스에서 물리적으로 분리 — 동기 도메인 외부에서 독립적 동작
- DRAM은 NVM 미디어의 캐시/버퍼 역할 — 캐시 히트 시 LLC로 직접 데이터 로드, 미스 시 NVMC가 NVM에서 DRAM 캐시로 데이터 로드
- BIOS, 타이밍 파라미터, OS 설계 등 기존 환경 그대로 유지 — 부팅 시 타이밍 위반 없음

### 3.2. tRFC 기반 버스 충돌 회피 메커니즘

- DRAM 리프레시 주기(tRFC) 동안 iMC가 어떤 명령도 발행하지 않음을 활용
- NVMC가 CA(Command/Address) 버스를 모니터링하여 iMC의 REFRESH 명령 감지
- tRFC 시간을 BIOS나 iMC 레지스터를 통해 조정하여 NVMC가 DRAM에 접근할 수 있는 시간 창 확보
- 두 가지 하드웨어 요구사항: (1) NVMC의 CA 버스 모니터링, (2) tRFC 시간의 프로그래밍 가능 설정
- 표준 DDR4 인터페이스와 프로토콜 수정 없이 다중 마스터 칩이 동일 메모리 버스를 공유 가능

### 3.3. NVMC 설계

- DDR4 컨트롤러 + NAND 컨트롤러를 통합 — DDR4 타이밍 파라미터는 호스트 시스템과 동일하게 구성
- NVM 미디어의 웨어레벨링, garbage collection, bad-block 관리 수행
- 4KB 그레뉼리티의 NAND 기본 연산(Read, Program, Erase) + ECC 적용
- Zynq MPSoC(Cortex-A53 MPCore) 기반 FPGA 구현 — 6x Deserializer로 DDR 클록 도메인 간 인터페이스 처리

### 3.4. 소프트웨어 스택 (nvdc driver)

- DAX(Direct Access) 인터페이스 지원 — page cache 우회하여 바이트 주소 접근
- DRAM 캐시 관리를 위한 소프트웨어 캐시 일관성 관리(clflush, sfence)
- 4KB 페이지 기준 Z-NAND-DRAM 매핑 관리
- Uncached 접근 시 writeback/cachefill 연산을 tRFC 윈도우에 맞춰 직렬화

## 핵심 기여

1. **기존 시스템 완전 호환 NVDIMM 아키텍처 최초 제안:** DDR4 인터페이스의 표준 프로토콜을 그대로 사용하면서 비volución 메모리 기능 제공 — pluggable 업그레이드 경로 제시
2. **tRFC 기반 버스 충돌 회피:** 하드웨어/프로토콜 수정 없이 다중 마스터가 동일 DRAM 버스를 공유하는 문제 해결 — 표준 DDR4 인터페이스의 refresh 타이밍 활용
3. **DRAM 캐시 히트 시 높은 성능:** 4KB random write 4615 MB/s (16 threads) — 현 SCM 요구사항 충족 가능
4. **NAND 기반 한계와 미디어 업그레이드 경로:** NAND로는 SCM 수준 불가 → STT-MRAM/PRAM(1.85us 이하) 사용 시 914 MB/s 달성 가능
5. **실물 PoC 검증:** FPGA 기반 PoC를 x86-64 서버에 설치하여 기존 환경 수정 없이 평가 — 상용화 가능성 입증

## 주요 결과

- **하드웨어:** Xilinx Zynq MPSoC 기반 FPGA PoC(Proof-of-Concept) 보드 — Cortex-A53 코어, 6x Deserializer, Z-NAND 컨트롤러 2개(CH0/CH1)
- **NVDIMM-C 보드:** DDR4 288-pin DIMM 폼팩터, DDR 클록 도메인의 물리 핀과 NVM 클록 도메인의 LPDDR4(펌웨어용) 탑재
- **소프트웨어:** Linux 커널의 nvdc 드라이버 — DAX-aware 파일 시스템 지원, 페이지 매핑 관리
- **평가 환경:** x86-64 서버 시스템, Intel Xeon 프로세서 — 기존 실행 환경 수정 없이 PoC 디바이스 설치 후 테스트

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2020HPCA-summarize/nvdimm-c-a-byte-addressable-non-volatile-memory-module-for-compatibility-with-standard-ddr-memory-interfaces.md|전체 요약 보기]]
