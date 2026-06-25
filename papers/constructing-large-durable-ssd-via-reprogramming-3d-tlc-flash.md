---
tags: [paper, 2019, 2019MICRO, topic/storage]
venue: "52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '19)"
year: 2019
summary_path: "../paper-summaries/2019MICRO-summarize/constructing-large-durable-and-fast-ssd-system-via-reprogramming-3d-tlc-flash-memory.md"
---

# Constructing Large, Durable and Fast SSD System via Reprogramming 3D TLC Flash Memory

**Venue:** 52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '19)
**저자:** Congming Gao (Chongqing University, University of Pittsburgh), Min Ye (YEESTOR Microelectronics), Qiao Li (City University of Hong Kong), Chun Jason Xue (City University of Hong Kong), Youtao Zhang (University of Pittsburgh), Liang Shi (East China Normal University), Jun Yang (University of Pittsburgh)

## 개요

- 3D NAND flash SSD는 적층 레이어 수를 늘려 밀도를 높이지만, 셀당 비트 수를 늘리면(TLC: 3-bit/cell) 내구성과 접근 지연 시간이 크게 악화
- 3D TLC SSD의 한 셀은 8개 전압 상태(ER, P1~P7)를 사용하여 3비트를 표현하며, 셀 간 전압 범위가 좁아 재프로그래밍(reprogramming) 적용이 어려움
- Garbage Collection(GC)는 SSD의 성능과 내구성을 크게 저하시키는 주요 병목: 유효 페이지 마이그레이션 비용이 높고,多次 erase 연산은 셀 마모를 가속
- RAID 5 시스템에서는 Stripe와 Parity Protection으로 인해 쓰기 증폭이 발생: 평균 parity 쓰기가 전체 사용자 쓰기의 88.1%에 달하며, parity 업데이트 간격이 사용자 데이터 대비 32.3% 짧음
- 2D NAND flash에서는 재프로그래밍이 연구되었으나, 3D TLC의 경우 전압 상태 간 간격이 좁고 신뢰성 문제가 있어 기존 기법을 직접 적용할 수 없음
- 핵심 문제: **3D TLC SSD에서 재프로그래밍을 통해 용량, 내구성, 성능을 동시에 향상시키는 것**

## 방법론

### 3.1. 재프로그래밍 가능성 검증 (3D TLC)

- **실물 3D TLC NAND flash 검증:** YEESTOR 9083 플래시 메모리 테스트 플랫폼과 Micron B17A 시리즈 칩으로 재프로그래밍 가능성 실험
- **OLR (One-Layer Reprogram):** 한 레이어 내 word line을 랜덤 순서로 재프로그래밍 → 최대 비트 에러: 10 (OVO 기준), 평균 비트 에러: 2 → 현대 SSD의 ECC(80 bits/1KB)로 교정 가능
- **MLR (Multi-Layer Reprogram):** 2개 물리 레이어를 하나의 재프로그래밍 가능 슈퍼 레이어로 구성 → 최대 비트 에러: 46, 평균 비트 에러: 9 → ECC로 교정 가능
- **MLR 3레이어 이상:** 최대 비트 에러 234, 평균 비트 에러 11 → ECC로 교정 불가능하므로 최대 2레이어로 제한
- **신뢰성 주요 원인:** Cell-to-Cell Interference와 Background Pattern Dependency(BPD)가 주요 에러 소스; BPD가 지배적

### 3.2. 전압 상태 배열 및 재프로그래밍 절차

- **초기 프로그래밍:** TLC를 MLC 모드로 프로그래밍 (ER~P3 상태 사용, 2비트 저장)
- **4가지 재프로그래밍 시나리오:**
  - LSB/LSB: LSB가 먼저 무효화된 후 LSB 업데이트
  - LSB/MSB: LSB 무효화 후 MSB 업데이트
  - MSB/MSB: MSB가 먼저 무효화된 후 MSB 업데이트
  - MSB/LSB: MSB 무효화 후 LSB 업데이트
