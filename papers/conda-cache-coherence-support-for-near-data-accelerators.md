---
tags: [paper, 2019, 2019ISCA, topic/cache, topic/dram, topic/pim]
venue: "The 46th Annual International Symposium on Computer Architecture (ISCA '19)"
year: 2019
summary_path: "../paper-summaries/2019ISCA-summarize/conda-efficient-cache-coherence-support-for-near-data-accelerators.md"
---

# CoNDA: Efficient Cache Coherence Support for Near-Data Accelerators

**Venue:** The 46th Annual International Symposium on Computer Architecture (ISCA '19)
**저자:** Amirali Boroumand (Carnegie Mellon University), Saugata Ghose (Carnegie Mellon University), Minesh Patel (ETH Zürich), Hasan Hassan (ETH Zürich), Brandon Lucia (Carnegie Mellon University), Rachata Ausavarungnirun (Carnegie Mellon University / KMUTNB), Kevin Hsieh (Carnegie Mellon University), Nastaran Hajinazar (Simon Fraser University), Krishna T. Malladi (Samsung Semiconductor, Inc.), Hongzhong Zheng (Samsung Semiconductor, Inc.), Onur Mutlu (ETH Zürich / Carnegie Mellon University)

## 개요

- 특화된 온칩 가속기(on-chip accelerators)가 시스템 성능과 에너지 효율 향상에 널리 사용됨
- 3D 적재 메모리 기술의 발전으로 **근데이터 가속기(NDA, Near-Data Accelerators)**가 실현 가능해짐 — 오프칩 메모리 근처에 배치되어 데이터 이동을 크게 줄일 수 있음
- 그러나 NDA의 핵심 과제는 **기존 시스템과의 캐시 일관성(coherence) 유지**:
  1. NDA와 CPU 간의 **오프칩 통신 비용이 매우 높음** — HMC(Hybrid Memory Cube)의 시리얼 링크 에너지 소비가 DRAM 배열 자체와 유사한 수준
  2. NDA 애플리케이션은 **낮은 연산 요구, 불량한 국소성, 대량의 오프칩 데이터 이동** 특성 → 많은 일관성 미스 발생
- 기존 일관성 메커니즘(MESI 등)을 NDA에 적용하면:
  - 모든 캐시 미스 시 오프칩 메시지 전송 필요
  - 높은 메시지 비용과 빈도로 인해 **NDA의 대부분의 이점을 상쇄**
- 그래프 처리 및 하이브리드 인메모리 데이터베이스 워크로드 분석에서:
  - CPU 스레드와 NDA 커널이 **동일 데이터 영역에 동시 접근**하지만, 실제 **동시 캐시라인 충돌은 드黑恶**
  - 충돌 시에도 CPU는 주로 **읽기 전용** 접근

## 방법론

### 3.1. 낙관적 NDA 실행 모델

- NDA 커널 시작 시 **체크포인트 생성**: PC와 소프트웨어 가시 레지스터 저장 → 재실행 시 사용
- NDA 커널 실행 중:
  - 모든 NDA 작업은 **미커밋(uncommitted)** 상태로 유지
  - CPU 스레드는 기존대로 일반 실행 수행
- 세 가지 충돌 시나리오 처리:
  1. **NDA 읽기 vs CPU 쓰기**: 재실행 필요 — CPU 쓰기가 DRAM에 플러시된 후 NDA가 다시 실행
  2. **NDA 쓰기 vs CPU 읽기**: 재실행 불필요 — NDA가 **데이터 업데이트 버퍼**에 값을 유지, 커밋 시 CPU 캐시의 불필요한 복사본을 무효화
  3. **NDA 쓰기 vs CPU 쓰기**: 재실행 불필요 — 데이터 업데이트 버퍼의 **워드별 더티 비트 마스크**를 사용하여 정확한 병합 수행

### 3.2. 시그니처 기반 접근 추적

- **병렬 블룸 필터(Parallel Bloom Filter)**를 시그니처로 구현:
  - N비트 시그니처를 M개 세그먼트로 분할, 각 세그먼트에 고유 해시 함수 적용
  - 메모리 주소 추가 시 각 세그먼트의 해시 값을 1로 설정
- 세 가지 연산 지원:
  1. 주소 포함 여부 확인: 모든 세그먼트에서 해시 값이 1인지 검사
  2. 모든 주소 목록 복원: 시그니처 확장(signature expansion) 기법 활용
  3. 두 시그니처 비교: 세그먼트별 XOR 연산으로 충돌 여부 빠르게 탐지
- CPU와 NDA 모두 시그니처를 유지: CPU는 **읽기/쓰기 시그니처**, NDA는 **읽기/쓰기 시그니처** 각각 유지

### 3.3. Coherence 해결 프로세스

- 낙관적 실행 종료 시:
  1. NDA가 자신의 시그니처를 CPU로 전송
  2. CoNDA가 NDA 시그니처와 CPU 시그니처를 비교하여 **필요한 일관성 요청 식별**
  3. 충돌 감지 시:
     - NDA의 모든 미커밋 업데이트 무효화
     - CPU가 **필요한 일관성 작업만 수행** (불필요한 트래픽 제거)
     - NDA가 미커밋된 부분을 재실행
  4. 충돌 미감지 시: NDA의 미커밋 업데이트를 커밋하고 낙관적 실행 재개

### 3.4. 프로그래밍 인터페이스

- **NDA_begin / NDA_end 매크로**: 프로그래머가 NDA에서 실행할 코드 영역을 지정
- 컴파일러가 매크로를 ISA 명령어로 변환
- **NDA 데이터 영역**: NDA가 접근할 수 있는 메모리 페이지를 페이지 테이블 엔트리에 **1비트 플래그**로 표시
- 동기화 프리미티브 지원: 기존 다중 스레드 프로그래밍 모델과 호환

## 핵심 기여

- **핵심 Contribution**: NDA를 위한 최초의 효율적 캐시 일관성 메커니즘 CoNDA 제안 — 낙관적 실행과 시그니처 기반 접근 추적을 통해 불필요한 오프칩 일관성 트래픽을 제거
- **성능 향상 수치**: 기존 최고 성능 대비 **19.6% 성능 향상**, 이상적 메커니즘과 **10.4% 이내** 수준
- **에너지 효율**: 기존 최고 에너지 효율 대비 **18.0% 절감**, CPU-only 대비 **43.7% 절감**
- **의의**: NDA의 실용화를 위한 핵심 기술 장벽(일관성)을 해결하여, 근데이터 가속기의 잠재력을 완전히 발휘할 수 있는 기반 마련 — 그래프 처리, 데이터베이스 등 대용량 데이터 워크로드에서의 NDA 활용 촉진

## 주요 결과

- **구현 언어/도구**: 하드웨어 시뮬레이션 기반 구현
- **시그니처 크기**: 병렬 블룸 필터 기반, 메모리 오버헤드 최소화
- **데이터 업데이트 버퍼**: NDA 쓰기 시 임시 저장소로 사용, 워드별 더티 비트 마스크 포함
- **하드웨어 오버헤드**: 기존 메커니즘 대비 낮은 수준 유지
- **호환성**: 기존 공유 메모리 프로그래밍 모델과 완전 호환

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2019ISCA-summarize/conda-efficient-cache-coherence-support-for-near-data-accelerators.md|전체 요약 보기]]
