---
tags: [paper, 2020, 2020MICRO, topic/cache, topic/dram, topic/nvm, topic/virtual-memory]
venue: "53rd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '20)"
year: 2020
summary_path: "../paper-summaries/2020MICRO-summarize/characterizing-and-modeling-non-volatile-memory-systems.md"
---

# Characterizing and Modeling Non-Volatile Memory Systems

**Venue:** 53rd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '20)
**저자:** Zixuan Wang, Xiao Liu, Jian Yang*, Theodore Michailidis, Steven Swanson, Jishen Zhao (University of California, San Diego)

## 개요

- Intel Optane DC Persistent Memory(Optane DIMM)가 최초의 서버급 NVRAM DIMM 제품으로 출시되었으나, 기존 연구에서 가정한 성능 특성과 실측 결과 간 상당한 차이 존재
- 기존 NVRAM 에뮬레이터(PMEP, Quartz)는 DRAM을 단순히 느린 메모리로 모델링하지만, 실제 Optane DIMM은 훨씬 복잡한 성능 거동을 보임 (Figure 1)
  - PMEP는 load/store 대역폭을 non-temporal store보다 높게 모델링하지만, 실제 Optane에서는 non-temporal store가 더 높은 대역폭 달성
  - PMEP는 안정적인 read 레이턴시를 시뮬레이션하지만, 실제 Optane은 포인터 추적 영역 크기에 따라 레이턴시가 3개 구간으로 증가
- 기존 메모리 시뮬레이터(DRAMSim2, Ramulator)도 Optane DIMM의 성능 특성을 정확히 모델링하지 못함 (Figure 3)
  - 평균 정확도가 현저히 낮으며, 포인터 추적 테스트에서 레이턴시 곡선이 안정적으로 시뮬레이션됨
- 기존 프로파일링 도구(MLC, perf, DRAMA)는 Optane DIMM의 on-DIMM 버퍼 구조를 분석할 수 없음 (Table I)
- 산업 문서는 Optane DIMM의 복잡한 마이크로아키텍처를 암시하지만, 상세 정보를 공개하지 않음

## 방법론

### 3.1. 마이크로벤치마크 (Table II)

- **Pointer Chasing:** 임의 메모리 접근 벤치마크, 버퍼 오버플로우 및 증폭 측정
  - 변형 1: 고정 PC-Block 크기, 다양한 PC-Region 크기 → 평균 레이턴시 측정
  - 변형 2: 고정 PC-Region, 다양한 PC-Block → 읽기/쓰기 증폭 정량화
  - 변형 3: 읽기 후 쓰기(RaW) 요청 → 데이터 패스포워딩 효과 분석
- **Overwrite:** 고정 메모리 영역에 반복 쓰기, 실행 시간 측정
  - 변형 1: 고정 영역, 각 반복의 실행 시간
  - 변형 2: 다양한 영역 크기로 롱 테일 레이턴시 빈도 측정
- **Stride:** 고정 스트라이드 거리로 순차 읽기/쓰기
  - 변형 1: 고정 스트라이드, 접근 크기 증가 → 대역폭 측정
  - 변형 2: 고정 총 접근 크기, 가변 스트라이드 → 멀티-DIMM 인터리빙 분석

### 3.2. 버퍼 프로버 (Buffer Prober)

- **버퍼 용량 탐지:** PC-Region 크기를 점진적으로 증가시키며 레이턴시 변화 관찰
  - Optane DIMM에서 읽기 레이턴시가 16KB와 16MB에서 급격히 증가 → 2단계 읽기 버퍼 존재 확인
  - 쓰기 레이턴시는 512B와 4KB에서 변화 → WPQ(Write Pending Queue)와 LSQ(Load-Store Queue) 식별
- **버퍼 조직 분석:**
  - 레이턴시 곡선의 굴곡점 수 = 상이한 용량의 버퍼 수
  - RaW(Read-after-Write) 테스트로 포함 관계(inclusive) vs. 독립 버퍼 판단
  - Optane DIMM은 RMW Buffer와 AIT Buffer가 2단계 포함 계층(inclusive hierarchy)으로 구성
