---
tags: [paper, 2023, 2023ISCA, topic/nvm, topic/pim]
venue: "ISCA 2023 (50th Annual International Symposium on Computer Architecture)"
year: 2023
summary_path: "../paper-summaries/2023ISCA-summarize/on-endurance-of-processing-in-nonvolatile-memory.md"
---

# On Endurance of Processing in (Nonvolatile) Memory

**Venue:** ISCA 2023 (50th Annual International Symposium on Computer Architecture)
**저자:** Salonik Resch, Husrev Cilasun, Zamshed Chowdhury, Masoud Zabihi, Zhengyang Zhao, Jian-Ping Wang, Sachin Sapatnekar, Ulya R. Karpuzcu (University of Minnesota)

## 개요

- 비휘발성 메모리(PIM, Processing-in-Memory) 아키텍처는 메모리 벽(Memory Wall) 문제를 완화하기 위해 메모리 내에서 직접 연산을 수행하는 유망한 기술로 주목받고 있다
- 그러나 NVM(Nonvolatile Memory) 기술은 **제한된 내구성(endurance)**을 가지며, 메모리 셀은 일정 횟수 이상의 쓰기 작업 후 실패한다: MTJ는 ~10^12회, RRAM은 ~10^8-10^9회, PCM은 ~10^6-10^9회
- PIM은 일반 아키텍처 대비 **150배 이상 많은 쓰기 작업**을 유발한다: 예를 들어 32비트 정수 곱셈의 경우, 일반 아키텍처는 64 셀 읽기/쓰기만 필요하지만, PIM 아키텍처(DADDA 곱셈기 사용)는 9,824개의 셀 쓰기와 19,616개의 셀 읽기를 요구한다
- 기존 NVM 로드 밸런싱 전략은 PIM에 직접 적용할 수 없다: PIM 연산은 데이터 레이아웃에 물리적으로 종속되어 있어, 가상-물리 주소 매핑 변경만으로는 올바른 연산이 불가능하다
- PIM 배열에서 **단일 셀 실패**도 전체 연산을 무효화할 수 있다: N×N 배열에서 단일 레인(lane)의 단일 셀 실패는 동일 주소의 모든 레인의 셀을 사용 불가하게 만든다

## 방법론

### 3.1. 쓰기 불균형 분석 (Write Distribution)

- DADDA 곱셈기 기반 32비트 곱셈에서 workspace 셀은 input/output 셀 대비 **수십 배 더 자주 사용**됨 (Fig. 5)
- 각 lane 내부에서 셀 사용량이 크게 불균일하며, workspace 영역이 가장 먼저 실패함
- 병렬도가 높은 애플리케이션(곱셈)은 lane 간 균형이 양호하나, 병렬도가 낮은 애플리케이션(덧셈 기반 dot-product)은 lane 간 불균형이 심각

### 3.2. PIM vs. 일반 NVM 로드 밸런싱의 차이

- **일반 NVM 로드 밸런싱:** 가상-물리 주소 매핑을 변경해 쓰기 작업을 재분배 (Algorithm 1, Fig. 6a)
- **NVPIM 로드 밸런싱:** PIM 연산은 동일 lane의 동일 column에서 operands가 물리적으로 정렬되어야 하므로, 단순 주소 재매핑은 연산 오류를 유발 (Fig. 6b)
- 따라서 PIM 특화 로드 밸런싱은 lane 내부의 logical-to-physical 주소 재매핑과 lane 간 재매핑을 모두 고려해야 함

### 3.3. 셀 실패의 영향

- N×N PIM 배열에서 셀 실패 비율이 증가하면 lane 내 사용 가능한 셀 수가 급격히 감소 (Fig. 11)
- 배열 크기에 관계없이 곱셈 연산조차 수행할 수 없을 정도로 가용 셀이 빠르게 감소
- workaround로 lane을 set으로 나누어 순차 실행하면 수명은 연장되나 지연 시간이 크게 증가

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1. 소프트웨어 로드 밸런싱

**Lane 내부 (Within Lanes):**
- **Random Shuffling (Ra):** logical-to-physical 비트 주소를 무작위로 재매핑하여 cell 사용량 균일화. 단, row-parallel 아키텍처에서 변수의 비트가 여러 byte에 분산되어 메모리 접근 비용 증가 (Fig. 8)
- **Byte-Shifting (Bs):** logical-to-physical 주소를 정수 byte 단위로 주기적 시프팅. 비트 순서와 주소 정렬을 유지하므로 메모리 접근 친화적 (Fig. 9)
- 재컴파일 빈도: 50회 반복마다 시프팅하면 거의 최적의 쓰기 분포에 도달 (전체 100,000회 중 0.05%)

**Lane 간 (Between Lanes):**
- Dot-product의 reduction 연산으로 인해 낮은 주소의 column이 과사용됨
- Byte-Shifting는 column이 과사용되는 영역으로 시프팅되므로 효과 없음
- Random Shuffling이 lane 간 불균형 해소에 더 효과적

### 4.2. 하드웨어 로드 밸런싱

- **Hardware Re-mapping (Hw):** 아키텍처의 레지스터 리네이밍과 유사한 방식으로, lane 내 spare 비트를 활용해 논리-물리 주소를 실행 시점에 재매핑
- 추가 비용 없이 소프트웨어 전략 대비 더 빈번한 재매핑 가능 (매 gate 마다 적용 가능)
- Pinatubo와 같은 SA 기반 아키텍처에서는 추가 데이터 전송 없이 출력 방향만 변경하여 in-place 리매핑 가능
- CRAM과 같은 아키텍처에서는 출력 셀의 초기값이 계산에 영향을 미치므로 추가 쓰기 작업 필요

### 4.3. Memory Access Aware Re-mapping

- 연산 전에 COPY gate로 입력을 셔플링하고, 연산 후 출력을 원래 위치로 복원
- 일반 메모리 읽기/쓰기 패턴을 방해하지 않음
- 오버헤드: 32비트 곱셈의 경우 추가 gate 2.17%, 32비트 덧셈의 경우 61.78% (Table 2)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]]


## 전체 요약

[[../paper-summaries/2023ISCA-summarize/on-endurance-of-processing-in-nonvolatile-memory.md|전체 요약 보기]]
