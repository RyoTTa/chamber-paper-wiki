---
tags: [paper, 2019, 2019MICRO, topic/cache, topic/dram, topic/nvm]
venue: "52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '19)"
year: 2019
summary_path: "../paper-summaries/2019MICRO-summarize/binary-star-coordinated-reliability-in-heterogeneous-memory-systems.md"
---

# Binary Star: Coordinated Reliability in Heterogeneous Memory Systems for High Performance and Scalability

**Venue:** 52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '19)
**저자:** Xiao Liu, David Roberts, Rachata Ausavarungnirun, Onur Mutlu, Jishen Zhao (UC San Diego, King Mongkut's University of Technology North Bangkok, ETH Zürich)

## 개요

- 메모리 용량 확장에 따라 전통적인 캐시/메모리 계층 구조는 높은 신뢰성과 낮은 저장/성능 비용을 동시에 보장하기 어려운 상황
- Sub-20nm DRAM 프로세스 기술로의 스케일링이 심각한 신뢰성 문제를 야기:
  - In-DRAM ECC (IECC)와 Rank-level ECC (RECC)를 결합해도 sub-20nm DRAM 기반 시스템의 신뢰성이 28nm DRAM 시스템보다 낮음
  - IECC는 DRAM 칩 내부에 ECC 엔진을 통합하여 높은 저장 오버헤드를 발생
- 3D 적층 DRAM LLC는 워크셋 수용량을 늘리지만, TSV(Through Silicon Via) 연결로 인해 BER(Bit Error Rate) 증가
- NVRAM(PCM, STT-RAM, RRAM 등)은 확장 가능한 밀도와 비용 잠재력이 있으나, DRAM 대비 낮은 내구성으로 인해 하드 에러 보호 기술이 필요
  - PCM 셀은 10^7-10^9번의 쓰기 사이클 후 마모
  - Wear leveling과 같은 하드 에러 완화 기술은 성능 및 저장 오버헤드를 초래
- 기존 퍼시스턴트 메모리 기술은 데이터 일관성을 위해 멀티버저닝, 쓰기 순서 제어(cache flush, memory barrier) 등 높은 비용을 요구
  - 코드 수정이 필요하고, 영속성이 필요 없는 애플리케이션에 불필요한 오버헤드 부과
- 핵심 문제: **LLC와 메모리 간 분리된 비조정된 신뢰성 방식**으로 인해 동일 데이터가 불필요하게 반복적으로 보호됨 (ECC 이중 적용)

## 방법론

### 3.1. 조정된 신뢰성 스킴 (Coordinated Reliability Scheme)

- **관찰 1:** LLC의 에러는 NVRAM의 일관된 데이터 사본으로 보정 가능
  - LLC 데이터는 메모리 데이터의 부분 집합 → 메모리에 일관된 사본이 유지되면 LLC 에러를 무시하거나 보정 가능
  - LLC는 CRC만 사용하여 에러 탐지 → ECC 제거로 성능/저장 오버헤드 대폭 절감
- **주기적 강제 쓰기 (Periodic forced writeback):**
  - 더러운 캐시 라인을 주기적으로 NVRAM으로 쓰기하여 체크포인트 생성
  - 체크포인트 후 모든 업데이트된 NVRAM 블록을 "일관됨"으로 표시
  - 체크포인트 간 LLC 에러 발생 시 마지막 체크포인트 이후로 롤백
  - 최적 주기: 평가에서 30분이 최적
- **일관된 캐시 쓰기 (Consistent cache writeback):**
  - 자연적 LLC 쓰기가 체크포인트 데이터와 다른 NVRAM 위치로 리다이렉트
  - 쓰기 granularity는 캐시 라인 수준 → 트랜잭션 인터페이스 불필요
  - 쓰기 순서 제어 불필요 → 기존 퍼시스턴트 메모리 기술 대비 오버헤드 대폭 절감
- **애플리케이션 투명성:** 애플리케이션 코드 수정 불필요

### 3.2. Wear Leveling과 일관된 캐시 쓰기의 조정

- **관찰 2:** NVRAM wear leveling은 데이터 업데이트를 대체 메모리 위치로 자연적으로 리다이렉트
- 기존 퍼시스턴트 메모리 시스템은 모든 커밋 시 리다이렉트가 필요하지만, wear leveling은 원래 위치가 반복적으로 덮어쓰여질 때만 리다이렉트
- Binary Star는 writeback을 NVRAM wear leveling과 동기화:
  - 체크포인트 쓰기 시 wear leveling의 리맵핑 메타데이터에 체크포인트 블록 정보 저장
  - 자연적 쓰기가 기존 리맵핑을 따르도록 하여 추가 메타데이터 관리 불필요
- 결과: 일관된 캐시 쓰기의 주소 리맵핑 비용을 기존 wear leveling 인프라에 통합

### 3.3. 에러 복구 메커니즘

- LLC에서 CRC로 에러 탐지 시:
  - 더러운 캐시 라인인지 확인 (LLC 컨트롤러가 dirty 비트 읽기)
  - 더러운 라인인 경우: 메모리 컨트롤러가 NVRAM에서 일관된 데이터를 복구 → 애플리케이션 롤백
  - 클린 라인인 경우: LLC 라인 무효화 → 캐시 미스로 NVRAM에서 ECC 보호된 사본 로드

## 핵심 기여

- **핵심 기여:** 3D DRAM LLC와 NVRAM 메모리 간 **최초의 조정된 신뢰성 스킴** 제시
- LLC에서 ECC를 제거하고 CRC만 사용하여 에러 탐지, NVRAM의 일관된 데이터 사본으로 에러 복구
- **FIT 92.9% 감소**라는 높은 신뢰성 향상과 ECC 없는 DRAM 대비 **99% 성능 유지**
- Wear leveling과 consistent cache writeback의 조정으로 추가 하드웨어/메타데이터 비용 없이 데이터 일관성 달성
- 애플리케이션 투명성 보장 (코드 수정 불필요)
- 메모리 용량 확장 시 신뢰성과 성능을 동시에 해결하는 실용적 방안 제시

## 주요 결과

- **시스템 구성:**
  - LLC: 온칩 3D 적층 DRAM (기가바이트 규모)
  - 메모리: 오프칩 NVRAM (SLC PCM, 수백 GB~테라바이트 규모)
  - 상위 캐시: SRAM
- **보정 코드:**
  - LLC: CRC (에러 탐지만)
  - NVRAM: 기존 ECC 메커니즘 활용
- **소프트웨어-하드웨어 협력 메커니즘:**
  - 하드웨어: 3D DRAM LLC 컨트롤러의 CRC 탐지, 주기적 강제 쓰기 제어
  - 소프트웨어: 에러 발생 시 애플리케이션 롤백 (체크포인트 기반 복구)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]


## 전체 요약

[[../paper-summaries/2019MICRO-summarize/binary-star-coordinated-reliability-in-heterogeneous-memory-systems.md|전체 요약 보기]]
