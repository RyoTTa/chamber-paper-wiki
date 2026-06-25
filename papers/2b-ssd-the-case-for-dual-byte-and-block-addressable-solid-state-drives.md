---
tags: [paper, 2018, 2018ISCA, topic/storage, topic/nvm]
venue: "ISCA 2018"
year: 2018
summary_path: "../paper-summaries/2018ISCA-summarize/2b-ssd-the-case-for-dual-byte-and-block-addressable-solid-state-drives.md"
---

# 2B-SSD: The Case for Dual, Byte- and Block-Addressable Solid-State Drives

**Venue:** ISCA 2018
**저자:** Duck-Ho Bae, Insoon Jo, Youra Adel Choi, Joo-Young Hwang, Sangyeun Cho, Dong-Gi Lee, Jaeheon Jeong (Samsung Electronics)

## 개요

NVRAM은 배터리 백업 DRAM으로 구현되어 비용과 DIMM 슬롯을 차지하며 확장성이 제한적이다. Persistent Memory는 완전한 블록 스토리지 대체가 불가능하며, 블록 I/O와 바이트 접근이 분리되어 데이터 이동 오버헤드가 발생한다.

2B-SSD는 동일한 파일을 바이트 인터페이스와 블록 I/O의 두 독립 경로로 동시 접근 가능한 SSD 아키텍처이다. PCIe 인터페이스의 MMIO를 활용하여 DRAM 수준의 sub-1μs 쓰기 지연 시간을 달성하며, 1.2×~2.8× 처리량 향상을 보인다.

## 방법론

### 전체 구조
- SSD 내부 DRAM을 BA-buffer(Byte-Addressable buffer)로 활용하여 CPU가 MMIO로 직접 접근
- 주소 번역 하드웨어로 MMIO 주소 → BA-buffer 내부 주소 변환
- 블록 I/O 게이팅 하드웨어로 DRAM에 매핑된 NAND 페이지에 대한 블록 I/O 차단 → 일관성 보장

### 영속성 보장
- 캐퍼시터 백업으로 전원 차단 시 데이터 영속성 보장
- 쓰기 순서 보장: `clflush`+`mfence` (CPU WC buffer → root complex) + write-verify read (root complex → BA-buffer)

### 2B-SSD API
- `BA_PIN`, `BA_FLUSH`, `BA_SYNC`, `BA_GET_ENTRY_INFO`, `BA_READ_DMA`
- Linux ioctl 기반, 기존 블록 I/O 경로 변경 없음

### BA-WAL (데이터베이스 로깅)
- 기존 WAL의 작은 빈번한 쓰기 문제를 메모리 인터페이스로 해결
- 바이트 수준 읽기/쓰기, 즉시 영속성, WAF 감소

## 핵심 기여

1. 최초로 바이트 주소 지정과 블록 주소 지정을 동시에 지원하는 SSD 아키텍처
2. DRAM 수준의 sub-1μs 쓰기 지연 시간 달성
3. 하드웨어/소프트웨어 공존 설계로 기존 스택 변경 최소화

## 주요 결과

- **지연 시간**: 1KB 이하 쓰기 시 sub-1μs
- **처리량**: MySQL/MongoDB에서 1.2×~2.8× 향상
- **영속성**: 전원 차단 시 데이터 무손실 보장

## 한계점

- NVRAM 대비 확장성 우위는 있으나, 전체 메모리-스토리지 계층 재설계 필요
- PCIe 인터페이스의 바이트 주소 지정 기능에 대한 의존

## 관련 개념

- [[paper-wiki/concepts/storage.md|Storage]]
- [[paper-wiki/concepts/nvm.md|NVM]]
