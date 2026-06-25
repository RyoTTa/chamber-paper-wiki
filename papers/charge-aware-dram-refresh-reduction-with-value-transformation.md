---
tags: [paper, 2020, 2020HPCA, topic/dram]
venue: "2020 IEEE International Symposium on High Performance Computer Architecture (HPCA '20)"
year: 2020
summary_path: "../paper-summaries/2020HPCA-summarize/charge-aware-dram-refresh-reduction-with-value-transformation.md"
---

# Charge-Aware DRAM Refresh Reduction with Value Transformation

**Venue:** 2020 IEEE International Symposium on High Performance Computer Architecture (HPCA '20)
**저자:** Seikwon Kim (Samsung Research, Samsung Electronics), Wonsang Kwak (School of Computing, KAIST), Changdae Kim (ETRI), Daehyeon Baek (School of Computing, KAIST), Jaehyuk Huh (School of Computing, KAIST)

## 개요

- 시스템 메모리 용량이 증가함에 따라 DRAM 리프레시(refresh) 동작이 전체 DRAM 전력 소비에서 차지하는 비율이 지속적으로 증가
- 리프레시는 고정된 시간 간격(보통 32ms 또는 64ms) 동안 전체 DRAM 용량에 대해 적용되어야 하므로, 메모리 용량 증가 시 리프레시 에너지 소비가 악화
- 기존 리프레시 절감 기법들의 한계:
  - 유지 시간(retention time) 기반: 셀별 유지 시간이 동적으로 변하여 상태 확인 필요 (최대 18개 요인 영향)
  - 접근 기반 (Smart Refresh): 고정된 리프레시 주期内 접근된 행의 비율이 메모리 용량 증가 시 빠르게 감소
  - 미할당 메모리 기반: DRAM에 새로운 HW 인터페이스와 상당한 OS 변경 필요
- DRAM 셀의 특성: 방전(discharged) 상태는 리프레시 불필요. 전체 행이 방전된 셀로 구성되면 리프레시 스킵 가능
- 실제 메모리 콘텐츠에서 byte 수준에서는 평균 43%가 0 값을 가지지만, row 수준(1KB 블록)에서는 0 연속 블록이 평균 2.3%에 불과 (Figure 6)

## 방법론

### 3.1. Charge-Aware 리프레시 절감 메커니즘

- **방전된 행 감지:** 리프레시 시 센스 앰플리피어가 모든 셀의 충전 상태를 검출. 비트별 wire-OR로 행 전체의 충전/방전 상태 결정
- **방전 상태 추적 테이블 (Discharged-Status Table):**
  - 네이브 설계: 32GB 메모리에서 830만+ 행 → 1MB SRAM 필요 (누설 전력 337.14mW @ 32nm)
  - 최적화: 방전 상태 테이블을 DRAM 공간에 저장하고, 코스-grain access bit 테이블(8KB SRAM)로 쓰기 추적
  - access bit 테이블: 각 비트가 여러 행을 커버. 쓰기 발생 시 해당 비트 설정. 리프레시 시 access bit이 설정된 범위는 일반 리프레시 수행
- **리프레시 카운터 수정:** 기존 리프레시 카운터에 방전 상태 조회 로직 추가

### 3.2. 값 변환 (Value Transformation)

- **BDI 기반 변환:** 캐시 라인 단위로 값을 베이스(base)와 델타(delta)로 변환
- **EBDI (Enhanced BDI):** ZERO-REFRESH를 위해 확장된 BDI 코딩. 더 많은 방전 비트 생성为目标
- **비트 전치 (Bit Plane Rotation):** 변환된 값을 비트 평면 단위로 전치하여 연속 방전 비트를 각 행에 배치
- **멀티칩 매핑 조정:** 여러 칩에 걸친 캐시 라인 매핑을 조정하여 특정 행 세트가 모두 방전 셀을 갖도록 함

### 3.3. 셀 타입 인식

- **true-cell:** 0 값이 방전 상태로 저장됨. 값 변환 없이 리프레시 스킵 가능
- **anti-cell:** 0 값이 충전 상태로 저장됨. 리프레시 스킵을 위해 반전(inversion) 필요
- 기존 셀 타입 식별 기법 (Kwon et al. [16], Meza et al. [42]) 활용
- 행 단위로 true-cell과 anti-cell이 혼재할 수 있으므로, 값 변환 시 셀 타입 정보 반영

### 3.4. 미할당 메모리 처리

- OS가 미할당 페이지를 0으로 채우는 특성 활용
- deallocation 시 0으로 클리닝하면, 할당 전까지 유휴 페이지가 0으로 채워짐
- true-cell 행: 0이 방전 상태 → 리프레시 스킵 가능
- anti-cell 행: 0이 충전 상태 → 값 변환으로 방전 비트로 변환 필요
- OS 및 애플리케이션 투명 동작 (새로운 인터페이스 불필요)

## 핵심 기여

- **핵심 기여:** DRAM 셀의 방전 특성을 활용한 최초의 값 인식 리프레시 절감 아키텍처 제안
- **성능 향상:** 리프레시 연산 최대 83% 절감, 에너지 최대 82% 절감, IPC 최대 10.8% 향상
- **실용성:** OS 및 애플리케이션 투명 동작, 기존 DRAM 인터페이스와의 호환성 유지
- **의의:** 메모리 용량 증가 추세에서 리프레시 에너지 문제를 근본적으로 해결하는 방향 제시. 값 변환과 셀 타입 인식을 결합한 새로운 패러다임 제시

## 주요 결과

- **시뮬레이션 기반 평가:** CACTI 6.5로 SRAM 전력 모델링, Vivado Design Suite 2017.4로 EBDI 모듈 에너지 모델링
- **EBDI 모듈:** Zynq 디바이스 (xc7z020clg484-1) 기반, 1GHz 클록에서 연산당 15pJ 소비
- **Access Bit 테이블:** 8KB SRAM, 32nm 기술에서 2.71mW 대기 누설 전력
- **DRAM 모듈 수정:** 리프레시 로직에 방전 상태 조회 로직 추가. per-bank AR 명령 지원 (LPDDR, HBM에서 이미 지원, 일반 DDR에도 최소 변경으로 적용 가능)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2020HPCA-summarize/charge-aware-dram-refresh-reduction-with-value-transformation.md|전체 요약 보기]]
