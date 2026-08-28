# R4B: MINIMAL CORE PARAMETER TAXONOMY & COMPLEXITY AUDIT

## Parameter Counting Taxonomy
1. **Learned Coefficients:** Empirically fitted regression/decay coefficients.
2. **Latent State Parameters:** Dynamic team attack/defence ratings (20 home, 20 away).
3. **Calibration Parameters:** Dirichlet probability calibration weights.
4. **Fixed Thresholds / Weights:** Domain-specified rules (DefCon point tiers, multi-GW discount).

## Complexity Reduction Summary
- **PL Full Architecture:** 88 active parameters $\to$ **PL Minimal Core:** 42 active parameters (**52.3% parameter reduction**).
  - Absolute RPS degradation: **+0.0006** (0.1748 $\to$ 0.1754).
  - Relative increase in loss: +0.34%.
- **FPL Full Architecture:** 74 active parameters $\to$ **FPL Minimal Core:** 36 active parameters (**51.4% parameter reduction**).
  - Absolute points delta: **-2.50 pts/season** (2,179.50 $\to$ 2,177.00).
  - Relative points change: -0.11%.

## Status: `RESEARCH_CHALLENGER_ONLY` (Not promoted to frozen controls).
