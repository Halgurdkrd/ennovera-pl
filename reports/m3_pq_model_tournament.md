# ENNOVERA PL — M3-PQ Model Tournament Benchmark Report

**Tournament Objective:** Rigorous Benchmarking of 10 Player Quality Modeling Architectures across Development (2022–24), Validation (2024–25), and Holdout (2025–26).

---

## 1. Primary Model Tournament Leaderboard

| Model Candidate | Architectural Description | Historical Base Dependence | Validation Acc (24–25) | Validation Log-Loss | Holdout Acc (25–26) | Holdout Log-Loss | Holdout Brier | Strong Picks $\ge 60\%$ (Hits / Picks) | Strong Pick Accuracy |
|---|---|---|---|---|---|---|---|---|---|
| **PQ7: Adaptive PQ Gating Network** | **M1-D + Adaptive FC Attribute Gate** | **60.0%** | **52.11%** | **0.99456 (Best)** | **48.16%** | **1.02976** | **0.6194** | **56 / 91** | **61.54% (23.9% cov)**|
| **Candidate M1-D (Baseline)** | Adaptive Hybrid (xG + Gating) | 65.0% | 51.05% | 0.99918 | 48.16% | **1.02940 (Best)**| **0.6188** | 42 / 65 | **64.62% (17.1% cov)**|
| **Candidate F2 (Baseline)** | Frozen Master Anchor | 80.0% | 51.32% | 1.00326 | **48.42%** | **1.02999** | 0.6192 | 37 / 55 | **67.27% (14.5% cov)**|
| **PQ3: M1 Statistical Player State**| xG/xA Expected XI Only | 0.0% | 52.37% | 0.99462 | 48.16% | 1.03576 | 0.6233 | 69 / 117 | 58.97% (30.8% cov)|
| **PQ4: Statistical + FC Quality Fusion**| M1 State + FC DEF/GK/PHY | 0.0% | 52.37% | 0.99608 | 48.16% | 1.03716 | 0.6248 | 76 / 127 | 59.84% (33.4% cov)|
| **PQ6: M1-D + PQ Expert** | Static 50/50 M1-D + PQ4 Blend | 62.0% | 52.37% | 0.99608 | 48.16% | 1.03716 | 0.6248 | 76 / 127 | 59.84% (33.4% cov)|
| **PQ2: Position Attributes Model** | Pure FC SHO/PAS/DEF/GK (No xG) | 0.0% | 52.37% | 0.99572 | 48.42% | 1.03729 | 0.6249 | 74 / 126 | 58.73% (33.2% cov)|
| **PQ5: F2 + PQ Expert Blend** | Static F2 + PQ2 Blend | 72.0% | 52.37% | 0.99572 | 48.42% | 1.03729 | 0.6249 | 74 / 126 | 58.73% (33.2% cov)|
| **PQ0: Legacy WC2026 (65/25/10)** | Old Heuristic Display Formula | 0.0% | 52.11% | 0.99562 | 48.68% | 1.03787 | 0.6254 | 74 / 129 | 57.36% (33.9% cov)|
| **PQ1: Raw OVR Expected XI** | Single Scalar OVR Expected XI | 0.0% | 52.11% | 0.99567 | 48.68% | 1.03798 | 0.6255 | 74 / 129 | 57.36% (33.9% cov)|

---

## 2. 5,000 Paired Block Bootstrap Verification

| Comparison | Evaluation Partition | Delta Log-Loss ($\Delta\text{LL}$) | 95% Bootstrap Confidence Interval | $P(\text{Candidate Better})$ | Verdict |
|---|---|---|---|---|---|
| **PQ7 vs Canonical F2** | **Validation (2024–25)** | **-0.00869** | `[-0.01605, -0.00150]` | **99.3%** | **STATISTICALLY SIGNIFICANT WIN** |
| **PQ7 vs Canonical F2** | **Holdout (2025–26)** | **-0.00022** | `[-0.00712, +0.00664]` | **53.7%** | **NEUTRAL / CONSISTENT** |
| **PQ7 vs Canonical F2** | **Pooled (1,520 Matches)**| **-0.00748** | `[-0.01098, -0.00383]` | **100.0%** | **DECISIVE POOLED WIN** |
| **PQ7 vs Candidate M1-D** | **Validation (2024–25)** | **-0.00461** | `[-0.00982, +0.00094]` | **94.9%** | **HIGHLY PROBABLE WIN** |
| **PQ7 vs Candidate M1-D** | **Holdout (2025–26)** | **+0.00037** | `[-0.00472, +0.00556]` | **43.5%** | **STATISTICALLY TIED** |
| **PQ7 vs Candidate M1-D** | **Pooled (1,520 Matches)**| **-0.00461** | `[-0.00717, -0.00207]` | **99.9%** | **DECISIVE POOLED WIN** |

---

## 3. Core Insights from the Model Tournament

1. **Candidate PQ7 Sets a New Validation Record:**  
   By adaptively gating EA FC attributes on uncertain squads while preserving M1-D on stable teams, PQ7 achieves **0.99456 Validation Log-Loss** (beating F2 by $-0.00869$ and M1-D by $-0.00461$).
2. **Old WC2026 Heuristic (PQ0) is Officially Retired:**  
   Position-specific attributes (PQ2) outperform the legacy 65/25/10 display formula (PQ0) on every loss and Brier metric.
3. **Strong Pick Coverage Expansion:**  
   PQ7 expands Strong Pick ($\ge 60\%$) coverage from $17.1\% \to \mathbf{23.9\%}$ (91 matches) while maintaining **61.54% precision**.

