---
tags: [paper, 2020, 2020ISCA, topic/nvm, topic/virtual-memory]
venue: "2020 ACM/IEEE 47th Annual International Symposium on Computer Architecture (ISCA '20)"
year: 2020
summary_path: "../paper-summaries/2020ISCA-summarize/lelantus-fine-granularity-copy-on-write-operations-for-secure-non-volatile-memories.md"
---

# Lelantus: Fine-Granularity Copy-On-Write Operations for Secure Non-Volatile Memories

**Venue:** 2020 ACM/IEEE 47th Annual International Symposium on Computer Architecture (ISCA '20)
**저자:** Jian Zhou (University of Central Florida), Amro Awad (University of Central Florida), Jun Wang (University of Central Florida)

## 개요

- NVM (비휘발성 메모리)은 terabyte급 용량과 데이터 지속성으로 차세대 메모리 시스템의 핵심 후보이나, 제한된 쓰기 내구성(limited write endurance)과 느린 쓰기 연산이 주요 문제
- NVM은 데이터 잔류(data remanence) 공격에 취약하므로, 일반적으로 메모리 암호화와 함께 사용됨 (Intel 3D XPoint Apache Pass, AMD SME, Intel TME 등)
- 메모리 암호화는 avalanche effect로 인해 쓰기 내구성 문제를 악화시키고, NVM의 느린 쓰기가 성능에 미치는 영향을 증폭
- 복사-쓰기(Copy-on-Write, CoW)는 운영체제에서 광범위하게 사용되는 효율적 기법이나, 페이지 단위로 수행되어 NVM에서 심각한 성능 문제 초래:
  - **첫 쓰기 지연:** CoW 페이지의 첫 쓰기 시 전체 페이지를 복사/초기화 → 일반 페이지(4KB)에서 쓰기 증폭 7.07×, huge 페이지(2MB)에서 477.96×
  - **쓰기 증폭:** 전체 페이지 쓰기 시에도 일반 페이지 1.87×, huge 페이지 1.97× 증폭
  - Huge 페이지 사용 시 NVM의 느린 쓰기와 제한된 대역폭이 메모리 시스템을 throttle
- 기존 기법의 한계:
  - Silent Shredder: 제로 초기화만 회피 (CoW의 일부만 해결)
  - DMA 엔진 기반 bulk copy: 여전히 페이지 granularity에서 동작
  - TLB 비트맵 기반 캐시 라인 추적: TLB 수정 필요, CoW 이외의 용도 제한적

## 방법론

### 3.1. 보안 메타데이터 활용한 CoW 인코딩

- **Solution 1: 카운터 블록 리사이징 (Resizing Counter Blocks)**
  - 일반 페이지: 7비트 minor 카운터 × 64 + 63비트 major 카운터 + 1비트 CoW_Flag
  - CoW 페이지: 6비트 minor 카운터 × 64 + 63비트 major 카운터 + 64비트 소스 페이지 주소
  - minor 카운터 값이 0이면 해당 캐시 라인이 아직 복사되지 않았음을 의미
  - 공간 오버헤드: 없음 (카운터 블록 크기 동일)
  - 단점: minor 카운터가 1비트 줄어들어 overflow 발생 가능성 증가 (200%)

- **Solution 2: 보조 CoW 메타데이터 (Lelantus-CoW)**
  - 별도의 CoW 메타데이터 블록에 소스 페이지 주소 저장 (페이지당 8B)
  - minor 카운터 값 0 = 미복사 캐시 라인, 기타 = 일반 블록
  - CoW 캐시(카운터 캐시의 일부)로 CoW 메타데이터 조회 지연 최소화
  - 공간 오버헤드: 0.02% (매우 미미)
  - overflow 증가율: 0.07% (Solution 1 대비 훨씬 낮음)

### 3.2. 메모리 컨트롤러 명령어

- 세 가지 CoW 명령어를 메모리 컨트롤러에 추가:
  - **page copy:** 소스/대상 페이지 주소를 메모리 컨트롤러에 전달 → 메타데이터에 CoW 정보 인코딩 (실제 복사 없음)
  - **page phyc:** 소스 페이지 주소가 대상 페이지의 메타데이터와 일치하면 미복사 캐시 라인을 실제로 복사
  - **page free:** 복사된 페이지를 해제할 때 CoW 메타데이터 제거
- 메모리 맵드 I/O 레지스터를 통해 소프트웨어와 통신
- 프로세서의 out-of-order 실행 보장: 대상 페이지에 대한 활동은 일시 정지, 인터럽트 및 페이지 폴트 처리는 가능

### 3.3. 소스 페이지의 조기 회수 처리

- 부모 프로세스가 종료되면 소스 페이지의 map count가 1이 됨 → 커널이 소스 페이지를 쓰기 가능으로 변경
- 문제: 대상 페이지가 여전히 소스 페이지를 참조하면 잘못된 데이터 반환
- 해결: Linux의 rmap(reverse mapping) 코드를 활용한 역방향 조회
  - anon_vma 구조체를 통해 포크된 프로세스들의 복사된 페이지 추적
  - 소스 페이지의 map count가 1이 되면 wp_page_reuse/page_move_anon_rmap 호출 일시 정지
  - 실제 쓰기 발생 시 page fault handler에서 미복사 캐시 라인을 먼저 복사

### 3.4. 재귀적 복사 체인 처리

- 포크된 프로세스가 다시 포크하면 소스 페이지가 복사된 페이지를 다시 복사하는 체인 발생
- Lelantus는 소스 페이지의 메타데이터를 복사 페이지에 저장하여 체인 추적
- huge 페이지의 경우 미수정 캐시 라인이 많아 체인 최적화 효과 큼
- 소스 페이지 회수 시 직접적인 형제 페이지만 복사 (병렬 처리 가능)

### 3.5. 보안 고려사항

- 암호화 카운터 블록은 Merkle Tree에 의해 무결성 보호 → CoW 메타데이터 변조 감지
- 보조 CoW 메타데이터는 일반 데이터 블록과 동일하게 암호화 및 무결성 보호
- CoW 메타데이터가 암호화되지 않은 카운터 블록에 저장될 경우 접근 패턴 정보 노출 가능 → 암호화로 해결 가능
- 비보안 메모리에도 적용 가능: 카운터 블록 유사 메타데이터 사용 (≈1.5% 저장 오버헤드)

## 핵심 기여

- **핵심 기여:** 암호화 카운터를 재사용한 최초의 fine-granularity CoW 메커니즘, NVM 보안과 성능의 동시 해결
- **성능 향상:** 일반 페이지 평균 2.25×, huge 페이지 평균 10.57× speedup
- **수명 향상:** NVM 쓰기를 42.78%(일반)/29.65%(huge)로 감소
- **실용성:** 기존 보안 NVM 하드웨어(TME, SME, SGX)와의 호환성, 최소한의 커널 수정
- **연구 방향:** RowClone/DMA 엔진 등 기존 bulk operation 기법과의 결합을 통한 추가 최적화 가능
- **의의:** NVM 도입의 핵심 장애물인 CoW 쓰기 증폭과 보안 요구사항을 동시에 해결하는 실용적 솔루션

## 주요 결과

- **구현 환경:** Gem5 시뮬레이터 + Linux 커널 v5.0 수정
- **시스템 구성:**
  - 프로세서: 8코어, 1GHz, out-of-order x86-64
  - L1 캐시: 2_cycles, 64KB, 8-way; L2: 8_cycles, 512KB, 8-way; L3: 25_cycles, 8MB, 8-way
  - 메인 메모리: 16GB, NVM 읽기 60ns, 쓰기 150ns
  - 카운터 캐시: 256KB, 16-way
  - 페이지 크기: 4KB, 2MB
- **커널 수정:**
  - copy_user_page, do_wp_page, put_page 함수 재구현
  - 메모리 컨트롤러에 메모리 맵드 I/O 레지스터 추가 (CoW 명령어 통신)
  - 카운터 캐시 확장으로 CoW 메타데이터 캐싱

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2020ISCA-summarize/lelantus-fine-granularity-copy-on-write-operations-for-secure-non-volatile-memories.md|전체 요약 보기]]
