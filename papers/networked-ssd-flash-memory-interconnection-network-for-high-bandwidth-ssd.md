---
tags: [paper, 2022, 2022MICRO, topic/disaggregation, topic/dram, topic/nvm, topic/storage]
venue: "MICRO 2022 (55th IEEE/ACM International Symposium on Microarchitecture)"
year: 2022
summary_path: "../paper-summaries/2022MICRO-summarize/networked-ssd-flash-memory-interconnection-network-for-high-bandwidth-ssd.md"
---

# Networked SSD: Flash Memory Interconnection Network for High-Bandwidth SSD

**Venue:** MICRO 2022 (55th IEEE/ACM International Symposium on Microarchitecture)
**저자:** Jiho Kim (KAIST), Seokwon Kang (Hanyang University), Yongjun Park (Yonsei University), John Kim (KAIST)

## 개요

- NAND Flash 기반 SSD의 대역폭은 5년마다 약 10배씩 증가하고 있으나, Flash Memory 채널(인터커넥트) 대역폭은 10년마다 약 10배씩 증가하는 수준에 그쳐 병목이 심화 (Fig. 1)
- 현대 NV-DDR4 인터페이스의 18개 핀 중 데이터(DQ)에 사용되는 핀은 8개뿐이며, 나머지 10개는 제어 신호 전용으로 활용률이 낮음
- 채널당 연결된 Flash 칩 수가 증가(8~16개)하면서 채널 대역폭 병목이 전체 SSD 성능의 핵심 제약 요인으로 부상
- 기존 Flash-to-Flash 직접 통신이 불가능하여 Garbage Collection(GC)와 I/O 간의 간섭이 심각한 성능 저하를 유발

## 방법론

### 3.1. 패킷 기반 인터페이스 (Fig. 5)

- 기존: CLE, ALE, RE, WE 등 별도 제어 핀으로 데이터 타입 구분 → 핀 활용률 낮음
- pSSD: 기존 제어 핀을 패킷화에 활용하여 16비트 데이터 버스(기존 8비트 대비 2배 대역폭)
- 패킷 오버헤드: Flash 페이지 크기(16~64KB) 대비 패킷 헤더 비용은 상대적으로 작음
- Flash 컨트롤러와 온다이 컨트롤러에 패킷화 로직 추가, 내부 Flash 동작은 변경 없음

### 3.2. Omnibus 토폴로지 (Fig. 11)

- 수평 채널(h-channel): 기존 Flash 컨트롤러~Flash 칩 연결 유지
- 수직 채널(v-channel): 인접 칼럼의 Flash 칩 간 직접 통신 경로 추가
- 각 Flash 컨트롤러가 h-channel과 v-channel을 모두 관리
- 네트워크 직경이 작아 멀티홉 오버헤드 최소화 (기존 2D mesh 대비)

### 3.3. Split 전송 기법 (Fig. 14)

- 페이지 데이터를 2개 경로(h-channel + v-channel)로 분할 전송하여 대역폭 추가 향상
- pnSSD(+split)은 baseSSD 대비 82% 성능 향상 달성

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1. I/O 그룹과 GC 그룹 분리 (Fig. 12)

- Flash 메모리를 I/O 그룹과 GC 그룹으로 물리적 분리 (각 50%)
- I/O 그룹: 외부 트래픽(Read/Write) 처리
- GC 그룹: 내부 트래픽(GC page copy) 처리 → v-channel을 통해 직접 통신
- GC 완료 후 전체 Flash를 I/O에 활용, 다음 GC 시 그룹 교환(P/E 균등화)

### 4.2. 동시 I/O 및 GC 실행 (Fig. 13)

- 기존 병렬 GC: GC 중 I/O 서비스 불가
- 기존 SpGC(base SSD): 채널 공유로 간섭 여전
- pnSSD + SpGC: v-channel 격리로 I/O와 GC 간 간섭 최소화

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2022MICRO-summarize/networked-ssd-flash-memory-interconnection-network-for-high-bandwidth-ssd.md|전체 요약 보기]]
