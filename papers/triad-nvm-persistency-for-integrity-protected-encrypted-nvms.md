---
tags: [paper, 2019, 2019ISCA, topic/dram, topic/nvm, topic/security]
venue: "The 46th Annual International Symposium on Computer Architecture (ISCA '19)"
year: 2019
summary_path: "../paper-summaries/2019ISCA-summarize/triad-nvm-persistency-for-integrity-protected-and-encrypted-non-volatile-memories.md"
---

# Triad-NVM: Persistency for Integrity-Protected and Encrypted Non-Volatile Memories

**Venue:** The 46th Annual International Symposium on Computer Architecture (ISCA '19)
**저자:** Amro Awad, Mao Ye, Yan Solihin, Laurent Njilla, Kazi Abu Zubair (University of Central Florida, Air Force Research Laboratory)

## 개요

- 비휘발성 주 메모리(NVMM, Non-Volatile Main Memory)는 DRAM 대비 높은 용량, 낮은 비트당 비용, 바이트 주소 가능성, 그리고 비휘발성을 제공하지만, 전원이 꺼진 후에도 데이터가 잔류(data remanence)하여 보안 취약점을 노출
- Intel Optane DC Persistent Memory는 메모리 측 암호화(memory-side encryption)를 제공하지만, 프로세서 측 메모리 보안(processor-side memory security)에 비해 보호가 약함 (시스템 버스에서 평문 전송, 애플리케이션에 대한 안전한 실행 환경 미제공)
- 기존 연구(예: Liu et al. [18])는 데이터와 카운터의 원자적 영속화에 초점을 맞추었으나, **MAC(Message Authentication Code)와 Bonsai Merkle Tree(BMT)의 영속화를 무시**하여 카운터 리플레이 공격(counter replay attack) 및 데이터 변조에 취약
- 엄격한 보안 메타데이터 영속화(strict persistence) 시 워크로드에 따라 최대 **9.4× 성능 저하** 발생 (Figure 4)
- 6TB NVMM 시스템에서 비영속 영역 복구에 **5,154초(약 85.9분)** 소요 — 실용적이지 않음

## 방법론

### 3.1. 보안 영속성의 요구사항 분석

- **기밀성 및 무결성 보존:** 카운터 모드 메모리 암호화(counter-mode encryption)에서 MAC과 BMT가 반드시 유지되어야 함
  - BMT 루트는 프로세서 칩 내부에 영구 보관
  - 카운터 값이 재사용되어서는 안 됨 (AES 일회용 패드 생성에 사용)
- **데이터 복원 가능性的:** 영속 영역의 데이터는 크래시/재부팅 후 복원 가능해야 하며, 이를 위해 데이터와 모든 보안 메타데이터(카운터, MAC, BMT)가 함께 영속화되어야 함
- **빠른 영속화 및 복구:** 영속화가 정상 실행 속도를 크게 저해해서는 안 되며, 크래시 후 복구 시간이 합리적이어야 함

### 3.2. 영속/비영속 영역 분리 (Figure 5, 6)

- NVMM을 영속 영역(파일 시스템, PMDK 사용 가능)과 비영속 영역(일반 메모리)으로 분리
- 각 영역별로 별도의 암호화 카운터, MAC 할당
- BMT 분리 전략 두 가지:
  1. **단일 BMT + 서브트리 분할:** 메모리 공간 비율이 0:8, 1:7, ..., 8:0 중 하나여야 하며, 각 루트 MAC이 영속 또는 비영속 데이터만 커버
  2. **완전 분리 BMT (채택):** 영속/비영속 영역용 별도 BMT와 루트를 가지며, 영속 영역 BMT는 해당 영역 내에 저장
- 영속 영역의 BMT 업데이트는 루트까지 즉시 반영, 비영속 영역은 캐시에서 지연 쓰기(lazy write-back) 가능

### 3.3. 암호화 카운터 영속화 완화 (Relaxation)

- **영속 영역:** 카운터가 업데이트될 때 즉시 NVM에 기록 (WPQ를 통한 원자적 영속화)
- **비영속 영역:** 카운터 재사용 방지를 위해 세션 카운터(session counter) 활용
  - 매 재부팅 시 세션 카운터 증가 → 같은 키를 사용하더라도 카운터 재사용 방지
  - 세션 0은 영속 데이터용, 비영속 데이터는 비영속 세션 사용
- 영속 키(Persistent Key)와 영구 키(Volatile Key) 분리 방식 대신 세션 카운터 방식을 채택 (BMT 루트 사전 계산 가능)

### 3.4. BMT 영속화 수준 조정 (Persist Level)

- **TriadNVM-N:** 영속 영역에 대해 Merkle Tree의 N번째 레벨까지 엄격한 영속화 보장
  - TriadNVM-1: 카운터 블록의 부모 노드만 영속화
  - TriadNVM-2: 부모 + 조부모 노드 영속화
  - TriadNVM-3: 더 상위 레벨까지 영속화
- 레벨이 높을수록 복구 시간은 단축되지만 쓰기 오버헤드 증가
- 비영속 영역의 BMT 중간 노드는 캐시에서 지연 업데이트

### 3.5. 비영속 영역 크래시 복구 — Lazy Recovery

- 6TB NVMM, 50% 비영속 영역에서 전체 메타데이터 재구성 시 **5,154초** 소요
- **Lazy Recovery 메커니즘:**
  - 레벨 1(카운터 블록의 부모)의 중간 노드를 제로로 초기화하고, 상위 레벨을 순차적으로 구성하여 초기 루트 값 생성
  - 첫 번째 쓰기 발생 시 부모 노드의 해당 MAC 위치(8B)가 0이면 초기화된 값으로 간주하고 카운터를 제로로 설정, 부모 노드 업데이트
  - 자연 발생적 64비트 제로 MAC 확률(1/2^64)을 대비하여, MAC이 0인 카운터 블록은 마이너 카운터 증가 후 재암호화
  - 결과: 레벨 1~2만 순회하면 복구 완료

### 3.6. 전체 쓰기 동작 (Figure 7)

- **Write-Pending Queue(WWPQ)**가 영속 영역(perersistence domain)의 일부로 포함
- 쓰기 동작 단계:
  1. 영속 레지스터에 업데이트 로깅 (카운터, 데이터, MT 노드, 루트)
  2. READY_BIT 설정 → 크래시 시 영속 레지스터에서 WPQ로 재전송 가능
  3. 영속 영역: 카운터 즉시 WPQ로 복사, BMT persist level 이상의 중간 노드 즉시 영속화
  4. 비영속 영역: 캐시에서 지연 업데이트, eviction 시 WPQ로 전송
- 영속 레지스터 수: TriadNVM-2는 5개, TriadNVM-3는 9개 필요

## 핵심 기여

- **보안 영속성(Secure Persistency)의 체계적 분석:** 메모리 암호화·무결성 검증 시스템에서 영속화의 첫 번째 포괄적 연구
- Triad-NVM은 strict persistence 대비 **약 2× 처리량 향상**, 8TB NVMM에서 **4초 미만 복구** (비영속 미영속화 대비 **3,648×** 빠름)
- 영속/비영속 영역의 차별적 보안 메타데이터 처리가 핵심: 이를 무시하면 성능 또는 보안 저하
- BMT와 MAC 영속화가 카운터 영속화보다 더 큰 영속화 오버헤드를 유발 → 기존 연구의 영속화 비용 과소 평가
- Triad-NVM은 애플리케이션/라이브러리 수정 불필요 (PMDK 등 기존 영속화 모델과 호환 가능)

## 주요 결과

- **시뮬레이터:** Gem5 전체 시스템(full-system) 모드
- **커널:** Linux 4.14 기반, Ubuntu 16.04 디스크 이미지
- **설정:** `memmap=4G!12G` 파라미터로 12GB~16GB 주소 범위를 4GB 영속 영역으로 할당
- **영속 파일 시스템:** DAX 지원 ext4 파일 시스템
- **영속 라이브러리:** Intel PMDK
- **프로세서:** 8코어, 1GHz, 순차 실행(out-of-order) x86-64
- **캐시:** L1 32KB(2-way), L2 512KB(8-way), L3 8MB(64-way)
- **NVM:** 16GB PCM (읽기 60ns, 쓰기 150ns), 2 ranked/channel, 8 bank/rank
- **보안 메타데이터 캐시:** 카운터 캐시 128KB, BMT 캐시 128KB, BMT 9레벨 8-ary

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/security.md|Security]]


## 전체 요약

[[../paper-summaries/2019ISCA-summarize/triad-nvm-persistency-for-integrity-protected-and-encrypted-non-volatile-memories.md|전체 요약 보기]]
