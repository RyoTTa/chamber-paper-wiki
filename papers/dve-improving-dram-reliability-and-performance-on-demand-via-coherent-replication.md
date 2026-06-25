---
tags: [paper, 2021, 2021ISCA, topic/cache, topic/dram]
venue: "ISCA 2021 (48th Annual IEEE/ACM International Symposium on Computer Architecture)"
year: 2021
summary_path: "../paper-summaries/2021ISCA-summarize/dve-improving-dram-reliability-and-performance-on-demand-via-coherent-replication.md"
---

# Dve: Improving DRAM Reliability and Performance On-Demand via Coherent Replication

**Venue:** ISCA 2021 (48th Annual IEEE/ACM International Symposium on Computer Architecture)
**저자:** Adarsh Patil (University of Edinburgh), Vijay Nagarajan (University of Edinburgh), Rajeev Balasubramonian (University of Utah), Nicolai Oswald (University of Edinburgh)

## 개요

- 기술 축소에 따라 메모리 서브시스템의 failure rate가 증가하고 있으며, 데이터센터 및 슈퍼컴퓨터에서의 필드 연구들이 대용량 메모리 오류/실패 및 예상치 못한 DRAM failure 모드를 보고
- 기존 ECC 기반 보호 방식(SEC-DED, Chipkill 등)는 데이터와 수정 코드를 동일 채널/DIMM에 배치하므로, 메모리 컨트롤러, 채널, 전체 DIMM 장애를 복구할 수 없음
- DDR5에서는 셀 오류율 증가로 in-DRAM ECC가 추가되고 ECC 비트가 8비트→16비트로 2배 증가(64비트 데이터 대비 25%)하지만, 비셀 오류(chip 내부 회로, 보드 레벨 회로, 채널 장애)는 여전히 해결 불가
- Intel Memory Mirroring은 채널 간 미러링을 제공하지만 복사본을 백업으로만 사용하여 성능 이점이 없고, 단일 소켓/메모리 컨트롤러에 복제본을 국한시켜 컨트롤러 장애에 취약
- IBM RAIM은 5개 채널을 RAID-3로 구성하지만 256바이트 고정 읽기/쓰기로 성능이 저하되고 단일 RAIM 컨트롤러 장애에 취약
- 클라우드/HPC 시스템에서 메모리 용량의 최소 50%가 90%의 시간 동안 유휴 상태로, 신뢰성과 성능을 동시에 향상시킬 수 있는 기회 존재

## 방법론

### 3.1. 신뢰성 분석

- **Chipkill 비교**: Dve는 동일 위치의 두 독립 복제 메모리 구성요소가 동시에 실패할 때만 DUE 발생 → Chipkill 대비 DUE 4배 감소
  - Chipkill DUE: ~10⁻², Dve+DSD: 2.5×10⁻³ (4배 개선)
  - Chipkill SDC: 3.1×10⁻¹⁰, Dve+TSD: 2.5×10⁻¹⁶ (6orders 개선)
- **IBM RAIM 비교**: Dve+Chipkill은 RAIM 대비 DUE 172배(2 orders) 감소
  - RAIM DUE: 1.5×10⁻¹⁴, Dve+Chipkill: 8.7×10⁻¹⁷
- **열 위험 인지 매핑**: 칩 간 10°C 온도차를 활용한 리스크 역매핑으로 Dve+TSD의 DUE를 4.15배 추가 절감
  - Intel Mirroring 대비 최소 11% DUE 절감 (열 위험 인지 매핑 적용 시)

### 3.2. Coherent Replication 프로토콜

- **Allow-based 프로토콜**: 복제 디렉토리가 "허가 권한"을 끌어당기는 방식 (reactive)
  - 복제 디렉토리에 해당 위치의 entry가 없으면 invalid 상태로 간주하고 홈 디렉토리에 요청 전달
  - 수정된 더러운 블록은 홈 메모리와 복제 메모리에 동기적으로 기록
  - 개인 쓰기가 많은 워크로드에 적합 (불필요한 invalidate 전파 최소화)
