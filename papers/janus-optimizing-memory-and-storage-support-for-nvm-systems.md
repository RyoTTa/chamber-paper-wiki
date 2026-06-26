---
tags: [paper, 2019, 2019ISCA, topic/compression, topic/dram, topic/nvm, topic/security, topic/storage]
venue: "The 46th Annual International Symposium on Computer Architecture (ISCA '19)"
year: 2019
summary_path: "../paper-summaries/2019ISCA-summarize/janus-optimizing-memory-and-storage-support-for-nvm-systems.md"
---

# Janus: Optimizing Memory and Storage Support for Non-Volatile Memory Systems

**Venue:** The 46th Annual International Symposium on Computer Architecture (ISCA '19)
**저자:** Sihang Liu (University of Virginia), Korakit Seemakhupt (University of Virginia), Gennady Pekhimenko (University of Toronto), Aasheesh Kolli (Penn State University / VMware Research), Samira Khan (University of Virginia)

## 개요

- NVM(Non-Volatile Memory) 기술(예: Intel 3D XPoint)은 DRAM 수준의 성능으로 **데이터 지속성(persistence)** 제공
- **Crash consistency** 보장을 위해 쓰기 연산이 NVM까지 도달해야 하며, 이로 인해 **쓰기가 프로그램 실행의 Critical Path에 위치**
- NVM 시스템에서 **Backend Memory Operations (BMOs)**가 쓰기 지연 시간을 크게 증가:
  - **Encryption**: counter-mode 암호화로 데이터 보안 유지
  - **Integrity Protection**: Bonsai Merkle Tree로 MAC 및 해시 트리 업데이트
  - **Deduplication**: 중복 데이터 감지 및 쓰기 취소
  - **Compression**: 데이터 압축으로 저장 공간 절약
- BMOs는 순차적으로 수행되며 **수백 나노초의 추가 지연** 발생
- ADR(Asynchronous DRAM Refresh) 기반 시스템에서 BMO 없이 쓰기 지연은 **약 15ns**이나, BMO 포함 시 **10배 이상 증가**

## 방법론

### 3.1. BMO 분해 및 의존성 분석

- **Counter-mode Encryption** 분해:
  - E1: 새 카운터 생성
  - E2: One-Time Padding 생성: `OTP = En(counter|address)`
  - E3: XOR로 데이터 암호화: `EncData = OTP ⊕ Data`
- **Deduplication** 분해:
  - D1: 데이터 해싱
  - D2: 해시 테이블 조회
  - D3: 주소 매핑 테이블 업데이트
  - D4: 새 주소 매핑 엔트리 암호화 및 NVM에 기록
- 의존성 유형:
  - **Intra-operation dependency**: 같은 BMO 내 서브 연산 간 의존성
  - **Inter-operation dependency**: 서로 다른 BMO 간 서브 연산 의존성
  - **External dependency**: 외부 입력(data, address)에 대한 의존성

### 3.2. 병렬화 메커니즘

- 독립적인 서브 연산 그룹을 동시에 실행:
  - `{E1, E2}`와 `{D1, D2, D3}`는 서로 독립 → 병렬 실행 가능
  - `{E3}`와 `{D4}`는 서로 독립 → 병렬 실행 가능
-undo-logging 트랜잭션의 세 단계(backup, update, commit)에서 BMO 병렬화 적용
- 직렬화 대비 실행 시간 대폭 감소

### 3.3. 사전 실행 메커니즘

- 서브 연산을 **외부 입력 유형**에 따라 분류:
  - **Address-dependent**: E1, E2 (주소에만 의존)
  - **Data-dependent**: D1, D2 (데이터에만 의존)
  - **Address-and-data-dependent**: E3, D3, D4 (주소와 데이터 모두에 의존)
- 사전 실행 요구사항:
  1. 프로세서/메모리 상태에 영향 없어야 함
  2. 오래된 사전 실행 결과는 무효화되어야 함
- NVM 쓰기 전에 BMO를 미리 실행하여 Critical Path에서 제거

### 3.4. 소프트웨어 인터페이스

- **범용적이고 확장 가능한 인터페이스**: 다양한 BMO와 호환
- **프로그래밍 용이성**: undo/red/shadow logging 등 다양한 crash consistency 프로그래밍 모델 지원
- **컴파일러 패스**: 수동 계측 대신 자동으로 프로그램 계측
- 프로그래머는 NVM 프로그램에 인터페이스 주석을 추가

## 핵심 기여

- **핵심 Contribution**: NVM 시스템에서 BMO의 병렬화와 사전 실행을 통한 쓰기 지연 시간 최적화
- **성능 향상**: 수동 계측 2.35×, 자동 계측 2.00× 속도 향상
- **실용성**: 기존 crash consistency 프로그래밍 모델과 호환되는 소프트웨어 인터페이스 제공
- **의의**: NVM 시스템의 상용화를 위한 핵심 기술로, BMO 오버헤드를 효과적으로 줄여 NVM 성능 잠재력 극대화

## 주요 결과

- **하드웨어 지원**: 메모리 컨트롤러에 BMO 병렬화/사전 실행 로직 추가
- **소프트웨어 지원**: Janus 인터페이스 및 자동 계측 컴파일러 패스
- **평가 시스템**: Encryption + Integrity + Deduplication이 통합된 NVM 시스템
- **프로그래밍 모델**: 수동 계측(manual instrumentation) 및 자동 계측(automated compiler pass) 지원

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/security.md|Security]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2019ISCA-summarize/janus-optimizing-memory-and-storage-support-for-nvm-systems.md|전체 요약 보기]]
