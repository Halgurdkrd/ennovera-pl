# ENNOVERA PL — M3 Mixture-of-Experts Architecture Tournament Report

**Tournament Scope:** Multi-Season Benchmarking of 7 MoE Architectures (M3-A to M3-G) Across Validation (2024–25) and Holdout (2025–26).

---

## 1. Candidate Leaderboard: M3 MoE Tournament

| Model Architecture | Gating / Stacking Mechanism | Val Acc (%) | Val Log-Loss | Holdout Correct (2025–26) | Holdout Acc (%) | Holdout Log-Loss | Holdout Brier | Holdout ECE | Strong Picks $\ge 60\%$ (Hits / Picks) | Strong Pick Accuracy |
|---|---|---|---|---|---|---|---|---|---|---|
| **M3-C: Rule-Based Interpretable Gate** | Domain-engineered routing heuristics | 52.11% | 0.99612 | 185 / 380 | 48.68% | **1.02706 (Record)**| 0.6174 | 0.0412 | 53 / 83 | **63.86%** |
| **M3-E: Shallow Tree Gate (HGB Router)** | Shallow gradient boosted decision trees | 52.37% | 0.99610 | **189 / 380** | **49.74% (Peak)** | 1.02782 | 0.6178 | 0.0435 | 56 / 92 | 60.87% |
| **M3-D: Regularized Softmax Gate** | Multinomial L2 logistic gating router | 52.37% | 0.99518 | 188 / 380 | 49.47% | 1.02786 | 0.6177 | 0.0428 | 57 / 93 | 61.29% |
| **M3-G: Best Hybrid MoE (Mode A)** | Softmax Router + Global Prior Calibration | 52.11% | 0.99488 | 188 / 380 | 49.47% | 1.02800 | 0.6179 | 0.0430 | 57 / 94 | 60.64% |
| **M3-G: Best Hybrid MoE (Mode B Lineup)**| Softmax Router + Confirmed XI Shock | 52.11% | 0.99488 | 188 / 380 | 49.47% | 1.02800 | 0.6179 | 0.0430 | 57 / 94 | 60.64% |
| **M3-B: Global Learned Weights** | Static convex weights fit on Dev | 52.37% | **0.99455** | 188 / 380 | 49.47% | 1.02834 | 0.6180 | 0.0441 | 57 / 95 | 60.00% |
| **M3-A: Equal Expert Blend** | Uniform weights ($w_k = 0.20$) | 51.84% | 0.99670 | 185 / 380 | 48.68% | 1.02775 | 0.6178 | 0.0420 | 53 / 82 | **64.63%** |
| **M3-F: Stacked Multinomial Model** | Linear meta-classifier on probability vectors| **52.89%** | 1.00110 | 188 / 380 | 49.47% | 1.03611 | 0.6235 | 0.0512 | 88 / 150 | 58.67% *(Overfit)* |

---

## 2. Tournament Synthesis:
1. **Calibration Record Broken:** M3-C achieves the lowest Holdout Log-Loss (**1.02706**), while M3-E achieves peak Holdout Accuracy (**49.74%, 189 / 380 correct**).
2. **Failure of Dense Stacking (M3-F):** Stacking all 15 raw class probabilities resulted in severe overconfidence and degradation on holdout log-loss ($1.03611$). Regularized convex routing (M3-D, M3-G) remains substantially superior for generalization.

