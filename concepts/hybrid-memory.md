---
tags: [concept, hybrid-memory, dram, nvm, memory-tiering]
source_count: 2
last_updated: 2026-06-26
---

# Hybrid Memory

## Summary

Hybrid Memory는 DRAM과 NVM과 같은 다른 유형의 메모리를 결합하여 비용 효율성과 성능을 동시에 달성하는 메모리 시스템입니다. 주요 연구 주제에는 메모리 관리, 마이그레이션 전략, 공정성 및 성능 최적화가 포함됩니다.

## Key Ideas

### Memory Management
- **ProFess**: 고성능과 공정성을 위한 확률론적 하이브리드 메인 메모리 관리 프레임워크 — RSM와 MDM을 통한 공정성 15% 향상, 성능 12% 향상 ([paper-summaries/2018HPCA-summarize/profess-a-probabilistic-hybrid-main-memory-management-framework-for-high-performance-and-fairness.md])
- **Reliability-Aware Data Placement**: HMA에서 AVF 기반 hotness-risk quadrant 분석으로 신뢰성 향상 — static 1.6×, dynamic 1.5×, annotation 1.3× reliability 향상 ([paper-summaries/2018HPCA-summarize/reliability-aware-data-placement-for-heterogeneous-memory-architecture.md])

### Migration Strategies
- 데이터 마이그레이션을 통한 메모리 계층 최적화
- 접근 패턴 기반 적응형 마이그레이션 전략
- 비용-편익 분석을 통한 효과적인 마이그레이션 결정

### Performance and Fairness
- 다중 프로그램 워크로드에서의 공정한 메모리 할당
- 성능과 공정성 간의 트레이드오프 최적화
- 확률론적 접근을 통한 의사결정 최적화

## Related Papers

- [profess-a-probabilistic-hybrid-main-memory-management-framework-for-high-performance-and-fairness.md]
- [reliability-aware-data-placement-for-heterogeneous-memory-architecture.md]

## Cross-references

- [[paper-wiki/concepts/nvm.md|Non-Volatile Memory]] — NVM as component of hybrid memory
- [[paper-wiki/concepts/dram.md|DRAM]] — DRAM as fast component of hybrid memory
- [[paper-wiki/concepts/memory-tiering.md|Memory Tiering]] — Hybrid memory as tiered architecture
