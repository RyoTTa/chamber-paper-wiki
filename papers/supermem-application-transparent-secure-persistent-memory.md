---
tags: [paper, 2019, 2019MICRO, topic/cache, topic/dram, topic/nvm, topic/security, topic/storage]
venue: "IEEE/ACM International Symposium on Microarchitecture (MICRO) 2019"
year: 2019
summary_path: "../paper-summaries/2019MICRO-summarize/supermem-enabling-application-transparent-secure-persistent-memory-with-low-overheads.md"
---

# SuperMem: Enabling Application-transparent Secure Persistent Memory with Low Overheads

**Venue:** IEEE/ACM International Symposium on Microarchitecture (MICRO) 2019
**저자:** Pengfei Zuo (Huazhong University of Science and Technology, UC Santa Barbara), Yu Hua* (Huazhong University of Science and Technology), Yuan Xie (UC Santa Barbara)

## 개요

- NVM(PCM, ReRAM, STT-RAM, 3D XPoint)은 차세대 메인 메모리로 주목받으나 **데이터 지속성(persistence)**과 **보안(security)** 두 가지 근본적 문제를 동시에 해결해야 함
- **Crash consistency 문제:** NVM 시스템에 CPU cache, DRAM 같은 volatile 저장소가 존재 → 시스템 장애 시 부분 업데이트로 데이터 불일치 발생. modern CPU/memory controller의 write reorder로 인해 crash inconsistency 악화
- **Security 문제 (Data remanence vulnerability):** NVM은 전원 차단 후에도 데이터 유지 → DIMM 탈취 시 데이터 유출 가능. DRAM은 volatility로 인해 도난 시 데이터 소멸되나, NVM에서는 악용 가능
- **Counter mode encryption의 persistence gap (핵심 갭):**
  - 보안 NVM에서 데이터 write 시 **2개의 write 요청** 발생: 데이터(1) + 카운터(1)
  - 시스템 장애 시 데이터와 카운터가 원자적으로 영속화되지 않으면 복구 불가
  - **Case A:** 카운터만 persisted → 데이터 복호화 불가 (올바른 카운터 없음)
  - **Case B:** 데이터만 persisted → 카운터 없이 복호화 불가
  - 기존 write-back counter cache + battery backup 방식: 배터리 비용이 크고 counter cache가 수백 KB~MB 규모
  - **SCA (Selective Counter Atomicity):** 언어 수준의 CounterAtomic 변수, counter_cache_writeback() 함수 필요 → **application 비투명 (software 변경 필수)**
  - 결과: unencrypted NVM용으로 작성된 애플리케이션이 encrypted NVM에서 직접 실행 불가

**Table 1 (논문 내) - Durable transaction의 recoverability 분석:**
| Stage | Log Content | Log Counter | Data Content | Data Counter | Recoverable? |
|-------|-------------|-------------|--------------|--------------|--------------|
| Prepare | Wrong | Wrong | Correct | Correct | Yes |
| Mutate | Correct | Unknown | Wrong | Wrong | No |
| Commit | Correct | Unknown | Correct | Unknown | No |

## 방법론

### 3.1. Write-through Counter Cache + Register

- **Baseline write-through counter cache 동작 (Figure 6):**
  1. CPU가 cache line A flush 요청 → Flu(A)
  2. Memory controller가 counter cache에서 카운터 읽기 → Read(Ac)
  3. 카운터 증가 → Ac++
  4. 증가된 카운터로 데이터 암호화 → Enc(A)
  5. **증가된 카운터를 write queue에 추가** → App(Ac) (write-through)
  6. 암호화된 데이터를 write queue에 추가 → App(A)
  7. Acknowledge 전송, flush 완료

- **문제:** Counter가 write queue에 먼저 추가된 후 데이터가 추가되기까지의 시간 간격에서 장애 발생 시 불일치 가능

- **Register 기반 해결 (Figure 7):**
  - AES 암호화 엔진에 레지스터 추가 (2 cache line 크기)
  - 카운터를 write queue에 바로 넣지 않고 레지스터에 저장 → Sto(Ac)
  - 데이터 암호화 후 암호화된 데이터도 레지스터에 저장 → Sto(A)
  - **둘 다 동시에 write queue에 추가** → App(Ac + A)
  - 결과: 데이터와 카운터가 write queue에 항상 동기화되어 존재 → crash consistency 보장
  - 레지스터 읽기/쓰기 비용은 무시 가능 (매우 작고 빠름)

