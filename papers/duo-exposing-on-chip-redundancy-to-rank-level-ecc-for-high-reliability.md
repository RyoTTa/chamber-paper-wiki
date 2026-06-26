---
tags: [paper, 2018, 2018HPCA, topic/dram]
venue: "IEEE International Symposium on High Performance Computer Architecture (HPCA) 2018"
year: 2018
summary_path: "../paper-summaries/2018HPCA-summarize/duo-exposing-on-chip-redundancy-to-rank-level-ecc-for-high-reliability.md"
---

# DUO: Exposing On-chip Redundancy to Rank-Level ECC for High Reliability

**Venue:** IEEE International Symposium on High Performance Computer Architecture (HPCA) 2018
**저자:** Seong-Lyong Gong (UT Austin), Jungrae Kim (Microsoft), Sangkug Lym (UT Austin), Michael Sullivan (NVIDIA), Howard David (Huawei), Mattan Erez (UT Austin)

## 개요

- DRAM 기술의 지속적인 스케일링으로 인해 고유 결함(inherent faults) 발생률 증가
- 기존 row/column sparing 기술로는 예상되는 높은 고유 결함률을 효율적으로 처리할 수 없음
- In-DRAM ECC(IECC)는 스케일링 에러를 해결할 수 있지만, 높은 신뢰성이 요구되는 시스템에서 rank-level ECC(RECC)와 결합 시 비효율적 발생
- 향후 DDR5와 같은 인터페이스에서 더 긴 버스트로 데이터 전송 시 rank당 fewer devices 사용으로 인해 높은 신뢰성 RECC 구현이 어려워짐

## 방법론

### 3.1. IECC 우회 모드

- 기존 IECC 모듈을 우회하여 온칩 중복성을 메모리 채널을 통해 직접 전달
- IECC의 인코딩/디코딩, 오버페치, read-modify-write 오버헤드 방지
- 현재 DRAM 설계에 대한 значительных 변경 없이 구현 가능

### 3.2. DUO SDDC 설계

- 긴 코드워드를 통한 근본적으로 높은 검출 및 정정 능력
- 여러 가지 2차 정정 기법 통합으로 정정 능력 추가 확장
- 다양한 결함 오류 모델에서의 높은 신뢰성 검증

### 3.3. 다양한 DRAM 구성 지원

- 낮은 신뢰성 시스템(非ECC DIMM) 지원
- 높은 신뢰성 시스템 지원
- DDR5와 같은 향후 인터페이스에서의 좁은 rank 구성 지원

## 핵심 기여

- DUO를 통해 IECC의 비효율성을 해결하면서 높은 신뢰성 달성
- 온칩 중복성의 이중 활용으로 성능, 에너지 효율, 신뢰성 동시에 향상
- 향후 DRAM 스케일링에 대비한 강건한 ECC 솔루션 제시
- 다양한 시스템 구성에서의广泛的한 적용 가능성 확인

## 주요 결과

- 기존 DRAM 설계에 대한显著な 변경 없이 DUO 구현 가능
- 온칩 중복성 및 IECC 포함 DRAM 벤더 가정
- 다양한 DRAM 구성(ECC/非ECC DIMM)에서의 적용 가능

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2018HPCA-summarize/duo-exposing-on-chip-redundancy-to-rank-level-ecc-for-high-reliability.md|전체 요약 보기]]
