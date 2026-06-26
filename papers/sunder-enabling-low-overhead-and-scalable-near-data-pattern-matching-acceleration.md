---
tags: [paper, 2021, 2021MICRO, topic/cache, topic/pim]
venue: "MICRO 2021 (54th Annual IEEE/ACM International Symposium on Microarchitecture)"
year: 2021
summary_path: "../paper-summaries/2021MICRO-summarize/sunder-enabling-low-overhead-and-scalable-near-data-pattern-matching-acceleration.md"
---

# Sunder: Enabling Low-Overhead and Scalable Near-Data Pattern Matching Acceleration

**Venue:** MICRO 2021 (54th Annual IEEE/ACM International Symposium on Microarchitecture)
**저자:** Elaheh Sadredini (University of California, Riverside), Reza Rahimi (University of Virginia), Mohsen Imani (University of California, Irvine), Kevin Skadron (University of Virginia)

## 개요

- 정규표현식 기반 패턴 매칭은 네트워크 침입 탐지, 스팸 필터, 바이오인포매틱스 등 다양한 응용에서 필수적이나, 패턴의 수가 방대하고 구조가 복잡하여 기존 von Neumann 아키텍처로는 실시간 처리 요구사항 충족이 어려움
- 기존 인메모리 오토마타 처리 아키텍처(Micron AP, Impala, Cache Automaton)는 **95%의 응용에서 리포팅 단계가 주요 병목**이나, 리포팅 비용을 낙관적으로 무시하거나 실제 리포팅 오버헤드를 정확히 고려하지 않음
  - Micron AP의 리포팅 아키텍처: **40% 면적 오버헤드**, **최대 46x 성능 오버헤드** (스톨 및 호스트 통신)
  - Snort 벤치마크에서 AP-style 리포팅 사용 시 **46x 느려짐**
  - 19개 벤치마크 중 **7개에서 리포팅 오버헤드가 오토마타 전이 처리 시간보다 큼**
- 기존 인메모리 아키텍처는 **고정된 8-bit/cycle 처리 속도**를 사용하여 응용 특성에 따른 처리 속도 조정 불가 → 스루풋 및 용량 손실
- Impala는 하드웨어적으로 고정된 16-bit/cycle 처리를 제공하나, 재구성이 불가능하고 복수의 서브어레이를 병렬 사용 시 최종 결과 집계를 위한 추가 하드웨어 필요

## 방법론

### 3.1. Nibble Processing 변환

- 기존 8-bit 오토마타 처리: 각 서브어레이에서 **2^8 = 256행** 필요
- 4-bit nibble 처리: **2^4 = 16행**만 필요 → 메모리 사용량 대폭 감소
- Table 3: 1-nibble(4-bit) 변환 시 평균 **3.1x** 상태 수 감소, **4.5x** 전이 수 감소
- 4-nibble(16-bit) 변환 시: 평균 **1.2x** 상태 수, **1.8x** 전이 수 변화
- Impala와 달리 **하드웨어적으로 재구 가능한 처리 속도** 지원

### 3.2. In-Situ Reporting 아키텍처

- **8T SRAM 셀** (Figure 6): 기존 6T SRAM 셀에 2개 트랜지스터 추가
  - **Port 1**: 상태 매칭 서브어레이 초기 구성 + 리포팅 데이터 읽기/쓰기
  - **Port 2**: 상태 매칭 연산 수행 (읽기 전용)
  - 두 포트를 동시에 사용하여 상태 매칭과 리포팅을 **병렬 처리**
- **리포팅 데이터 위치**: 상태 매칭 서브어레이 내에 직접 저장 (in-place)
  - 각 오토마타에 **독점적 리포팅 버퍼** 제공 → 공유 버스 충돌 방지
  - 12비트 리포팅 데이터 + 20비트 메타데이터 per 상태

### 3.3. 리포팅 최적화 기법

- **Report Summarization**: 
  - Port 2를 사용하여 리포팅 행들 간의 **column-wise NOR 연산** 수행
  - 상태 매칭은 1-2 사이클 동안 스톨
  - 빈번한 리포팅이 필요한 응용에서 **I/O 비용 대폭 절감**
- **Selective Reporting**: 호스트가 어떤 사이클이든 모든 상태의 리포팅 상태를 **상수 시간에** 읽기 가능
- **FIFO Strategy**: 
  - 실제 응용 분석 결과: 전체 실행 사이클의 **12% 미만에서만 리포팅 발생** (Table 1)
  - 리포팅 데이터를 버퍼 시작점부터 순차적으로 읽기 → Port 1(리포팅 읽기)과 Port 2(상태 매칭)를 동시에 사용
  - 리포팅 버퍼가 가득 찬 경우에만 스톨 발생

### 3.4. 인터커넥트

- **메모리 매핑 방식의 풀 크로스바 인터커넥트**: 8T SRAM 스위치 셀 사용
- 각 열이 하나의 상태에 대응, 모든 행과 교차 → 최대 256개 상태 간 연결 지원
- 인터커넥트 혼잡 없이 고도로 연결된 NFA도 처리 가능
- wired-NOR 기능으로 상태 전이 조건 충족 여부 효율적 판정

### 3.5. 시스템 통합

- Intel Xeon의 **LLC(Last Level Cache) 리퍼포징** 방식으로 구현 가능
  - Sandy Bridge 마이크로아키텍처: LLC가 독립 슬라이스로 분할, 링 토폴로지로 연결
  - **CAT(Cache Allocation Technology)**로 특정 캐시_way 접근 제한
  - 1GB 페이지 크기(mmap)로 물리 주소 매핑
  - `/proc/self/pagemap`으로 가상-물리 주소 변환

## 핵심 기여

- **핵심 기여**: In-SRAM 패턴 매칭 가속기에서 **리포팅 오버헤드 문제를 근본적으로 해결**하는 최초의 아키텍처
- **성능 향상**: Micron AP 대비 **280x**, 기존 SRAM 기반 최신 해법(CA, Impala) 대비 **4x ~ 22x** 스루풋 향상
- **리포팅 혁신**: 95% 응용에서 **제로 리포팅 오버헤드**, 하드웨어 추가 비용 **2% 미만**
- **재구성 유연성**: 4-bit/8-bit/16-bit/cycle 처리 속도를 응용 특성에 따라 선택 가능
- **의의**:
  - 인메모리 오토마타 처리의 상용화 가능성 제고 (단위 면적당 스루풋 3 orders of magnitude 향상)
  - 네트워크 보안, 바이오인포매틱스, 데이터 마이닝 등 실시간 패턴 매칭 응용의 실용화 촉진
  - 기존 아키텍처들이 간과했던 리포팅 단계의 중요성을 조명하고 체계적 해결책 제시

## 주요 결과

| 항목 | 내용 |
|------|------|
| **시뮬레이터** | 오픈소스 in-house Automata compiler and simulator |
| **기술 노드** | 14nm (표준 메모리 컴파일러 기반) |
| **SRAM 셀** | 8T SRAM (상태 매칭 + 리포팅), 6T SRAM (비교용) |
| **서브어레이 크기** | 256×256 (Sunder), 16×16 (Impala) |
| **최대 주파수** | 4.01 GHz (상태 매칭), 3.6 GHz (글로벌 스위칭) |
| **처리 속도** | 4-bit, 8-bit, 16-bit/cycle 재구 가능 |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2021MICRO-summarize/sunder-enabling-low-overhead-and-scalable-near-data-pattern-matching-acceleration.md|전체 요약 보기]]
