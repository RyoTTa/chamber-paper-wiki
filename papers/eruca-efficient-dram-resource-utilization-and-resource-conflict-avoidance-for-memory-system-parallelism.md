---
tags: [paper, 2018, 2018HPCA, topic/dram]
venue: "HPCA 2018"
year: 2018
summary_path: "../paper-summaries/2018HPCA-summarize/eruca-efficient-dram-resource-utilization-and-resource-conflict-avoidance-for-memory-system-parallelism.md"
---

# ERUCA: Efficient DRAM Resource Utilization and Resource Conflict Avoidance for Memory System Parallelism

**Venue:** HPCA 2018
**저자:** Sangkug Lym (UT Austin), Heonjae Ha (Stanford University), Yongkee Kwon (UT Austin), Chun-kai Chang (UT Austin), Jungrae Kim (Microsoft), Mattan Erez (UT Austin)

## 개요

메모리 시스템 성능은 접근 지연 시간과 대역폭으로 측정되며, DRAM 접근 병렬성이 이 모두에 중요한 영향을 미칩니다. 기존 연구는 물리적 뱅크를 세분화하여 유효 뱅크 수를 늘리는 데 중점을 두었으나, 공유 리소스 충돌을 방지하지 않으면 세분화带来的 이점이 제한됩니다.

ERUCA는 효율적인 서브뱅킹 및 주파수 확장 가능한 DRAM 아키텍처로, 서브뱅크 간 주소 국소성을 활용한 공유 리소스 충돌 방지를 통해 거의 제로의 면적 오버헤드로 15% 성능 향상을 달성합니다.

## 방법론

### Row Address Permutation (RAP)
- 서브뱅크 간 주소 국소성을 활용한 충돌 감소
- 메모리 접근 주소 로컬리티를 고려한 서브뱅크 간 공유 리소스 충돌 방지
- 물리적 주소 해싱 기법과의 통합을 통한 최적화

### DRAM 칩 레벨 데이터 버스 개선
- 데이터 버스 효율성 향상을 통한 접근 병렬성 개선
- 뱅크 그룹 간 버스 경쟁 최소화
- 연속적인 동일 뱅크 그룹 접근 시 인트라그룹 버스 경쟁 해결

### 주파수 확장 가능한 설계
- DRAM 채널 클록 주파수 지속적 스케일링 대응
- 내부 프리페치 깊이와의 조화를 통한 성능 최적화
- 다양한 DRAM 세대(DDR~DDR4)에서의 호환성 확보

## 핵심 기여

1. DRAM 리소스 효율성과 접근 병렬성을 동시에 향상시키는 ERUCA 제안
2. 거의 제로의 면적 오버헤드로 15% 성능 향상 달성
3. 주소 국소성을 활용한 공유 리소스 충돌 방지 기법 제시

## 주요 결과

- **성능 향상**: 전체적으로 15% 성능 향상 달성
- **면적 오버헤드**: <0.3% DRAM 다이 면적 오버헤드 발생
- **일관성**: 다양한 워크로드에서 일관된 성능 개선 확인

## 한계점

- 특정 DRAM 구성에서의 평가로 다른 구성에서의 일반화 필요
- 다양한 워크로드에서의 추가 검증 필요
- 실제 상용 시스템에서의 실증 평가 필요

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]

## 관련 논문

- [paper-summaries/2018HPCA-summarize/eruca-efficient-dram-resource-utilization-and-resource-conflict-avoidance-for-memory-system-parallelism.md]