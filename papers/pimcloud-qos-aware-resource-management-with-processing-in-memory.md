---
tags: [paper, 2022, 2022HPCA, topic/dram, topic/pim]
venue: "IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2022"
year: 2022
summary_path: "../paper-summaries/2022HPCA-summarize/pimcloud-qos-aware-resource-management-with-processing-in-memory.md"
---

# PIMCloud: QoS-Aware Resource Management of Latency-Critical Applications in Clouds with Processing-in-Memory

**Venue:** IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2022
**저자:** Shuang Chen (Cornell University), Yi Jiang (Cornell University), Christina Delimitrou (Cornell University), José F. Martínez (Cornell University)

## 개요

- Moore's Law의 둔화와 함께 3D 적층(3D Stacking) 로직+메모리 기술의 발전으로 프로세싱-인-메모리(PIM: Processing-in-Memory) 아키텍처가 벤 노이만 병목(von Neumann bottleneck)을 해결하기 위한 주요 후보로 부상
- 기존 PIM 연구는 대부분 처리량 중심(Best-Effort) 워크로드에 초점을 맞추고 있으며, 클라우드 환경에서 지연 시간이 중요한(Latency-Critical) 애플리케이션에 대한 PIM의 영향은 충분히 연구되지 않음
- 클라우드 데이터센터에서는 지연 시간이 핵심 성능 지표이며, 마이크로서비스의 확산으로 인해 마이크로초 수준의 QoS 제약이 요구됨
- PIM 아키텍처의 잠재력을 클라우드 애플리케이션에 적용하기 위해 해결해야 할 과제:
  - 다양한 클라우드 애플리케이션 유형에 대응할 수 있는 범용 PIM 아키텍처의 필요성
  - 지연 시간 중요 애플리케이션(LC: Latency-Critical)에 대한 PIM의 영향 정량화
  - PIM 리소스를 인식하는 적응형 자원 관리 기법의 부재

## 방법론

### 3.1. PIM 아키텍처 특성 분석

- **HBM 기반 3D 적층 로직+메모리 모듈**: 각 PIM 스택에 저지연 와이미 코어가 로직 레이어에 통합
- Table III에서 9가지 아키텍처(Arch 1-9)를 체계적으로 특성화:
  - **CPU-centric (Arch 1-4)**: 높은 메모리 지연 시간, 브로니(Brawny)/와이미 코어, 깊이/얕은 메모리 계층
  - **Unrealistic (Arch 5-6)**: 낮은 메모리 지연 시간 + 브로니 코어 (실현 불가)
  - **PIM-centric (Arch 7-9)**: 낮은 메모리 지연 시간, 와이미 코어,얕은 메모리 계층
- **핵심 발견**: PIM-centric 아키텍처(Arch 8)가 평균적으로 모든 CPU-centric 아키텍처보다 높은 최대 부하(Max Load) 달성
- 각 애플리케이션의 PIM 선호도가显著히 다름: Masstree는 약간의 개선, Sphinx는 PIM에서 최대 부하가 2배 이상 향상

### 3.2. 데이터 배치(Data Placement) 전략

- PIM 스택 간 교차 스택 메모리 접근의 지연 시간 차이가 성능에 significant 영향
- **정적 데이터 배치 정책** (Figure 3):
  - **Interleaving (IL)**: 모든 페이지를 노드 간 인터리빙
  - **First-touch (FT)**: 첫 접근 시 해당 노드에 할당 — Sphinx에서 IL/CC보다 최대 46% 우수
  - **Concentrated (CC)**: 가능한 적은 노드에 집중 할당
- **동적 데이터 배치**:
  - **페이지 마이그레이션**: 프라이빗 페이지를 로컬 스택으로 마이그레이션 — Sphinx에서 최대 40% 개선
  - **페이지 복제**: 공유 읽기 전용 페이지를 원격 스택에 복제 — ImgDNN에서 최대 20% 개선
- Figure 4에서 메모리 페이지 접근 유형별 분해: 프라이빗/공유, 읽기전용/읽기쓰기 구분

### 3.3. PIMCloud 자원 관리 알고리즘

- **R-value 기반 앱 순위**: 각 애플리케이션의 CPU/PIM 선호도를 정량화하여 순위 결정
- **Downsize(A)**: 여유 자원이 있는 애플리케이션에서 자원을 회수하여 BE 풀로 이동
  - 다운사이즈 임계값(Threshold)을 유지하여 과도한 다운사이즈 방지
- **Upsize(A)** (Algorithm 2): QoS 위반 애플리케이션에 자원 추가 할당
  - 게으른(Lazy) 방식: 순차적으로 자원 이전
  - 적극적(Eager) 방식: 남은 애플리케이션에서 적극적으로 자원 회수
  - 원격 PIM 코어 할당 시 페이지 마이그레이션/복제 수행
- **adjustCore(A, count)**: 코어 수 조정 시 PIMCloud 규칙 만족 보장
  - count=+1: CPU 코어 우선 할당, 불가 시 로컬/원격 PIM 코어 할당
  - count=-1: CPU 코어 우선 회수, 불가 시 원격/로컬 PIM 코어 회수
- **적응형 모니터링**: 자원 조정 후 지연 시간 안정화까지 대기 시간을 동적으로 조절

### 3.4. 시스템 오버헤드

- 코어 할당 조정: 리눅스 taskset 등 기존 OS 인터페이스 활용 (약 100μs/조정)
- 페이지 조작: 1μs/4KB 페이지 또는 250ms/1GB
- 페이지 접근 빈도 모니터링: 페이지 테이블 엔트리에 접근 빈도 필드 추가, 요청 처리 크리티컬 패스에 없음
- 특수 시스템 호출: 스택에서 n개 최다 접근 페이지 반환 (10ms 이내)

## 핵심 기여

- **핵심 기여**: PIM을 인식하고 QoS를 고려한 최초의 클라우드 자원 관리자 PIMCloud를 제안하여, LC 애플리케이션과 BE 애플리케이션의 혼용을 효율적으로 관리
- **성능**: 유효 기계 활용도(EMU)를 기존 최신 기법(Octopus-Man) 대비 평균 24% 향상 (최대 70%)
- **실용성**: 기존 OS 인터페이스(taskset, 페이지 마이그레이션)를 활용하여 낮은 오버헤드로 구현 가능
- **PIM의 잠재력**: 지연 시간 중요 클라우드 애플리케이션에서도 PIM이 significant 성능 이점을 제공할 수 있음을 최초로 규명
- **의의**: 클라우드 데이터센터에서 PIM 기술의 실용적 도입을 위한 자원 관리 프레임워크를 제시하여, 향후 PIM 기반 클라우드 시스템 설계에 기여

## 주요 결과

- **시뮬레이터**: 사이클 레벨 멀티코어 시뮬레이터 사용
- **시스템 설정**:
  - PIM 스택: 로직 레이어 면적 예산 50mm² (22nm 공정 기준)
  - 와이미 코어: CPU 코어 대비 약 1/4 면적 (약 5mm²)
  - 16개 와이미 코어를 2개 메모리 스택에 분산 배치 (스택당 8개)
- **애플리케이션**: 6개 LC 서비스 — Silo(인메모리 DB), Masstree(키-값 스토어), ImgDNN(이미지 인식), Xapian(웹 검색), Moses(실시간 번역), Sphinx(음성 인식)
- **QoS 목표**: Silo/Masstree 1ms, ImgDNN 7ms, Xapian/Moses 10ms, Sphinx 6ms

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2022HPCA-summarize/pimcloud-qos-aware-resource-management-with-processing-in-memory.md|전체 요약 보기]]
