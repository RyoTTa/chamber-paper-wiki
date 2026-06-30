---
tags: [concept, pim, near-data, processing-in-memory]
source_count: 46
last_updated: 2026-06-30
---

# Processing-in-Memory

## Summary

Processing-in-Memory (PIM) integrates computation logic near or inside memory arrays to overcome the data movement bottleneck (von Neumann bottleneck). Research spans analog in-memory computing (crossbar-based), digital PIM (bank-level processors), near-data processing (NDP), and full software stacks for real hardware.

## Key Ideas

### PIM Architectures

#### Bank-level PIM (Digital)
- **PIM-HBM (Samsung)**: Commercial HBM2-based PIM with FP16 MAC units per DRAM bank; full software stack demonstrated ([hardware-architecture-and-software-stack-for-pim-based-on-commercial-dram-technology.md])
- **Newton**: DRAM-maker's Accelerator-in-Memory architecture for ML workloads ([newton-a-dram-makers-accelerator-in-memory-aim-architecture-for-machine-learning.md])
- **SIMDRAM**: Framework for bit-serial SIMD processing using DRAM ([simdram-a-framework-for-bit-serial-simd-processing-using-dram.md])
- **CODIC**: Low-cost substrate for custom in-DRAM functionalities and optimizations ([codic-a-low-cost-substrate-for-enabling-custom-in-dram-functionalities-and-optimizations.md])
- **Active-Routing**: Compute-on-the-way for near-data processing ([active-routing-compute-on-the-way-for-near-data-processing.md])

#### Analog/Crossbar PIM
- **FloatPIM**: In-memory acceleration of DNN training using analog computing ([floatpim-in-memory-acceleration-of-deep-neural-network-training.md])
- **RACER**: Bit-pipelined processing using resistive memory ([racer-bit-pipelined-processing-using-resistive-memory.md])
- **CASCADE**: Connecting RRAMs for in-memory processing ([cascade-connecting-rrams-for-in-memory-processing.md])
- Accelerating GCNs using crossbar-based PIM architectures ([accelerating-gcns-using-crossbar-based-processing-in-memory-architectures.md])
- **Memristive Accelerators for Scientific Computing**: 메모리스트 크로스바에서 고정밀 부동소수점 연산 지원 — 지수 범위 국소성, 조기 종료, 정적 스케줄링 기법으로 GPU 대비 10.3배 성능 향상, 10.9배 에너지 절감 ([paper-summaries/2018ISCA-summarize/enabling-scientific-computing-on-memristive-accelerators.md])
- **GraphR**: ReRAM 크로스바 기반 그래프 처리 가속기 — 아날로그 SpMV로 CPU 대비 16× speedup, 34× energy 절감 ([paper-summaries/2018HPCA-summarize/graphr-accelerating-graph-processing-using-reram.md])
- **Memristive Neural Network Accelerators**: 산술 코드 기반 오류 수정으로 memristive 신경망 가속기의 아날로그 컴퓨팅 오류 해결 — 영역 4.5% 미만, 에너지 4.7% 미만 오버헤드로 MNIST 1.5배, ILSVRC-2012 1.1배 오류율 감소 ([paper-summaries/2018HPCA-summarize/making-memristive-neural-network-accelerators-reliable.md])

### Near-Data Processing (NDP)
- **CoNDA**: Cache coherence support for near-data accelerators ([conda-efficient-cache-coherence-support-for-near-data-accelerators.md])
- **MEDAL**: Scalable DIMM-based NDP accelerator for DNA seeding ([medal-scalable-dimm-based-ndp-accelerator-for-dna-seeding-algorithm.md])
- **TensorDIMM**: Near-memory processing for embeddings and tensor operations ([tensordimm-near-memory-processing-for-embeddings-and-tensor-operations.md])
- **ABC-DIMM**: Alleviating communication bottleneck in DIMM-based NDP ([abc-dimm-alleviating-the-bottleneck-of-communication-in-dimm-based-near-memory-processing.md])
- **Near-data acceleration with concurrent host access** ([near-data-acceleration-with-concurrent-host-access.md])
- **Beacon**: Scalable NDP accelerators for genome analysis with CXL support ([beacon-scalable-near-data-processing-accelerators-for-genome-analysis-near-memory-pool-with-the-cxl-support.md])
- **MCN**: DDR 채널 위에서 이더넷 통신을 에뮬레이션하는 NDP 아키텍처 — 기존 MPI/Spark를 변경 없이 사용 가능, 8 DIMM으로 4.56× 처리량 향상 ([application-transparent-near-memory-processing-architecture-with-memory-channel-network.md])

### PIM Software and Systems
- **UPMEM**: Real PIM hardware with commercial DRAM; software secrets for real workloads ([upmem-unleashed-software-secrets-for-speed.md])
- **Full software stack** for commercial PIM: C/C++ programming model, compiler, runtime
- **PIM-Malloc**: Fast and scalable dynamic memory allocator for PIM systems ([pim-malloc-a-fast-and-scalable-dynamic-memory-allocator-for-pim.md])
- **DL-PIM**: Improving data locality in PIM systems ([dl-pim-improving-data-locality-in-processing-in-memory-systems.md])
- **Modeling/simulation frameworks** for PIM architectures ([modeling-and-simulation-frameworks-for-processing-in-memory-architectures.md])

