---
tags: [paper, 2021, 2021ISCA, topic/dram, topic/nvm, topic/virtual-memory]
venue: "ACM/IEEE 48th Annual International Symposium on Computer Architecture (ISCA) 2021"
year: 2021
summary_path: "../paper-summaries/2021ISCA-summarize/supporting-legacy-libraries-on-non-volatile-memory-a-user-transparent-approach.md"
---

# Supporting Legacy Libraries on Non-Volatile Memory: A User-Transparent Approach

**Venue:** ACM/IEEE 48th Annual International Symposium on Computer Architecture (ISCA) 2021
**저자:** Chencheng Ye (Huazhong University of Science and Technology), Yuanchao Xu (North Carolina State University), Xipeng Shen (University of Central Florida), Xiaofei Liao (Huazhong University of Science and Technology), Hai Jin (Huazhong University of Science and Technology), Yan Solihin (University of Central Florida)

## 개요

- NVM (Non-Volatile Memory)은 byte-addressable, DRAM-like latency/bandwidth, persistency를 제공하여 클라우드 환경에서 **최대 10x 성능 향상** 또는 **38% 비용 절감** 관찰
- 그러나 모든 기존 NVM 프로그래밍 모델(Intel PMDK, NVHeap 등)은 persistent 객체에 대해 **특수한 데이터 타입과 별도 API**를 요구
- legacy 라이브러리들은 이러한 특수 타입을 지원하지 않으므로, NVM 애플리케이션과의 호환성에 심각한 장애물
- Ubuntu 20.04 LTS 공식 패키지 아카이브에 **6,505개 라이브러리** 존재; Boost, Gnulib, GTK, CPL 등 4개 라이브러리만으로도 **5.4M lines** C/C++ 코드와 **342K functions** 포함
- **Redis → NVM 마이그레이션 사례**: Intel 엔지니어가 수개월 소요, **4,348 lines** 변경 (Redis 코드베이스의 **7.6%**), 마이그레이션 미완료 (zipmap 등 미구현)
- **RocksDB 인덱싱 마이그레이션**: 단일 인덱싱 데이터 구조만으로 **4,117 lines** 추가
- 기존 영속성 프로그래밍 모델: PMEMoid (PMDK, **128비트 fat pointer**), object pool ID + offset 기반 → persistent pointer는 기존 pointer와 타입/표현 방식이 다름
- 모든 persistent pointer는 relocatable해야 함 (다른 실행 시 pool이 다른 virtual address에 매핑될 수 있으므로)

## 방법론

### 3.1. 메모리 레이아웃과 포인터 표현

- 256TB 가상 주소 공간을 **반으로 분할**: 전반부(DRAM), 후반부(NVM)
- virtual address의 **bit 47**로 NVM/DRAM 판별 (물리 주소 변환 불필요)
- **64비트 포인터** 표현:
  - **MSB (bit 63) = 0**: 일반 virtual address 포인터 (volatile)
  - **MSB (bit 63) = 1**: relative address 포인터 (persistent)
    - bit 32~62: **31-bit pool ID**
    - bit 0~31: **32-bit intra-pool offset**
- 동일한 포인터 길이(8 bytes)를 유지하면서도 persistent/volatile 타입 구분

### 3.2. 런타임 검사 (Runtime Checks)

- 포인터 값의 flagging 비트를 검사하여 적절한 해석 수행:
  - `determineX(addr)`: bit 63이 1이면 NVM, 아니면 bit 47로 DRAM/NVM 판별
  - `determineY(val)`: bit 63이 1이면 Relative, 아니면 Virtual
- 포인터 할당 시:
  - NVM에 저장 + virtual address 값 → `va2ra()` 변환 후 저장
  - DRAM에 저장 + relative address 값 → `ra2va()` 변환 후 저장
  - 같은 영역 + 같은 타입 → 직접 복사

### 3.3. 하드웨어 지원 (storeP 명령어)

