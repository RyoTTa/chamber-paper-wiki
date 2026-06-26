---
tags: [paper, 2025, 2025MICRO, topic/dram, topic/llm-inference, topic/nvm, topic/pim, topic/virtual-memory]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO 2025)"
year: 2025
summary_path: "../paper-summaries/2025MICRO-summarize/compass-compatible-pim-protocol-architecture.md"
---

# ComPASS: A Compatible PIM Protocol Architecture and Scheduling Solution for Processor-PIM Collaboration

**Venue:** IEEE/ACM International Symposium on Microarchitecture (MICRO 2025)
**저자:** Seunghyuk Yu, Hyeonu Kim, Kyoungho Jeun, Sunyoung Hwang, Seongmin Cho, Eojin Lee (Inha University)

## 개요

- 메모리 바운드 애플리케이션의 증가로 프로세서-메모리 간 데이터 이동이 주요 병목으로 부상, Processing-In-Memory(PIM)가 해결책으로 주목받고 있으나 기존 PIM 설계는 호환성과 효율성에 한계
- 기존 PIM 프로토콜의 한계:
  - UPMEM-PIM: DDR4 표준 호환이 가능하나 PIM 실행 중 일반 메모리 접근 완전 차단
  - HBM-PIM: HBM2 인터페이스 준수하나 일반/PIM 모드 전환 시 명령어 시퀀스 필요 → 전환 오버헤드 발생, PIM 모드에서 일반 메모리 요청 처리 불가
  - GDDR6-AiM: 모드 전환 없이 세밀한 교차(interleaving) 지원 가능하나 새로운 명령어 체계 필요 → 메모리 서브시스템 커스터마이징 required
- 제한된 명령어/주소(CA) 공간에서 다양한 PIM 아키텍처와 호환되는 통일된 프로토콜 부재
- PIM과 일반 워크로드 간 대역폭 배분 및 스케줄링 문제: PIM 우선 시 일반 워크로드 지연, 일반 워크로드 우선 시 PIM 처리량 감소 → QoS 보장 어려움

## 방법론

### 3.1. PIM-ACT 명령어

- 다중 뱅크 동시 활성화를 단일 명령어로 수행 → 기존 모드 전환 시퀀스 제거
- optype 필드를 통해 각 PIM 디바이스가 자체 연산 의미를 정의 가능 → 아키텍처 다양성 지원
- optype 0-31: 연산 작업, 32-63: 데이터 전달 작업으로 분류 → 디코딩 로직 단순화
- HBM-PIM: 35개 optype 사용 (MUL, ADD, MAD, MAC, ReLU, MOV)
- GDDR6-AiM: 32개 optype 사용 (MAC, MAC4B, MACAB, EWMUL, AF, RDCP, WRCP 등)

### 3.2. PIM 요청 생성기

- 메모리 컨트롤러 내에 위치하며, 매크로 요청을 마이크로 요청으로 변환
- send_PIM_req(), send_PIM_data(), run_PIM_request_generator() API 제공
- 프로세서가 매크로 요청과 데이터를 전달하면, 생성기가 독립적으로 마이크로 요청 생성 → 명령어 전송 오버헤드 감소
- 모든 PIM-ACT 호환 디바이스에 범용 적용 가능 → 디바이스별 커스터마이징 불필요

### 3.3. Architecture-Aware Optimization (AAO)

- PIM-ACT의 row timing 파라미터를 PIM 디바이스 아키텍처에 맞게 조정
- HBM-PIM: 모드 전환 오버헤드 제거로 GEMV 성능 2.54~11.38% 향상
- GDDR6-AiM: PIM-ACT 미적용 시 GEMV 성능 11.69% 감소 → AAO 적용 시 0.59%로 완화
- per-optype column timing 조정 지원 (SPD에 정의된 파라미터 활용)

### 3.4. 주소 공간 관리

- PIM 연산의 물리적 연속 메모리 할당을 위해 HugeTLB(2MB/1GB 허가지 페이지) 사용
- 메모리 단편화 시 memory compaction 기능 활용 가능
- LLM 추론 등 장기 반복 접근 워크로드에서 초기 할당 오버헤드 상쇄 가능

## 핵심 기여

- **핵심 기여:** PIM-ACT 명령어와 메모리 컨트롤러 내 PIM 요청 생성기를 통한 호환성 있는 PIM 프로토콜 제안 → 다양한 PIM 아키텍처 통합 가능
- **호환성 검증:** HBM-PIM, GDDR6-AiM, LPDDR 변형 모두에서 PIM-ACT + AAO로 기존 프로토콜 대비 동등 이상의 성능 달성
- **스케줄링 기여:** AT-BLC 적응형 스케줄러로 CPU-PIM 공동 실행 시 PIM QoS 보장 및 CPU 성능 최적화 동시 달성
- **성능 결과:** LPDDR-PIM에서 non-PIM 대비 최대 10.75× GEMV 가속, CPU-hi 워크로드 공존 시에도 QoS 충족
- **실용성:** 제한된 CA 공간을 활용하는 기존 DRAM 표준과의 호환성을 유지하면서 다양한 PIM 아키텍처를 하나의 프로토콜로 통합하는 최초의 시도

## 주요 결과

- **PIM 디바이스:** HBM-PIM, GDDR6-AiM, LPDDR-PIM, LPDDR-AiM 시뮬레이션
- **프로세서 워크로드:** GPT-3 6.7B 및 GPT-3 XL 모델의 GEMV 연산
- **CPU 워크로드:** SPEC CPU 2017, GAP Benchmark Suite (BFS, PR)
- **스케줄러:** FR-FCFS, Batch, TCM, ST-BLC, AT-BLC 비교
- **시스템 구성:** 멀티 채널 메모리 컨트롤러, PIM 요청 큐 분리 구조

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2025MICRO-summarize/compass-compatible-pim-protocol-architecture.md|전체 요약 보기]]
