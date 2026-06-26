---
tags: [paper, 2019, 2019MICRO, topic/dram, topic/gpu, topic/storage]
venue: "52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '19)"
year: 2019
summary_path: "../paper-summaries/2019MICRO-summarize/deepstore-in-storage-acceleration-for-intelligent-queries.md"
---

# DeepStore: In-Storage Acceleration for Intelligent Queries

**Venue:** 52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '19)
**저자:** Vikram Sharma Mailthody (UIUC), Zaid Qureshi (UIUC), Weixin Liang (Stanford University), Ziyan Feng (UIUC), Simon Garcia de Gonzalo (UIUC), Youjie Li (UIUC), Hubertus Franke (IBM Research), Jinjun Xiong (IBM Research), Jian Huang (UIUC), Wen-mei Hwu (UIUC)

## 개요

- 딥러닝 기반 지능형 쿼리(intelligent query)가 이미지 검색, 음악 검색, 질문 답변 등 다양한 데이터 서비스에서 핵심 역할을 수행
- 지능형 쿼리는 전통적인 키 기반 쿼리와 달리 비정형 데이터에서 특징 벡터(feature vector)를 추출하여 유사도 비교를 수행하며, DNN의 비선형성으로 인해 효율적 인덱싱이 어려움
- 특징 벡터의 크기가 크고(0.8~44KB), 대규모 데이터셋(Facebook 사진/비디오 서비스 규모)의 경우 모든 특징을 메인 메모리에 상주시킬 수 없음
- 현재 GPU+SSD 시스템이 일반적이지만, **스토리지 I/O 대역폭이 쿼리 실행 시간의 56%~90%를 차지**하여 주요 병목
- 새로운 GPU(Pascal→Volta)로.compute 속도가 33% 향상되어도 스토리지 I/O 병목으로 인해 전체 성능 향상이 제한됨
- SSD 컨트롤러의 임베디드 CPU 코어는 약하여(wimpy cores) 유사도 비교 네트워크(SCN)의 복잡한 연산을 효율적으로 처리할 수 없음
- 핵심 문제: **대규모 데이터셋에 대한 지능형 쿼리의 스토리지 I/O 병목을 제거하면서 에너지 효율성을 달성하는 것**

## 방법론

### 3.1. 지능형 쿼리 워크로드 특성 분석

- **5가지 유형의 지능형 쿼리 워크로드 평가:**
  - Person Re-identification (ReId): 동일 인물 검색, 특징 벡터 44KB, CONV 2개, FC 2개
  - Music Information Retrieval (MIR): 음악 스타일 기반 검색, 특징 벡터 2KB, FC 3개
  - Exact Street to Shop (ESTP): 의류 제품 검색, 특징 벡터 16KB, FC 3개
  - Text-based Image Retrieval (TIR): 텍스트 설명 기반 이미지 검색, 특징 벡터 2KB, FC 3개
  - Text-based Question and Answer (TextQA): 문서 기반 질문 답변, 특징 벡터 0.8KB, FC 1개
- **주요 관찰:**
  - 모든 워크로드에서 스토리지 I/O가 전체 실행 시간의 56~90%를 차지
  - SCN은 주로 합성곱, 완전 연결, 요소별(element-wise) 레이어로 구성
  - wimpy SSD 컨트롤러 코어로는 SCN 연산을 효율적으로 처리 불가

### 3.2. 인스토리지 가속기 설계

- **직렬 배열(Systolic Array) 기반 공간적 아키텍처:**
  - 합성곱 및 완전 연결 레이어의 효율적 매핑 지원
  - 첫 번째 열의 각 행에 추가 입력 라인을 추가하여 요소별 연산(dot-product, subtraction, addition) 지원
  - 요소별 연산 처리량을 행 수만큼 가속
- **스크래치패드 메모리(SRAM):**
  - 쿼리 특징 벡터(QFV), 데이터베이스 특징 벡터(DFV), SCN 모델 가중치, 중간 결과를 버퍼링
  - 높은 뱅킹 구조로 직렬 배열의 병렬 요청 지원
- **컨트롤러:**
  - SSD DRAM에서 모델 가중치 로드
  - 플래시 칩에서 DFV 프리페치
  - 우선순위 큐 기반 top-K 정렬 내장
  - 이진 검색으로 태그 배열에서 새 항목 위치 탐지

### 3.3. SSD 병렬성 활용 및 설계 공간 탐색

