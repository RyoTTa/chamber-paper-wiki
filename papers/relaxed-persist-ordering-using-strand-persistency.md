---
tags: [paper, 2020, 2020ISCA, topic/cache, topic/dram, topic/nvm, topic/storage]
venue: "2020 ACM/IEEE 47th Annual International Symposium on Computer Architecture (ISCA 2020)"
year: 2020
summary_path: "../paper-summaries/2020ISCA-summarize/relaxed-persist-ordering-using-strand-persistency.md"
---

# Relaxed Persist Ordering Using Strand Persistency

**Venue:** 2020 ACM/IEEE 47th Annual International Symposium on Computer Architecture (ISCA 2020)
**저자:** Vaibhav Gogte, Peter M. Chen, William Wang, Satish Narayanasamy, Stephan Diestelhorst, Thomas F. Wenisch (University of Michigan, USA; Arm Research, UK; Xilinx DCG, UK)

## 개요

- 지속성 메모리(Persistent Memory, PM) 기술(예: Intel Optane DC)은 DRAM 수준의 성능과 Flash의 내구성을 결합하지만, 효율적인 프로그래밍을 위한 persistency 모델이 필수적.
- 기존 언어 수준 persistency 모델(ATLAS, SFR, 트랜잭션 기반 모델)은 C++의 일반 동기화 프리미티브를 활용하여 PM 연산의 순서와 실패 원자성(failure atomicity)을 정의.
- 그러나 실제 하드웨어 ISA 수준의 persistency 메커니즘은 언어 수준 모델이 요구하는 것보다 훨씬 엄격한 ordering 제약을 부과. 예: Intel x86의 SFENCE 명령은 후속 CLWB와 store의 시각화(visibility)를 이전 CLWB 완료까지 차단.
- **SFENCE의 한계**: epoch persistency 모델 내에서만 재배열 허용. 독립적인但在 다른 epoch에 속하는 persist는 동시 처리 불가. Figure 1(e-g)에서 보듯 Persist C는 A, B와 동시에 처리 가능하지만, epoch 경계에 의해 순서화됨.
- 기존 하드웨어 로깅 메커니즘(Doshi et al., ATOM, FIRM 등)은 고정적이고 유연하지 못한 하드웨어로, 진화하는 언어 수준 persistency 모델에 적용 불가.
- 언어 수준 모델의 컴파일러 최적화도 메모리 의존성 분석의 어려움으로 persist 연산을 효과적으로 병합하지 못함.

## 방법론

### 3.1. 마이크로아키텍처 구조

- **Persist queue**: load-store queue(LSQ) 옆에 구현. CLWB와 store가 persist barrier 또는 JoinStrand에 의해 순서화되어 L1 캐시로_issue되도록 보장.
- **Strand buffer unit**: L1 캐시 인접. 다수의 strand buffer로 구성. 서로 다른 strand에서 CLWB를 동시에 issue하여 PM으로 병렬 드레인 가능.
  - 각 strand buffer는 해당 strand 내에서 persist barrier에 의해 persist 순서를 보장.
  - 캐시 코히런스 메시지를 추적하여 inter-thread persist 의존성 처리.
- **Write-back buffer / Snoop buffer 확장**: 각 엔트리에 8비트 추가 (strand buffer index 기록용). strand buffer unit과의 인터페이스 처리.

### 3.2. Persist Ordering 동작 원리

- **Intra-strand ordering**: Persist barrier로 분리된 두 persist는 동일 strand에서 순서화됨. NewStrand 이후의 persist는 이전 barrier의 ordering에서 해방됨.
- **Inter-strand ordering**: JoinStrand은 이전 strand들의 persist 완료를 보장한 후 후속 persist를 허용. Figure 2(c,d)에서 JS 이후의 persist C는 A, B 완료 후에만 issues.
- **Strong persist atomicity (SPA)**: 동일 또는 겹치는 PM 위치에 대한 persist는 가시성 순서(consistency model)를 따름. 이는 recovery 시 잘못된 순서 관찰을 방지.
- **Inter-thread persist ordering**: 동기화 프리미티브(lock/unlock)는 happens-before 관계를 설정하지만 persist 순서는 보장하지 않음. JoinStrand을 lock/unlock 전후에 배치하여 해결.

