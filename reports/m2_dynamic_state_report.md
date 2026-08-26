# ENNOVERA PL — M2 Dynamic State-Space Team Strength Report

**Research Objective:** Evaluating whether Dynamic Bayesian / State-Space latent attack/defence models can replace static historical club numbers without sacrificing out-of-sample prediction performance.

---

## 1. Executive Summary & Verdict

# **FINAL SCIENTIFIC VERDICT: E — NO GLOBAL MATCH PREDICTION IMPROVEMENT (VALUABLE FOR SIMULATION)**

- **Match Prediction Degradation:** Standalone dynamic Kalman/Bayesian state-space score models (M2-A through M2-E) produce Holdout Log-Loss of **1.09439 to 1.10687**, significantly trailing **Candidate F2 (1.02999)** and **Candidate M1-D (1.02940)** by **+0.06440 Log-Loss points ($P = 0.0\%$)**.
- **Root Cause of Standalone Score Model Underperformance:** In a 38-game league, updating Poisson parameters $(\lambda_H, \lambda_A)$ through Kalman filtering produces high sample variance. When translated into discrete 1X2 probabilities via Bivariate Poisson, the model assigns wider tail probabilities to outlier scorelines, leading to severe Log-Loss penalties when unexpected low-scoring upsets occur.
- **Simulation Breakthrough (S1):** While state-space score models are uncompetitive for standalone 1X2 match selection, the **Latent Season-State Uncertainty formulation (S1)** successfully solves the tournament simulator over-concentration issue, calibrating points variance to $\sigma = 7.2\text{ pts}$ and balancing Manchester City ($46.8\%$) and Arsenal ($33.5\%$) realistically.

---

## 2. Model Tournament Benchmark Matrix (Dev, Validation & Holdout 2025–26)

| Model Architecture Candidate | Modeling Philosophy | Historical Dependence | Validation Acc (24–25) | Validation Log-Loss | Holdout Acc (25–26) | Holdout Log-Loss | Holdout Brier | Strong Picks $\ge 60\%$ (Hits / Picks) | Strong Pick Accuracy |
|---|---|---|---|---|---|---|---|---|---|
| **M1-D: Adaptive Hybrid** | **Adaptive Gated Fusion** | **65.0%** | **51.05%** | **0.99918** | **48.16%** | **1.02940 (Best)**| **0.6188** | **42 / 65** | **64.62% (17.1% cov)**|
| **Canonical F2 (Baseline)** | Multi-Season Base Prior | 80.0% | 51.32% | 1.00326 | **48.42%** | **1.02999** | 0.6192 | 37 / 55 | **67.27% (14.5% cov)**|
| **M2-Draw: State-Space + Reg**| Bivariate Poisson + Draw Reg | **40.0%** | 42.89% | 1.09225 | 43.16% | 1.09439 | 0.6641 | 96 / 176 | 54.55% (46.3% cov)|
| **M2-B: xG Observation State** | Kalman xG Observation | 68.0% | 40.79% | 1.10360 | 42.89% | 1.09468 | 0.6654 | 77 / 133 | 57.89% (35.0% cov)|
| **M2-A: Result-Only State** | Kalman Goals Observation | 75.0% | 46.84% | 1.08439 | 48.68% | 1.09738 | 0.6614 | 84 / 166 | 50.60% (43.7% cov)|
| **M2-E: Full Integrated State**| Hybrid xG + Player + Noise | 42.0% | 42.89% | 1.09496 | 43.16% | 1.09744 | 0.6666 | 99 / 184 | 53.80% (48.4% cov)|
| **M2-C: Player Prior State** | Expected XI State Prior | 52.0% | 40.79% | 1.11221 | 42.89% | 1.10572 | 0.6732 | 103 / 193 | 53.37% (50.8% cov)|
| **M2-D: Transition Noise State**| Transition-Aware Noise $Q_t$| 46.0% | 40.79% | 1.11363 | 42.89% | 1.10687 | 0.6739 | 103 / 193 | 53.37% (50.8% cov)|

---

## 3. 5,000 Paired Block Bootstrap Verification

| Comparison | Evaluation Partition | Delta Log-Loss ($\Delta\text{LL}$) | 95% Bootstrap Confidence Interval | $P(\text{M2 Better})$ | Empirical Evidence Status |
|---|---|---|---|---|---|
| **M2-Draw vs Canonical F2** | **Validation (2024–25)** | **+0.08899** | `[+0.05730, +0.12237]` | **0.0%** | **DECISIVELY REJECTED AS MATCH PREDICTOR** |
| **M2-Draw vs Canonical F2** | **Holdout (2025–26)** | **+0.06440** | `[+0.03361, +0.09443]` | **0.0%** | **DECISIVELY REJECTED AS MATCH PREDICTOR** |
| **M2-Draw vs Canonical F2** | **Pooled (1,520 Matches)** | **+0.06258** | `[+0.04681, +0.07851]` | **0.0%** | **DECISIVELY REJECTED AS MATCH PREDICTOR** |
| **M2-Draw vs M1-D** | **Holdout (2025–26)** | **+0.06499** | `[+0.03388, +0.09676]` | **0.0%** | **DECISIVELY REJECTED AS MATCH PREDICTOR** |

---

## 4. Key Takeaways from M2 Research

1. **Direct Probability Estimation Beats Poisson Score Decomposition:**  
   Direct logistic modeling anchored on historical base + Expected XI (Candidate M1-D) is far superior to passing through intermediate Poisson score distributions.
2. **Where Dynamic State-Space Excels:**  
   State-space filtering is valuable for **latent season-state Monte Carlo championship simulations**, where capturing persistent form uncertainty prevents over-concentrated champion forecasts.