- **SSD 레벨 가속기 (32×64 PE, 800MHz):**
  - 높은 SSD 내부 대역폭 접근 가능, 스토리지 I/O 병목 제거
  - 그러나 유사도 비교의 병렬성이 제한적 → 가장 낮은 성능
- **채널 레벨 가속기 (16×64 PE, 800MHz):**
  - 32개 채널의 병렬성 활용, 8MB 공유 스크래치패드로 가중치 32× 재사용
  - **최고의 에너지 효율성 달성:** GPU 대비 최대 78.6× 에너지 효율 향상
  - 성능: GPU+SSD 대비 3.9~17.7× 향상
- **칩 레벨 가속기 (4×32 PE, 400MHz):**
  - 128-way 병렬성 (32 채널 × 4 칩) 활용
  - 리소스 제한으로 대규모 모델(ReId) 실행 불가
  - 성능: GPU+SSD 대비 1.1~5.2× 향상
- **설계 공간 탐색 결과:**
  - 채널 레벨이 병렬성과 리소스 효율의 최적 균형점
  - 55W 전력 예산, 20GBps DRAM 대역폭, 800MBps 플래시 칩 대역폭 제약 조건 내 최적화

### 3.4. 유사도 기반 쿼리 캐시

- **핵심 아이디어:** DNN 기반 쿼리는 오차를 일정 수준 허용 → 유사한 쿼리의 결과를 캐싱하여 재사용 가능
- **Query Comparison Network (QCN):** 채널 레벨 가속기에서 실행되어 새로운 쿼리와 캐시된 쿼리 간 유사도 비교
- **Universal Sentence Encoder:** 쿼리 간 의미적 유사도 점수 계산
- **캐시 성능:**
  - Uniform 분포: 최대 25.9× 성능 향상 (DeepStore + QCache vs. GPU+SSD)
  - Zipfian 분포(α=0.7): 최대 25.9× 성능 향상
  - 오차 임계값 0%→20%로 완화 시 최대 1.7× 추가 성능 향상
  - 1K 캐시 엔트리(TIR 기준 약 22MB)로 충분한 성능 달성

### 3.5. 소프트웨어 추상화 및 API

- **writeDB / appendDB:** 특징 데이터베이스 쓰기/추가
- **loadModel:** ONNX 형식의 컴퓨팅 그래프 및 모델 가중치 로드
- **query:** 호스트에서 SSD DRAM으로 쿼리 특징 전송
- **getResults:** 쿼리 결과를 호스트 메모리로 반환
- **setQC:** QCN, 특징 벡터 크기, 임계값을 설정하여 쿼리 캐시 구성

## 핵심 기여

- **핵심 기여:** 지능형 쿼리의 스토리지 I/O 병목을 식별하고, SSD 내부에 DNN 가속기를 배치하는 최초의 인스토리지 가속 시스템 제시
- **성능 향상:** GPU+SSD 시스템 대비 최대 **17.7× 성능 향상**, 최대 **78.6× 에너지 효율 향상**
- **채널 레벨 가속기가 최적:** SSD 내부 병렬성과 가속기 리소스 효율의 최적 균형점
- **유사도 기반 쿼리 캐시:** DNN 쿼리의 오차 허용 특성을 활용하여 캐시 재사용 → 추가 성능 향상
- **저가 플래시 칩 호환:** 플래시 지연 시간이 4배 증가해도 성능 10% 미만 감소
- 대규모 데이터셋에서 지능형 쿼리의 실시간 처리를 위한 실용적 시스템 아키텍처 제시

## 주요 결과

- **구현 플랫폼:** SSD-Sim과 SCALE-Sim 기반 시뮬레이터
- **변경 사항:** 쿼리 캐시, 요소별 레이어 지원, 메모리 계층 구조 추가, 멀티 채널/칩 병렬 접근 지원
- **가속기 기술:** 32nm 공정, SSD/채널 레벨 800MHz, 칩 레벨 400MHz
- **정밀도:** 32비트 부동소수점 (원래 애플리케이션과 동일한 정확도 유지)
- **플래시 구성:** 32채널, 채널당 4칩, 칩당 8플레인, 플레인당 512블록, 블록당 128페이지, 페이지 16KB
- **데이터베이스 스트라이핑:** 특징 데이터베이스를 채널과 칩에 걸쳐 균등 분산

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2019MICRO-summarize/deepstore-in-storage-acceleration-for-intelligent-queries.md|전체 요약 보기]]
