---
tags: [paper, 2025, 2025ISCA, topic/dram, topic/rowhammer]
venue: "ISCA '25 (52nd Annual International Symposium on Computer Architecture), June 21–25, 2025, Tokyo, Japan"
year: 2025
summary_path: "../paper-summaries/2025ISCA-summarize/pudhammer-experimental-analysis-of-read-disturbance-effects-of-processing-using-dram.md"
---

# PuDHammer: Experimental Analysis of Read Disturbance Effects of Processing-using-DRAM in Real DRAM Chips

**Venue:** ISCA '25 (52nd Annual International Symposium on Computer Architecture), June 21–25, 2025, Tokyo, Japan
**저자:** Ismail Emir Yuksel, Akash Sood, Ataberk Olgun, Oğuzhan Canpolat, Haocong Luo, Nisa Bostanci, Mohammad Sadrosadati, Giray Yaglikci, Onur Mutlu

## 개요

- Processing-using-DRAM (PuD)는 DRAM 배열의 대규모 내부 병렬성과 대역폭을 활용하여 데이터 이동 병목을 완화하는 유망한 패러다임 → 데이터베이스, 그래프 처리, 유전체 분석, 생성형 AI 등 가속에 활용
- PuD의 핵심 기법인 **다중 행 활성화(multiple-row activation)**는 기존 DRAM 접근 패턴과 근본적으로 다름: 기존에는 한 번에 하나의 DRAM 행만 활성화하나, PuD는 여러 행을 동시에 또는 빠르게 연속 활성화
- **RowHammer 및 RowPress:** 단일 DRAM 행을 반복 활성화하면 물리적으로 인접한 비접근 행에서 비트 플립이 발생하는 읽기 방해(read disturbance) 현상 → 보안, 안정성, 신뢰성 문제로 악화
- **기존 연구의 한계:** 지금까지 다중 행 활성화 기반 PuD 연산이 읽기 방해에 미치는 영향을 실험적으로 분석한 연구가 없음
- **PuDHammer 현상:** 다중 행 활성화 기반 PuD 연산(PuDHammer)이 읽기 방해를 크게 심화시킴 → 최소 해머 카운트(HC_first)가 RowHammer 대비 최대 158.58배 감소

## 방법론

### 3.1. CoMRA의 읽기 방해 효과

- **Double-sided CoMRA vs RowHammer:** CoMRA로 공격 시 HC_first가 RowHammer 대비 SK Hynix에서 13.98배, Samsung에서 3.28배, Micron에서 1.18배, Nanya에서 1.58배 감소
- **데이터 패턴 영향:** CheckerBoard 패턴(0x55/0xAA)이 일반적으로 가장 효과적이나, 제조사 및 행마다 최악의 데이터 패턴이 다름
- **온도 영향:** 온도 증가에 따라 읽기 방해 효과가 악화되는 경향 (SK Hynix: 50°C→80°C에서 3.45배 HC_first 감소)
- **Single-sided CoMRA:** Single-sided RowHammer보다 더 낮은 HC_first (SK Hynix: 1.42배 감소)
- **CoMRA vs RowPress:** Row on time(𝑡𝐴𝑔𝑔𝑂𝑛)이 증가하면 CoMRA의 HC_first가 크게 감소 (Micron: 78.74배 감소 at 70.2μs)
- **공간 변이:** 서브배 내 행 위치에 따라 HC_first가 최대 2.57배 변이 (Samsung)

### 3.2. SiMRA의 읽기 방해 효과

- **Double-sided SiMRA:** SK Hynix 칩에서만 관찰, RowHammer 대비 HC_first가 최대 158.58배 감소 (4행 동시 활성화)
- **동시 활성화 행 수의 비선형성:** 100%의 비ictim 행에서 2~16행 동시 활성화 시 RowHammer보다 낮은 HC_first 관찰, 최소 HC_first는 26 (RowHammer: 4123 대비)
- **데이터 패턴 영향:** 0x00 비ictim 데이터 패턴이 평균 HC_first를 최대 57.80배 증가 → SiMRA와 RowHammer의 비트 플립 방향이 반대 (SiMRA: 1→0, RowHammer: 0→1)
- **온도 의존성:** 온도 증가에 따라 HC_first가 일관되게 감소 (50°C→80°C에서 3.02~3.26배 감소)
- **𝑡𝐴𝑔𝑔𝑂𝑛 효과:** Row on time 증가 시 HC_first가 144.93~270.27배 감소

### 3.3. RowHammer + PuDHammer 결합 효과

- **CoMRA + RowHammer:** RowHammer만 사용할 때 대비 평균 HC_first가 1.34배 감소 (90% CoMRA 해머 카운트)
- **SiMRA + RowHammer:** CoMRA보다 덜 효과적이나 여전히 HC_first를 1.22배 감소
- **RowHammer + CoMRA + SiMRA:** 가장 효과적인 조합으로 평균 HC_first를 1.66배 감소

### 3.4. TRR 완화 메커니즘 회피

- **TRR 메커니즘:** 샘플링 기반으로 마지막 450개 ACT 명령의 주소를 샘플링하여 잠재적 공격 행을 식별
- **SiMRA의 TRR 회피:** SiMRA-32는 TRR 활성화 시에도 11340배 더 많은 비트 플립 유도
- **CoMRA의 TRR 회피:** CoMRA는 TRR 활성화 시 1.10배 더 많은 비트 플립 유도
- **원인:** SiMRA는 백투백 2개 ACT 명령만 issuing하여 최대 32행을 동시 활성화 → TRR이 2개 공격 행 주소만 감지 가능

## 핵심 기여

- **핵심 기여:** 다중 행 활성화 기반 PuD 연산이 DRAM 읽기 방해를 크게 심화시킨다는 것을 최초로 실험적으로 입증
- **성능 악화 수치:** CoMRA는 HC_first를 최대 13.98배, SiMRA는 최대 158.58배 감소
- **TRR 무용성:** 기존 TRR 완화 메커니즘은 SiMRA/CoMRA에 대해 무효 (11340배 더 많은 비트 플립)
- **완화의 어려움:** 적응형 PRAC도 평균 48.26% 성능 오버헤드 발생 → 새로운 효율적 완화 기법 필요
- **미래 연구 방향:** PuDHammer의 장치 수준 원인 이해, PuD 친화적 읽기 방해 완화 메커니즘 설계 필요

## 주요 결과

- **DRAM 테스트 인프라:** DRAM Bender (FPGA 기반 DDR4 테스트 인프라, SoftMC 기반)
- **테스트 칩:** 40개 DRAM 모듈의 316개 COTS DDR4 DRAM 칩 (SK Hynix, Micron, Samsung, Nanya)
- **물리적 행 주소 매핑:** 모든 칩의 물리적 행 주소 레이아웃을 역공학하여 결정
- **리프레시 비활성화:** 주기적 리프레시를 비활성화하여 읽기 방해 비트 플립을 회로 수준에서 직접 관찰
- **온도 제어:** 열전 Couple 온도 센서와 히터 패드로 50°C~80°C 범위에서 실험

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]


## 전체 요약

[[../paper-summaries/2025ISCA-summarize/pudhammer-experimental-analysis-of-read-disturbance-effects-of-processing-using-dram.md|전체 요약 보기]]
