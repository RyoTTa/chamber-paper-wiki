---
tags: [paper, 2018, 2018MICRO, topic/cache, topic/dram, topic/nvm]
venue: "51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)"
year: 2018
summary_path: "../paper-summaries/2018MICRO-summarize/picl-a-software-transparent-persistent-cache-log-for-nonvolatile-main-memory.md"
---

# PiCL: A Software-Transparent Persistent Cache Log for Nonvolatile Main Memory

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Tri M. Nguyen (Princeton University), David Wentzlaff (Princeton University)

## 개요

- NVMM(Nonvolatile Main Memory)은 바이트 주소 가능 NVM(Non-Volatile Memory) 제품(Intel 3D XPoint, NVDIMM-F/P/N)의 상용화로 점차 현실화
- NVMM은 즉시 복구, 높은 가용성을 제공하지만, **크래시 일관성(Crash Consistency)** 문제 해결이 필수적
- 캐시 계층은 메모리 접근을 재순서화하고 병합하여 전력 상실 시 메모리 불일치 유발
- **기존 소프트웨어 투명 방식의 한계:**
  - **캐시 플러시 오버헤드:** 대형 온칩 캐시(64MB+)에서 플러시 지연이 커밋 시간의 대부분을 차지 (2MB 캐시 → 약 1ms 플러시)
  - **동기적 플러시:** "stop-the-world" 방식으로 시스템 전체를 정지
  - **비순차적 로깅:** NVM의 랜덤 접근 성능(DRAM 대비 10배+)으로 인한 높은 비용
  - 기존 방식(ThyNVM 등)은 1.5~5.0배 성능 저하 발생

## 방법론

### 3.1. 멀티-언도 로깅(Multi-Undo Logging)

- 기존 언도 로깅의 확장: 여러 에포크의 동시 로깅 가능
- 캐시 라인에 Epoch ID(EID) 태깅으로 별도의 에포크 데이터를 동시에 추적
- **에포크 상태:**
  - Executing epoch: 미커밋 에포크 (SystemEID와 동일)
  - Committed epoch: 커밋되었으나 NVM에 미지속된 에포크
  - Persisted epoch: NVM에 완전히 기록된 에포크 (복구 기준점)

### 3.2. 캐시 기반 로깅(Cache-Driven Logging)

- 캐시 계층이 캐시 수정사항을 에포크 간 직접 추적
- **기존 언도 로깅의 read-log-modify 시퀀스를 우회:**
  - 기존: 캐시 미스 시 → 메모리에서 언도 데이터 읽기 → 언도 버퍼에 기록 → 캐시에 쓰기
  - PiCL: 크로스-에포크 쓰기 감지 시 → 언도 엔트리를 온칩 언도 버퍼에 저장 → 나중에 일괄 기록
- 캐시 미éviction 시 이전 에포크의 데이터를 언도 엔트리로 저장
- 온칩 언도 버퍼에서 대량의 엔트리를 순차적으로 NVM에 기록 → 랜덤 접근 최소화

### 3.3. 비동기 캐시 스캔(Asynchronous Cache Scan)

- 캐시 플러시를 크리티컬 패스에서 제거
- 캐시 스캔이 이전 에포크의 언도 데이터를 수집하는 동안 현재 에포크의 실행이 계속됨
- 언도 버퍼가 가득 차면 백그라운드에서 NVM으로 순차 기록
- 에포크 경계에서의 동기적 플러시를 제거하여 "stop-the-world" 오버헤드 해소

### 3.4. NVM과의 호환성

- DDR NVDIMM 인터페이스와의 호환성 유지
- 기존 캐시 교체 정책 변경 불필요
- 번역 테이블, NVM 캐시, 복잡한 NVM 컨트롤러 불필요
- 기존 상용 NVDIMM 장치와 직접 호환 가능

## 핵심 기여

- 소프트웨어 투명 크래시 일관성을 1% 미만의 성능 오버헤드로 구현하는 최초의 메커니즘
- 멀티-언도 로깅, 캐시 기반 로깅, 비동기 캐시 스캔의 조합으로 캐시 플러시와 랜덤 접근 문제를 동시에 해결
- FPGA 프로토타입을 통한 실현 가능성 검증
- NVMM의 즉시 복구 이점을 기존 소프트웨어와의 호환성으로 즉시 활용 가능하게 함

## 주요 결과

- **프로토타입:** OpenPiton 오픈소스 Manycore 프레임워크 기반 FPGA 구현
- **구현 언어:** Verilog
- **FPGA 보드:** Xilinx Genesys2
- **인터럽트 핸들러:** 완전한 프로토타입을 위한 인터럽트 처리 구현
- **에러 복구:** 합성(synthesis) 후 오버헤드 보고

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]


## 전체 요약

[[../paper-summaries/2018MICRO-summarize/picl-a-software-transparent-persistent-cache-log-for-nonvolatile-main-memory.md|전체 요약 보기]]
