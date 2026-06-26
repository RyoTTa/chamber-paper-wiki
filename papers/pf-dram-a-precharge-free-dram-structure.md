---
tags: [paper, 2021, 2021ISCA, topic/cache, topic/dram]
venue: "ISCA 2021 (48th Annual IEEE/ACM International Symposium on Computer Architecture)"
year: 2021
summary_path: "../paper-summaries/2021ISCA-summarize/pf-dram-a-precharge-free-dram-structure.md"
---

# PF-DRAM: A Precharge-Free DRAM Structure

**Venue:** ISCA 2021 (48th Annual IEEE/ACM International Symposium on Computer Architecture)
**저자:** Nezam Rohbani (IPM, Sharif University of Technology), Sina Darabi (IPM, Sharif University of Technology), Hamid Sarbazi-Azad (IPM, Sharif University of Technology)

## 개요

- 현대 컴퓨팅 시스템에서 메모리 서브시스템은 전체 시스템 전력 소비의 **25%~57%**를 차지하며, DRAM 칩이 그 중 상당 부분을 소비
- DRAM의 Read, Write, Refresh 작업은 모두 **Precharge 단계**에서 시작되며, 이 단계는 막대한 에너지 소비와 함께 행을 닫고 다른 행을 열 때의 지연 시간을 증가
- 최근 워크로드尤其是 멀티코어 시스템에서 row-hit rate이 감소하면서 precharge rate이 증가하여 DRAM 전력 소비와 접근 지연 시간이 악화
- 모든 세대의 DRAM에서 Activation 전에 bitline을 VDD/2로 사전 충전(Precharge)하는 것이 필수적이며, 이는 에너지 소비의 주요 원인
- 기존 DRAM의 precharge 에너지 공식: Epre = ζ · CBL · VDD² / 2 (ζ ≈ 0.54)
- Precharge 지연 시간(tRP)은 DRAM 접근 주기(tRC)의 약 1/3을 차지하며, DDR3에서 DDR4로 세대가 변하면서 오히려 증가(12.5ns → 14.1ns)

## 방법론

### 3.1. Bitline 구조 변경

- 기존 DRAM: 모든 bitline을 VDD/2로 사전 충전 후 Activation 시 한쪽은 VDD로, 다른 쪽은 0으로 충전/방전
- PF-DRAM: bitline이 이전 상태를 유지하며, 셀 값과 다를 때만 flip 발생
- Bitline Left(BLL)과 Bitline Right(BLR)은 더 이상 반대 값을 가지지 않음
- bitline을 SA 입력/출력에서 분리하는 절연 트랜지스터(M4, M5) 추가
- 기존 DRAM의 전체 bitline 대비 **8.8% 면적 오버헤드**

### 3.2. 비대칭 Sense Amplifier (SA Imbalancer)

- 8가지 가능한 시작점 조건을 구분하기 위한 비대칭 SA 설계
- 두 개의 tri-스테이트 NOT 게이트(BOOSTR, BOOSTL)로 구성
- Scenario I (셀 값 = bitline 값): VSPF = 0, 두 노드 전압이 동일 → 부스트된 쪽이 안정화 포인트 결정
- Scenario II (셀 값 ≠ bitline 값): VSPF = VDD · Ccell / (CBL + Ccell), 단일 NOT 게이트가 승리
-SA Imbalancer는 SA와 병렬로 작동하여 출력을 증폭

### 3.3. 복원(Restoration) 메커니즘

- 기존 DRAM: 연결된 bitline을 셀 값으로 충전하고 다른 bitline은 반대 값으로 설정
- PF-DRAM: BLL과 BLR을 모두 접근된 셀의 동일한 값으로 충전/방전
- Voltage Updater(VUR/VUL)와 디 coupler 신호를 통해 bitline을 SA에 다시 연결
- 복원 시 SA의 부스트된 쪽이 bitline을 구동하므로 안정적인 복원 보장

## 핵심 기여

- **핵심 기여**: Precharge 단계를 완전히 제거하는 최초의 DRAM 구조 제안
- **성능**: 평균 35.3% 전력 절감, 8.6% IPC 향상, 19.2% 지연 시간 감소
- **의의**: DRAM의 "블랙박스" 문제를 해결하고, 기존에 불가능했던 연구 방식을 실현 가능한 범용 기반 구조 제공
- 기존 DRAM 전력 절감 기술들과 결합하여 추가적인 에너지 절감 가능성

## 주요 결과

| 항목 | 내용 |
|------|------|
| **평가 환경** | HSPICE 회로 시뮬레이터, 16nm Multi-Gate 기술 모델 |
| **시스템 시뮬레이터** | gem5 풀시스템 시뮬레이터 |
| **워크로드** | SPEC CPU2017 (16개), PARSEC 2.1 (5개 멀티스레드) |
| **시스템 구성** | 단일/멀티(2,4,8)코어, 아웃오브오더 X86(64비트), 3GHz |
| **캐시** | L1: 32KB 프라이빗(코어당), L2: 2MB 공유 |
| **메모리** | 8GB DDR4-2400, 16 Chip/DIMM, 2 Channel, 2 Rank/channel, 16 Bank |
| **회로 파라미터** | CBL=144fF, Ccell=24fF, MAT=512×512 셀 |
| **면적 오버헤드** | < 8.8% (SA 변경, 셀 배열 변경 없음) |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2021ISCA-summarize/pf-dram-a-precharge-free-dram-structure.md|전체 요약 보기]]
