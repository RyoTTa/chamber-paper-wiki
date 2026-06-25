---
tags: [paper, 2021, 2021HPCA, topic/cache, topic/dram, topic/gpu, topic/virtual-memory]
venue: "2021 IEEE International Symposium on High-Performance Computer Architecture (HPCA '21)"
year: 2021
summary_path: "../paper-summaries/2021HPCA-summarize/improving-gpu-multi-tenancy-with-page-walk-stealing.md"
---

# Improving GPU Multi-tenancy with Page Walk Stealing

**Venue:** 2021 IEEE International Symposium on High-Performance Computer Architecture (HPCA '21)
**저자:** B. Pratheek (Indian Institute of Science), Neha Jawalkar (Indian Institute of Science), Arkaprava Basu (Indian Institute of Science)

## 개요

- GPU 아키텍처는 단일 애플리케이션의 일부를 가속화하도록 설계되었으며, 가상 메모리 시스템은 **"대부분 공유(shared-mostly)"** 설계를 채택: 단일 애플리케이션과 하나의 주소 공간이 GPU에 상주한다는 가정
- 클라우드 인프라에서 GPU 사용이 증가하면서 **멀티 테넌시(multi-tenancy)** 필수 요구사항으로 부상: 하나의 대형 서버급 GPU의 물리적 리소스를 여러 동시 실행 테넌트 간에 공유하여 리소스 통합 및 공정성 보장
- NVIDIA MPS(Multi-Process Service) 및 MIG(Multi-Instance GPU) 등 하드웨어/소프트웨어 스택이 멀티 테넌시 지원으로 진화 중
- 가상 메모리 시스템의 두 가지 핵심 병목:
  - **공유 L2 TLB**: 여러 테넌트가 동일한 TLB 엔트리 경쟁
  - **공유 페이지 테이블 워커(PTW)**: 독립적인 페이지 워크 요청이 워커 풀에서 인터리빙되어 대기 시간 증가
- 기존 정적 파티셔닝은 리소스 비활용을 초래하고, 동적 공유는 제어되지 않는 간섭으로 성능 저하 유발

## 방법론

### 3.1. 기본 동작 원리 (DWS)

- **테넌트-워커 매핑(TWM)**: 각 테넌트에 워커 세트를 사전 할당
  - 테넌트 식별자(tenantID)로 워커 소유권 추적
  - 비트맵(bitmap)으로 각 워커의 소유 테넌트 기록
- **워커-테넌트 매핑(WTM)**: 각 워커의 소유 테넌트 추적
- **무료 워커 배열(FWA)**: 각 워커의 대기열에서 사용 가능한 슬롯 수 추적
- **동작 흐름**:
  1. 새 페이지 워크 요청 도착 시 → 소유 테넌트의 워커 중 가장 적재량 적은 워커에 배정
  2. 워커 완료 시 → 소유 테넌트에 대기 작업 있으면 서비스, 없으면 다른 테넌트에서 스틸
  3. **스틸 조건**: 소유 테넌트에 대기 페이지 워크가 **0개**일 때만 가능
  4. 인터리빙 제어: 각 테넌트의 워크는 최대 **하나의 다른 테넌트 워크**만 통과 가능 (기존 수십 개 대비 크게 감소)

### 3.2. DWS++ 향상 기능

- **공정성-성능 균형 최적화**: DWS는 특정 워크로드에서 공정성 문제 발생 가능
- **상대적 페이지 워크 생성 률 측정**: 에포크(고정된 워크 수, 기본 200개) 단위로 각 테넌트의 워크 도착 률 계산
- **차등 임계값(DIFF_THRES)**:
  - 두 테넌트의 페이지 워크 생성 률이 유사(비율 ≤ 1.5) → 공격적 스틸 허용 (DIFF_THRES = 0.4)
  - 한 테넌트가 훨씬 더 많은 워크 생성 (비율 ≥ 2) → 스틸 억제 (DIFF_THRES = 0.8)
- **대기열 점유율 임계값(QUEUE_THRES)**: 워커 자체의 대기열이 포화되면 스틸 금지
- **스틸 빈도 제어**: isstolen 비트로 연속 스틸 방지, 인터리빙 엄격히 제한
- **매개변수화된 공격성**: DIFF_THRES 조절로 처리량-공정성 간 다양한 균형점 설정 가능

### 3.3. 하드웨어 구현

- **최소한의 하드웨어 상태 추가** (16 워커, 2 테넌트 기준):
  - FWA: 80비트 (워커당 5비트 + isstolen 비트)
  - TWM: 80비트 (테넌트당 비트맵 + 카운터)
  - WTM: 32비트 (워커당 테넌트 ID)
  - 총 **192비트**
- **에포크 카운터**: 8비트 글로벌 카운터, 200 도달 시 에포크 종료
- **기존 페이지 워크 서브시스템 수정 최소화**: 기존 192 엔트리 대기열을 워커별로 분할
- **Critical path 영향 없음**: 모든 페이지 워크가 최소 1회 DRAM 접근과 대기 시간을 가지므로, DWS/DWS++ 연산은 추가 지연 없음

## 핵심 기여

- GPU 멀티 테넌시에서 **공유 페이지 워커가 L2 TLB보다 더 큰 성능 저하 원인**임을 정량적으로 입증
- **DWS**: 최소한의 하드웨어 추가(192비트)로 처리량 **37%** 향상, 인터리빙을 엄격히 제어
- **DWS++**: 동적 임계값 조절로 처리량-공정성 간 최적 균형점 설정 가능
- NVIDIA MPS/MIG 등 상용 멀티 테넌시 기술과 호환되는 실용적 솔루션
- 클라우드 환경에서 GPU 리소스 효율적 공유를 위한 가상 메모리 시스템 설계 가이드라인 제시

## 주요 결과

- **시뮬레이터**: GPGPU-Sim 기반 MASK 프레임워크 활용
- **기반 구성**: 30 SMs, 1137 MHz, GTO 스케줄러
- **가상 메모리 시스템**: 1024 엔트리 공유 L2 TLB, 16개 공유 페이지 워커, 192 엔트리 워크 대기열
- **테넌트 수**: 기본 2개, 확장 3-4개 동시 실행 지원
- **워크로드**: MAFIA 프레임워크에서 12개 벤치마크 선택, L2 TLB MPMI 기준 Light/Medium/Heavy 분류
- **총 45개 워크로드** (LL, ML, MM, HL, HM, HH 클래스)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2021HPCA-summarize/improving-gpu-multi-tenancy-with-page-walk-stealing.md|전체 요약 보기]]
