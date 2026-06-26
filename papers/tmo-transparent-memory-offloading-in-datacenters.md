---
tags: [paper, 2022, 2022ASPLOS, topic/dram, topic/memory-tiering, topic/nvm, topic/storage]
venue: "ACM SIGPLAN International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS) 2022"
year: 2022
summary_path: "../paper-summaries/2022ASPLOS-summarize/tmo-transparent-memory-offloading-in-datacenters.md"
---

# TMO: Transparent Memory Offloading in Datacenters

**Venue:** ACM SIGPLAN International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS) 2022
**저자:** Johannes Weiner, Niket Agarwal, Dan Schatzberg, Leon Yang, Hao Wang, Blaise Sanouillet, Bikash Sharma, Tejun Heo, Mayank Jain, Chunqiang Tang, Dimitrios Skarlatos (Meta Inc. / Carnegie Mellon University)

## 개요

- 데이터센터 애플리케이션의 메모리 수요가 지속적으로 증가하는 반면, DRAM은 서버 비용의 33%에 달할 정도로 인프라 비용의 핵심 부담요소로 부상
- NVMe SSD는 DRAM 대비 동일 용량 기준 **10배 이상 저렴**하고 전력 소비도 현저히 낮아 대체 메모리 기술로 주목받고 있으나, 하드웨어 이질성 (SSD 세대별 읽기/쓰기 지연시간 470μs~9.3ms)과 다양한 워크로드의 메모리 접근 패턴 차이로 인해 투명한 오프로딩이 어려움
- Google의 g-swap은 단일 느린 메모리 계층 (압축 메모리)만 지원하고 오프라인 프로파일링에 의존하며, 고정된 promotion rate 기반으로 동작하여 이질적인 하드웨어 환경에서 최적의 메모리 절약을 달성하지 못함
- 데이터센터에서 메모리의 **약 35%가 cold memory**로 존재 (19%~62% 범위),\application 별로 냉각 비율이 크게 다르며, 마이크로서비스 아키텍처에서는 라우팅, 프록시, 로깅 등 인프라 계층이 서버 메모리의 **약 20%**를 차지 (datacenter tax 13% + microservice tax 7%)

## 방법론

### 3.1. PSI (Pressure Stall Information)

- non-idle 프로세스의 compute potential (CPU 수로 capped된 non-idle 프로세스 수) 대비 자원 부족으로 인한 비생산적 시간의 비율을 측정
- **some metric**: 도메인 내 최소 1개 프로세스가 리소스 대기로 stalling된 시간 비율 → 개인 프로세스에 대한 지연 시간 효과 포착
- **full metric**: 도메인 내 모든 프로세스가 동시에 지연된 시간 비율 → 완전한 생산성 손실 포착
- 메모리 리소스의 경우: (1) 메모리 가득 참으로 새 페이지 할당 시 reclaim 발생, (2) 최근 파일 캐시에서 evict된 페이지의 refault (major fault), (3) swap 장치에서 페이지 읽기 대기의 3가지 상황에서 stalling 시간을 기록
- 기존 metrics (RSS, promotion rate)의 한계를 극복: RSS는 메모리 부족이 성능에 미치는 영향을 측정 불가, promotion rate는 오프로딩 백엔드의 성능 특성을 고려하지 못하고 메모리 가용 증가에 따른 성능 향상도 포착 불가
- 마이크로초 해상도의 실시간 집계와 running averages (10s, 1m, 5m) 제공 → 리소스 관리에 활용

### 3.2. Senpai 사용자 공간 에이전트

- 매 6초마다 각 cgroup에 대해 다음 공식으로 회수할 메모리 양을 계산: `reclaim_mem = current_mem × reclaim_ratio × max(0, 1 − PSI_some / PSI_threshold)`
- PSI_some이 PSI_threshold에 접근하면 점진적으로 회수량을 감소시켜 mild steady-state memory pressure 유지
- 기존 cgroup memory limit 조정 방식의 문제점 해결을 위해 stateless `memory.reclaim` 커널 제어 파일 추가 → 확장 중인 워크로드 블로킹 위험 방지
- 생산 환경 전역 설정: `reclaim_ratio = 0.0005`, `PSI_threshold = 0.1%`, 회수 주기 6초, 최대 회수량은 워크로드 크기의 1%
- IO PSI도 함께 모니터링: 메모리 PSI만으로는 부족한 경우 (저장 장치 포화 등)를 대비
- 사용자 공간 구현의 장점: 부동 소수점 연산 가능, 릴리스 사이클이 커널보다 빠름, 다양한 설정值 반복 실험 용이

