---
tags: [paper, 2019, 2019MICRO, topic/cache, topic/gpu]
venue: "52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO-52), 2019"
year: 2019
summary_path: "../paper-summaries/2019MICRO-summarize/gencache-leveraging-in-cache-operators-for-sequence-alignment.md"
---

# GenCache: Leveraging In-Cache Operators for Efficient Sequence Alignment

**Venue:** 52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO-52), 2019
**저자:** Anirban Nag, C. N. Ramachandra, Rajeev Balasubramonian, Ryan Stutsman, Edouard Giacomin, Hari Kambalasubramanyam, Pierre-Emmanuel Gaillardon (University of Utah)

## 개요

- 정밀 의학(Precision Medicine)은 암 치료, 희귀 질환 진단 등을 위해 빈번한 유전체 분석을 요구하며, 각 환자당 하루 수백 건의 유전체 분석 쿼리가 필요.
- GATK 파이프라인의 시퀀스 정렬 단계는 현대 CPU에서 **4.5시간** 소요되며, 초당 처리량이 **12.5 Mbases**로 시퀀싱 머신(2300 Mbases/min)의 처리량을 크게 하회 (Figure 1).
- 기존 유전체 가속기 GenAx(2nd gen)와 Darwin(3rd gen)은 대형 스크래치패드와 타일링을 활용하지만, **메모리 대역폭이 주요 병목**으로 작용. GenAx는 153.6 GB/s 메모리 대역폭을 거의 포화시키면서도 배치 처리에 **194초** 소요.
- 시퀀스 정렬의 첫 3단계(시드 선택, 해시 테이블 조회, 필터링)는 다수의 병렬 연산과 메모리 접근을 필요로 하며, 4단계(SWA 동적 프로그래밍)의 부담을 결정적으로 좌우.
- 기존 FPGA 기반 가속기(GateKeeper, DRAGEN 등)는 인캐시 연산자 대비 **병렬성이 낮고**, 참조 유전체 세그먼트를 가져올 때 추가 대역폭 페널티와 캐시 미스 문제가 발생.
- 2nd gen reads의 **75-80%가 0에러(정확한 일치)**, 15%가 1에러, 5%가 2-5에러를 보이지만(Figure 5), 기존 GenAx는 모든 에러 케이스를 동일하게 처리하여 불필요한 계산이大量 발생.

## 방법론

### 3.1. 아키텍처 개요 (Figure 3)

- **Baseline**: GenAx 아키텍처를 기반으로 모델링. GenCache는 GPU 카드와 유사한 co-processor로 동작.
- **구성 요소**: 시딩 려인(Seeding Lanes) × 다수 + 중앙 제어 유닛 + SRAM 배열(In-Cache 연산자 포함) + SWA 엔진
- **작동 흐름**: 읽기(read) 배치 입력 → 시딩 려인에서 시드 선택/필터링 → 중앙 제어 유닛이 In-Cache 연산자에 필터링 명령 전달 → 후보 위치만 SWA 엔진으로 전달
- **SWA 엔진은 변경 없음**: 기존 GenAx의 SWA 엔진을 그대로 사용하여 정확도 보장.

### 3.2. In-Cache 연산자 상세 (Figure 4)

- **기존 연산자 (Compute Caches 기반)**: AND, NOR, OR, XOR, COPY — 비트라인에서 두 워드라인을 동시 활성화하여 비트 단위 연산 수행. 추가 논리 회로 없이 기본 비트라인 주변 회로만으로 구현.
- **5개 신규 RISC-like 연산자**:
  1. **Hamming Mask (HM)**: 두 문자열 간 해밍 마스크 계산 — 정확 일치, SHD/Myer's 알고리즘의 핵심 연산 (Algorithm 1, 2)
  2. **Hamming Distance (HD)**: 해밍 벡터에서 1의 개수 합산 — 정확 일치 검출, SHD/Myer's에서 에러 수 계산
  3. **Shift Left (SL)**: 시프트 연산 — SHD에서 삽입/삭제 시뮬레이션
  4. **Shift Right (SR)**: 시프트 연산 — SHD에서 삽입/삭제 시뮬레이션
  5. **32-bit Addition (ADD)**: 32비트 덧셈 — Myer's 알고리즘의 동적 프로그래밍에서 보조 벡터 계산