- **접근 세분성:** 읽기/쓰기 증폭 점수(amplification score)로 각 버퍼의 엔트리 크기 결정
  - RMW Buffer: 256B, AIT Buffer: 4KB, WPQ: 512B, LSQ: 256B

### 3.3. Optane DIMM 마이크로아키텍처 (Figure 4, 8)

- **iMC 내부:**
  - WPQ(Write Pending Queue): ADR(Asynchronous DRAM Refresh) 도메인, 데이터 지속성 보장
  - 멀티-DIMM 인터리빙: 4KB 단위 인터리빙 (LSQ 및 AIT Buffer 엔트리 크기와 일치)
- **DIMM 내부:**
  - **RMW Buffer:** 16KB SRAM 기반, 256B 접근 세분성, 읽기-수정-쓰기 작업 수행
  - **AIT Buffer:** 16MB DRAM 기반, 4KB 접근 세분성, 주소 간접 변환(AIT) 테이블 및 데이터 버퍼 포함
  - **LSQ:** 4KB 용량, 읽기/쓰기 요청 재ordering으로 쓰기 결합(write combining) 수행
  - **테일 레이턴시:** ~14,000회 쓰기마다 발생 (약 3.4MB 간격), 100배 이상의 레이턴시 패널티 → 웨어-레벨링 데이터 마이그레이션 추정
  - 웨어-레벨링 블록 크기: 64KB 이상 오버라이트 시 테일 레이턴시 빈도 급감

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1. 시뮬레이션 모델 설계 (Figure 8)

- **모듈형 구현:** iMC와 NVRAM DIMM을 독립적으로 모델링, 다양한 아키텍처 탐색 가능
- **iMC 모델:** 멀티-DIMM 제어, WPQ(ADR 도메인), 요청/grant 통신 체계
- **NVRAM DIMM 모델:**
  - LSQ: 최상위 스토리지, iMC에서 직접 요청 수용, 쓰기 결합 수행
  - RMW Buffer: LSQ에서 요청 수용, AIT Buffer와 256B 단위 통신
  - AIT Buffer: 번역 테이블(CPU 주소→미디어 주소) + 데이터 버퍼, 웨어-레벨링 기록 관리
  - 스케줄링: FCFS(First-Come-First-Serve) 기본 정책
- **온-DIMM DRAM:** DDR4 프로토콜 기반 타이밍 모델링

### 4.2. DRAM 모델 검증

- Micron DDR4 검증 모델과 Cadence 도구체인으로 SPEC2006/2017 트레이스 검증
- 불법 DDR4 명령어 미발생 확인 → DDR4 사양 준수 입증

### 4.3. 마이크로벤치마크 검증 (Figure 9)

- **포인터 추적 단일-DIMM:** 쓰기 레이턴시 오차 < 10% (전체 접근 영역), 읽기 레이턴시 경향 정확히 모델링
- **포인터 추적 6-DIMM 인터리빙:** 평균 12% 차이
- **RMW Buffer 읽기 증폭:** 오차 9% 이내
- **테일 레이턴시:** 길이 및 간격에서 실측과 일치
- **전체 정확도:** 4개 지표 기준 평균 **86.5% 정확도** (Figure 9e)

### 4.4. SPEC CPU 벤치마크 검증 (Figure 11)

- VANS+gem5 풀시스템 시뮬레이션 vs. 실측 비교
- DRAM 기반 시뮬레이션: IPC 평균 61.2% 정확도, LLC miss율 85.5% 정확도 (gem5 제한)
- NVRAM 기반 시뮬레이션: **VANS+gem5 평균 87.1% 정확도** vs. **Ramulator+gem5 65.6% 정확도**
- 민감도 분석: DIMM 용량 변화가 지연 시간 곡선에 미치는 영향 미미 (버퍼로 미디어 레이턴시 은닉)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2020MICRO-summarize/characterizing-and-modeling-non-volatile-memory-systems.md|전체 요약 보기]]