### 3.3. 커널 최적화: 균형 잡힌 오프로딩

- 기존 커널은 파일 캐시 reclaim를 강하게 선호하는 휴리스틱으로 swap을 긴급 오버플로우로만 활용 → 파일 캐시 working set이 완전히 소진될 때까지 swap 오프로딩 미수행
- **비resident 캐시 추적 (refault detection)**: 파일 캐시 페이지 evict 시 shadow entry에 현재 페이지 fault 카운터 저장 → 재 fault 시 reuse distance 계산 → reuse distance < resident 메모리 크기이면 refault로 판정
- 파일 캐시에서 refault가 발생하기 전까지는 파일 캐시만 회수, refault가 발생하면 파일 캐시 회수 속도와 swap-in 속도를 균형 있게 조절
- 이 접근으로 파일 캐시와 익명 메모리의 오프로딩이 균형을 이루고 aggregate paging 양을 최소화
- 커널 수정 사항은 Linux에 upstream 완료

### 3.4. 투명한 zswap 지원

- zswap: 압축된 형태로 RAM에 저장하는 익명 메모리 오프로딩 메커니즘, block device I/O 없이 디코прессion으로 복원
- 백엔드 성능 차이를 자동으로 적응:更快な zswap/SSD 백엔드 사용 시 더 많은 페이지 오프로딩 가능 (낮은 per-page latency)
- zstd 압축 알고리즘과 Zsmalloc 할당 채택 (실험 기반 선택: 좋은 압축률 + 낮은 오버헤드)

## 핵심 기여

- **핵심 기여 1**: PSI를 통해 메모리 부족으로 인한 실제 작업 손실을 실시간 측정하는 최초의 솔루션 → 기존 fragile한 low-level metrics (promotion rate, major fault)를 대체
- **핵심 기여 2**: Senpai가 사전 프로파일링 없이 diverse 워크로드와 이질적 하드웨어에 대응하는 자동화된 메모리 오프로딩 달성
- **핵심 기여 3**: 메모리 오프로딩을 긴급 오버플로우가 아닌 subliminal pressure 레벨로 전환 → 파일 캐시와 균형 잡힌 turnover
- **핵심 기여 4**: 수백만 서버에서 1년 이상 프로덕션 배포 경험 보고 → **20~32% 메모리 절약** 달성
- **핵심 기여 5**: PSI를 Linux kernel에 upstream, Senpai를 open source로 공개하여 재사용성 확보
- **의의**: DRAM 비용 증가 문제에 대한 실용적인 시스템 수준 솔루션을 대규모 프로덕션에서 검증, 향후 NVM/CXL 디바이스와의 통합을 위한 기반 마련

## 주요 결과

- **커널**: Linux kernel에 PSI와 `memory.reclaim` cgroup 인터페이스 upstream 완료
- **Senpai**: 사용자 공간 에이전트로 open source 공개 (GitHub)
- **압축 알고리즘**: zstd 채택 (lzo, lz4, zstd 비교 실험)
- **메모리 풀 할당자**: Zsmalloc 채택 (Z3fold, Zbud, Zsmalloc 비교 실험)
- **커널 reclaim 알고리즘 수정**: 비resident 캐시 추적 및 파일 캐시/swap 균형 회수 로직 추가 → upstream 완료
- **Senpai 동작 주기**: 6초 간격, 최대 1% 메모리 회수/주기, extreme contraction 대응 시간은 수 분
- Memcached의 reclaim은 커널의 0.05% CPU 사이클만 사용 (negligible)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2022ASPLOS-summarize/tmo-transparent-memory-offloading-in-datacenters.md|전체 요약 보기]]
