---
tags: [concept, security, encryption, trusted-execution, side-channel]
source_count: 20
last_updated: 2026-06-25
---

# Security

## Summary

Memory security research covers memory encryption, trusted execution environments, side-channel attacks, and RowHammer as a security threat. Recent work focuses on practical, low-overhead solutions for real systems.

## Key Ideas

### Memory Encryption
- **Counter-light Memory Encryption**: Lightweight encryption with reduced counter storage overhead ([counter-light-memory-encryption.md])
- **Triad-NVM**: Persistency for integrity-protected encrypted NVMs ([triad-nvm-persistency-for-integrity-protected-and-encrypted-non-volatile-memories.md])
- **Lelantus**: Fine-granularity copy-on-write operations for secure NVMs ([lelantus-fine-granularity-copy-on-write-operations-for-secure-non-volatile-memories.md])
- **SuperMem**: Application-transparent secure persistent memory with low overheads ([supermem-enabling-application-transparent-secure-persistent-memory-with-low-overheads.md])
- **DeWrite**: 암호화된 NVM의 성능과 수명을 향상시키는 중복 제거 기반 쓰기 최적화 — 경량 해시 기반 인라인 중복 제거로 쓰기 54% 감소, 암호화와의 시너지 통합 ([improving-the-performance-and-endurance-of-encrypted-non-volatile-main-memory-through-deduplicating-writes.md])

### Trusted Execution
- Memory encryption engines (MEE) for TEEs like Intel SGX and TDX
- Page table protection mechanisms
- Security for disaggregated memory systems

### Side Channels and Covert Channels
- **BranchScope**: 분기 방향 예측기에 대한 최초의 세밀한 사이드 채널 공격 — PHT 충돌을 이용한 분기 방향 추론 ([paper-summaries/2018ASPLOS-summarize/branchscope-a-new-side-channel-attack-on-directional-branch-predictor.md])
- **CEASER**: 암호화된 주소 공간과 동적 리매핑으로 LLC conflict-based 공격 완화 — 100년 이상 공격 견딤, 1% 성능 오버헤드 ([paper-summaries/2018MICRO-summarize/ceaser-mitigating-conflict-based-cache-attacks-via-encrypted-address-and-remapping.md])
- **CheckMate**: μhb 그래프와 RMF를 이용한 하드웨어 익스플로잇 자동 합성 — Meltdown/Spectre 자동 합성, SpectrePrime으로 Intel i7에서 99.95% 정확도 달성 ([paper-summaries/2018MICRO-summarize/checkmate-automated-synthesis-of-hardware-exploits-and-security-litmus-tests.md])
- RowHammer defenses can introduce new covert channels ([understanding-and-mitigating-covert-channel-and-side-channel-vulnerabilities-introduced-by-rowhammer-defenses.md])
- Timing-based side channels through shared memory resources
- Cross-user-kernel-boundary RowHammer attacks ([pthammer-cross-user-kernel-boundary-rowhammer-through-implicit-accesses.md])
- **Shadow Block**: ORAM 보안 유지하면서 데이터 블록 조기 접근 — RD-Dup/HD-Dup 동적 결합으로 성능 향상 ([paper-summaries/2018MICRO-summarize/shadow-block-accelerating-oram-accesses-with-data-duplication.md])

### Applied Security
- **DAMN**: IOMMU 기반 DMA 공격 보호에서 보안/성능 트레이드오프 제거 — 사용자/커널 경계에서 보호 제공 ([paper-summaries/2018ASPLOS-summarize/damn-overhead-free-iommu-protection-for-networking.md])
- **Anubis**: Ultra-low overhead recovery for secure NVMs ([anubis-ultra-low-overhead-and-recovery-for-secure-nvms.md])
- Security for CXL memory pooling
- Integrity verification for disaggregated memory

## Related Papers

- [branchscope-a-new-side-channel-attack-on-directional-branch-predictor.md]
- [damn-overhead-free-iommu-protection-for-networking.md]
- [counter-light-memory-encryption.md]
- [understanding-and-mitigating-covert-channel-and-side-channel-vulnerabilities-introduced-by-rowhammer-defenses.md]
- [lelantus-fine-granularity-copy-on-write-operations-for-secure-non-volatile-memories.md]
- [pthammer-cross-user-kernel-boundary-rowhammer-through-implicit-accesses.md]
- [ceaser-mitigating-conflict-based-cache-attacks-via-encrypted-address-and-remapping.md]
- [checkmate-automated-synthesis-of-hardware-exploits-and-security-litmus-tests.md]
- [improving-the-performance-and-endurance-of-encrypted-non-volatile-main-memory-through-deduplicating-writes.md]

## Cross-references

- [[paper-wiki/concepts/rowhammer.md|RowHammer]] ??DRAM disturbance as security threat
- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]] ??Secure NVM design
- [[paper-wiki/concepts/disaggregation.md|Disaggregation]] ??Security for CXL/fabric-attached memory
