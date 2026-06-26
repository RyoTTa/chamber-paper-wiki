---
tags: [paper, 2022, 2022ISCA, topic/nvm, topic/storage]
venue: "ISCA 2022 (The 49th Annual International Symposium on Computer Architecture)"
year: 2022
summary_path: "../paper-summaries/2022ISCA-summarize/sibyl-adaptive-and-extensible-data-placement-in-hybrid-storage-systems-using-rl.md"
---

# Sibyl: Adaptive and Extensible Data Placement in Hybrid Storage Systems Using Online Reinforcement Learning

**Venue:** ISCA 2022 (The 49th Annual International Symposium on Computer Architecture)
**저자:** Gagandeep Singh, Rakesh Nadig, Jisung Park, Rahul Bera, Nastaran Hajinazar, David Novo, Juan Gómez-Luna, Sander Stuijk, Henk Corporaal, Onur Mutlu (ETH Zürich / Eindhoven University of Technology / LIRMM, Univ. Montpellier, CNRS)

## 개요

- 하이브리드 스토리지 시스템(HSS)은 빠르지만 작은 스토리지 장치와 느리지만 큰 스토리지 장치를 결합하여 높은 성능과 확장 가능한 저장 용량을 제공
- 핵심 과제: 성능에 민감한 데이터(performance-critical data)를 정확히 식별하여 "best-fit" 스토리지 장치에 배치하는 것
- 기존 데이터 배치 기술의 두 가지 주요 한계:
  1. **적응성 부족 (workload 변화):** 과거 기술들은 제한된 수의 workload 특성만 고려하고, 설계 시점에 고정된 파라미터 값을 사용하여 다양한 동적 workload 수요에 적응하지 못함
  2. **적응성 부족 (장치 유형/구성 변화):** 대부분의 기존 기술들은 스토리지 장치 특성 변화(읽기/쓰기 지연 시간 비대칭성, 장치 수/유형 변화)에 잘 적응하지 못함
  3. **확장성 부족:** 대부분의 기존 기술들은 두 개의 스토리지 장치로 구성된 HSS를 위해 설계됨. 현대 HSS는 세 개 이상의 장치를 통합하므로, 기존 기술을 확장하기 위해 시스템 설계자가 많은 노력 필요
- 기존 기술들의 성능 격차: 오라클 기법(미래 접근 패턴에 대한 완전한 지식 보유) 대비 최대 **41.1%** 낮은 성능

## 방법론

### 3.1. RL 기반 데이터 배치 공식화

- **상태(State):** 워크로드와 스토리지 시스템의 다양한 특성 관찰
  - 현재 요청의 접근 카운트(access count)
  - 빠른 스토리지의 남은 용량(remaining capacity)
  - 기타 시스템 특성
- **행동(Action):** 데이터를 어떤 장치에 배치할지 결정
- **보상(Reward):** 요청 지연 시간(per-request latency)을 기반으로 한 지연 보상(delayed reward)
  - 내부 장치 특성 반영: 읽기/쓰기 지연 시간, 가비지 컬렉션 지연, 큐잉 지연, 에러 처리 지연, 쓰기 버퍼 상태
  - eviction 발생 시 음의 패널티 추가 → credit assignment 문제 해결 및 성능에 민감한 페이지만 빠른 스토리지에 배치하도록 유도

### 3.2. 구현 과제 해결

- **상태 공간 축소:** 상태를 소수의 bin으로 나누어 상태 공간을 대폭 줄임
- **신경망 기반 Q-러닝:**
  - 기존 테이블 기반 RL 접근 방식 대신 간단한 피드포워드 신경망 사용
  - 두 개의 은닉층: 20개 노드, 30개 노드
  - 대규모 상태/행동 공간에서도 낮은 구현 오버헤드 달성
- **하이퍼파라미터 튜닝:** 다양한 workload에서 잘 작동하는 파라미터 값을 철저히 탐색

### 3.3. 시스템 구성 및 확장성

- **듀얼 HSS:** 빠른 장치(NVM SSD) + 느린 장치(NAND SSD/HDD) 구성
- **트라이 HSS:** 세 개의 서로 다른 스토리지 장치를 가진 구성으로 확장 가능
- **구현 위치:** 호스트 시스템의 운영 체제(OS) 스토리지 관리 레이어에서 구현 (또는 FTL과 같은 스토리지 펌웨어에서도 가능)

## 핵심 기여

1. **기존 HSS 데이터 배치 기술의 한계 확인:** 적응성 부족( workload 변화, 장치 특성 변화) 및 확장성 부족(두 장치 기반 설계)
2. **강화학습 기반 데이터 배치의 효과 입증:** 듀얼 HSS에서 최고 기존 기술 대비 21.6%/19.9%, 트라이 HSS에서 23.9%~48.2% 성능 향상
3. **온라인 학습으로 다양한 workload와 시스템 구성에 적응:** 학습되지 않은 워크로드에서도 감독 학습 기반 기술보다 46.1%/54.6% 우수한 성능
4. **낮은 구현 오버헤드:** 124.4 KiB의 저장 공간으로 실용적 구현 가능
5. **오라클 기법의 80% 성능 달성:** 미래 접근 패턴에 대한 완전한 지식이 없어도 높은 성능 구현

**Broader Significance:** Sibyl는 강화학습을 스토리지 시스템 데이터 배치에 성공적으로 적용하여, 기존 heuristic 및 ML 기반 기술의 한계를 극복. 시스템 설계자의 부담을 줄이면서 다양한 HSS 구성에서 우수한 성능을 달성하는 자기 최적화(self-optimizing) 메커니즘을 제시

## 주요 결과

- **구현 언어:** C (시스템 소프트웨어), Python (학습 에이전트)
- **시스템 구성요소:**
  - RL 에이전트: 데이터 배치 결정을 수행하는 핵심 모듈
  - 신경망: 2개 은닉층(20, 30 노드)으로 구성된 간단한 피드포워드 네트워크
  - 스토리지 관리 레이어: OS 레이어 또는 스토리지 펌웨어
- **평가에 사용된 스토리지 트레이스:** Microsoft Research Cambridge(MSRC)의 14개 다양한 기업 서버 트레이스
- **학습된 workload:** FileBench에서 수집된 워크로드 (학습되지 않은 워크로드로 일반화 능력 평가)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2022ISCA-summarize/sibyl-adaptive-and-extensible-data-placement-in-hybrid-storage-systems-using-rl.md|전체 요약 보기]]
