---
tags: [paper, 2025, 2025MICRO, topic/cache, topic/disaggregation, topic/dram, topic/gpu, topic/virtual-memory]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO) 2025"
year: 2025
summary_path: "../paper-summaries/2025MICRO-summarize/softwalker-software-page-table-walk-for-irregular-gpu-applications.md"
---

# SoftWalker: Supporting Software Page Table Walk for Irregular GPU Applications

**Venue:** IEEE/ACM International Symposium on Microarchitecture (MICRO) 2025
**저자:** Sungbin Jang, Junhyeok Park, Yongho Lee, Osang Kwon, Donghyun Kim, Juyoung Seok, Seokin Hong (Sungkyunkwan University / ETRI)

## 개요

- GPU는 과학 시뮬레이션, 데이터 분석, 딥 러닝 등 다양한 분야에서 핵심 가속기로 활용되며, NVLink 및 CXL과 같은 고속 인터커넥트를 통해 단일 큰 메모리 도메인으로 통합되는 추세
- 가상 메모리 시스템은 확장된 이질적 메모리 공간에서 데이터 위치를 추상화하고 원활한 접근을 가능케 하는 핵심 기반이나, **주소 변환(address translation)이 점점 심각한 성능 병목**이 되고 있음
- 불규칙한(irregular) 어플리케이션(그래프 처리, 희소 선형 대수, 데이터베이스 작업 등)은 산발적이고 미세한 메모리 접근 패턴을 보이며, 하나의 warp 내 스레드들이 서로 다른 메모리 페이지에 접근하여 **TLB miss율이 급증**
- 기존 GPU는 고정된 소수의 하드웨어 Page Table Walker(PTW)로 TLB miss를 처리하지만, thousands개의 활성 스레드에서 동시에 발생하는 높은 translation 압력 하에서 **PTW 리소스 경쟁으로 인해 막대한 queueing delay** 발생
- NVIDIA A2000 실측 결과: **256개의 동시 page walk 시 메모리 접근 지연이 1-walk 대비 4배 증가** (Figure 4)
- 비정형 워크로드에서 queueing delay가 전체 page table walk 지연의 **평균 95%를 차지**하며, 실제 page table traversal 시간을 크게 초과 (Figure 7)
- 이상적인 시스템(경쟁 없음) 대비 비정형 워크로드에서 평균 **2.58배의 잠재 성능 향상 가능** (512~1024 PTW 필요)

## 방법론

### 3.1. Page Walk Warp (PW Warp)

- 각 SM에 고정된 페이지 walk 전용 warp를 구조적으로 격리하여 배치
- 일반 사용자 warp 컨텍스트를 소비하지 않고, 전용 instruction buffer entry, scoreboard entry, SIMT stack entry를 포함한 독립적 아키텍처 슬롯 보유
- **최고 스케줄링 우선순위** 부여 — page walk 지연은 다른 warp 명령어 실행을 stall시킴
- PW Warp는 16개의 레지스터만 필요 (GPU 레지스터 파일의 미미한 부분)
- 호스트 드라이버가 애플리케이션 커널 디스패치 전에 미리 page walk 명령어를 로드하고 각 SM에 특수 블록을 사전 실행
- 보안: GPU 하드웨어가 warp 간 레지스터 파일 파티셔닝을 강제하며, shared memory는 스레드 블록별로 격리된 논리 주소 공간으로 매핑

### 3.2. ISA 확장

| 명령어 | 설명 |
|--------|------|
| `LDPT` | page table에서 PTE를 로드 (TLB 우회) |
| `FL2T` | 마지막 레벨 PTE로 L2 TLB 엔트리 채움 |
| `FPWC` | 각 page table 레벨의 PTE 로드 후 PWC 엔트리 업데이트 |
| `FFB` | 유효하지 않은 PTE를 Fault Buffer에 저장 (page fault 처리) |

### 3.3. 요청 관리 구조

- **Request Distributor**: L2 TLB-side에서 각 L2 TLB miss를 대상 코어에 할당. per-core 요청 카운터를 유지하여 요청 오버플로우 방지 및 유휴 PW Warp가 있는 코어에만 배정
- **SoftPWB (Software Page Walk Buffer)**: L1D/shared memory 공간의 일부를 재사용한 공유 메모리 기반 요청 버퍼. 각 요청은 33비트 VPN + 31비트 page table base PFN + 2비트 현재 레벨 = 96비트
- **SoftWalker Controller**: SoftPWB 비트맵(2비트/스레드)으로 PW Warp 상태 추적 (invalid/valid/processing)

### 3.4. In-TLB MSHR

- 비정형 어플리케이션에서 L2 TLB 히트율이 2.4%에 불과하여 TLB 엔트리가 심각하게 미활용
- In-TLB MSHR: 각 L2 TLB 엔트리에 pending 비트를 추가하여 세 가지 상태(valid/invalid/MSHR) 지원
- MSHR 포화 시, 교체 정책에 따라 victim TLB 엔트리를 선택하고 해당 엔트리에 미처리 요청의 메타데이터를 저장
- page walk 완료 시 tag-matching된 모든 way의 pending 비트 해제 후 PTE 정보를 채움
- 최대 **1024개의 동시 미처리 요청** 추적 가능
- 하드웨어 오버헤드: In-TLB MSHR 제어 로직 0.0061mm² (28nm UMC 기준)

## 핵심 기여

- **핵심 기여**: GPU에서 소프트웨어 기반 page table walk의 첫 번째 프레임워크 제안 — 고정 하드웨어 PTW의 확장성 한계를 근본적으로 해결
- **성능**: 평균 페이지 walk 지연 72.8% 감소, 어플리케이션 속도 2.24배 향상 (비정형 워크로드 3.94배)
- **효율성**: 하드웨어 비용 대비 소프트웨어 기반 병렬화가 훨씬 효율적 — 동일 면적 예산에서 2.6x 이상의 성능
- **실용성**: 하이브리드 모드로 일반/비정형 워크로드 모두 지원, Unified Virtual Memory와 호환
- **의의**: 향상된 GPU 메모리 시스템에서 소프트웨어 관리 주소 변환이 확장 가능하고 효율적인 솔루션임을 입증

## 주요 결과

- **구현 언어**: SystemVerilog (하드웨어), SASS 어셈블리 (page walk 코드)
- **시뮬레이터**: Accel-sim v1.2.0 기반 cycle-accurate GPU 시뮬레이터 확장
- **ISA 확장**: LDPT, FL2T, FPWC, FFB 4개 명령어 추가
- **소프트웨어 구성 요소**: Request Distributor, SoftWalker Controller, SoftPWB
- **하드웨어 오버헤드**: PW Warp 컨텍스트 1470비트/SM + In-TLB MSHR 1024비트

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2025MICRO-summarize/softwalker-software-page-table-walk-for-irregular-gpu-applications.md|전체 요약 보기]]
