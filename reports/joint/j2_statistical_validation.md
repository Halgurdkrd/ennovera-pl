# J2 STATISTICAL VALIDATION & BENCHMARK ABLATION

- **Canonical Benchmark Universe:** 1,520 matches across 4 seasons.
- **Expected XI Ablation:** Degrades 3-class accuracy by -2.2% (58.4% -> 56.2%), RPS by +0.0147. 100.0% of paired bootstrap resamples favored the full model over the ablated model.
- **Player Attack Ablation:** Degrades accuracy by -1.1% (58.4% -> 57.3%), RPS by +0.0062. 99.8% of resamples favored the full model.
- **Subgroup Verification:** In matches with >2 missing starters, Expected XI improves RPS by -0.0250 (0.2045 -> 0.1795).
