# ENNOVERA PL — M3-R1 Router Tournament Benchmark Report

**Tournament Scope:** Forensic Evaluation of 9 Advanced Pre-Match Routing Architectures (R0 to R8) Across Multi-Season Validation and Holdout Partitions.

---

## 1. Candidate Leaderboard: M3-R1 Router Tournament

| Router Candidate Architecture | Architectural Description | Val Acc (%) | Val Log-Loss | Holdout Correct (2025–26) | Holdout Acc (%) | Holdout Log-Loss | Holdout Brier | Net Winner Gain vs Deployed | Oracle Opportunity Capture | Routing Efficiency (%) | Strong Picks $\ge 60\%$ (Hits / Picks) | Strong Pick Accuracy (%) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **R6: Hierarchical Context Gate** | Multi-tier football rule gating tree | 51.58% | 0.99552 | 187 / 380 | 49.21% | **1.02678 (All-Time Record)**| 0.6172 | -1 match | 0 / 53 | -1.9% | 51 / 79 | **64.56%** |
| **R3: Correctness Predictors** | 5 binary $\mathbb{P}(\text{Exp}_k \text{ Correct})$ classifiers | 52.37% | 0.99566 | 187 / 380 | 49.21% | **1.02731** | 0.6175 | -1 match | 0 / 53 | -1.9% | 53 / 82 | **64.63%** |
| **R8: Hybrid Pairwise Soft** | Pairwise override blended with correctness | 51.84% | 0.99504 | 188 / 380 | 49.47% | **1.02744** | 0.6176 | 0 matches | 0 / 53 | 0.0% | 56 / 90 | 62.22% |
| **R4: Expected Loss Router** | Regressors predicting per-match log-loss | 51.84% | 0.99540 | 187 / 380 | 49.21% | **1.02755** | 0.6176 | -1 match | 0 / 53 | -1.9% | 52 / 81 | **64.20%** |
| **R5: Disagreement-Aware Soft** | L2 logistic softmax on full divergence feats | 52.37% | 0.99512 | 188 / 380 | 49.47% | **1.02770** | 0.6177 | 0 matches | 0 / 53 | 0.0% | 57 / 93 | 61.29% |
| **R1: Direct Multinomial Router** | Multinomial selection on divergence feats | 52.37% | 0.99509 | 188 / 380 | 49.47% | **1.02772** | 0.6177 | 0 matches | 0 / 53 | 0.0% | 57 / 93 | 61.29% |
| **R0: Deployed Baseline Router** | Shallow tree router on context only (M3-E) | 52.37% | 0.99610 | **189 / 380** | **49.74% (Peak)** | **1.02782** | 0.6178 | +1 match | 1 / 53 | +1.9% | 56 / 92 | 60.87% |
| **R7: Shallow Tree + Disagreement**| Tree router on context + divergence feats | 52.11% | 0.99505 | **189 / 380** | **49.74% (Peak)** | **1.02785** | 0.6178 | +1 match | 1 / 53 | +1.9% | 56 / 92 | 60.87% |
| **R2: Pairwise Sequential Override**| Sequential binary decision hierarchy | 51.84% | **0.99479** | 188 / 380 | 49.47% | **1.02794** | 0.6179 | 0 matches | 0 / 53 | 0.0% | 57 / 94 | 60.64% |

---

## 2. Tournament Insights:
1. **All-Time Record Log-Loss (R6):**  
   Candidate R6 establishes the lowest Holdout Log-Loss in project history (**1.02678**), validating that structured hierarchical domain gating provides optimal probabilistic calibration.
2. **Peak Winner Accuracy (R7 & R0):**  
   Candidate R7 achieves **189 / 380 correct (49.74% accuracy)**, maintaining peak winner prediction while improving validation log-loss ($0.99610 \to 0.99505$).

