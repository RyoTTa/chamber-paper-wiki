---
tags: [paper, 2020, 2020ISCA, topic/cache, topic/dram, topic/nvm, topic/storage]
venue: "2020 ACM/IEEE 47th Annual International Symposium on Computer Architecture (ISCA 2020)"
year: 2020
summary_path: "../paper-summaries/2020ISCA-summarize/tvarak-software-managed-hardware-offload-for-redundancy-in-direct-access-nvm-storage.md"
---

# TVARAK: Software-Managed Hardware Offload for Redundancy in Direct-Access NVM Storage

**Venue:** 2020 ACM/IEEE 47th Annual International Symposium on Computer Architecture (ISCA 2020)
**저자:** Rajat Kateja, Nathan Beckmann, Gregory R. Ganger (Carnegie Mellon University)

## 개요

- NVM(Non-Volatile Memory)은 DRAM과 유사한 성능과 디스크와 같은 내구성을 제공하여 상태 유지 애플리케이션의 성능을 크게 향상시킴. Direct Access(DAX) 인터페이스를 통해 파일 시스템 오버헤드 없이 load/store 명령으로 직접 접근 가능.
- 프로덕션 스토리지 시스템은 디바이스 수준 ECC(미디어 에러 대응) 외에 시스템 수준 중복성(system-checksums + cross-device parity)을 통해 펌웨어 버그로 인한 데이터 손상을 보호. 그러나 DAX 환경에서 이러한 중복성 유지가 새로운 도전 과제로 부각.
- 펌웨어 버그의 두 가지 주요 카테고리: (1) Lost write bugs - 펌웨어가 쓰기 확인 후 실제 미디어를 업데이트하지 않음, (2) Misdirected read/write bugs - 잘못된 물리적 위치에서 읽기/쓰기 수행. 디바이스 수준 ECC는 이러한 버그를 탐지할 수 없음.
- 기존 솔루션의 한계: Nova-Fortis/Plexistore는 DAX 매핑 시 중복성 미유지; Mojim/HotPot/Pangolin은 소프트웨어 기반으로 높은 오버헤드(Redis set-only에서 50% 이상 성능 저하); Vilamb은 배치 지연으로 보호 윈도우 취약.
- DAX NVM에서 시스템 수준 중복성을 효율적으로 유지하면서도 모든 읽기/쓰기에 대한 검증을 제공하는 하드웨어 지원 솔루션 필요.

## 방법론

### 3.1. 아키텍처 구성

- **위치**: 각 LLC 뱅크 컨트롤러에 하나의 TVARAK 컨트롤러 배치.
- **구성 요소**: 주소 범위 비교기(Comperators), 체크섬/패리티 연산용 더하기(Adders), 온-컨트롤러 중복성 캐시(4KB).
- **LLC 파티션**: 중복성 캐시 정보용 2-way(전체 16-way 중), 데이터 diff 저장용 1-way.
- **캐시 일관성**: 컨트롤러 간 MESI 프로토콜로 중복성 캐시 라인 공유.
- **면적 오버헤드**: 온-컨트롤러 캐시가 주요 면적 차지. 2MB LLC 뱅크당 4KB 캐시 = LLC 대비 0.2% 면적.

### 3.2. DAX-CL-checksums 메커니즘

- **목적**: 페이지 수준 체크섬 검증의 읽기 확대 문제(64B 캐시 라인 읽기 위해 4KB 페이지 전체를 읽어야 함) 해결.
- **구현**: 캐시 라인 수준 체크섬(CRC-32C, 4바이트)을 별도 NVM 영역에 저장. 16개 캐시 라인 체크섬이 하나의 캐시 라인에 팩킹.
- **특성**: DAX 매핑된 데이터에 대해서만 임시로 유지. 언매핑 시 파일 시스템이 공간 회수. 디버그/복구 시에는 페이지 수준 시스템 체크섬 사용.
- **읽기 확대**: 65×(기존 naive) → 2×(DAX-CL-checksum 사용)로 감소.

### 3.3. 효율적 체크섬 및 패리티 업데이트

