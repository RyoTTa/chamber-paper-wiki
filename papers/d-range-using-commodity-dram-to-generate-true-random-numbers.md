---
tags: [paper, 2019, 2019HPCA, topic/dram]
venue: "25th IEEE International Symposium on High Performance Computer Architecture (HPCA '19)"
year: 2019
summary_path: "../paper-summaries/2019HPCA-summarize/d-range-using-commodity-dram-to-generate-true-random-numbers.md"
---

# D-RaNGe: Using Commodity DRAM Devices to Generate True Random Numbers with Low Latency and High Throughput

**Venue:** 25th IEEE International Symposium on High Performance Computer Architecture (HPCA '19)
**저자:** Jeremie S. Kim, Minesh Patel, Hasan Hassan, Lois Orosa, Onur Mutlu (Carnegie Mellon University, ETH Zürich)

## 개요

- 난수 생성기(RNG)는 암호학, 과학 시뮬레이션, 산업 테스트 등 다양한 응용에서 필수적이나, 기존 TRNG(True Random Number Generator)는 전용 하드웨어가 필요하거나 고처리량을 달성하지 못함
- 기존 DRAM 기반 TRNG 접근법들은 DRAM 데이터 보유 실패(data retention failure), DRAM 시작값(startup values), DRAM 명령 스케줄링의 비결정성을 활용했으나, 연속적 고처리량(mb/s) 운용이 불가능하거나 근본적으로 비결정적인 엔트로피 소스를 활용하지 못함
- PRNG(Pseudo-Random Number Generator)는 시작 시드 값에 의해 완전히 결정되므로 암호학적 응용에 적합하지 않음
- 효과적인 TRNG는 (1) 진정으로 무작위인 숫자 생성, (2) 저지연 고처리량, (3) 저비용 구현이 가능해야 함

## 방법론

### 3.1. Activation Failure 프로파일링

- DRAM 타이밍 파라미터 tRCD(.row activation latency)를 제조사 권장값 이하로 축소하여 각 DRAM 셀의 활성화 실패 특성 프로파일링
- 각 셀에 대해 여러 tRCD 값으로 테스트하여activation failure 발생 빈도와 무작위성 측정
- 282개 최신 LPDDR4 디바이스(3개 제조사)에서 실험적으로 검증

### 3.2. 무작위 수 생성

- 프로파일링에서 식별된 취약 셀들을 대상으로 축소된 tRCD로 반복 액세스하여 activation failure 유도
- 활성화 실패 시 반환되는 데이터를 엔트로피 소스로 사용
- 여러 셀의 데이터를 집계(aggregation)하여 고처리량 달성
- 일반 DRAM 행 활성화보다 빠르게 activation failure 유도 가능하여 저지연 보장

### 3.3. 셀별 안정성 및 특성

- 시간 변화와 온도 변화에 대해 무작위 데이터가 견고함을 확인
- 테스트 기간 15일 동안, 신뢰 온도 범위 전체(55°C~70°C)에서 고품질 난수 생성 유지
- NIST 표준 무작위성 테스트 스위트에서 모든 테스트 통과

## 핵심 기여

- D-RaNGe는 상용 DRAM 디바이스에서 진정한 무작위 수를 기존 최고 성능 TRNG 대비 100배 이상 높은 처리량으로 생성하는 최초의 방법
- 특화 하드웨어 없이 상용 시스템에서 즉시 구현 가능
- 암호학, 과학 시뮬레이션 등 고처리량 TRNG가 필요한 다양한 응용에 적합
- DRAM 타이밍 위반을 엔트로피 소스로 활용하는 새로운 패러다임 제시

## 주요 결과

- 구현 언어: 소프트웨어 기반 (하드웨어 변경 없음)
- 메모리 컨트롤러에서 DRAM 타이밍 파라미터 조작 능력 필요
- 대부분의 기존 시스템에서 즉시 실행 가능
- SoftMC와 유사한 간단한 소프트웨어 API 노출로 대부분의 디바이스 구현 가능

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2019HPCA-summarize/d-range-using-commodity-dram-to-generate-true-random-numbers.md|전체 요약 보기]]
