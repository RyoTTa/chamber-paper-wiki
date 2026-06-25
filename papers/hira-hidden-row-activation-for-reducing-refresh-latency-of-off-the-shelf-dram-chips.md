---
tags: [paper, 2022, 2022MICRO, topic/dram, topic/rowhammer]
venue: "55th IEEE/ACM International Symposium on Microarchitecture (MICRO 2022)"
year: 2022
summary_path: "../paper-summaries/2022MICRO-summarize/hira-hidden-row-activation-for-reducing-refresh-latency-of-off-the-shelf-dram-chips.md"
---

# HiRA: Hidden Row Activation for Reducing Refresh Latency of Off-the-Shelf DRAM Chips

**Venue:** 55th IEEE/ACM International Symposium on Microarchitecture (MICRO 2022)
**저자:** A. Giray Yağlıkçı (ETH Zürich), Ataberk Olgun (ETH Zürich), Minesh Patel (ETH Zürich), Haocong Luo (ETH Zürich), Hasan Hassan (ETH Zürich), Lois Orosa (ETH Zürich / Galicia Supercomputing Center), Oğuz Ergin (TOBB University), Onur Mutlu (ETH Zürich)

## 개요

- DRAM 셀은 전하 누설로 인해 주기적 리프레시(refresh)가 필요하며, 리프레시 동안 해당 뱅크/랭크의 메모리 접근이 차단되어 **시스템 성능 저하** 발생
- DRAM 밀도 증가와 함께 리프레시 오버헤드가 세 가지 원인으로 악화:
  1. DRAM 칩 내 리프레시해야 할 행(row) 수 증가
  2. 기술 노드 축소로 셀이 작아져 더 자주 리프레시 필요
  3. **RowHammer** 악화로 인한 예방적 리프레시(preventive refresh) 증가
- 기존 리프레시 지연 감소 기법은 DRAM 회로를 수정해야 하므로 **오프더쉘(off-the-shelf) DRAM 칩에는 적용 불가**
- RowHammer: 공격자가 인접 행을 반복 활성화하면 victim 행에 bitflip 발생. 현대 DRAM 칩은 이전 세대보다 더 취약하며, 공격자가 64ms 리프레시 윈도우 내 9600회 활성화로 첫 RowHammer bitflip 유발 가능
- 기존 REF 명령은 랭크 단위로 여러 뱅크의 여러 행을 배치 리프레시 → 명령 버스 점유율 높음. HiRA는 행 단위 세밀한 리프레시로 이 문제를 해결

## 방법론

### 3.1. HiRA 명령 시퀀스

- **동작 흐름 (Figure 2):**
  1. `ACT RowA`: RowA를 활성화하여 로컬 행 버퍼 X에 연결
  2. `PRE`: 로컬 행 버퍼 X를 bank I/O에서 분리 (RowA는 계속 charge restoration)
  3. `ACT RowB`: 다른 서브어레이 Y의 RowB를 활성화 (RowA와 비트라인/센스 앰프리파이어 미공유)
  4. 결과: RowA는 리프레시 완료, RowB는 컬럼 액세스 가능
- **타이밍 파라미터:** t1(ACT→PRE) = 6ns, t2(PRE→ACT) = 최소화. 총 HiRA 작업 시간 6ns
- **리프레시 지연 절감:** 두 행 리프레시에 38ns (기존 78.25ns 대비 51.4% 절감)

### 3.2. HiRA-MC 컴포넌트

- **Refresh Table:** 리프레시 요청의 데드라인, 뱅크 ID, 리프레시 타입(Periodic/Preventive) 저장. 68 엔트리/rank, 0.00031mm²
- **RefPtr Table:** 서브어레이 내 리프레시할 행 주소 저장. 2048 엔트리(뱅크당 128개), 0.00683mm²
- **PR-FIFO:** 예방적 리프레시 요청 대기열. 뱅크당 4 엔트리, 0.00029mm²
- **Subarray Pairs Table (SPT):** 서브어레이 쌍 정보 (비트라인 미공유 서브어레이 목록). 0.00180mm²
- **전체 면적:** 0.00923mm²/rank (22nm Intel 프로세서 대비 0.0023%)
- **전체 접근 지연:** 6.31ns (tRP 14.5ns보다 작음 → 메모리 액세스에 추가 지연 없음)

### 3.3. 주기적 리프레시 스케줄링

- 기존 REF는 랭크 단위 배치 리프레시 → HiRA는 행 단위 개별 리프레시
- 64K 행/뱅크를 리프레시하려면 64K HiRA 작업 필요 (기존 8K REF 명령)
- 명령 버스 부하 분산: 16 뱅크에 대해 각각 다른 시간 오프셋으로 리프레시 요청 생성 (60.9ns 간격)
- **tRefSlack:** 리프레시 요청의 데드라인까지의 시간 여유. 0, 2tRC, 4tRC, 8tRC로 실험

### 3.4. RowHammer 예방적 리프레시

- HiRA-MC는 RowHammer 방어 메커니즘의 병렬화 지원
- PARA(Probabilistic Row Activation)와 통합: pth(확률 임계값)를 tRefSlack 고려하여 재설계
- **보안 분석:** 기존 PARA-Legacy는 공격자가 NRH만큼만 활성화한다고 가정 → 실제 공격자는 리프레시 윈도우 내 최대 tREFW/tRC번 활성화 가능
- 개선된 pth 계산: NRH가 1024→64로 감소 시 pth는 0.068→0.860으로 증가 (더 공격적 예방 리프레시 필요)

## 핵심 기여

- **최초로 오프더쉘 DRAM에서 리프레시-액세스/리프레시-리프레시 병렬화 가능함을 입증**
- HiRA는 DRAM 칩 수정 없이 기존 ACT/PRE 명령 시퀀스만으로 구현되는 실용적 솔루션
- 56개 실chip 실험으로 **32% 행 병렬화 가능**, 리프레시 지연 **51.4% 절감** 확인
- HiRA-MC: 0.00923mm² 면적, 6.31ns 응답으로 하드웨어 오버헤드 극소
- DRAM 밀도 증가(128Gb) 시 **12.6%** 성능 향상, RowHammer 취약성 악화(NRH=64) 시 **3.73x** 성능 향상
- 향후 고밀도/저RowHammer-threshold DRAM에서 Refresh 오버헤드를 효과적으로 완화하는 메커니즘

## 주요 결과

- **실험 인프라:** SoftMC 기반 DDR4 테스트 플랫폼 (Xilinx Alveo U200 FPGA + DDR4 SoftMC)
- **온도 제어:** MaxWell FT200으로 ±0.1°C 정밀 유지
- **테스트 데이터 패턴:** 0xFF, 0x00, 0xAA, 0x55 (4가지 패턴)
- **시험 대상:** SK Hynix 제조 56개 DDR4 DRAM 칩 (4Gb~8Gb)
- **시뮬레이터:** Ramulator 기반 cycle-level 시뮬레이터
- **시스템 구성:** 8코어 프로세서, DDR4-2400, 1채널 1랭크, 16뱅크, FR-FCFS 스케줄러

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]


## 전체 요약

[[../paper-summaries/2022MICRO-summarize/hira-hidden-row-activation-for-reducing-refresh-latency-of-off-the-shelf-dram-chips.md|전체 요약 보기]]
