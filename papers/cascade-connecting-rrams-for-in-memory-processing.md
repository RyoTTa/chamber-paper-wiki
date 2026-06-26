---
tags: [paper, 2019, 2019MICRO, topic/pim]
venue: "52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '19)"
year: 2019
summary_path: "../paper-summaries/2019MICRO-summarize/cascade-connecting-rrams-for-in-memory-processing.md"
---

# CASCADE: Connecting RRAMs to Extend Analog Dataflow In An End-To-End In-Memory Processing Paradigm

**Venue:** 52nd Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '19)
**저자:** Teyuh Chou, Wei Tang, Jacob Botimer, Zhengya Zhang (University of Michigan, Ann Arbor)

## 개요

- 딥러닝(DNN)과 순환 신경망(RNN)이 이미지 분석, 음성 인식 등에 광범위하게 배포됨에 따라 고효율 저전력 추론 하드웨어에 대한 수요 급증
- In-RRAM PIM(Processing in Memory)은 RRAM 크로스바 어레이에서 병렬 곱셈-누적(MAC) 연산을 수행하여 데이터 이동 없이 높은 병렬성 달성 가능
- 그러나 in-RRAM 연산의 핵심 제약요소:
  - **A/D 변환 비용:** ISAAC 아키텍처에서 8-bit ADC가 전체 전력의 **58%**, 실리콘 면적의 **31%**를 차지
  - RRAM 어레이 크기와 해상도가 증가하면 필수 ADC 해상도도 증가 → A/D 변환이 eventual로 영역 및 에너지 소비를 지배
- **SA 기반 인터페이스의 한계:** PRIME은 sense amplifier로 면적을 줄였으나, 6-bit 출력을 얻기 위해 최대 2^6 사이클의 결정 시간 필요 → 지연 시간이 해상도에 지수적으로 의존
- **크기 제한:** 최신 RRAM 크로스바는 64×64 ~ 256×256 크기 → AlexNet FC 레이어의 경우 9,216개 부분합 축적, GoogLeNet Conv 레이어는 1,728개 부분합 축적 필요 → 단일 크로스바로는 처리 불가
- **부분합 디지털 축적의 비효율:** 16비트 입력의 경우 16회 A/D 변환과 SRAM/레지스터에서의 데이터 왕복 발생 → 에너지 효율성 심각 저하
- 실제 PIM 칩들은 high-resolution 출력의 비용을 줄이기 위해 최상위 비트(MSB)만 디지털화하는 등 제한적 접근 → 응용 범위 제한

## 방법론

### 3.1. MAC RRAM에서의 입력 스트리밍 및 가중치 매핑

- **비트 직렬 입력 스트리밍 (bWL = 1):** 16비트 입력을 LSB부터 MSB까지 16개 WL 펄스로 전송
  - 1비트 WL 드라이버는 다중 비트 DAC 대비 더 단순하고 소형이며 저전력
- **가중치 매핑:** 16비트 가중치를 1셀당 1비트(bcell = 1)로 매핑
  - 16비트 가중치는 한 행의 16개 셀에 저장
  - 64×64 MAC RRAM은 한 행에 4개의 16비트 가중치를 저장, 총 256개 가중치 수용
  - 64×64 어레이는 4개의 64×16 하위 구간으로 분할 가능
- **BL 해상도:** bWL=1, bcell=1, Nrows=64 → **7비트** BL 해상도
  - 인코딩 적용 후 **6비트**로 추가 감소 (Table 1에서 기존 작업 대비 최저)
  - 낮은 해상도 → 노이즈 및 변동(variation)에 대한 높은 허용 margin

### 3.2. 버퍼 RRAM에서의 부분합 버퍼링

- MAC RRAM의 BL이 아날로그 부분합을 운반 → 비트 직렬 입력 스트리밍에서 새 입력 비트 벡터마다 새로운 부분합 생성
- **디지털 축적 vs 아날로그 in-RRAM 축적:**
  - 기존(ADC/SA 기반): 매 사이클 ADC로 부분합을 디지털화 → SRAM에서 임시 합 읽기/쓰기 → LSB 트런케이션 → **16회 A/D 변환 필요**
  - CASCADE: TIAs로 아날로그 전압 변환 → 버퍼 RRAM에 아날로그 부분합 저장 → **최종 A/D 변환만 수행**
- **R-Mapping 스킴 (Figure 5):**
  - LSB 우선 비트 직렬 스트리밍에서 입력 비트 벡터 0의 16개 부분합을 버퍼 RRAM 주소 i에 저장
  - 입력 비트 벡터 1의 부분합은 1비트 왼쪽 시프트 후 주소 i+1에 저장
  - 16비트 입력 완료 시 15행×30열(부호 있는 입력 기준)에 부분합 저장
  - 최종 축적을 버퍼 RRAM의 단일 읽기로 수행 가능
- **에너지 절감:** 아날로그 in-RRAM 버퍼링/축적이 디지털 축적 대비 **7.59배** 적은 에너지 사용
  - SRAM 반복 읽기/쓰기 제거가 주요 기여 요소

### 3.3. TIA 인터페이스

- TIA: 입력 전류를 비례하는 출력 전압으로 변환 (OTA + 피드백 저항)
- MAC RRAM의 BL 아날로그 전류를 버퍼 RRAM의 입력 전압으로 직접 변환
- ADC/SA 인터페이스 대비 **77.5배(ADC) / 325.4배(SA)** 낮은 에너지 소비
- 버퍼 RRAM은 6비트 MLC RRAM 사용 → MAC RRAM의 6비트 BL 해상도와 호환

### 3.4. 최종 축적 및 출력

- 16회 비트 직렬 스트리밍 완료 후 버퍼 RRAM에서 아날로그 최종 합산
- Summing amplifier로 여러 열의 부분합을 결합
- ADC로 최종 10비트 출력 디지털화 (A/D 변환 횟수 대폭 절감)

## 핵심 기여

- **핵심 기여:** MAC RRAM과 버퍼 RRAM을 TIA 인터페이스로 연결하여 아날로그 데이터 플로우를 확장하는 end-to-end in-RRAM 연산 아키텍처
- A/D 변환과 디지털 부분합 축적을 아날로그 in-RRAM 버퍼링/축적으로 대체 → 에너지 **3.5배** 절감, 처리량 **1.86배** 향상
- R-Mapping 스킴으로 in-RRAM 부분합 축적 효율적 구현, 아날로그 summation으로 저차원 A/D 변환 우회
- 낮은 BL 해상도(6비트)로 변동/노이즈 허용 margin 확보하면서도 실용적 정확도 유지
--edge/IoT 디바이스의 제한된 에너지/면적 환경에 적합한 경량 CMOS 주변장치 기반 설계

## 주요 결과

- **프로세스:** 65nm 기술 기반 시뮬레이션
- **RRAM 모델:** 65nm RRAM 모델 (Chen 등, 2018)
- **SRAM 모델:** 메모리 컴파일러 기반
- **아날로그 부품:** SAR ADC (ISAAC 기반, 65nm 스케일링), SA, Summing amplifier, TIA
- **설계 공간:** 4개 변수 - RRAM 배열 크기(H), 배열 수(R), TIA 수(T), ADC 수(A)
  - 최적: 80개 64×64 RRAM 배열, 배열당 32 TIA, 7개 중앙 ADC → **101 GOPs/s/mm²** 피크 성능
- **총 가중치 저장 용량:** 3.2MB (40KB × 80 블록)
- **DDR4 I/O 대역폭:** 25.6GB/s

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2019MICRO-summarize/cascade-connecting-rrams-for-in-memory-processing.md|전체 요약 보기]]
