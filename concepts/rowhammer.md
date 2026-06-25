---
tags: [concept, rowhammer, security, dram, reliability]
source_count: 20
last_updated: 2026-06-19
---

# RowHammer

## Summary

RowHammer is a DRAM disturbance vulnerability where repeatedly activating a row causes bit flips in adjacent rows due to capacitive coupling. First reported in 2014, it has become increasingly critical as DRAM scales to smaller technology nodes. Research spans characterization of the phenomenon, attack methodologies, and mitigation techniques.

## Key Ideas

### Characterization
- **Aggressor-victim model**: Repeated activation (hammering) of aggressor rows induces charge leakage in victim rows through cell-to-cell coupling
- **HCfirst measurement**: The minimum hammer count required for first bit flip decreases with newer DRAM generations ([revisiting-rowhammer-an-experimental-analysis-of-modern-dram-devices-and-mitigation-techniques.md]) 
- **Temperature dependency**: RowHammer effects worsen at higher temperatures; controlled at 50째C in experimental studies
- **Data pattern sensitivity**: Certain data patterns (e.g., row-stripe) increase bit flip probability
- **In-DRAM TRR**: Modern DRAM includes Target Row Refresh (TRR) mechanisms, but these can be reverse-engineered ([uncovering-in-dram-rowhammer-protection-mechanisms.md])

### Attack Vectors
- **PThammer**: Cross-user-kernel-boundary RowHammer through implicit memory accesses ([pthammer-cross-user-kernel-boundary-rowhammer-through-implicit-accesses.md])
- **Rho-Hammer**: Revives RowHammer attacks on new architectures via prefetching ([rho-hammer-reviving-rowhammer-attacks-on-new-architectures-via-prefetching.md])
- **Covert/side channels**: RowHammer defenses introduce new vulnerability surfaces ([understanding-and-mitigating-covert-channel-and-side-channel-vulnerabilities-introduced-by-rowhammer-defenses.md])

### Mitigation Techniques

#### Counter-based
- **TWiCe**: Time Window Counter based prevention ([twice-preventing-row-hammering-by-exploiting-time-window-counters.md])
- **BlockHammer**: Prevents RowHammer at low cost by tracking aggressor rows ([blockhammer-preventing-rowhammer-at-low-cost.md])
- **PrIDE**: Achieves secure RowHammer mitigation with low-cost in-DRAM trackers ([pride-achieving-secure-rowhammer-mitigation-with-low-cost-in-dram-trackers.md])
- **AQUA**: Scalable mitigation by quarantining aggressor rows at runtime ([aqua-scalable-rowhammer-mitigation-by-quarantining-aggressor-rows-at-runtime.md])

#### Probabilistic
- **PARA**: Probabilistic Adjacent Row Activation ??refreshes random adjacent rows with probability p
- **Randomized Row-Swap**: Breaks spatial correlation by swapping row mappings ([randomized-row-swap-mitigating-row-hammer-by-breaking-spatial-correlation.md])

#### Hybrid
- **Graphene**: Strong yet lightweight Row Hammer protection combining multiple techniques ([graphene-strong-yet-lightweight-row-hammer-protection.md])
- Page table protection using monotonic pointers ([protecting-page-tables-from-rowhammer-attacks-using-monotonic-pointers.md])

### Trends
- RowHammer vulnerability is **worsening** with each DRAM generation ??newer chips require fewer activations to flip bits
- In-DRAM TRR is not a complete solution; software and system-level defenses remain necessary
- The tension between performance, cost, and security is a central theme ??all mitigations involve trade-offs
- Recent work shows RowHammer-like effects (read disturb) also affect modern NAND flash

> **Contradiction**: Some papers suggest in-DRAM TRR may be sufficient for consumer workloads, while characterization studies show TRR can be bypassed with specific access patterns.

## Related Papers

- [revisiting-rowhammer-an-experimental-analysis-of-modern-dram-devices-and-mitigation-techniques.md] ??Comprehensive characterization
- [a-deeper-look-into-rowhammer-sensitivities-experimental-analysis.md] ??Latest sensitivity analysis
- [uncovering-in-dram-rowhammer-protection-mechanisms.md] ??In-DRAM TRR analysis
- [pride-achieving-secure-rowhammer-mitigation-with-low-cost-in-dram-trackers.md] ??PrIDE mitigation
- [blockhammer-preventing-rowhammer-at-low-cost.md] ??BlockHammer mitigation
- [pthammer-cross-user-kernel-boundary-rowhammer-through-implicit-accesses.md] ??Cross-boundary attacks
- [graphene-strong-yet-lightweight-row-hammer-protection.md] ??Graphene hybrid protection
- [randomized-row-swap-mitigating-row-hammer-by-breaking-spatial-correlation.md] ??Row-swap mitigation
- [twice-preventing-row-hammering-by-exploiting-time-window-counters.md] ??TWiCe counter-based

## Cross-references

- [[paper-wiki/concepts/dram.md|DRAM]] ??RowHammer is a DRAM-level vulnerability
- [[paper-wiki/concepts/security.md|Security]] ??RowHammer as a security threat
- [[paper-wiki/concepts/storage.md|Storage]] ??Read disturb in NAND flash (analogous phenomenon)
