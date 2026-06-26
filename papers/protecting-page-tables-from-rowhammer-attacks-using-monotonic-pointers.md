---
tags: [paper, 2019, 2019ASPLOS, topic/dram, topic/rowhammer, topic/virtual-memory]
venue: "ASPLOS 2019"
year: 2019
summary_path: "../paper-summaries/2019ASPLOS-summarize/protecting-page-tables-from-rowhammer-attacks-using-monotonic-pointers.md"
---

# Protecting Page Tables from RowHammer Attacks using Monotonic Pointers in DRAM True-Cells

**Venue:** ASPLOS 2019
**저자:** Xin-Chuan Wu, Timothy Sherwood, Frederic T. Chong, Yanjing Li (University of Chicago, UC Santa Barbara)

## 개요

- RowHammer 공격은 DRAM row를 반복 활성화하여 인접 row에 bit-flip을 유발하는 하드웨어 취약점
- PTE(Page Table Entry) 기반 privilege escalation 공격이 가장 심각: 공격자가 자기 프로세스의 PTE를 변조하여 page table에 대한 쓰기 권한 획득 → 전체 물리 메모리 접근 → root 권한 탈취
- 기존 RowHammer 방어 기법들 (TRR, PARA, Refresh-based)은 하드웨어 수정 필요하거나 과도한 refresh 오버헤드 발생
- ECC는 RowHammer로 인한 disturbance error를 교정하지 않도록 설계 (random error와 구분 어려움)
- DRAM 셀에는 **true-cell** ('1'→'0' error)과 **anti-cell** ('0'→'1' error)의 비대칭성이 존재하지만, 기존에는 보안 목적으로 활용되지 않음

## 방법론

### 3.1. True-Cell과 Anti-Cell의 비대칭성

- DRAM bank에서 true-cell row와 anti-cell row가 일반적으로 **N=512** 간격으로 교대로 존재
- True-cell: 충전된 상태 = '1', 방전 = '0' → 충전 누수 시 **'1'→'0'** error
- Anti-cell: 충전된 상태 = '0', 방전 = '1' → 충전 누수 시 **'0'→'1'** error
- System-level에서 DRAM refresh를 비활성화한 후 '1'을 쓰고 일정 시간 후 읽어서 셀 타입 판별 가능
- 각 DRAM row는 일반적으로 동일한 셀 타입으로 구성

### 3.2. Monotonicity Property

- 하나의 데이터 객체를 하나의 셀 타입에만 할당하면:
  - True-cell에만 할당된 포인터: 오직 **'1'→'0'** flip만 발생 가능
  - Anti-cell에만 할당된 포인터: 오직 **'0'→'1'** flip만 발생 가능
- PTE의 write permission bit이 '1'(쓰기 허용)에서 '0'(쓰기 불허)으로 flip되는 것은 보안상 위험하지만, '0'→'1' flip은 write permission을 추가하지 않음
- 따라서 **true-cell에 PTE를 배치**하면 RowHammer로 write permission을 획득하는 것이 수학적으로 불가능

### 3.3. Low Water Mark 기법

- DRAM 물리 주소 공간에서 true-cell 영역의 상위 portion에 page table을 할당
- "low water mark" = true-cell 영역의 하한 경계
- Low water mark 이하의 주소는 general allocation에만 사용
- Page table 할당 시 해당 주소가 true-cell 영역인지 사전 확인

### 3.4. PTE Self-Reference 방어

- RowHammer PTE privilege escalation의 핵심: PTE가 자기 프로세스의 다른 PTE를 가리키는 self-reference 구성
- CTA 할당으로 모든 page table이 true-cell에 위치 → attacker가 control하는 page도 true-cell
- True-cell에서 '0'→'1' flip은 write bit을 set하지 못하므로 self-reference 구성 실패

## 핵심 기여

- **핵심 Contribution**: DRAM true-cell/anti-cell 비대칭성을 최초로 보안 목적으로 활용 — monotonicity property를 통해 RowHammer PTE 공격을 수학적으로 방어
- **구현 효율성**: 18줄 코드 수정으로 Linux 커널에 구현, 성능 overhead **0%** — 기존 방어 기법 중 가장 낮은 비용
- **보안 강도**: 204,000대 중 1대만 취약, 취약하더라도 공격에 **231일** 소요 — 실질적 무의미
- **범용성**: CTA 메모리 할당은 RowHammer 외에도 다른 메모리 기반 공격 (cold boot, DMA 등)에도 확장 가능
- **의의**: 하드웨어 수정이나 refresh overhead 없이 OS 레이만으로 RowHammer를 방어하는 새로운 패러다임 제시 — DRAM 물리 특성과 OS 메모리 관리의 교차점에서 보안 문제 해결

## 주요 결과

- **OS**: Ubuntu Linux 커널
- **수정 규모**: 18줄 코드 수정
- **프로토타입 시스템**:
  - Intel i7-6700 quad-core (8GB 물리 메모리)
  - Intel Xeon Silver 4110 32-core (128GB 물리 메모리)
- **할당 로직**: kmalloc/gfp 커널 할당기에서 true-cell 영역 여부를 확인하는 조건문 추가
- **초기화**: boot 시 true-cell 영역 탐지 (refresh 비활성화 방식)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2019ASPLOS-summarize/protecting-page-tables-from-rowhammer-attacks-using-monotonic-pointers.md|전체 요약 보기]]
