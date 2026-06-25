---
tags: [paper, 2019, 2019HPCA, topic/compression, topic/dram, topic/nvm, topic/storage]
venue: "25th IEEE International Symposium on High Performance Computer Architecture (HPCA '19)"
year: 2019
summary_path: "../paper-summaries/2019HPCA-summarize/cidr-a-cost-effective-in-line-data-reduction-system-for-terabit-per-second-scale-ssd-arrays.md"
---

# CIDR: A Cost-Effective In-line Data Reduction System for Terabit-per-Second Scale SSD Arrays

**Venue:** 25th IEEE International Symposium on High Performance Computer Architecture (HPCA '19)
**저자:** Mohammadamin Ajdari (POSTECH), Pyeongsu Park, Joonsung Kim, Dongup Kwon, Jangwoo Kim (Seoul National University)

## 개요

- 매일 2.5 quintillion bytes의 데이터가 생성되며, 빅 데이터 분석, 머신 러닝, VDI의 수요가 급증하여 차세대 스토리지 서버에 대용량·고성능이 요구됨.
- SSD array는 높은 용량과 성능을 제공하지만, SSD 비용이 비싸고 쓰기 수명에 제한이 있어 **데이터 감소(deduplication, compression) 기술이 필수적**.
- 클라우드 환경에서 dedup+compression 조합으로 **60% 스토리지 절약** (일반 사용자 데이터), VM 환경에서 **최대 90% 절약** 가능.
- 기존 소프트웨어 기반 데이터 감소의 한계:
  - 24코어 서버에서 평균 **4.2 GB/s (33.6 Gbps)** 처리량에 불과
  - Tbps 규모 달성 시 **23개 소켓**의 고급 22코어 CPU 필요 (일반 메인보드는 최대 4소켓 지원)
- 기존 하드웨어 가속화 방식의 한계:
  - **SSD 내장 가속:** RAID-0 16 SSD 환경에서 최대 **90% dedup 기회 상실** (중복 데이터가 서로 다른 SSD로 분산)
  - **ASIC 기반 가속:** 고정된 하드웨어로 워크로드 변화에 대응 불가, 비용 효율성 떨어짐

## 방법론

### 3.1. 전체 시스템 구성

- 호스트 CPU에 연결된 **FPGA 보드 배열**로 구성
- 각 FPGA는 데이터 감소 엔진(signature generation, compression) 포함
- **중앙 집중식 메타데이터 서버**가 노드 전체 메타데이터 관리
- NVRAM(Non-volatile RAM)을 활용한 메타데이터 영속성 보장

### 3.2. 데이터 감소 워크플로우 (Figure 1)

#### 3.2.1. 쓰기 요청 처리

1. 클라이언트가 데이터와 LBA(Logical Block Address) 전송
2. **Signature generation:** 데이터 블록의 고유 서명 생성 (dedup용)
3. **Deduplication check:** 중앙 메타데이터 테이블에서 중복 검사
4. **Compression:** 중복되지 않은 데이터 블록 압축
5. **SSD 저장:** 압축된 데이터를 SSD array에 기록
6. **메타데이터 업데이트:** 중앙 테이블에 새 메타데이터 추가

#### 3.2.2. 읽기 요청 처리

1. 클라이언트가 LBA로 데이터 요청
2. **메타데이터 조회:** 중앙 테이블에서 LBA对应的 PBA(Physical Block Address) 및 압축 정보 검색
3. **SSD에서 데이터 읽기:** 해당 PBA에서 압축된 데이터 로드
4. **Decompression:** 데이터 디压缩 후 클라이언트에 전달

### 3.3. FPGA 하드웨어 설계

- **Signature Generation Engine:** 해시 함수 기반 고유 서명 생성
- **Compression Engine:** 블록 레벨 압축 알고리즘 하드웨어 구현
- **Metadata Controller:** 중앙 메타데이터 서버와의 통신 및 동기화
- **PCIe 인터페이스:** 호스트 CPU와의 고속 데이터 교환

### 3.4. 소프트웨어 지원 모듈

- **Workload Profiler:** 런타임에 워크로드 패턴 분석 (read/write ratio, dedup ratio, compression ratio)
- **Dynamic Mapping:** 분석 결과를 기반으로 FPGA 리소스 할당 최적화
- **Metadata Manager:** 중앙 메타데이터 테이블 관리 및 동기화

## 핵심 기여

- **핵심 Contribution:** FPGA 기반 비용 효율적인 인라인 데이터 감소 시스템으로 Tbps 규모 SSD array 달성.
- **성능:** 소프트웨어 기반 대비 최대 2.47x (write-only), 3.2x (mixed) 성능 향상.
- **확장성:** PCIe 기반 확장으로 소켓 수 제한 없이 Tbps 규모 달성 가능.
- **비용 효율성:** FPGA 재구성 가능성으로 다양한 워크로드에 대응, ASIC 대비 높은 비용 효율성.
- **의의:** 차세대 스토리지 시스템에서 데이터 감소의 확장성 문제를 근본적으로 해결하며, 실용적인 하드웨어-소프트웨어 공동 설계 접근법 제시.

## 주요 결과

- **구현 언어:** Verilog (FPGA 하드웨어), C/C++ (소프트웨어 모듈)
- **프로토타입:** 2개 FPGA 보드 기반 구현
- **FPGA 보드:** 상용 FPGA 보드 사용 (구체적 모델 미명시)
- **호스트 서버:** 다중 소켓 CPU 서버
- **네트워크:** PCIe 기반 고속 인터커넥트

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2019HPCA-summarize/cidr-a-cost-effective-in-line-data-reduction-system-for-terabit-per-second-scale-ssd-arrays.md|전체 요약 보기]]