- **4개 CISC-like 연산자**: SHD, SHD_C(e+1 에러 필터링), MYERS, MYERS_B(배nded Myer's) — 각각 다수의 RISC 연산을 조합한 매크로 연산. ROM에 RISC 명령 시퀀스를 저장하고, 로컬 제어 회로가 파라미터에 따라 언롤링.
- **하드웨어 구현**: 
  - 비트라인 주변 회로:偶数 비트라인마다 배치, 8:1/4:1 MUX, D-Flip Flop
  - 128비트 Adder Tree: 28nm 기준 **0.55ns** 크리티컬 패스 지연
  - 32비트 Adder: 서브어레이 인접 배치, 128비트 행 덧셈을 4사이클에 처리
  - 로컬 제어 회로 면적: **225μm²**

### 3.3. Error-Aware 4단계 알고리즘 (Figure 7)

- **Phase 1 (정확 일치, 75-80% reads 처리)**:
  - 가장 드문 시드 1개 선택 → 해당 위치에서 In-Cache HD 연산 수행
  - GenAx 대비 메모리 접근 **1000+ → 10 미만**으로 대폭 감소 (Figure 6)
  - Bloom Filter로 0 빈도 시드 사전 검출 → 읽기 skip
- **Phase 2 (1에러, ~15% reads)**:
  - 가장 드문 시드 2개 선택 → 좌/우 시프트된 해밍 마스크 계산 (SL, SR, HM RISC 연산)
  - Bloom Filter로 0/1 빈도 시드 검출
- **Phase 3 (2-5에러, ~5% reads)**:
  - Hobbes 알고리즘(경량 동적 프로그래밍)으로 시드 선택
  - SHD CISC 연산으로 5에러 초과 위치 필터링 (7% false positive)
  - MYERS_B CISC 연산으로 True Positive 확인
- **Phase 4 (6+에러, 나머지)**:
  - SMEM 알고리즘(TCAM 배열 사용, GenAx에 이미 포함)으로 시드 선택
  - MYERS_B로 편집 거리 40 미만 필터링 후 SWA 엔진으로 전달
- **읽기 페칭 최적화**:
  - GenAx: 각 읽기를 1-384회 페칭 (20-25%가 384회 전체 반복)
  - GenCache: 각 읽기를 1-96회 페칭 (75-80%가 Phase 1에서 정확 일치 → 즉시 중단)

### 3.4. SRAM 할당 및 Bloom Filter

- **Phase별 SRAM 재할당**: 
  - Phase 1-2: 참조 유전체 스크래치패드 48MB (In-Cache 연산 최대 활용) + 해시 테이블 캐시 4MB + Bloom Filter 20MB
  - Phase 4: 해시 테이블 캐시 48MB (SMEM 시드 조회 증가)
  - 중앙 제어 유닛이 Phase 시작 시 SRAM 배열을 재구성
- **Bloom Filter 세부사항**:
  - 해시 테이블(1.5GB)의 highly skewed 분포 활용: 70-80% 시드가 0 빈도, 14-17%가 1 빈도
  - 20MB Bloom Filter로 4MB 캐시된 해시 테이블의 고빈도 엔트리 추적
  - Phase 1-2에서 futile 해시 테이블 접근을 사전 차단 → 캐시 오염 방지 + 대역폭 절감
  - False positive rate 10% 기준으로 충분한 성능 달성 (Figure 12)

## 핵심 기여

- GenCache는 **In-Cache 연산자를 유전체 시퀀스 정렬에 최초로 적용**하여 메모리 병목을 극복한 연구.
- **핵심 기여:**
  1. SRAM 배열 내에서 비트 단위 병렬 연산을 수행하는 5개 RISC-like + 4개 CISC-like 연산자 제안
  2. 에러 분포를 활용한 4단계 알고리즘으로 불필요한 계산/메모리 접근 제거
  3. Bloom Filter로 highly skewed 해시 테이블 분포를 효율적으로 처리
  4. 하드웨어-소프트웨어 조합 시 **초가산적 5.26× 속도 향상**과 **8.6× 에너지 효율** 달성
  5. 메모리 접근 **15배 절감** — 향후 보안/프라이버시 강화로 오프칩 접근 비용이 커지는 환경에 적합
- **확장성**: 3rd gen 시퀀싱에도 적용 가능 (1.8× 필터링 향상), Indel Realign, Variant Calling 등 파이프라인 다른 단계에도 확장 가능.
- **의의**: GenAx와 Darwin 모두 지적한 메모리 병목 문제를 In-Cache 연산과 알고리즘 재구성의 시너지로 해결하고, 정밀 의학의 컴퓨팅 요구사항 충족에 기여.

## 주요 결과

- **소프트웨어**: BWA-MEM과 비교하여 정확도 검증. ERR194147_1.fastq 데이터셋(787M reads, 101bp) 사용. GenCache는 GenAx와 동일한 출력 보장 (0.0023% 분산은 SWA tie-breaking 차이).
- **회로 합성**: Synopsys Design Compiler로 비트라인 주변 회로, Adder Tree, 시드 솔버, Bloom Filter 해싱 회로, 중앙 제어 유닛 합성. FDSOI 28nm 기술로 지연/전력/에너지 모델링.
- **시스템 모델**: Aladdin 도구의 수정된 Cacti로 스크래치패드 모델링, DDR4 에너지 51pj/bit 가정. 사이클 정확 시뮬레이터로 전체 아키텍처 모델링.
- **면적 오버헤드**: GenAx 대비 **16.4%** 면적 증가, 피크 전력 **34.7%** 증가, 평균 전력 **15%** 증가.
  - 비트라인 주변 회로: 캐시 서브시스템 면적의 **14.7%** 추가
  - Bloom Filter용 추가 SRAM: 4MB (**5.9%** 오버헤드)
  - Adder Tree와 32-bit Adder: 면적 미미

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/gpu.md|GPU]]


## 전체 요약

[[../paper-summaries/2019MICRO-summarize/gencache-leveraging-in-cache-operators-for-sequence-alignment.md|전체 요약 보기]]
