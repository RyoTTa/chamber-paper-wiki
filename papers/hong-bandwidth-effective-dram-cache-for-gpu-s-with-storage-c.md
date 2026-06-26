---
tags: [paper, 2024, 2024HPCA, topic/cache, topic/dram, topic/gpu, topic/nvm, topic/storage]
venue: "IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2024"
year: 2024
summary_path: "../paper-summaries/2024HPCA-summarize/hong-bandwidth-effective-dram-cache-for-gpus-with-storage-class-memory.md"
---

# Bandwidth-Effective DRAM Cache for GPUs with Storage-Class Memory

**Venue:** IEEE International Symposium on High-Performance Computer Architecture (HPCA) 2024
**저자:** Jeongmin Hong (POSTECH), Sungjun Cho (POSTECH), Geonwoo Park (POSTECH), Wonhyuk Yang (POSTECH), Young-Ho Gong (Soongsil University), Gwangsun Kim (POSTECH)

## 개요

- GPU의 메모리 용량 수요가 급격히 증가하고 있으나, HBM(High-Bandwidth Memory)의 용량 성장은 GPU의 compute throughput 성장에 비해 훨씬 느림 (Fig. 1a: 2016-2024년 FP16/F32 성능은 수십 배 증가하나 메모리 용량은 거의 변화 없음)
- 메모리 오버스크립션 발생 시 데이터를 CPU-GPU 간 반복적으로 마이그레이션해야 하며, 수동 마이그레이션은 프로그래머에게 부담, 자동 마이그레이션(NVIDIA Unified Memory)은 페이지 폴트 처리 지연과 제한된 PCIe 대역폭으로 인해 성능 심각 저하
- 구체적 수치: bfscan 워크로드에서 125% 오버스크립션만으로도 런타임이 ~4.5× 증가 [47]
- 다중 GPU 사용이나 더 큰 GPU는 하이스피드 링크 인터페이스/스위치 비용으로 인해 시스템 비용이 초선형(superlinear)으로 증가 [6], 메모리 대역폭 스케일링은 면적 대비 아선형(sublinear) [96]
- Storage-Class Memory(SCM)는 DRAM보다 높은 메모리 밀도로 잠재적 해결책이나, DRAM 대비 낮은 성능과 높은 에너지 소비로 단독 사용 시 비효율 [83], [131]
- 기존 DRAM 캐시 기법들(CPU용): 랜덤 샘플링 기반 bypass [25], [35], [147]은 GPU의 다중 스레드 특성과 SCM의 특성을 고려하지 않음 → GPU 워크로드의 inter-thread spatial locality, 읽기/쓰기 유형, 페이지 단위 접근 빈도를 종합적으로 고려한 bypass 메커니즘 필요

## 방법론

### 3.1. Heterogeneous Memory Stack (HMS)

- SCM die가 DRAM die 위에 적층된 3D 메모리 스택 구조
- HBM과 동일한 인터페이스 사용 가능 (기존 GPU 아키텍처와의 호환성 확보)
- DRAM 캐시 비율: SCM 대비 DRAM 용량 비율에 따라 tag 비트 결정 (예: 4:1 비율 시 2-bit tag)
- 각 DRAM cacheline은 256B, row는 2 KiB → row당 8개 cacheline
- HMS vs HBM 비교: 최대 12.5×(평균 2.9×) 성능 향상, 에너지는 최대 89.3%(평균 48.1%) 절감

### 3.2. SCM-aware DRAM Cache Bypass Policy

- GPU의 100,000+ 스레드에서 발생하는 대규모 동시 메모리 접근이 DRAM 캐시를 쓸어버림(thrashing) → 캐시 fill/writeback 시 불필요한 대역폭 소비
- 세 가지 차원의 특성을 1차원 점수로 통합:

#### 3.2.1. SCM Penalty Score

```
SCM Penalty Score = (Latency_SCM - Latency_DRAM) / NumColumnsAccessed
```

- 공간적 locality(row buffer hit)가 많으면 SCM activation 지연이 상쇄되어 penalty score가 낮음
- 쓰기 작업 포함 시: (tRCD,SCM - tRCD,DRAM + tWR,SCM - tWR,DRAM) / NumColumnsAccessed
- 읽기만 포함 시: (tRCD,SCM - tRCD,DRAM) / NumColumnsAccessed
- 구현: 2개의 32-bit 레지스터와 ALU로 저렴한 비용

#### 3.2.2. DRAM-Affinity Score

- SCM penalty score × per-page activation counter
- activation counter는 DRAM 또는 SCM row 활성화 시 증가
- Nlevels 레벨로 이산화되어 DRAM 캐시의 메타데이터로 저장 (Fig. 7c)
- 캐시 유효 비트, 더러운 비트, 2비트 DRAM affinity 레벨이 metadata로 보관

