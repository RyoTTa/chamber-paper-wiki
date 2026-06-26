---
tags: [paper, 2018, 2018ISCA, topic/cache, topic/dram]
venue: "International Symposium on Computer Architecture (ISCA) 2018"
year: 2018
summary_path: "../paper-summaries/2018ISCA-summarize/nonblocking-memory-refresh.md"
---

# Nonblocking Memory Refresh

**Venue:** International Symposium on Computer Architecture (ISCA) 2018
**저자:** Kate Nguyen, Kehan Lyu, Xianze Meng (Virginia Tech), Vilas Sridharan (AMD), Xun Jian (Virginia Tech)

## 개요

- DRAM은 50년 이상 컴퓨터 메인 메모리로 사용되어 왔으나, 동적/활성 갱신(dynamic/active refresh) 연산이 필수적
- 갱신 연산은 읽기 요청을 차단(block)하여 성능을 저하시킴
- DRAM vs SRAM: DRAM은 커패시터 충전 유지를 위해 주기적 갱신 필요, SRAM은 래치 피드백으로 정적/배경 갱신 가능
- 세대별 DRAM에서 갱신 지연 시간(refresh latency)이 지속적으로 증가:
  - DDR에서 DDR4까지 최소 읽기 지연 시간 대비 갱신 지연 시간 비율 증가
  - 16Gb DRAM 칩: tRFC = 550ns, 32Gb 칩: 더 큰 값
- 기존 완화 기술의 한계:
  - 지능적 갱신 스케줄링: 제한된 효과
  - 갱신 스킵(skip): 보안 및 신뢰성 저하 → 보안/신뢰성이 중요한 시스템에 적합하지 않음
  - 서버 메모리 시스템은 이미 하드웨어 장애 보호를 위한 중복 데이터(redundant data)를 포함 → 미이용 여유 존재

## 방법론

### 3.1. 메모리 블록 단위 갱신
- 기존: 전체 메모리 블록을 한 번에 갱신 → 차단(blocking)
- 제안: 블록의 일부만 갱신하면서 나머지 데이터를 Reed-Solomon 코드 등으로 계산
- 갱신 주기(tRFC) 동안 더 자주 백그라운드에서 부분 갱신 수행
- 읽기 요청이 갱신 중인 블록에 도달하면 중복 데이터로 누락된 데이터 계산

### 3.2. 서버 메모리 시스템 활용
- 서버 메모리의 기존 칩킬 코렉트(chipkill-correct) 기능 활용
- SCC (Single Chipkill-Correct): 2개의 체크 바이트로 1개 칩 장애 탐지/교정
- MCC (Multiple Chipkill-Correct): 4개의 체크 바이트로 최대 2개 칩 장�� 대응
- RAIM (Redundant Array of Independent Memories): 45개 칩/rank, DIMM 전체 장애 허용
- 장애가 없을 때: 체크 바이트를 갱신 중인 데이터 계산에 재사용
- 장애 발생 시: 랭크가 갱신을 완료한 후 다시 읽기 → 기존 교정 능력 유지

### 3.3. 쓰기 버퍼 관리
- Little's Law로 쓰기 버퍼 크기 결정: 약 28KB (3.2GHz, 64비트 와이드 채널 기준)
- 쓰기 그룹(write group) 선택: 가장 많이 점유한 세트 기반 라운드로빈 방식
- tRFC 간격마다 활성 쓰기 그룹 1개 선택하여 해당 간격 동안 쓰기 허용
- 임계 점유율 미만 시: 모든 쓰기 그룹이 Nonblocking Refresh 수행

### 3.4. 장애 보존(Failure Protection) 충분 조건
- A) 물리적/원시 고장률 증가 없음 (기존과 동일한 갱신 수행)
- B) 동일한 오류 탐지 강도 (블록당 동일한 양의 중복 데이터)
- C) 동일한 오류 교정 강도 (오류 발견 시 다시 읽기 → 기존 교정 능력 유지)
- 그림 9: 읽기 동작 흐름도 (오류 발견 시 재읽기, 없으면 erasure correction)

## 핵심 기여

- Nonblocking Refresh는 DRAM을 SRAM처럼 시스템 수준에서 배경 갱신이 가능하도록 변환
- 서버 메모리의 기존 중복 데이터를 활용하여 추가 하드웨어 비용 없이 구현
- 16Gb 칩에서 16.2%, 32Gb 칩에서 30.3% 성능 향상
- 갱신 지연 시간이 증가하는 고밀도 DRAM 시대에 효과적인 해결책
- 보안/신뢰성을 저하시키지 않으면서 성능을 크게 향상시키는 실용적 접근

## 주요 결과

- 메모리 컨트롤러(MC)에 쓰기 버퍼(set-associative writeback cache) 추가
- 쓰기 그룹 관리 로직
- Reed-Solomon 또는 유사 erasure 코드 기반 데이터 계산
- 서버 메모리의 기존 칩킬 코렉트 기능과의 통합

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2018ISCA-summarize/nonblocking-memory-refresh.md|전체 요약 보기]]
