---
tags: [paper, 2020, 2020MICRO, topic/dram, topic/pim]
venue: "53rd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '20)"
year: 2020
summary_path: "../paper-summaries/2020MICRO-summarize/catcam-constant-time-alteration-ternary-cam-with-scalable-in-memory-architecture.md"
---

# CATCAM: Constant-time Alteration Ternary CAM with Scalable In-Memory Architecture

**Venue:** 53rd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '20)
**저자:** Dibei Chen, Zhaoshi Li, Tianzhu Xiong, Zhiwei Liu, Jun Yang, Shouyi Yin, Shaojun Wei, Leibo Liu* (Tsinghua University, Southeast University)

## 개요

- SDN(Software-Defined Networking) 환경에서 동적 네트워크 재구성을 위해 규칙(rule) 업데이트가 빈번하게 발생하지만, 상용 하드웨어 스위치는 초당 40~50건의 규칙 업데이트만 지원 (Open vSwitch는 42,000건/초)
- TCAM(Ternary Content-Addressable Memory)은 패킷 분류의 핵심 컴포넌트이지만, 규칙 우선순위가 물리적 주소에 종속되어 있어 삽입 시 기존 엔트리 재배치가 필요 — 최악의 경우 O(n) 시간 복잡도
- HP 5406zl 스위치 측정 결과, 규칙 설치 지연이 최대 300ms까지 발생하며, 이는 40Gbps 링크에서 64바이트 패킷 1500만 개가 도착하는 시간에 해당 (Figure 1)
- 기존 TCAM 업데이트 알고리즘(FastRule, RuleTris, POT, TreeCAM)은 최소 의존성 그래프를 활용하지만, 의존성 정보 컴파일에 상당한 시간이 소요되어 펌웨어 시간이 주요 병목
- SDN의 요구사항 충족을 위해 나노초 수준의 상수 시간(constant-time) 업데이트가 필요하지만, 기존 접근법으로는 해결 불가능

## 방법론

### 3.1. 매트릭스 기반 우선순위 인코딩 (Section III, Figure 5)

- 우선순위 행렬 P에서 Pij = true는 규칙 i가 규칙 j보다 높은 우선순위를 가짐을 의미
- **우선순위 결정 과정:**
  1. 입력 패킷이 매칭 행렬(match matrix)에서 비교 → 매칭 벡터 생성
  2. 매칭된 규칙들의 서브매트릭스를 우선순위 행렬에서 추출
  3. 각 열에 대해 리덕티브 NOR(reductive NOR) 연산 수행
  4. 결과가 true인 열이 최고 우선순위 규칙을 나타내는 원핫 리포트 벡터 생성
- **규칙 업데이트:** 빈 슬롯에 즉시 삽입 가능, 우선순위 행렬에서 해당 행/열만 업데이트 → O(1) 시간

### 3.2. 계층적 확장성 (Section IV, Figure 7-10)

- **글로벌 우선순위 행렬(Global Priority Matrix):** 서브테이블 간 우선순위 관계를 인코딩
- 규칙 우선순위 범위를 비중복 구간(non-overlapping intervals)으로 분할, 각 서브테이블에 구간 할당
- **3가지 삽입 시나리오:**
  1. **서브테이블 사용 가능:** 빈 슬롯에 즉시 삽입, 구간 변경 없음 (Figure 8)
  2. **서브테이블 가득 참:** 가장 높은/낮은 우선순위 규칙을 추방 → 후속 서브테이블로 재삽입, 구간 조정 (Figure 9)
  3. **연쇄 실할당 방지:** 빈 서브테이블을 동적으로 할당하여 추방된 규칙 수용, 글로벌 우선순위 행렬 갱신 (Figure 10)
- 어떤 시나리오에서든 최대 1개 규칙만 재배치 → O(1) 시간 보장
- 최대 우선순위 추적: 로컬 매칭 벡터를 전체 true로 설정하여 우선순위 결정 결과에서 최대 우선순위 업데이트

### 3.3. 인메모리 구현 (Section V)

- **데이터 레이아웃 (Figure 11):** 우선순위 행렬을 동일 크기의 8T SRAM 배열로 매핑
  - 매칭된 RWL(read word-line) 활성화 → RBL(read bit-line)에서 NOR 연산 결과 감지
  - 매칭 안된 열은 '0'으로 접지되어 영향 제거
- **컬럼 단위 쓰기 (Figure 12):** Dual-voltage 방식 채택
  - 데이터를 WWL(write word-line)에 적용, WBL 대신 컬럼 주소로 '1'과 '0'을 별도 사이클에 기록
  - 비대상 컬럼은 과도 구동(under-driven)으로 보호, 기존 행 단위 쓰기도 유지
  - 컬럼 쓰기 2사이클 + 행 쓰기 1사이클 = 총 3사이클로 업데이트 완료
- **매칭 행렬 (Figure 13):** 8T SRAM 셀 2개를 전치(transposed)하여 16T TCAM과 동등한 기능 구현
  - 삼진 상태 인코딩: 1→10, 0→01, *→00
  - 검색 라인(SL)과 매칭 라인(ML)로 병렬 비교 수행

### 3.4. 전체 아키텍처 (Figure 14)

- 서브테이블 집합 + 글로벌 우선순위 행렬 + 메타데이터 캐시 + 태스크 스케줄러
- **3단계 파이프라인 lookup:** 엔트리 매칭 → 글로벌 우선순위 결정 → 로컬 우선순위 결정
- 요청 버퍼링을 위한 FIFO,lookup과 업데이트가 O(1) 시간에 처리되어 상호 블로킹 없음

## 핵심 기여

- **핵심 기여:** 물리적 주소와 우선순위를 분리하는 매트릭스 기반 인코딩으로 TCAM 업데이트를 O(1) 시간으로 달성한 최초의 연구
- **성능 혁신:** 기존 최적 알고리즘(FastRule, RuleTris 등) 대비 3~6배수준의 속도 향상, 나노초 수준 업데이트
- **현실적实用性:** 0.3%功율, 20% 면적 오버헤드로 상용 TCAM과 동등한 lookup 성능 유지
- **확장성:** 계층적 서브테이블 구조로 수십만 규칙 지원, 어떤 시나리오에서든 최대 1회 재배치 보장
- **SDN 활용:** 나노초 업데이트로 동적 네트워크 재구성의 실질적 병목 해소, 네트워크 상태 일관성 보장
- **향후 과제:** (1) 병렬 업데이트 스케줄링, (2) 더 큰 용량에서의 검증, (3) 실제 SDN 스위치와의 통합

## 주요 결과

- **공정:** TSMC 28nm 풀커스텀 디자인
- **클럭 주파수:** 500 MHz
- **용량:** 40 Mb (256개 서브테이블 × 256 엔트리 = 64K 엔트리)
- **하드웨어 구성:**
  - 매칭 행렬: 4×256 서브어레이, 각 160비트 폭 → 총 640비트 검색 키
  - 우선순위 행렬: 256×256 SRAM 배열
  - 우선순위 스토어: 256×16 레지스터 파일 (16비트 OpenFlow 우선순위 필드)
  - 글로벌 우선순위 행렬: 256×256 SRAM 배열
- ** Lookup 처리량:** 500 MOPS (Million Operations Per Second)
- **Update 처리량:** 100 MOPS (평균 4.4 CPR, 28%는 3사이클, 72%는 5사이클)
- **功率:** 16.7 W
- **면적:** 48.8 mm²

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2020MICRO-summarize/catcam-constant-time-alteration-ternary-cam-with-scalable-in-memory-architecture.md|전체 요약 보기]]
