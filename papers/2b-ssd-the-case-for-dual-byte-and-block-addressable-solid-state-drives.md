---
tags: [paper, 2018, 2018ISCA, topic/dram, topic/nvm, topic/storage]
venue: "45th Annual International Symposium on Computer Architecture (ISCA '18)"
year: 2018
summary_path: "../paper-summaries/2018ISCA-summarize/2b-ssd-the-case-for-dual-byte-and-block-addressable-solid-state-drives.md"
---

# 2B-SSD: The Case for Dual, Byte- and Block-Addressable Solid-State Drives

**Venue:** 45th Annual International Symposium on Computer Architecture (ISCA '18)
**저자:** Duck-Ho Bae, Insoon Jo, Youra Adel Choi, Joo-Young Hwang, Sangyeun Cho, Dong-Gi Lee, Jaeheon Jeong (Samsung Electronics Co., Ltd.)

## 개요

- 성능 중시 트랜잭션 및 스토리지 시스템은 쓰기 데이터의 빠른 영속성을 요구하며, 일반적으로 NVRAM(Non-Volatile RAM)을 사용하여 데이터 영속성을 보장
- 기존 NVRAM은 배터리 백업 DRAM으로 구현되며, DIMM 슬롯을 차지하고 비용이 크고 용량이 제한적 (4~16GB)
- Persistent Memory(PM) 기술이 주목받고 있으나, 완전한 블록 스토리지 대체는 불가능 — PM 용량 제한, DRAM과 PM 사이 접근 지연 시간 격차 존재
- 기존 메모리-스토리지 계층 구조의 한계:
  - PM 데이터는 블록 I/O로 접근 불가 → 전체 I/O 스택을 통한 디스태징(de-staging) 필요
  - NVRAM은 비용/면적/슬롯 문제로 확장성 제한
  - 블록 I/O와 바이트 접근 인터페이스가 분리되어 있어 데이터 이동 오버헤드 발생
- 핵심 문제: 블록 주소 지정과 바이트 주소 지정의 장점을 동시에 활용할 수 있는 하드웨어/소프트웨어 공존 설계 부재

## 방법론

### 3.1. 전체 구조 및 주소 번역

- **하이브리드 스토어 아키텍처**: SSD 내부 DRAM을 BA-buffer(Byte-Addressable buffer)로 활용
  - CPU가 MMIO를 통해 BA-buffer에 직접 접근
  - BA-buffer는 NAND 플래시의 캐시 역할 수행
- **주소 번역 하드웨어**: MMIO 주소 → BA-buffer 내부 주소로 변환
  - 펌웨어가 LBA(Logical Block Address)와 BA-buffer offset 간 매핑 관리
- **블록 I/O 게이팅 하드웨어**: DRAM에 매핑된 NAND 페이지에 대한 블록 I/O 요청을 차단하여 일관성 보장
  - 두 개의 독립 I/O 경로에서 동시에 같은 데이터를 접근하는 문제 방지

### 3.2. 영속성 보장 메커니즘

- **전원 차단 대비**: 캐퍼시터 백업으로 BA-buffer 데이터 영속성 보장
- **쓰기 순서 보장** (두 단계):
  1. **CPU WC buffer → Root Complex**: `clflush` + `mfence` 명령어로 WC buffer를 root complex로 플러시
  2. **Root Complex → BA-buffer**: "write-verify read" 연산 (0바이트 읽기)으로 쓰기 순서 강제
     - PCIe 메모리 쓰기는 "posted" 트랜잭션이므로 완료 대기 안 함
     - 읽기는 "non-posted" 트랜잭션 → 모든 선행 쓰기 커밋 보장

### 3.3. 2B-SSD API

| API | 기능 |
|-----|------|
| `BA_PIN(EID, offset, LBA, length)` | NAND 페이지를 BA-buffer로 가져와 핀ning + 매핑 테이블 엔트리 추가 |
| `BA_FLUSH(EID)` | BA-buffer 내용을 NAND로 동기화 (더티 데이터 플러시) |
| `BA_SYNC(EID)` | BA-buffer 내용의 영속성 보장 (clflush + mfence + write-verify read) |
| `BA_GET_ENTRY_INFO(EID)` | 매핑 테이블에서 EID 엔트리 상세 정보 조회 |
| `BA_READ_DMA(EID, dst, length)` | BA-buffer 내용을 DMA로 호스트 메모리로 복사 |

- Linux ioctl 기반 구현, 기존 블록 I/O 경로 변경 없음
- 응용 프로그램은 MMIO를 통해 BA-buffer에 직접 접근

### 3.4. 데이터베이스 로깅 사례 연구 (BA-WAL)

- **기존 WAL 문제**: 작은 빈번한 쓰기로 인한 성능 저하, NAND 쓰기 지연 시간, WAF(Write Amplification Factor) 증가
- **BA-WAL 장점**:
  - 바이트 수준 읽기/쓰기 → SSD 쓰기 부담 대폭 감소
  - BA-buffer에 기록 즉시 영속성 보장 (캐퍼시터 백업)
  - CPU 캐시 플러시 + write-verify read만 필요 → NAND 조작 오버헤드보다 훨씬 작음
  - WAF 감소: 여러 로그 페이지를 한 번에 NAND로 플러시
- **커밋 모드**: 동기 커밋, 비동기 커밋, BA 커밋 (새로운 모드)

## 핵심 기여

- **핵심 기여**: 최초로 바이트 주소 지정과 블록 주소 지정을 동시에 지원하는 SSD 아키텍처 제안
- **실용성**: 기존 NVMe SSD 하드웨어를 기반으로 구현 가능하며, 소프트웨어 스택 변경 최소화
- **성능**: DRAM 수준의 sub-1μs 쓰기 지연 시간, 1.2×~2.8× 처리량 향상
- **영속성**: 캐퍼시터 백업 + write-verify read로 전원 차단 시 데이터 무손실 보장
- **의의**: 메모리-스토리지 경계를 허무는 하이브리드 스토어 개념 제시 → 향후 Persistent Memory와 NAND 플래시의 융합에 대한 기반 연구

## 주요 결과

- **구현 플랫폼**: 상용 NVMe SSD 기반 프로토타입 구현
- **인터페이스**: PCIe, NVMe
- **소프트웨어 스택**: 커널 드라이버 + ioctl 기반 API, 파일 시스템 투과
- **하드웨어 구성 요소**:
  - 주소 번역 하드웨어
  - 블록 I/O 게이팅 하드웨어
  - 캐퍼시터 백업 전원 공급
  - 전원 차단 감지/복구 회로

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2018ISCA-summarize/2b-ssd-the-case-for-dual-byte-and-block-addressable-solid-state-drives.md|전체 요약 보기]]
