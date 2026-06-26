---
tags: [paper, 2024, 2024HPCA, topic/cache, topic/dram, topic/nvm]
venue: ""
year: 2024
summary_path: "../paper-summaries/2024HPCA-summarize/prosper-program-stack-persistence-in-hybrid-memory-systems.md"
---

# Prosper: Program Stack Persistence in Hybrid Memory Systems

**Venue:** 
**저자:** 

## 개요

- 전원 장애 및 시스템 크래시에 대한 복원력을 보장하기 위해 프로세스의 지속적이고 크래시 컨시스턴트한 실행 상태가 필수적
- NVM(Non-Volatile Memory)의 등장으로 DRAM과 비슷한 read/write 레이턴시를 가지는 하이브리드 메모리 시스템에서 효율적인 체크포인트 메커니즘 설계 가능
- 기존 메모리 지속성 기술의 한계:
  - **SSP [41]**: 프로세스 지속성 미지원, stack pointer awareness 없음, stack을 DRAM에 유지 불가
  - **JUSTDO [24]**: 프로세스 지속성 미지원, 컴파일러 지원 필요
  - **SoftWRAP [19]**: 프로세스 지속성 미지원
  - **Timestone [30]**: 프로세스 지속성 미지원, 컴파일러 지원 필요
  - **Romulus [15]**: 프로세스 지속성 미지원, 컴파일러 지원 필요
- Stack은 특유의 grow/shrink 사용 패턴과 activation record 특성으로 인해 일반 메모리 지속성 기술을 단순 적용하면 비효율 발생
  - Gapbs_pr 벤치마크: stack 영역의 70%가 read/write 수행
  - YCSB_mem 벤치마크: 전체 스택 쓰기의 상당수가 SP(final stack pointer) 너머에 발생 (불필요한 쓰기)
- Page 수준 dirty tracking은 sub-page byte 수준 대비 checkpoint 크기가 300×(Gapbs_pr), 56×(G500_sssp), 33×(YCSB_mem)큼 큼

## 핵심 아이디어

- **Prosper**: 하드웨어-소프트웨어(OS) 공동 설계 기반 checkpoint 메커니즘으로 stack 지속성 달성
- 하드웨어가 sub-page byte 수준에서 stack 변경 사항을 추적하여 checkpoint 크기 대폭 감소
- OS가 checkpoint interval의 시작/종료를 제어하고, 하드웨어 트래커가 스택 쓰기를 필터링하여 bitmap에 기록
- 핵심 도전 과제:
  1. 하드웨어와 소프트웨어 간 효율적인 통신 프로토콜 설계
  2. 트래커가 프로세스의 load/store 요청을 stall하지 않도록 out-of-path 설계
  3. 다양한 실행 엔티티 간 추적 범위, 메타데이터 영역 공유 및 동기화

## Prosper 시스템

## 방법론

- OS는 애플리케이션 스레드의 stack 주소 범위를 기록하고, 추적粒度, 메타데이터 영역 주소 등 파라미터를 하드웨어에 전달
- Checkpoint interval 종료 시:
  1. 하드웨어에 bitmap 영역 flush 지시
  2. flush 완료 확인 (하드웨어 인디케이터 체크)
  3. bitmap 비트 검사 후 수정된 stack 영역을 NVM의 임시 버퍼로 복사 (Step 4→5)
  4. 임시 버퍼에서 per-thread persistent stack으로 업데이트
- bitmap inspection 시 coalescing 기회 탐색 (8바이트 내)으로 오버헤드 최소화
- Context switch 시: outgoing context의 bitmap 영역 quietens (2단계 프로세스), incoming context의 저장된 상태 복원

### 3.2. 하드웨어 구성 요소

- **Dirty Tracker**: checkpoint interval 동안 활성화, 메모리 store 모니터링
  - stack 영역에 대한 store를 필터링하여 bitmap 영역의 해당 비트를 설정
  - 추적粒度는 8바이트 배수로 구성 가능
- **Lookup Table (.bitmap cache)**:
  - bitmap store 요청을 coalesce하기 위한 small cache
  - 각 엔트리: <bitmap location address (64bits), bitmap value (32bits)>
  - 병렬 검색 가능 (bitmap location address를 key로 사용)
  - **Accumulate and Apply** 전략 사용: 새 엔트리를 즉시 할당하고, bitmap store 요청 시에만 메모리에서 기존 bitmap 값을 로드하여 병합
