---
tags: [paper, 2018, 2018ISCA, topic/dram]
venue: "International Symposium on Computer Architecture (ISCA) 2018"
year: 2018
summary_path: "../paper-summaries/2018ISCA-summarize/energy-efficient-neural-network-accelerator-based-on-outlier-aware-low-precision-computation.md"
---

# Energy-efficient Neural Network Accelerator Based on Outlier-aware Low-precision Computation

**Venue:** International Symposium on Computer Architecture (ISCA) 2018
**저자:** Eunhyeok Park, Dongyoung Kim, Sungjoo Yoo (Seoul National University)

## 개요

- 딥러닝 가속기의 에너지 효율은 서버 및 모바일 기기에서의 활용 적합성을 결정하는 핵심 요소
- 정밀도 감소는 에너지 효율 향상의 유효한 수단이지만, 기존 양자화 방법은 ResNet-101과 같은 깊은 네트워크에서 4비트와 같은 낮은 정밀도를 달성하지 못함
- 기존 양자화의 한계:
  - 균일한 수준 간격을 사용하는 기존 방법은 아웃라이어에 의해 대부분의 수준을 낭비
  - 낮은 정밀도(4비트)에서 심각한 양자화 오류 발생
  - 아웃라이어 존재로 인해 정밀도 제한이 어려움
- 기존 가속기(Eyeriss, ZeNA)의 한계:
  - 8비트 또는 16비트 정밀도 기반
  - 아웃라이어 처리 비효율

## 방법론

### 3.1. 전체 구조
- PE 스웜(PE swarm): 여러 PE 클러스터, 스웜 버퍼, 컨트롤러로 구성
- PE 클러스터: 활성화/가중치 버퍼, PE 그룹, 클러스터 출력 버퍼로 구성
- PE 그룹: 여러 MAC 유닛, 그룹 활성화/가중치/출력 버퍼로 구성
- 두 가지 유형의 PE 그룹:
  - 일반 PE 그룹: 16개 일반 4비트 MAC + 1개 아웃라이어 MAC
  - 아웃라이어 PE 그룹: 17개 혼합 정밀도 MAC (16비트 × 4비트 연산 지원)

### 3.2. 데이터플로우
- 가중치 청크(weight chunk): 80비트 구조
  - 16개 4비트 가중치
  - 8비트 아웃라이어 포인터(OL ptr)
  - 4비트 아웃라이어 인덱스(OL idx)
  - 4비트 아웃라이어 MSB(OL MSB)
- 활성화 청크(activation chunk): 16×4비트 입력 활성화
- 출력 트리버퍼(tri-buffer): 24비트 × 16 부분 합 관리

### 3.3. 일반 PE 그룹 동작
- 아웃라이어 가중치가 1개인 경우:
  - 아웃라이어 MAC이 OL MSB와 활성화를 곱함
  - 결과를 일반 MAC에 브로드캐스트
  - 1클록 사이클에 17 MAC 유닛 동작
- 아웃라이어 가중치가 2개 이상인 경우:
  - 두 개의 가중치 청크 사용
  - 2클록 사이클 필요 (8비트 가중치 × 4비트 활성화)

### 3.4. 아웃라이어 PE 그룹
- 아웃라이어 활성화는 스웜 버퍼에만 저장
- 희소 데이터 구조: 16비트 활성화 + 3개 좌표(w.idx, h.idx, c.idx)
- 17개 혼합 정밀도 MAC 유닛으로 16개 출력 채널의 부분 합 생성

### 3.5. 부분 합 축적
- 일반 및 아웃라이어 축적 유닛의 파이프라인 방식 동작
- 트리버퍼의 3개 버퍼를 교차 접근하여 일관성 문제 해결
- 일반 유닛이 먼저 부분 합을 추가한 후 아웃라이어 유닛이 접근

### 3.6. 제로 건너뛰기
- 영(0) 입력 활성화에 대한 연산 건너뛰기
- 비영 값 수가 다른 활성화 청크에 따라 PE 그룹 완료 시간 차이
- 동적 자원 할당으로 높은 MAC 유닛 활용도 유지

## 핵심 기여

- 아웃라이어 인식 양자화를 하드웨어로 구현한 최초의 가속기
- 4비트 정밀도로 깊은 딥러닝 네트워크 지원 (ResNet-101 등)
- 아웃라이어 가중치/활성화의 차별화 처리로 효율성 극대화
- 기존 16비트 가속기 대비 최대 62.2% 에너지 절감
- 메모리 접근 감소와 연산 단위 축소를 통한 에너지 효율 달성

## 주요 결과

- 언어: Verilog
- 프로세스: 65nm LP 상용 라이브러리
- 클럭 주파수: 250 MHz
- 전압: 1.0 V
- 설계 도구: Design Compiler
- SRAM 면적/전력/지연: CACTI 사용
- DRAM 전력 모델: Micron 기반

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2018ISCA-summarize/energy-efficient-neural-network-accelerator-based-on-outlier-aware-low-precision-computation.md|전체 요약 보기]]