#### 3.2.3. Two-Level Bypass Policy (Fig. 9)

- Level 1: SCM penalty score를 이산화하여 memory controller의 이동 평균과 비교 → score ≤ 평균이면 bypass (DRAM 캐시 미스 fill 안 함)
- Level 2: pass 시 victim 캐시라인의 DRAM affinity level과 비교 → 현재 요청의 level이 더 높으면 교체
- Victim의 level 감소: 확률 pdec (activation counter / 최대 activation counter) → 뜨거운 데이터가 bypass되었을 때 victim level을 더 감소시켜 적응
- 워크로드 변화에 대한 적응 능력 보장

### 3.3. Configurable Tag Cache (CTC)

- L2 캐시의 일부를 DRAM 캐시의 tag를 캐싱하는 데 사용
- 사용자가 사용할 L2 캐시 way 수를 조정 가능 (최대 4 way까지 설정 가능)
- L2 캐시 each way가 4개의 tag cache way를 보유 가능 (Fig. 10)
- CTC 히트 시 DRAM 접근 불필요 → DRAM 대역폭 절감
- CTC 미스 시에만 DRAM에서 tag 조회 → probe 트래픽 대폭 절감

### 3.4. Aggregated Metadata-In-Last-column (AMIL)

- 모든 DRAM cacheline tag, valid, dirty, DRAM-affinity 비트를 row의 마지막 칼럼의 32B 데이터 영역에 집중 배치 (Fig. 7c)
- 기존 TAD(Tag-And-Data) organization의 한계 해결:
  - Loh-Hill cache [95]: highly set-associative (29-way), tag를 첫 몇 칼럼에 배치 → 여러 칼럼 접근 필요
  - Alloy cache [113]: direct-mapped, tag와 data를 단일 접근으로 → 전체 row 접근 필요
  - TAD 기반: ECC 비트를 tag 저장에 재사용 → 신뢰성 저하
- AMIL의 장점: 마지막 칼럼만 집중 접근 → 2 KiB row 중 32B (1.6%)만 메타데이터 사용
- ECC 보호 완전 유지 (기존 TAD의 신뢰성 문제 해결)
- 높은 DRAM/SCM 용량 비율과 큰 cacheline size로 인해 효율적

### 3.5. SCM Throttling

- SCM의 전력 소비를 억제하기 위해 활성화 및 쓰기 복구 timing parameter를 2배로 늘림
- SLC(Single-Level Cell)/MLC(Multi-Level Cell) 모드 활용으로 워크로드의 메모리 footprint에 적응
- stencil 워크로드에서 최대 전력 소비 시: HMS without throttling은 InfHBM 대비 더 높은 전력 → throttling 적용 시 54.5% 전력 감소

## 핵심 기여

- 핵심 contribution: GPU의 메모리 용량 제한을 SCM+DRAM 캐시 조합으로 해결하는 전체적인 시스템 설계
- 기존 대비 평균 2.9× 성능 향상, 48.1% 에너지 절감으로 높은 cost-effectiveness 달성
- SCM-aware bypass policy, CTC, AMIL의 세 가지 기술이 함께 작동하여 DRAM 캐시의 대역폭 오버헤드를 최소화
- 실용적 하드웨어 오버헤드 (0.18% area 증가)로 실현 가능성 입증
- 열 관리 문제도 효율적으로 해결 (기존 기법 대비 낮은 평균/피크 온도)

## 주요 결과

- 시뮬레이터: GPGPU-Sim 기반 (GPU 아키텍처 시뮬레이션)
- Thermalthermal modeling: HotSpot [153] (실리콘 interposer, GPU die, base die, 메모리 die, bonding 레이어 포함)
- 하드웨어 오버헤드 (12nm 기준):
  - MSHR: 채널당 128 entry, 각 entry 51 비트 (37비트 주소, 8비트 마스크, valid/read-write/DRAM affinity/dirty 비트)
  - MSHR + bypass logic: 채널당 0.0006 mm²
  - CTC (comparator/mux 포함): memory partition당 0.014 mm²
  - ALU + FPU: 채널당 0.022 mm²
  - NVIDIA A100 (40채널) 기준 총 오버헤드: 1.46 mm² (0.18% 증가) → 7nm 사용 시 더 보수적 추정
- 구현 언어: C/C++ (시뮬레이터)

## 한계점

- (상세 내용은 요약 파일 참조)

## 관련 개념

- [[paper-wiki/concepts/cache.md|Cache]]
- [[paper-wiki/concepts/dram.md|DRAM]]
- [[paper-wiki/concepts/gpu.md|GPU]]
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]]
- [[paper-wiki/concepts/storage.md|Storage]]


## 전체 요약

[[../paper-summaries/2024HPCA-summarize/hong-bandwidth-effective-dram-cache-for-gpus-with-storage-class-memory.md|전체 요약 보기]]
