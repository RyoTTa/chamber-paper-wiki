---
tags: [paper, 2021, 2021HPCA, topic/cache, topic/disaggregation, topic/dram, topic/virtual-memory]
venue: "2021 IEEE International Symposium on High-Performance Computer Architecture (HPCA '21)"
year: 2021
summary_path: "../paper-summaries/2021HPCA-summarize/deact-architecture-aware-virtual-memory-support-for-fabric-attached-memory-systems.md"
---

# DeACT: Architecture-Aware Virtual Memory Support for Fabric Attached Memory Systems

**Venue:** 2021 IEEE International Symposium on High-Performance Computer Architecture (HPCA '21)
**저자:** Vamsee Reddy Kommareddy (University of Central Florida), Clayton Hughes (Sandia National Laboratories), Simon David Hammond (Sandia National Laboratories), Amro Awad (North Carolina State University)

## 개요

- 현대 HPC 시스템은 노드당 수백 GB의 메모리를 필요로 하나, 스케줄러가 노드 단위로 자원을 할당하여 **메모리 언더UTIL리제이션**이 심각: Summit 슈퍼컴퓨터는 노드당 512GB DRAM + 96GB HBM2를 보유하지만, 일부 애플리케이션은 수 GB만 사용
- **Fabric-Attached Memory (FAM)** 은 시스템 인터페이스에 직접 연결된 메모리 모듈로, Gen-Z, CXL 등의 프로토콜을 통해 여러 Processing Element (PE) 간 메모리 풀 공유 가능
- FAM은 메모리 분리(disaggregation)를 통해 유연성, 비용 효율성, 메모리 활용도를 향상시키지만, **가상 메모리 보안** 문제가 새로운 도전 과제로 부상: 여러 노드가 동일 FAM 풀에 접근하므로 악성 OS/애플리케이션이 다른 노드의 데이터에 무단 접근 가능
- 기존의 두 가지 메모리 관리 접근법:
  - **Exposed FAM (E-FAM)**: FAM을 노드 OS에 직접 노출 → 성능 우수하지만 OS 수정 필요 및 보안 취약 (최대 20.6x 성능 저하 없음)
  - **Indirect FAM (I-FAM)**: 시스템 레벨에서 두 번째 주소 변환 계층 도입 → 보안 보장하지만 **최대 20.6x (평균 3.3x) 성능 저하** 발생
- x86-64 시스템에서 기존 4계층 페이지 테이블만으로도 TLB 미스 시 4번의 메모리 액세스 필요, 가상화 환경에서는 최대 **24번**의 메모리 액세스 필요 (Bhargava et al. [11])

## 방법론

### 3.1. 접근 제어 메타데이터 (ACM)

- 각 4KB FAM 페이지마다 **16비트 ACM** 저장: 2비트 읽기/쓰기 권한 + 14비트 노드 ID
- 최대 **16,383개 노드** 지원, 공유 페이지는 모든 노드 ID 비트를 1로 설정하여 표시
- 1GB 공유 페이지마다 **16K 비트 비트맵(2KB)** 을 사용하여 공유 권한 관리 (전체 메모리 대비 <0.0001% 오버헤드)
- ACM은 FAM에 저장되며, STU가 캐싱하여 노드가 직접 접근하지 못하도록 보안 격리

### 3.2. FAM 트랜슬레이터 (메모리 컨트롤러 내)

- 로컬 DRAM에 **FAM translation cache** 유지 (기본 1MB, 4-way associative)
- 각 캐시 엔트리: 52비트 태그(노드 페이지 주소) + 52비트 값(FAM 페이지 주소) = 104비트
- **4개 비교기(conparator)** 를 병렬로 사용하여 태그 매칭을 1사이클에 수행
- **히트 시**: 노드 주소를 FAM 주소로 치환하여 요청 전달, 응답이 필요한 경우 outstanding mapping list에 저장
- **미스 시**: STU에 FAM 페이지 테이블 워크(PTW) 요청, 완료 후 translation cache 업데이트
- 미스트랜SL레이션 시 **V(verification) 플래그** 를 리셋하여 STU가 PTW와 검증을 구분

### 3.3. STU 캐시 조직 (DeACT-W vs DeACT-N)

- **DeACT-W (Way-level contiguous)**: 각 캐시 way에서 ACM을 인접 페이지 4개씩 캐싱 → ACM 히트율 약 90%
- **DeACT-N (Non-contiguous)**: 캐시 way를 2개의 sub-way로 분할, 인접하지 않은 페이지 ACM도 캐싱 → ACM 히트율 **약 99%** 로 향상
- DeACT-N은 태그를 44비트로 축소하여 한 way에 태그+ACM 쌍 2개 저장 가능 (32PB 주소 공간 지원)
- spatial locality가 낮은 랜덤 FAM 할당 환경에서 DeACT-N이 DeACT-W보다 우수

### 3.4. 전체 시스템 동작 흐름

```
노드 CPU → N-MMU (TLB/PTW) → FAM translator (로컬 DRAM 캐시) → STU (ACM 검증) → FAM
```

1. 노드가 FAM 액세스 시 N-MMU가 먼저 로컬 TLB 확인
2. FAM translator가 로컬 DRAM의 translation cache에서 변환 조회
3. 히트 시: FAM 주소로 변환 후 STU에 검증 요청 전달
4. STU가 ACM을 확인하여 접근 권한 검증
5. 미스 시: STU가 FAM 페이지 테이블을 워크하여 변환 및 검증 수행

## 핵심 기여

- DeACT는 FAM 시스템에서 **보안과 성능을 동시에 달성**하는 최초의 가상 메모리 메커니즘
- 접근 제어와 주소 변환을 분리하여 로컬 메모리의 높은 공간적 국소성을 활용한 효율적 캐싱 가능
- I-FAM 대비 평균 **1.8x (최대 4.59x)** 성능 향상, 평균 성능 저하를 69.7%에서 35.3%로 개선
- OS 수정 불필요, 기존 가상화 기술과 호환 가능한 설계
- 향후 연구 방향: 큰 페이지支持, 페이지 마이그레이션 최적화, 더 많은 노드 스케일링

## 주요 결과

- **시뮬레이터**: SST (Structural Simulation Toolkit) 기반 사이클 레벨 시뮬레이션
- **시뮬레이션 파라미터**: 4코어 Out-of-Order (2GHz, 2 issues/cycle), L1 32KB/L2 256KB/L3 1MB, 로컬 메모리 1GB DRAM, FAM 16GB NVM
- **STU**: 1024 엔트리, 8-way associative (Haswell Xeon L2 TLB 설계 참고)
- **네트워크 지연시간**: 500ns (fabric interconnect 기준)
- **Warp size**: 128개 미완료 요청 지원

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2021HPCA-summarize/deact-architecture-aware-virtual-memory-support-for-fabric-attached-memory-systems.md|전체 요약 보기]]
