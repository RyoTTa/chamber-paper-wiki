---
tags: [paper, 2020, 2020HPCA, topic/dram, topic/near-data-processing, topic/pim]
venue: "IEEE International Symposium on High Performance Computer Architecture (HPCA '20)"
year: 2020
summary_path: "../paper-summaries/2020HPCA-summarize/elp2im-efficient-and-low-power-bitwise-operation-processing-in-dram.md"
---

# ELP2IM: Efficient and Low Power Bitwise Operation Processing in DRAM

**Venue:** IEEE International Symposium on High Performance Computer Architecture (HPCA '20)
**저자:** Xin Xin, Youtao Zhang, Jun Yang (University of Pittsburgh)

## 개요

- 현대 컴퓨팅 시스템은 "메모리 벽(Memory Wall)" 문제로 인해 성능이 제한됨. 빅데이터 애플리케이션에서 프로세서-메모리 간 오프칩 버스의 제한된 대역폭이 데이터 수요를 충족하지 못하며, 데이터 이동에 상당한 에너지 소모 발생
- 기존 DRAM 기반 근접 데이터 처리(NDP) 방식(HMC, Automata, DRISA 등)은 DRAM 배열 외부에 로직 유닛(LU)을 구현하지만, 고속 LU는 높은 복잡도로 인해 다이 면적을 크게 차지하고 메모리 밀도를 저하시킴 (DRISA의 adder는 51% 면적, Automata의 라우팅 매트릭스는 약 30% 차지)
- 기존 DRAM 기반 PIM 아키텍처인 Ambit은 트리플 로우 액티베이트(TRA)를 사용한 벌크 비트와이즈 연산을 제안했으나, 여러 구조적 문제에 직면:
  - TRA는 높은 전력 소모로 인해 tFAW 등 전력 제약을 위반하고 뱅크 레벨 병렬성을 감소시킴
  - XOR 연산 하나에 7개 커맨드(약 363ns, DDR3-1600 기준) 필요로 긴 지연 시간
  - 계산을 위한 예약 로우 그룹(보통 8개)이 필요하여 용량 및 지연 오버헤드 발생
  - TRA의 셀 간 전하 공유가 공정 변동(process variation)과 비트라인 커플링 효과로 인해 신뢰도 저하

## 방법론

### 3.1. 관찰 및 기반 메커니즘

- **Pseudo-precharge 상태 (Figure 3a):**
  - 활성화 상태에서 비트라인과 비트라인이 각각 Vdd와 Gnd로 충전됨
  - 프리차지 상태에서 하나의 공급 전압만 Vdd/2로 전환하면, 해당 비트라인만 Vdd/2로 따라가고 다른 쪽은 기존 전압 유지
  - SA는 레일-투-레일 출력 특성으로 인해 안정적 상태 유지
  - 이 상태를 "pseudo-precharge"라 명명. 기존 프리차지와 구별하여 SA 공급 전압 제어로 구현
- **오버라이트 프로세스 (Figure 3b):**
  - 프리차지 상태에서 비트라인만 Vdd/2로 충전하고 비트라인은 기존 값을 유지하면, 후속 접근된 셀이 비트라인 값으로 덮어쓰기 됨
  - 비트라인 커패시터(Cb)가 셀 커패시터(Cc)보다 2~4배 크므로 전하 공유 시 비트라인 전압이 지배적
  - 덮어쓰기 활성화를 위해 프리차지 유닛을 수정: EQ 신호를 EQ와 EQb로 분리하여 각 측면을 독립적으로 제어

### 3.2. 논리 연산 구현

- **OR 연산 (Figure 4):**
  - 1번 셀에서 '1'을 읽으면 비트라인에 Vdd 유지 → 2번 셀이 '1'로 덮어쓰기 → OR 결과 = 1
  - 1번 셀에서 '0'을 읽으면 비트라인이 Vdd/2로 조절 → 2번 셀이 정상 접근 → OR 결과 = 0 (1번='0', 2번='0'인 경우)
  - **"Two-cycle" 연산:** APP-AP 시퀀스로 OR(또는 AND) 완료. DDR3-1600 기준 일반 2사이클 대비 ~18% 더 긺
- **AND 연산:**
  - Pseudo-precharge에서 Vdd를 Vdd/2로, Gnd는 유지
  - '0'이 비트라인에서 덮어쓰기를 유도하고, '1'은 Vdd/2로 조절되어 영향 없음
- **NOT 연산:** Ambit과 동일한 이중 연결 셀(dual-connected cell) 사용

### 3.3. 기본 연산 전략 (Figure 5)

- **AAP-AP 전략 (Figure 5a, 5d):** 같은 주소의 A=f(A,B) 유형. APP-AP 시퀀스 사용. 가장 낮은 지연 시간이나 A=f(A,B) 유형으로 제한
- **AAP-APP-AP 전략 (Figure 5b, 5e):** C=f(A,B) 유형, 동일 디코더 도메인 내. Rowclone의 AAP로 데이터 복사 후 APP-AP 연산
- **oAAP-APP-oAAP 전략 (Figure 5c, 5f):** 이중 연결 셀의 예약 로우 활용. 지연 시간이 AAP-APP-AP보다 짧지만 추가 워드라인 활성화 필요
- **XOR 연산 최적화 (Figure 8):** C = A⊕B = A'B + AB
  - 기본: 최대 3개 oAAP-APP-oAAP 시퀀스 → ~519ns
  - 명령어 병합과 중간 데이터 복제 제거를 통해 7개 프리미티브로 ~409ns
  - oAPP과 tAPP 활용으로 ~346ns까지 절감
  - 추가 버퍼 활용 시 6개 프리미티브로 ~297ns 달성

### 3.4. 성능 개선 기법

- **격리 트랜지스터 활용 (Isolation Architecture) (Figure 7a):**
  - 비트라인에 격리 트랜지스터를 통합하여 SA와 PU를 동시에 활성화 가능
  - Pseudo-precharge와 프리차지를 겹치게(oAPP) 수행 → ~21% 지연 시간 절감
- **복원 트렁케이션 (Restore Truncation) (Figure 7c):**
  - 중간 데이터를 재사용하지 않으므로 센스 후 복원 단계를 제거(tAPP)
  - ~31% 지연 시간 절감
- **6개 프리미티브 (Table 1):**
  - AP: 49ns (일반 액티베이트-프리차지)
  - AAP: 84ns (데이터 복사)
  - oAPP: 53ns (겹친 pseudo-precharge)
  - APP: 67ns (pseudo-precharge 포함)
  - oAPP: 53ns (겹친 oAPP)
  - tAPP: 46ns (복원 제거된 APP)

### 3.5. 대체 전략 (Alternative Strategy)

- Cb/Cc 비율이 작을 때(짧은 비트라인)의 신뢰도 문제 해결
- **보완적 pseudo-precharge 전략:** 비트라인 대신 비트라인을 pseudo-precharge 상태에서 조절
  - 비트라인에 '1'이 있으면 비트라인은 Gnd, 비트라인에 '1/2'이 있으면 비트라인은 Vdd/2
  - 물리적으로 다른 서브어레이에 배치되어 커플링 효과 회피

## 핵심 기여

- **핵심 기여:** DRAM의 pseudo-precharge 상태를 활용한 ELP2IM 아키텍처로 Ambit의 구조적 한계(TRA 기반 다중 로우 활성화, 높은 지연 시간, 많은 예약 로우, 신뢰도 문제)를 해결
- **성능 향상:** 기본 논리 연산에서 Ambit 대비 1.17배, 실\application에서는 최대 3.2배(Bitmap, 전력 제약 하) 처리량 향상
- **전력 효율:** Ambit 대비 2배 이상의 전력 효율 향상 달성. 동시 활성화 로우 수 감소로 인한 전력 절감
- **면적 효율:** 1개 예약 로우만 필요(Ambit 8개 대비). ELP2IM의 총 배열 오버헤드는 Ambit 대비 22% 적음 (open-bitline 기준)
- **DRAM 호환성:** 기존 DRAM 제조 공정과의 호환성이 우수. 격리 트랜지스터(~0.8% 면적) 외에 최소한의 수정만 필요
- **한계점:** XOR/XNOR 연산에서 추가 버퍼 없이는 Ambit 대비 큰 이득이 없음. 또한 비트와이즈 PIM의 공통 과제인 오류 정정(ECC) 문제는 여전히 미해결 상태로 남아있음

## 주요 결과

- **시뮬레이터:** H-spice 기반 회로 레벨 시뮬레이션 (Rambus 파워 모델 파라미터 사용)
- **기본 타이밍:** DDR3-1600 (tCK = 2.5ns, 49ns AP 사이클)
- **적용 대상 DRAM:** Ambit, Drisa_nor, ELP2IM 비교 평가
- **케이스 스터디 구현:** Bitmap 인덱스, 테이블 스캔(BitWeaving), CNN(Accelerator 내 TWN/NID)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2020HPCA-summarize/elp2im-efficient-and-low-power-bitwise-operation-processing-in-dram.md|전체 요약 보기]]