- **메타데이터:** Distribution ID(2비트, 현재 전압 분포 식별), RPCnt(2비트, 재프로그래밍 횟수 기록, "10"이면 재프로그래밍 금지), Validity(2비트, LSB/MSB 유효성)
- **상태 전이:** 예: 초기 "00" 상태 → LSB 무효화 → "01"로 업데이트 (P5 상태로 전압 이동) → MSB 무효화 → "00" 재프로그래밍 (P6 상태)
- 셀당 총 4비트 정보 저장 가능 (초기 2비트 + 재프로그래밍 2회)

### 3.3. ReSSD 시스템 아키텍처

- **Hotness Filter:** 쓰기 요청의 핫NESS를 4단계로 분류 (30분, 60분, 120분 기준 업데이트 간격)
  - Rule 1: 업데이트된 요청만 핫 쓰기로 선택
  - Rule 2: 유사한 핫NESS를 가진 데이터를 같은 블록에 배치
- **블록 유형:**
  - Normal Block: 일반 TLC 프로그래밍
  - Repro. Block: 재프로그래밍 가능한 블록 (슈퍼 레이어 단위)
- **슈퍼 레이어 관리:** 하나의 슈퍼 레이어가 가득 차면 다음 슈퍼 레이어 활성화
- **Candidate Block:** 유효 페이지가 모두 무효화된 후 재프로그래밍 가능한 블록으로 전환
- **Fully Invalidated:** 콜드 데이터를 일반 TLC 블록으로 사전 마이그레이션하여 재프로그래밍 블록 확보

### 3.4. 오버헤드 분석

- **메타데이터 공간:** 576GB SSD 기준 총 10MB 미만 (블록 타임스탬프 384KB + 핫NESS/블록 태그 36KB + 포인터 432B + 워드라인 상태 9MB)
- **매핑 저장 공간 절감:** 재프로그래밍 블록은 페이지가 2개뿐이므로 매핑 엔트리 절반 절약 → 12개 블록이면 추가 공간 비용 상쇄
- **재프로그램 지연 시간:** 일반 프로그래밍보다 적은 전압 상태로 인해 charging cycle 감소 → 추가 읽기 오버헤드 포함해도 일반 프로그래밍보다 빠름

## 핵심 기여

- **핵심 기여:** 3D TLC NAND flash에서의 재프로그래밍 가능성을 **실물 칩 실험으로 최초 검증**
- **ReSSD 시스템:** 선택적 재프로그래밍을 통해 SSD의 용량, 내구성, 성능을 동시에 향상시키는 실용적 설계
- **성능 향상 수치:** 내구성 **30.3% 향상**, 쓰기 성능 **16.7% 향상**, 유효 용량 **7.71% 증가**
- **RAID 5 적용:** parity 쓰기 증폭이 심한 RAID 5 환경에서 특히 효과적 → GC 시간 **48.3% 감소**
- **오버헤드:** 메타데이터 10MB 미만, 재프로그램 지연 시간이 일반 프로그래밍보다 작음
- 메모리 용량 확장이 어려운 3D NAND flash의 한계를 소프트웨어-하드웨어 협력으로 극복하는 실용적 방안 제시

## 주요 결과

- **시뮬레이션 기반:** SSDSim 워크로드 기반 flash 메모리 시뮬레이터 사용
- **변경 사항:** one-shot programming 구현, 여러 ReSSD SSD를 RAID 5로 구성 (Linux Kernel 5.0.2 /drivers/md/ 기반)
- **FTL:** Page mapping 기반 flash translation layer
- **GC:** Greedy 기반 garbage collection
- **Wear Leveling:** Static wear leveling
- **테스트 플랫폼:** YEESTOR 9083 flash memory testing platform + Micron B17A 3D TLC NAND flash chips
- **워크로드:** MSRC Cambridge 워크로드 15개 (RAID 5 parity 요청 포함)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2019MICRO-summarize/constructing-large-durable-and-fast-ssd-system-via-reprogramming-3d-tlc-flash-memory.md|전체 요약 보기]]
