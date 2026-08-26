# ENNOVERA PL — M3-DATA-04 Cross-Competition & Foreign Calibration Tournament Report

**Tournament Scope:** Multi-Season Benchmarking of European Strength, Foreign Transfer Calibration, and Squad Quality Architectures (D0 to D11).

---

## 1. Candidate Leaderboard: DATA-04 Tournament

| Model Architecture | Architectural Description | Validation Acc | Validation Log-Loss | Holdout Correct (2025–26) | Holdout Log-Loss | Holdout Acc (%) | Holdout Brier | Strong Picks $\ge 60\%$ (Hits / Picks) | Strong Pick Accuracy |
|---|---|---|---|---|---|---|---|---|---|
| **D7: T7 + European Team Strength** | **T7 + Opponent-Adjusted European xG Form** | **52.37%** | **0.99657** | **188 / 380** | **1.02713 (Best)**| **49.47%** | **0.6174 (Best)** | **57 / 89** | **64.04% (23.4% cov)** |
| **D0: T7 Tactical Benchmark** | **Tactical Matchup Geometry Expert (Baseline)**| **52.37%** | **0.99455** | **188 / 380** | **1.02835** | **49.47%** | **0.6180** | **57 / 95** | **60.00% (25.0% cov)** |
| **D8: T7 + Foreign Empirical Prior**| **T7 + Empirical League Translation ($\gamma$)** | **51.84%** | **0.99769** | **187 / 380** | **1.02844** | **49.21%** | **0.6183** | **55 / 87** | **63.22% (22.9% cov)** |
| **D9: T7 + Squad-Derived Strength** | **T7 + Starting XI & Bench Depth Talent** | **52.63%** | **0.99377** | **187 / 380** | **1.02973** | **49.21%** | **0.6189** | **57 / 98** | **58.16% (25.8% cov)** |
| **D10: Linear Combined Expert** | **T7 + Euro + Foreign + Squad Linear Fusion** | **52.11%** | **0.99435** | **184 / 380** | **1.03218** | **48.42%** | **0.6205** | **61 / 101**| **60.40% (26.6% cov)** |
| **D11: Non-linear ML Combined** | **HistGradientBoosting on All DATA-04 Features**| **50.79%** | **1.01474** | **176 / 380** | **1.04339** | **46.32%** | **0.6295** | **75 / 127**| **59.06% (33.4% cov)** |

---

## 2. Scientific Tournament Insights:
1. **European Team Strength (D7) Wins Calibration:**  
   Adding opponent-adjusted European form (D7) achieves the **lowest Holdout Log-Loss in project history (1.02713)** and boosts Strong Pick precision to **64.04%**.
2. **Modular Regularization Superiority:**  
   Simple, modular blending (D7, D8) outperforms dense unconstrained trees (D11). Tree models on correlated squad and European variables overfit Development and degrade out-of-sample holdout performance.