- **Deny-based 프로토콜**: 홈 디렉토리가 "거부 권한"을 복제 디렉토리에 밀어推送하는 방식 (proactive)
  - 새로운 Remote Modified(RM) 상태 추가: 홈 LLC에서 블록이 수정 상태이면 복제본이 stale함을 표시
  - entry가 없으면 원격 쓰기가 없음을 의미하므로 복제본에서 직접 읽기 가능
  - 읽기 전용(또는 대부분 읽기) 워크로드에 적합
- **Dynamic 프로토콜**: Allow/Deny 두 프로토콜을 샘플링 기반으로 동적으로 전환
  - 100M 인스트럭션마다 프로파일링하여 더 나은 프로토콜 선택
  - Allow가 더 나은 워크로드: backprop, fft, ocean_cp, barnes, canneal, mg, lu (개인 쓰기 > 46%)
  - Deny가 더 나은 워크로드: graph500, stencil, xsbench, nw, rsbench, bfs, streamcluster

### 3.3. 복제 메모리 매핑

- **고정 함수 매핑**: f(p) = p/(L+1) - (2×S), 연속 물리 페이지를 인터리빙하여 다른 소켓의 복제 페이지로 매핑
- **테이블 기반 매핑 (RMT)**: OS가 물리 페이지를 복제 페이지로 매핑, 유연한 on-demand 복제 가능
  - RMT는 디렉토리 컨트롤러에서 캐싱 가능, HW walker로 탐색 가능
  - 복제 활성화/비활성화를 프로세스/컨테이너/VM 단위로 제어 가능
- **프로토콜 최적화**:
  - Speculative replica access: 복제 디렉토리 미스 시 홈 디렉토리 접근과 동시에 복제본을 추측 접근하여 레이턴시 중복
  - Coarse-grained replica directory: 캐시 라인이 아닌 블록 단위로 추적하여 오버헤드 경감
  - Sampling based dynamic protocol: 두 프로토콜의 성능을 모니터링하여 최적 선택

## 핵심 기여

- **핵심 Contribution**: NUMA 시스템에서 데이터 복제를 통한 신뢰성+성능 이중 향상 달성, Coherent Replication 프로토콜 제시
- **신뢰성**: Chipkill 대비 DUE 4배, IBM RAIM 대비 172배(2 orders) 개선, Intel Mirroring 대비 11% 추가 개선
- **성능**: Baseline NUMA 대비 최대 29% speedup (Dynamic 프로토콜), 모든 워크로드에서 zero penalty
- **유연성**: On-demand 메모리 복제로 용량-신뢰성 트레이드오프를 런타임에 제어 가능
- **의의**: 기존 ECC 기반 방식과 달리 복제를 통해 메모리 컨트롤러 장애까지 복구 가능한 유일한 방식, 동시에 성능까지 향상시키는 새로운 설계 지점 제시

## 주요 결과

| 항목 | 내용 |
|------|------|
| **프로토콜 검증** | Mur 모델 체커로 무 deadlock 및 Single-Write-Multiple-Reader 불변식 검증 |
| **시뮬레이터** | Prism 프레임워크(Valgrind 기반 트레이스 생성) + 수정된 gem5 |
| **시스템 구성** | 2소켓, 소켓당 8코어 (총 16코어), 3.0GHz |
| **캐시** | L1: 64KB, 8-way, 1 cycle; L2(LLC): 8MB, 16-way, 20 cycles |
| **기본 메모리** | 2×8GB DDR4-2400, 소켓당 1채널 |
| **복제 메모리** | 4×8GB DDR4-2400, 소켓당 2채널 |
| **소켓 간 연결** | Point-to-point, 50ns 레이턴시 |
| **복제 디렉토리** | Fully associative 2K entry |
| **벤치마크** | 20개 (HPC, PARSEC, SPLASH-2x, Rodinia, NAS PB, Parboil, SPEC 2017) |

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2021ISCA-summarize/dve-improving-dram-reliability-and-performance-on-demand-via-coherent-replication.md|전체 요약 보기]]
