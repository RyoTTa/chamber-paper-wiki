# Wiki Index

> Computer Architecture Research Wiki ??2019??026
> Last updated: 2026-06-26

## Overview

- [[paper-wiki/overview.md|Research Landscape]] ??High-level synthesis of the research field

## Concepts

- [[paper-wiki/concepts/dram.md|DRAM]] ??DRAM cell design, reliability, scaling, refresh, HBM
- [[paper-wiki/concepts/rowhammer.md|RowHammer]] ??RowHammer attacks, characterization, mitigation
- [[paper-wiki/concepts/pim.md|Processing-in-Memory]] ??PIM architectures, near-data processing, in-memory compute
- [[paper-wiki/concepts/llm-inference.md|LLM Inference]] ??Transformer inference, KV caching, phase splitting, sparsity
- [[paper-wiki/concepts/virtual-memory.md|Virtual Memory]] ??TLB, page tables, address translation, huge pages, MMU
- [[paper-wiki/concepts/storage.md|Storage]] ??SSD, Flash, NAND, FTL, key-value stores, computational storage
- [[paper-wiki/concepts/cache.md|Cache]] ??Caching policy, prefetching, replacement, LLC
- [[paper-wiki/concepts/security.md|Security]] ??Memory encryption, trusted execution, RowHammer, side channels
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]] ??Disaggregated memory, CXL, NUMA, far memory
- [[paper-wiki/concepts/hybrid-memory.md|Hybrid Memory]] ??Heterogeneous memory combining DRAM+NVM for cost-performance
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]] ??Persistent memory, PMEM, storage-class memory
- [[paper-wiki/concepts/compression.md|Compression]] ??Memory compression, data reduction, encoding
- [[paper-wiki/concepts/gpu.md|GPU]] ??GPU architecture, memory management, multi-tenancy
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]] ??Memory/storage disaggregation, CXL fabric
- [[paper-wiki/concepts/near-data-processing.md|Near-Data Processing]] ??NDP, computational storage, SmartSSD

## Papers (Recent)

