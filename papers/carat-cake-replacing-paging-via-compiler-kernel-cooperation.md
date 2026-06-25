---
tags: [paper, 2022, 2022ASPLOS, topic/cache, topic/dram, topic/virtual-memory]
venue: "ACM SIGPLAN International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS) 2022"
year: 2022
summary_path: "../paper-summaries/2022ASPLOS-summarize/carat-cake-replacing-paging-via-compiler-kernel-cooperation.md"
---

# CARAT CAKE: Replacing Paging via Compiler/Kernel Cooperation

**Venue:** ACM SIGPLAN International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS) 2022
**저자:** Brian Suchy, Souradip Ghosh, Drew Kersnar, Siyuan Chai, Zhen Huang, Aaron Nelson, Michael Cuevas, Alex Bernat, Gaurav Chaudhary, Nikos Hardavellas, Simone Campanoni, Peter Dinda (Northwestern University)

## 개요

- 가상 메모리(Virtual Memory), 특히 페이징(Paging)은 현대 시스템의 모든 수준에서 깊이 뿌리박혀 있으나, 하드웨어/소프트웨어 코드esign에 의존하여 TLB, page walker, page walk cache 등 복잡한 하드웨어 구조를 필요로 함
- TLB는 칩 전체 전력의 **15~17%**를 소비하며, 코어당 전력의 **최대 13%**를 차지하고, L1 캐시 에너지 소비의 **20~38%**를 차지함 (Industry reports 및 후속 연구)
- TLB 관련 하드웨어 구조(L1 캐시 대비 거의 동일한 면적 차지)는 점점 복잡해지는 워크로드에서 점점 더 큰 스트레스에 직면: 분산된 TLB 간 coherence 오버헤드도 큼
- 현대 L1 캐시는 virtually indexed로 설계되어 TLB lookup과 병렬로 동작하는데, 이는 synonyms 문제를 방지하기 위해 L1 캐시의 set 수를 제한 → 성능 저하 초래
- 기존 연구에서 CARAT(Compiler-And Runtime-based Address Translation) 개념이 제안되었으나, 사용자 수준(user-level) 프로토타입으로만 평가되어 커널 수준 구현의 도전 과제가 미해결

## 방법론

### 3.1. LLVM 컴파일러 트랜스포메이션

- LLVM IR(Static Single Assignment form) 수준에서 전체 커널 및 사용자 프로그램에 대한 코드 분석 및 변환 수행
- NOELLE 프레임워크를 활용한 정밀한 Program Dependence Graph(PDG) 생성 → CARAT CAKE의 오버헤드는 PDG 정확도에 반비례
- SCAF, SVF 등 다수의 alias 분석을 결합하여 가장 정확한 PDG 생성
- WLLVM/GLLVM을 사용한 whole-program 컴파일: 분리 컴파일 환경에서도 전체 커널/사용자 프로그램을 하나의 모듈로 취급하여 트랜스포메이션 적용
- 프론트엔드로 Clang(C/C++)을 사용하나, LLVM 미들엔드에서 동작하므로 다른 언어 프론트엔드와도 호환 가능

### 3.2. 메모리 보호 메커니즘

- 컴파일러가 모든 메모리 접근 지점에 보호 검사(protection check) 코드를 삽입
- 프로그램 객체 단위의 정확한 메모리 접근 추적 → 하드웨어 페이지 테이블 기반 보호를 소프트웨어로 대체
- 커널과 사용자 프로세스 모두에 대한 보호 적용: 커널 코드 자체에도 컴파일러 트랜스포메이션 적용
- 서명된(signed) 사용자 프로그램만 로드 가능 → 컴파일러 도구 체인으로 생성됨을 증명

### 3.3. 프로세스 추상화 및 분리 컴파일

- Nautilus 커널 위에 Linux 호환 프로세스 추상화 구현
- 커널과 사용자 수준 코드베이스의 분리 컴파일 달성: 런타임에서의 긴밀한 결합에도 불구하고
- 사용자 프로그램은 물리적 주소 공간에 직접 로드되며, 커널 모드에서 실행
- 싱글 어드레스 스페이스 OS 기반으로 커널과 프로세스가 하나의 물리적 주소 공간에서 공존

### 3.4. 메모리 컴팩션/디프래그멘테이션

- 컴파일러 도구 체인이 모든 코드베이스에 걸쳐 할당 및 포인터 이탈 추적을 도입
- 커널은 언제든 메모리 컴팩션/디프래그멘테이션 수행 가능 → 단일 물리적 주소 공간에서 필수적인 기능
- 메모리 객체 마이그레이션을 통한 동적 메모리 최적화

## 핵심 기여

- **핵심 기여 1**: CARAT 개념을 커널 수준으로 확장하여 CARAT CAKE 구현 → 페이징을 완전히 대체하는 최초의 실용적 시스템
- **핵심 기여 2**: Linux 호환 프로세스 추상화를 CARAT CAKE 위에 구현하여 일반 목적 OS로서의 기능 확보
- **핵심 기여 3**: 분리 컴파일 환경에서 커널-사용자 코드베이스의 긴밀한 런타임 결합 달성
- **핵심 기여 4**: TLB 제거를 통한 에너지 절약(15~17%), L1 캐시 크기 확대, 임의 크기 메모리 관리 등 새로운 시스템 이점 제시
- **의의**: 페이징이 1960년대 이후 수십 년간 유지해온 패러다임을 컴파일러/커널 협력으로 대체하는 새로운 패러다임 제시, 향후 메모리 시스템 설계에 큰 영향 미칠 가능성

## 주요 결과

- **기반 커널**: Nautilus (331K+ lines of code, x64 NUMA 하드웨어 직접 실행)
- **컴파일러 프레임워크**: LLVM/Clang 9.0.0
- **분석 프레임워크**: NOELLE (LLVM 기반 고수준 추상화 제공)
- **전체 프로그램 컴파일**: WLLVM 1.3.0 / GLLVM 1.3.0
- **Linux 호환 프로세스 추상화**: Nautilus 커널 확장하여 구현
- **구현 언어**: C/C++ (커널 및 컴파일러 패스)
- **평가 대상**: NAS, PARSEC 벤치마크

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2022ASPLOS-summarize/carat-cake-replacing-paging-via-compiler-kernel-cooperation.md|전체 요약 보기]]
