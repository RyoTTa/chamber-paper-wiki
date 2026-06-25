---
tags: [paper, 2020, 2020ISCA, topic/storage]
venue: "2020 ACM/IEEE 47th Annual International Symposium on Computer Architecture (ISCA '20)"
year: 2020
summary_path: "../paper-summaries/2020ISCA-summarize/check-in-in-storage-checkpointing-for-key-value-store-system-leveraging-flash-based-ssds.md"
---

# Check-In: In-Storage Checkpointing for Key-Value Store System Leveraging Flash-Based SSDs

**Venue:** 2020 ACM/IEEE 47th Annual International Symposium on Computer Architecture (ISCA '20)
**저자:** Joohyeong Yoon (Yonsei University, Samsung Electronics), Won Seob Jeong (Yonsei University, Samsung Electronics), Won Woo Ro (Yonsei University)

## 개요

- 지속성 키-값 저장소(persistent key-value store)는 클라우드 서비스, 소셜 네트워킹, 온라인 쇼핑 등 다양한 데이터 처리 서비스에广泛 적용
- 키-값 저장소는 데이터 일관성 유지를 위해 저널링(journaling)과 체크포인팅(checkpointing) 메커니즘 사용
- 기존 데이터 일관성 메커니즘의 문제점:
  - **쓰기 증폭(write amplification):** 동일한 데이터를 두 번 쓰게 됨 (저널에서 쓴 데이터를 체크포인트에서 다시 씀)
  - **성능 저하:** 체크포인팅 중 무거운 트래픽으로 쿼리 처리 지연
  - **SSD 수명 단축:** 플래시 메모리의 제한된 P/E 사이클 증가로 수명 감소
- Flash 기반 SSD는 디스크 대비 낮은 지연 시간과 높은 대역폭 제공하지만, 쓰기 연산은 시간과 에너지를 많이 소모
- 특히 키-값 저장소는 작은 키-값 데이터의 빈번한 갱신으로 많은 무효 플래시 페이지 생성 → 가비지 컬렉션(GC) 유발
- 핵심 문제: 기존 체크포인팅 메커니즘은 SSD의 효율적인 관리에 적합하지 않음

## 방법론

### 3.1. 호스트-SSD 협력 구조

- 호스트 측 스토리지 엔진: 키-값 저장소의 체크포인팅 로직 관리
- SSD 측 FTL: 물리적 플래시 메모리 관리 및 체크포인팅 최적화
- 두 레이어 간 효과적인 통신 프로토콜을 통해 중복 쓰기 방지
- 기존의 호스트만의 체크포인팅 또는 SSD만의 처리보다 효율적

### 3.2. 인스토리지 체크포인팅 프로세스

- 기존 체크포인팅: 호스트가 데이터를 SSD에 쓰고, SSD는 이를 플래시 메모리에 기록
- Check-In: 호스트가 체크포인팅 명령을 SSD에 전달하고, SSD가 내부적으로 효율적인 체크포인팅 수행
- 불필요한 데이터 이동 및 중복 쓰기 최소화
- FTL이 물리적 플래시 페이지 할당 및 관리를 최적화

### 3.3. 쓰기 증폭 완화 전략

- 저널 로그와 체크포인트 데이터의 중복 저장 방지
- FTL 수준에서 데이터 중복성 감지 및 제거
- 플래시 페이지 할당 시 기존 데이터와의 비교를 통한 최적화
- 가비지 컬렉션 오버헤드 최소화

### 3.4. 레이턴시 최적화

- 체크포인팅 중 발생하는 테일 레이턴시 92.1% 감소
- SSD 내부 처리를 통해 호스트 대기 시간 최소화
- 병렬 처리 및 비동기 동작을 통한 성능 향상
- 네트워크 및 버스 오버헤드 최소화

## 핵심 기여

- **핵심 기여:** 호스트-SSD 협력을 통한 인스토리지 체크포인팅 메커니즘 최초 제안
- **성능 향상:** 테일 레이턴시 92.1% 감소, 중복 쓰기 94.3% 감소, 처리량 8.1% 향상
- **실용성:** 기존 SSD 하드웨어와의 호환성을 고려한 설계
- **연구 방향:** 스토리지 시스템에서 호스트-디바이스 협력 최적화의 새로운 패러다임 제시
- **의의:** 키-값 저장소의 데이터 일관성 메커니즘을 SSD 친화적으로 재설계하여 시스템 전체 성능 및 SSD 수명 향상

## 주요 결과

- **구현 환경:** Flash 기반 SSD 프로토타입
- **소프트웨어:** 사용자 수준 스토리지 엔진, FTL 펌웨어
- **하드웨어:** NAND 플래시 메모리, SSD 컨트롤러
- **시스템 구성:**
  - 호스트: x86 기반 서버, Linux 운영체제
  - SSD: 커스텀 FTL 구현, NAND 플래시 메모리 타일
- **오버헤드:** FTL의 추가적인 연산 및 메모리 사용

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2020ISCA-summarize/check-in-in-storage-checkpointing-for-key-value-store-system-leveraging-flash-based-ssds.md|전체 요약 보기]]
