---
tags: [paper, 2018, 2018ISCA, topic/cache, topic/dram, topic/gpu, topic/pim]
venue: "International Symposium on Computer Architecture (ISCA) 2018"
year: 2018
summary_path: "../paper-summaries/2018ISCA-summarize/neural-cache-bit-serial-in-cache-acceleration-of-deep-neural-networks.md"
---

# Neural Cache: Bit-Serial In-Cache Acceleration of Deep Neural Networks

**Venue:** International Symposium on Computer Architecture (ISCA) 2018
**저자:** Charles Eckert, Xiaowei Wang, Jingcheng Wang, Arun Subramaniyan, Ravi Iyer†, Dennis Sylvester, David Blaauw, Reetuparna Das (University of Michigan, Intel Corporation)

## 개요

- 프로세서 칩당 코어 수는 지속적으로 증가하는 반면, 메모리 지연 시간은 상대적으로 변하지 않아 메모리 벽(memory wall) 문제 심화
- 데이터 집약적 시스템에서 에너지의 상당 부분이 메모리와 연산 유닛 간 데이터 이동에 소비됨
- 기존 PIM(Processing-in-Memory) 접근의 한계:
  - DRAM에 로직을 통합하는 3D 스택 방식 → DRAM 공정이 로직 계산에 최적화되지 않음
  - 각 DRAM 다이에 별도 로직 다이 필요 → 추가 비용 발생
- 현대 프로세서 다이의 70% 이상이 데이터 저장/검색에 사용됨 → 이를 연산에 활용하면 대규모 병렬 처리 가능

## 방법론

### 3.1. SRAM 배열에서의 제자리 연산
- 다중 워드 라인을 동시에 활성화하여 비트 라인에서 연산 수행
- 낮은 워드 라인 전압으로 멀티-row 접근 시 데이터 손실 방지
- 20개의 28nm 테스트 칩 측정: 64개 워드 라인 동시 활성화 시에도 데이터 손실 없음
- 6시그마 이상의 안정성 (Monte Carlo 시뮬레이션)

### 3.2. 비트 직렬 연산
- 8비트 정밀도(quantized) 기반: 입력 및 필터 가중치
- 비트 라인에 저장된 비트 간 AND/NOR 연산으로 곱셈, 덧셈, 축소(reduction) 수행
- 각 열이 별도 계산을 수행하며, 수천 개의 메모리 배열이 동시에 동작
- Xeon E5 캐시에서 최대 1,146,880개의 비트 직렬 ALU 슬롯 확보 가능

### 3.3. 데이터 레이아웃 및 매핑
- 전치 레이아웃: 필터 가중치를 비트 라인에 저장
- 채널 수준 병렬성 활용: 합성곱당 R×S MAC 연산을 채널 간 병렬로 수행
- 필터 분할(filter splitting): 큰 필터를 비트 라인 간 분할
- 필터 패킹(filter packing): 1×1 필터의 효율적 배치
- 캐시 슬라이스당 20개 웨이: way-20(CPU 정상 처리), way-19(입출력 저장), way-1~18(연산/필터)

### 3.4. 계층별 구현
- **합성곱**: 입력 스트리밍 + 필터 고정(stationary) 방식, 채널별 축소
- **완전 연결**: 합성곱과 동일한 연산 구조로 매핑
- **맥스 풀링**: 차감 후 MSB를 마스크로 활용한 선택적 복사
- **양자화**: 레이어 전체 min/max 계산 → CPU 부동소수점 연산 → 캐시 내 정수 곱셈/덧셈/시프트
- **배치 정규화**: 32비트 부호 없는 정수로 변환 후 재양자화
- **ReLU**: MSB를 쓰기 활성화로 활용한 선택적 0 쓰기

### 3.5. 트랜스포즈 메모리 유닛 (TMU)
- 비트 병렬 레이아웃 ↔ 전치 레이아웃 변환 하드웨어
- 8T SRAM 배열 기반, 수평/수직 양방향 접근 가능
- 캐시 컨트롤 박스(C-BOX)에 소수 개 배치로 인터커넥트 대역폭 포화

## 핵심 기여

- Neural Cache는 캐시를 대규모 벡터 연산 유닛으로 재활용하는 혁신적 접근
- CPU 대비 18.3배 지연 시간 향상, GPU 대비 7.7배 향상
- 전력 소비를 CPU 대비 50% 절감하면서 처리량 12.4배 향상
- 데이터 이동을 완전히 제거함으로써 에너지 효율성 극대화
- 현대 프로세서의 높은 실리콘 활용률(70% 이상 저장용)을 연산으로 전환하는 새로운 패러다임 제시

## 주요 결과

- 28nm 공정 기반 테스트 칩에서의 제자리 연산 검증
- 인텔 Xeon 프로세서 캐시 구조를 모델링한 시뮬레이션
- LLC 슬라이스: 14개, 80개 32KB 뱅크 (20웨이 × 4서브어레이)
- 8KB SRAM 배열 단위로 병렬 연산 수행
- 8비트 양자화 정밀도 (Google TPU와 동일)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2018ISCA-summarize/neural-cache-bit-serial-in-cache-acceleration-of-deep-neural-networks.md|전체 요약 보기]]
