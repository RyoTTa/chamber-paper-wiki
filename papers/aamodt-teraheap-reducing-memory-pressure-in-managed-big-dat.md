---
tags: [paper, 2023, 2023ASPLOS, topic/dram, topic/nvm, topic/storage, topic/virtual-memory]
venue: ""
year: 2023
summary_path: "../paper-summaries/2023ASPLOS-summarize/teraheap-reducing-memory-pressure-in-managed-big-data-frameworks.md"
---

# TeraHeap: Reducing Memory Pressure in Managed Big Data Frameworks

**Venue:** 
**저자:** 

## 개요

Managed big data framework(Spark, Giraph 등)는 반복 연산을 수행하며 방대한 양의 long-lived 객체를 생성한다. 이 객체들이 managed heap에 쌓이면 memory pressure가 증가하여 빈번한 GC가 발생하고, 각 GC cycle의 yield가 낮아진다(오래 사는 객체가 많아 reclaim 공간이 적음).

기존 해결책은 객체를 off-heap(NVMe SSD 등)으로 serialize하여 이동시키는 것이다. 그러나 이 접근은 두 가지 문제가 있다:

1. **높은 Serialization/Deserialization (S/D) 비용:** 복잡한 데이터 구조를 가진 응용에서 S/D는 실행 시간의 큰 부분을 차지한다.
2. **높은 GC 비용:** off-heap 객체를 다시 heap으로 가져와 처리할 때 GC pressure가 증가한다.

저자들의 측정에 따르면, big data 응용에서 **GC와 S/D가 실행 시간의 최대 87%**를 차지한다(§1). 예를 들어 Spark-SD에서 PageRank 실행 시 64GB heap 기준으로 171회의 major GC가 발생하고 각각 평균 3.7초가 소요된다(Figure 7). TMO[49]는 NVMe SSD로 cold memory를 투명하게 swap하고 device-resident 객체에 직접 접근을 제공하지만, 여전히 device 전체에 대한 느린 GC scan을 피하지 못한다.

## 방법론

- **OpenJDK 8 (jdk8u345)** 기반, **Parallel Scavenge (PS) GC** 확장.
- **Interpreter + C1/C2 JIT compiler**의 post-write barrier 확장 (H1/H2 구분을 위한 reference range check 추가).
- DaCapo benchmark로 측정한 barrier 오버헤드는 평균 3% 미만.
- **HugeMap**[31] 사용: file-backed mmap에 huge page 적용 (ML workload용).
- Spark v3.3.0 + Kryo serializer, Giraph v1.2 + Hadoop v2.4.

## 핵심 기여

(요약 파일의 결론 섹션 참조)

## 주요 결과

### 4.1 평가 방법론

| 항목 | 내용 |
|------|------|
| **Testbed** | NVMe 서버: Xeon E5-2630 32코어, 256GB DRAM, Samsung PM983 2TB NVMe SSD; NVM 서버: Xeon Platinum 24코어, 192GB DRAM, Intel Optane DC PM 3TB |
| **Framework** | Spark v3.3.0, Giraph v1.2 |
| **Workloads** | Spark: GraphX 5종(PR, CC, SSSP, SVD, TR), MLlib 4종(LR, LgR, SVM, BC), SQL 1종(RL); Giraph: 5종(PR, CDLP, WCC, BFS, SSSP) |
| **Baselines** | Spark-SD(heap=DRAM, cache=off-heap NVMe/NVM), Spark-MO(heap=NVM memory mode), Giraph-OOC(heap=DRAM, offload to NVMe), Panthera [48], PS(OpenJDK11), G1(OpenJDK17) |
| **Metrics** | Execution time breakdown (Other, S/D+I/O, Minor GC, Major GC) |

### 4.2 성능 결과

**NVMe SSD, 동일 DRAM 기준:**
- Spark: Spark-SD 대비 **실행 시간 18%(SSSP)~73%(BC) 감소** (Figure 6).
- Giraph: Giraph-OOC 대비 **실행 시간 21%(CDLP)~28%(PR) 감소**.
- GC overhead: Spark에서 최대 96%, Giraph에서 최대 54% 감소.
- S/D cost: Spark에서 2%(BC)~93%(LR) 감소.

**DRAM 절감 효과:**
- **1.3×~4.6× 적은 DRAM**으로 Spark-SD 대비 최대 65% 성능 향상(SVD).
- Giraph에서 **1.2× 적은 DRAM**으로 7%(CDLP)~18%(PR) 성능 향상.
- 예: Giraph-PR에서 5번째 major GC 후 17GB 객체가 H2로 이동 → heap usage 13%로 감소(Figure 7).

**최신 GC와 비교 (Figure 8):**
- G1(OpenJDK17): PS 대비 GC time 최대 95% 감소하나 S/D overhead(최대 44%)는 해결 못 함.
- TeraHeap: G1 대비 **21%(CC)~48%(LgR) 성능 향상**.
- G1은 humongous object fragmentation으로 SVM, BC, RL에서 OOM 발생 → TeraHeap은 해결.

**NVM 환경 (Figure 12):**
- Spark-SD 대비 최대 **79% 성능 향상**(평균 56%).
- Spark-MO 대비 최대 **86% 성능 향상**(평균 48%). Spark-MO는 NVM latency로 인해 minor GC time 평균 36% 증가, TeraHeap은 H2 배치를 제어하여 NVM 접근을 최소화.
- Panthera [48] 대비 **7%~69% 성능 향상**. Panthera는 NVM read 최대 54배, write 최대 51배 더 수행.

**확장성 (Figure 13):**
- Mutator thread 2배 증가 시 TeraHeap은 최대 **23% 추가 성능 향상** → Spark-SD는 GC cost 44% 증가로 확장 불가.
- Dataset 크기 증가에도 성능 향상 유지(최대 70%).

### 4.3 GC Overhead 분석

- TeraHeap의 major GC는 Giraph-OOC 대비 모든 phase에서 최대 **75% faster**(Figure 11(b)).
- PR에서 평균 1.09억 개의 H1→H2 forward reference가 매 GC마다 scan 회피.
- Compaction phase가 major GC time의 37~44% 차지 (device I/O).

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]]


## 전체 요약

[[../paper-summaries/2023ASPLOS-summarize/teraheap-reducing-memory-pressure-in-managed-big-data-frameworks.md|전체 요약 보기]]