- [[paper-wiki/papers/pimpal-accelerating-llm-inference-on-edge-devices-via-in-dram-arithmetic-lookup.md|PIMPAL]] — LUT 기반 PIM으로 엣지 기기 sLLM GEMV 가속화 — 기존 LUT 기반 PIM 대비 17.8× 성능, PU 기반 PIM 대비 40% 영역 오버헤드 감소 (DAC '25)
- [[paper-wiki/papers/llmservingSim-2.0-a-unified-simulator-for-heterogeneous-and-disaggregated-llm-serving-infrastructure.md|LLMServingSim 2.0]] — 이종적이고 분리된 LLM 서빙 인프라 통합 시뮬레이터 — 평균 오차 0.95%로 성능/메모리/전력 지표 재현 (ISPASS '26)
- [[paper-wiki/papers/fastserve-iteration-level-preemptive-scheduling-for-large-language-model-inference.md|FastServe]] — LLM 추론을 위한 iteration-level 선점형 스케줄링 — vLLM 대비 최대 6.1× throughput 향상 (NSDI '26)
- [[paper-wiki/papers/zipserv-fast-and-memory-efficient-llm-inference-with-hardware-aware-lossless-compression.md|ZipServ]] — GPU 아키텍처 공동설계 무손실 압축 LLM 추론 — cuBLAS 대비 최대 2.21× 가속, vLLM 대비 평균 1.22× 가속 (ASPLOS '26)
- [[paper-wiki/papers/understanding-and-optimizing-database-pushdown-on-disaggregated-storage.md|TapDB]] — 스토리지 분리 환경 데이터베이스 푸시다운 최적화 — 기존 솔루션 대비 1.3–2.3× 가속 (ASPLOS '26)
- [[paper-wiki/papers/straw-stress-aware-wl-based-read-disturbance-management-for-high-density-nand-flash-memory.md|STRAW]] — 고밀도 NAND 플래시 읽기 방해 관리 — RR 오버헤드 88.6% 감소 (ASPLOS '26)
- [[paper-wiki/papers/3676642-3736119.md|HybridTier]] — 적응형 CXL 메모리 tiering 시스템 — Memtis 대비 29% 성능 향상, 3.2× 빠른 적응 (ASPLOS '25)
- [[paper-wiki/papers/3779212-3790121.md|CXL Programming Model]] — CXL 위 분산 메모리 위한 최초의 formal programming model (ASPLOS '26)
- [[paper-wiki/papers/3779212-3790126.md|APT]] — 적응형 확률적 in-DRAM tracker로 DRAM read disturbance 방어 — 0% slowdown, TRH 694 (ASPLOS '26)
- [[paper-wiki/papers/lazy-persistency-a-high-performing-and-write-efficient-software-persistency-technique.md|Lazy Persistency]] — 캐시 자연적 퇴출 기반 NVM 영속성 — Eager 대비 실행 9%→1%, 쓰기증폭 21%→3% (ISCA '18)
- [[paper-wiki/papers/seesaw-using-superpages-to-improve-vipt-caches.md|SEESAW]] — Superpage 활용 VIPT 캐시 associativity 극복 — 2MB superpage에서 way 감소로 latency/energy 절감 (ISCA '18)
- [[paper-wiki/papers/snapea-predictive-early-activation-for-reducing-computation-in-deep-convolutional-neural-networks.md|SnaPEA]] — ReLU 특성 활용 조기 활성화 — Exact: 28% speedup, Predictive: 최대 3.59× speedup (ISCA '18)
- [[paper-wiki/papers/enabling-fine-grain-restricted-coset-coding-through-word-level-compression-for-pcm.md|WLCRC]] — MLC PCM 세밀한 인코딩 — 16비트 세밀화에서 39% 쓰기 에너지 절감 (HPCA '18)
- [[paper-wiki/papers/graphr-accelerating-graph-processing-using-reram.md|GraphR]] — ReRAM 기반 그래프 가속기 — CPU 대비 16× speedup, 34× energy 절감 (HPCA '18)
- [[paper-wiki/papers/mitigating-wordline-crosstalk-using-adaptive-trees-of-counters.md|CAT]] — 적응형 카운터 트리로 wordline crosstalk 완화 — 갱신전력 7% (SCA 21% 대비), 성능 ~0.5% 오버헤드 (ISCA '18)
- [[paper-wiki/papers/neural-cache-bit-serial-in-cache-acceleration-of-deep-neural-networks.md|Neural Cache]] — LLC를 대규모 병렬 연산유닛으로 재활용 — CPU 대비 18.3×, GPU 대비 7.7× 지연시간 향상 (ISCA '18)
- [[paper-wiki/papers/nonblocking-memory-refresh.md|Nonblocking Refresh]] — DRAM 배경 갱신으로 읽기 차단 제거 — 서버중복데이터 활용, 16Gb 16.2%, 32Gb 30.3% 성능향상 (ISCA '18)
- [[paper-wiki/papers/dhtm-durable-hardware-transactional-memory.md|DHTM]] — 최초의 완전한 하드웨어 ACID 트랜잭션 메모리 — 상용 HTM + redo 로깅, 21~25% 성능 향상 (ISCA '18)
- [[paper-wiki/papers/enabling-scientific-computing-on-memristive-accelerator.md|Memristive Scientific Computing]] — 메모리스트 크로스바에서 고정밀 부동소수점 연산 — GPU 대비 10.3× 성능, 10.9× 에너지 절감 (ISCA '18)
- [[paper-wiki/papers/energy-efficient-neural-network-accelerator-based-on-outlier-aware.md|OLAccel]] — 아웃라이어 인식 4비트 신경망 가속기 — 16비트 대비 최대 62.2% 에너지 절감 (ISCA '18)
- [[paper-wiki/papers/flexon-a-flexible-digital-neuron.md|Flexon]] — 유연한 디지털 뉴런 — CPU 대비 6,186× 에너지 효율 향상, 7.62mm² (ISCA '18)
- [[paper-wiki/papers/2b-ssd-the-case-for-dual-byte-and-block-addressable-solid-state-drives.md|2B-SSD]] — 바이트/블록 주소 지정 하이브리드 SSD — sub-1μs 쓰기 지연, 1.2~2.8× 처리량 향상 (ISCA '18)
- [[paper-wiki/papers/a-configurable-cloud-scale-dnn-processor-for-real-time-ai.md|Brainwave]] ??클라우드 규모 real-time AI를 위한 configurable NPU — 배치 없이 35 TeraFLOPS (ISCA '18)
- [[paper-wiki/papers/bit-fusion-bit-level-dynamically-composable-architecture-for-accelerating-deep-neural-network.md|Bit Fusion]] ??비트 수준 동적 융합 DNN 가속기 — Eyeriss 대비 3.9× 속도, 5.1× 에너지 절감 (ISCA '18)
- [[paper-wiki/papers/criticality-aware-tiered-cache-hierarchy-a-fundamental-relook-at-multi-level-cache-hierarchies.md|CATCH]] ??Criticality-aware 캐시 계층 — L2 제거로 30% 면적 절감 + 4.5% 성능 향상 (ISCA '18)
- [[paper-wiki/papers/farewell-my-shared-llc-a-case-for-private-die-stacked-dram-caches-for-servers.md|Farewell My Shared LLC!]] ??다이 스택 DRAM 기반 프라이빗 LLC로 서버 프로세서의 공유 LLC 한계 극복 (MICRO '18)
- [[paper-wiki/papers/genesys-enabling-continuous-learning-through-neural-network-evolution-in-hardware.md|GeneSys]] ??EA 기반 학습 시스템을 위한 HW-SW 프로토타입 — 2-5 orders of magnitude 에너지 효율성 향상 (MICRO '18)
- [[paper-wiki/papers/improving-the-performance-and-endurance-of-encrypted-non-volatile-main-memory-through-deduplicating-writes.md|DeWrite]] ??암호화된 NVM의 성능과 수명을 향상시키는 중복 제거 기반 쓰기 최적화 (MICRO '18)
- [[paper-wiki/papers/invalid-data-aware-coding-to-enhance-the-read-performance-of-high-density-flash-memories.md|IDA Coding]] ??고비트 밀도 플래시의 읽기 성능 향상을 위한 무효 데이터 인식 코딩 (MICRO '18)
- [[paper-wiki/papers/latr-lazy-translation-coherence.md|LATR]] ??Lazy TLB coherence로 IPI 없이 비동기적 TLB 무효화 처리 — Apache에서 59.9% 성능 향상 (ASPLOS '18)
- [[paper-wiki/papers/ltrf-enabling-high-capacity-register-files-for-gpus.md|LTRF]] ??컴파일 시간 구간 분석을 활용한 하드웨어/소프트웨어 협력 레지스터 프리페칭 — 31% IPC 향상 (ASPLOS '18)
- [[paper-wiki/papers/maeri-enabling-flexible-dataflow-mapping-over-dnn-accelerators.md|MAERI]] ??모듈형 DNN 가속기 — 유연한 데이터플로 매핑으로 8-459% 활용도 향상 (ASPLOS '18)
- [[paper-wiki/papers/filtering-translation-bandwidth-virtual-caching.md|Filtering Translation Bandwidth]] ??GPU 가상 캐시 계층을 통한 주소 번역 대역폭 필터링 — 이상적 MMU 대비 98% 성능 (ASPLOS '18)
- [[paper-wiki/papers/google-workloads-mitigating-data-movement.md|Google Workloads]] ??소비자 디바이스에서의 데이터 이동 병목 해결 — PIM으로 55.4% 에너지 절감 (ASPLOS '18)
- [[paper-wiki/papers/in-memory-data-parallel-processor.md|In-Memory Data Parallel Processor]] ??ReRAM 기반 인메모리 데이터 병렬 프로세서 — Parsec에서 7.5x speedup (ASPLOS '18)
- [[paper-wiki/papers/attache-towards-ideal-memory-compression-by-mitigating-metadata-bandwidth-overheads.md|Attaché]] ??메모리 압축 시 Metadata 대역폭 오버헤드 제거 (MICRO '18)
- [[paper-wiki/papers/cambricon-s-addressing-irregularity-in-sparse-neural-networks-through-a-cooperative-software-hardware-approach.md|Cambricon-S]] ??희소 신경망 불규칙성 해결을 위한 소프트웨어/하드웨어 협력 접근 (MICRO '18)
- [[paper-wiki/papers/checkmate-automated-synthesis-of-hardware-exploits-and-security-litmus-tests.md|CheckMate]] ??하드웨어 익스플로잇 자동 합성 및 보안 리터머스 테스트 (MICRO '18)
- [[paper-wiki/papers/compresso-pragmatic-main-memory-compression.md|Compresso]] ??OS-투명 메인 메모리 압축 (MICRO '18)
- [[paper-wiki/papers/beyond-the-memory-wall-a-case-for-memory-centric-hpc-system-for-deep-learning.md|Beyond the Memory Wall]] ??메모리 중심 딥러닝 HPC 아키텍처 (MICRO '18)
- [[paper-wiki/papers/ceaser-mitigating-conflict-based-cache-attacks-via-encrypted-address-and-remapping.md|CEASER]] ??암호화된 주소 기반 캐시 공격 완화 (MICRO '18)
- [[paper-wiki/papers/chameleon-a-dynamically-reconfigurable-heterogeneous-memory-system.md|CHAMELEON]] ??동적 재구성 이종 메모리 시스템 (MICRO '18)
- [[paper-wiki/papers/tapas-generating-parallel-accelerators-from-parallel-programs.md|TAPAS]] ??병렬 프로그램에서 동적 병렬리즘 지원 가속기 생성 (MICRO '18)
- [[paper-wiki/papers/taming-the-killer-microsecond.md|Taming the Killer Microsecond]] ??마이크로초 수준 지연 시간 숨김 문제 해결 (MICRO '18)
- [[paper-wiki/papers/swapcodes-error-codes-for-hardware-software-cooperative-gpu-pipeline-error-detection.md|SwapCodes]] ??GPU 파이프라인 오류 감지를 위한 하드웨어-소프트웨어 협력 메커니즘 (MICRO '18)
- [[paper-wiki/papers/ssdcheck-timely-and-accurate-prediction-of-irregular-behaviors-in-black-box-ssds.md|SSDcheck]] ??블랙박스 SSD 불규칙 동작 예측을 위한 성능 모델 (MICRO '18)
- [[paper-wiki/papers/diffy-a-dj-vu-free-differential-deep-neural-network-accelerator.md|Diffy]] ??차분 합성곱 기반 연산 이미징 DNN 가속기 (MICRO '18)
- [[paper-wiki/papers/duplicon-cache-mitigating-off-chip-memory-bank-and-bank-group-conflicts-via-data-duplication.md|Duplicon Cache]] ??뱅크/뱅크 그룹 충돌 완화를 위한 데이터 복제 캐시 (MICRO '18)
- [[paper-wiki/papers/efficient-hardware-assisted-logging-with-asynchronous-and-direct-update-for-persistent-memory.md|ReDU]] ??지속 메모리를 위한 비동기 직접 업데이트 HW 로깅 (MICRO '18)
- [[paper-wiki/papers/exploring-and-optimizing-chipkill-correct-for-persistent-memory-based-on-high-density-nvrams.md|NVRAM Chipkill-Correct]] ??고밀도 NVRAM 지속 메모리의 효율적 chipkill-correct (MICRO '18)
- [[paper-wiki/papers/invisispec-making-speculative-execution-invisible-in-the-cache-hierarchy.md|InvisiSpec]] ??스페큘레이션을 캐시 계층에서 숨겨 보안 달성 (MICRO '18)
- [[paper-wiki/papers/lergan-a-zero-free-low-data-movement-and-pim-based-gan-architecture.md|LerGAN]] ??PIM 기반 GAN 가속기로 데이터 이동 최소화 (MICRO '18)
- [[paper-wiki/papers/mdacache-caching-for-multi-dimensional-access-memories.md|MDACache]] ??다차원 접근 메모리를 위한 캐시 계층 설계 (MICRO '18)
- [[paper-wiki/papers/morphable-counters-enabling-compact-integrity-trees-for-low-overhead-secure-memories.md|Morphable Counters]] ??보안 메모리를 위한 컴팩트 무결성 트리 구현 (MICRO '18)
- [[paper-wiki/papers/multi-dimensional-parallel-training-of-winograd-layer-on-memory-centric-architecture.md|MPT]] ??Winograd 변환 기반 다차원 병렬 CNN 학습 — NDP 아키텍처로 2.7배 가속 (MICRO '18)
- [[paper-wiki/papers/neighborhood-aware-address-translation-for-irregular-gpu-applications.md|Neighborhood-Aware Address Translation]] ??비정형 GPU의 주소 변환 근방 인식 합치기 — 메모리 접근 37% 감소 (MICRO '18)
- [[paper-wiki/papers/permdnn-efficient-compressed-dnn-architecture-with-permuted-diagonal-matrices.md|PERM DNN]] ??순열 대각 행렬 기반 DNN 압축 — EIE 대비 3.3~4.8배 처리량 (MICRO '18)
- [[paper-wiki/papers/picl-a-software-transparent-persistent-cache-log-for-nonvolatile-main-memory.md|PiCL]] ??소프트웨어 투명 NVM 크래시 일관성 — 1% 미만 오버헤드 (MICRO '18)
- [[paper-wiki/papers/liu-processing-in-memory-for-energy-efficient-neural-network-training.md|PIM for NN Training]] ??이질적 PIM으로 신경망 학습 가속 — 고정 기능 + 프로그래머블 PIM 결합 (MICRO '18)
- [[paper-wiki/papers/wang-reducing-dram-latency-via-charge-level-aware-look-ahead-partial-restoration.md|CAL]] ??Charge-Level-Aware Look-Ahead Partial Restoration으로 DRAM 복원 지연시간 14.7% 감소 (MICRO '18)
- [[paper-wiki/papers/zhang-shadow-block-accelerating-oram-accesses-with-data-duplication.md|Shadow Block]] ??ORAM 보안 유지하면서 데이터 블록 조기 접근 — RD-Dup/HD-Dup 동적 결합 (MICRO '18)
- [[paper-wiki/papers/bharadwaj-scalable-distributed-last-level-tlbs.md|NOCSTAR]] ??분산 TLB 슬라이스 + 경량 인터커넥트로 공유 TLB 지연시간 감소 (MICRO '18)
- [[paper-wiki/papers/scope-a-stochastic-computing-engine-for-dram-based-in-situ-accelerator.md|SCOPE]] ??DRAM 기반 확률적 컴퓨팅 인시itu 가속기 — 데이터 이동 최소화 및 에너지 효율 향상 (MICRO '18)
- [[paper-wiki/papers/osiris-a-low-cost-mechanism-to-enable-restoration-of-secure-non-volatile-memories.md|Osiris]] ??보안 NVM의 저비용 복원 메커니즘 — 체크포인트 기반 빠른 복원 및 보안 유지 (MICRO '18)
- [[paper-wiki/papers/ucnn-exploiting-computational-reuse-in-deep-neural-networks-via-weight-repetition.md|UCNN]] ??가중치 반복을 활용한 CNN 가속기 — 최대 3.7배 에너지 절감 (ISCA '18)
- [[paper-wiki/papers/spandex-a-flexible-interface-for-efficient-heterogeneous-coherence.md|Spandex]] ??이기종 시스템을 위한 유연한 코히어런스 인터페이스 — 실행 시간 16% 절감 (ISCA '18)
- [[paper-wiki/papers/espresso-brewing-java-for-more-non-volatility-with-non-volatile-memory.md|Espresso]] ??Java에서 NVM 활용을 위한 전체적인 시스템 — PJH와 PJO로 기존 프로그램 호환성 유지 (ASPLOS '18)
- [[paper-wiki/papers/heatwatch-improving-3d-nand-flash-memory-device-reliability-by-exploiting-self-recovery-and-temperature-awareness.md|HeatWatch]] ??3D NAND 플래시에서 self-recovery 및 온도 효과 특성화 — 새로운 신뢰성 모델(오차 4.9%)로 플래시 수명 3.85배 향상 (HPCA '18)
- [[paper-wiki/papers/making-memristive-neural-network-accelerators-reliable.md|Memristive Neural Network Accelerators]] ??산술 코드 기반 오류 수정으로 memristive 신경망 가속기 신뢰성 확보 — 영역 4.5% 미만, 에너지 4.7% 미만 오버헤드 (HPCA '18)
- [[paper-wiki/papers/outerspace-an-outer-product-based-sparse-matrix-multiplication-accelerator.md|OuterSPACE]] ??외적 기반 희소 행렬 곱셈 가속기 — Intel MKL 대비 7.9배, cuSPARSE 대비 13.0배 속도 향상 (HPCA '18)
- [[paper-wiki/papers/latte-cc-latency-tolerance-aware-adaptive-cache-compression-management-for-energy-efficient-gpus.md|LATTE-CC]] ??GPU 레이턴시 내성 활용 적응형 캐시 압축 — 최대 48.4% 성능 향상, 에너지 10% 절감 (HPCA '18)
- [[paper-wiki/papers/profess-a-probabilistic-hybrid-main-memory-management-framework-for-high-performance-and-fairness.md|ProFess]] ??하이브리드 메인 메모리 관리를 위한 확률론적 프레임워크 — 공정성 15% 향상, 성능 12% 향상 (HPCA '18)
- [[paper-wiki/papers/rcoal-mitigating-gpu-timing-attack-via-subwarp-based-randomized-coalescing-techniques.md|RCoal]] ??GPU 타이밍 공격 완화를 위한 서브워프 기반 무작위화된 코얼레싱 기법 — 24~961배 보안 향상 (HPCA '18)
- [[paper-wiki/papers/record-replay-architecture-as-a-general-security-framework.md|Record-Replay Architecture]] ??RnR을 하드웨어 보안 기능을 보완하는 새로운 프레임워크 — 효율적이고 유연한 보안 메커니즘 (HPCA '18)
- [[paper-wiki/papers/making-huge-pages-actually-useful.md|Making Huge Pages Actually Useful]] ??huge pages 단편화 문제 해결 — Illuminator로 compaction 비용 99% 감소 (ASPLOS '18)
- [[paper-wiki/papers/mask-redesigning-the-gpu-memory-hierarchy-to-support-multi-application-concurrency.md|MASK]] ??GPU 멀티 애플리케이션 동시 실행을 위한 메모리 계층 재설계 — 시스템 처리량 57.8% 향상 (ASPLOS '18)
- [[paper-wiki/papers/neofog-nonvolatility-exploiting-optimizations-for-fog-computing.md|NEOFog]] ??비휘발성을 활용한 퍼지 컴퓨팅 최적화 — 인포프로세싱 능력 4.2배 증가 (ASPLOS '18)
- [[paper-wiki/papers/gist-efficient-data-encoding-for-deep-neural-network-training.md|Gist]] ??DNN 학습 feature maps 레이어별 인코딩 — 최대 4.1× 메모리 절감, 4% 오버헤드 (ISCA '18)
- [[paper-wiki/papers/grafboost-using-accelerated-flash-storage-for-external-graph-analytics.md|GraFBoost]] ??FPGA 기반 플래시 가속 그래프 분석 — 1GB DRAM으로 40억 정점/1280억 엣지 처리 (ISCA '18)
- [[paper-wiki/papers/guaranteeing-local-differential-privacy-on-ultra-low-power-systems.md|DP-Box]] ??ULP 시스템에서의 LDP 구현 — Resampling/Thresholding으로 저해상도 제약 극복 (ISCA '18)
- [[paper-wiki/papers/hiding-intermittent-information-leakage-with-architectural-support-for-blinking.md|Blinking]] ??정보 유출의 시간적 비균일성 활용 방어 — 15~30% 보호로 75%+ mutual information 차단 (ISCA '18)
- [[paper-wiki/papers/compressing-dma-engine-leveraging-activation-sparsity-for-training-deep-neural-networks.md|cDMA]] ??activation sparsity 활용 압축 DMA 엔진 — 평균 2.6× 압축률, 평균 53% 성능 향상 (HPCA '18)
- [[paper-wiki/papers/synergy-rethinking-secure-memory-design-for-error-correcting-memories.md|SYNERGY]] ??보안-신뢰성 공동 설계로 ECC-DIMM에 MAC 통합 — 추가 하드웨어 없이 20% 속도 향상, 31% EDP 감소, 185배 신뢰성 향상 (HPCA '18)
- [[paper-wiki/papers/crash-consistency-in-encrypted-non-volatile-main-memory-systems.md|Selective Counter-Atomicity]] ??암호화된 NVMM 시스템에서 crash consistency 최적화 — 1~8코어에서 6~40% 성능 향상 (HPCA '18)
- [[paper-wiki/papers/duo-exposing-on-chip-redundancy-to-rank-level-ecc-for-high-reliability.md|DUO]] ??온칩 중복성 이중 활용으로 IECC 비효율성 해결 — 평균 4-14% 낮은 에너지 소비 (HPCA '18)
- [[paper-wiki/papers/eruca-efficient-dram-resource-utilization-and-resource-conflict-avoidance-for-memory-system-parallelism.md|ERUCA]] ??효율적인 서브뱅킹으로 DRAM 리소스 충돌 방지 — 15% 성능 향상, <0.3% 면적 오버헤드 (HPCA '18)
- [[paper-wiki/papers/reliability-aware-data-placement-for-heterogeneous-memory-architecture.md|Reliability-Aware Data Placement]] ??HMA에서 AVF 기반 hotness-risk quadrant 분석으로 신뢰성 향상 — static 1.6×, dynamic 1.5×, annotation 1.3× reliability 향상 (HPCA '18)
- [[paper-wiki/papers/reducing-data-transfer-energy-by-exploiting-similarity-within-a-data-transaction.md|Base+XOR Transfer]] ??트랜잭션 내 데이터 유사성 활용 XOR 인코딩으로 POD I/O 에너지 절감 — 1값 35.3% 감소, DRAM 에너지 5.8% 절감, DBI 결합 시 48.2% 감소 (HPCA '18)
- [[paper-wiki/papers/espresso-brewing-java-for-more-non-volatility-with-non-volatile-memory.md|Espresso]] ??Java에서 NVM 활용 통합 지속성 프레임워크 — PJH와 PJO로 기존 프로그램 호환성 유지 + 최대 256x speedup (ASPLOS '18)
- [[paper-wiki/papers/secure-dimm-moving-oram-primitives-closer-to-memory.md|Secure DIMM]] ??ORAM 기능을 메모리 시스템으로 이동하여 프라이버시 보장 — SDIMM을 통한 성능 1.9배, 에너지 2.55배 향상 (HPCA '18)
- [[paper-wiki/papers/steal-but-no-force-efficient-hardware-undoredo-logging-for-persistent-memory-systems.md|Steal but No Force]] ??하드웨어 undo+redo 로깅을 통한 영속 메모리 시스템 성능 및 에너지 효율성 향상 (HPCA '18)
- [[paper-wiki/papers/the-dram-latency-puf-quickly-evaluating-physical-unclonable-functions-by-exploiting-the-latency-reliability-tradeoff-in-modern-commodity-dram-devices.md|DRAM Latency PUF]] ??소프트웨어 전용 시스템 호출을 통한 빠르고 신뢰할 수 있는 PUF 평가 — 기존 DRAM 유지보수 PUF 대비 152-1426배 속도 향상 (HPCA '18)


## Topic Coverage

| Topic | Paper Count (est.) | Key Venues |
|---|---|---|
| DRAM | ~30+ | ISCA, MICRO, HPCA |
| RowHammer | ~20+ | ISCA, MICRO, HPCA, ASPLOS |
| PIM | ~40+ | ISCA, MICRO, HPCA |
| LLM/AI | ~20+ | ISCA, ASPLOS, MICRO |
| Virtual Memory | ~25+ | ASPLOS, ISCA, HPCA |
| Storage | ~40+ | MICRO, ATC, FAST, ISCA |
| Security | ~15+ | ISCA, MICRO, ASPLOS |
| Memory Tiering | ~15+ | ASPLOS, MICRO, HPCA |
| NVM | ~30+ | ISCA, MICRO, HPCA |

## Source Map

Raw sources are organized by venue/year:
- `paper-source/{YYYY}{VENUE}/` ??PDF files
- `paper-summaries/{YYYY}{VENUE}-summarize/` ??Markdown summaries
- `ARXIV/{YYYY}ARXIV/` ??ArXiv papers
