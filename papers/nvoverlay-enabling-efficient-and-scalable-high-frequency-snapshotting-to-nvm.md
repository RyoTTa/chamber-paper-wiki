---
tags: [paper, 2021, 2021ISCA, topic/cache, topic/nvm, topic/virtual-memory]
venue: "ISCA 2021 (48th Annual IEEE/ACM International Symposium on Computer Architecture)"
year: 2021
summary_path: "../paper-summaries/2021ISCA-summarize/nvoverlay-enabling-efficient-and-scalable-high-frequency-snapshotting-to-nvm.md"
---

# NVOverlay: Enabling Efficient and Scalable High-Frequency Snapshotting to NVM

**Venue:** ISCA 2021 (48th Annual IEEE/ACM International Symposium on Computer Architecture)
**저자:** Ziqi Wang (Carnegie Mellon University), Chul-Hwan Choo (Samsung Electronics), Michael A. Kozuch (Intel Labs), Todd C. Mowry (Carnegie Mellon University), Gennady Pekhimenko (University of Toronto), Vivek Seshadri (Microsoft Research India), Dimitrios Skarlatos (Carnegie Mellon University)

## 개요

- 바이트 주소 가능 NVM(Non-Volatile Memory) 기술의 발전으로, 물리 주소 공간 전체의 빈번한 영속 스냅샷(per persistent snapshot)을 NVM에 캡처하는 것이 유망한 활용 모델로 부상 (밀리초 단위의 수백 번/snapshots/s)
- 활용 모델로 distributed cloud 애플리케이션의 time-traveling debugging, persistent/durable data structures, fine-grained system backup/replication, low-latency crash recovery 등이 있음
- **기존 기술의 한계**: 기존 스냅샷 기법은 persistence barrier stalls, NVM write amplification, 단일 소켓 이상의 확장성 부족의 조합으로 어려움을 겪음
  - **소프트웨어 방식** (Undo Logging 등): persistence barrier로 인한 성능 저하 + NVM write amplification (로그 작성 후 최종 위치로 복사)
  - **하드웨어 방식** (PiCL, ThyNVM 등): write amplification + 멀티소켓 확장성 부족 (집약적 LLC 가정, 중앙 집중 매핑 구조 등)
- NVM write amplification은 NVM 대역폭을 사실상 **2배**로 증가시키고, Program/Erase(P/E) 사이클도 감소시킴
- 기존 하드웨어 제안들은 inclusive monolithic cache hierarchy, 중앙 집중 매핑 테이블 등 비확장적 구조에 의존

## 방법론

### 3.1. Coherent Snapshot Tracking (CST)

- **Version Access Protocol**: 각 캐시 라인에 16비트 OID(Overlay ID) 필드를 추가하여 마지막으로 업데이트된 epoch ID를 저장
- **Versioned Domain (VD)**: 코어 그룹 내에서 독립적인 epoch 실행, VD 내부 동기화는 로컬 통신으로 경량화
- **Relaxed Epoch Model**: VD 간 데이터 의존성이 발생하면 Lamport clock 유사 방식으로 epoch 동기화 (데이터가 "미래에서 온" 경우 수신 VD의 epoch를 업데이트)
- **L1 Store-Eviction 메커니즘**: 불변(immutable) 버전이 캐시에 있을 때, L1 컨트롤러가 불변 버전을 L2로 eviction한 후 in-place로 store 수행 (Fig. 4)
- **L2 External Downgrade/Invalidation**: 캐시 간 직접 전송으로 불필요한 NVM write 회피 (Fig. 5, 6)
- 불리 프로토콜(MESI 기반)을 수정하지 않고, 기존 coherence 동작에 tag checks와 evicts만 추가

### 3.2. Multi-snapshot NVM Mapping (MNM)

- **Overlay Memory Controller (OMC)**: 메모리 컨트롤러와 캐시 계층 사이에 위치, 주소-버전 매핑 테이블 유지
- **Master Mapping Table (Mmaster)**: 5-level radix tree 구조 (Fig. 10), 가장 최근 영속화된 버전의 물리 주소-NVM 주소 매핑 저장
- **Per-epoch volatile tables (Mi)**: 각 epoch마다 버전별 물리-NVM 주소 매핑 저장
- **Background merging**: rec-epoch가 업데이트되면 Mmaster로 per-epoch 테이블을 병합, 정지 없이 백그라운드에서 수행
- **Garbage Collection**: stale 버전을 회수, compaction 알고리즘으로 oldest epoch 버전을 최신 epoch로 복사하여 공간 회수
- 스냅샷은 epoch 단위로 NVM에 저장되어 개별 또는 최신 스냅샷 접근 가능

## 핵심 기여

- **핵심 Contribution**: 멀티소켓 병렬 애플리케이션의 비수정(unmodified) 환경에서 NVM 기반 고빈도 스냅샷을 지원하는 최초의 하드웨어 기법 제시
- **성능**: PiCL 대비 write amplification **29%~47%** 절감, 12개 벤치마크 중 9개에서 스냅샷 오버헤드 **0%**
- **대역폭**: NVM write 대역폭 소비를 대폭 절감하여 확장성 확보
- **실용성**: OID 태그 오버헤드 **3.2%** 이하, 기존 MESI 프로토콜 수정 없이 구현 가능
- **의의**: crash recovery와 time-travel debugging을 대규모 병렬 애플리케이션에서 실용적으로 구현 가능

## 주요 결과

| 항목 | 내용 |
|------|------|
| **시뮬레이터** | zsim (Pin 기반 사이클 정확 멀티코어 시뮬레이터) |
| **프로세서** | 16코어 4-way superscalar @ 3GHz |
| **L1-D 캐시** | 32KB, 64B lines, 8-way, 4 cycles |
| **L2 캐시** | 256KB, 64B lines, 8-way, 8 cycles |
| **Shared LLC** | 32MB, 64B lines, 16-way, 30 cycles |
| **DRAM** | DDR3 1333 MHz, 4 컨트롤러 |
| **NVDIMM** | 16 banks, 133 ns write latency (miss) |
| **OID 태그 오버헤드** | 캐시 라인당 16bit → 온칩 SRAM **3.2%** 증가 |
| **DRAM 오버헤드** | 라인당 16bit OID → 최대 **3.2%** (4KB row당 16 OID 사용 시 **0.8%** 이하) |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2021ISCA-summarize/nvoverlay-enabling-efficient-and-scalable-high-frequency-snapshotting-to-nvm.md|전체 요약 보기]]
