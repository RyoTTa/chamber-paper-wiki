---
tags: [paper, 2022, 2022ISCA, topic/dram, topic/nvm, topic/pim, topic/storage]
venue: "ISCA 2022 (The 49th Annual International Symposium on Computer Architecture)"
year: 2022
summary_path: "../paper-summaries/2022ISCA-summarize/to-pim-or-not-for-emerging-general-purpose-processing-in-ddr-memory-systems.md"
---

# To PIM or Not for Emerging General Purpose Processing in DDR Memory Systems

**Venue:** ISCA 2022 (The 49th Annual International Symposium on Computer Architecture)
**저자:** Alexandar Devic, Siddhartha Balakrishna Rai, Anand Sivasubramaniam (The Pennsylvania State University), Ameen Akel, Sean Eilert, Justin Eno (Micron Technology, Inc)

## 개요

- 메모리 월(memory wall) 극복을 위해 PIM(Processing-in-Memory) 하드웨어가 활발히 연구되고 있으나, 기존 제안들은 특화/하드웨어 연산 중심이었고 DDR DRAM 기반 범용 프로세서가 각 메모리 뱅크에 통합된 상용 제품(UPMEM)이 등장하면서 소프트웨어 프레임워크의 필요성이 대두
- 현재 상용 PIM 코어(200MHz RISC-V)는 호스트 CPU(Xeon Gold 2.2GHz) 대비 **11배 느린 클럭**, 부동소수점 연산 능력 부족, 각 뱅크 내 **32MB 제한된 메모리 접근** 등의 한계
- 데이터 레이아웃 변환 비용: 호스트의 DDR 최적화된 레이아웃에서 PIM 뱅크별 독립적 레이아웃으로 재배치 시 **64비트 워드의 각 바이트가 다른 칩의 뱅크에 스트라이핑**되어 64비트 채널의 나머지 56비트가 유휴 상태로 오버헤드 발생 (Figure 2)
- 벡터 엔진(AVX)이 호스트에는 존재하나, 상용 PIM 제품에는 벡터화 기능이 없어 "PIM or not" 결정에 또 다른 차원 추가

## 방법론

### 3.1. BLIMP 하드웨어 아키텍처

- **Bank-Level In-Memory Processing:** 각 DRAM 뱅크에 200MHz RISC-V RV64GC 프로세서 탑재
- 프로세서 구성: 캐시/테이블/버퍼 없이 instruction buffer와 data scratchpad(1KB)로 구성
- v0 레지스터를 통해 bank row buffer에 직접 접근 가능
- **데이터 레이아웃 제약:** 각 PIM 코어는 자기 뱅크 내 데이터만 접근 가능 → 호스트가 데이터를 명시적으로 레이아웃 변환 (Listing 1)
- 오프로딩 비용 공식:
  - 입력: o_B(r) = r/8 × (t_r + 8t_w + 64t_ops)
  - 출력: o_C(r) = r/8 × (8t_r + t_w + 64t_ops)

### 3.2. BLIMP-V 벡터 엔진 확장

- **row buffer 크기 벡터 연산:** 8192비트(1KB) row buffer를 벡터 레지스터 v1, v2로 활용
- **256개 ALU/FPU:** 각 32비트로 구성된 full width 벡터 연산 유닛
- 일반 DDR 채널(64비트) 대비 **128배 넓은 데이터 패스** 활용 가능
- RISC-V 코어가 벡터 명령어를 순차적으로 실행

### 3.3. 소프트웨어 컴파일 프레임워크

**3단계 식별 프로세스:**
1. **Step 1 - 벡터화 가능?** Inter-loop 데이터 독립성, 비단축 반복, 마스크 가능한 조건 검사
2. **Step 2 - 병렬화 가능?** Inter-loop 요소 독립성 검사 (벡터화보다 느슨한 조건)
3. **Step 3 - 오프로딩 가능?** 코드 크기, 입력 데이터 크기, 작업 스크래치 패드 크기, 출력 데이터 크기가 32MB 뱅크에 맞는지 + 오프로딩 이득이 비용보다 큰지 검사

**4단계 컴파일 패스 (Figure 4):**
1. **Region Identification:** 코드 블록을 식별하고 오프로딩 가능성 태깅
2. **Source Separation:** 오프로딩 가능한 블록을 별도 소스 파일로 분리, auto-generated offload preamble/postamble 삽입
3. **Code Compilation:** RISC-V 컴파일러로 bank-level 코드 컴파일, 호스트 컴파일러로 나머지 컴파일
4. **Application Recombination:** RISC-V ELF를 호스트 애플리케이션의 데이터 세그먼트에 배치

**런타임 동작:**
- 애플리케이션 시작 시 bank ELF를 해당 bank로 로드
- offload preamble에서 런타임 검사 후 입력 데이터를 bank로 오프로딩
- 메모리 컨트롤러에 syscall로 bank 연산 시작 지시
- 연산 완료 후 onload postamble에서 출력 데이터 복구

## 핵심 기여

1. **PIM은 만능이 아님:** 16개 애플리케이션 중 상당수가 오프로딩 비용, 제한된 메모리 공간, 느린 클럭 속도로 인해 호스트 코어에서 실행하는 것이 더 효율적
2. **자동 컴파일 프레임워크 필수:** 벡터화/병렬화/데이터 크기/오프로딩 비용을 종합 분석하여 what/where/how를 자동 결정하는 LLVM 기반 프레임워크 개발
3. **BLIMP-V 벡터 엔진 유용성:** 128배 넓은 벡터 연산으로 벡터화된 워크로드에서 significant speedup 가능
4. **하드웨어 구성의 영향:** 뱅크 수, 클럭 속도, 호스트 프로세서 성능에 따라 "to PIM or not" 결정이 달라짐
5. **데이터 레이아웃 비용이 핵심:** 오프로딩 전후 데이터 재배치 비용이 성능을 좌우하는 주요 요인

**Broader Significance:** DDR DRAM 기반 범용 PIM 시스템에서 소프트웨어 프레임워크의 중요성을 최초로 체계적으로 분석하고, PIM이 만능이 아닌 특정 조건에서만 유용하다는 것을 실증적으로 입증한 연구

## 주요 결과

- **호스트 시스템:** Intel Xeon Gold 5220R (2.2GHz, 96코어) + AVX-512 + 512GB RAM
- **시뮬레이터:** riscvOVPsim (RISC-V 시뮬레이터) + DRAMSim2 (DDR4 모델링)
- **PIM 하드웨어:** 128개 BLIMP/BLIMP-V 뱅크 (각 32MB, 총 4GB)
- **컴파일러:** LLVM 프레임워크 기반 C/C++ 컴파일러 확장
- **평가 대상:** SPEC CPU 2017 9개 애플리케이션 + Phoenix MapReduce 7개 애플리케이션

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2022ISCA-summarize/to-pim-or-not-for-emerging-general-purpose-processing-in-ddr-memory-systems.md|전체 요약 보기]]
