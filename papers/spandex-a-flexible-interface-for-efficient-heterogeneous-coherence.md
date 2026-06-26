---
tags: [paper, 2018, 2018ISCA, topic/cache, topic/gpu]
venue: "45th Annual International Symposium on Computer Architecture (ISCA '18)"
year: 2018
summary_path: "../paper-summaries/2018ISCA-summarize/spandex-a-flexible-interface-for-efficient-heterogeneous-coherence.md"
---

# Spandex: A Flexible Interface for Efficient Heterogeneous Coherence

**Venue:** 45th Annual International Symposium on Computer Architecture (ISCA '18)
**저자:** NOTA 논문 정보에서 확인 필요

## 개요

- 이기종 시스템의 등장:
  - CPU, GPU, 가속기 등 다양한 디바이스가 하나의 칩에 통합
  - 각 디바이스는 다른 메모리 접근 패턴과 코히어런스 요구사항 보유
  - 기존 MESI 기반 코히어런스의 한계 부각

- 기존 코히어런스 프로토콜의 한계:
  - **계층적 캐시 구조:** CPU-GPU 통신을 위해 중간 캐시(L2) 필요
  - **프로토콜 복잡성:** MESI, MOESI 등 다양한 확장 프로토콜
  - **블로킹 상태(Blocking States):** 데이터 전송 시 다른 디바이스 차단
  - **거짓 공유(False Sharing):** 라인 단위 소유권으로 인한 불필요한 전송
  - **인디렉션 오버헤드:** 중간 캐시를 통한 추가 레이턴시

- 이기종 디바이스의 다양한 요구사항:
  - **CPU (MESI):** 라인 단위 소유권, 라이터-무효화 읽기(writer-invalidated reads)
  - **GPU coherence:** 단어 단위 유효성, 셀프-무효화(self-invalidation)
  - **DeNovo:** 단어 단위 소유권, 셀프-무효화, 비블로킹 전송
  - 기존 프로토콜은 이 모든 요구사항을 동시에 지원 불가

## 방법론

### 3.1. Spandex LLC 프로토콜

- **상태(State):**
  - I (Invalid): 유효하지 않음
  - V (Valid): 유효하지만 소유권 없음 (셀프-무효화 가능)
  - O (Owned): 소유권 보유 (단어 단위)
  - S (Shared): 공유 상태 (라이터-무효화)

- **요청 타입(Request Types):**
  - ReqV: 유효 데이터 요청 (셀프-무효화)
  - ReqO/ReqO+data: 소유권 요청 (선택적 데이터 포함)
  - ReqWT/ReqWT+data: 라이트스루 요청
  - ReqS: 공유 상태 요청 (MESI 호환)
  - RvkO: 소유권 회수 요청
  - Inv: 무효화 요청

- **단어 단위 소유권 추적:**
  - LLC에서 단어 단위로 소유자(owner) 추적
  - 라인 내 다른 위치는 다른 디바이스가 소유 가능
  - 거짓 공유(False Sharing) 최소화

### 3.2. Spandex 디바이스 요구사항

- **GPU coherence 디바이스:**
  - O 또는 S 상태 미지원 → 포워딩된 요청 처리 불가
  - TU(Translation Unit)가 ReqV 재시도, 응답 코얼레스(coalescing) 처리
  - 다중 소스 응답 수집 후 라인 단위 응답 생성

- **DeNovo 디바이스:**
  - 단어 단위 소유권 지원
  - ReqV Nack 시 ReqWT+data로 대체 (최대 1회 재시도)
  - 부분 읽기(partial response) 지원

- **MESI 디바이스:**
  - 라인 단위 소유권 → TU가 단어 단위 요청을 라인 단위로 변환
  - O 상태에서 외부 요청 처리 시 부가적 ReqWB 트리거
  - 블로킹 상태 관리 및 코얼레스(coalescing) 처리

### 3.3. TU(Translation Unit) 역할

- 각 디바이스에 연결된 번역 유닛
- 디바이스 고유 프로토콜과 Spandex LLC 간의 갭(gap) 해소
- 요청 타입 변환, 응답 코얼레스, 재시도 로직 구현
- 디바이스 캐시 IP 변경 최소화

### 3.4. 일관성(Consistency) 요구사항

- SC-for-DRF (Sequential Consistency for Data-Race-Free) 모델 가정
- 구현 요구사항:
  1. 동기화 접근의 순서 재배치 제한
  2. 동기화 지점에서 쓰기 버퍼 플러시
  3. 동기화 지점에서 유효 데이터 셀프-무효화
- DeNovo regions, scoped synchronization 등으로 완화 가능

## 핵심 기여

- **핵심 기여:** 이기종 시스템을 위한 유연하고 단순한 코히어런스 인터페이스 Spandex 제안
- **성능 향상:** 기존 계층적 MESI 대비 실행 시간 평균 **16%**, 네트워크 트래픽 평균 **27%** 절감
- **의의:**
  - 다양한 디바이스의 코히어런스 요구사항을 하나의 프로토콜로 지원
  - 계층적 캐시 구조의 인디렉션 오버헤드 제거
  - 단어 단위 소유권으로 거짓 공유 최소화
  - 비블로킹 소유권 전송으로 높은 동시성 달성
  -未来的 디바이스의 유연한 통합 가능성
- **한계점:**
  - 단어 단위 소유권 추적을 위한 LLC 저장소 오버헤드
  - 디바이스에 TU 추가 필요 (면적/전력 오버헤드)
  - 기존 MESI 확장 프로토콜(MOESI, MESIF) 미지원
  - 복잡한 프로토콜 변환을 위한 디바이스별 TU 구현 필요

## 주요 결과

- **시뮬레이션 환경:**
  - Simics (CPU 모델링)
  - GEMS (메모리 시스템)
  - GPGPU-Sim (GPU 모델링)
  - Garnet (네트워크)

- **캐시 설정:**
  - CPU: 8코어, 2GHz, MESI 또는 DeNovo L1
  - GPU: 16 CUs, 700MHz, GPU coherence 또는 DeNovo L1
  - LLC: 8MB Spandex 또는 4MB+8MB 계층적 MESI

- **벤치마크:**
  - 합성 마이크로벤치마크: Indirection, ReuseO, ReuseS
  - 실제 애플리케이션: BC, PR (Pannotia), HSTI, TRNS, RSCT, TQH (Chai)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/gpu.md|GPU]]


## 전체 요약

[[../paper-summaries/2018ISCA-summarize/spandex-a-flexible-interface-for-efficient-heterogeneous-coherence.md|전체 요약 보기]]