- **Coalescing 임계값**:
  - HWM (High-Water-Mark): lookup table 엔트리의 설정된 비트 수가 임계값에 도달하면 bitmap store 요청 생성
  - LWM (Low-Water-Mark): eviction 시 기준. LWM 이하의 엔트리를 우선 eviction하여 자주 수정되는 stack 영역의 엔트리를 보존
- 에너지/면적 오버헤드 (7nm FINFET, CACTI-P):
  - Dynamic read energy per access: 0.0000773194 nJ
  - Write energy per access: 0.000128375 nJ
  - Leakage power: 0.01067596 mW
  - Lookup table 면적: 0.000704786 mm² (16 entries)

### 3.3. Multi-threading 지원

- 각 소프트웨어 스레드의 stack은 해당 logical CPU에서 추적 가능
- Context switch 시 outgoing context의 Prosper 상태 (설정 + bitmap 정보) 저장 및 복원
- Inter-thread stack 수정 처리: page table 엔트리 권한 분리 (자기 stack은 write, 타 스레드 stack은 read-only) → write fault 시 OS가 bitmap 비트 설정 후 쓰기 허용

## 핵심 기여

- **핵심 기여**: Stack의 특수한 특성(grow/shrink 패턴, activation record 쓰기 특성)을 처리하는 sub-page byte 수준 checkpoint 기반 지속성 메커니즘 최초 제안
- **성능 향상**: SSP 대비 stack persistence 오버헤드 평균 2.1×(최대 3.6×) 감소, 전체 memory persistence 오버헤드 평균 2×(최대 2.6×) 개선
- **실용성**: OS와 하드웨어 공동 설계로 기존 checkpoint 메커니즘과 자연스럽게 통합 가능, tracking 오버헤드 평균 1% 미만
- **응용**: 하이브리드 메모리 시스템(DRAM+NVM)에서 프로세스 지속성의 효율적인 달성 방향 제시, future work로 stack 외 heap 영역에도 적용 가능

## 주요 결과

### 방법론

| 항목 | 내용 |
|------|------|
| **Setup-I** | gem5, 4개 out-of-order core, 3.2GHz, 32KB L1-I/D, 256KB L2, 8MB LLC, DDR3-1600 |
| **Setup-II** | gem5, 4개 out-of-order core, 3.2GHz, 32KB L1-I/D, 256KB L2, 2MB LLC, NVM (320ns read, 480ns write) |
| **OS** | 수정된 Linux 커널 (Prosper 소프트웨어 통합) |
| **벤치마크** | SPEC CPU2017 (mcf, lbm, xalancbmk, etc.), Graph500 SSSP, GAPBS PR |
| **체크포인트 간격** | 10ms |
| **기법 비교** | SSP, Romulus, page-level Dirtybit, byte-level dirty tracking |

### 주요 결과

- **Checkpoint 크기 감소**: byte 수준 dirty tracking으로 page 수준 대비 평균 ~4× checkpoint 데이터 복사량 감소
  - Gapbs_pr: 99% checkpoint 크기 감소 (300× 개선)
  - G500_sssp: 56× checkpoint 크기 감소
  - YCSB_mem: 33× checkpoint 크기 감소
- **Stack persistence 오버헤드 감소**:
  - SSP 대비 평균 2.1×, 최대 3.6× 감소
  - Page-level Dirtybit 대비 최대 1.27× 감소
- **전체 memory persistence 개선**: Prosper + SSP 조합 시 SSP 단독 대비 평균 2×, 최대 2.6× 개선
- **Tracking 오버헤드**: 평균 1% 미만 (최대 ~3%)
- **Checkpoint 시간 개선**: sparse write 시 stack checkpoint 시간 ~22× 개선
- **Lookup Table 민감도 분석**:
  - G500_sssp: HWM 증가 시 bitmap load/store 감소 (spatial locality 존재)
  - mcf: HWM 증가 시 bitmap load/store 증가 (spatial locality 부족), LWM 증가 시 감소 (eviction이 유리)

### Design Choices / Ablation Study

- **Accumulate and Apply vs Load and Update**: Accumulate and Apply 채택 → lookup table 엔트리를 즉시 할당 가능, 로드 지연으로 복잡성 회피
- **HWM/LWM 설정**: HWM=24, LWM=8로 고정 사용. 동적 스킴은 future work로留待
- **Tracking粒度**: 8바이트 배수로 구성 가능. 8바이트에서 상당한 개선 달성
- **SP awareness**: checkpoint 시점의 active stack 영역만 처리 → 불필요한 operations 제거

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]


## 전체 요약

[[../paper-summaries/2024HPCA-summarize/prosper-program-stack-persistence-in-hybrid-memory-systems.md|전체 요약 보기]]
