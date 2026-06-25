---
tags: [paper, 2021, 2021ISCA, topic/dram]
venue: "ISCA 2021 (48th Annual IEEE/ACM International Symposium on Computer Architecture)"
year: 2021
summary_path: "../paper-summaries/2021ISCA-summarize/codic-a-low-cost-substrate-for-enabling-custom-in-dram-functionalities-and-optimizations.md"
---

# CODIC: A Low-Cost Substrate for Enabling Custom In-DRAM Functionalities and Optimizations

**Venue:** ISCA 2021 (48th Annual IEEE/ACM International Symposium on Computer Architecture)
**저자:** Lois Orosa (ETH Zurich), Yaohua Wang (National University of Defense Technology), Mohammad Sadrosadati (ETH Zurich, IPM), Jeremie S. Kim (ETH Zurich), Minesh Patel (ETH Zurich), Ivan Puddu (ETH Zurich), Haocong Luo (ETH Zurich), Kaveh Razavi (ETH Zurich), Juan Gomez-Luna (ETH Zurich, University of Illinois at Urbana-Champaign), Hasan Hassan (ETH Zurich), Nika Mansouri-Ghiasi (ETH Zurich), Saugata Ghose (University of Illinois at Urbana-Champaign), Onur Mutlu (ETH Zurich)

## 개요

- DRAM은 현대 컴퓨팅 시스템의 지배적인 메인 메모리 기술이며, 메모리 컨트롤러는 DRAM 명령(명령)을 통해 DRAM과 인터페이스
- 현대 DRAM 디바이스에서 제조사는 각 명령에 대한 내부 회로 타이밍을 설계 시점에 **고정**하여 결정 → 이 고정된 타이밍은 DRAM이 수행할 수 있는 연산의 유형을 제한
- 고정된 내부 타이밍으로 인해 두 가지 주요 연구 방향이 제약:
  1. **DRAM 기능 확장**: ComputeDRAM 등에서 DRAM 내부 연산 능력을 시연했으나, 신뢰할 수 있는 계산이 가능한 셀이 전체의 **극히 일부**에 불과 (원인 불명 - DRAM 블랙박스 설계로 내부 타이밍 제어 불가)
  2. **DRAM 에너지/레이턴시 최적화**: 메모리 컨트롤러 타이밍 매개변수를 줄이는 연구가 있으나, DRAM 내부 타이밍 신호 최적화는 미exploited (예: ACT 명령에서 access transistor 활성화와 sense amplifier 활성화 간 보수적 시간 간격)
- 기존 DRAM PUF(Physical Unclonable Function)는 (1) 긴 평가 시간, (2) 무거운 필터링 메커니즘 필요, (3) 온도 변화에 따른 높은 응답 변동, (4) 메모리 내용 의존성 등 **네 가지 주요 한계** 보유
- Cold Boot Attack 방지 메커니즘은 메모리 암호화(TCG 등)가 에너지/성능 오버헤드가 크고, 기존 하드웨어 기반 방법(RowClone 등)도 충분히 빠르지 않음

## 방법론

### 3.1. DRAM 내부 타이밍 제어

- **제어 대상 4개 신호** (Figure 2, 3):
  1. **Wordline(WL) 활성화**: access transistor를 켜서 DRAM 셀을 bitline에 연결
  2. **Sense Amplifier Enable (sense_p)**: 셀의 미세한 전하 변화를 감지하고 증폭
  3. **Sense Amplifier Enable (sense_n)**: 차동 증폭의 반대편 제어
  4. **EQ(Precharge)**: bitline을 Vdd/2로 초기화하여 다음 접근 준비
- **CODIC 명령 variants** (Table 2):
  - `CODIC-activate`: 표준 ACT와 유사하나 내부 타이밍 제어 가능 (35ns, 17.3nJ)
  - `CODIC-precharge`: 표준 PRE와 유사하나 내부 타이밍 제어 가능 (13ns, 17.2nJ)
  - `CODIC-sig`: 셀을 Vdd/2로 precharge 후 SA를 활성화하여 시그니처 값 생성 (35ns, 17.2nJ)
  - `CODIC-sig-opt`: 최적화된 시그니처 생성 (13ns, 17.2nJ)
  - `CODIC-det`: 특정 값을 가진 셀을 탐지 (35ns, 17.2nJ)