### 3.3. 언어 수준 Persistency 모델 통합

- **Undo logging 메커니즘**: StrandWeaver의 프리미티브를 활용하여 로그와 in-place 업데이트 간 최소 순서 제약만 부과.
  - 각 로그-업데이트 쌍은 별도 strand에서 수행 (NewStrand으로 분리)
  - Persist barrier로 로그가 해당 업데이트보다 먼저 persist되도록 보장
  - Failure-atomic region의 시작과 끝은 JoinStrand으로 감싸서 region 내 모든 persist 완료 보장
- **ATLAS 통합**: lock/unlock으로 둘러싸인 outermost critical section에서 logbegin/logend 생성
- **SFR 기반 모델 통합**: acquire/release 동작에 logbegin/logend 배치
- **트랜잭션 기반 모델 통합**: failure-atomic transaction의 commit 시 모든 PM 변경사항 flush 및 로그 커밋

### 3.4. 로그 구조 및 복구 과정

- **로그 엔트리 구조**: 64B 캐시 라인 정렬. 필드: Type (Store/Acquire/Release/TXBEGIN/TXEND), Addr, Value, Size, Valid, Commit marker
- **원형 로그 버퍼**: 스레드별 PM에 위치. Head/tail 포인터로 유효 엔트리 범위 추적
- **커밋 과정**: Commit marker 설정 → 로그 엔트리 invalidate → head 포인터 flush
- **복구 과정**: 커밋되지 않은 로그 엔트리를 역순으로 스캔하여 in-place 업데이트를 롤백

## 핵심 기여

- StrandWeaver는 strand persistency 모델을 최초로 ISA 프리미티브와 하드웨어 메커니즘으로 구현하여 PM 연산의 persist 순서를 최소한으로 제약.
- 세 가지 프리미티브(NewStrand, Persist barrier, JoinStrand)를 통해 strand 내 순서 보장과 strand 간 동시 persist 처리를 모두 지원.
- 언어 수준 persistency 모델(ATLAS, SFR, 트랜잭션)과의 통합 로깅 메커니즘을 제안하여 프로그래머 친화적 persistency semantics 제공.
- Intel x86 대비 평균 **1.45×**, HOPS 대비 평균 **1.20×** 성능 향상 달성. 쓰기 집약적 워크로드에서 가장 큰 효과 (N-Store write-heavy: 1.82×).
- Persist ordering을 memory consistency model과 분리하는 설계 원칙으로, 보수적 consistency model(TSO) 환경에서도 persist 순서 완화 가능.
- 기존 하드웨어 로깅 메커니즘의 고정적/비유연한 설계 한계를 극복하고, 진화하는 언어 수준 persistency 모델에 대응 가능한 유연한 하드웨어 기반을 제시.

## 주요 결과

- **구현 환경**: gem5 시뮬레이터 기반 구현
- **시스템 설정**: 8코어 OoO 프로세서, 2GHz, 6-wide dispatch, 224-entry ROB, 32KB L1, 28MB L2
- **PM 모델**: Intel Optane DC 특성 기반 (346ns 읽기, 96ns 컨트롤러 쓰기, 500ns PM 쓰기)
- **하드웨어 오버헤드**: StrandWeaver 전체 구현에 코어당 144B 추가 저장소 (persist queue + strand buffer unit)
- **소프트웨어 통합**: YCSB 엔진 기반 N-Store 벤치마크의 undo-log 엔진을 StrandWeaver 로깅 메커니즘으로 교체
- **벤치마크**: Queue, Hashmap, Array-Swap, RB-Tree, TPCC, N-Store (read-heavy/balanced/write-heavy)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2020ISCA-summarize/relaxed-persist-ordering-using-strand-persistency.md|전체 요약 보기]]
