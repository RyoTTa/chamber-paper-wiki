---
tags: [storage, ssd, full-system-simulation, gem5, flash-memory, ftl]
venue: MICRO
year: 2018
summary_path: paper-summaries/2018MICRO-summarize/amber-enabling-precise-full-system-simulation-with-detailed-modeling-of-all-ssd-resources.md
---

# Amber*: Enabling Precise Full-System Simulation with Detailed Modeling of All SSD Resources

**Venue:** 51st Annual IEEE/ACM International Symposium on Microarchitecture (MICRO '18)
**저자:** Donghyun Gouk, Miryeong Kwon, Jie Zhang, Sungjoon Koh, Wonil Choi, Nam Sung Kim, Mahmut Kandemir, Myoungsoo Jung (Yonsei University, Pennsylvania State University, University of Illinois Urbana-Champaign)

---

## 개요

풀시스템 시뮬레이션 환경에서 SSD의 모든 하드웨어/소프트웨어 리소스를 정밀 모델링하는 Amber(SimpleSSD 2.0) 프레임워크를 제안. gem5와 통합하여 SATA, UFS, NVMe, OCSSD 등 다양한 스토리지 인터페이스와 완전한 펌웨어 스택(FTL, ICL, HIL)을 에뮬레이션.

## 방법론

- **SSD 연산 컴플렉스 모델링:** 내장 CPU 코어, DRAM, 메모리 컨트롤러를 포함한 SSD 내부 하드웨어 모델링
- **완전한 펌웨어 스택:** FIL(Flash Interface Layer), FTL(Flash Translation Layer), ICL(Internal Caching Layer)의 완전한 구현
- **다양한 인터페이스 지원:** SATA, UFS, NVMe, OCSSD 1.2/2.0 프로토콜 에뮬레이션
- **데이터 전송 에뮬레이션:** gem5의 호스트 DMA 엔진과 시스템 버스 수정으로 실제 데이터 흐름 시뮬레이션
- **재구성 가능한 소프트웨어 모듈:** ICL의 캐시 구조, FTL의 매핑 알고리즘 등 다양한 구성 지원

## 핵심 기여

- 풀시스템 시뮬레이션에서 SSD의 모든 리소스를 정밀 모델링하는 최초의 프레임워크
- 다양한 스토리지 인터페이스(SATA, UFS, NVMe, OCSSD)를 아우르는 통합 시뮬레이션 환경
- gem5와의 통합으로 모바일/범용 컴퓨팅 플랫폼에서의 SSD 영향 분석 가능

## 주요 결과

- 실제 SSD 동작을 정확히 캡처하는 풀시스템 시뮬레이션 달성
- MQSim 대비 약간 더 빠른 시뮬레이션 속도로 풀시스템 특성 모델링
- Active Storage vs Passive Storage 아키텍처 비교 분석 가능
- 다양한 워크로드에서 커널 CPU 활용률, DRAM 사용량, 시스템 성능을 정확히 모델링

## 한계점

- 시뮬레이션 속도가 실제 SSD 하드웨어 시뮬레이션 대비 느릴 수 있음
- 모든 SSD 유형의 펌웨어를 완전히 모델링하지 못할 수 있음 (특정 벤더 최적화)
- gem5 기반의 제한된 플랫폼 지원 (x86, ARM)

## 관련 개념

- [[paper-wiki/concepts/storage.md|Storage]]

## 전체 요약

[amber-enabling-precise-full-system-simulation-with-detailed-modeling-of-all-ssd-resources.md](../../paper-summaries/2018MICRO-summarize/amber-enabling-precise-full-system-simulation-with-detailed-modeling-of-all-ssd-resources.md)
