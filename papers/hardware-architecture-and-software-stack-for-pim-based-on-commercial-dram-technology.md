---
tags: [paper, 2021, 2021ISCA, topic/dram, topic/pim, topic/storage]
venue: "ISCA 2021 (48th Annual IEEE/ACM International Symposium on Computer Architecture) - Industry Track"
year: 2021
summary_path: "../paper-summaries/2021ISCA-summarize/hardware-architecture-and-software-stack-for-pim-based-on-commercial-dram-technology.md"
---

# Hardware Architecture and Software Stack for PIM Based on Commercial DRAM Technology

**Venue:** ISCA 2021 (48th Annual IEEE/ACM International Symposium on Computer Architecture) - Industry Track
**저자:** Sukhan Lee (Samsung Electronics), Shin-haeng Kang (Samsung Electronics), Jaehoon Lee (Samsung Electronics), Hyeonsu Kim (Samsung Advanced Institute of Technology), Eojin Lee (Samsung Advanced Institute of Technology), Seungwoo Seo (Samsung Advanced Institute of Technology), Hosang Yoon (Samsung Advanced Institute of Technology), Seungwon Lee (Samsung Advanced Institute of Technology), Kyounghwan Lim (Samsung Electronics), Hyunsung Shin (Samsung Electronics), Jinhyun Kim (Samsung Electronics), Seongil O (Samsung Electronics), Anand Iyer (Samsung Electronics), David Wang (Samsung Electronics), Kyomin Sohn (Samsung Electronics), Nam Sung Kim (Samsung Electronics)

## 개요

- 딥 뉴럴 네트워크(DNN), 자연어 처리(NLP), 추천 모델(RM) 등 신흥 애플리케이션은 높은 오프칩 메모리 대역폭을 요구
- 칩 패키지와 시스템 보드의 물리적 제약으로 인해 기존 DRAM의 대역폭을进一步 증가시키는 것이 매우 비용적으로 부담
- 메모리 계층 간 데이터 전송 에너지는 전체 시스템 에너지 소비의 상당 부분을 차지하며, 기술 스케일링 정체와 데이터 재사용 특성 부족으로 비율이 지속적으로 증가
- 오프칩 DRAM에서 레지스터 파일까지의 데이터 전송은 프로세서의 부동소수점(FP) 연산 대비 약 **100배** 더 많은 에너지 소비
- HBM(High Bandwidth Memory)은 높은 대역폭과 낮은 에너지를 제공하지만, 모델 크기와 컴퓨팅 밀도의 급격한 증가로 인해 여전히 메모리 병목이 발생
- 기존 PIM(Processing-in-Memory) 아키텍처는 주 프로세서 및/또는 애플리케이션 코드 수정을 요구하여 메모리 제조사의 채택이 어려움

## 방법론

### 3.1. 메모리 아키텍처

- HBM2 구조를 기반으로 하며, 각 DRAM 은행에 PIM 실행 유닛을 통합
- **표준 모드(SB)**: 일반 HBM으로 동작하며, 기존 DRAM 인터페이스와 완전 호환
- **PIM 모드(AB-PIM)**: 은행 수준 병렬성을 활용한 PIM 작업 모드
- DRAM 은행의 내부 대역폭(I/O 대역폭 대비 10배 이상)을 프로세서에 직접 노출
- 4개의 PIM-HBM 디바이스 통합 시 최대 **4배** 높은 온칩 대역폭 제공

### 3.2. PIM 실행 유닛

- 각 DRAM 은행에 연결된 16비트 부동소수점(FP16) 곱셈-누적(MAC) 유닛
- 256비트 그래픽 레지스터 파일(GRF) 탑재
- 드라마 쓰기 데이터 경로를 통해 32바이트 벡터 데이터 수신
- DRAM 읽기 명령을 통해 결과 데이터 전송
- **GEMV(GEMM-Vector)**: 가중치 행렬과 입력 벡터의 곱셈 연산에 최적화
- **ADD**: 원소별 덧셈 연산 지원
- **BN(Batch Normalization)**: 배치 정규화 연산 지원

### 3.3. 명령어 세트 및 데이터 레이아웃

- **PIM 명령어**: 표준 DRAM 명령어(READ, WRITE)의 확장으로 구현
- 128바이트 정렬된 주소 경계에 벡터 데이터 배치 (Figure 15)
- PIM BLAS API가 GEMV 연산 시 데이터 레이아웃을 자동으로 재배치
- 벡터 크기가 128바이트의 배수가 아닌 경우 더미 값으로 패딩

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1. PIM BLAS 라이브러리

- 기존 BLAS(Basic Linear Algebra Subprograms) 인터페이스와 호환되는 PIM 가속화 라이브러리
- TensorFlow, PyTorch 등 ML 프레임워크와无缝하게 통합
- MKL, oneAPI(MKL-DNN), CuDNN, MIOpen 등 기존 API와 호환

### 4.2. 캐시 바이패스 및 데이터 관리

- PIM이 작동하는 메모리 영역은 캐시에서 제외하거나 PIM 시작 전 캐시된 데이터를 플러시해야 함
- ARMv8의 LDNP/STNP 명령어를 활용한 캐시 바이패스 기법 적용
- 캐시에서 제외함으로써 캐시 간섭 및 경합 감소 → PIM 워크로드 성능 향상

### 4.3. 데이터 배치 및 메모리 인터리빙

- 호스트 프로세서가 각 메모리 채널의 PIM 작업을 독립적으로 제어 가능
- PIM 실행 유닛이 호스트 프로세서와 동일한 데이터 접근 세밀함으로 메모리 접근
- 물리 주소 매핑 체계에 대한 아키텍처적 무관성 달성
- 128바이트 정렬 경계에 두 개의 피연산자를 배치하는 데이터 레이아웃 (Figure 15)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2021ISCA-summarize/hardware-architecture-and-software-stack-for-pim-based-on-commercial-dram-technology.md|전체 요약 보기]]
