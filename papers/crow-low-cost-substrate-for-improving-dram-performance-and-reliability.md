---
tags: [paper, 2019, 2019ISCA, topic/cache, topic/dram, topic/rowhammer, topic/storage]
venue: "The 46th Annual International Symposium on Computer Architecture (ISCA '19)"
year: 2019
summary_path: "../paper-summaries/2019ISCA-summarize/crow-low-cost-substrate-for-improving-dram-performance-energy-efficiency-and-reliability.md"
---

# CROW: A Low-Cost Substrate for Improving DRAM Performance, Energy Efficiency, and Reliability

**Venue:** The 46th Annual International Symposium on Computer Architecture (ISCA '19)
**저자:** Hasan Hassan (ETH Zürich), Minesh Patel (ETH Zürich), Jeremie S. Kim (ETH Zürich / Carnegie Mellon University), A. Giray Yaglikci (ETH Zürich), Nandita Vijaykumar (ETH Zürich / Carnegie Mellon University), Nika Mansouri Ghiasi (ETH Zürich), Saugata Ghose (Carnegie Mellon University), Onur Mutlu (ETH Zürich / Carnegie Mellon University)

## 개요

- DRAM은 수십 년간 메인 메모리의 주요 기술이었으나, 프로세스 기술 스케일링으로 인해 세 가지 핵심 과제에 직면
  - **높은 접근 지연 시간**: DRAM 용량은 지난 20년간 크게 증가했으나, 접근 지연 시간은 거의 개선되지 않음 — 워크로드 성능에 큰 영향
  - **높은 리프레시 오버헤드**: DRAM 셀이 충전을 누설하여 주기적 리프레시 필요, 현대 LPDDR4에서 **32ms마다 모든 셀 리프레시** 필요, 최대 **50%의 DRAM 에너지가 리프레시에 소비**
  - **증가하는 취약성**: 셀 크기 축소로 인해 셀 간 간격 감소, **RowHammer**와 같은 실패 메커니즘에 노출 — 반복적 활성화로 인접 셀에 비트 플립 유발
- 기존 해결책의 한계:
  - 지연 시간 최적화 DRAM 모듈은 일반 DRAM 대비 **크기와 비용이 크게 증가**
  - DRAM 셀 배열 구조를 직접 변경하면 밀도 최적화에 부정적 영향, **작은 변경만으로도 상당한 면적 오버헤드 발생**

## 방법론

### 3.1. 기본 구조

- 각 DRAM 서브어레이를 두 영역으로 분리:
  - **Regular rows (RR)**: 기존 일반 데이터 저장 영역
  - **Copy rows (CR)**: 복제된 데이터를 저장하는 고속 영역
- **독립 디코더**: 복사 행용 별도 디코더를 추가하여 일반 행과 독립적으로 활성화 가능
- **CROW-table**: 메모리 컨트롤러에 구현된 작은 테이블로, 복사 행의 상태 정보(어떤 일반 행이 복사되었는지)를 추적
- DRAM 칩당 추가 면적: **0.48%**, 저장 용량: **1.6%** (서브어레이당 8개 복사 행 기준)

### 3.2. CROW-cache (DRAM 내 캐싱)

- **ACT-c 명령**: 일반 행을 활성화한 후 약간의 지연으로 복사 행을 활성화 → 동일 서브어레이의 센스 앰프리파이어를 공유하여 두 행의 충전 복원이 동시에 이루어짐으로써 복사 수행
- **ACT-t 명령**: 일반 행과 복사 행을 동시에 활성화 → 각 셀의 충전이 두 개의 센스 앰프리파이어를 동시에 구동하여 **활성화 지연 시간 38% 감소**
- **부분 복원(Partial Restoration)**: 복사 행을 완전히 복원하지 않고 부분적으로 유지 → 복원 지연 시간을 크게 단축
- **CROW-table 관리**: 테이블 미스 시 새로운 일반 행을 복사 행에 복제, 이미 할당된 경우 가장 오래된 엔트리를 교체
- 완전 복원 여부 추적 필드(isFullyRestored)를 통해 안전한 교체 보장

### 3.3. CROW-ref (리프레시 오버헤드 경감)

- **약한 행 식별**: 시스템 부팅 또는 런타임에서 리텐션 시간 프로파일링을 통해 약한 행을 탐지
  - 기존 연구에 따르면 리프레시 간격을 **2~4배 연장**해도 약 **1000개 셀만 실패** (32 GiB 모듈 기준)
  - 비트 에러율(BER)이 **4×10⁻⁹** 수준으로 매우 낮음 (256ms 리프레시 간격)
- **강한 복사 행으로 리맵핑**: 약한 일반 행의 데이터를 동일 서브어레이의 강한 복사 행에 저장
- **리프레시 간격 연장**: 약한 행을 회피하므로 전체 DRAM 칩의 리프레시 간격을 기존 **32ms → 최대 256ms**로 연장 가능
- 소프트웨어에 투명한 동적 리맵핑 지원

## 핵심 기여

- **핵심 Contribution**: DRAM 내부 복사 행을 활용하는 유연한 기반 구조 CROW 제안, 성능·에너지·신뢰성 세 가지 과제를 동시에 해결
- **성능 향상 수치**: 메모리 집약적 워크로드에서 **20.0% 성능 향상**, **22.3% 에너지 절감**
- **실용성**: DRAM 칩 면적 **0.48%**, 저장 용량 **1.6%**의 매우 낮은 오버헤드로 기존 DRAM 공정과의 호환성 유지
- **의의**: DRAM 셀 배열 변경 없이 최소 수정으로 DRAM의 근본적인 한계를 해결하는 기반 구조로, 향후 다양한 DRAM 최적화 기술의 발전에 기여

## 주요 결과

- **DRAM 칩 변경**: 서브어레이 디코더에 복사 행용 독립 라인 추가, 기존 로컬 행 디코더 로직 확장
- **면적 오버헤드**: DRAM 칩 전체 기준 **0.48%** (복사 행 8개/서브어레이)
- **저장 용량 오버헤드**: **1.6%** (복사 행 저장 공간)
- **메모리 컨트롤러**: CROW-table 구현, 약 **11.3 KiB** 저장 오버헤드
- **새 명령어**: ACT-c, ACT-t 추가 — 기존 LPDDR4 명령/주소 버스의 다중 사이클 전송 활용

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2019ISCA-summarize/crow-low-cost-substrate-for-improving-dram-performance-energy-efficiency-and-reliability.md|전체 요약 보기]]
