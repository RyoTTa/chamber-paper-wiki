---
tags: [paper, 2018, 2018HPCA, topic/dram]
venue: "IEEE International Symposium on High Performance Computer Architecture (HPCA) 2018"
year: 2018
summary_path: "../paper-summaries/2018HPCA-summarize/eruca-efficient-dram-resource-utilization-and-resource-conflict-avoidance-for-memory-system-parallelism.md"
---

# ERUCA: Efficient DRAM Resource Utilization and Resource Conflict Avoidance for Memory System Parallelism

**Venue:** IEEE International Symposium on High Performance Computer Architecture (HPCA) 2018
**저자:** Sangkug Lym (UT Austin), Heonjae Ha (Stanford University), Yongkee Kwon (UT Austin), Chun-kai Chang (UT Austin), Jungrae Kim (Microsoft), Mattan Erez (UT Austin)

## 개요

- 메모리 시스템 성능은 접근 지연 시간과 대역폭으로 측정되며, DRAM 접근 병렬성이 이 모두에 중요한 영향
- 기존 연구는 물리적 뱅크를 세분화하여 유효 뱅크 수를 늘리는 데 중점
- 공유 리소스 충돌을 방지하지 않으면 세분화带来的 이점이 제한됨
- DRAM 채널 클록 주파수 지속적 스케일링으로 인한 추가 제약: 내부 프리페치 깊이 증가, 뱅크 그룹핑 기법 활용

## 방법론

### 3.1. Row Address Permutation (RAP)

- 서브뱅크 간 주소 국소성을 활용한 충돌 감소
- 메모리 접근 주소 로컬리티를 고려한 서브뱅크 간 공유 리소스 충돌 방지
- 물리적 주소 해싱 기법과의 통합을 통한 최적화

### 3.2. DRAM 칩 레벨 데이터 버스 개선

- 데이터 버스 효율성 향상을 통한 접근 병렬성 개선
- 뱅크 그룹 간 버스 경쟁 최소화
- 연속적인 동일 뱅크 그룹 접근 시 인트라그룹 버스 경쟁 해결

### 3.3. 주파수 확장 가능한 설계

- DRAM 채널 클록 주파수 지속적 스케일링 대응
- 내부 프리페치 깊이와의 조화를 통한 성능 최적화
- 다양한 DRAM 세대(DDR~DDR4)에서의 호환성 확보

## 핵심 기여

- ERUCA를 통해 DRAM 리소스 효율성과 접근 병렬성 동시 향상
- 거의 제로의 면적 오버헤드로 15% 성능 향상 달성
- 주소 국소성을 활용한 공유 리소스 충돌 방지 기법 제시
- 향후 DRAM 세대에서의 메모리 시스템 성능 최적화 기반 마련

## 주요 결과

- 상업용 DRAM 칩에서 활용 가능한 저utilized 리소스 활용
- 거의 제로의 면적 오버헤드(<0.3%) 달성
- 메모리 컨트롤러와의 통합을 통한 시스템 레벨 최적화

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]


## 전체 요약

[[../paper-summaries/2018HPCA-summarize/eruca-efficient-dram-resource-utilization-and-resource-conflict-avoidance-for-memory-system-parallelism.md|전체 요약 보기]]