- **쓰기 시 처리**: LLC에서 NVM으로 캐시 라인 쓰기 시, TVARAK이 해당 DAX-CL-checksum, system-checksum, parity를 읽음 → 데이터 diff로 새 값을 계산 → 캐시된 중복성 정보 업데이트 → NVM에 쓰기.
- **데이터 diff 활용**: LLC의 더러워진 캐시 라인에서 diff를 계산하여 LLC 파티션에 저장. 향후 eviction 시 이 diff를 사용하여 NVM에서 이전 데이터 읽기 불필요.
- **전력 지원 가정**: 서버에 배터리 백업 전원이 장착되어 있어 캐시의 내구성(데이터 일관성) 보장. ADR(Applied Data Retention) 또는 랙 배터리 지원.

### 3.4. 읽기 검증 흐름

```
DAX 캐시 라인 읽기 시:
1. DAX-CL-checksum 주소 계산
2. 온-컨트롤러 캐시에서 조회 → LLC 중복성 파티션에서 조회 → NVM에서 읽기
3. 데이터 캐시 라인의 체크섬 계산
4. DAX-CL-checksum과 비교 검증
5. 검증 성공 시 데이터 전달, 실패 시 인터럽트 → OS 트랩 → 파일 시스템 복구
```

### 3.5. 쓰기 업데이트 흐름

```
DAX 캐시 라인 쓰기 시:
1. 시스템 체크섬, DAX-CL-checksum, 패리티 주소 계산 및 읽기 (캐시 히트 우선)
2. LLC 파티션에서 데이터 diff 조회
3. diff를 사용하여 새 시스템 체크섬, DAX-CL-checksum, 패리티 계산
4. 업데이트된 중복성 정보를 온-컨트롤러 캐시에 저장
5. 데이터 캐시 라인을 NVM에 쓰기
```

## 핵심 기여

- **TVARAK은 LLC 컨트롤러에 위치한 경량 하드웨어 오프로드를 통해 DAX NVM 스토리지의 시스템 수준 중복성을 효율적으로 유지**. 모든 읽기에 대한 체크섬 검증과 모든 쓰기에 대한 중복성 업데이트를 제공.
- **DAX-CL-checksums**: 캐시 라인 수준 체크섬으로 읽기 검증 오버헤드를 65×에서 2×로 대폭 감소. 임시적 특성으로 공간 오버헤드 최소화.
- **Redis set-only에서 3% 오버헤드**로 기존 최적 소프트웨어 솔루션(Pangolin 기반 50%) 대비 17배 성능 향상.
- **소프트웨어 전용 솔루션 대비 33-3900%까지 성능 우위** 달성 (애플리케이션/워크로드에 따라 차이).
- **NVM 스토리지가 프로덕션 환경에서 주요 저장소로 사용되기 위한 필수적인 펌웨어 버그 복원력 mechanisms을 하드웨어 수준에서 제공**하는 실용적 접근법 제시.

## 주요 결과

- **시뮬레이터**: zsim 기반, Intel Westmere 유사 프로세서 모델.
- **시스템 구성**: 12개 OOO 코어(2.27GHz), 32KB L1-D/I, 256KB L2, 24MB LLC(12 뱅크 × 2MB), 6 DDR DIMMs(DRAM), 4 NVM DIMMs(60ns 읽기, 150ns 쓰기).
- **애플리케이션**: Redis(PMDK 기반), PMDK의 C-Tree/B-Tree/RB-Tree, N-Store(YCSB 워크로드), fio(합성 벤치마크), Stream(메모리 대역폭 마이크로벤치마크).
- **소프트웨어 측**: 파일 시스템이 DAX 매핑 시 물리적 페이지 범위와 체크섬 페이지 정보를 TVARAK에 전달. 하드웨어는 LLC 쓰기 백업/읽기 시 자동으로 중복성 처리.

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2020ISCA-summarize/tvarak-software-managed-hardware-offload-for-redundancy-in-direct-access-nvm-storage.md|전체 요약 보기]]