- **하드웨어 구현**: DRAM 칩과 DDRx 인터페이스에 **최소한의 변경**만으로 구현 가능
- 모든 CODIC 변형의 에너지 소비가 유사 (~17nJ) - 주소 라우팅(~40%)과 SA/Precharge 로직(~40%)이 주요 에너지 소스

### 3.2. CODIC 기반 PUF (Physical Unclonable Function)

- **CODIC-sig PUF 원리**:
  1. CODIC-precharge 로직으로 셀을 Vdd/2로 설정 (초기 값 무관)
  2. CODIC-sig로 SA를 활성화하여 셀의 process variation에 의한 고유 시그니처 생성
  3. 시그니처 = 특정 주소의 DRAM 셀에서 증폭되는 고유 비트 값 (대부분 동일 값으로 증폭, 극히 일부가 반대값으로 증폭)
- **4가지 장점**:
  1. 필터링 메커니즘 불필요 또는 경량화 가능 (99.72%의 챌린지가 단일 필터링으로 안정적 응답)
  2. **1.8배** 높은 처리량 (PreLatPUF 대비), DRAM Latency PUF 대비 **20~100배** 낮은 평가 지연
  3. 온도 변화에 대한 우수한 복원력 (55°C 변화에서도 높은 Intra-Jaccard index 유지)
  4. 메모리 내용에 독립적 (모든 셀이 항상 Vdd/2로 사전 충전되므로)

### 3.3. CODIC 기반 Cold Boot Attack 방지

- **Self-Destruction 메커니즘**:
  - DRAM 전원 인가 시 CODIC-sig 또는 CODIC-det 명령으로 전체 DRAM 내용을 자동으로 파괴
  - 메모리 컨트롤러의 개입 없이 DRAM 칩 내부에서 자율적으로 수행 (공격자가 컨트롤러를 제어할 수 없음)
  - **하드웨어 구현 두 가지 방식**:
    1. 전용 회로 추가: 모든 행에 연속적(back-to-back) CODIC 명령 발행, 은행 간 병렬화, JEDEC 타이밍 제약 준수
    2. 기존 self-refresh 회로 재사용: MUX 추가로 기존 refresh 신호와 CODIC 신호 전환, 추가 비용 최소화
  - 전원 인가 시 자동 트리거 → 보안성은 DRAM 모듈의 전원 인가 검출 회로의 신뢰성에 의존

## 핵심 기여

- **핵심 Contribution**: DRAM 내부 회로 타이밍에 대한 세밀한 제어를 가능하게 하는 최초의 저비용 기반 구조(CODIC) 제시 → 새로운 기능과 최적화를 위한 범용 플랫폼 제공
- **보안 응용**: (1) 기존 최고 state-of-the-art 대비 **1.8배** 높은 처리량과 우수한 안정성을 가진 DRAM PUF, (2) **런타임 오버헤드 0%**의 Cold Boot Attack 방지 메커니즘 (기존 대비 **2배** 빠르고 **1.7배** 적은 에너지)
- **실용성**: 136개 실물 DRAM 칩으로 검증된 실험 결과, DRAM 칩과 DDRx 인터페이스에 최소한의 변경만으로 구현 가능
- **범용성**: 보안 외에도 DRAM 레이턴시/에너지 최적화, 기능 확장 등 다양한 응용 가능 (Section 5.3에서 추가 use case 논의)
- **의의**: DRAM "블랙박스" 설계 문제를 해결하여 향후 DRAM 기반 연구의 새로운 방향을 열어주는 인프라 기여

## 주요 결과

| 항목 | 내용 |
|------|------|
| **평가 환경** | 136개 실물 DDR3 DRAM 칩 (15개 모듈, 3개 벤더: A/B/C) |
| **DRAM 특성** | DDR3 1333~1600MHz, 2~4Gb, 1.35V(DDR3L)/1.5V(DDR3) |
| **하드웨어 플랫폼** | SoftMC 메모리 컨트롤러 + Xilinx ML605 FPGA |
| **시뮬레이터** | Ramulator (Cold Boot 평가용) |
| **DRRAMPower** | 에너지 소비 추정용 커스터마이즈 버전 |
| **시뮬레이션 파라미터** | in-order core, 32KB L1 D&I, 512KB L2, DDR3-1600 x8 11/11/11 |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2021ISCA-summarize/codic-a-low-cost-substrate-for-enabling-custom-in-dram-functionalities-and-optimizations.md|전체 요약 보기]]