- 기존 load/store 외에 **storeP** 명령어 추가 (pointer 저장 전용)
- **MMU에 두 가지 lookaside buffer 추가**:
  - **POLB (Persistent Object Lookaside Buffer)**: ObjectID → virtual address 변환
  - **VALB (Virtual Address Lookaside Buffer)**: virtual address → ObjectID 변환 (TCAM 기반 longest prefix match)
- **storeP functional unit**: FSM 기반으로 Rs/Rd 변환을 동시에 처리
  - Rs가 virtual address → relative address 변환 필요 시 VALB 조회
  - Rd가 virtual address → relative address 변환 필요 시 POLB 조회
- FSM, POLB, VALB 총 온칩 저장 비용: **1,280 bytes**, 면적: **0.0479 mm²** (45nm octal core Nehalem 대비 **0.059%**)
- **POTB, VATB**: 커널 메모리의 소프트웨어 데이터 구조

### 3.4. Soundness 분석

- ISO C11 표준의 모든 포인터 연산 (cast, dereference, arithmetic, comparison, sizeof, alignof 등)에 대해 사용자 투명 persistent reference의 시맨틱을 체계적으로 검증
- 모든 포인터 연산의 반환값이 ISO C11 명세와 일관됨을 보장
- hardware 지원은 포인터를 사용/저장하기 직전에 절대 주소↔상대 주소 변환 → 변환 결과는 일반 포인터에 자연스럽게 재사용됨

### 3.5. 컴파일러 지원

- **Hardware-based 방법**: LLVM pass가 pointer 연산을 감지하여 `storeD`(데이터 저장) 또는 `storeP`(포인터 저장) 명령어로 변환
  - 모든 최적화 pass 이후에 실행되어 기존 최적화와의 충돌 방지
- **Compiler-based 방법**: 정적 타입 추론으로 동적 검사 삽입 최소화 시도
  - backward dataflow analysis로 pmalloc/pfree의 인자/반환값에서 다른 변수로 속성 전파
  - 그러나 C 언어의 포인터 별칭(alias)과 함수 인자 전달의 복잡성으로 약 **42%**의 동적 검사가 여전히 필요
  - branch misprediction이 심각 (SW 버전에서 **6.7배** 증가)

## 핵심 기여

- **최초의 legacy 라이브러리 NVM 지원 솔루션**: user-transparent persistent reference로 기존 라이브러리의 코드 수정 없이 NVM 애플리케이션에서 사용 가능
- 하드웨어 지원 시 런타임 오버헤드 **거의 무시할 수 있는 수준** (최대 12%), Explicit 방식 대비 **1.33x faster**
- Boost 라이브러리 6개 데이터 구조와 KNN 머신러닝 애플리케이션에서 soundness와 효율성 검증
- 코드 수정량: Proposed **7 lines** vs. Explicit **863 lines** → 레거시 라이브러리 NVM 마이그레이션 비용 대폭 절감
- 6,505개 legacy 라이브러리의 NVM 호환성 문제를 해결하여 NVM의 실용적 도입 가속화

## 주요 결과

- **하드웨어 지원**: storeP 명령어, VALB (TCAM 기반), POLB, FSM 추가
  - on-chip 저장: FSM(**512B**), POLB(**384B**), VALB(**384B**)
  - 면적: **0.0479 mm²** (45nm 공정 기준)
- **소프트웨어 지원**: LLVM compiler pass + persistent memory allocator (libvmmalloc)
  - 레거시 라이브러리는 재컴파일 또는 binary rewriting만 필요
- 시뮬레이터: **Sniper-sim** (Pin 기반, interval-based timing), 64-bit X86, Gainestown 아키텍처
  - CPU: 1코어 2.66GHz, L1D 4 cycles, L2 12 cycles, L3 40 cycles
  - Memory: DRAM 120 cycles (45ns), NVM 240 cycles
  - POLB/VALB: hit 3 cycles, miss 30 cycles

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2021ISCA-summarize/supporting-legacy-libraries-on-non-volatile-memory-a-user-transparent-approach.md|전체 요약 보기]]