### 3.2. Cross-bank Counter Storage (XBank)

- **기존 방식 (SingleBank, Figure 8a):**
  - 모든 카운터를 하나의 bank에 연속 저장
  - 데이터 write는 여러 bank에 분산 가능 (병렬) → 병렬 처리 가능
  - 그러나 카운터 write는 모두 하나의 bank로 집중 → **bank bottleneck**
  - 예: Data 0→Bank 0, Data 1→Bank 1, Data 2→Bank 2 → 병렬 처리 가능
  - Ctr 0, Ctr 1, Ctr 2 → 모두 Bank 7로 → 순차 처리 (병렬화 불가)

- **SameBank 방식 (Figure 8b):**
  - 각 카운터를 해당 데이터와 같은 bank에 저장
  - 동일 bank에서 데이터와 카운터가 동시에 write 대기 → bank 내부 병렬화 불가

- **XBank 방식 (Figure 8c):**
  - 데이터 bank ID를 offset하여 카운터를 다른 bank에 분산
  - **Bank 0에 저장된 Data 0의 카운터 → Bank 4에 저장**
  - **Bank 1에 저장된 Data 1의 카운터 → Bank 5에 저장**
  - 데이터와 카운터가 항상 서로 다른 bank에 → **동시 병렬 처리 가능**
  - 성능 향상: 최대 **2×** speedup

### 3.3. Counter Write Coalescing (CWC)

- Write queue 내에서 동일 memory line에 대한 카운터 write들을 병합
- **Spatial locality 활용:** 인접한 물리 주소를 가진 데이터의 카운터는 같은 memory line에 저장
  - 카운터는 보통 8 Byte (64비트 counter + 암호화 메타데이터)
  - Cache line = 64 Byte → 하나의 memory line에 8개의 카운터 저장 가능
  - 데이터가 같은 memory line 내에 있으면 카우터가 동일 memory line에 저장됨
- **동작:**
  - Write queue에 새로운 카운터 write가 들어올 때, 기존 entry와 같은 memory line인지 확인
  - 같으면 기존 entry의 해당 카운터 필드 업데이트 (새 write 무시)
  - 결과: write 요청 수 **최대 50% 감소**

### 3.4. 전체 시스템 아키텍처 (Figure 5)

```
CPU Cache (LLC) → Memory Controller → Encrypted NVM
                  ├─ AES-ctr engine + Register (2 cache lines)
                  ├─ Counter Cache (write-through)
                  └─ Write Queue + ADR
```

- 하드웨어 수정 범위: Memory Controller 내부 (AES 엔진, 카운터 캐시, write queue)
- **소프트웨어 변경 불필요** → Application transparent
- ADR (Asynchronous DRAM Refresh) 적용: write queue에 도달한 cache line은 durable로 간주

## 핵심 기여

- SuperMem은 **encrypted NVM에서 application-transparent하게 crash consistency를 보장**하는 최초의 하드웨어 기반 시스템
- Write-through counter cache + Register로 battery backup과 software 변경 없이 데이터-카운터 동기화 달성
- XBank + CWC 최적화로 write-through의 성능 오버헤드를 상쇄 → 이상적 보안 NVM과 동등한 성능
- 기존 unencrypted NVM용 애플리케이션이 encrypted NVM에서 **그대로 실행 가능** (portability 극대화)
- NVM의 practical deployment를 위한 보안+성능+휴리스틱리티 동시 해결의 모범 사례

## 주요 결과

- **시뮬레이터:** gem5 [6] + NVMain [33] 기반 구현
- **암호화 엔진:** AES-ctr (counter mode) 하드웨어 구현
- **카운터 캐시:** Write-through 정책, 수백 KB 규모
- **Write Queue:** ADR 적용, 카운터 + 데이터 동기화 관리
- 프로토타입 하드웨어 수정: Memory Controller 내부에 CWC, XBank 로직 추가

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/security.md|Security]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2019MICRO-summarize/supermem-enabling-application-transparent-secure-persistent-memory-with-low-overheads.md|전체 요약 보기]]
