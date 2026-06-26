---
tags: [paper, 2018, 2018ASPLOS, topic/dram, topic/virtual-memory]
venue: "ASPLOS 2018 (Architectural Support for Programming Languages and Operating Systems)"
year: 2018
summary_path: "../paper-summaries/2018ASPLOS-summarize/making-huge-pages-actually-useful.md"
---

# Making Huge Pages Actually Useful

**Venue:** ASPLOS 2018 (Architectural Support for Programming Languages and Operating Systems)
**저자:** Ashish Panwar, Aravinda Prasad, K. Gopinath (Indian Institute of Science)

## 개요

- 현대 워크로드에서 주소 변환 오버헤드가 주요 성능 병목이 되고 있으며, TLB 용량 확장이 메모리 용량 증가를 따라가지 못함
- Huge pages는 페이지 테이블 조회를 줄여 CPU 시간을 최소화할 수 있지만, 연속 메모리 매핑 필요성으로 인해 단편화 문제 발생
- Linux 커널에서 huge pages 사용 시 높은 CPU 활용률, 지연시간 스파이크 등의 문제가 발생
- 가상화 시스템에서는 게스트와 호스트 OS 모두에서 불필요한 작업이 수행되어 문제 악화
- 데이터베이스 서버들은 huge pages를 비활성화한 상태로 출시되는 경우가 많아, 하드웨어 지원이 20년 가까이 되었음에도 제대로 활용되지 못함
- 기존 연구들은 단편화가 중요 문제가 아니며 메모리 컴팩션으로 효율적으로 처리할 수 있다고 주장하지만, 실제 장기 실행 시스템에서는 그렇지 않음

## 방법론

### 3.1. unmovable 페이지 추적 메커니즘

- Linux 커널에 소소한 변경을 통해 모든 unmovable 페이지를 명시적으로 추적
- 페이지 할당자에게 unmovable 페이지 클러스터링 정보 제공
- 메모리 컴팩션 서브시스템에게 LIU 마이그레이션 회피 정보 제공
- 가상화 환경에서도 효율적으로 작동하도록 설계

### 3.2. fragmentation via pollution 해결

- unmovable 페이지가 메모리 연속성을 불필요하게 오염시키는 문제 해결
- 페이지 할당자가 unmovable 페이지를 효율적으로 클러스터링하여 단편화 최소화
- huge pages 할당 시 불필요한 페이지 이동 제거

### 3.3. LIU 마이그레이션 회피

- huge pages 할당 시 불필요한 페이지 마이그레이션으로 인한 지연시간 문제 해결
- 컴팩션 과정에서 unmovable 페이지가 포함된 영역의 마이그레이션을 회피
- 컴팩션 비용을 최대 99%까지 감소

## 핵심 기여

- Linux 커널의 기존 메모리 관리 정책이 huge pages 관련 성능 이상의 근본 원인임을 규명
- Illuminator는 단편화를 효과적으로 완화하여 스트레스가 심한 조건에서도 huge pages의 이점을 애플리케이션이 활용할 수 있게 함
- 다양한 성능 지표에서 Linux를 크게 능가하는 성능 보여줌
- 실세계에서 흔히 경험되는 huge pages 관련 성능 이상을 해결하는 실용적인 접근법 제시

---

## 참고 자료

- 논문 원문: `/home/ryotta205/Chamber_paper/paper-source/2018ASPLOS/Making_Huge_Pages_Actually_Useful.pdf`
- 관련 개념: Huge Pages, Memory Management, Address Translation, Memory Compaction

## 주요 결과

- Linux 커널 기반 구현
- 페이지 할당자, 메모리 컴팩션 서브시스템 수정
- unmovable 페이지 추적을 위한 새로운 데이터 구조 추가
- 기존 Linux 커널과의 호환성 유지

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2018ASPLOS-summarize/making-huge-pages-actually-useful.md|전체 요약 보기]]
