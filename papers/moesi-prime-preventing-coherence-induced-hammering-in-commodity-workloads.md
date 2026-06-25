---
tags: [paper, 2022, 2022ISCA, topic/cache, topic/dram, topic/rowhammer]
venue: "ISCA 2022 (The 49th Annual International Symposium on Computer Architecture)"
year: 2022
summary_path: "../paper-summaries/2022ISCA-summarize/moesi-prime-preventing-coherence-induced-hammering-in-commodity-workloads.md"
---

# MOESI-prime: Preventing Coherence-Induced Hammering in Commodity Workloads

**Venue:** ISCA 2022 (The 49th Annual International Symposium on Computer Architecture)
**저자:** Kevin Loughlin (University of Michigan), Stefan Saroiu (Microsoft), Alec Wolman (Microsoft), Yatin A. Manerkar (University of Michigan), Baris Kasikci (University of Michigan)

## 개요

- Rowhammer는 DRAM 행(row)을 반복 활성화하여 인접 행의 비트를 뒤집는 보안/신뢰성 취약점으로, 기존 공격에서는 악의적으로 설계된 캐시 bypass 지령 시퀀스를 통해 DRAM에 빈번히 접근
- 최신 DRAM에서 MAC(Maximum Activate Count, 비트 플립 전 최대 활성화 횟수)이 점점 낮아지고 있어(RH 임계값 20,000 이하로 하락), Rowhammer에 대한 우려가 증가하고 있음
- **기존 연구의 한계:** 지금까지 알려진 모든 Rowhammer 공격은 악의적 코드에 의한 것이었으며, 정상 동작하는 상용 워크로드(commodity workloads)에서 Rowhammer를 유발하는 경우는 보고된 적이 없음
- 본 논문은 Intel의 cache coherent non-uniform memory access (ccNUMA) 프로토콜 구현으로 인해 **비악의적 상용 워크로드에서 최초로 Rowhammer가 발생**함을 발견 (coherence-induced hammering)
- 실험 결과: 메모리 접근 트레이스 분석에서 memcached는 64ms 내 21,917회, terasort는 39,031회 단일 행 활성화를 관찰하여 현재 MAC을 초과

## 방법론

### 3.1. Downgrade Writebacks (Source #1)
- MESI 프로토콜에서 dirty+read-only 상태(O)가 없어, 캐시 라인이 공유될 때 M→S 전환 시 writeback이 DRAM으로 발생
- ccNUMA 시스템에서 DRAM은 coherence 포인트 역할을 하므로, LLC 대신 DRAM으로 writeback이 전달됨
- 실험 검증: memcached의 경우 single-node 실행 시 최대 활성화 6,349회 → multi-node 실행 시 21,917회로 증가

### 3.2. Memory Directory Writes (Source #2)
- Intel의 메모리 디렉토리 프로토콜에서 원격 요청 시 DRAM의 디렉토리 비트를 업데이트하기 위한 쓰기가 빈번히 발생
- Migra 마이크로벤치마크에서 downgrade writeback을 제거했에도 불구하고 165,233회 활성화 관찰
- 디렉토리 캐시 HitME의 write-on-allocate 정책도 DRAM 쓰기에 기여

### 3.3. Speculative Reads (Source #3)
- 브로드캐스트 프로토콜에서 LLC miss 시 snoop과 parallel로 DRAM read를 수행하는 성능 최적화가 hammering 원인
- Migra(broad) 실험에서 write-based hammering은 제거되었으나 read-based hammering으로 421,360회 활성화 관찰
- 디렉토리 프로토콜에서도 디렉토리 캐시 미스 시 유사한 speculative read가 발생

## 핵심 기여

- **최초 발견:** 비악의적 상용 워크로드에서 발생하는 coherence-induced hammering을 최초로 발견
- **세 가지 원인:** Downgrade writebacks, 불필요한 메모리 디렉토리 쓰기, mis-speculated reads
- **MOESI-prime:** 7-안정 상태 프로토콜로 세 가지 hammering 소스를 모두 차단하면서도 성능/전력 영향 최소화
- **실용성:** Intel/AMD ccNUMA 시스템에 즉시 적용 가능하며, chiplet 아키텍처 확산으로 향후 더욱 중요해질 것으로 예상
- **기여:** Rowhammer 방어 프로토콜이 불필요한 DRAM 접근을 제거하여 오히려 성능/전력도 개선하는 동시 달성

## 주요 결과

### 4.1. 프로토콜 구조 (Section 4)
- **M' (Modified-prime):** M과 동일하나, 메모리 디렉토리 쓰기가 불필요함을 인식
- **O' (Owned-prime):** O와 동일하나, 메모리 디렉토리 쓰기가 불필요함을 인식
- **핵심 불변식 (Lemma 1):** M' 또는 O'에 진입한 후, 완료된 Put이 발생할 때까지 메모리 디렉토리 상태는 A (snoop-All)를 유지
  - 조건(1): M'/O' 진입 시 디렉토리 상태가 A
  - 조건(2): 디렉토리가 A인 동안 상태 변경 불가 (소유자가 Put만 가능)
  - 조건(3): 완료된 Put 후 모든 M'/O' 인스턴스 제거
- **Theorem 1:** MOESI-prime의 M'/O' 상태는 기존 MOESI의 M/O와 프로그램 관점에서 동일한 결과 보장

### 4.2. 디렉토리 캐시 수정 (Section 5.2)
- 기존 Intel 프로토콜: 로컬 노드가 소유자일 때 디렉토리 캐시 엔트리 할당 안 함 (Intel 특허)
- MOESI-prime: 로컬 소유자에게도 디렉토리 캐시 엔트리 할당 (로컬 노드를 가리키도록)
- 디렉토리 캐시 히트 = snoop 성공 보장 → 불필요한 DRAM read 차단

### 4.3. Greedy Local Ownership (Section 4.3)
- 소유권을 로컬 노드에 유지하면 디렉토리 캐시 엔트리가 유지되어 미스peculated reads 방지
- 원격 노드에서 요청 시에만 소유권 이전

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/rowhammer.md|RowHammer]]


## 전체 요약

[[../paper-summaries/2022ISCA-summarize/moesi-prime-preventing-coherence-induced-hammering-in-commodity-workloads.md|전체 요약 보기]]