### Application-Specific PIM
- **RecNMP**: Accelerating personalized recommendation with NDP ([recnmp-accelerating-personalized-recommendation-with-near-memory-processing.md])
- **SPACE**: Locality-aware processing in heterogeneous memory for recommendations ([space-locality-aware-processing-in-heterogeneous-memory-for-recommendations.md])
- **GraphQ**: Scalable PIM-based graph processing ([graphq-scalable-pim-based-graph-processing.md])
- **SISA**: Set-centric ISA for graph mining on PIM systems ([sisa-set-centric-isa-for-graph-mining-on-pim-systems.md])
- **PIM for NN Training**: 이질적 PIM으로 신경망 학습 가속 — 고정 기능 + 프로그래머블 PIM 결합, OpenCL 기반 프로그래밍 ([paper-summaries/2018MICRO-summarize/processing-in-memory-for-energy-efficient-neural-network-training-a-heterogeneous-approach.md])
- **GenPIP**: In-memory acceleration of genome analysis ([genpip-in-memory-acceleration-of-genome-analysis-via-tight-integration-of-basecalling-and-read-mapping.md])
- **TRiM**: Enhancing processor-memory interfaces with scalable tensor reduction in memory ([trim-enhancing-processor-memory-interfaces-with-scalable-tensor-reduction-in-memory.md])
- **PLUTO**: Massively parallel computation in DRAM via lookup tables ([pluto-enabling-massively-parallel-computation-in-dram-via-lookup-tables.md])
- **PIMPAL**: LUT 기반 PIM으로 sLLM GEMV 가속화 — 서브어레이 수준 병렬 룩업, 지역성 인식 컴퓨팅 매핑(LCM), LUT 집합화(LAG)로 기존 LUT 기반 PIM 대비 17.8배 성능 향상, PU 기반 PIM 대비 40% 영역 오버헤드 감소 ([paper-summaries/2025DAC-summarize/pimpal-accelerating-llm-inference-on-edge-devices-via-in-dram-arithmetic-lookup.md])
- **Google Workloads for Consumer Devices**: 소비자 디바이스에서의 데이터 이동 병목 해결 — PIM으로 평균 55.4% 에너지 절감, 54.2% 실행 시간 단축 ([paper-summaries/2018ASPLOS-summarize/google-workloads-for-consumer-devices-mitigating-data-movement-bottlenecks.md])
- **OuterSPACE**: 외적 기반 희소 행렬 곱셈 가속기 — 곱셈과 축적 분리로 중복 메모리 접근 제거, Intel MKL 대비 7.9배, cuSPPARSE 대비 13.0배 속도 향상, 24W에서 2.9 GFLOPS ([paper-summaries/2018HPCA-summarize/outerspace-an-outer-product-based-sparse-matrix-multiplication-accelerator.md])

### Domain-Specific PIM
- **PIM-VR**: Customized memory cube for virtual reality ([pim-vr-customized-memory-cube-for-virtual-reality.md])
- **iPIM**: Programmable in-memory image processing accelerator ([ipim-programmable-in-memory-image-processing-accelerator-using-near-bank-architecture.md])
- **eAP**: Scalable in-memory accelerator for automata processing ([eap-scalable-in-memory-accelerator-for-automata-processing.md])
- **BioPIM**: Processing-in-memory for genomics workloads ([biopim-processing-in-memory-for-genomics-workloads.md])
- **SparseAP**: 프로파일링 기반 핫/콜드 상태 예측으로 대규모 NFA 애플리케이션을 효율적 처리 — 기하평균 2.1×(최대 47×) 속도 향상 ([architectural-support-for-efficient-large-scale-automata-processing.md])

### PIM Interconnect
- **PIMnet**: PIM 뱅크 간 직접 연결을 제공하는 도메인 특화 네트워크 — 호스트 CPU 통신 병목 제거, AllReduce 최대 85배 가속, 실제 애플리케이션 11.8배 성능 향상 ([paper-summaries/2025HPCA-summarize/pimnet-a-domain-specific-network-for-efficient-collective-communication-in-scalable-pim.md])

### GPU + PIM
- Improving address translation in multi-GPUs with PIM concepts
- Designing virtual memory systems for MCM GPUs with near-data processing

## Related Papers

See paper-summaries directories: many PIM papers across ISCA, MICRO, HPCA (2019??026)

## Cross-references

- [[paper-wiki/concepts/dram.md|DRAM]] ??PIM is built on DRAM technology
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]] ??Overlapping concept space
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]] ??LLM-specific PIM accelerators
- [[paper-wiki/concepts/gpu.md|GPU]] ??GPU/PIM hybrid architectures
- [[paper-wiki/concepts/storage.md|Storage]] ??Computational storage as NDP variant
