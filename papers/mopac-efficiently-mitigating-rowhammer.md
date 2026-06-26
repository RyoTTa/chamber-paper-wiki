---
tags: [paper, 2025, 2025ISCA, topic/cache, topic/dram, topic/rowhammer]
venue: "ISCA '25 (52nd Annual International Symposium on Computer Architecture), June 21–25, 2025, Tokyo, Japan"
year: 2025
summary_path: "../paper-summaries/2025ISCA-summarize/mopac-efficiently-mitigating-rowhammer.md"
---

# MoPAC: Efficiently Mitigating Rowhammer with Probabilistic Activation Counting

**Venue:** ISCA '25 (52nd Annual International Symposium on Computer Architecture), June 21–25, 2025, Tokyo, Japan
**저자:** Suhas Vittal, Salman Qazi, Poulami Das, Moinuddin Qureshi

## 개요

- Rowhammer는 DRAM row의 활성화가 인접 row의 비트 플립을 유발하는 보안/신뢰성 위협으로, 공격 기준치(TRH: Rowhammer Threshold)가 지속적으로 감소: 2014년 140K → 2020년 4.8K
- JEDEC는 DDR5 확장으로 PRAC(Per-Row Activation Counters)와 ALERT-Back-off(ABO)를 도입하여 각 row마다 활성화 카운터를 DRAM에 저장하고 보안적으로 안전한 완화 방식을 표준화
- PRAC의 핵심 문제: 카운터 업데이트를 위해 DRAM 타이밍을 확장 (tRP: 14ns→36ns, 2.57x; tRC: 46ns→52ns, 1.13x)하여 **모든 활성화에 대해 10% 평균 성능 저하** 발생
- 현재 TRH(4.8K) 또는 향후 TRH(500) 수준에서 ABO가 거의 발생하지 않음에도 불구하고, PRAC 카운터 업데이트 오버헤드만으로도 상당한 성능 손실 초래
- TRH=500 기준 MoPAC-C와 MoPAC-D의 평균 slowdown은 각각 1.7%와 0.7%로, PRAC의 10%에 비해 크게 감소

## 방법론

### 3.1. MoPAC-C (메모리 컨트롤러 측 구현)

- **Two precharge commands:** PRE(일반 precharge, 정상 레이턴시, 카운터 업데이트 없음)와 PREcu(카드 업데이트 포함, 높은 레이턴시)로 구성
- 메모리 컨트롤러가 각 활성화마다 확률 p로 counter-update 여부를 결정 → p에 해당하는 확률로 PREcu 사용
- **安全保障 파라미터:** p=1/64(4K), 1/32(2K), 1/16(1K), 1/8(500), 1/4(250)
- **Critical Number of Updates (C):** 이항 분포를 사용하여 확률 ε 이하의 보안 실패율을 보장하는 C 값 결정
  - 예: TRH=500에서 C=22, ATH*=176, 업데이트 8x 감소
- JEDEC 사양의 사소한 수정 필요: 두 종류의 precharge 명령과 MR(Machine Register)을 통한 p 값 설정 인터페이스

### 3.2. MoPAC-D (DRAM 내부 구현)

- **Selected Row Queue (SRQ):** 각 bank에 16-엔트리 큐 (3 bytes/엔트리, bank당 48 bytes SRAM)로 카운터 업데이트 대상 row를 버퍼링
- MINT를 사용한 확률적 선택으로 정확히 1/p 활성화마다 하나의 엔트리를 SRQ에 삽입
- **ABO를 이용한 시간 획득:** SRQ가 가득 차면 ABO를 트리거하여 350ns 동안 최대 5개 row의 카운터 업데이트 수행 (row당 70ns)
- **Drain-on-REF:** 리프레시 시간의 일부를 활용하여 SRQ 엔트리를 추가로 드레인하여 ABO 발생률 추가 감소
  - TRH=1000에서 REF당 1개, TRH=500에서 2개, TRH=250에서 4개 드레인
- **Tardiness 제어:** ACtr 카운터로 SRQ 진입 후 활성화 수를 추적, TTH(32) 초과 시 강제 ABO 트리거하여 보안 보장

## 핵심 기여

- **핵심 기여:** PRAC의 카운터 업데이트 오버헤드를 확률적으로 감소시켜 PRAC 상용화의 주요 장애물 제거
- **성능:** TRH=500 기준 PRAC 10% → MoPAC-C 1.7%, MoPAC-D 0.7% (NUP 적용 시 0%)
- **보안:** 이항 분포 기반 보안 분석으로 Bank-MTTF 10K년 보장, Double-sided 공격에서도 동시 실패 확률 제곱근 적용
- **유연한 구현:** JEDEC 사양 변경 최소화(MoPAC-D) 또는 MC 구현 옵션(MoPAC-C) 제공
- **DRAM 업계의 PRAC 채택을 촉진하는 실용적 솔루션으로, 향후 DDR6/LPDDR6 표준에 기여할 것으로 기대**

## 주요 결과

- **시뮬레이터:** DRAMSim3 기반 상세 메모리 모델, DDR5 스펙 (JESD79-5C)
- **시스템 구성:** Out-of-Order 8코어 4GHz, 4-wide, 256-entry ROB, LLC 8MB 16-Way
- **구현 언어:** C++ (DRAMSim3 시뮬레이터 확장), Python (분석 스크립트)
- **MoPAC-D 하드웨어 오버헤드:** bank당 48 bytes SRAM (16-entry SRQ), DDR4 TRR(32-entry)보다 적은 오버헤드

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]


## 전체 요약

[[../paper-summaries/2025ISCA-summarize/mopac-efficiently-mitigating-rowhammer.md|전체 요약 보기]]
