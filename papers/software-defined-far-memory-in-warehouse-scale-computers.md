---
tags: [paper, 2019, 2019ASPLOS, topic/compression, topic/dram, topic/memory-tiering, topic/nvm]
venue: "ASPLOS 2019"
year: 2019
summary_path: "../paper-summaries/2019ASPLOS-summarize/software-defined-far-memory-in-warehouse-scale-computers.md"
---

# Software-Defined Far Memory in Warehouse-Scale Computers

**Venue:** ASPLOS 2019
**저자:** Andres Lagar-Cavilla, Junwhan Ahn, Suleiman Souhlal, Neha Agarwal, Radoslaw Burny, Shakeel Butt, Jichuan Chang, Ashwin Chaugule, Nan Deng, Junaid Shahid, Greg Thelen, Kamil Adam Yurtsever, Yu Zhao, Parthasarathy Ranganathan (Google)

## 개요

- DRAM 비용 절감이 Warehouse-Scale Computer (WSC)의 Total Cost of Ownership (TCO) 개선에 핵심이나, Moore's law 종료로 DRAM GB당 비용 절감이 정체되고 동시에 인메모리 컴퓨팅 확산으로 DRAM 수요가 폭발적으로 증가
- 기존의 물리적 far memory (NVM, remote memory)는 고정된 크기로 provisioning하여 자원 낭비(stranding) 발생 가능. NVM은 수백 ns~수십 µs 지연시간, 원격 메모리는 클러스터 규모에 따라 수~수십 µs
- Google WSC에서 cold memory 비율은 클러스터별 **1%~61%**, 동일 클러스터 내에서도 시간대별 **1%~52%**로 변동. 고정 far memory는 이러한 변동에 대응 불가
- WSC 애플리케이션은 수백~수천 개로 다양(per-application tuning 불가), 최소 수%의 성능 저하도 TCO 절감분 상쇄 가능 (SLA 위반 + provisioning 증가)

## 방법론

### 3.1. Cold Page Identification Mechanism

- Memory page의 마지막 접근 시점으로부터 **T초** 동안 미접근 시 cold로 분류
- Google WSC 측정 결과: T=120s에서 평균 **32%** cold memory, **15%**의 cold memory가 매분 재접근 (promotion rate)
- T를 줄이면 cold page 증가 but 성능 저하 위험, T를 늘리면 far memory 활용도 감소
- **Optimal T 탐색**이 자동화 필요 → ML autotuning으로 해결

### 3.2. Kernel-Level Implementation (zswap 기반)

- Linux zswap 프레임워크를 far memory 계층으로 활용
- Cold page를 **single-digit µs** (6µs) 지연시간으로 압축 저장
- 압축 비율: 실제 workloads에서 평균 **20%**의 데이터를 far memory로 전환 가능
- Proactive eviction: 사용자 space에서 주기적으로 access bit을 스캔하여 cold page 식별
- Reactive eviction 대비 동일 메모리 확보량에서 **성능 저하 50% 감소** (실험 결과)

### 3.3. Node Agent & Control Plane

- 각 노드에서 동작하는 **node agent**가 kernel 메커니즘의 aggressiveness를 제어
- 애플리케이션 동작에 따라 실시간으로 파라미터 조정
- SLO 위반 감지 시 자동으로 eviction 속도 감소

### 3.4. ML-Based Autotuning System

- **Fast far memory model**: WSC 전체의 far memory 동작을 시뮬레이션하는 저비용 모델
- **GP Bandit**: design space 탐색을 통해 최적 configuration 자동 탐색
- 클러스터별, 시간대별 변화에 ** אדם 개입 없이 적응**
- Heuristic 기반 대비 효율성 **30% 향상**

## 핵심 기여

- **핵심 Contribution**: 소프트웨어 정의 far memory를 통해 하드웨어 추가 없이 DRAM TCO 절감 달성 — Google WSC에 2016년부터 실배포
- **TCO 절감**: memory 비용 **67% 이상 절감** (far memory 영역), 전체 TCO **4~5% 절감**
- **성능**: 6µs tail latency로 애플리케이션 영향 최소화, 수천 개 서비스에서 무시 가능한 성능 저하
- **유연성**: 고정 하드웨어 provisioning 없이 소프트웨어로 far memory 비율을 실시간 조정 — cold memory 변동(1%~61%)에 유연하게 대응
- **의의**: DRAM 비용 절감의 새로운 패러다임 제시 — 하드웨어 far memory의 한계(고정 크기, provisioning 오버헤드)를 소프트웨어로 극복, fleet-wide ML 자동 최적화로 운영 부담 제거

## 주요 결과

- **OS**: Linux 커널 zswap 프레임워크 수정
- **구현 언어**: C (커널), Python (node agent, autotuning)
- **구성 요소**: kernel page scanner, zswap compressor, node agent, fleet-wide autotuner
- **Scale**: Google WSC 전체에 2016년부터 배포, 수천 개 production service 지원

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/compression.md|Compression]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]


## 전체 요약

[[../paper-summaries/2019ASPLOS-summarize/software-defined-far-memory-in-warehouse-scale-computers.md|전체 요약 보기]]
