---
tags: [paper, 2023, 2023ASPLOS, topic/cache]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023ASPLOS-summarize/flame-a-centralized-cache-controller-for-serverless-computing.md"
---

# Flame: A Centralized Cache Controller for Serverless Computing

**Venue:** 
**저자:** 

## 개요

Serverless computing의 stateless 실행 모델은 coldstart 문제를 야기한다. 함수 컨테이너를 처음부터 초기화하는 coldstart latency는 함수 실행 시간보다 수 배에서 수십 배 높을 수 있다. 이를 해결하기 위한 **function caching** (완료된 함수를 메모리에 keep-alive)은 warmstart로 coldstart를 거의 제거할 수 있지만(컨테이너 복구 < 0.5 ms), 캐시된 인스턴스가 물리 서버 리소스를 지속적으로 소비한다.

실제 클라우드 환경(Huawei Cloud)에서는 coldstart ratio < 1%를 달성하기 위해 서버리스 클러스터 메모리의 **20% 이상**을 함수 캐싱에 소비한다. 기존 서버리스 플랫폼은 각 서버에 **local cache controller**를 두어 TTL 기반 또는 priority 기반 keep-alive 정책을 적용하지만, 이 "local cache control" 방식은 다음 근본적 한계를 갖는다:

**Observation #1 — Hotspot contention:** Azure function trace에서 90%의 호출이 10%의 hotspot 함수에서 발생. Consistent hashing 등의 로드밸런싱으로 인해 hotspot 함수가 특정 서버에 집중 → 서버 간 coldstart ratio 최대 **100×** 차이 발생 (4.7% vs 0.04%).

**Observation #2 — Cache redundancy:** Local controller가 독립적으로 캐시 결정 → 동일 함수가 여러 서버에 중복 캐시. Top-20 hotspot 함수가 호출의 95%를 차지하지만 메모리 사용량의 20%만 소비. **75% 이상의 캐시 리소스**가 non-hotspot 함수 캐싱에 낭비. Non-hotspot 인스턴스의 리소스 활용률은 10-30%.

**Observation #3 — Load-balancing dilemma:** Round-robin은 hotspot contention을 제거하지만 cache locality를 위반해 3× 이상의 캐시 리소스 사용 증가. Consistent hashing은 locality를 보존하지만 skewness 증폭.

## 방법론

### 3.1 방법론

| 항목 | 상세 |
|------|------|
| **Testbed** | 8-server cluster, Intel Xeon Silver-4215 (32-core, 2.50 GHz), 256GB RAM/node, 10 Gbps Ethernet |
| **Framework** | OpenFaaS + Kubernetes (modified) |
| **Workloads** | Azure function traces에서 샘플링한 8개 trace (각 384 functions, 1주일 분량, 2.1M-24.7M requests) |
| **Benchmarks** | ServerlessBench [35] + FunctionBench [13], 22개 애플리케이션을 확장해 384 functions pool 구성 |
| **Baselines** | TTL-based keep-alive (OpenWhisk), FaasCache [8] (ASPLOS'21), CH-RLU [9] (HPDC'22), Icebreaker [26] (ASPLOS'22) |
| **Metrics** | Coldstart ratio, function latency (CDF), memory consumption, drop ratio |

### 3.2 주요 결과 (Hashing-based load balancing)

**Memory consumption:**
- FaasCache 대비: 평균 **36%** 감소 (최대 80%, trace F)
- CH-RLU 대비: 평균 **33%** 감소
- 절감분의 82% (13,385 TB·s)가 top-N hotspot 함수에서 발생

**Coldstart ratio:** FaasCache(1.83%), CH-RLU(5.34%), TTL(4.68%), Icebreaker(6.11%) 대비 Flame은 **0.86%**

**Warm invocation ratio:** Flame 99.1% > FaasCache(98.2%) > TTL(95.2%) > Icebreaker(94.2%) > CH-RLU(91.9%)

**Drop ratio:** Flame 0.02% — hotspot contention 38.7-81.4× 감소

**99th-percentile latency:** Flame이 가장 낮으며, TTL-based/Icebreaker 대비 **10× 이상** P99 latency 감소

### 3.3 Round-robin load balancing

Memory consumption: FaasCache 대비 **40%** 감소 (최대 71%). Coldstart ratio: TTL 대비 2.9×, Icebreaker 대비 2.7× 개선. Flame은 load-balancing 정책에 관계없이 일관된 성능.

### 3.4 Cache allocation dynamics (Figure 8a)

Workload burst (2-4h) 동안 Flame은 hotspot detection으로 oscillation 없이 대응하고, burst 종료 후 자동으로 over-provisioned 인스턴스 reclaim. FaasCache는 리소스가 허용하는 한 모든 함수를 캐싱해 메모리 고갈.

### 3.5 Sensitivity

**Cluster scale (4→32 servers, total memory 고정):** TTL/FaasCache/Icebreaker는 scale 증가 시 coldstart ratio 급증 (local control의 redundancy 심화). Flame은 안정적 유지 (scalability 입증).

**Server memory size (16GB→256GB):** 모든 메모리 크기에서 Flame이 가장 낮은 coldstart ratio.

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

- **Flame:** OpenFaaS + Kubernetes 기반, **~4,000 lines of Go**. Gateway, faas-netes, alert-manager 수정
- **Simulator:** **~12,000 lines of Java** — 대규모 파라미터 탐색 및 정책 검증
- **테스트/스크립트:** ~7,000 LOC (Java + Linux Shell)
- 기존 모듈 재사용: 인증, 보안, NAT streaming

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]


## 전체 요약

[[../paper-summaries/2023ASPLOS-summarize/flame-a-centralized-cache-controller-for-serverless-computing.md|전체 요약 보기]]
